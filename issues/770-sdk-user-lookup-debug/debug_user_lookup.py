"""
探测脚本：复现 #770 中孙丽的 iWork SDK 用户查找异常。

直接调用 iWork SDK UserManager.search / find_user_by_name，
对比"孙丽"与正常用户（如"苏威"）以及"李卓潼"的返回结构差异。

运行方式（在 efficiency/tasks 目录）：
    MIGRATION_CONFIG=production python debug_user_lookup.py
"""

import logging
import os
import sys
from pathlib import Path

# 把 efficiency/tasks 加入路径，以便导入 infrastructure.gateway.iwork
TASKS_DIR = Path(__file__).resolve().parents[3] / "efficiency" / "tasks"
ORIGIN_CWD = os.getcwd()
os.chdir(TASKS_DIR)
sys.path.insert(0, str(TASKS_DIR))

# 先加载 .env.production，确保 IWorkConfig 能读到配置
from dotenv import load_dotenv
load_dotenv(TASKS_DIR / ".env.production", override=True)

from infrastructure.gateway.iwork.client import IWorkAPI
from infrastructure.gateway.iwork.config import IWorkConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("debug_user_lookup")


def main():
    config = IWorkConfig(
        base_url=os.environ["IWORK_BASE_URL"],
        jwt_token=os.environ["IWORK_TOKEN"],
        operator_user_id=int(os.environ.get("IWORK_OPERATOR_USER_ID", "0")),
        operator_user_name=os.environ.get("IWORK_OPERATOR_USER_NAME", ""),
    )
    api = IWorkAPI(config)
    api.set_art("车机应用软件")

    names = ["苏威", "李卓潼", "孙丽"]
    for name in names:
        print(f"\n{'=' * 60}")
        print(f"查找用户: {name}")
        print("=" * 60)
        try:
            # 1. 直接调用 SDK search
            sdk_users = api.users._manager._sdk.users.search(
                business_project_id=str(api.users._manager._context.space_config.space_id),
                keyword=name,
                page_num=1,
                page_size=15,
            )
            print(f"SDK search 返回数量: {len(sdk_users)}")
            for idx, u in enumerate(sdk_users):
                print(
                    f"  [{idx}] type={type(u).__name__}, key={getattr(u, 'key', None)!r}, "
                    f"display_name={getattr(u, 'display_name', None)!r}, "
                    f"_raw_data={getattr(u, '_raw_data', None)!r}"
                )
        except Exception as e:
            print(f"SDK search 异常: {type(e).__name__}: {e}")
            logger.exception("search")

        try:
            # 2. 调用防腐层 lookup_user_id
            user_id = api.users.lookup_user_id(name)
            print(f"lookup_user_id 结果: {user_id}")
        except Exception as e:
            print(f"lookup_user_id 异常: {type(e).__name__}: {e}")
            logger.exception("lookup_user_id")

    print("\n" + "=" * 60)
    print("模拟 SDK IssueManager.create 中负责人查找路径")
    print("=" * 60)
    # 直接拿到 SDK client 和 IssueManager，复现 issues.py:211 的 bug
    sdk_client = api.users._manager._sdk
    for name in names:
        print(f"\n-- {name} --")
        try:
            user = sdk_client.users.find_user_by_name(
                str(api.users._manager._context.space_config.space_id), name
            )
            print(f"find_user_by_name 返回 type={type(user).__name__}, value={user!r}")
            if user:
                # 这正是 issues.py 中的错误写法
                try:
                    account_id = user.get("accountId")
                    display_name = user.get("disPlayName")
                    print(f"按 dict 取值成功: accountId={account_id}, disPlayName={display_name}")
                except AttributeError as ae:
                    print(f"❌ 按 dict 取值失败: {type(ae).__name__}: {ae}")
                # 正确写法
                account_id = getattr(user, "key", None)
                display_name = getattr(user, "display_name", None)
                print(f"按 User 对象属性取值: key={account_id}, display_name={display_name}")
        except Exception as e:
            print(f"find_user_by_name 异常: {type(e).__name__}: {e}")
            logger.exception("find_user_by_name")


if __name__ == "__main__":
    try:
        main()
    finally:
        os.chdir(ORIGIN_CWD)

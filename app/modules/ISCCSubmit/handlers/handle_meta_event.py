import time
from datetime import datetime, timezone, timedelta

from api.message import send_private_msg
from config import OWNER_ID
from core.switchs import is_private_switch_on
from logger import logger
from utils.generate import generate_text_message

from .. import DAILY_REFRESH_HOUR, DAILY_REFRESH_MINUTE, MODULE_NAME
from .data_manager import DataManager
from .iscc_client import ARENA_TRACK, ISCCClient, ISCCClientError, REGULAR_TRACK
from .monitor_service import MonitorLock, run_monitor_once


BEIJING_TZ = timezone(timedelta(hours=8))

# DB meta 表中记录"最近一次每日刷新日期（北京时间 YYYY-MM-DD）"使用的 key
DAILY_REFRESH_META_KEY = "daily_refresh_last_date"


class MetaEventHandler:
    _last_run_at = 0
    _running = False

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.post_type = msg.get("post_type", "")
        self.meta_event_type = msg.get("meta_event_type", "")

    async def handle(self):
        try:
            if self.post_type == "meta_event" and self.meta_event_type == "heartbeat":
                await self.handle_heartbeat()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理元事件失败: {e}")

    async def handle_heartbeat(self):
        if not is_private_switch_on(MODULE_NAME):
            return
        if self.__class__._running:
            return

        now = int(time.time())
        if now - self.__class__._last_run_at < 60:
            return
        self.__class__._running = True

        try:
            with DataManager() as dm:
                accounts = dm.get_all_accounts()
                last_refresh_date = dm.get_meta(DAILY_REFRESH_META_KEY)

            beijing_now = datetime.now(BEIJING_TZ)
            should_daily_refresh = self._should_daily_refresh(beijing_now, last_refresh_date)

            if should_daily_refresh:
                # 先落库标记，避免刷新过程中进程崩溃、重启后又触发一轮
                today = beijing_now.strftime("%Y-%m-%d")
                with DataManager() as dm:
                    dm.set_meta(DAILY_REFRESH_META_KEY, today)

            # 先跑账号 session 保活 / 每日刷新
            for account in accounts:
                if should_daily_refresh:
                    await self._daily_refresh_account(account, beijing_now)
                else:
                    await self._keep_account_alive(account)

            # 再跑擂台赛监控：上一步可能刷新了 session，需要重新读 DB 拿到最新值
            await self._run_arena_monitor()

            # 真正跑完后再更新节流时间戳，避免长任务被后续心跳误判为"节流未到"后又撞上 _running 锁
            self.__class__._last_run_at = int(time.time())
        finally:
            self.__class__._running = False

    async def _run_arena_monitor(self):
        if not OWNER_ID:
            return

        lock = MonitorLock.get()
        if lock.locked():
            return

        with DataManager() as dm:
            account = dm.get_account(str(OWNER_ID))

        if not account or not account.get("session"):
            # 没有可用凭据，跳过即可（管理员还没 iscc配置）
            return

        async with lock:
            try:
                await run_monitor_once(
                    self.websocket,
                    str(OWNER_ID),
                    account=account,
                    manual_trigger=False,
                )
            except Exception as e:
                logger.error(f"[{MODULE_NAME}]心跳触发擂台赛监控失败: {e}")

    def _should_daily_refresh(self, beijing_now: datetime, last_refresh_date: str) -> bool:
        today = beijing_now.strftime("%Y-%m-%d")
        if last_refresh_date == today:
            return False
        # 到达或超过 07:50 即触发。心跳最小间隔 60s，能保证当日被触发。
        if beijing_now.hour > DAILY_REFRESH_HOUR:
            return True
        if beijing_now.hour == DAILY_REFRESH_HOUR and beijing_now.minute >= DAILY_REFRESH_MINUTE:
            return True
        return False

    async def _keep_account_alive(self, account: dict):
        user_id = str(account["user_id"])
        client = ISCCClient(account.get("session", ""))
        keep_alive_ok = False
        try:
            await client.keep_alive_arena_score()
            keep_alive_ok = True
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]ISCC session 保活失败，准备重新登录: {e}")

        if not keep_alive_ok:
            try:
                session = await client.login(account["username"], account["password"])
                with DataManager() as dm:
                    dm.save_session(user_id, session)
                await send_private_msg(
                    self.websocket,
                    user_id,
                    [generate_text_message(
                        "ISCC 登录状态已过期，机器人已自动重新登录并刷新 session。\n"
                        f"新的 session：{session}"
                    )],
                )
                keep_alive_ok = True
            except ISCCClientError as e:
                if e.is_transient_server_error:
                    # 5xx 视为对端临时不可用，等下个心跳自动重试，不打扰管理员
                    logger.warning(
                        f"[{MODULE_NAME}]ISCC 重新登录遇到服务端 {e.status_code}，"
                        "静默等待下个心跳重试"
                    )
                else:
                    logger.error(f"[{MODULE_NAME}]ISCC 自动重新登录失败: {e}")
                    await send_private_msg(
                        self.websocket,
                        user_id,
                        [generate_text_message(f"ISCC 登录状态已过期，自动重新登录失败：{e}")],
                    )
            except Exception as e:
                logger.error(f"[{MODULE_NAME}]ISCC 自动重新登录失败: {e}")
                await send_private_msg(
                    self.websocket,
                    user_id,
                    [generate_text_message(f"ISCC 登录状态已过期，自动重新登录失败：{e}")],
                )

        if keep_alive_ok:
            await self._refresh_unsolved_cache(user_id, client)

    async def _daily_refresh_account(self, account: dict, beijing_now: datetime):
        user_id = str(account["user_id"])
        username = account.get("username", "")
        password = account.get("password", "")
        client = ISCCClient(account.get("session", ""))
        timestamp = beijing_now.strftime("%Y-%m-%d %H:%M:%S")

        try:
            session = await client.login(username, password)
        except ISCCClientError as e:
            if e.is_transient_server_error:
                # 5xx 时不通知管理员，并清掉当日已触发标记，让下一次心跳继续重试
                logger.warning(
                    f"[{MODULE_NAME}]ISCC 每日定时登录遇到服务端 {e.status_code}，"
                    "静默等待下个心跳重试"
                )
                with DataManager() as dm:
                    dm.set_meta(DAILY_REFRESH_META_KEY, "")
                return
            logger.error(f"[{MODULE_NAME}]ISCC 每日定时登录失败: {e}")
            await send_private_msg(
                self.websocket,
                user_id,
                [generate_text_message(
                    f"[ISCC 每日定时刷新] 北京时间 {timestamp} 自动登录失败：{e}"
                )],
            )
            return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]ISCC 每日定时登录失败: {e}")
            await send_private_msg(
                self.websocket,
                user_id,
                [generate_text_message(
                    f"[ISCC 每日定时刷新] 北京时间 {timestamp} 自动登录失败：{e}"
                )],
            )
            return

        with DataManager() as dm:
            dm.save_session(user_id, session)

        # 登录成功后顺带刷新 nonce 缓存
        regular_nonce = ""
        arena_nonce = ""
        try:
            regular_nonce, arena_nonce = await client.fetch_nonces()
            if regular_nonce or arena_nonce:
                # 用 update_nonce + `x or None`：抓到空串视为"这次没拿到"，保留 DB 原值
                with DataManager() as dm:
                    dm.update_nonce(user_id, regular_nonce or None, arena_nonce or None)
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]ISCC 每日定时刷新 nonce 失败: {e}")

        lines = [
            f"[ISCC 每日定时刷新] 北京时间 {timestamp}",
            "自动重新登录成功，session 已更新。",
            f"新的 session：{session}",
        ]
        if regular_nonce or arena_nonce:
            lines.append(f"练武题 nonce：{regular_nonce or '（未获取）'}")
            lines.append(f"擂台题 nonce：{arena_nonce or '（未获取）'}")

        # 每日刷新顺便重建一次未解题缓存，减少一天内再去实时拉取
        regular_unsolved, arena_unsolved = await self._refresh_unsolved_cache(user_id, client)
        if regular_unsolved is not None and arena_unsolved is not None:
            lines.append(
                f"未解题缓存：练武题 {regular_unsolved} 题 / 擂台题 {arena_unsolved} 题"
            )

        await send_private_msg(
            self.websocket,
            user_id,
            [generate_text_message("\n".join(lines))],
        )

    async def _refresh_unsolved_cache(
        self, user_id: str, client: ISCCClient
    ) -> tuple[int | None, int | None]:
        """调用 client.fetch_unsolved_challenges_detailed 并落库；失败返回 (None, None)。"""
        try:
            fresh = await client.fetch_unsolved_challenges_detailed()
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]刷新未解题缓存失败: {e}")
            return None, None
        with DataManager() as dm:
            for track in (REGULAR_TRACK, ARENA_TRACK):
                track_data = fresh.get(track, {})
                names = track_data.get("names", {})
                categories = track_data.get("categories", {})
                dm.save_unsolved_ids(
                    user_id,
                    track,
                    list(names),
                    names,
                    categories,
                )
        regular_n = len(fresh.get(REGULAR_TRACK, {}).get("names", {}))
        arena_n = len(fresh.get(ARENA_TRACK, {}).get("names", {}))
        return regular_n, arena_n

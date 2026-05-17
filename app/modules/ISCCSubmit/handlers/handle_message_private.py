import html
import re

from api.message import send_private_msg
from core.menu_manager import MENU_COMMAND, MenuManager
from core.switchs import handle_module_private_switch, is_private_switch_on
from logger import logger
from utils.auth import is_system_admin
from utils.generate import generate_reply_message, generate_text_message

from .. import (
    CONFIG_COMMAND,
    FLAG_PATTERN,
    HELP_COMMAND,
    MODULE_NAME,
    MONITOR_ADD_COMMAND,
    MONITOR_CHECK_COMMAND,
    MONITOR_LIST_COMMAND,
    MONITOR_REMOVE_COMMAND,
    NONCE_COMMAND,
    REFRESH_COMMAND,
    SESSION_COMMAND,
    SWITCH_NAME,
)
from .data_manager import DataManager
from .iscc_client import (
    ARENA_TRACK,
    ISCCClient,
    ISCCClientError,
    REGULAR_TRACK,
    SubmitResult,
)
from .monitor_service import MonitorLock, run_monitor_once


class PrivateMessageHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.user_id = str(msg.get("user_id", ""))
        self.message_id = str(msg.get("message_id", ""))
        self.raw_message = msg.get("raw_message", "").strip()

    async def handle(self):
        try:
            if await self._handle_switch_command():
                return
            if await self._handle_menu_command():
                return
            if self.raw_message == HELP_COMMAND:
                await self._reply(self._help_text())
                return
            if not is_private_switch_on(MODULE_NAME):
                return
            if not is_system_admin(self.user_id):
                return

            if self.raw_message.startswith(f"{CONFIG_COMMAND} "):
                await self._handle_config()
                return
            if self.raw_message.lower() == SESSION_COMMAND.lower():
                await self._handle_query_session()
                return
            if self.raw_message.lower() == NONCE_COMMAND.lower():
                await self._handle_query_nonce()
                return
            if self.raw_message == REFRESH_COMMAND:
                await self._handle_refresh_unsolved()
                return
            if self.raw_message == MONITOR_LIST_COMMAND:
                await self._handle_monitor_list()
                return
            if self.raw_message.startswith(MONITOR_ADD_COMMAND):
                await self._handle_monitor_add()
                return
            if self.raw_message.startswith(MONITOR_REMOVE_COMMAND):
                await self._handle_monitor_remove()
                return
            if self.raw_message == MONITOR_CHECK_COMMAND:
                await self._handle_monitor_check()
                return
            flags = self._extract_flags(self.raw_message)
            if flags:
                await self._handle_submit_flag(flags)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")
            await self._reply(f"ISCC 自动提交处理失败：{e}")

    async def _handle_switch_command(self) -> bool:
        if self.raw_message.lower() == SWITCH_NAME.lower():
            if not is_system_admin(self.user_id):
                return True
            await handle_module_private_switch(MODULE_NAME, self.websocket, self.user_id, self.message_id)
            return True
        return False

    async def _handle_menu_command(self) -> bool:
        if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
            await self._reply(MenuManager.get_module_commands_text(MODULE_NAME), auto_delete=True)
            return True
        return False

    async def _handle_config(self):
        parts = self.raw_message.split(maxsplit=2)
        if len(parts) != 3:
            await self._reply("配置格式错误，用法：iscc配置 <账号> <密码>")
            return

        username, password = parts[1], parts[2]
        client = ISCCClient()
        try:
            session = await client.login(username, password)
        except ISCCClientError as e:
            await self._reply(f"ISCC 登录失败：{e}")
            return

        with DataManager() as dm:
            dm.save_account(self.user_id, username, password, session)

        # 登录成功后顺便把未解题缓存建起来，这样后续提交 flag 可以直接走缓存
        ok, regular_n, arena_n, err = await self._refresh_unsolved_cache(client)

        msg_lines = ["ISCC 登录成功，账号、密码和 session 已保存。"]
        if ok:
            msg_lines.append(
                f"未解题缓存已建立：练武题 {regular_n} 题，擂台题 {arena_n} 题。"
            )
        elif err:
            msg_lines.append(f"未解题缓存建立失败：{err}")
        await self._reply("\n".join(msg_lines))

    async def _handle_submit_flag(self, flags: list[tuple[str, str | None]]):
        with DataManager() as dm:
            account = dm.get_account(self.user_id)
        if not account:
            await self._reply("尚未配置 ISCC 账号，请先发送：iscc配置 <账号> <密码>")
            return

        if len(flags) == 1:
            flag_text, cat_filter = flags[0]
            if cat_filter:
                notice = (
                    f"已识别到 flag：{flag_text}\n"
                    f"方向限定：{cat_filter}（不区分大小写、模糊匹配）\n"
                    "已开始提交，请等待结果。"
                )
            else:
                notice = f"已识别到 flag：{flag_text}\n已开始提交，请等待结果。"
        else:
            bullet = "\n".join(
                f"- {flag_text}" + (f"（方向：{cat}）" if cat else "")
                for flag_text, cat in flags
            )
            notice = (
                f"已识别到 {len(flags)} 个 flag，将并发提交：\n{bullet}\n请等待结果。"
            )
        await self._reply(notice)

        client = await self._ensure_client(account)

        # 优先用缓存；任一赛道缺缓存时，现场拉一次并落库，保证结果准。
        prefetched, prefetched_names, prefetched_categories = await self._resolve_unsolved_ids(client)

        # 若用户带了方向过滤但缓存里没有任何 category（旧缓存未升级或拉取失败），
        # 主动再拉一次明细，避免方向过滤把所有题目当成不匹配丢掉。
        needs_categories = any(cat for _, cat in flags)
        has_any_category = any(prefetched_categories.get(track) for track in prefetched_categories)
        if needs_categories and not has_any_category:
            try:
                fresh = await client.fetch_unsolved_challenges_detailed()
            except Exception as e:
                logger.warning(f"[{MODULE_NAME}]按方向提交前补拉题目分类失败: {e}")
            else:
                prefetched = {}
                prefetched_names = {}
                prefetched_categories = {}
                with DataManager() as dm:
                    for track in (REGULAR_TRACK, ARENA_TRACK):
                        track_data = fresh.get(track, {})
                        names = track_data.get("names", {})
                        categories = track_data.get("categories", {})
                        prefetched_names[track] = names
                        prefetched_categories[track] = categories
                        prefetched[track] = list(names)
                        dm.save_unsolved_ids(
                            self.user_id, track, list(names), names, categories
                        )

        flag_results = await client.submit_flags_to_unsolved(
            flags,
            prefetched_ids=prefetched,
            prefetched_names=prefetched_names,
            prefetched_categories=prefetched_categories,
        )
        await self._save_session(client.session_cookie)
        # 用所有 flag 的结果共同刷新缓存，避免被某个 flag 判对后其他 flag 再重复提交。
        merged_results = [item for _, results in flag_results for item in results]
        self._update_cache_after_submit(merged_results)
        await self._refresh_nonces(client, account)
        await self._reply(self._format_multi_flag_results(flag_results, flags))

    @staticmethod
    def _extract_flags(message: str) -> list[tuple[str, str | None]]:
        """提取消息中所有 ISCC{...} flag 与可选的方向限定，保序去重。

        - 单条消息允许多次出现 `ISCC{...}` 或 `ISCC{...} <方向>`，按出现顺序返回。
        - 去重 key 为 (flag, category_filter_lower)，避免同一 flag 同一方向重复提交，
          但同一 flag 不同方向（或一带方向一不带）视为两次独立提交。
        """
        seen: set[tuple[str, str]] = set()
        ordered: list[tuple[str, str | None]] = []
        for match in re.finditer(FLAG_PATTERN, message):
            # FLAG_PATTERN 形如：ISCC\{[^{}]+\}(?:[ \t]+([^\s{}]+))?
            # group(1) 仅捕获方向 token；flag 主体需通过 `ISCC{...}` 子模式重新定位。
            flag_match = re.match(r"ISCC\{[^{}]+\}", match.group(0))
            if not flag_match:
                continue
            flag_body = html.unescape(flag_match.group(0))
            cat_token = match.group(1)
            cat_filter = html.unescape(cat_token).strip() if cat_token else ""
            cat_filter = cat_filter or None
            key = (flag_body, (cat_filter or "").lower())
            if key in seen:
                continue
            seen.add(key)
            ordered.append((flag_body, cat_filter))
        return ordered

    async def _resolve_unsolved_ids(
        self, client: ISCCClient
    ) -> tuple[dict[str, list[int]], dict[str, dict[int, str]], dict[str, dict[int, str]]]:
        """读取未解题缓存（id/name/category）；缓存缺失时实时拉一次并落库。出错时返回空 dict 走兜底分支。"""
        prefetched: dict[str, list[int]] = {}
        prefetched_names: dict[str, dict[int, str]] = {}
        prefetched_categories: dict[str, dict[int, str]] = {}
        missing_tracks: list[str] = []
        with DataManager() as dm:
            for track in (REGULAR_TRACK, ARENA_TRACK):
                ids = dm.get_unsolved_ids(self.user_id, track)
                if ids is None:
                    missing_tracks.append(track)
                else:
                    prefetched[track] = ids
                    prefetched_names[track] = dm.get_unsolved_names(self.user_id, track)
                    prefetched_categories[track] = dm.get_unsolved_categories(self.user_id, track)

        if not missing_tracks:
            return prefetched, prefetched_names, prefetched_categories

        try:
            fresh = await client.fetch_unsolved_challenges_detailed()
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]flag 提交前拉取未解题失败: {e}")
            # 让 submit_flag_to_unsolved 自己走兜底的实时拉路径，同时给已有缓存留着
            return prefetched, prefetched_names, prefetched_categories

        with DataManager() as dm:
            for track in (REGULAR_TRACK, ARENA_TRACK):
                if track in fresh:
                    names = fresh[track].get("names", {})
                    categories = fresh[track].get("categories", {})
                    dm.save_unsolved_ids(
                        self.user_id,
                        track,
                        list(names),
                        names,
                        categories,
                    )
        for track in missing_tracks:
            track_data = fresh.get(track, {})
            prefetched_names[track] = track_data.get("names", {})
            prefetched_categories[track] = track_data.get("categories", {})
            prefetched[track] = list(prefetched_names[track])
        return prefetched, prefetched_names, prefetched_categories

    def _update_cache_after_submit(self, results: list[SubmitResult]):
        """把刚被判为"正确/已解决"的题目从未解缓存里摘掉。"""
        solved_map: dict[str, list[int]] = {REGULAR_TRACK: [], ARENA_TRACK: []}
        for item in results:
            if item.status in {"1", "2"} and item.challenge_id > 0:
                solved_map.setdefault(item.track, []).append(item.challenge_id)
        if not any(solved_map.values()):
            return
        with DataManager() as dm:
            for track, ids in solved_map.items():
                if ids:
                    dm.remove_unsolved_ids(self.user_id, track, ids)

    async def _refresh_unsolved_cache(
        self, client: ISCCClient
    ) -> tuple[bool, int, int, str]:
        """主动刷新未解题缓存（id/name/category），返回 (是否成功, 练武未解数, 擂台未解数, 错误信息)。"""
        try:
            fresh = await client.fetch_unsolved_challenges_detailed()
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]刷新未解题缓存失败: {e}")
            return False, 0, 0, str(e)
        with DataManager() as dm:
            for track in (REGULAR_TRACK, ARENA_TRACK):
                track_data = fresh.get(track, {})
                names = track_data.get("names", {})
                categories = track_data.get("categories", {})
                dm.save_unsolved_ids(
                    self.user_id,
                    track,
                    list(names),
                    names,
                    categories,
                )
        await self._save_session(client.session_cookie)
        regular_n = len(fresh.get(REGULAR_TRACK, {}).get("names", {}))
        arena_n = len(fresh.get(ARENA_TRACK, {}).get("names", {}))
        return True, regular_n, arena_n, ""

    async def _handle_refresh_unsolved(self):
        with DataManager() as dm:
            account = dm.get_account(self.user_id)
        if not account:
            await self._reply("尚未配置 ISCC 账号，请先发送：iscc配置 <账号> <密码>")
            return

        await self._reply("正在刷新未解题缓存，请稍候...")
        client = await self._ensure_client(account)
        ok, regular_n, arena_n, err = await self._refresh_unsolved_cache(client)
        if ok:
            with DataManager() as dm:
                regular_meta = dm.get_unsolved_meta(self.user_id, REGULAR_TRACK)
                arena_meta = dm.get_unsolved_meta(self.user_id, ARENA_TRACK)
                regular_ids = dm.get_unsolved_ids(self.user_id, REGULAR_TRACK) or []
                arena_ids = dm.get_unsolved_ids(self.user_id, ARENA_TRACK) or []
                regular_names = dm.get_unsolved_names(self.user_id, REGULAR_TRACK)
                arena_names = dm.get_unsolved_names(self.user_id, ARENA_TRACK)
                regular_categories = dm.get_unsolved_categories(self.user_id, REGULAR_TRACK)
                arena_categories = dm.get_unsolved_categories(self.user_id, ARENA_TRACK)
            ts = (
                regular_meta and regular_meta.get("updated_at")
            ) or (arena_meta and arena_meta.get("updated_at")) or "刚刚"
            lines = [
                "未解题缓存已刷新",
                f"练武题：{regular_n} 题未解",
                f"擂台题：{arena_n} 题未解",
                f"更新时间：{ts}",
            ]
            if regular_ids or arena_ids:
                lines.append("")
                lines.append("未解题目：")
                for cid in regular_ids:
                    lines.append(
                        "- "
                        + self._format_unsolved_line(
                            REGULAR_TRACK,
                            cid,
                            regular_names.get(cid, ""),
                            regular_categories.get(cid, ""),
                        )
                    )
                for cid in arena_ids:
                    lines.append(
                        "- "
                        + self._format_unsolved_line(
                            ARENA_TRACK,
                            cid,
                            arena_names.get(cid, ""),
                            arena_categories.get(cid, ""),
                        )
                    )
            await self._reply("\n".join(lines))
        else:
            await self._reply(f"刷新未解题缓存失败：{err}")

    async def _handle_query_session(self):
        with DataManager() as dm:
            account = dm.get_account(self.user_id)
        if not account:
            await self._reply("尚未配置 ISCC 账号，请先发送：iscc配置 <账号> <密码>")
            return
        session = account.get("session") or ""
        if not session:
            await self._reply("当前未保存 ISCC session，请提交一次 flag 触发登录。")
            return
        await self._reply(f"当前 ISCC session：\n{session}")

    async def _handle_query_nonce(self):
        with DataManager() as dm:
            account = dm.get_account(self.user_id)
            nonce_row = dm.get_nonce(self.user_id) if account else None
        if not account:
            await self._reply("尚未配置 ISCC 账号，请先发送：iscc配置 <账号> <密码>")
            return

        if not nonce_row or (not nonce_row.get("regular_nonce") and not nonce_row.get("arena_nonce")):
            # 没有缓存的 nonce，尝试立刻拉取一次（必要时自动重登录重试）
            client = await self._ensure_client(account)
            try:
                regular_nonce, arena_nonce = await self._fetch_nonces_with_retry(client, account)
            except ISCCClientError as e:
                await self._reply(f"获取 nonce 失败：{e}")
                return
            await self._save_session(client.session_cookie)
            if regular_nonce or arena_nonce:
                with DataManager() as dm:
                    dm.update_nonce(self.user_id, regular_nonce or None, arena_nonce or None)
                # 为保证回显的 updated_at 与 DB 一致，回读一次；查询不到时退回内存值
                with DataManager() as dm:
                    refreshed = dm.get_nonce(self.user_id)
                nonce_row = refreshed or {
                    "regular_nonce": regular_nonce,
                    "arena_nonce": arena_nonce,
                    "updated_at": "刚刚",
                }
            else:
                await self._reply("获取 nonce 失败，请稍后重试。")
                return

        await self._reply(
            "当前 ISCC nonce：\n"
            f"练武题 nonce：{nonce_row.get('regular_nonce') or '（未获取）'}\n"
            f"擂台题 nonce：{nonce_row.get('arena_nonce') or '（未获取）'}\n"
            f"更新时间：{nonce_row.get('updated_at', '未知')}"
        )

    async def _ensure_client(self, account: dict) -> ISCCClient:
        client = ISCCClient(account.get("session", ""))
        if await client.verify_login():
            return client

        session = await client.login(account["username"], account["password"])
        with DataManager() as dm:
            dm.save_session(self.user_id, session)
        return client

    async def _save_session(self, session: str):
        if not session:
            return
        with DataManager() as dm:
            dm.save_session(self.user_id, session)

    async def _refresh_nonces(self, client: ISCCClient, account: dict):
        try:
            regular_nonce, arena_nonce = await self._fetch_nonces_with_retry(client, account)
        except Exception as e:
            logger.warning(f"[{MODULE_NAME}]刷新 nonce 失败: {e}")
            return
        if not regular_nonce and not arena_nonce:
            return
        # 用 update_nonce + `x or None`：某一路抓到空串时保留 DB 原值，避免被覆盖
        with DataManager() as dm:
            dm.update_nonce(self.user_id, regular_nonce or None, arena_nonce or None)

    async def _fetch_nonces_with_retry(self, client: ISCCClient, account: dict) -> tuple[str, str]:
        """优先使用当前 session 拉取 nonce；遇到登录失效或两路都空时，重登录后再试一次。"""
        try:
            regular_nonce, arena_nonce = await client.fetch_nonces()
        except ISCCClientError as e:
            # 登录失效：走重登录后重试一次
            if "登录状态失效" not in str(e):
                raise
            regular_nonce, arena_nonce = "", ""

        if regular_nonce or arena_nonce:
            return regular_nonce, arena_nonce

        # 两路都拿不到，可能是 session 已失效但页面没把登录表单露出来。
        # 强制重登录一次再试。
        session = await client.login(account["username"], account["password"])
        with DataManager() as dm:
            dm.save_session(self.user_id, session)
        return await client.fetch_nonces()

    def _format_results(
        self, results: list[SubmitResult], cat_filter: str | None = None
    ) -> str:
        if not results:
            if cat_filter:
                return f"ISCC 提交完成：当前没有匹配方向「{cat_filter}」的未解题目。"
            return "ISCC 提交完成：当前没有未解决题目。"

        accepted = [item for item in results if item.status == "1"]
        already = [item for item in results if item.status == "2"]
        failed = [item for item in results if item.status not in {"1", "2"}]
        lines = [
            "ISCC 提交完成",
            f"总提交：{len(results)} 题",
            f"成功：{len(accepted)} 题",
            f"已解决：{len(already)} 题",
            f"失败或跳过：{len(failed)} 题",
        ]
        for item in results:
            lines.append(f"{self._format_result_target(item)}: {item.message}")
        return "\n".join(lines)

    @staticmethod
    def _format_result_target(item: SubmitResult) -> str:
        if item.challenge_name:
            return f"{item.track} {item.challenge_name} #{item.challenge_id}"
        return f"{item.track} #{item.challenge_id}"

    def _format_multi_flag_results(
        self,
        flag_results: list[tuple[str, list[SubmitResult]]],
        flag_specs: list[tuple[str, str | None]] | None = None,
    ) -> str:
        if not flag_results:
            return "ISCC 提交完成：未识别到有效 flag。"

        # 用原始 specs 的方向信息为每个 flag 标注；按出现顺序与 flag_results 一一对应。
        specs = list(flag_specs or [])

        def _spec_for(idx: int, flag: str) -> tuple[str, str | None]:
            if idx < len(specs):
                return specs[idx]
            return flag, None

        if len(flag_results) == 1:
            flag, results = flag_results[0]
            _, cat_filter = _spec_for(0, flag)
            body = self._format_results(results, cat_filter)
            header = f"flag：{flag}"
            if cat_filter:
                header += f"\n方向限定：{cat_filter}"
            return f"{header}\n{body}"

        all_results = [item for _, results in flag_results for item in results]
        total = len(all_results)
        accepted = sum(1 for item in all_results if item.status == "1")
        already = sum(1 for item in all_results if item.status == "2")
        failed = total - accepted - already

        lines = [
            f"ISCC 批量提交完成（共 {len(flag_results)} 个 flag）",
            f"合计提交：{total} 题",
            f"成功：{accepted} 题",
            f"已解决：{already} 题",
            f"失败或跳过：{failed} 题",
        ]
        for idx, (flag, results) in enumerate(flag_results):
            _, cat_filter = _spec_for(idx, flag)
            tag = f"[{flag}]" + (f"（方向：{cat_filter}）" if cat_filter else "")
            if not results:
                if cat_filter:
                    lines.append(
                        f"\n{tag} 当前没有匹配方向「{cat_filter}」的未解题目。"
                    )
                else:
                    lines.append(f"\n{tag} 当前没有未解决题目。")
                continue
            flag_accepted = sum(1 for item in results if item.status == "1")
            flag_already = sum(1 for item in results if item.status == "2")
            flag_failed = len(results) - flag_accepted - flag_already
            lines.append(
                f"\n{tag} 提交 {len(results)} 题，"
                f"成功 {flag_accepted}，已解决 {flag_already}，失败 {flag_failed}"
            )
            for item in results:
                lines.append(f"  {self._format_result_target(item)}: {item.message}")
        return "\n".join(lines)

    @staticmethod
    def _format_unsolved_line(
        track: str, challenge_id: int, challenge_name: str, category: str = ""
    ) -> str:
        parts = [track]
        if challenge_name:
            parts.append(challenge_name)
        parts.append(f"#{challenge_id}")
        head = " ".join(parts)
        return f"{head} [{category}]" if category else head

    def _help_text(self) -> str:
        return (
            "ISCC 自动提交与擂台赛监控帮助\n"
            "iscc：系统管理员开关模块\n"
            "iscc配置 <账号> <密码>：登录并保存账号、密码、session\n"
            "ISCC{xxxxx}：消息中包含一个或多个该形式即会被识别为 flag，多个 flag 会并发提交到所有未解题目\n"
            "ISCC{xxxxx} <方向>：flag 后跟一个空格再跟方向（如 web、misc），表示只把该 flag 提交到匹配该方向的未解题，方向不区分大小写并支持模糊匹配\n"
            f"{SESSION_COMMAND}：查询当前 ISCC session\n"
            f"{NONCE_COMMAND}：查询当前练武题和擂台题 nonce\n"
            f"{REFRESH_COMMAND}：立即刷新练武题/擂台题未解题目缓存\n"
            f"{MONITOR_ADD_COMMAND} <team_id> [备注]：添加擂台赛监控目标\n"
            f"{MONITOR_REMOVE_COMMAND} <team_id>：删除擂台赛监控目标\n"
            f"{MONITOR_LIST_COMMAND}：查看擂台赛监控目标列表\n"
            f"{MONITOR_CHECK_COMMAND}：立即触发一次擂台赛监控轮询\n"
            f"{SWITCH_NAME}{MENU_COMMAND}：查看模块菜单\n"
            "说明：开启模块并配置好账号后，心跳会驱动 session 保活/每日刷新，\n"
            "同时定期刷新未解题目缓存；收到 flag 时会直接对缓存中的未解题目批量提交。\n"
            "擂台赛监控会按节流间隔轮询所有监控目标的解题详情，新通过题目会私聊通知管理员。"
        )

    # ==================== 擂台赛监控命令 ====================

    async def _handle_monitor_list(self):
        with DataManager() as dm:
            targets = dm.list_monitor_targets()
            account = dm.get_account(self.user_id)

        if not targets:
            await self._reply(
                "当前没有监控任何擂台赛 team id。\n"
                "可以通过 `isccm添加 <team_id> [备注]` 添加监控对象。"
            )
            return

        lines = [f"当前监控中的擂台赛 team id 共 {len(targets)} 个："]
        for idx, t in enumerate(targets, start=1):
            remark = t.get("remark") or ""
            team_name = t.get("team_name") or ""
            total_score = t.get("total_score") or ""
            baseline = "基线已建立" if t.get("baseline_ready_at") else "基线待建立"
            line = (
                f"{idx}. {t['team_id']}"
                + (f" [{remark}]" if remark else "")
                + (f" 队名：{team_name}" if team_name else "")
                + (f" {total_score}" if total_score else "")
                + f"（{baseline}）"
            )
            lines.append(line)
        lines.append("")
        lines.append(
            "抓取凭据："
            + (
                "使用当前 ISCC 账号的 session"
                if account and account.get("session")
                else "当前账号未登录，请先 `iscc配置` 保存账号后再监控"
            )
        )
        await self._reply("\n".join(lines))

    async def _handle_monitor_add(self):
        parts = self.raw_message.split(maxsplit=2)
        if len(parts) < 2 or not parts[1].strip():
            await self._reply("用法：isccm添加 <team_id> [备注]")
            return
        team_id = parts[1].strip()
        remark = parts[2].strip() if len(parts) == 3 else ""

        with DataManager() as dm:
            is_new = dm.add_monitor_target(team_id, remark)

        if is_new:
            await self._reply(
                f"已添加擂台赛监控：{team_id}"
                + (f"（备注：{remark}）" if remark else "")
                + "\n下一次心跳会尝试拉取该队伍的擂台赛详情并建立基线。"
            )
        else:
            await self._reply(
                f"该 team id 已在监控中，已更新备注为：{remark or '(空)'}"
            )

    async def _handle_monitor_remove(self):
        parts = self.raw_message.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await self._reply("用法：isccm删除 <team_id>")
            return
        team_id = parts[1].strip()
        with DataManager() as dm:
            ok = dm.remove_monitor_target(team_id)
        if ok:
            await self._reply(
                f"已删除擂台赛监控：{team_id}，相关历史提交记录已清除。"
            )
        else:
            await self._reply(f"未找到擂台赛监控 team id：{team_id}")

    async def _handle_monitor_check(self):
        lock = MonitorLock.get()
        if lock.locked():
            await self._reply("已有一次擂台赛监控轮询在执行，请稍后再试。")
            return

        with DataManager() as dm:
            account = dm.get_account(self.user_id)
        if not account or not account.get("session"):
            await self._reply(
                "当前账号尚未登录或 session 为空，请先发送：iscc配置 <账号> <密码>"
            )
            return

        await self._reply("正在立即执行一次 ISCC 擂台赛监控轮询...")
        async with lock:
            await run_monitor_once(
                self.websocket,
                self.user_id,
                account=account,
                manual_trigger=True,
            )

    async def _reply(self, text: str, auto_delete: bool = False):
        note = "del_msg=30" if auto_delete else ""
        await send_private_msg(self.websocket, self.user_id, [generate_reply_message(self.message_id), generate_text_message(text)], note=note)

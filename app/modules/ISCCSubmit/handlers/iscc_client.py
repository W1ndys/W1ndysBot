import asyncio
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from http.cookies import SimpleCookie

import aiohttp
from bs4 import BeautifulSoup
from yarl import URL

from .. import BASE_URL


STATUS_TEXT = {
    "1": "正确",
    "0": "错误",
    "2": "已解决",
    "3": "提交过快",
    "4": "题目未开放或无权限",
    "5": "服务器错误",
    "-1": "Nonce 错误或登录失效",
}


@dataclass
class ChallengeContext:
    track: str
    submit_path: str
    challenge_ids: list[int]
    challenge_names: dict[int, str] = field(default_factory=dict)
    challenge_categories: dict[int, str] = field(default_factory=dict)


# 赛道标签 -> (未解题提交前缀 / referer 页面)
REGULAR_TRACK = "练武题"
ARENA_TRACK = "擂台题"
TRACK_SUBMIT_PATH = {
    REGULAR_TRACK: "/chal",
    ARENA_TRACK: "/are",
}
TRACK_REFERER_PATH = {
    REGULAR_TRACK: "/challenges",
    ARENA_TRACK: "/arena",
}


@dataclass
class SubmitResult:
    track: str
    challenge_id: int
    status: str
    message: str
    challenge_name: str = ""


@dataclass
class ArenaSolve:
    """擂台赛单题通过记录。"""

    name: str
    category: str = ""
    score: str = ""
    solved_at: str = ""


@dataclass
class TeamArenaSnapshot:
    """某个 team 在擂台赛页面上的快照，用于监控对比。"""

    team_id: str
    team_name: str = ""
    total_score: str = ""
    solves: list[ArenaSolve] = field(default_factory=list)


class ISCCClientError(Exception):
    """ISCC 客户端异常。

    - `status_code` 为 HTTP 状态码（可用时），便于调用方区分短暂性服务端错误（5xx）与
      业务错误（如登录失败、nonce 过期等）。
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

    @property
    def is_transient_server_error(self) -> bool:
        return self.status_code is not None and 500 <= self.status_code < 600


class ISCCClient:
    def __init__(self, session_cookie: str = ""):
        self.base_url = BASE_URL.rstrip("/")
        self.session_cookie = session_cookie
        self._session: aiohttp.ClientSession | None = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    async def login(self, username: str, password: str) -> str:
        async with self._operation_session() as session:
            async with session.post(
                f"{self.base_url}/login",
                data={"name": username, "password": password},
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": self.base_url,
                    "Referer": f"{self.base_url}/login",
                },
            ) as response:
                if response.status >= 400:
                    raise ISCCClientError(
                        f"登录失败，HTTP 状态码 {response.status}",
                        status_code=response.status,
                    )
                cookie = self._extract_session_cookie(response)
                if not cookie:
                    raise ISCCClientError("登录失败，响应中未返回 session")
                self.session_cookie = cookie
                self._sync_session_cookie()
                return cookie

    async def verify_login(self) -> bool:
        if not self.session_cookie:
            return False
        try:
            async with self._operation_session():
                html = await self._request_text("GET", "/challenges", referer=f"{self.base_url}/")
        except ISCCClientError:
            return False
        return bool(self._extract_team_id(html)) and "login" not in html.lower()

    async def fetch_nonces(self) -> tuple[str, str]:
        """获取练武题与擂台题的 nonce，返回 (regular_nonce, arena_nonce)。

        - 登录失效异常会向外抛出，让调用侧决定是否重登录重试。
        - 其它网络/HTTP 错误视为"这次取不到"，对应字段返回空串。
        """
        async with self._operation_session():
            async def _fetch(path: str) -> str:
                try:
                    html = await self._request_text("GET", path, referer=f"{self.base_url}/")
                    return self._extract_nonce(html)
                except ISCCClientError as e:
                    if "登录状态失效" in str(e):
                        raise
                    return ""

            regular_nonce = await _fetch("/challenges")
            arena_nonce = await _fetch("/arena")
            return regular_nonce, arena_nonce

    async def keep_alive_arena_score(self) -> str:
        async with self._operation_session():
            html = await self._request_text("GET", "/arena", referer=f"{self.base_url}/")
            team_id = self._extract_team_id(html)
            if not team_id:
                raise ISCCClientError("获取队伍信息失败")
            await self._request_text("GET", f"/teamarena/{team_id}", referer=f"{self.base_url}/team/{team_id}")
            return team_id

    async def fetch_team_arena_snapshot(self, team_id: str) -> TeamArenaSnapshot:
        """拉取指定 team 的擂台赛页面并解析，供监控模块对比使用。

        仅做只读访问：不依赖当前登录账号是否为该 team 的成员。
        """
        if not team_id:
            raise ISCCClientError("team_id 为空")

        async with self._operation_session():
            html = await self._request_text(
                "GET",
                f"/teamarena/{team_id}",
                referer=f"{self.base_url}/arenascoreboard",
            )
            return self._parse_team_arena(team_id, html)

    def _parse_team_arena(self, team_id: str, html: str) -> TeamArenaSnapshot:
        soup = BeautifulSoup(html, "html.parser")
        snapshot = TeamArenaSnapshot(team_id=team_id)

        team_node = soup.find(id="team-id")
        if team_node and team_node.get_text(strip=True):
            snapshot.team_name = team_node.get_text(strip=True)

        score_node = soup.find(
            lambda tag: tag.name == "h3"
            and "总积分" in tag.get_text(strip=True)
        )
        if score_node:
            snapshot.total_score = score_node.get_text(strip=True)

        table = self._find_arena_solve_table(soup)
        if table is None:
            return snapshot

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")
        for tr in rows:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) < 4:
                continue
            name, category, score, solved_at = cells[0], cells[1], cells[2], cells[3]
            if not name:
                continue
            snapshot.solves.append(
                ArenaSolve(name=name, category=category, score=score, solved_at=solved_at)
            )
        return snapshot

    def _find_arena_solve_table(self, soup: BeautifulSoup):
        """从 /teamarena/<id> 页面找到擂台解题详情表。"""
        for table in soup.find_all("table"):
            header_text = table.get_text(" ", strip=True)
            if "擂台名称" in header_text and "通过时间" in header_text:
                return table
        return None

    async def submit_flag_to_unsolved(
        self,
        flag: str,
        prefetched_ids: dict[str, list[int]] | None = None,
        prefetched_names: dict[str, dict[int, str]] | None = None,
        prefetched_categories: dict[str, dict[int, str]] | None = None,
        category_filter: str | None = None,
    ) -> list[SubmitResult]:
        """对当前所有未解题目提交单个 flag。

        - `prefetched_ids` 传入 `{"练武题": [...], "擂台题": [...]}` 时，直接使用该列表，
          不再实时拉取。缓存未命中的赛道会回退到实时拉取（保持旧逻辑兼容）。
        - `category_filter` 不为 None 时，仅向 category 匹配该过滤条件的题目提交，
          匹配规则在客户端侧统一处理（不区分大小写、支持子串模糊匹配）。
        """
        grouped = await self.submit_flags_to_unsolved(
            [(flag, category_filter)],
            prefetched_ids,
            prefetched_names,
            prefetched_categories,
        )
        # 保持老调用方签名：返回单个 flag 的结果列表。
        return grouped[0][1] if grouped else []

    async def submit_flags_to_unsolved(
        self,
        flags: list[str] | list[tuple[str, str | None]],
        prefetched_ids: dict[str, list[int]] | None = None,
        prefetched_names: dict[str, dict[int, str]] | None = None,
        prefetched_categories: dict[str, dict[int, str]] | None = None,
    ) -> list[tuple[str, list[SubmitResult]]]:
        """对当前所有未解题目并发提交一批 flag。

        - `flags` 既兼容老的 `list[str]`，也支持新格式 `list[tuple[str, str | None]]`，
          后者第二项为该 flag 的方向过滤条件（None 表示不过滤，即全量提交）。
        - 拿到"哪些题未解"只做一次（同一 session 下 prefetched 缺失的赛道才补拉）。
        - 各 flag 之间 `asyncio.gather` 并发；同一 flag 内部仍串行遍历题目，避免触发
          平台"提交过快"（status=3）与 nonce 冲突。
        - 返回值保持与 flags 同序：`[(flag, [SubmitResult, ...]), ...]`。
        """
        prefetched_ids = prefetched_ids or {}
        prefetched_names = prefetched_names or {}
        prefetched_categories = prefetched_categories or {}
        if not flags:
            return []

        # 统一成 (flag, category_filter) 形式，向后兼容旧调用方
        normalized: list[tuple[str, str | None]] = []
        for item in flags:
            if isinstance(item, tuple):
                flag_text, cat_filter = item
                normalized.append((flag_text, cat_filter))
            else:
                normalized.append((item, None))

        async with self._operation_session():
            contexts: list[ChallengeContext] = []
            shared_errors: list[SubmitResult] = []

            for track in (REGULAR_TRACK, ARENA_TRACK):
                ids = prefetched_ids.get(track)
                if ids is not None:
                    contexts.append(
                        ChallengeContext(
                            track,
                            TRACK_SUBMIT_PATH[track],
                            sorted(set(ids)),
                            prefetched_names.get(track, {}),
                            prefetched_categories.get(track, {}),
                        )
                    )
                    continue
                try:
                    if track == REGULAR_TRACK:
                        contexts.append(await self._regular_context())
                    else:
                        contexts.append(await self._arena_context())
                except Exception as e:
                    shared_errors.append(SubmitResult(track, 0, "error", f"获取题目失败：{e}"))

            async def submit_one(flag: str, cat_filter: str | None) -> list[SubmitResult]:
                results: list[SubmitResult] = []
                for context in contexts:
                    target_ids = self._filter_by_category(context, cat_filter)
                    for challenge_id in target_ids:
                        results.append(
                            await self._submit_challenge(context, challenge_id, flag)
                        )
                return [*shared_errors, *results]

            per_flag_results = await asyncio.gather(
                *(submit_one(flag, cat_filter) for flag, cat_filter in normalized)
            )
            return list(zip([flag for flag, _ in normalized], per_flag_results))

    @staticmethod
    def _filter_by_category(
        context: ChallengeContext, cat_filter: str | None
    ) -> list[int]:
        """根据方向过滤未解题目 id，规则：不区分大小写 + 子串模糊匹配。

        - `cat_filter` 为 None 或空字符串时返回全部 challenge_ids。
        - context.challenge_categories 为空（拉取阶段未取到分类）时按"无可匹配题目"
          处理，返回空列表，避免误把全部题目当作匹配项。
        """
        if not cat_filter:
            return list(context.challenge_ids)
        needle = cat_filter.strip().lower()
        if not needle:
            return list(context.challenge_ids)
        if not context.challenge_categories:
            return []
        return [
            cid
            for cid in context.challenge_ids
            if needle in str(context.challenge_categories.get(cid, "")).lower()
        ]

    async def fetch_unsolved_ids(self) -> dict[str, list[int]]:
        """拉取当前账号在两个赛道上的未解题 id，返回 `{"练武题": [...], "擂台题": [...]}`。

        任一赛道失败时把异常包装成 ISCCClientError 抛出（由调用侧决定是否整体失败或部分保留）。
        """
        async with self._operation_session():
            regular_ctx, arena_ctx = await asyncio.gather(
                self._regular_context(), self._arena_context()
            )
            return {
                REGULAR_TRACK: list(regular_ctx.challenge_ids),
                ARENA_TRACK: list(arena_ctx.challenge_ids),
            }

    async def fetch_unsolved_challenges(self) -> dict[str, dict[int, str]]:
        """拉取当前账号在两个赛道上的未解题 id 与题目名。"""
        async with self._operation_session():
            regular_ctx, arena_ctx = await asyncio.gather(
                self._regular_context(), self._arena_context()
            )
            return {
                REGULAR_TRACK: {
                    cid: regular_ctx.challenge_names.get(cid, "")
                    for cid in regular_ctx.challenge_ids
                },
                ARENA_TRACK: {
                    cid: arena_ctx.challenge_names.get(cid, "")
                    for cid in arena_ctx.challenge_ids
                },
            }

    async def fetch_unsolved_challenges_detailed(
        self,
    ) -> dict[str, dict[str, dict[int, str]]]:
        """拉取当前账号在两个赛道上的未解题 id、题目名以及题目方向（category）。

        返回结构：
        ```
        {
            REGULAR_TRACK: {"names": {cid: name}, "categories": {cid: category}},
            ARENA_TRACK:   {"names": {cid: name}, "categories": {cid: category}},
        }
        ```
        """
        async with self._operation_session():
            regular_ctx, arena_ctx = await asyncio.gather(
                self._regular_context(), self._arena_context()
            )
            return {
                REGULAR_TRACK: {
                    "names": {
                        cid: regular_ctx.challenge_names.get(cid, "")
                        for cid in regular_ctx.challenge_ids
                    },
                    "categories": {
                        cid: regular_ctx.challenge_categories.get(cid, "")
                        for cid in regular_ctx.challenge_ids
                    },
                },
                ARENA_TRACK: {
                    "names": {
                        cid: arena_ctx.challenge_names.get(cid, "")
                        for cid in arena_ctx.challenge_ids
                    },
                    "categories": {
                        cid: arena_ctx.challenge_categories.get(cid, "")
                        for cid in arena_ctx.challenge_ids
                    },
                },
            }

    async def _regular_context(self) -> ChallengeContext:
        html, challenge_ids = await asyncio.gather(
            self._request_text("GET", "/challenges", referer=f"{self.base_url}/"),
            self._regular_challenge_ids(),
        )
        team_id = self._extract_team_id(html)
        solved_ids = await self._regular_solved_ids(team_id)
        unsolved_ids = sorted(challenge_ids - solved_ids)
        challenge_names, challenge_categories = await self._regular_challenge_details(unsolved_ids)
        return ChallengeContext(
            REGULAR_TRACK,
            TRACK_SUBMIT_PATH[REGULAR_TRACK],
            unsolved_ids,
            challenge_names,
            challenge_categories,
        )

    async def _arena_context(self) -> ChallengeContext:
        challenge_ids, solved_ids = await asyncio.gather(self._arena_challenge_ids(), self._arena_solved_ids())
        unsolved_ids = sorted(challenge_ids - solved_ids)
        challenge_names, challenge_categories = await self._arena_challenge_details(unsolved_ids)
        return ChallengeContext(
            ARENA_TRACK,
            TRACK_SUBMIT_PATH[ARENA_TRACK],
            unsolved_ids,
            challenge_names,
            challenge_categories,
        )

    async def _regular_solved_ids(self, team_id: str) -> set[int]:
        """当前登录账号已解的练武题 id，走 session 维度的 /solves 接口。"""
        if not team_id:
            return set()
        data = await self._request_json(
            "GET",
            f"/solves/{team_id}",
            referer=f"{self.base_url}/team/{team_id}",
        )
        return {int(item["chalid"]) for item in data.get("solves", []) if str(item.get("chalid", "")).isdigit()}

    async def _regular_challenge_ids(self) -> set[int]:
        data = await self._request_json("GET", "/chals", referer=f"{self.base_url}/challenges")
        return self._challenge_ids_from_payload(data)

    async def _regular_challenge_names(self, challenge_ids: list[int]) -> dict[int, str]:
        names, _ = await self._regular_challenge_details(challenge_ids)
        return names

    async def _regular_challenge_details(
        self, challenge_ids: list[int]
    ) -> tuple[dict[int, str], dict[int, str]]:
        return await self._fetch_challenge_details(
            challenge_ids,
            detail_path="/chals/{id}",
            referer=f"{self.base_url}/challenges",
        )

    async def _arena_challenge_ids(self) -> set[int]:
        data = await self._request_json("GET", "/arenas", referer=f"{self.base_url}/arena")
        return self._challenge_ids_from_payload(data)

    async def _arena_challenge_names(self, challenge_ids: list[int]) -> dict[int, str]:
        names, _ = await self._arena_challenge_details(challenge_ids)
        return names

    async def _arena_challenge_details(
        self, challenge_ids: list[int]
    ) -> tuple[dict[int, str], dict[int, str]]:
        return await self._fetch_challenge_details(
            challenge_ids,
            detail_path="/arenas/{id}",
            referer=f"{self.base_url}/arena",
        )

    async def _fetch_challenge_names(
        self,
        challenge_ids: list[int],
        detail_path: str,
        referer: str,
    ) -> dict[int, str]:
        names, _ = await self._fetch_challenge_details(
            challenge_ids, detail_path=detail_path, referer=referer
        )
        return names

    async def _fetch_challenge_details(
        self,
        challenge_ids: list[int],
        detail_path: str,
        referer: str,
    ) -> tuple[dict[int, str], dict[int, str]]:
        """并发拉取 challenge 详情，返回 (names, categories) 两个 dict。

        - 平台返回的 `category` 字段在不同部署里可能名为 `category`/`cat`/`tags`，
          目前只取 `category`（ISCC 平台主流字段名）；取不到时返回空串。
        - 任一请求失败时该题目仅保留可用字段，不影响其它题目。
        """
        async def fetch_one(challenge_id: int) -> tuple[int, str, str]:
            try:
                data = await self._request_json(
                    "GET",
                    detail_path.format(id=challenge_id),
                    referer=referer,
                )
            except Exception:
                return challenge_id, "", ""
            name = str(data.get("name") or "").strip()
            category = str(data.get("category") or data.get("cat") or "").strip()
            return challenge_id, name, category

        triples = await asyncio.gather(*(fetch_one(cid) for cid in challenge_ids))
        names: dict[int, str] = {}
        categories: dict[int, str] = {}
        for cid, name, category in triples:
            if name:
                names[cid] = name
            if category:
                categories[cid] = category
        return names, categories

    @staticmethod
    def _challenge_ids_from_payload(data: dict) -> set[int]:
        ids: set[int] = set()
        for key in ("game", "challenges"):
            for item in data.get(key, []) or []:
                cid = item.get("id") if isinstance(item, dict) else None
                if str(cid).isdigit():
                    ids.add(int(cid))
        return ids

    async def _arena_solved_ids(self) -> set[int]:
        data = await self._request_json("GET", "/arenasolves", referer=f"{self.base_url}/arena")
        return {int(item["chalid"]) for item in data.get("solves", []) if str(item.get("chalid", "")).isdigit()}

    async def _submit_challenge(self, context: ChallengeContext, challenge_id: int, flag: str) -> SubmitResult:
        try:
            nonce = await self._get_nonce_for_track(context.track)
            referer_path = TRACK_REFERER_PATH.get(context.track, "/")
            text = await self._request_text(
                "POST",
                f"{context.submit_path}/{challenge_id}",
                data={"key": flag, "nonce": nonce},
                referer=f"{self.base_url}{referer_path}",
                ajax=True,
            )
            status = text.strip()
            return SubmitResult(
                context.track,
                challenge_id,
                status,
                STATUS_TEXT.get(status, f"未知返回：{status}"),
                context.challenge_names.get(challenge_id, ""),
            )
        except Exception as e:
            return SubmitResult(
                context.track,
                challenge_id,
                "error",
                f"提交异常：{e}",
                context.challenge_names.get(challenge_id, ""),
            )

    async def _get_nonce_for_track(self, track: str) -> str:
        path = TRACK_REFERER_PATH.get(track, "/challenges")
        html = await self._request_text("GET", path, referer=f"{self.base_url}/")
        nonce = self._extract_nonce(html)
        if not nonce:
            raise ISCCClientError(f"获取{track} nonce 失败")
        return nonce

    async def _request_text(self, method: str, path: str, data: dict | None = None, referer: str = "", ajax: bool = False) -> str:
        headers = self._request_headers(referer, ajax)
        async with self._request_session().request(method, f"{self.base_url}{path}", data=data, headers=headers) as response:
            text = await response.text()
            self._sync_session_cookie()
            if response.status >= 400:
                raise ISCCClientError(
                    f"{method} {path} 失败，HTTP 状态码 {response.status}",
                    status_code=response.status,
                )
            if self._looks_like_login_page(text):
                raise ISCCClientError("登录状态失效")
            return text

    async def _request_json(self, method: str, path: str, referer: str) -> dict:
        headers = self._request_headers(referer, True)
        async with self._request_session().request(method, f"{self.base_url}{path}", headers=headers) as response:
            self._sync_session_cookie()
            if response.status >= 400:
                raise ISCCClientError(
                    f"{method} {path} 失败，HTTP 状态码 {response.status}",
                    status_code=response.status,
                )
            return await response.json(content_type=None)

    @asynccontextmanager
    async def _operation_session(self):
        if self._session is not None:
            yield self._session
            return

        timeout = aiohttp.ClientTimeout(total=20)
        self._session = aiohttp.ClientSession(timeout=timeout, headers=self.headers, cookie_jar=aiohttp.CookieJar(unsafe=True))
        if self.session_cookie:
            self._session.cookie_jar.update_cookies({"session": self.session_cookie}, response_url=URL(self.base_url))
        try:
            yield self._session
        finally:
            self._sync_session_cookie()
            await self._session.close()
            self._session = None

    def _request_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise ISCCClientError("请求会话未初始化")
        return self._session

    def _sync_session_cookie(self):
        if self._session is None:
            return
        for cookie in self._session.cookie_jar:
            if cookie.key == "session":
                self.session_cookie = cookie.value
                return

    def _request_headers(self, referer: str, ajax: bool) -> dict:
        headers = {
            "Accept": "*/*" if ajax else "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": referer or self.base_url,
        }
        if ajax:
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Origin"] = self.base_url
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        return headers

    def _extract_session_cookie(self, response: aiohttp.ClientResponse) -> str:
        if "session" in response.cookies:
            return response.cookies["session"].value
        for header in response.headers.getall("Set-Cookie", []):
            cookie = SimpleCookie(header)
            if "session" in cookie:
                return cookie["session"].value
        return ""

    def _extract_nonce(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for name in ("nonce", "csrf_nonce"):
            node = soup.find("input", attrs={"name": name})
            if node and node.get("value"):
                return str(node["value"])
        match = re.search(r'name=["\'](?:nonce|csrf_nonce)["\'][^>]*value=["\']([^"\']+)', html)
        return match.group(1) if match else ""

    def _extract_team_id(self, html: str) -> str:
        match = re.search(r'href=["\']/team/([0-9a-fA-F]+)["\']', html)
        return match.group(1) if match else ""

    def _looks_like_login_page(self, text: str) -> bool:
        lowered = text.lower()
        return "name=\"password\"" in lowered and "name=\"name\"" in lowered

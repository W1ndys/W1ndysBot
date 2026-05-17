import os
import sqlite3
from datetime import datetime
from typing import Optional
import json

from .. import MODULE_NAME


class DataManager:
    def __init__(self):
        self.data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, f"{MODULE_NAME}.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_account (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                session TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_nonce (
                user_id TEXT PRIMARY KEY,
                regular_nonce TEXT NOT NULL DEFAULT '',
                arena_nonce TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )
        # 通用 k/v 元数据表，用于持久化跨进程状态（例如每日刷新日期）
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )
        # 擂台赛监控：被监控的 team_id 列表
        # baseline_ready_at 用于标记"首次抓取已完成"，避免首次监控把历史通过全量通知
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_monitor_target (
                team_id TEXT PRIMARY KEY,
                remark TEXT NOT NULL DEFAULT '',
                team_name TEXT NOT NULL DEFAULT '',
                total_score TEXT NOT NULL DEFAULT '',
                baseline_ready_at TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        # 擂台赛监控：已知通过记录，(team_id, challenge_name) 唯一
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_monitor_submit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id TEXT NOT NULL,
                challenge_name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                score TEXT NOT NULL DEFAULT '',
                solved_at TEXT NOT NULL DEFAULT '',
                recorded_at TEXT NOT NULL,
                UNIQUE(team_id, challenge_name)
            )
            """
        )
        # 未解题目缓存：按 user_id + track 维度记录当前可提交的 challenge id 列表
        # ids 用逗号分隔的字符串保存（不会很大，几十题量级），避免再建一张明细表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iscc_unsolved_cache (
                user_id TEXT NOT NULL,
                track TEXT NOT NULL,
                ids TEXT NOT NULL DEFAULT '',
                names TEXT NOT NULL DEFAULT '{}',
                categories TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, track)
            )
            """
        )
        self._ensure_unsolved_cache_names_column()
        self._ensure_unsolved_cache_categories_column()
        self.conn.commit()

    def _ensure_unsolved_cache_names_column(self):
        self.cursor.execute("PRAGMA table_info(iscc_unsolved_cache)")
        columns = {row["name"] for row in self.cursor.fetchall()}
        if "names" not in columns:
            self.cursor.execute(
                "ALTER TABLE iscc_unsolved_cache ADD COLUMN names TEXT NOT NULL DEFAULT '{}'"
            )

    def _ensure_unsolved_cache_categories_column(self):
        self.cursor.execute("PRAGMA table_info(iscc_unsolved_cache)")
        columns = {row["name"] for row in self.cursor.fetchall()}
        if "categories" not in columns:
            self.cursor.execute(
                "ALTER TABLE iscc_unsolved_cache ADD COLUMN categories TEXT NOT NULL DEFAULT '{}'"
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()
        return False

    @staticmethod
    def _now_text() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_account(self, user_id: str) -> dict | None:
        self.cursor.execute(
            """
            SELECT user_id, username, password, session FROM iscc_account
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_accounts(self) -> list[dict]:
        self.cursor.execute(
            """
            SELECT user_id, username, password, session FROM iscc_account
            ORDER BY user_id ASC
            """
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def save_account(self, user_id: str, username: str, password: str, session: str):
        self.cursor.execute(
            """
            INSERT INTO iscc_account (user_id, username, password, session, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET username = excluded.username,
                          password = excluded.password,
                          session = excluded.session,
                          updated_at = excluded.updated_at
            """,
            (user_id, username, password, session, self._now_text()),
        )

    def save_session(self, user_id: str, session: str):
        self.cursor.execute(
            """
            UPDATE iscc_account SET session = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (session, self._now_text(), user_id),
        )

    def get_nonce(self, user_id: str) -> dict | None:
        self.cursor.execute(
            """
            SELECT user_id, regular_nonce, arena_nonce, updated_at FROM iscc_nonce
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def save_nonce(self, user_id: str, regular_nonce: str = "", arena_nonce: str = ""):
        """保存 nonce，传入的空字符串会覆盖已有值，因此调用方需按需传入。"""
        self.cursor.execute(
            """
            INSERT INTO iscc_nonce (user_id, regular_nonce, arena_nonce, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET regular_nonce = excluded.regular_nonce,
                          arena_nonce = excluded.arena_nonce,
                          updated_at = excluded.updated_at
            """,
            (user_id, regular_nonce, arena_nonce, self._now_text()),
        )

    def update_nonce(self, user_id: str, regular_nonce: str | None = None, arena_nonce: str | None = None):
        """按需更新单一 nonce 字段，None 表示保持原值。"""
        existing = self.get_nonce(user_id) or {"regular_nonce": "", "arena_nonce": ""}
        new_regular = regular_nonce if regular_nonce is not None else existing.get("regular_nonce", "")
        new_arena = arena_nonce if arena_nonce is not None else existing.get("arena_nonce", "")
        self.save_nonce(user_id, new_regular, new_arena)

    def get_meta(self, key: str) -> str:
        self.cursor.execute(
            """
            SELECT value FROM iscc_meta WHERE key = ?
            """,
            (key,),
        )
        row = self.cursor.fetchone()
        return row["value"] if row else ""

    def set_meta(self, key: str, value: str):
        self.cursor.execute(
            """
            INSERT INTO iscc_meta (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value,
                          updated_at = excluded.updated_at
            """,
            (key, value, self._now_text()),
        )

    # ==================== 未解题目缓存 ====================

    def get_unsolved_ids(self, user_id: str, track: str) -> Optional[list[int]]:
        """读取某用户某赛道的未解题缓存。返回 None 表示无缓存（区别于"已知为空"）。"""
        self.cursor.execute(
            """
            SELECT ids FROM iscc_unsolved_cache WHERE user_id = ? AND track = ?
            """,
            (user_id, track),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        raw = (row["ids"] or "").strip()
        if not raw:
            return []
        return [int(x) for x in raw.split(",") if x.strip().isdigit()]

    def get_unsolved_names(self, user_id: str, track: str) -> dict[int, str]:
        """读取未解题缓存中的题目名映射。旧缓存无名称时返回空 dict。"""
        self.cursor.execute(
            """
            SELECT names FROM iscc_unsolved_cache WHERE user_id = ? AND track = ?
            """,
            (user_id, track),
        )
        row = self.cursor.fetchone()
        if row is None:
            return {}
        try:
            raw = json.loads(row["names"] or "{}")
        except (TypeError, ValueError):
            return {}
        return {
            int(cid): str(name)
            for cid, name in raw.items()
            if str(cid).isdigit() and name
        }

    def get_unsolved_categories(self, user_id: str, track: str) -> dict[int, str]:
        """读取未解题缓存中的题目方向映射。旧缓存无方向时返回空 dict。"""
        self.cursor.execute(
            """
            SELECT categories FROM iscc_unsolved_cache WHERE user_id = ? AND track = ?
            """,
            (user_id, track),
        )
        row = self.cursor.fetchone()
        if row is None:
            return {}
        try:
            raw = json.loads(row["categories"] or "{}")
        except (TypeError, ValueError):
            return {}
        return {
            int(cid): str(category)
            for cid, category in raw.items()
            if str(cid).isdigit() and category
        }

    def get_unsolved_meta(self, user_id: str, track: str) -> Optional[dict]:
        self.cursor.execute(
            """
            SELECT ids, updated_at FROM iscc_unsolved_cache
            WHERE user_id = ? AND track = ?
            """,
            (user_id, track),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def save_unsolved_ids(
        self,
        user_id: str,
        track: str,
        ids: list[int],
        names: dict[int, str] | None = None,
        categories: dict[int, str] | None = None,
    ):
        """覆盖式保存未解题缓存。"""
        joined = ",".join(str(int(x)) for x in ids)
        names_payload = json.dumps(
            {str(int(cid)): str(name) for cid, name in (names or {}).items() if name},
            ensure_ascii=False,
        )
        categories_payload = json.dumps(
            {
                str(int(cid)): str(category)
                for cid, category in (categories or {}).items()
                if category
            },
            ensure_ascii=False,
        )
        self.cursor.execute(
            """
            INSERT INTO iscc_unsolved_cache (user_id, track, ids, names, categories, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, track)
            DO UPDATE SET ids = excluded.ids,
                          names = excluded.names,
                          categories = excluded.categories,
                          updated_at = excluded.updated_at
            """,
            (user_id, track, joined, names_payload, categories_payload, self._now_text()),
        )

    def remove_unsolved_ids(self, user_id: str, track: str, removed_ids: list[int]):
        """从未解缓存里剔除若干 id（提交成功/已解题之后调用）。无缓存时静默跳过。"""
        if not removed_ids:
            return
        current = self.get_unsolved_ids(user_id, track)
        if current is None:
            return
        remaining = [cid for cid in current if cid not in set(removed_ids)]
        if remaining == current:
            return
        names = self.get_unsolved_names(user_id, track)
        categories = self.get_unsolved_categories(user_id, track)
        self.save_unsolved_ids(
            user_id,
            track,
            remaining,
            {cid: names[cid] for cid in remaining if cid in names},
            {cid: categories[cid] for cid in remaining if cid in categories},
        )

    # ==================== 擂台赛监控 ====================

    def add_monitor_target(self, team_id: str, remark: str = "") -> bool:
        """添加监控目标，返回是否为新插入。已存在则仅更新备注。"""
        now = self._now_text()
        existing = self.get_monitor_target(team_id)
        if existing:
            self.cursor.execute(
                """
                UPDATE iscc_monitor_target
                SET remark = ?, updated_at = ?
                WHERE team_id = ?
                """,
                (remark, now, team_id),
            )
            return False
        self.cursor.execute(
            """
            INSERT INTO iscc_monitor_target
                (team_id, remark, team_name, total_score, baseline_ready_at, created_at, updated_at)
            VALUES (?, ?, '', '', '', ?, ?)
            """,
            (team_id, remark, now, now),
        )
        return True

    def remove_monitor_target(self, team_id: str) -> bool:
        self.cursor.execute(
            "DELETE FROM iscc_monitor_target WHERE team_id = ?",
            (team_id,),
        )
        removed = self.cursor.rowcount > 0
        if removed:
            self.cursor.execute(
                "DELETE FROM iscc_monitor_submit WHERE team_id = ?",
                (team_id,),
            )
        return removed

    def get_monitor_target(self, team_id: str) -> Optional[dict]:
        self.cursor.execute(
            """
            SELECT team_id, remark, team_name, total_score,
                   baseline_ready_at, created_at, updated_at
            FROM iscc_monitor_target
            WHERE team_id = ?
            """,
            (team_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def list_monitor_targets(self) -> list[dict]:
        self.cursor.execute(
            """
            SELECT team_id, remark, team_name, total_score,
                   baseline_ready_at, created_at, updated_at
            FROM iscc_monitor_target
            ORDER BY created_at ASC
            """
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def update_monitor_profile(self, team_id: str, team_name: str, total_score: str):
        self.cursor.execute(
            """
            UPDATE iscc_monitor_target
            SET team_name = ?, total_score = ?, updated_at = ?
            WHERE team_id = ?
            """,
            (team_name, total_score, self._now_text(), team_id),
        )

    def mark_monitor_baseline_ready(self, team_id: str):
        now = self._now_text()
        self.cursor.execute(
            """
            UPDATE iscc_monitor_target
            SET baseline_ready_at = ?, updated_at = ?
            WHERE team_id = ? AND baseline_ready_at = ''
            """,
            (now, now, team_id),
        )

    def get_monitor_known_submits(self, team_id: str) -> dict[str, dict]:
        """返回某 team 在擂台赛上的全部已知通过记录，key 为题目名称。"""
        self.cursor.execute(
            """
            SELECT challenge_name, category, score, solved_at, recorded_at
            FROM iscc_monitor_submit
            WHERE team_id = ?
            """,
            (team_id,),
        )
        result: dict[str, dict] = {}
        for row in self.cursor.fetchall():
            result[row["challenge_name"]] = dict(row)
        return result

    def record_monitor_submit(
        self,
        team_id: str,
        challenge_name: str,
        category: str,
        score: str,
        solved_at: str,
    ):
        """写入或更新一条通过记录。solved_at 仅在原值为空时才覆盖，
        避免 ISCC 页面显示相对时间（如"刚刚"）时每轮都被刷掉。"""
        now = self._now_text()
        self.cursor.execute(
            """
            INSERT INTO iscc_monitor_submit
                (team_id, challenge_name, category, score, solved_at, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(team_id, challenge_name)
            DO UPDATE SET category = excluded.category,
                          score = excluded.score,
                          solved_at = CASE
                              WHEN iscc_monitor_submit.solved_at = '' THEN excluded.solved_at
                              ELSE iscc_monitor_submit.solved_at
                          END,
                          recorded_at = excluded.recorded_at
            """,
            (team_id, challenge_name, category, score, solved_at, now),
        )

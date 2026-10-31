"""
Database Manager for MY YOUTUBE CREATOR STUDIO.
Provides SQLite persistence with cache-TTL invalidation, channel-video relationships,
settings persistence, publishing tasks, and clean Windows file-lock closure.
"""

import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "creator_studio.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
        conn = self._get_connection()
        try:
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            # Perform column migrations if older DB exists
            self._migrate_db(conn)
            conn.commit()
        finally:
            conn.close()

    def _migrate_db(self, conn: sqlite3.Connection):
        """Adds any missing columns to existing tables safely."""
        cursor = conn.cursor()
        
        # 1. Migrate channels table
        cursor.execute("PRAGMA table_info(channels)")
        channel_cols = [row["name"] for row in cursor.fetchall()]
        if "data_source" not in channel_cols:
            cursor.execute("ALTER TABLE channels ADD COLUMN data_source TEXT DEFAULT 'Public Ingestion'")
        if "is_cached" not in channel_cols:
            cursor.execute("ALTER TABLE channels ADD COLUMN is_cached INTEGER DEFAULT 0")
        if "last_refreshed_at" not in channel_cols:
            cursor.execute("ALTER TABLE channels ADD COLUMN last_refreshed_at TIMESTAMP")
            cursor.execute("UPDATE channels SET last_refreshed_at = CURRENT_TIMESTAMP WHERE last_refreshed_at IS NULL")
        if "banner_image" not in channel_cols:
            cursor.execute("ALTER TABLE channels ADD COLUMN banner_image TEXT")

        # 2. Migrate channel_audits table
        cursor.execute("PRAGMA table_info(channel_audits)")
        audit_cols = [row["name"] for row in cursor.fetchall()]
        if "score_breakdown_json" not in audit_cols:
            cursor.execute("ALTER TABLE channel_audits ADD COLUMN score_breakdown_json TEXT")

        # 3. Migrate video_analyses table
        cursor.execute("PRAGMA table_info(video_analyses)")
        vid_cols = [row["name"] for row in cursor.fetchall()]
        if "video_id" not in vid_cols:
            cursor.execute("ALTER TABLE video_analyses ADD COLUMN video_id TEXT")
        if "channel_id" not in vid_cols:
            cursor.execute("ALTER TABLE video_analyses ADD COLUMN channel_id TEXT")
        if "readiness_score" not in vid_cols:
            cursor.execute("ALTER TABLE video_analyses ADD COLUMN readiness_score REAL DEFAULT 0.0")
        if "scores_json" not in vid_cols:
            cursor.execute("ALTER TABLE video_analyses ADD COLUMN scores_json TEXT")

        # 4. Migrate assistant_chats table
        cursor.execute("PRAGMA table_info(assistant_chats)")
        chat_cols = [row["name"] for row in cursor.fetchall()]
        if "channel_id" not in chat_cols:
            cursor.execute("ALTER TABLE assistant_chats ADD COLUMN channel_id TEXT")

        # 5. Migrate competitors table
        cursor.execute("PRAGMA table_info(competitors)")
        comp_cols = [row["name"] for row in cursor.fetchall()]
        if "competitor_group" not in comp_cols:
            cursor.execute("ALTER TABLE competitors ADD COLUMN competitor_group TEXT DEFAULT 'default'")
        if "handle" not in comp_cols:
            cursor.execute("ALTER TABLE competitors ADD COLUMN handle TEXT")
        if "upload_frequency" not in comp_cols:
            cursor.execute("ALTER TABLE competitors ADD COLUMN upload_frequency REAL DEFAULT 0.0")

    # --- Channel Management & Cache Control ---
    def save_channel(self, channel_data: Dict[str, Any], is_cached: bool = False) -> int:
        query = """
        INSERT INTO channels (
            channel_id, title, custom_url, description, subscriber_count, 
            view_count, video_count, profile_image, banner_image, data_source,
            is_cached, last_refreshed_at, raw_data_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(channel_id) DO UPDATE SET
            title=excluded.title,
            custom_url=excluded.custom_url,
            description=excluded.description,
            subscriber_count=excluded.subscriber_count,
            view_count=excluded.view_count,
            video_count=excluded.video_count,
            profile_image=excluded.profile_image,
            banner_image=excluded.banner_image,
            data_source=excluded.data_source,
            is_cached=excluded.is_cached,
            last_refreshed_at=CURRENT_TIMESTAMP,
            raw_data_json=excluded.raw_data_json;
        """
        raw_json = json.dumps(channel_data.get("raw_data", {}))
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    channel_data.get("channel_id", ""),
                    channel_data.get("title", "Untitled Channel"),
                    channel_data.get("custom_url", ""),
                    channel_data.get("description", ""),
                    int(channel_data.get("subscriber_count", 0)),
                    int(channel_data.get("view_count", 0)),
                    int(channel_data.get("video_count", 0)),
                    channel_data.get("profile_image", ""),
                    channel_data.get("banner_image", ""),
                    channel_data.get("data_source", "Public Ingestion"),
                    1 if is_cached else 0,
                    raw_json,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0
        finally:
            conn.close()

    def _hydrate_channel_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures channel dict has unpacked videos, counts, and formatted strings."""
        if d.get("raw_data_json"):
            try:
                d["raw_data"] = json.loads(d["raw_data_json"])
            except Exception:
                d["raw_data"] = {}
        else:
            d["raw_data"] = {}

        d["videos"] = d["raw_data"].get("videos", [])
        shorts_count = sum(1 for v in d["videos"] if v.get("is_short"))
        d["shorts_count"] = shorts_count
        d["long_count"] = len(d["videos"]) - shorts_count

        sub = d.get("subscriber_count", 0)
        if sub >= 1_000_000:
            d["subscriber_count_str"] = f"{sub / 1_000_000:.2f}M"
        elif sub >= 1_000:
            d["subscriber_count_str"] = f"{sub / 1_000:.1f}K"
        else:
            d["subscriber_count_str"] = str(sub)

        views = d.get("view_count", 0)
        if views >= 1_000_000:
            d["view_count_str"] = f"{views / 1_000_000:.2f}M"
        elif views >= 1_000:
            d["view_count_str"] = f"{views / 1_000:.1f}K"
        else:
            d["view_count_str"] = str(views)

        return d

    def get_channel(
        self, channel_id_or_handle: str, max_age_seconds: Optional[int] = None, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves channel by channel_id or custom_url handle.
        If force_refresh is True or age exceeds max_age_seconds, returns None.
        """
        if force_refresh:
            return None

        clean_ident = channel_id_or_handle.strip()
        handle_with_at = f"@{clean_ident.lstrip('@')}"

        query = """
        SELECT * FROM channels 
        WHERE channel_id = ? OR custom_url = ? OR custom_url = ?
        ORDER BY last_refreshed_at DESC LIMIT 1
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (clean_ident, clean_ident, handle_with_at))
            row = cursor.fetchone()
            if not row:
                return None

            d = dict(row)
            if max_age_seconds is not None and d.get("last_refreshed_at"):
                try:
                    refreshed = datetime.datetime.fromisoformat(d["last_refreshed_at"].replace("Z", "+00:00"))
                    age = (datetime.datetime.now(datetime.timezone.utc) - refreshed).total_seconds()
                    if age > max_age_seconds:
                        return None  # Cache expired
                except Exception:
                    pass

            return self._hydrate_channel_dict(d)
        finally:
            conn.close()

    def get_recent_channels(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = "SELECT * FROM channels ORDER BY last_refreshed_at DESC LIMIT ?"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                results.append(self._hydrate_channel_dict(d))
            return results
        finally:
            conn.close()

    # --- Channel Audits ---
    def save_channel_audit(
        self, channel_id: str, score: int, audit_data: Dict[str, Any], breakdown: Optional[Dict[str, Any]] = None
    ) -> int:
        query = """
        INSERT INTO channel_audits (channel_id, audit_score, score_breakdown_json, audit_data_json)
        VALUES (?, ?, ?, ?)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    query,
                    (channel_id, score, json.dumps(breakdown or {}), json.dumps(audit_data)),
                )
            except sqlite3.OperationalError as e:
                if "score_breakdown_json" in str(e):
                    # Table was created before score_breakdown_json column existed; self-heal schema
                    cursor.execute("ALTER TABLE channel_audits ADD COLUMN score_breakdown_json TEXT")
                    cursor.execute(
                        query,
                        (channel_id, score, json.dumps(breakdown or {}), json.dumps(audit_data)),
                    )
                else:
                    raise
            conn.commit()
            return cursor.lastrowid or 0
        finally:
            conn.close()

    def get_latest_channel_audit(self, channel_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM channel_audits WHERE channel_id = ? ORDER BY created_at DESC LIMIT 1"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (channel_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                data = json.loads(d["audit_data_json"])
                for k, v in data.items():
                    if k not in d:
                        d[k] = v
                d["audit_data"] = data
                if d.get("score_breakdown_json"):
                    try:
                        d["score_breakdown"] = json.loads(d["score_breakdown_json"])
                    except Exception:
                        d["score_breakdown"] = {}
                return d
            return None
        finally:
            conn.close()

    # --- Video Analyses ---
    def save_video_analysis(self, analysis_data: Dict[str, Any], channel_id: Optional[str] = None) -> int:
        query = """
        INSERT INTO video_analyses (
            channel_id, title, source_type, video_id, file_name, file_size, duration,
            aspect_ratio, resolution, fps, bitrate, audio_channels, sample_rate,
            hook_score, pacing_score, readiness_score, scores_json, analysis_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    channel_id or analysis_data.get("channel_id"),
                    analysis_data.get("title", "Untitled Video"),
                    analysis_data.get("source_type", "upload"),
                    analysis_data.get("video_id", ""),
                    analysis_data.get("file_name", ""),
                    int(analysis_data.get("file_size", 0)),
                    float(analysis_data.get("duration", 0.0)),
                    analysis_data.get("aspect_ratio", "16:9"),
                    analysis_data.get("resolution", "1920x1080"),
                    float(analysis_data.get("fps", 0.0)),
                    int(analysis_data.get("bitrate", 0)),
                    int(analysis_data.get("audio_channels", 2)),
                    int(analysis_data.get("sample_rate", 44100)),
                    float(analysis_data.get("hook_score", 0.0)),
                    float(analysis_data.get("pacing_score", 0.0)),
                    float(analysis_data.get("readiness_score", 0.0)),
                    json.dumps(analysis_data.get("scores", {})),
                    json.dumps(analysis_data.get("details", {})),
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0
        finally:
            conn.close()

    def get_recent_video_analyses(
        self, channel_id: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        if channel_id:
            query = "SELECT * FROM video_analyses WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?"
            params = (channel_id, limit)
        else:
            query = "SELECT * FROM video_analyses ORDER BY created_at DESC LIMIT ?"
            params = (limit,)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("analysis_json"):
                    try:
                        d["details"] = json.loads(d["analysis_json"])
                    except Exception:
                        d["details"] = {}
                if d.get("scores_json"):
                    try:
                        d["scores"] = json.loads(d["scores_json"])
                    except Exception:
                        d["scores"] = {}
                results.append(d)
            return results
        finally:
            conn.close()

    # --- Publishing Tasks ---
    def save_publishing_task(self, task_data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO publishing_tasks (channel_id, title, format_type, target_date, target_time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    task_data.get("channel_id", ""),
                    task_data.get("title", "Untitled Task"),
                    task_data.get("format_type", "Long-form"),
                    task_data.get("target_date", ""),
                    task_data.get("target_time", ""),
                    task_data.get("status", "Scheduled"),
                    task_data.get("notes", ""),
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0
        finally:
            conn.close()

    def get_publishing_tasks(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if channel_id:
            query = "SELECT * FROM publishing_tasks WHERE channel_id = ? ORDER BY target_date ASC, target_time ASC"
            params = (channel_id,)
        else:
            query = "SELECT * FROM publishing_tasks ORDER BY target_date ASC, target_time ASC"
            params = ()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_publishing_task(self, task_id: int):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM publishing_tasks WHERE id = ?", (task_id,))
            conn.commit()
        finally:
            conn.close()

    # --- User Settings ---
    def set_setting(self, key: str, value: str):
        query = """
        INSERT INTO user_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (key, value))
            conn.commit()
        finally:
            conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        query = "SELECT value FROM user_settings WHERE key = ?"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
        finally:
            conn.close()

    # --- Competitors ---
    def save_competitor(self, competitor_data: Dict[str, Any], group: str = "default") -> int:
        query = """
        INSERT INTO competitors (
            competitor_group, channel_id, channel_title, handle, subscriber_count,
            video_count, view_count, upload_frequency, raw_data_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(channel_id) DO UPDATE SET
            competitor_group=excluded.competitor_group,
            channel_title=excluded.channel_title,
            handle=excluded.handle,
            subscriber_count=excluded.subscriber_count,
            video_count=excluded.video_count,
            view_count=excluded.view_count,
            upload_frequency=excluded.upload_frequency,
            raw_data_json=excluded.raw_data_json,
            updated_at=CURRENT_TIMESTAMP;
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    group,
                    competitor_data.get("channel_id", ""),
                    competitor_data.get("channel_title", "Unknown Competitor"),
                    competitor_data.get("handle", ""),
                    int(competitor_data.get("subscriber_count", 0)),
                    int(competitor_data.get("video_count", 0)),
                    int(competitor_data.get("view_count", 0)),
                    float(competitor_data.get("upload_frequency", 0.0)),
                    json.dumps(competitor_data.get("raw_data", {})),
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0
        finally:
            conn.close()

    def get_competitors(self, group: str = "default") -> List[Dict[str, Any]]:
        query = "SELECT * FROM competitors WHERE competitor_group = ? ORDER BY subscriber_count DESC"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (group,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("raw_data_json"):
                    try:
                        d["raw_data"] = json.loads(d["raw_data_json"])
                    except Exception:
                        d["raw_data"] = {}
                results.append(d)
            return results
        finally:
            conn.close()

    def delete_competitor(self, channel_id: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM competitors WHERE channel_id = ?", (channel_id,))
            conn.commit()
        finally:
            conn.close()

    # --- Assistant Chats ---
    def save_chat_message(
        self, session_id: str, role: str, message: str, context: Optional[Dict[str, Any]] = None, channel_id: Optional[str] = None
    ):
        query = "INSERT INTO assistant_chats (session_id, channel_id, role, message, context_json) VALUES (?, ?, ?, ?, ?)"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (session_id, channel_id, role, message, json.dumps(context or {})))
            conn.commit()
        finally:
            conn.close()

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM assistant_chats WHERE session_id = ? ORDER BY created_at ASC LIMIT ?"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (session_id, limit))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("context_json"):
                    try:
                        d["context"] = json.loads(d["context_json"])
                    except Exception:
                        d["context"] = {}
                results.append(d)
            return results
        finally:
            conn.close()

    def clear_chat_history(self, session_id: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assistant_chats WHERE session_id = ?", (session_id,))
            conn.commit()
        finally:
            conn.close()

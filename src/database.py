import hashlib
import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class ContentDB:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DATA_DIR / "content.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT,
                DATA BLOB,
                HASH TEXT,
                content_type TEXT,
                created_at INTEGER,
                UNIQUE(url, version)
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_url ON content(url)"
        )
        self.conn.commit()

    def insert(self, url, content=None, data=None, content_type="HTML"):
        if data is not None:
            content_type = "FILE"
            content = None
            data_hash = hashlib.sha256(data).hexdigest()
        else:
            content_type = "HTML"
            data_hash = None

        cur = self.conn.execute(
            "SELECT version, content_type, content, HASH FROM content "
            "WHERE url = ? ORDER BY version DESC LIMIT 1",
            (url,),
        )
        row = cur.fetchone()

        if row is None:
            version = 1
        elif data_hash is not None:
            if row["content_type"] == "FILE" and row["HASH"] == data_hash:
                return False
            version = row["version"] + 1
        elif row["content_type"] == "HTML" and row["content"] == content:
            return False
        else:
            version = row["version"] + 1

        self.conn.execute(
            """
            INSERT INTO content (url, version, content, DATA, HASH, content_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (url, version, content, data, data_hash, content_type, int(time.time())),
        )
        self.conn.commit()
        return True

    def exists(self, url):
        cur = self.conn.execute(
            "SELECT 1 FROM content WHERE url = ? LIMIT 1", (url,)
        )
        return cur.fetchone() is not None

    def get_urls(self):
        cur = self.conn.execute("SELECT DISTINCT url FROM content")
        return [row["url"] for row in cur.fetchall()]

    def get(self, url, version=None):
        if version is None:
            cur = self.conn.execute(
                """
                SELECT * FROM content
                WHERE url = ?
                ORDER BY version DESC LIMIT 1
                """,
                (url,),
            )
        else:
            cur = self.conn.execute(
                """
                SELECT * FROM content
                WHERE url = ? AND version = ?
                """,
                (url, version),
            )
        row = cur.fetchone()
        if row is None:
            return None
        result = dict(row)
        return result

    def get_versions(self, url):
        cur = self.conn.execute(
            """
            SELECT id, version, content, DATA, HASH, content_type, created_at
            FROM content WHERE url = ?
            ORDER BY version ASC
            """,
            (url,),
        )
        return [dict(row) for row in cur.fetchall()]

    def merge_url(self, old, new):
        if old == new:
            return
        cur = self.conn.execute(
            "SELECT MAX(version) FROM content WHERE url = ?", (new,)
        )
        max_version = cur.fetchone()[0] or 0
        rows = self.conn.execute(
            "SELECT * FROM content WHERE url = ? ORDER BY version ASC", (old,)
        ).fetchall()
        for i, row in enumerate(rows, start=1):
            self.conn.execute(
                """
                INSERT OR IGNORE INTO content
                (url, version, content, DATA, HASH, content_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new,
                    max_version + i,
                    row["content"],
                    row["DATA"],
                    row["HASH"],
                    row["content_type"],
                    row["created_at"],
                ),
            )
        self.conn.execute("DELETE FROM content WHERE url = ?", (old,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class LinksDB:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DATA_DIR / "links.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                created_at INTEGER
            )
            """
        )
        self.conn.commit()

    def insert(self, url):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO links (url, created_at) VALUES (?, ?)",
            (url, int(time.time())),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def get_links(self):
        cur = self.conn.execute("SELECT id, url FROM links")
        return {row["url"]: row["id"] for row in cur.fetchall()}

    def exists(self, url):
        cur = self.conn.execute(
            "SELECT 1 FROM links WHERE url = ?", (url,)
        )
        return cur.fetchone() is not None

    def count(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM links")
        return cur.fetchone()[0]

    def merge_url(self, old, new):
        if old == new:
            return
        cur = self.conn.execute(
            "SELECT MIN(created_at) FROM links WHERE url = ?", (old,)
        )
        old_created = cur.fetchone()[0]
        self.conn.execute(
            """
            INSERT INTO links (url, created_at)
            VALUES (?, ?)
            ON CONFLICT(url) DO NOTHING
            """,
            (new, old_created),
        )
        self.conn.execute("DELETE FROM links WHERE url = ?", (old,))
        self.conn.commit()

    def close(self):
        self.conn.close()


contentdb = ContentDB()
linkdb = LinksDB()
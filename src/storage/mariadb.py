from __future__ import annotations
import os
from typing import Any, Dict, List
import mysql.connector
from mysql.connector.connection import MySQLConnection
from ..core.logger import setup_logger

logger = setup_logger()

class MariaDBStorage:
    def __init__(self, conn: MySQLConnection, table: str, mode: str = "upsert"):
        self.conn = conn
        self.table = table
        self.mode = mode

    @classmethod
    def from_env(cls, table: str, mode: str = "upsert") -> "MariaDBStorage":
        host = os.getenv("DB_HOST", "mariadb")
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "airly")
        password = os.getenv("DB_PASSWORD", "airlypass")
        database = os.getenv("DB_NAME", "air_quality")

        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=False,
        )
        return cls(conn=conn, table=table, mode=mode)

    def save_measurements(self, rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return 0

        cols = ["installation_id","measured_at","param","value","source","from_datetime","till_datetime"]
        placeholders = ", ".join(["%s"] * len(cols))
        col_list = ", ".join(cols)

        if self.mode == "insert":
            sql = f"INSERT INTO {self.table} ({col_list}) VALUES ({placeholders})"
        elif self.mode == "upsert":
            updates = ", ".join([f"{c}=VALUES({c})" for c in ["value","source","from_datetime","till_datetime"]])
            sql = f"INSERT INTO {self.table} ({col_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
        else:
            raise ValueError(f"Unknown storage mode: {self.mode}")

        data = []
        for r in rows:
            data.append([r.get(c) for c in cols])

        cur = self.conn.cursor()
        try:
            cur.executemany(sql, data)
            self.conn.commit()
            return cur.rowcount
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

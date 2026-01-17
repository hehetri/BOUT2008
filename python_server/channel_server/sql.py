"""SQL database helper for the channel server."""
from __future__ import annotations

import configparser
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import mysql.connector


LOGGER = logging.getLogger(__name__)


@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


class SQLDatabase:
    def __init__(self, owner: str, config_path: str | Path = "configs/mysql.conf") -> None:
        self.owner = owner
        self.config_path = Path(config_path)
        self.config: Optional[MySQLConfig] = None
        self.connection = None

    def _load_config(self) -> MySQLConfig:
        parser = configparser.ConfigParser()
        content = self.config_path.read_text(encoding="utf-8", errors="ignore")
        parser.read_string("[mysql]\n" + content)
        section = parser["mysql"]
        return MySQLConfig(
            host=section.get("MySQL_ip", "127.0.0.1"),
            port=section.getint("MySQL_port", 3306),
            user=section.get("MySQL_id", "root"),
            password=section.get("MySQL_pw", ""),
            database=section.get("MySQL_db", ""),
        )

    def start(self) -> None:
        self.config = self._load_config()
        self.connection = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
        )
        LOGGER.info("[%s] SQL Connection started", self.owner)

    def query(self, query: str, params: Optional[Iterable[Any]] = None) -> list[dict[str, Any]]:
        if self.connection is None:
            raise RuntimeError("SQL connection is not initialized")
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def update(self, query: str, params: Optional[Iterable[Any]] = None) -> None:
        if self.connection is None:
            raise RuntimeError("SQL connection is not initialized")
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        cursor.close()

"""Item data access translated from Java ItemClass."""
from __future__ import annotations

from typing import Any, Optional

from .sql import SQLDatabase


class ItemClass:
    def __init__(self, sql: SQLDatabase) -> None:
        self.sql = sql

    def get_item_name(self, item_id: int) -> Optional[str]:
        rows = self.sql.query("SELECT name FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return rows[0]["name"] if rows else None

    def get_item_id(self, name: str) -> int:
        rows = self.sql.query("SELECT id FROM bout_items WHERE name=%s LIMIT 1", (name,))
        return int(rows[0]["id"]) if rows else 0

    def get_item_id_like(self, name: str) -> Optional[list[str]]:
        rows = self.sql.query("SELECT id, name FROM bout_items WHERE name LIKE %s", (f"{name}%",))
        if not rows:
            return None
        results = [f"{row['id']} - {row['name']}" for row in rows[:5]]
        results.append(str(len(rows)))
        return results

    def get_item_shop_infos(self, item_id: int) -> Optional[dict[str, Any]]:
        rows = self.sql.query("SELECT * FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return rows[0] if rows else None

    def get_sell(self, item_id: int) -> int:
        rows = self.sql.query("SELECT sell FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return int(rows[0]["sell"]) if rows else -1

    def get_buy(self, item_id: int) -> int:
        rows = self.sql.query("SELECT buy, buyable FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        if rows and int(rows[0]["buyable"]) == 1:
            return int(rows[0]["buy"])
        return -1

    def get_buy_coins(self, item_id: int) -> int:
        rows = self.sql.query("SELECT coins, buyable FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        if rows and int(rows[0]["buyable"]) == 1:
            return int(rows[0]["coins"])
        return -1

    def get_coin_days(self, item_id: int) -> int:
        rows = self.sql.query("SELECT day FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return int(rows[0]["day"]) if rows else -1

    def get_item_script(self, item_id: int) -> Optional[str]:
        rows = self.sql.query("SELECT script FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return rows[0]["script"] if rows else None

    def get_item_info(self, item_id: int) -> Optional[dict[str, Any]]:
        rows = self.sql.query("SELECT reqlevel, bot, part FROM bout_items WHERE id=%s LIMIT 1", (item_id,))
        return rows[0] if rows else None

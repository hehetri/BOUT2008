"""Bot data model and inventory handling."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .item import ItemClass
from .packet import Packet
from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)


@dataclass
class BotClass:
    account: str
    ip: str
    item: ItemClass
    sql: SQLDatabase

    botname: str = ""
    bottype: int = 0
    exp: int = 0
    level: int = 0
    hp: int = 0
    gigas: int = 0
    attmin: int = 0
    attmax: int = 0
    attmintrans: int = 0
    attmaxtrans: int = 0
    transgauge: int = 0
    crit: int = 0
    evade: int = 0
    spectrans: int = 0
    speed: int = 0
    transdef: int = 0
    transbotatt: int = 0
    transspeed: int = 0
    rangeatt: int = 0
    luk: int = 0
    botstract: int = 0
    coins: int = 0

    equipitemspart: list[int] = field(default_factory=lambda: [0, 0, 0])
    equipitemsgear: list[int] = field(default_factory=lambda: [0] * 8)
    equipitemspack: list[int] = field(default_factory=lambda: [0] * 6)
    equipitemscoin: list[int] = field(default_factory=lambda: [0, 0])
    inventitems: list[int] = field(default_factory=lambda: [0] * 10)

    hpb: int = 0
    attminb: int = 0
    attmaxb: int = 0
    attmintransb: int = 0
    attmaxtransb: int = 0
    transgaugeb: int = 0
    critb: int = 0
    evadeb: int = 0
    spectransb: int = 0
    speedb: int = 0
    transdefb: int = 0
    transbotattb: int = 0
    transspeedb: int = 0
    rangeattb: int = 0
    lukb: int = 0

    room: list[int] = field(default_factory=lambda: [-1, -1])

    def load_char(self) -> None:
        rows = self.sql.query("SELECT * FROM bout_characters WHERE username=%s LIMIT 1", (self.account,))
        if rows:
            row = rows[0]
            self.botname = row.get("name", "")
            self.bottype = int(row.get("bot", 0))
            self.exp = int(row.get("exp", 0))
            self.level = int(row.get("level", 0))
            self.hp = int(row.get("hp", 0))
            self.gigas = int(row.get("gigas", 0))
            self.attmin = int(row.get("attmin", 0))
            self.attmax = int(row.get("attmax", 0))
            self.attmintrans = int(row.get("attmintrans", 0))
            self.attmaxtrans = int(row.get("attmaxtrans", 0))
            self.transgauge = int(row.get("transgauge", 0))
            self.crit = int(row.get("crit", 0))
            self.evade = int(row.get("evade", 0))
            self.spectrans = int(row.get("specialtrans", 0))
            self.speed = int(row.get("speed", 0))
            self.transdef = int(row.get("transdef", 0))
            self.transbotatt = int(row.get("transbotatt", 0))
            self.transspeed = int(row.get("transspeed", 0))
            self.rangeatt = int(row.get("rangeatt", 0))
            self.luk = int(row.get("luk", 0))
            self.botstract = int(row.get("botstract", 0))
            self.equipitemspart = [
                int(row.get("equiphead", 0)),
                int(row.get("equipbody", 0)),
                int(row.get("equiparm", 0)),
            ]
            self.equipitemsgear = [
                int(row.get("equipminibot", 0)),
                int(row.get("equipgun", 0)),
                int(row.get("equipefield", 0)),
                int(row.get("equipwing", 0)),
                int(row.get("equipshield", 0)),
                int(row.get("equiparmpart", 0)),
                int(row.get("equipflag1", 0)),
                int(row.get("equipflag2", 0)),
            ]
            self.equipitemspack = [
                int(row.get("equippassivskill", 0)),
                int(row.get("equipaktivskill", 0)),
                int(row.get("equippack", 0)),
                int(row.get("equiptransbot", 0)),
                int(row.get("equipmerc", 0)),
                int(row.get("equipmerc2", 0)),
            ]
            self.equipitemscoin = [
                int(row.get("equipheadcoin", 0)),
                int(row.get("equipminibotcoin", 0)),
            ]

        inv_rows = self.sql.query("SELECT * FROM bout_inventory WHERE name=%s LIMIT 1", (self.botname,))
        if inv_rows:
            row = inv_rows[0]
            for idx in range(10):
                self.inventitems[idx] = int(row.get(f"item{idx + 1}", 0))

        coin_rows = self.sql.query("SELECT coins FROM bout_users WHERE username=%s LIMIT 1", (self.account,))
        if coin_rows:
            self.coins = int(coin_rows[0].get("coins", 0))

    def load_equip_bonus(self) -> None:
        self.hpb = 0
        self.attminb = 0
        self.attmaxb = 0
        self.attmintransb = 0
        self.attmaxtransb = 0
        self.transgaugeb = 0
        self.critb = 0
        self.evadeb = 0
        self.spectransb = 0
        self.speedb = 0
        self.transdefb = 0
        self.transbotattb = 0
        self.transspeedb = 0
        self.rangeattb = 0
        self.lukb = 0

        for value in self.equipitemspart + self.equipitemsgear + self.equipitemspack + self.equipitemscoin:
            if value:
                script = self.item.get_item_script(value)
                if script:
                    self.parse_script(script)

    def parse_script(self, script: str) -> None:
        while True:
            idx = script.find(";")
            if idx == -1 or idx < 5:
                break
            chunk = script[:idx]
            script = script[idx + 2 :]
            if "," not in chunk:
                continue
            stat, value = chunk.split(",", 1)
            try:
                self.parse_stat(stat, int(value))
            except ValueError:
                continue

    def parse_stat(self, stat: str, value: int) -> None:
        mapping = {
            "hpp": "hpb",
            "attmin": "attminb",
            "attmax": "attmaxb",
            "atttransmin": "attmintransb",
            "atttransmax": "attmaxtransb",
            "transgauge": "transgaugeb",
            "crit": "critb",
            "evade": "evadeb",
            "spectrans": "spectransb",
            "speed": "speedb",
            "transbotdef": "transdefb",
            "transbotatt": "transbotattb",
            "transspeed": "transspeedb",
            "luk": "lukb",
            "rangeatt": "rangeattb",
        }
        attr = mapping.get(stat)
        if attr:
            setattr(self, attr, getattr(self, attr) + value)

    def _to_bytes(self, value: int, num: int) -> bytes:
        return value.to_bytes(num, "little", signed=False)

    def get_packet_cinfo(self) -> bytes:
        self.load_equip_bonus()
        packet = bytearray()
        nullbyte = b"\x00"

        charname = self.botname.encode("latin-1")
        charname = charname.ljust(15, nullbyte)

        packet.extend(charname)
        packet.extend(self._to_bytes(self.bottype, 2))
        packet.extend(self._to_bytes(self.exp, 4))
        packet.extend(self._to_bytes(self.level, 2))
        packet.extend(self._to_bytes(self.hp + self.hpb, 2))
        packet.extend(self._to_bytes(self.gigas, 4))
        packet.extend(self._to_bytes(self.attmin + self.attminb, 2))
        packet.extend(self._to_bytes(self.attmax + self.attmaxb, 2))
        packet.extend(self._to_bytes(self.attmintrans + self.attmintransb, 2))
        packet.extend(self._to_bytes(self.attmaxtrans + self.attmaxtransb, 2))
        packet.extend(self._to_bytes(800, 2))
        packet.extend(self._to_bytes(self.transgauge + self.transgaugeb, 2))
        packet.extend(self._to_bytes(self.crit + self.critb, 2))
        packet.extend(self._to_bytes(self.evade + self.evadeb, 2))
        packet.extend(self._to_bytes(self.spectrans + self.spectransb, 2))
        packet.extend(self._to_bytes(self.speed + self.speedb, 2))
        packet.extend(self._to_bytes(self.transdef + self.transdefb, 2))
        packet.extend(self._to_bytes(self.transbotatt + self.transbotattb, 2))
        packet.extend(self._to_bytes(self.transspeed + self.transspeedb, 2))
        packet.extend(self._to_bytes(self.rangeatt + self.rangeattb, 2))
        packet.extend(self._to_bytes(self.luk + self.lukb, 2))
        packet.extend(self._to_bytes(self.botstract, 4))

        packet.extend(nullbyte * 16)

        empty_item = b"\x00" * 8
        marker = b"\xFF" * 4

        for value in self.equipitemspart:
            if value == 0:
                packet.extend(empty_item)
            else:
                packet.extend(self._to_bytes(value, 4))
                packet.extend(marker)
            packet.extend(nullbyte)

        packet.extend(b"\x01")

        for value in self.inventitems:
            if value == 0:
                packet.extend(empty_item)
            else:
                packet.extend(self._to_bytes(value, 4))
                packet.extend(marker)
            packet.extend(nullbyte)

        packet.extend(self._to_bytes(self.gigas, 4))
        packet.extend(nullbyte * 12)

        packet.extend(nullbyte * 230)

        for value in self.equipitemsgear:
            if value == 0:
                packet.extend(empty_item)
            else:
                packet.extend(self._to_bytes(value, 4))
                packet.extend(marker)
            packet.extend(nullbyte)

        for value in self.equipitemspack:
            if value == 0:
                packet.extend(empty_item)
            else:
                packet.extend(self._to_bytes(value, 4))
                packet.extend(marker)
            packet.extend(nullbyte)

        packet.extend(nullbyte * 200)

        for value in self.equipitemscoin:
            if value == 0:
                packet.extend(empty_item)
            else:
                packet.extend(self._to_bytes(value, 4))
                packet.extend(marker)
            packet.extend(nullbyte)

        while len(packet) != 1374:
            packet.extend(nullbyte)

        return bytes(packet)

    def create_bot(self, username: str, name: str, bottype: int) -> int:
        self.sql.update(
            "INSERT INTO bout_characters (username, name, bot) VALUES (%s, %s, %s)",
            (username, name, bottype),
        )
        self.sql.update("INSERT INTO bout_inventory (name) VALUES (%s)", (name,))
        return 1

    def delete_bot(self, charname: str, username: str) -> int:
        self.sql.update(
            "DELETE FROM bout_characters WHERE username=%s AND name=%s",
            (username, charname),
        )
        return 1

    def check_bot(self) -> bool:
        rows = self.sql.query("SELECT id FROM bout_characters WHERE username=%s LIMIT 1", (self.account,))
        return bool(rows)

    def get_invent_packet(self, head: int) -> Packet:
        packet = Packet()
        packet.add_header(head, 0x2E)
        packet.add_packet_head(0x01, 0x00)
        packet.add_byte(0x01)
        for value in self.inventitems:
            packet.add_int(value, 4, False)
            if value == 0:
                packet.add_byte4(0x00, 0x00, 0x00, 0x00)
            else:
                packet.add_byte4(0xFF, 0xFF, 0xFF, 0xFF)
            packet.add_byte(0x00)
        packet.add_int(self.gigas, 4, False)
        return packet

    def update_bot(self) -> None:
        self.sql.update(
            "UPDATE bout_characters SET bot=%s, exp=%s, level=%s, hp=%s, gigas=%s, attmin=%s, attmax=%s, "
            "attmintrans=%s, attmaxtrans=%s, specialtrans=%s, rangeatt=%s, botstract=%s WHERE name=%s",
            (
                self.bottype,
                self.exp,
                self.level,
                self.hp,
                self.gigas,
                self.attmin,
                self.attmax,
                self.attmintrans,
                self.attmaxtrans,
                self.spectrans,
                self.rangeatt,
                self.botstract,
                self.botname,
            ),
        )

    def update_invent(self) -> None:
        fields = {f"item{i + 1}": self.inventitems[i] for i in range(10)}
        assignments = ", ".join([f"{key}=%s" for key in fields.keys()])
        self.sql.update(
            f"UPDATE bout_inventory SET {assignments} WHERE name=%s",
            tuple(fields.values()) + (self.botname,),
        )

    def update_coins(self) -> None:
        self.sql.update("UPDATE bout_users SET coins=%s WHERE username=%s", (self.coins, self.account))

    def update_equip(self) -> None:
        self.sql.update(
            "UPDATE bout_characters SET equiphead=%s, equipbody=%s, equiparm=%s, equipminibot=%s, equipgun=%s, "
            "equipefield=%s, equipwing=%s, equipshield=%s, equiparmpart=%s, equipflag1=%s, equipflag2=%s, "
            "equippassivskill=%s, equipaktivskill=%s, equippack=%s, equiptransbot=%s, equipmerc=%s, equipmerc2=%s, "
            "equipheadcoin=%s, equipminibotcoin=%s WHERE name=%s",
            (
                self.equipitemspart[0],
                self.equipitemspart[1],
                self.equipitemspart[2],
                self.equipitemsgear[0],
                self.equipitemsgear[1],
                self.equipitemsgear[2],
                self.equipitemsgear[3],
                self.equipitemsgear[4],
                self.equipitemsgear[5],
                self.equipitemsgear[6],
                self.equipitemsgear[7],
                self.equipitemspack[0],
                self.equipitemspack[1],
                self.equipitemspack[2],
                self.equipitemspack[3],
                self.equipitemspack[4],
                self.equipitemspack[5],
                self.equipitemscoin[0],
                self.equipitemscoin[1],
                self.botname,
            ),
        )

    def get_equip(self, epart: int, part: int) -> int:
        if epart == 1:
            return self.equipitemspart[part]
        if epart == 2:
            return self.equipitemsgear[part - 3]
        if epart == 3:
            return self.equipitemspack[part - 11]
        if epart == 4:
            return self.equipitemscoin[part]
        return -1

    def set_equip(self, item_id: int, epart: int, part: int) -> None:
        if epart == 1:
            self.equipitemspart[part] = item_id
        elif epart == 2:
            self.equipitemsgear[part - 3] = item_id
        elif epart == 3:
            self.equipitemspack[part - 11] = item_id
        elif epart == 4:
            self.equipitemscoin[part] = item_id
        self.update_equip()

    def slot_available(self) -> int:
        for idx, value in enumerate(self.inventitems):
            if value == 0:
                return idx
        return -1

    def equip(self, slot: int, epart: int) -> Packet:
        packet = Packet()
        if epart == 1:
            packet.add_header(0xE4, 0x2E)
        elif epart == 2:
            packet.add_header(0x19, 0x2F)
        else:
            packet.add_header(0x1B, 0x2F)

        aid = self.inventitems[slot]
        if aid == 0:
            packet.add_packet_head(0x00, 0x60)
            return packet

        item_info = self.item.get_item_info(aid)
        if not item_info:
            packet.add_packet_head(0x00, 0x60)
            return packet

        if int(item_info.get("reqlevel", 0)) > self.level:
            packet.add_packet_head(0x00, 0x65)
            return packet

        bott = int(item_info.get("bot", 0))
        if bott not in (0, self.bottype):
            packet.add_packet_head(0x00, 0x60)
            return packet

        part = int(item_info.get("part", 0)) - 1
        if part == 17:
            epart = 4
            part = 0
        elif part == 18:
            epart = 4
            part = 1

        old = self.get_equip(epart, part)
        if part == 15 and old != 0:
            old2 = self.get_equip(epart, part + 1)
            if old2 == 0:
                old = 0
                part += 1

        if old != -1:
            self.inventitems[slot] = old
            self.set_equip(aid, epart, part)
            packet.set_packet(self.get_packet_cinfo())
            return packet

        packet.add_packet_head(0x00, 0x60)
        return packet

    def deequip(self, slot: int, epart: int) -> Packet:
        packet = Packet()
        if epart == 1:
            packet.add_header(0xE5, 0x2E)
            if slot == 0 and self.equipitemscoin[0] != 0:
                epart = 4
        elif epart == 2:
            packet.add_header(0x1A, 0x2F)
            if slot == 0 and self.equipitemscoin[1] != 0:
                epart = 4
                slot = 1
            else:
                slot += 3
        else:
            packet.add_header(0x1C, 0x2F)
            slot += 11

        aid = self.get_equip(epart, slot)
        if aid == 0:
            packet.add_packet_head(0x00, 0x60)
            return packet

        islot = self.slot_available()
        if islot != -1:
            self.inventitems[islot] = aid
            self.set_equip(0, epart, slot)
            packet.set_packet(self.get_packet_cinfo())
            return packet

        packet.add_packet_head(0x00, 0x61)
        return packet

    def get_equip_by_name(self, charname: str) -> Optional[Packet]:
        rows = self.sql.query("SELECT * FROM bout_characters WHERE name=%s LIMIT 1", (charname,))
        if not rows:
            return None
        row = rows[0]
        packet = Packet()
        packet.add_header(0x27, 0x2F)
        packet.add_int(1, 4, False)
        packet.add_int(int(row.get("level", 0)), 2, False)
        packet.add_int(0, 2, False)
        for idx in range(11):
            packet.add_int(int(row.get(list(row.keys())[idx + 24], 0)), 4, False)
        packet.add_int(int(row.get("equipheadcoin", 0)), 4, False)
        packet.add_int(int(row.get("equipminibotcoin", 0)), 4, False)
        packet.add_byte(0x00)
        packet.add_byte(int(row.get("bot", 0)))
        packet.add_byte(0x01)
        packet.add_byte(0x00)
        packet.add_string(charname)
        return packet

    def set_invent(self, item: int, slot: int) -> None:
        self.inventitems[slot] = item
        self.update_invent()

    def set_gigas(self, gigas: int) -> None:
        self.gigas = gigas
        self.update_bot()

    def set_coins(self, coins: int) -> None:
        self.coins = coins
        self.update_coins()

    def get_invent_all(self) -> list[int]:
        return self.inventitems

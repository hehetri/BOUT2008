"""Shop handling for buy/sell actions."""
from __future__ import annotations

from .bot import BotClass
from .item import ItemClass
from .packet import Packet


class Shop:
    head_buy = 0xEA
    head_sell = 0xEB
    head_buycoins = 0xEC

    nogigas = 0x41
    nocoins = 0x41
    noitem = 0x42
    noslot = 0x44

    def __init__(self, bot: BotClass, item: ItemClass) -> None:
        self.bot = bot
        self.item = item

    def buy(self, item_id: int) -> Packet:
        price = self.item.get_buy(item_id)
        if price == -1:
            return self._error_packet(self.noitem, self.head_buy)
        if self.bot.gigas < price:
            return self._error_packet(self.nogigas, self.head_buy)
        slot = self._slot_available()
        if slot == -1:
            return self._error_packet(self.noslot, self.head_buy)
        self.bot.set_gigas(self.bot.gigas - price)
        self.bot.set_invent(item_id, slot)
        return self.bot.get_invent_packet(self.head_buy)

    def buy_coin(self, item_id: int) -> Packet:
        price = self.item.get_buy_coins(item_id)
        if price == -1:
            return self._error_packet(self.noitem, self.head_buycoins)
        if self.bot.coins < price:
            return self._error_packet(self.nocoins, self.head_buycoins)
        slot = self._slot_available()
        if slot == -1:
            return self._error_packet(self.noslot, self.head_buycoins)
        self.bot.set_coins(self.bot.coins - price)
        self.bot.set_invent(item_id, slot)
        return self.bot.get_invent_packet(self.head_buycoins)

    def sell(self, item_id: int, slot: int) -> Packet:
        price = self.item.get_sell(item_id)
        if price == -1 or not self._item_at_slot(item_id, slot):
            return self._error_packet(self.noitem, self.head_sell)
        self.bot.set_gigas(self.bot.gigas + price)
        self.bot.set_invent(0, slot)
        return self.bot.get_invent_packet(self.head_sell)

    def _error_packet(self, error: int, head: int) -> Packet:
        packet = Packet()
        packet.add_header(head, 0x2E)
        packet.add_packet_head(0x00, error)
        for _ in range(95):
            packet.add_byte(0xCC)
        return packet

    def _slot_available(self) -> int:
        for idx, value in enumerate(self.bot.get_invent_all()):
            if value == 0:
                return idx
        return -1

    def _item_at_slot(self, item_id: int, slot: int) -> bool:
        return self.bot.inventitems[slot] == item_id

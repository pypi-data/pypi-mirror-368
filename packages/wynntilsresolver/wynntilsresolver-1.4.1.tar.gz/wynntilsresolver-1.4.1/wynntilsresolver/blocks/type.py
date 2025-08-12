"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-28 22:57:36
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-07 18:53:01
FilePath     : /wynntilsresolver/blocks/type.py
"""

from typing import List, Type

from wynntilsresolver.exception import InvalidItemType

from .block import Block
from .identification import Identifications
from .name import Name
from .powder import Powder
from .reroll import Reroll
from .shiny import Shiny


class ItemType(Block):
    _start_byte: int = 1
    _type_id: int
    _required_blocks: List[Type[Block]] = []
    _optional_blocks: List[Type[Block]] = []

    def to_bytes(self) -> List[int]:
        return self.encode_with_start([self._type_id])

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"


class GearItem(ItemType):
    _type_id = 0
    _required_blocks = [Name]
    _optional_blocks = [Identifications, Powder, Reroll, Shiny]

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "GearItem":
        super().from_bytes(data)
        if data[0] != cls._type_id:
            raise InvalidItemType(f"Invalid item type {data[0]} for item {cls.__name__}")
        del data[0]
        return cls()

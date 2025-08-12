"""
    QApp Platform Project base_enum.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from enum import Enum


class BaseEnum(Enum):
    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return super().__hash__()

    @staticmethod
    def resolve(type: str):
        pass

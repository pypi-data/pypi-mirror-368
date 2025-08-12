"""
    QApp Platform Project processing_unit.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..enum.base_enum import BaseEnum


class ProcessingUnit(BaseEnum):
    CPU = 'CPU'
    GPU = 'GPU'
    QPU = 'QPU'

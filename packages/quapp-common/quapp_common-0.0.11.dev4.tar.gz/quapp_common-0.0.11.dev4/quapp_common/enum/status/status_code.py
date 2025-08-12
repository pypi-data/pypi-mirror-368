"""
    QApp Platform Project status_code.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from enum import Enum


class StatusCode(Enum):
    DONE = 0
    ERROR = 1
    POLLING = 2

"""
    QApp Platform Project job_status.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from enum import Enum


class JobStatus(Enum):
    ERROR = 'ERROR'
    COMPLETED = 'COMPLETED'
    DONE = 'DONE'

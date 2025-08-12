"""
    QApp Platform Project invocation_step.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..enum.base_enum import BaseEnum


class InvocationStep(BaseEnum):
    POLLING = "POLLING"
    PREPARATION = "PREPARATION"
    EXECUTION = "EXECUTION"
    ANALYSIS = "ANALYSIS"
    FINALIZATION = "FINALIZATION"
    PROMISE = "PROMISE"

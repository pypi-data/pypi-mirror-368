"""
    QApp Platform Project async_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC, abstractmethod


class AsyncTask(ABC):

    @abstractmethod
    def do(self):
        pass

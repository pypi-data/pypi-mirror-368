#  Quapp Platform Project
#  handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod

from quapp_common.config.logging_config import job_logger


class Handler(ABC):

    def __init__(self, request_data: dict, post_processing_fn):
        self.request_data = request_data
        self.post_processing_fn = post_processing_fn
        self.job_id = request_data.get('jobId')
        self.logger = job_logger(self.job_id)
        self.logger.info(f'Init Handler with values: {self.__dict__.keys()}')

    @abstractmethod
    def handle(self):
        """

        """
        raise NotImplementedError(
                '[Handler] handle() method must be implemented')

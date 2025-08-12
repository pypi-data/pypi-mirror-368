"""
    QApp Platform Project handler_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC

from ..config.logging_config import *
from ..handler.handler import Handler


class HandlerFactory(ABC):

    @staticmethod
    def create_handler(
            event,
            circuit_preparation_fn,
            post_processing_fn,
    ) -> Handler:
        logger.debug("Create InvocationHandler")

        raise NotImplementedError(
            '[HandlerFactory] create_handler() method must be implemented')

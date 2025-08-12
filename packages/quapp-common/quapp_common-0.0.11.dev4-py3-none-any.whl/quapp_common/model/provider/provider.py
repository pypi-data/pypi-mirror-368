"""
    QApp Platform Project provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC, abstractmethod

from ...config.logging_config import logger
from ...enum.provider_tag import ProviderTag

logger = logger.bind(context='Provider')


class Provider(ABC):

    def __init__(self, provider_type: ProviderTag):
        self.provider_type = provider_type

    @abstractmethod
    def get_backend(self, device_specification):
        """
        @param device_specification:
        """

        raise NotImplementedError('[Provider] get_backend() method must be implemented')

    @abstractmethod
    def collect_provider(self):
        """

        """

        raise NotImplementedError('[Provider] collect_provider() method must be implemented')

    def get_provider_type(self):
        logger.debug('Get provider type')

        return self.provider_type

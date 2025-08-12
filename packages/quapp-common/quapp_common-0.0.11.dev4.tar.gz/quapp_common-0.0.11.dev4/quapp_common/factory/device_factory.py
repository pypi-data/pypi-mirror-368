"""
    QApp Platform Project device_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC

from ..enum.sdk import Sdk
from ..model.provider.provider import Provider


class DeviceFactory(ABC):

    @staticmethod
    def create_device(provider: Provider, device_specification: str,
                      authentication: dict, sdk: Sdk):
        """
        @param sdk:
        @param provider:
        @param device_specification:
        @param authentication:
        @return:
        """

        raise NotImplementedError(
            '[DeviceFactory] create_device() method must be implemented')

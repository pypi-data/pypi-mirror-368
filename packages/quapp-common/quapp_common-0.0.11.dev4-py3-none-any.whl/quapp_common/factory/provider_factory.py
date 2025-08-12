"""
    QApp Platform Project provider_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC

from ..enum.provider_tag import ProviderTag
from ..enum.sdk import Sdk


class ProviderFactory(ABC):

    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk,
                        authentication: dict):
        """

        @param sdk:
        @param provider_type:
        @param authentication:
        @return:
        """

        raise NotImplementedError(
            '[ProviderFactory] create_provider() method must be implemented')

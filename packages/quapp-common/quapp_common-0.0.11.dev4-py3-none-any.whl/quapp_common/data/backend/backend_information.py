"""
    QApp Platform Project backend_information.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ...enum.provider_tag import ProviderTag


class BackendInformation:
    def __init__(self,
                 device_name: str,
                 provider_tag: ProviderTag,
                 authentication: dict):
        self.device_name = device_name
        self.provider_tag = provider_tag
        self.authentication = authentication

"""
    QApp Platform Project backend_holder.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ...backend.backend_information import BackendInformation


class BackendDataHolder:
    def __init__(self,
                 backend_information: BackendInformation,
                 user_token: str):
        self.backend_information = backend_information
        self.user_token = user_token

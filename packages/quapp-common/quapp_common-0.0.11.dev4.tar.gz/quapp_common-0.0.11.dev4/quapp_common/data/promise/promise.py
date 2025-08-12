"""
    QApp PlatformQApp Platform Project promise.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..callback.callback_url import CallbackUrl
from ...data.response.authentication import Authentication


class Promise:
    def __init__(self, callback_url: CallbackUrl, authentication: Authentication):
        self.callback_url = callback_url
        self.authentication = authentication

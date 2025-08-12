"""
    QApp Platform Project callback_url.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""


class CallbackUrl:
    def __init__(self, callback_url: dict):
        self.on_start = callback_url.get("onStartCallbackUrl")
        self.on_error = callback_url.get("onErrorCallbackUrl")
        self.on_done = callback_url.get("onDoneCallbackUrl")

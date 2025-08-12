#  Quapp Platform Project
#  custom_header.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

class CustomHeader:
    """
    Represents a custom HTTP header.

    This class is designed to store and handle an HTTP header with a given name
    and value. It is primarily used for HTTP request or response customization.
    """

    def __init__(self, name: str, value: str = ''):
        self.name = name
        self.value = value

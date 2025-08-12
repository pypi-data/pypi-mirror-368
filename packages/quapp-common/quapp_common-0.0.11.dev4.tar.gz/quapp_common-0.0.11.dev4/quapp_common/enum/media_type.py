"""
    QApp Platform Project media_type.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..enum.base_enum import BaseEnum


class MediaType(BaseEnum):
    APPLICATION_JSON = 'application/json'
    ALL_TYPE = '*/*'
    MULTIPART_FORM_DATA = 'multipart/form-data'
    APPLICATION_ZIP = 'application/zip'
    SVG_XML = 'image/svg+xml'

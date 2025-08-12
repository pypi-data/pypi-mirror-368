"""
    QApp Platform Project file_utils.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO


class FileUtils:
    @staticmethod
    def zip(io_buffer_value, file_name):
        """

        @param io_buffer_value:
        @param file_name:
        @return:
        """

        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, mode="w", compression=ZIP_DEFLATED) as zf:
            zf.writestr(file_name, io_buffer_value)

        return zip_buffer

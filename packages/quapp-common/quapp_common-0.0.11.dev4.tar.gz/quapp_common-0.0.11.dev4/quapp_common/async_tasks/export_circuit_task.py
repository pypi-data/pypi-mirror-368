#  Quapp Platform Project
#  export_circuit_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import abstractmethod
from io import BytesIO

import requests

from .async_task import AsyncTask
from ..config.logging_config import job_logger
from ..data.async_task.circuit_export.backend_holder import BackendDataHolder
from ..data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from ..enum.media_type import MediaType
from ..util.file_utils import FileUtils
from ..util.http_utils import create_bearer_header, get_job_id_from_url


class CircuitExportTask(AsyncTask):
    MAX_CIRCUIT_IMAGE_SIZE = 5 * (1024 ** 2)

    def __init__(self, circuit_data_holder: CircuitDataHolder,
                 backend_data_holder: BackendDataHolder):
        super().__init__()
        self.circuit_data_holder = circuit_data_holder
        self.backend_data_holder = backend_data_holder
        self.logger = job_logger(
                get_job_id_from_url(self.circuit_data_holder.export_url))

    def do(self):
        """
          Export circuit to svg file, then send it to QuaO server for saving
        """
        self.logger.info("Starting circuit export task...")

        circuit_export_url = self.circuit_data_holder.export_url

        if circuit_export_url is None or len(circuit_export_url) < 1:
            self.logger.warning("Export URL is missing. Task will exit.")
            return

        try:
            self.logger.debug('Converting circuit to SVG')
            figure_buffer = self.__convert()
        except Exception as e:
            self.logger.error(f"Error converting circuit to SVG: {e}",
                              exc_info=True)
            return

        try:
            self.logger.debug('Determining if circuit SVG should be zipped')
            io_buffer_value, content_type = self.__determine_zip(
                    figure_buffer=figure_buffer)
            self.logger.debug(f"Content type: {content_type}")
            self.logger.debug(f"Buffer size: {len(io_buffer_value)} bytes")
        except Exception as e:
            self.logger.error(
                    f"Error determining if circuit SVG should be zipped: {e}",
                    exc_info=True)
            return

        try:
            self.logger.debug('Sending circuit to backend')
            self.__send(io_buffer_value=io_buffer_value,
                        content_type=content_type)
            self.logger.debug("Circuit sent to backend successfully.")
        except Exception as e:
            self.logger.error(f"Error sending exported circuit to backend: {e}",
                              exc_info=True)

        self.logger.info("Circuit export task finished.")

    def __convert(self):
        """
        Convert circuit to SVG, return as BytesIO.
        """
        self.logger.debug("Preparing circuit figure...")
        transpiled_circuit = self._transpile_circuit()
        self.logger.debug("Transpiled circuit successfully.")

        try:
            circuit_figure = transpiled_circuit.draw(output='mpl', fold=-1)
        except Exception as exception:
            self.logger.error(f"Error drawing circuit: {exception}",
                              exc_info=True)
            raise exception

        self.logger.debug("Converting circuit figure to SVG file...")
        figure_buffer = BytesIO()
        try:
            circuit_figure.savefig(figure_buffer, format='svg',
                                   bbox_inches='tight')
            self.logger.debug(
                    f"SVG export complete. Size: {figure_buffer.getbuffer().nbytes} bytes")
        except Exception as exception:
            self.logger.error(
                    f"Error saving circuit figure to SVG: {exception}",
                    exc_info=True)
            raise exception

        return figure_buffer

    def __determine_zip(self, figure_buffer):
        """
        Determine if the buffer needs to be zipped; return (buffer, content_type).
        """
        self.logger.debug("Checking if SVG file needs to be zipped.")
        buffer_value = figure_buffer.getvalue()
        content_type = MediaType.SVG_XML

        self.logger.debug("Checking max file size")
        estimated_file_size = len(buffer_value)

        if estimated_file_size > CircuitExportTask.MAX_CIRCUIT_IMAGE_SIZE:
            self.logger.debug("Zip file")
            zip_file_buffer = FileUtils.zip(io_buffer_value=buffer_value,
                                            file_name="circuit_image.svg")

            buffer_value = zip_file_buffer.getvalue()
            content_type = MediaType.APPLICATION_ZIP

        return buffer_value, content_type

    def __send(self, io_buffer_value, content_type: MediaType):
        """
       Send circuit SVG (or zipped SVG) to the backend.
       """
        url = self.circuit_data_holder.export_url

        self.logger.debug(
                f"Sending circuit svg image to [{url}] with POST method ...")

        payload = {'circuit': ('circuit_image.svg', io_buffer_value,
                               content_type.value)}

        try:
            response = requests.post(url=url, headers=create_bearer_header(
                    self.backend_data_holder.user_token), files=payload)
        except Exception as exception:
            self.logger.error(f"HTTP request failed: {exception}",
                              exc_info=True)
            raise

        if response.ok:
            self.logger.info("Request sent to QuaO backend successfully.")
        else:
            self.logger.error(
                    f"Sending request to QuaO backend failed with status {response.status_code}! Response: {response.content}")

        self.logger.debug("HTTP request complete.")

    @abstractmethod
    def _transpile_circuit(self):
        """
        Should be implemented in subclass to return transpiled circuit.
        """
        self.logger.debug(
                "Calling _transpile_circuit (must be implemented in subclass)")

        raise NotImplementedError(
                '[CircuitExportTask] __transpile_circuit() method must be implemented')

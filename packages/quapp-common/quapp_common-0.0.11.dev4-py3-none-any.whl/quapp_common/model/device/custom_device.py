#  Quapp Platform Project
#  custom_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod

from ...component.callback.update_job_metadata import update_job_metadata
from ...data.callback.callback_url import CallbackUrl
from ...data.response.job_response import JobResponse
from ...model.device.device import Device
from ...model.provider.provider import Provider
from ...util.response_utils import build_error_job_response


class CustomDevice(Device, ABC):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.shots = None

    def _on_analysis(self, job_response: JobResponse,
                     analysis_callback: CallbackUrl, original_job_result):
        """

        @param job_response:
        @param analysis_callback:
        @param original_job_result:
        @return:
        """
        from ...util.json_parser_utils import parse

        self.logger.debug("On analysis started")

        update_job_metadata(job_response, analysis_callback.on_start)

        try:
            self.logger.debug(
                    "Producing histogram data from original job result")

            job_response.job_histogram = self._produce_histogram_data(
                    original_job_result)

            self.logger.debug("Parsing original job result")
            original_job_result_dict = parse(original_job_result)

            self.logger.debug("Calculating execution time from parsed results")
            self._calculate_execution_time(original_job_result_dict)
            job_response.execution_time = self.execution_time

            self.logger.debug("Retrieving shot count from job result")
            job_response.shots = self._get_shots(original_job_result)

            update_job_metadata(job_response, analysis_callback.on_done)

            self.logger.info("Analysis completed successfully")
            return job_response

        except Exception as exception:
            self.logger.error(
                    f"Exception when analyzing job result: {exception}",
                    exc_info=True)

            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when analyzing job result')

            update_job_metadata(job_response, analysis_callback.on_error)
            return None

    @abstractmethod
    def _get_shots(self, job_result) -> int:
        """
        Retrieve the number of shots from the job result.

        This method extracts the 'shots' value from the provided job result
        dictionary and logs the action for debugging purposes.

        Args:
            job_result (dict): A dictionary containing the results of a job,
                               which is expected to include the key 'shots'.

        Returns:
            int: The number of shots retrieved from the job result.
                 If the key 'shots' do not exist, it will return None.

        Raises:
            KeyError: If the job_result does not contain the 'shots' key,
                       and the implementation does not handle it.
        """
        raise NotImplementedError(
                "[CustomDevice] Subclasses must implement this "
                "method")

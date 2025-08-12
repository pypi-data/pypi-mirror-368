#  Quapp Platform Project
#  device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod

from ...async_tasks.post_processing_task import PostProcessingTask
from ...component.callback.update_job_metadata import update_job_metadata
from ...config.logging_config import job_logger
from ...data.callback.callback_url import CallbackUrl
from ...data.device.circuit_running_option import CircuitRunningOption
from ...data.promise.post_processing_promise import PostProcessingPromise
from ...data.response.authentication import Authentication
from ...data.response.custom_header import CustomHeader
from ...data.response.job_response import JobResponse
from ...enum.invocation_step import InvocationStep
from ...enum.media_type import MediaType
from ...enum.status.job_status import JobStatus
from ...enum.status.status_code import StatusCode
from ...model.provider.provider import Provider
from ...util.http_utils import get_job_id_from_url
from ...util.response_utils import build_error_job_response


class Device(ABC):
    def __init__(self, provider: Provider, device_specification: str):
        self.provider = provider
        self.device = provider.get_backend(device_specification)
        self.execution_time = None
        self.logger = job_logger()

    def run_circuit(self, circuit, post_processing_fn,
                    options: CircuitRunningOption, callback_dict: dict,
                    authentication: Authentication,
                    project_header: CustomHeader,
                    workspace_header: CustomHeader):
        """

        @param project_header: project header
        @param callback_dict: callback url dictionary
        @param options: Options for run circuit
        @param authentication: Authentication for calling quao server
        @param post_processing_fn: Post-processing function
        @param circuit: Circuit was run
        """
        self.logger = job_logger(get_job_id_from_url(
                callback_dict.get(InvocationStep.EXECUTION).on_done))

        self.logger.info(
                f"Run circuit started with device {self.device} and options {options}")

        original_job_result, job_response = self._on_execution(
                authentication=authentication, project_header=project_header,
                workspace_header=workspace_header,
                execution_callback=callback_dict.get(InvocationStep.EXECUTION),
                circuit=circuit, options=options)

        if original_job_result is None:
            self.logger.warning(
                    "Execution returned no job result; aborting further processing")
            return

        job_response = self._on_analysis(job_response=job_response,
                                         original_job_result=original_job_result,
                                         analysis_callback=callback_dict.get(
                                                 InvocationStep.ANALYSIS))

        if job_response is None:
            self.logger.warning(
                    "Analysis returned no job response; aborting finalization")
            return

        self._on_finalization(job_result=original_job_result,
                              authentication=authentication,
                              post_processing_fn=post_processing_fn,
                              finalization_callback=callback_dict.get(
                                      InvocationStep.FINALIZATION),
                              project_header=project_header,
                              workspace_header=workspace_header)

        self.logger.info("Run circuit completed")

    def _on_execution(self, authentication: Authentication,
                      project_header: CustomHeader,
                      workspace_header: CustomHeader,
                      execution_callback: CallbackUrl, circuit,
                      options: CircuitRunningOption):
        """

        @param authentication: authentication information
        @param project_header: project header information
        @param execution_callback: execution step callback urls
        @param circuit: circuit will be run
        @param options: options will use for running
        @return: job and job response
        """
        self.logger.debug("On execution started")

        job_response = JobResponse(authentication=authentication,
                                   project_header=project_header,
                                   workspace_header=workspace_header,
                                   status_code=StatusCode.DONE)

        update_job_metadata(job_response=job_response,
                            callback_url=execution_callback.on_start)
        try:
            job = self._create_job(circuit=circuit, options=options)
            job_response.provider_job_id = self._get_provider_job_id(job)
            job_response.job_status = self._get_job_status(job)
            original_job_result = None

            if self._is_simulator():
                job_result = self._get_job_result(job)
                job_response.job_status = self._get_job_status(job)

                if JobStatus.ERROR.value.__eq__(job_response.job_status):
                    job_response.job_result = job_result
                    job_response.content_type = MediaType.APPLICATION_JSON
                else:
                    original_job_result = job_result
            else:
                job_response.status_code = StatusCode.POLLING

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_done)

            return original_job_result, job_response

        except Exception as exception:
            self.logger.debug(
                    "Execute job failed with error {}".format(str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.content_type = MediaType.APPLICATION_JSON
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {"error": str(exception)}

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_error)
            return None, None

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

        update_job_metadata(job_response=job_response,
                            callback_url=analysis_callback.on_start)

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

            update_job_metadata(job_response=job_response,
                                callback_url=analysis_callback.on_done)

            self.logger.info("Analysis completed successfully")
            return job_response

        except Exception as exception:
            self.logger.error(
                    f"Exception when analyzing job result: {exception}",
                    exc_info=True)

            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when analyzing job result')

            update_job_metadata(job_response=job_response,
                                callback_url=analysis_callback.on_error)
            return None

    def _on_finalization(self, job_result, finalization_callback: CallbackUrl,
                         post_processing_fn, authentication: Authentication,
                         project_header: CustomHeader,
                         workspace_header: CustomHeader):
        """

        @param job_result: final job result
        @param finalization_callback: callback for update job result
        @param post_processing_fn: post processing function
        @param authentication: authentication of quao
        @param project_header: project header
        """
        self.logger.info("On finalization started")

        if finalization_callback is None:
            self.logger.warning(
                    "Finalization callback is None, skipping finalization")

            return

        self.logger.debug("Starting PostProcessingTask")

        post_processing_promise = PostProcessingPromise(
                callback_url=finalization_callback,
                authentication=authentication, job_result=job_result,
                project_header=project_header,
                workspace_header=workspace_header)

        PostProcessingTask(post_processing_fn=post_processing_fn,
                           promise=post_processing_promise).do()

    @abstractmethod
    def _create_job(self, circuit, options: CircuitRunningOption):
        """

        @param circuit: Circuit for create job
        @param options:
        """

        raise NotImplementedError(
                '[Device] _create_job() method must be implemented')

    @abstractmethod
    def _is_simulator(self) -> bool:
        """

        """

        raise NotImplementedError(
                '[Device] _is_simulator() method must be implemented')

    @abstractmethod
    def _produce_histogram_data(self, job_result) -> dict | None:
        """

        @param job_result:
        """

        raise NotImplementedError(
                '[Device] _produce_histogram_data() method must be implemented')

    @abstractmethod
    def _get_provider_job_id(self, job) -> str:
        """

        """

        raise NotImplementedError(
                '[Device] _get_provider_job_id() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job) -> str:
        """

        """

        raise NotImplementedError(
                '[Device] _get_job_status() method must be implemented')

    @abstractmethod
    def _calculate_execution_time(self, job_result) -> float:
        """

        """

        raise NotImplementedError(
                '[Device] _calculate_execution_time() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """

        @param job:
        @return:
        """
        job_logger().debug('[Device] Get job result')

        return job.result()

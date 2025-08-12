#  Quapp Platform Project
#  job_fetcher.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod
from typing import Dict

from ...async_tasks.post_processing_task import PostProcessingTask
from ...config.logging_config import job_logger
from ...config.thread_config import circuit_running_pool
from ...data.callback.callback_url import CallbackUrl
from ...data.promise.post_processing_promise import PostProcessingPromise
from ...data.request.job_fetching_request import JobFetchingRequest
from ...data.response.authentication import Authentication
from ...data.response.custom_header import CustomHeader
from ...data.response.job_response import JobResponse
from ...enum.invocation_step import InvocationStep
from ...enum.media_type import MediaType
from ...enum.status.job_status import JobStatus
from ...enum.status.status_code import StatusCode
from ...util.json_parser_utils import parse


class JobFetcher(ABC):
    """
       Abstract base class for fetching job results from different providers.
       """

    def __init__(self, request_data: JobFetchingRequest):
        """Initializes the JobFetcher with request data."""
        self.provider_authentication: Dict = request_data.provider_authentication
        self.provider_job_id: str = request_data.provider_job_id
        self.backend_authentication: Authentication = request_data.authentication
        self.project_header: CustomHeader = request_data.project_header
        self.workspace_header: CustomHeader = request_data.workspace_header
        self.callback_urls: Dict[InvocationStep, CallbackUrl] = {
            InvocationStep.EXECUTION   : request_data.execution,
            InvocationStep.ANALYSIS    : request_data.analysis,
            InvocationStep.FINALIZATION: request_data.finalization}
        self.job_id = request_data.job_id
        self.logger = job_logger(self.job_id)
        self.logger.info(f"Initializing JobFetcher with job id: {self.job_id}")

    @abstractmethod
    def _collect_provider(self):
        """Abstract method to create and return the provider client."""
        raise NotImplementedError(
                '[JobFetcher] _collect_provider() method must be implemented')

    @abstractmethod
    def _retrieve_job(self, provider):
        """Abstract method to retrieve the job object from the provider."""
        raise NotImplementedError(
                '[JobFetcher] _retrieve_job() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job):
        """Abstract method to extract the job status from the provider's job object."""
        raise NotImplementedError(
                '[JobFetcher] _get_job_status() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """Abstract method to extract the raw job result from the provider's job object."""
        raise NotImplementedError(
                '[JobFetcher] _get_job_result() method must be implemented')

    @abstractmethod
    def _produce_histogram_data(self, job_result) -> dict | None:
        """Abstract method to produce histogram data from the raw job result."""
        raise NotImplementedError(
                '[JobFetcher] _produce_histogram_data() method must be implemented')

    @abstractmethod
    def _get_execution_time(self, job_result):
        """Abstract method to extract the execution time from the raw job result."""
        raise NotImplementedError(
                '[JobFetcher] _get_execution_time() method must be implemented')

    @abstractmethod
    def _get_shots(self, job_result):
        """Abstract method to extract the number of shots from the raw job result."""
        raise NotImplementedError(
                '[JobFetcher] _get_shots() method must be implemented')

    def fetch(self, post_processing_fn):
        """Fetches the job, handles different job statuses, and initiates post-processing."""
        from ..callback.update_job_metadata import update_job_metadata
        from ...util.response_utils import build_done_job_response, \
            build_error_job_response, generate_response

        self.logger.debug("Starting fetch for job")
        job_response = build_done_job_response(self)

        try:
            self.logger.debug('Collecting provider')
            provider = self._collect_provider()

            self.logger.debug('Retrieving job from provider')
            job = self._retrieve_job(provider)

            self.logger.debug('Getting job status')
            job_status = self._get_job_status(job)

            self.logger.debug('Getting original job result')
            original_job_result = self._get_job_result(job)

            self.logger.info('Job status: {job_status}')
            job_response.job_status = job_status

            if job_status == JobStatus.DONE.value:
                self.logger.debug("Job done, handling success")

                self._handle_successful_job(original_job_result, job_response,
                                            post_processing_fn)
                update_job_metadata(job_response, self.callback_urls[
                    InvocationStep.EXECUTION].on_done)
            elif job_status == JobStatus.ERROR.value:
                self.logger.error("Job resulted in error, handling failure")

                self._handle_failed_job(original_job_result, job_response)
                update_job_metadata(job_response, self.callback_urls[
                    InvocationStep.EXECUTION].on_error)
            else:
                self.logger.info(
                        f"Job status {job_status} indicates polling state")
                job_response.status_code = StatusCode.POLLING

        except Exception as exception:
            self.logger.error(
                    f"Exception during job fetch for provider_job_id {self.provider_job_id}: {exception}",
                    exc_info=True)

            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when fetching job with provider_job_id {0}'.format(
                                                            self.provider_job_id))
            update_job_metadata(job_response, self.callback_urls[
                InvocationStep.EXECUTION].on_error)

        self.logger.debug("Fetch finished, generating response")
        return generate_response(job_response)

    def _handle_successful_job(self, original_job_result,
                               job_response: JobResponse, post_processing_fn):
        """Handles the job result when the job is successfully completed."""
        self.logger.debug("Submitting job result for asynchronous processing")
        circuit_running_pool.submit(self._process_job_result,
                                    original_job_result, job_response,
                                    self.callback_urls, post_processing_fn)

    def _handle_failed_job(self, original_job_result,
                           job_response: JobResponse):
        """Handles the job result when the job has encountered an error."""
        self.logger.error("Parsing job result from failed job")
        job_response.job_result = parse(original_job_result)

    def _process_job_result(self, original_job_result,
                            job_response: JobResponse,
                            callback_urls: Dict[InvocationStep, CallbackUrl],
                            post_processing_fn):
        """Processes the job result through analysis and finalization steps."""
        self.logger.debug("Processing job result - analysis and finalization")

        job_response = self._on_analysis(callback_urls[InvocationStep.ANALYSIS],
                                         job_response,
                                         original_job_result=original_job_result)

        if job_response:
            self.logger.debug("Proceeding to finalization")
            self._on_finalization(post_processing_fn=post_processing_fn,
                                  callback_url=callback_urls[
                                      InvocationStep.FINALIZATION],
                                  original_job_result=original_job_result)
        else:
            self.logger.warning(
                    "Analysis returned no job response, skipping finalization")

    def _on_analysis(self, callback_url: CallbackUrl, job_response: JobResponse,
                     original_job_result) -> JobResponse | None:
        """Handles the analysis step of the job result."""
        from ...component.callback.update_job_metadata import \
            update_job_metadata
        self.logger.debug("Performing analysis step")

        update_job_metadata(job_response, callback_url.on_start)
        self.logger.debug('Calling update_job_metadata on_start')

        try:
            job_response.content_type = MediaType.APPLICATION_JSON

            self.logger.debug("Producing histogram data")
            job_response.job_histogram = self._produce_histogram_data(
                    original_job_result)

            self.logger.debug('Getting execution time')
            job_response.execution_time = self._get_execution_time(
                    original_job_result)

            self.logger.debug('Getting shots')
            job_response.shots = self._get_shots(original_job_result)

            update_job_metadata(job_response, callback_url.on_done)
            self.logger.debug("Analysis step done")

            return job_response

        except Exception as exception:
            self.logger.error(f"Exception during analysis: {exception}",
                              exc_info=True)
            from ...util.response_utils import build_error_job_response
            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when analyzing job result')

            update_job_metadata(job_response, callback_url.on_error)
            return None

    def _on_finalization(self, post_processing_fn, callback_url: CallbackUrl,
                         original_job_result):
        """Handles the finalization step of the job result."""
        self.logger.debug("Performing finalization step")

        promise = PostProcessingPromise(callback_url,
                                        authentication=self.backend_authentication,
                                        job_result=original_job_result,
                                        project_header=self.project_header,
                                        workspace_header=self.workspace_header)

        self.logger.debug("Submitting post-processing task")
        PostProcessingTask(post_processing_fn, promise).do()

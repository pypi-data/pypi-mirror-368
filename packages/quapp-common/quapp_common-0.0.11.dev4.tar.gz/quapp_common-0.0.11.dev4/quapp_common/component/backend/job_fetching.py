#  Quapp Platform Project
#  job_fetching.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod
from typing import Any

from ..callback.update_job_metadata import update_job_metadata
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
from ...util.response_utils import build_done_job_response, \
    build_error_job_response, generate_response


class JobFetching(ABC):
    def __init__(self, request_data: JobFetchingRequest):
        self.provider_authentication: dict = request_data.provider_authentication
        self.provider_job_id: str = request_data.provider_job_id
        self.backend_authentication: Authentication = request_data.authentication
        self.project_header: CustomHeader = request_data.project_header
        self.workspace_header: CustomHeader = request_data.workspace_header
        self.callback_dict: dict = {
            InvocationStep.EXECUTION   : request_data.execution,
            InvocationStep.ANALYSIS    : request_data.analysis,
            InvocationStep.FINALIZATION: request_data.finalization}
        self.logger = job_logger(request_data.job_id)

    def fetch(self, post_processing_fn):
        """

        @param post_processing_fn:
        @return:
        """
        self.logger.debug("Fetch job")

        job_response = build_done_job_response()

        try:
            self.logger.debug("Collecting provider")
            provider = self._collect_provider()

            self.logger.debug("Retrieving job from provider")
            job = self._retrieve_job(provider)

            self.logger.debug("Getting job status")
            job_status = self._get_job_status(job)

            self.logger.debug("Getting job result")
            original_job_result = self._get_job_result(job)

            self.logger.info(f"Job status: {job_status}")
            job_response.job_status = job_status

            if JobStatus.DONE.value.__eq__(job_response.job_status):
                self.logger.debug("Job done, handling success")

                circuit_running_pool.submit(self.__handle_job_result,
                                            original_job_result, job_response,
                                            self.callback_dict,
                                            post_processing_fn)

                update_job_metadata(job_response, self.callback_dict.get(
                        InvocationStep.EXECUTION).on_done)

            elif JobStatus.ERROR.value.__eq__(job_response.job_status):
                self.logger.error("Job resulted in error, handling failure")

                job_response.job_result = parse(original_job_result)

                update_job_metadata(job_response, self.callback_dict.get(
                        InvocationStep.EXECUTION).on_error)

            else:
                self.logger.info(
                    f"Job status {job_status} indicates polling state")

                job_response.status_code = StatusCode.POLLING

        except Exception as exception:
            self.logger.debug(
                    "Exception when fetch job with provider_job_id {0}: {1}".format(
                            self.provider_job_id, str(exception)))

            job_response = build_error_job_response(exception, job_response,
                                                    message='Exception when fetch job with provider_job_id {0}'.format(
                                                            self.provider_job_id))

            update_job_metadata(job_response, self.callback_dict.get(
                    InvocationStep.EXECUTION).on_error)

        return generate_response(job_response)

    def __handle_job_result(self, original_job_result,
                            job_response: JobResponse, callback_dict: dict,
                            post_processing_fn):
        """
        Fetch job from IBM Quantum

        @return: Job status
        """

        job_response = self.__on_analysis(
                callback_url=callback_dict.get(InvocationStep.ANALYSIS),
                job_response=job_response,
                original_job_result=original_job_result)

        if job_response is None:
            self.logger.debug("Job response is None")
            return

        self.__on_finalization(post_processing_fn=post_processing_fn,
                               callback_url=callback_dict.get(
                                       InvocationStep.FINALIZATION),
                               original_job_result=original_job_result)

    def __on_analysis(self, callback_url: CallbackUrl,
                      job_response: JobResponse, original_job_result):
        """

        @param callback_url:
        @param job_response:
        @param original_job_result:
        @return:
        """
        self.logger.debug("On analysis")

        update_job_metadata(job_response, callback_url.on_start)

        try:
            job_response.content_type = MediaType.APPLICATION_JSON

            job_response.job_histogram = self.__produce_histogram_data(
                    original_job_result)

            job_response.execution_time = self.__get_execution_time(
                    original_job_result)

            update_job_metadata(job_response, callback_url.on_done)

            return job_response

        except Exception as exception:
            self.logger.error(
                    "Exception when analyst job result with provider_job_id {0}: {1}".format(
                            self.provider_job_id, str(exception)))

            job_response = build_error_job_response(exception, job_response,
                                                    message='Exception when analyst job result with provider_job_id {0}'.format(
                                                            self.provider_job_id))

            update_job_metadata(job_response, callback_url.on_error)

            return None

    def __on_finalization(self, post_processing_fn, callback_url: CallbackUrl,
                          original_job_result):
        """

        @param post_processing_fn:
        @param callback_url:
        @param original_job_result:
        """
        self.logger.debug("On finalization")

        promise = PostProcessingPromise(callback_url=callback_url,
                                        authentication=self.backend_authentication,
                                        job_result=original_job_result.result(),
                                        project_header=self.project_header,
                                        workspace_header=self.workspace_header)

        PostProcessingTask(post_processing_fn=post_processing_fn,
                           promise=promise).do()

    @staticmethod
    def __produce_histogram_data(job_result) -> Any | None:
        """

        @param job_result:
        @return:
        """
        self.logger.debug("Produce histogram")

        try:
            histogram_data = job_result.result()[0].data.meas.get_counts()

        except Exception as e:
            self.logger.debug(
                    "Can't produce histogram with error: {0}".format(str(e)))
            histogram_data = None

        return histogram_data

    @staticmethod
    def __get_execution_time(job_result):
        """

        @param job_result:
        @return:
        """
        return job_result.usage()

    @abstractmethod
    def _collect_provider(self, ):
        """
        Create a provider with ProviderFactory
        """

        raise NotImplementedError(
                '[Invocation] _create_provider() method must be implemented')

    @abstractmethod
    def _retrieve_job(self, provider):
        """
        Retrieve a job from a provider
        """

        raise NotImplementedError(
                '[Invocation] _retrieve_job() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job):
        """
        Get job status
        """

        raise NotImplementedError(
                '[Invocation] _get_job_status() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """
        Get a job result
        """

        raise NotImplementedError(
                '[Invocation] _get_job_result() method must be implemented')

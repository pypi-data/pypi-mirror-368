"""
    QApp Platform Project post_processing_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from .async_task import AsyncTask
from ..config.logging_config import job_logger
from ..data.promise.post_processing_promise import PostProcessingPromise
from ..enum.media_type import MediaType
from ..util.http_utils import get_job_id_from_url
from ..util.json_parser_utils import parse


class PostProcessingTask(AsyncTask):
    def __init__(self, post_processing_fn, promise: PostProcessingPromise):
        self.post_processing_fn = post_processing_fn
        self.promise = promise
        self.logger = job_logger(
                get_job_id_from_url(self.promise.callback_url.on_done))

    def do(self):
        """
           Execute post_processing and send to backend
        """
        from ..component.callback.update_job_metadata import update_job_metadata
        from ..util.response_utils import build_done_job_response, \
            build_error_job_response

        job_response = build_done_job_response(post_promise=self.promise)

        update_job_metadata(job_response, self.promise.callback_url.on_start)

        job_response.content_type = MediaType.APPLICATION_JSON

        try:
            self.logger.info("Execute post_processing ...")
            job_result_post_processing = self.post_processing_fn(
                    self.promise.job_result)

            self.logger.debug("Parsing job result....")
            print(job_result_post_processing)
            job_response.job_result = parse(job_result_post_processing)

            update_job_metadata(job_response, self.promise.callback_url.on_done)

        except Exception as exception:
            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when post processing job result')

            update_job_metadata(job_response,
                                self.promise.callback_url.on_error)

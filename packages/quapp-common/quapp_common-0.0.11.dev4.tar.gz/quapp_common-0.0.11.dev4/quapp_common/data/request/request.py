#  Quapp Platform Project
#  request.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from ..response.authentication import Authentication
from ..response.custom_header import CustomHeader
from ...config.logging_config import job_logger
from ...data.callback.callback_url import CallbackUrl
from ...util.http_utils import get_custom_header


class Request:
    def __init__(self, request_data):
        self.provider_job_id = request_data.get("providerJobId")
        self.job_id = request_data.get('jobId')
        self.authentication: Authentication = Authentication(
                user_token=request_data.get("userToken"),
                user_identity=request_data.get("userIdentity"))
        self.execution = CallbackUrl(request_data.get("execution"))
        self.analysis: CallbackUrl = CallbackUrl(request_data.get("analysis"))
        finalization_callback = request_data.get("finalization")
        self.finalization: CallbackUrl = CallbackUrl(
                finalization_callback) if finalization_callback else finalization_callback
        self.project_header: CustomHeader = get_custom_header(request_data,
                                                              'projectHeader')
        self.workspace_header: CustomHeader = get_custom_header(request_data,
                                                                'workspaceHeader')
        self.logger = job_logger(self.job_id)
        self.logger.info(
                f"Initializing Request with job id: {self.job_id} and provider job id: {self.provider_job_id}"
        )

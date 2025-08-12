#  Quapp Platform Project
#  post_processing_promise.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from ..callback.callback_url import CallbackUrl
from ..response.authentication import Authentication
from ..response.custom_header import CustomHeader
from ...data.promise.promise import Promise


class PostProcessingPromise(Promise):
    def __init__(self, callback_url: CallbackUrl,
                 authentication: Authentication, job_result,
                 project_header: CustomHeader, workspace_header: CustomHeader):
        super().__init__(callback_url, authentication)
        self.job_result = job_result
        self.project_header = project_header
        self.workspace_header = workspace_header

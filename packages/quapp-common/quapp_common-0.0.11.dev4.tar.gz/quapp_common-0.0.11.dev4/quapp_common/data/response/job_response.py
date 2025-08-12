#  Quapp Platform Project
#  job_response.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from .authentication import Authentication
from .custom_header import CustomHeader
from ...enum.media_type import MediaType
from ...enum.status.status_code import StatusCode


class JobResponse(object):
    def __init__(self, provider_job_id: str = "", job_status: str = None,
                 status_code: StatusCode = None, job_result: dict = None,
                 content_type: MediaType = MediaType.ALL_TYPE,
                 authentication: Authentication = None,
                 project_header: CustomHeader = None,
                 workspace_header: CustomHeader = None,
                 job_histogram: dict = None, execution_time: float = None,
                 job_id: str = None):
        self.job_id = job_id
        self.provider_job_id = provider_job_id
        self.job_status = job_status
        self.job_result = job_result
        self.content_type = content_type
        self.job_histogram = job_histogram
        self.user_identity = authentication.user_identity
        self.user_token = authentication.user_token
        self.execution_time = execution_time
        self.status_code = status_code
        self.project_header = project_header
        self.workspace_header = workspace_header

'''
    QApp Platform Project response_utils.py Copyright © CITYNOW Co. Ltd. All rights reserved.
'''

from ..component.backend.job_fetcher import JobFetcher
from ..config.logging_config import job_logger
from ..data.promise.post_processing_promise import PostProcessingPromise
from ..data.response.job_response import JobResponse
from ..enum.status.job_status import JobStatus
from ..enum.status.status_code import StatusCode

AUTHENTICATION = 'authentication'
BACKEND_AUTHENTICATION = 'backend_authentication'
PROJECT_HEADER = 'project_header'
PROVIDER_JOB_ID = 'provider_job_id'
WORKSPACE_HEADER = 'workspace_header'


def generate_response(job_response: JobResponse) -> dict:
    if job_response:
        status_code = job_response.status_code.value
        body = {'providerJobId': job_response.provider_job_id,
                'jobStatus'    : job_response.job_status,
                'jobResult'    : job_response.job_result,
                'contentType'  : job_response.content_type.value,
                'histogram'    : job_response.job_histogram,
                'executionTime': job_response.execution_time}

        # Add 'shots' only if it exists in the job_response
        if hasattr(job_response, 'shots'):
            body['shots'] = job_response.shots

    else:
        status_code = job_response.status_code.value
        body = 'Error in function code. Please contact the developer.'

    return {'statusCode'  : status_code, 'body': body,
            'userIdentity': job_response.user_identity,
            'userToken'   : job_response.user_token,
            'projectId'   : job_response.project_header.value,
            'workspaceId' : job_response.workspace_header.value}


def build_done_job_response(fetcher: JobFetcher = None,
                            post_promise: PostProcessingPromise = None) -> JobResponse | None:
    return JobResponse(
            provider_job_id=__extract_provider_job_id(fetcher, post_promise),
            authentication=__extract_authentication(fetcher, post_promise),
            project_header=__extract_project_header(fetcher, post_promise),
            workspace_header=__extract_workspace_header(fetcher, post_promise),
            status_code=StatusCode.DONE)


def build_error_job_response(exception: Exception,
                             job_response: JobResponse = None,
                             fetcher: JobFetcher = None,
                             post_promise: PostProcessingPromise = None,
                             message: str = None) -> JobResponse:
    if job_response is None:
        job_response = JobResponse()
    job_response.provider_job_id = __extract_provider_job_id(fetcher,
                                                             post_promise)
    job_response.authentication = __extract_authentication(fetcher,
                                                           post_promise)
    job_response.project_header = __extract_project_header(fetcher,
                                                           post_promise)
    job_response.tenant_header = __extract_workspace_header(fetcher,
                                                            post_promise)
    job_response.status_code = StatusCode.ERROR
    job_response.job_status = JobStatus.ERROR.value
    job_response.job_result = {'message'  : message or 'Unknown error occurred.',
                               'exception': str(exception)}
    return job_response


def __extract_authentication(fetcher: JobFetcher,
                             post_promise: PostProcessingPromise):
    return getattr(fetcher, BACKEND_AUTHENTICATION,
                   getattr(post_promise, AUTHENTICATION, None))


def __extract_project_header(fetcher: JobFetcher,
                             post_promise: PostProcessingPromise):
    return getattr(fetcher, PROJECT_HEADER,
                   getattr(post_promise, PROJECT_HEADER, None))


def __extract_provider_job_id(fetcher: JobFetcher,
                              post_promise: PostProcessingPromise):
    return getattr(fetcher, PROVIDER_JOB_ID,
                   getattr(post_promise, PROVIDER_JOB_ID, None))


def __extract_workspace_header(fetcher: JobFetcher,
                               post_promise: PostProcessingPromise):
    return getattr(fetcher, WORKSPACE_HEADER,
                   getattr(post_promise, WORKSPACE_HEADER, None))

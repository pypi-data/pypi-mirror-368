#  Quapp Platform Project
#  update_job_metadata.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import requests

from ...config.logging_config import job_logger
from ...data.response.job_response import JobResponse
from ...util.http_utils import create_application_json_header, \
    get_job_id_from_url
from ...util.response_utils import generate_response


def update_job_metadata(job_response: JobResponse, callback_url: str):
    logger = job_logger(get_job_id_from_url(callback_url))
    logger.info(
            f"Calling backend to update job metadata at URL: {callback_url}")

    request_body = generate_response(job_response)

    try:
        request_headers = create_application_json_header(
                token=job_response.user_token,
                project_header=job_response.project_header,
                workspace_header=job_response.workspace_header)

        response = requests.patch(url=callback_url, json={'data': request_body},
                                  headers=request_headers)

        logger.info(
                f"Request to backend completed with status code: {response.status_code}")
        if not response.ok:
            logger.warning(
                    f"Unexpected status code received: {response.status_code}, response content: {response.content}")


    except Exception as exception:
        logger.error(f"Error occurred while calling backend: {exception}",
                     exc_info=True)

        raise exception

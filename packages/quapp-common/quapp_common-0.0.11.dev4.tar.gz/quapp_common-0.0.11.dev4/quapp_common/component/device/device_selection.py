#  Quapp Platform Project
#  device_selection.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from json import JSONDecodeError

import requests

from ...config.logging_config import logger
from ...data.backend.backend_information import BackendInformation
from ...data.response.custom_header import CustomHeader
from ...enum.provider_tag import ProviderTag
from ...util.http_utils import create_bearer_header

logger = logger.bind(context='DeviceSelection')


class DeviceSelection:
    def __init__(self, required_qubit_number, device_id, user_token, url,
                 project_header: CustomHeader, workspace_header: CustomHeader):
        self.required_qubit_number = required_qubit_number
        self.device_id = device_id
        self.user_token = user_token
        self.url = url
        self.project_header = project_header
        self.workspace_header = workspace_header

    def select(self) -> BackendInformation:
        """

        @return: Backend information
        """

        request, header = self._prepare()

        return self._do(request, header)

    def _prepare(self):
        """

        @return: Request and header
        """

        request = {"deviceId"   : self.device_id,
                   "qubitAmount": self.required_qubit_number}
        header = create_bearer_header(self.user_token, self.project_header,
                                      self.workspace_header)

        return request, header

    def _do(self, request: dict, header: dict):
        """

        @param request: Request
        @param header: Header
        @return:
        """
        logger.debug('Select device with request: {0}'.format(request))

        response = requests.get(self.url, params=request, headers=header)

        if response.status_code != 200:
            logger.error(
                    'Select device fail with status code: {0} and content: {1}'.format(
                            response.status_code, response.content))

            raise ValueError(f"Select device failed: {response.content}")

        try:
            response_dict = response.json().get("data")

            logger.debug(
                    'Select device successfully: {0}'.format(response_dict))

            return BackendInformation(provider_tag=ProviderTag.resolve(
                    response_dict.get("providerTag")),
                    device_name=response_dict.get("deviceName"),
                    authentication=response_dict.get("authentication"))
        except JSONDecodeError:
            return None

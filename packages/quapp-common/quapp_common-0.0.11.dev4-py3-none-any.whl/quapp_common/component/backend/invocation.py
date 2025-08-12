#  Quapp Platform Project
#  invocation.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod

from ..callback.update_job_metadata import update_job_metadata
from ...component.device.device_selection import DeviceSelection
from ...config.logging_config import job_logger
from ...config.thread_config import circuit_running_pool
from ...data.backend.backend_information import BackendInformation
from ...data.device.circuit_running_option import CircuitRunningOption
from ...data.request.invocation_request import InvocationRequest
from ...data.response.authentication import Authentication
from ...data.response.custom_header import CustomHeader
from ...data.response.job_response import JobResponse
from ...enum.invocation_step import InvocationStep
from ...enum.sdk import Sdk
from ...enum.status.status_code import StatusCode
from ...model.provider.provider import Provider
from ...util.response_utils import build_error_job_response

EXPORT_CIRCUIT_SDK = {Sdk.QISKIT, Sdk.BRAKET}


class Invocation(ABC):
    def __init__(self, request_data: InvocationRequest):
        self.sdk: Sdk = Sdk.resolve(request_data.sdk)
        self.input = request_data.input
        self.device_id = request_data.device_id
        self.backend_information: BackendInformation
        self.authentication: Authentication = request_data.authentication
        self.project_header: CustomHeader = request_data.project_header
        self.workspace_header: CustomHeader = request_data.workspace_header
        self.job_id = request_data.job_id
        self.options = CircuitRunningOption(shots=request_data.shots,
                                            processing_unit=request_data.processing_unit,
                                            executor=circuit_running_pool,
                                            max_job_size=1, )
        self.device_selection_url: str = request_data.device_selection_url
        self.circuit_export_url: str = request_data.circuit_export_url
        self.callback_dict: dict = {
            InvocationStep.PREPARATION : request_data.preparation,
            InvocationStep.EXECUTION   : request_data.execution,
            InvocationStep.ANALYSIS    : request_data.analysis,
            InvocationStep.FINALIZATION: request_data.finalization, }
        self.invoke_authentication = request_data.invoke_authentication
        self.logger = job_logger(self.job_id)
        self.logger.info(
                f"Initializing Invocation with job id: {self.job_id}, sdk: {self.sdk}, device id: {self.device_id}")

    def submit_job(self, circuit_preparation_fn, post_processing_fn):
        """

        @param post_processing_fn: Post-processing function
        @param circuit_preparation_fn: Circuit-preparation function
        @return: Job result
        """
        self.logger.debug("Invoke job started")

        circuit = self.__pre_execute(circuit_preparation_fn)

        if circuit is None:
            self.logger.warning(
                    "Circuit preparation returned None, cancelling job submission")
            return

        self.__execute(circuit, post_processing_fn)
        self.logger.info("Submit job completed")

    def __pre_execute(self, circuit_preparation_fn):
        """

        @param circuit_preparation_fn: Circuit preparation function
        """
        self.logger.debug("Pre-execute: preparing circuit")
        circuit = self.__prepare_circuit(circuit_preparation_fn)

        if circuit is None:
            self.logger.error(
                    "Circuit preparation failed, returning None from pre-execute")
            return None

        try:
            self.logger.debug("Preparing backend data")
            self.__prepare_backend_data(circuit)
            self.logger.info(
                    f"Backend data prepared: device {self.backend_information.device_name}, provider {self.backend_information.provider_tag.value}")

        except Exception as exception:
            self.logger.error(f"Error when prepare backend data: {exception}",
                              exc_info=True)

            job_response = build_error_job_response(exception,
                                                    message='Error when prepare backend data')

            update_job_metadata(job_response, self.callback_dict.get(
                    InvocationStep.PREPARATION).on_error)

        self.logger.debug("Exporting circuit")
        self._export_circuit(circuit)

        return circuit

    def __execute(self, circuit, post_processing_fn):
        """

        @param circuit: Circuit was run
        @param post_processing_fn: Post-processing function
        @return: Job response
        """
        self.logger.debug("Execute: starting job execution")

        try:
            if self.backend_information is None:
                self.logger.error(
                        "Backend information is None before execution")
                raise ValueError("Backend is not found")

            device_name = self.backend_information.device_name
            provider_tag = self.backend_information.provider_tag

            self.logger.debug(
                    f"Executing job with provider tag: {provider_tag.value}")

            provider = self._create_provider()

            self.logger.debug(f"Executing job with device name: {device_name}")
            device = self._create_device(provider)

        except Exception as exception:
            self.logger.error(
                    f"Exception when create provider or device: {exception}",
                    exc_info=True)

            job_response = build_error_job_response(exception,
                                                    message='Error when create provider or device')
            update_job_metadata(job_response, self.callback_dict.get(
                    InvocationStep.EXECUTION).on_error, )

            return

        self.logger.info(
                f"Running circuit on device {device_name} with provider {provider_tag.value}")

        device.run_circuit(circuit=circuit,
                           post_processing_fn=post_processing_fn,
                           options=self.options,
                           callback_dict=self.callback_dict,
                           authentication=self.authentication,
                           project_header=self.project_header,
                           workspace_header=self.workspace_header)

    def __prepare_circuit(self, circuit_preparation_fn):
        """

        @param circuit_preparation_fn: Circuit preparation function
        @return: circuit
        """
        self.logger.debug('Prepare circuit started')

        job_response = JobResponse(status_code=StatusCode.DONE,
                                   authentication=self.authentication,
                                   project_header=self.project_header,
                                   workspace_header=self.workspace_header)
        update_job_metadata(job_response, self.callback_dict.get(
                InvocationStep.PREPARATION).on_start)

        try:
            circuit = circuit_preparation_fn(self.input)

            if circuit is None:
                self.logger.warning(
                        "Circuit preparation function returned None")
                raise ValueError('Error when prepare circuit')

            self.logger.debug(f"Circuit prepared: {circuit}")

            update_job_metadata(job_response, self.callback_dict.get(
                    InvocationStep.PREPARATION).on_done)

            return circuit

        except Exception as exception:
            self.logger.error(f'Error when prepare circuit: {exception}',
                              exc_info=True)

            job_response = build_error_job_response(exception, job_response,
                                                    message='Error when prepare circuit')

            update_job_metadata(job_response, self.callback_dict.get(
                    InvocationStep.PREPARATION).on_error)

            return None

    def __prepare_backend_data(self, circuit):
        """

        @param circuit: Circuit was run
        """
        self.logger.debug("Prepare backend data started")

        required_qubit_amount = self._get_qubit_amount(circuit)
        self.logger.info(
                f"Qubit amount required for circuit: {required_qubit_amount}")

        device_selection = DeviceSelection(required_qubit_amount,
                                           self.device_id,
                                           self.authentication.user_token,
                                           self.device_selection_url,
                                           self.project_header,
                                           self.workspace_header)

        self.backend_information = device_selection.select()
        self.backend_information.authentication = self.invoke_authentication
        self.logger.debug(
                f"Selected backend: deviceName={self.backend_information.device_name}, provider_tag={self.backend_information.provider_tag}")

    @abstractmethod
    def _export_circuit(self, circuit):
        """

        @param circuit: Circuit was exported
        """

        raise NotImplementedError(
                '_export_circuit() method must be implemented')

    @abstractmethod
    def _create_provider(self, ):
        """
        Create a provider with ProviderFactory
        """

        raise NotImplementedError(
                '_create_provider() method must be implemented')

    @abstractmethod
    def _create_device(self, provider: Provider):
        """
        Create a device with DeviceFactory
        """

        raise NotImplementedError('_create_device() method must be implemented')

    @abstractmethod
    def _get_qubit_amount(self, circuit):
        """
        Get number qubit of circuit
        """

        raise NotImplementedError(
                '_get_qubit_amount() method must be implemented')

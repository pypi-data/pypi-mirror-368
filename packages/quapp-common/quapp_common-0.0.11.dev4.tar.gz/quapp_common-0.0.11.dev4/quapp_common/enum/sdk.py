"""
    QApp Platform Project sdk.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from ..enum.base_enum import BaseEnum


class Sdk(BaseEnum):
    QISKIT = 'qiskit'
    BRAKET = 'braket'
    TYTAN = 'tytan'
    D_WAVE_OCEAN = "d-wave ocean"
    CUDA_QUANTUM = "cuda quantum"
    PENNYLANE = "pennylane"
    PYQUIL = "pyquil"

    @staticmethod
    def resolve(sdk: str):
        for element in Sdk:
            if element.value.__eq__(sdk):
                return element

        raise Exception("Sdk type is not supported!")

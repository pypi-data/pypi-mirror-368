"""
    QApp Platform Project provider_tag.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from ..enum.base_enum import BaseEnum


class ProviderTag(BaseEnum):
    QUAO_QUANTUM_SIMULATOR = 'QUAO_QUANTUM_SIMULATOR'
    IBM_QUANTUM = 'IBM_QUANTUM'
    IBM_CLOUD = 'IBM_CLOUD'
    AWS_BRAKET = 'AWS_BRAKET'
    D_WAVE = 'D_WAVE'
    OQC_CLOUD = 'OQC_CLOUD'
    RIGETTI = 'RIGETTI'

    @staticmethod
    def resolve(provider_tag: str):
        for element in ProviderTag:
            if element.value.__eq__(provider_tag):
                return element

        raise Exception("Provider tag is not supported!")

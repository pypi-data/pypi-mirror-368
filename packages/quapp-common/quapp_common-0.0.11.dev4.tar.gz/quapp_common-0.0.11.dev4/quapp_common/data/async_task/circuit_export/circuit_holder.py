"""
    QApp Platform Project circuit_holder.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""


class CircuitDataHolder:
    def __init__(self,
                 circuit,
                 export_url: str):
        self.circuit = circuit
        self.export_url = export_url

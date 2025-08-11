# ========================================================================================
#  Copyright (C) 2025 CryptoLab Inc. All rights reserved.
#
#  This software is proprietary and confidential.
#  Unauthorized use, modification, reproduction, or redistribution is strictly prohibited.
#
#  Commercial use is permitted only under a separate, signed agreement with CryptoLab Inc.
#
#  For licensing inquiries or permission requests, please contact: pypi@cryptolab.co.kr
# ========================================================================================

from typing import List, Union

import evi
from evi import SingleCiphertext

from proto.es2_comm_type_pb2 import SerializedCiphertext


class CipherBlock:
    """
    CipherBlock class for handling ciphertexts.

    Ciphertexts can be either an encrypted vector or an encrypted similarity scores.
    """

    def __init__(
        self,
        data: Union[List[SingleCiphertext], List[SerializedCiphertext]],
    ):
        self._is_score = None
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: Union[List[SingleCiphertext], List[SerializedCiphertext]]):
        if value is None:
            raise ValueError("Data cannot be None.")
        if not isinstance(value, list):
            raise ValueError("Data must be a list of SingleCiphertext or SerializedCiphertext.")
        if not value:
            raise ValueError("Data list cannot be empty.")
        if isinstance(value[0], SerializedCiphertext):
            self._is_score = True
        elif isinstance(value[0], SingleCiphertext):
            self._is_score = False
        else:
            raise ValueError("Data must be a list of SingleCiphertext or SerializedCiphertext.")
        self._data = value

    def serialize(self) -> bytes:
        """
        Serializes the CipherBlock to bytes.

        Returns:
            bytes: Serialized bytes of the CipherBlock.
        """
        if self._is_score is True:
            raise ValueError("CipherBlock data must be set before serialization.")
        return evi.serialize_query_to(self.data)

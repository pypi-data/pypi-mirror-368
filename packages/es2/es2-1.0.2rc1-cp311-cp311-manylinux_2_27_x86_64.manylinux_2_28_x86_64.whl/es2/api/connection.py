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

import grpc

###################################
# Connection Class
###################################


class Connection:
    def __init__(self, server_address: str, secure: bool = False):
        self.server_address = server_address
        self.channel = (
            grpc.secure_channel(server_address, grpc.ssl_channel_credentials())
            if secure
            else grpc.insecure_channel(server_address)
        )
        try:
            grpc.channel_ready_future(self.channel).result(timeout=3)
            self._connected = True
        except grpc.FutureTimeoutError:
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_channel(self):
        return self.channel

    def close(self):
        self.channel.close()
        self._connected = False

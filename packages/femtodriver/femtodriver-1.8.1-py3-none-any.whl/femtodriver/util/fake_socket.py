#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

import numpy as np

AF_INET = None
SOCK_STREAM = None


class socket:
    def __init__(self, foo, bar):
        self.send_data = bytes()

    def connect(self, host_port):
        pass

    def sendall(self, data):
        self.send_data += data

    def recv(self, num_bytes):
        fake_u32 = np.zeros((num_bytes // 4,), dtype=np.uint32)
        # give it an acceptable code
        fake_u32[::3] = 4  # read reply
        fake_bytes = fake_u32.tobytes()
        return fake_bytes

    def close(self):
        pass

import socket
import pickle
import time

import numpy as np


ip_address = '127.0.0.1'
port = 8765
buffer_size = 4096

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip_address, port))

        v = np.arange(100, dtype=np.float64), np.random.randn(100)
        # v = np.random.randn(100, 100) + np.random.randn() * 100

        data = pickle.dumps(v)
        header = pickle.dumps({'size': len(data), 'type': 'data'})

        s.send(header)
        _ = s.recv(buffer_size)
        s.sendall(data)

    time.sleep(0.2)

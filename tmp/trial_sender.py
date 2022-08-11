from ctypes import sizeof
import socket
import pickle

import numpy as np


ip_address = '127.0.0.1'
port = 7772
buffer_size = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip_address, port))

    v = np.arange(1024000, dtype=np.float64)

    data = pickle.dumps(v)
    header = pickle.dumps({'size': len(data)})

    s.send(header)
    print(s.recv(buffer_size))
    s.sendall(data)

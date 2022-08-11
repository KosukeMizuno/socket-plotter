import socket
import pickle

import numpy as np

ip_address = '127.0.0.1'
port = 7772
buffer_size = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((ip_address, port))
    s.listen(1)
    s.settimeout(1)
    print("receiver is started:", (ip_address, port))

    while True:
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print('KeyboardInterrupt.')
            break
        except InterruptedError:
            print('Interruptted.')
            break
        print("accepted:", (conn, addr))

        with conn:
            header_bytes = conn.recv(buffer_size)
            header = pickle.loads(header_bytes)
            print(header)

            conn.send(b'size was received.')

            databuf = bytearray(header['size'])
            conn.recv_into(databuf)
            # print(databuf)
            print('received.')

            try:
                v = pickle.loads(databuf)
            except pickle.UnpicklingError:
                print('pickle.UnpicklingError')
                continue
            print('unpickling...')
            print(v)
            print(v.__class__)

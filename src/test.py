import struct


print("len: ", struct.calcsize('i'))
print("len: ", struct.calcsize('I'))
print("len: ", struct.calcsize('h'))

import socket, errno

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(("0.0.0.0", 6620))
except socket.error as e:
    if e.errno == errno.EADDRINUSE:
        print("Port is already in use")
    else:
        # something else raised the socket.error exception
        print(e)

s.close()


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

print(is_port_in_use(9005))


from test_class import testClass
testClass()
print("end")
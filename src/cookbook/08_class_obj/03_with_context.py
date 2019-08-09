
from socket import socket, AF_INET, SOCK_STREAM
"""
编写上下文管理器的主要原理是你的代码会放到 with 语句块中执行。 
当出现 with 语句的时候，对象的 __enter__() 方法被触发， 它返回的值(如果有的话)会被赋值给 as 声明的变量。
然后，with 语句块里面的代码开始执行。 最后，__exit__() 方法被触发进行清理工作。

不管 with 代码块中发生什么，上面的控制流都会执行完，就算代码块中发生了异常也是一样的。 
事实上，__exit__() 方法的第三个参数包含了异常类型、异常值和追溯信息(如果有的话)。 
__exit__() 方法能自己决定怎样利用这个异常信息，或者忽略它并返回一个None值。 
如果 __exit__() 返回 True ，那么异常会被清空，就好像什么都没发生一样， with 语句后面的程序继续在正常执行。
"""
class LazyConnection:
    def __init__(self, address, family=AF_INET, type=SOCK_STREAM):
        self.address = address
        self.family = family
        self.type = type
        self.sock = None

    def __enter__(self):
        if self.sock is not None:
            raise RuntimeError('Already connected')
        self.sock = socket(self.family, self.type)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, exc_ty, exc_val, tb):
        self.sock.close()
        self.sock = None


if __name__ == '__main__':
    from functools import partial

    conn = LazyConnection(('www.python.org', 80))
    # Connection closed
    with conn as s:
        # conn.__enter__() executes: connection open
        s.send(b'GET /index.html HTTP/1.0\r\n')
        s.send(b'Host: www.python.org\r\n')
        s.send(b'\r\n')
        resp = b''.join(iter(partial(s.recv, 8192), b''))
        print(resp)
        # conn.__exit__() executes: connection closed
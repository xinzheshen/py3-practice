import time
from functools import wraps

def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    # 注意加不加@wraps的区别
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper


@timethis
def hello(msg: str):
    """
    print the message after sleep 2s
    """
    time.sleep(2)
    print(msg)


hello("decoretor")
print(hello.__name__)
print(hello.__doc__)
print(hello.__module__)
print(hello.__annotations__)

print(hello.__wrapped__("hi"))

from inspect import signature
# 打印参数签名信息
print(signature(hello))
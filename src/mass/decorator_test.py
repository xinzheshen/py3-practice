from functools import wraps


def log1(func):
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper


@log1
def now1():
    '''now1 doc'''
    print('2018-11-21')


# 相当于执行了 now = log(now)
now1()
print('without @wraps :', now1.__name__)
print('without @wraps :', now1.__doc__)
print('----------------------------------')


def log2(func):
    # wraps(func) 能够保留原函数的元数据，包括这个函数的名字、文档字符串、注解和参数签名等
    @wraps(func)
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper


@log2
def now2():
    '''now2 doc'''
    print('2018-11-21')


now2()
print('with @wraps :', now2.__name__)
print('with @wraps :', now2.__doc__)
print('----------------------------------')


def log3(text):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator


@log3('execute')
def now3():
    print('2018-11-21')


# 相当于执行了now = log('execute')(now)
# 首先执行log('execute')，返回的是decorator函数，再调用返回的函数，参数是now函数，返回值最终是wrapper函数
now3()
print('module: ', now3.__module__)
print('-----------------------')

# 你想创建一个新的拥有一些额外功能的实例属性类型，比如类型检查，
# 可以通过一个描述器类的形式来定义它的功能。

# Descriptor attribute for an integer type-checked attribute
# 一个描述器就是一个实现了三个核心的属性访问操作(get, set, delete)的类
class Integer:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError('Expected an int')
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class Point:
    # 描述器的一个比较困惑的地方是它只能在类级别被定义，而不能为每个实例单独定义。
    x = Integer('x')
    y = Integer('y')

    def __init__(self, x, y):
        self.x = x
        self.y = y


if __name__ == '__main__':
    p = Point(2,3)
    print(p.x)  # Calls Point.x.__get__(p, Point)
    print(Point.x)  # Calls Point.x.__get__(None, Point)
    p.y = 2.5
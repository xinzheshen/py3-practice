

class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Pair({0.x!r}, {0.y!r})'.format(self)

    def __str__(self):
        return '({0.x!s}, {0.y!s})'.format(self)

if __name__ == '__main__':
    p = Pair(3, 4)
    # 在交互环境下，直接输入p时，会调用__repr__方法
    # p
    # print 会调用__str__方法
    print(p)
    # 特别来讲，!r 格式化代码指明输出使用 __repr__() 来代替默认的 __str__()
    print('p is {0!r}'.format(p))
    print('p is {0}'.format(p))

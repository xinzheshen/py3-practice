
from timeit import Timer



def test1():
    li = []
    for i in range(10000):
        li.append(i)


def test2():
    li = []
    for i in range(10000):
        li += [i]


def test3():
    li = [i for i in range(10000)]


def test4():
    li = list(range(10000))

def test5():
    li = []
    for i in range(10000):
        li.extend([i])

def test6():
    li = []
    for i in range(10000):
        li.insert(0, i)

def test7():
    li = []
    for i in range(10000):
        li = li + [i]


# 测试性能
timer1 = Timer("test1()", "from __main__ import test1")
print("append:", timer1.timeit(1000)) # 1.3826961190120473
timer2 = Timer("test2()", "from __main__ import test2")
print("+=:", timer2.timeit(1000)) # 1.4140574127044139
timer3 = Timer("test3()", "from __main__ import test3")
print("i for i in range:", timer3.timeit(1000)) # 0.5894140286427341
timer4 = Timer("test4()", "from __main__ import test4")
print("list(range):", timer4.timeit(1000)) # 0.34011615774210036
timer5 = Timer("test5()", "from __main__ import test5")
print("extend:", timer5.timeit(1000)) # 1.7666775668385166
timer6 = Timer("test6()", "from __main__ import test6")
print("insert:", timer6.timeit(1000)) # 42.77878607744147
timer7 = Timer("test7()", "from __main__ import test7")
print("+:", timer7.timeit(1000)) # 154.8507259

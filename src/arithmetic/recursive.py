

'''
递归：
三要素：
第一要素：明确你这个函数想要干什么
第二要素：寻找递归结束条件
第三要素：找出函数的等价关系式，不断缩小参数的范围
'''

def cal_factorial(n: int):
    # 计算阶乘
    if n <= 2:
        return n
    else:
        return n * cal_factorial(n-1)
print(cal_factorial(3))


def fib(n):
    if n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)
print('fib:', fib(9))

# 一只青蛙一次可以跳上1级台阶，也可以跳上2级。求该青蛙跳上一个n级的台阶总共有多少种跳法
def skip(n):
    if n <= 2:
        return n
    else:
        # 第一种跳法：第一次我跳了一个台阶，那么还剩下n-1个台阶还没跳，剩下的n-1个台阶的跳法有f(n-1)种。
        # 第二种跳法：第一次跳了两个台阶，那么还剩下n-2个台阶还没，剩下的n-2个台阶的跳法有f(n-2)种
        return skip(n-1) + skip(n-2)
print('skip:', skip(3))


# 优化递归： 避免重复计算, 可以利用字典存储计算结果


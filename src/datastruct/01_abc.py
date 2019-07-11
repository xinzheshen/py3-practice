
"""
引入：
如果a+b+c=1000, 且a^2+b^2=c^2，a b c 为自然数，如何求出所有a b c的组合？
"""
import time
# 枚举法
def enum_method():
    # times:257s
    for a in range(0, 1001):
        for b in range(0, 1001):
            for c in range(0, 1001):
                if a + b + c ==1000 and a**2 + b**2 == c**2:
                    print(a, b, c)


def optimize_enum_method():
    # times:1s
    for a in range(0, 1001):
        for b in range(0, 1001):
            c = 1000 - a - b
            if a**2 + b**2 == c**2:
                print(a, b, c)

# 时间复杂度:因为每台计算机cpu效率不同，所以以算法执行的基本运算（加减乘除等）数量为衡量标准
#粗略计算： 1000 * 1000 * 1000 * 2
#  T(n) = n^3 * 2 ==> T(n) = k*g(n)+c , g(n) = n^3
#  ==> 近似记作T(n)=g(n)
#  ==> 这个g(n)=n^3 叫做这个算法时间复杂度的大O表示法,即O(n^3)
# 时间复杂度一般指最坏时间复杂度


start_time = time.time()
print("start time:", start_time)
optimize_enum_method()
end_time = time.time()
print("times:%d" % (end_time - start_time))
print("over")
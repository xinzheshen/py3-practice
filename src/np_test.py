import numpy as np
from numpy.lib.stride_tricks import as_strided


# https://blog.csdn.net/Scc_hy/article/details/82531723

# array切片之所以可以对原array数据进行修改，是因为两个array的内存地址在一个地方
x = np.array(range(1, 5))
print(x)
y = x[:-1]
# x[0] = 9
# 查看array的内存地址
print(x.__array_interface__['data'][0], y.__array_interface__['data'][0])
# 结果 => (1713365532096, 1713365532096)

print("数据类型----------------")
print(np.dtype(np.int8).type)
print(np.dtype(np.int8).itemsize) # 一个元素占内存字节大小 1
print(np.dtype(np.int32).itemsize) # 一个元素占内存字节大小 4

print("创建视图--------------")
y = x.view('<i4')
print(y.__array_interface__['data'][0])  # 1713365532096
# 视图的内存地址依旧和 x 相同，所以修改原数值，y 也会变化
print(y)  # array([67305985])
x[1] = 5
print(y)  # array([328193])

# 同样修改视图 y , x 也会变化
y[0] = 1024
print(y.dtype) # int32
print(x, x.dtype) # [1024    0] int16

print(y.base is x) # True

print("索引--------------")
x = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]], dtype = np.int8)
print(x.itemsize)
# 步伐 大小与dtype有关
print(x.strides) # (3, 1)
byte_offset = sum(x.strides*np.array([1,2])) # 步伐*想要查找的位置
print(x.flat[byte_offset])  # 6
print(x[1, 2])              # 6

print("用步长改变维度----------")
x = np.array([1, 2, 3, 4, 5, 6], dtype=np.int16)
# 维度 3行 2列
shape = (3, 2)
# 第一个维度间隔2个元素，第二个维度间隔1个元素
strides = x.itemsize*np.array([2, 1])
print("strides", strides)
y = as_strided(x, shape=shape, strides=strides)
print(y)
""" 结果
array([[1, 2],
       [3, 4],
       [5, 6]], dtype=int16)
"""

print("数组维度和量增多-------")
# 生成9*9的数组
## 采用np.int8 a.itemsize = 1 便于操作步伐strides
a = np.array(range(1, 10), dtype=np.int8)
print("a", a)
b = as_strided(a, shape=(9, 9), strides=(0, 1)).copy() # 第一维度步伐为0,即相等
print("b", b)
## 将 9*9 转化成 3*3*3*3 数组                   ==直接在原array上切割==
shape = (3, 3, 3, 3)
"""
第一维度(数组间行)间隔 3*(3*3)个元素， 第二维度(数组间列)间隔3个维度
第三维度(数组内行)间隔3个元素，最后的维度(数组内列)间隔1个元素
"""
strides = b.itemsize*np.array([27, 3 , 9, 1])
out = as_strided(b, shape=shape, strides = strides)
print("out", out)
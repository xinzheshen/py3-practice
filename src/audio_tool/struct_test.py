import struct
# https://blog.csdn.net/weiwangchao_/article/details/80395941
# https://www.cnblogs.com/volcao/p/8807507.html

# native byteorder
buffer = struct.pack("ihb", 1, 2, 3)
print(repr(buffer))
print(struct.unpack("ihb", buffer))
# data from a sequence, network byteorder
data = [1, 2, 3]
buffer = struct.pack("!ihb", *data)
print(repr(buffer))
print(struct.unpack("!ihb", buffer))
print('----------big-endian----------')
buffer = struct.pack(">ihb", *data)
print(repr(buffer))
print('----------little-endian----------')
buffer = struct.pack("<ihb", *data)
print(repr(buffer))

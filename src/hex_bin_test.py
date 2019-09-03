
# 10进制可以通过对应函数直接转为2，8，16进制
# 2，8，16…进制通过int函数可以转为10进制
# 2， 8，16进制之间转换使用10进制作为中转

a = 11

print("-"*15)
print(bin(a))
print(oct(a))
print(hex(a))

# 不带0b 0o 0x前缀
print(format(a, 'b'))
print(format(a, 'o'))
print(format(a, 'x'))

print("-"*15)
# 将不同进制 转 十进制
print(int('1011', 2))

# 十六进制转二进制
print("-"*15)
print(bin(int('b', 16)))
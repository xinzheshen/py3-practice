
# 2.1 使用多个界定符分割字符串
line = 'asdf fjdk; afed, fjek,asdf, foo'
import re
print("匹配多种分隔符")
print(re.split(r'[;,\s]\s*', line))
print("保留分隔符")
print(re.split(r'(;|,|\s)\s*', line))
print("使用括号，但不保留分隔符")
print(re.split(r'(?:,|;|\s)\s*', line))

# 2.2 字符串开头或结尾匹配


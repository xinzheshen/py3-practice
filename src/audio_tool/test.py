



# a = {"version":"1.0.0.1"}
# print(type(a))
# print(a)
# print(str(a))
# print(repr(a))
#
# b = "\"version\""
# print(str(b))
# print(repr(b))
#
# c = "{" + "\"version\":" + "1.0.0.1" + "}"
# print(c)

# status = "todo"
# timestamp = 1234L
# message = "todo"
# version = "1.0.0.1"
# response_message = "{" + "\"status\":\"" + status + "\",\"timestamp\":" + str(timestamp) \
#     + ",\"message\":\"" + message + "\",\"version\":\"" + version + "\"}"
#
# print(response_message)

zifuchuan = 'sfsjl sfsf'
# print(zifuchuan.replace([" ", '@'], "_"))

i = 12.1
j = 12.0
print(int(i) == i)
print(int(j) == j)

test_format = "hello %s %s"
print(test_format % ("tom", "bob"))

tmp_str = "Recognize Rejected: , confidence: 0, audio pos: 00:00:00, duration: 00:00:00.8000000"
print(tmp_str.split(",")[1].split(":")[1].strip())


def process_values(list_values):
    list_values[1:] = list_values[:2]


test_list = [1, 2, 3]
process_values(test_list)
print(test_list)

if 1<2<3:
    print("OK")


import os
print("proxy",os.environ["HTTP_PROXY"])





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

status = "todo"
timestamp = 1234L
message = "todo"
version = "1.0.0.1"
response_message = "{" + "\"status\":\"" + status + "\",\"timestamp\":" + str(timestamp) \
    + ",\"message\":\"" + message + "\",\"version\":\"" + version + "\"}"

print(response_message)
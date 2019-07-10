import time
from datetime import datetime

from pytz import timezone

timestamp = 1561082579
print(str(datetime.utcfromtimestamp(timestamp)))
time_list = time.localtime(timestamp)
result_time = time.strftime("%Y-%m-%d %H:%M:%S", time_list)
print(result_time)
timestamp += 10
time_list = time.localtime(timestamp)
print(timezone('Atlantic/Azores').localize(datetime(*[t for t in time_list][:6])).astimezone(timezone('Atlantic/Azores')))
print(timezone('Atlantic/Azores').localize(datetime.utcfromtimestamp(timestamp)))
print(timezone('Asia/Shanghai').localize(datetime(*[t for t in time_list][:6])).astimezone(timezone('Atlantic/Azores')))
print(timezone('Atlantic/Azores').localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone('Atlantic/Azores')))
print(timezone('Atlantic/Azores').localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone('Asia/Shanghai')))
print(timezone('Atlantic/Azores').localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone('US/Eastern')))
# print(datetime.utcfromtimestamp(timestamp).astimezone(timezone('Atlantic/Azores')))
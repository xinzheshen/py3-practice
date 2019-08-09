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

print("="*60)
timestr = "20190711235959"
year, month, day, hour, minute, sec = \
    int(timestr[0:4]), int(timestr[4:6]), int(timestr[6:8]), \
    int(timestr[8:10]), int(timestr[10:12]), int(timestr[12:14])
timeList = (year, month, day, hour, minute, sec, 0, 0, 0)
timestamp_1 = time.mktime(timeList)
print("timestamp_1", timestamp_1)
timestr_2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_1 + 10))
print("timestr_2", timestr_2)

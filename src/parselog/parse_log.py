from collections import defaultdict
from datetime import timedelta
import re


file_path = 'E:\code\py3-practice\other\case_log.txt'
action_time_dict = defaultdict(list)
with open (file_path, 'rt', encoding='utf8') as f:
    for line in f.readlines():
        if line.find('ACTION') != -1:
            # ['12/20', '18:59:12,033', ':', 'ACTION', 'Press', '[started]', 'line:', '3\n']
            # ['12/20', '18:59:20,087', ':', 'ACTION', 'Press', '[finished]', 'result=SUCCESS', 'duration=8.054sec\n']
            line_list = line.split(' ')
            if line_list[5] == '[started]':
                action_type_start = line_list[4]
                time = re.split(r'[:,]', line_list[1])
                start_time = \
                    timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]), milliseconds=int(time[3]))
            if line_list[5] == '[finished]':
                action_type_stop = line_list[4]
                if action_type_start == action_type_stop:
                    time = re.split(r'[:,]', line_list[1])
                    stop_time = \
                        timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]), milliseconds=int(time[3]))
                    duration = (stop_time - start_time).total_seconds()
                    action_time_dict[action_type_stop].append(duration)

for key, value in action_time_dict.items():
    average_time = sum(value) / len(value)
    print(key + ' : ' + str(average_time))






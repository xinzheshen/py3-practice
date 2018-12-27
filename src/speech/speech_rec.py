# from ..comm import file_process
import os
import subprocess
import random
import re


def get_wav_lable_dict(file_name):
    label_dict = {}
    with open(file_name, 'rt', encoding='utf8') as f:
        for line in f.readlines():
            key_value = line.split('\t')
            label_dict[key_value[0]] = key_value[1].strip()
    return label_dict


def get_valid_sub_file_list(base_path, postfix):
    sub_file_list = []
    all_sub = os.listdir(base_path)
    for sub in all_sub:
        if not os.path.isfile(os.path.join(base_path, sub)) or not sub.endswith(postfix):
            continue
        sub_file_list.append(base_path + os.path.sep + sub)

    return sub_file_list


if __name__ == '__main__':

    lable_path = 'D:\\sxz\\practice\\py3-practice\\other\\data\\trans.txt'
    lable_dict = get_wav_lable_dict(lable_path)

    source_path = 'D:\\sxz\\practice\\py3-practice\\other\\data\\wav\\C0936'
    file_list = get_valid_sub_file_list(source_path, '.wav')

    length = len(file_list)

    software_path = 'C:\\cats-node\\prod\\speech-recognize\\SpeechRecognizeBin.exe'
    grammar_path = 'C:\\cats-node\\prod\\speech-recognize\\grammarTest.txt'

    count = 0
    sample_num = length
    # for i in range(0, sample_num):
    #     file = file_list[random.randint(0, length-1)]
    for file in file_list:
        cmd = software_path \
              + ' -i ' + file \
              + ' -g ' + grammar_path \
              + ' -l zhCN -t 5';
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process.stdout.read().decode(encoding='utf-8')
        text = re.split(r'[:\r\n]', result)[1]
        key = file.split('\\')[-1].split('.')[0]
        if lable_dict[key] == text:
            count += 1;
            print('count :', count)
        else:
            print('fail', file)

    print('sample num is ', sample_num)
    print('success num is ', count)
    print('accuracy rate is ', count / sample_num)




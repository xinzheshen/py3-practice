#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    parselog.parse_log
    ~~~~~~~~~~~~~~~~~~~
    Load log file and parse data into a xls file.
    :copyright: © 2018 by xinzheshen.
    :license: MIT, see LICENSE for more details.
"""

import argparse
from collections import defaultdict
from datetime import timedelta
import re
import traceback

import xlwt


def parse_log_file(file_name):
    """Loading a log file and parse action type
    :param file_name: the path of the input log file.
    :return: a dict with key: action type, value: time list.
    """
    action_times_dict = defaultdict(list)
    with open(file_name, 'rt', encoding='utf8') as f:
        for line in f.readlines():
            if line.find('ACTION') != -1:
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
                        action_times_dict[action_type_stop].append(duration)
    return action_times_dict


def process_data(data):
    """process the data to a list
    :param data: a dict with key: action type, value: time list.
    :return: a list of tuple.
    """
    action_time_dict = defaultdict(list)
    for key, value in data.items():
        length = len(value)
        average_time = round(sum(value) / length, 3)
        action_time_dict[key].append(length)
        action_time_dict[key].append(average_time)
        print(key + ' : ' + str(length) + ' : ' + str(average_time))
    return sorted(action_time_dict.items(), key=lambda x: x[1][0])


def get_style(forecolor, bold):
    """Generate a style for specified forecolor and has bold or not
    :param forecolor: the name of the forecolor.
    :param bold: has bold or not.
    :return: a style, an :class:`XFstyle` object.
    """
    # https://secure.simplistix.co.uk/svn/xlwt/trunk/xlwt/Style.py
    # https://www.crifan.com/python_xlwt_set_cell_background_color/
    style = xlwt.easyxf(
        'pattern: pattern solid, fore_colour %s; font: bold %s;' % (
            forecolor, bold))
    return style


def export_xls(data, file_name):
    """Exporting the data into a xls file as a specific format
    :param data: the content to output.
    :param file_name: the path of the output xls file.
    """
    excel_file = xlwt.Workbook(encoding='utf8')
    new_sheet = excel_file.add_sheet('分析结果', cell_overwrite_ok='True')
    style_1 = xlwt.Style.default_style
    new_sheet.write(0, 0, 'action_type', style_1)
    new_sheet.write(0, 1, 'excute_times', style_1)
    new_sheet.write(0, 2, 'excute_aver_time', style_1)

    for row_num, value in enumerate(data, start=1):
        style_2 = xlwt.Style.default_style
        if value[1][1] > 2:
            style_2 = get_style('red', 'off')
        new_sheet.write(row_num, 0, value[0], style_1)
        new_sheet.write(row_num, 1, value[1][0], style_1)
        new_sheet.write(row_num, 2, value[1][1], style_2)

    excel_file.save(file_name)


def process_argv():
    """Processing input arguments
    :return: input args, has to be an instance of :attr:`argparse.Namespace`.
    """
    parser = argparse.ArgumentParser(prog='csv2xls')
    parser.add_argument('--input', '-i',
                        help='The file path of input log file.',
                        required=True)
    parser.add_argument('--output', '-o',
                        help='The file path of output xls file.',
                        required=True)
    return parser.parse_args()


if __name__ == '__main__':
    try:
        arg = process_argv()
        data = parse_log_file(arg.input)
        result = process_data(data)
        export_xls(result, arg.output)
    except Exception as exp:
        print(exp)
        traceback.print_exc()


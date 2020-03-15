# -*- coding: utf-8 -*-
import sys
import os
import re

import xlrd
import xlwt
from collections import OrderedDict

text_dict = OrderedDict()
text_dict_sorted =OrderedDict()

title = "筆畫檢索"
word_er = "兒"
word_op = "（"
ce = "冊"
num_dict = {
    '1': '一',  '2': '二', '3': '三', '4': '四', '5': '五',
    '6': '六',  '7': '七', '8': '八', '9': '九', '10': '十',
    '11': '十一',  '12': '十二', '13': '十三', '14': '十四', '15': '十五',
    '16': '十六',  '17': '十七', '18': '十八', '19': '十九', '20': '二十',
    '21': '二十一',  '22': '二十二', '23': '二十三', '24': '二十四', '25': '二十五',
    '26': '二十六',  '27': '二十七', '28': '二十八', '29': '二十九', '30': '三十',
    '31': '三十一',  '32': '三十二', '33': '三十三', '34': '三十四', '35': '三十五',
    '36': '三十六',  '37': '三十七', '38': '三十八', '39': '三十九', '40': '四十'
}

ignored_lines = OrderedDict()


def read_excel_for_merge(file_path, index, ce_num):
    # print("Reading excel file...")
    global text_dict
    excelFile = xlrd.open_workbook(file_path)
    sheet = excelFile.sheet_by_index(index)
    current_group = ""
    ce_with_num = ce + ce_num
    ignored_lines[ce_with_num] = []
    for row_no in range(0, sheet.nrows):
        cell_value_0 = sheet.cell_value(row_no, 0)
        cell_value_1 = sheet.cell_value(row_no, 1)
        cell_value_2 = sheet.cell_value(row_no, 2)
        try:
            if cell_value_0 == '？' or cell_value_0 == '' or cell_value_0 == '?':
                print(ce_with_num + " " + str(row_no + 1) + "行 : " + cell_value_0, cell_value_1, cell_value_2)
                ignored_lines[ce_with_num].append(str(row_no + 1))
                continue
            if current_group:
                if current_group not in text_dict.keys():
                    text_dict[current_group] = OrderedDict()
                    text_dict[current_group][ce_num] = []
                elif ce_num not in text_dict[current_group].keys():
                    text_dict[current_group][ce_num] = []
            if cell_value_1:
                text_dict[current_group][ce_num].append((cell_value_0, cell_value_1, cell_value_2))
            else:
                if cell_value_0 != "筆畫檢索":
                    current_group = cell_value_0
        except Exception as e:
            print(e)
            ignored_lines[ce_with_num].append(str(row_no + 1))


def read_excel_for_order(file_path, index):
    global text_dict
    words = []

    excelFile = xlrd.open_workbook(file_path)
    sheet = excelFile.sheet_by_index(index)
    current_group = ""
    for row_no in range(0, sheet.nrows):
        cell_value_0 = sheet.cell_value(row_no, 0)
        cell_value_1 = sheet.cell_value(row_no, 1)
        cell_value_2 = sheet.cell_value(row_no, 2)
        cell_value_3 = sheet.cell_value(row_no, 3)
        try:
            if current_group and current_group not in text_dict.keys():
                text_dict[current_group] = OrderedDict()
            if cell_value_1:
                key = cell_value_0[0]
                if key not in text_dict[current_group].keys():
                    text_dict[current_group][key] = OrderedDict()
                if cell_value_0 in words:
                    text_dict[current_group][key][cell_value_0].extend([cell_value_1, cell_value_2, cell_value_3])
                else:
                    text_dict[current_group][key][cell_value_0] = [cell_value_1, cell_value_2, cell_value_3]
                words.append(cell_value_0)
            else:
                if cell_value_0 != "筆畫檢索":
                    current_group = cell_value_0
        except Exception:
            ignored_lines.append(str(row_no + 1))



def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


def sorted_rule_1(s):
    index = str(s).find(word_op)
    if index != -1:
        s = s[:index]

    if s.endswith(word_er):
        return len(s) - 0.5
    return len(s)


def process_data():
    global text_dict, text_dict_sorted
    for group, value in text_dict.items():
        text_dict_sorted[group] = OrderedDict()
        for word_first in value.keys():
            words = text_dict[group][word_first].keys()
            for word in sorted(words, key=sorted_rule_1):
                if word in text_dict_sorted[group].keys():
                    text_dict_sorted[group][word].extend(text_dict[group][word_first][word])
                else:
                    text_dict_sorted[group][word] = text_dict[group][word_first][word]


def set_style(name, height, bold=False, right=False, title=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height

    # 设置单元格对齐方式
    alignment = xlwt.Alignment()
    if right:
        # 0x01(左端对齐)、0x02(水平方向上居中对齐)、0x03(右端对齐)
        alignment.horz = 0x03
    elif title:
        alignment.horz = 0x02
    else:
        alignment.horz = 0x01
    # 0x00(上端对齐)、 0x01(垂直方向上居中对齐)、0x02(底端对齐)
    alignment.vert = 0x01

    style.font = font
    style.alignment = alignment
    return style


def write_excel_for_merge(output_file):
    global text_dict
    print("Wtring excel file...")
    f = xlwt.Workbook()
    sheet = f.add_sheet('sheet',cell_overwrite_ok=True)
    sheet.write_merge(0, 0, 0, 2, title, style=set_style("黑体", 20*16, bold=True, title=True))
    strokes_style = set_style("宋体", 20*14, bold=True, title=True)
    detail_style1 = set_style("宋体", 20*12)
    detail_style2 = set_style("宋体", 20*12, right=True)
    row_num = 0
    for strokes, value in text_dict.items():
        row_num += 1
        sheet.write_merge(row_num, row_num, 0, 2, strokes, style=strokes_style)
        for ce_num, detailes in value.items():
            ce_num = ce + num_dict[ce_num]
            for line in detailes:
                row_num += 1
                sheet.write(row_num, 0, line[0], style=detail_style1)
                sheet.write(row_num, 1, ce_num, style=detail_style1)
                sheet.write(row_num, 2, line[1], style=detail_style1)
                sheet.write(row_num, 3, line[2], style=detail_style2)

    sheet.col(0).width = int(256*12.61)
    sheet.col(1).width = int(256*12.61)
    sheet.col(2).width = int(256*39.23)
    sheet.col(3).width = int(256*5.74)
    f.save(output_file)


def write_excel_for_order(output_file):
    global text_dict_sorted
    print("Wtring excel file...")
    f = xlwt.Workbook()
    sheet = f.add_sheet('sheet',cell_overwrite_ok=True)
    sheet.write_merge(0, 0, 0, 3, title, style=set_style("黑体", 20*16, bold=True, title=True))
    strokes_style = set_style("宋体", 20*14, bold=True, title=True)
    detail_style1 = set_style("宋体", 20*12)
    detail_style2 = set_style("宋体", 20*12, right=True)
    row_num = 0
    for strokes, value in text_dict_sorted.items():
        row_num += 1
        sheet.write_merge(row_num, row_num, 0, 3, strokes, style=strokes_style)
        for word, detailes in value.items():
            if len(detailes) == 3:
                row_num += 1
                sheet.write(row_num, 0, word, style=detail_style1)
                sheet.write(row_num, 1, detailes[0], style=detail_style1)
                sheet.write(row_num, 2, detailes[1], style=detail_style1)
                sheet.write(row_num, 3, detailes[2], style=detail_style2)
            else:
                for i in range(0, int(len(detailes)/3)):
                    row_num += 1
                    if i == 0:
                        sheet.write(row_num, 0, word, style=detail_style1)
                    sheet.write(row_num, 1, detailes[0 + 3*i], style=detail_style1)
                    sheet.write(row_num, 2, detailes[1 + 3*i], style=detail_style1)
                    sheet.write(row_num, 3, detailes[2 + 3*i], style=detail_style2)

    sheet.col(0).width = int(256*12.61)
    sheet.col(1).width = int(256*12.61)
    sheet.col(2).width = int(256*39.23)
    sheet.col(3).width = int(256*5.74)
    f.save(output_file)


if __name__ == '__main__':
    base_path = sys.argv[1]
    # base_path = "E:\园园\merge"
    files= os.listdir(base_path)
    file_dict = {}
    for file in files:
        num = re.findall(r'\d+', file)
        if num:
            file_dict[num[0]] = file
    file_order = sorted(file_dict)
    print("开始合并........")
    for k in file_order:
        read_excel_for_merge(os.path.join(base_path, file_dict[k]), 0, k)
    # process_data()
    output_file = os.path.join(base_path, "笔画检索汇总版.xls")
    write_excel_for_merge(output_file)
    print("合并的文件保存至：" + output_file)
    for num, values in ignored_lines.items():
        if values:
            sys.stderr.write(f"注意：合并时，{num}中第" + ",".join(values) + "行，无法处理，请稍后自行手动处理，谢谢合作.\n")

    print("开始排序........")
    ignored_lines = []
    text_dict = OrderedDict()

    read_excel_for_order(output_file, 0)
    process_data()
    output_file = os.path.join(base_path, "笔画检索汇总版_排序版.xls")
    write_excel_for_order(output_file)
    print("排序的文件保存至：" + output_file)
    if ignored_lines:
        sys.stderr.write("注意：排序时，Excel中第" + ",".join(ignored_lines) + "行，无法处理，请稍后自行手动处理，谢谢合作.\n")

    print("It's over, good job.")


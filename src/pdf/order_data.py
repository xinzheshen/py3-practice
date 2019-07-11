# -*- coding: utf-8 -*-
import sys

import xlrd
import xlwt
from collections import OrderedDict

text_dict = OrderedDict()
text_dict_sorted =OrderedDict()

title = "筆畫檢索"
word_er = "兒"
word_op = "（"

ignored_lines = []

def read_excel(file_path, index):
    print("Reading excel file...")
    global text_dict
    words = []

    excelFile = xlrd.open_workbook(file_path)
    sheet = excelFile.sheet_by_index(index)
    current_group = ""
    for row_no in range(0, sheet.nrows):
        cell_value_0 = sheet.cell_value(row_no, 0)
        cell_value_1 = sheet.cell_value(row_no, 1)
        cell_value_2 = sheet.cell_value(row_no, 2)
        try:
            print(str(row_no) + " : " + cell_value_0, cell_value_1, cell_value_2)
        except Exception:
            ignored_lines.append(str(row_no + 1))
            continue
        if current_group and current_group not in text_dict.keys():
            text_dict[current_group] = OrderedDict()
        if cell_value_1:
            key = cell_value_0[0]
            if key not in text_dict[current_group].keys():
                text_dict[current_group][key] = OrderedDict()
            if cell_value_0 in words:
                text_dict[current_group][key][cell_value_0].extend([cell_value_1, cell_value_2])
            else:
                text_dict[current_group][key][cell_value_0] = [cell_value_1, cell_value_2]
            words.append(cell_value_0)
        else:
            if cell_value_0 != "筆畫檢索":
                current_group = cell_value_0


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


def write_excel(output_file):
    global text_dict_sorted
    print("Wtring excel file...")
    f = xlwt.Workbook()
    sheet = f.add_sheet('sheet',cell_overwrite_ok=True)
    sheet.write_merge(0, 0, 0, 2, title, style=set_style("黑体", 20*16, bold=True, title=True))
    strokes_style = set_style("宋体", 20*14, bold=True, title=True)
    detail_style1 = set_style("宋体", 20*12)
    detail_style2 = set_style("宋体", 20*12, right=True)
    row_num = 0
    for strokes, value in text_dict_sorted.items():
        row_num += 1
        sheet.write_merge(row_num, row_num, 0, 2, strokes, style=strokes_style)
        for word, detailes in value.items():
            if len(detailes) == 2:
                row_num += 1
                sheet.write(row_num, 0, word, style=detail_style1)
                sheet.write(row_num, 1, detailes[0], style=detail_style1)
                sheet.write(row_num, 2, detailes[1], style=detail_style2)
            else:
                for i in range(0, int(len(detailes)/2)):
                    row_num += 1
                    if i == 0:
                        sheet.write(row_num, 0, word, style=detail_style1)
                    sheet.write(row_num, 1, detailes[0 + 2*i], style=detail_style1)
                    sheet.write(row_num, 2, detailes[1 + 2*i], style=detail_style2)

    sheet.col(0).width = int(256*12.61)
    sheet.col(1).width = int(256*39.23)
    sheet.col(2).width = int(256*5.74)
    f.save(output_file)


if __name__ == '__main__':
    file_path = sys.argv[1]
    # with open("./fileName.txt", "br") as f:
    #     file_path = str(f.readline(), encoding="utf8").strip()
    read_excel(file_path, 0)
    process_data()
    output_file = file_path[0:file_path.rfind(".")] + "_排序版.xls"
    write_excel(output_file)
    if ignored_lines:
        sys.stderr.write("注意：Excel中第" + ",".join(ignored_lines) + "行，无法处理，请稍后自行手动处理，谢谢合作.\n")
    print("It's over, good job.")
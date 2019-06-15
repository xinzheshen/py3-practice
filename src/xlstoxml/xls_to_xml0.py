#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xlrd
from xml.dom.minidom import Document
from collections import OrderedDict

ScreenName_COL_NO = 0
ElementName_COL_NO = 1
Text_COL_NO = 2
ResourceID_COL_NO = 3
Class_COL_NO = 4
AppPackage_COL_NO = 5


def read_excel():
    groups_dict = OrderedDict()
    ignored_groups = []

    # 文件位置

    excelFile = xlrd.open_workbook(r'D:\cats\bugs\1647exceltoxml\Sample\11.xlsx')

    # 获取目标EXCEL文件sheet名

    print(excelFile.sheet_names())

    #sheet2_name=ExcelFile.sheet_names()[1]

    # 读数据
    #sheet=ExcelFile.sheet_by_index(1)

    sheet = excelFile.sheet_by_name('Audio Elements Locators')

    current_group = ""
    in_ignored_group = False

    for row_no in range(1, sheet.nrows):
        row_values = sheet.row_values(row_no)
        group = row_values[0]
        if group:
            if group not in ignored_groups:
                if group not in groups_dict.keys():
                    groups_dict[group] = {}
                    current_group = group
                    in_ignored_group = False
                else:
                    ignored_groups.append(group)
                    del groups_dict[group]
                    in_ignored_group = True
        if not in_ignored_group:
            groups_dict[current_group][row_no] = row_values[0: AppPackage_COL_NO + 1]

    print(groups_dict)
    print("end")
    # print(sheet.name, sheet.nrows, sheet.ncols)
    #
    # #获取整行或者整列的值
    #
    # rows = sheet.row_values(2)#第三行内容
    #
    # cols = sheet.col_values(1)#第二列内容
    #
    # print(cols)
    # print(rows)
    #
    # #获取单元格内容
    #
    # print(sheet.cell(1, 0).value.encode('utf-8'))
    #
    # print(sheet.cell_value(1, 0).encode('utf-8'))
    #
    # print(sheet.row(1)[0].value.encode('utf-8'))
    #
    # #打印单元格内容格式
    #
    # print(sheet.cell(1, 0).ctype)
def clean_string(s):
    s = str(s).lower().strip()
    s = s.replace(r' ', '_')
    s = s.replace(r'~', '_')
    s = s.replace(r'!', '_')
    s = s.replace(r'@', '_')
    s = s.replace(r'#', '_')
    s = s.replace(r'$', '_')
    s = s.replace(r'%', '_')
    s = s.replace(r'^', '_')
    s = s.replace(r'&', '_')
    s = s.replace(r'*', '_')
    s = s.replace(r'(', '_')
    s = s.replace(r')', '_')
    s = s.replace(r'{', '_')
    s = s.replace(r'}', '_')
    s = s.replace(r'|', '_')
    s = s.replace(r'<', '_')
    s = s.replace(r'>', '_')
    s = s.replace(r'?', '_')
    s = s.replace(r'=', '_')
    s = s.replace(r'"', '_')
    s = s.replace(r"'", '_')
    s = s.replace(r',', '_')
    s = s.replace(r'\\', '_')
    s = s.replace(r';', '_')
    s = s.replace(r'/', '_')
    return s


if __name__ == '__main__':
    read_excel()

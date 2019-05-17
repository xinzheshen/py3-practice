#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import xlrd
from xml.dom.minidom import Document
from collections import OrderedDict
import re
import traceback

CLASS = 'class.xml'
PACKAGE = 'package.xml'
ID = 'id.{0}.xml'
TEXT = 'text.{0}.xml'

OUTPUT_FOLDER = ''
CSM_BUILD_VERSION = 'CSM build version: %s'

ScreenName_COL_NO = 0
ElementName_COL_NO = 1
Text_COL_NO = 2
ResourceID_COL_NO = 3
Class_COL_NO = 4
AppPackage_COL_NO = 5

PATTERN = re.compile(r'[ ~!@#$%^&*(){}|<>?="`\',\\;/]')


def read_excel(file_path, index):
    text_dict = OrderedDict()
    id_dict = OrderedDict()
    class_dict = OrderedDict()
    package_dict = OrderedDict()
    groups = []
    texts = []

    excelFile = xlrd.open_workbook(file_path)
    sheet = excelFile.sheet_by_index(index)
    current_group = ""
    for row_no in range(1, sheet.nrows):
        row_values = []
        for col_no in range(ScreenName_COL_NO, AppPackage_COL_NO + 1):
            cell_type = sheet.cell(row_no, col_no).ctype
            cell_value = sheet.cell_value(row_no, col_no)
            # datetime
            if cell_type == 3:
                cell_value = \
                    str(xlrd.xldate_as_datetime(sheet.cell_value(row_no, col_no), excelFile.datemode)).split(" ")[1][:5]
                if cell_value.startswith('0'):
                    cell_value = cell_value[1:]
            # number
            elif cell_type == 2 and cell_value == int(cell_value):
                cell_value = int(cell_value)
            row_values.append(cell_value)
        group = clean_string(row_values[0])
        if group and (group not in groups):
            groups.append(group)
            texts.clear()
            current_group = group
            text_dict[current_group] = OrderedDict()
            id_dict[current_group] = OrderedDict()

        if current_group:
            # organize text and id data
            if str(row_values[Text_COL_NO]).lower().strip() != 'no' and str(row_values[Text_COL_NO]).lower().strip() != '':
                text = clean_string(row_values[Text_COL_NO])
                text_dict[current_group][text] = row_values[Text_COL_NO]
                if text not in texts:
                    id_dict[current_group][text] = row_values[ResourceID_COL_NO]
                else:
                    num = texts.count(text) + 1
                    id_dict[current_group][text + '_' + str(num)] = row_values[ResourceID_COL_NO]
                texts.append(text)
            elif str(row_values[ElementName_COL_NO]).lower().strip() != '':
                id_dict[current_group][clean_string(row_values[ElementName_COL_NO])] = row_values[ResourceID_COL_NO]

            # organize class data
            class_data = clean_string(row_values[Class_COL_NO])
            if class_data != 'no' and class_data != "":
                class_name = '.'.join(class_data.split('.')[-2:])
                class_dict[class_name] = row_values[Class_COL_NO]

            # organize package data
            package_data = clean_string(row_values[AppPackage_COL_NO])
            if package_data != 'no' and package_data != "":
                package_name = package_data.split('.')[-1]
                package_dict[package_name] = row_values[AppPackage_COL_NO]

    return text_dict, id_dict, class_dict, package_dict


def clean_string(s):
    return re.sub(PATTERN, '_', str(s).lower().strip())


def write_xml(data, file_name, id_or_text=False):
    doc = Document()
    doc.appendChild(doc.createComment(CSM_BUILD_VERSION))
    caseVars_E = doc.createElement("CaseVars")
    doc.appendChild(caseVars_E)
    if id_or_text:
        for group, values in data.items():
            group_E = doc.createElement("Group")
            group_E.setAttribute("name", group)

            for name, value in values.items():
                item_E = doc.createElement("Item")
                item_E.setAttribute("desc", "")
                item_E.setAttribute("name", name)
                item_E.setAttribute("type", "String")
                value_text = doc.createTextNode(str(value))
                item_E.appendChild(value_text)
                group_E.appendChild(item_E)

            caseVars_E.appendChild(group_E)
    else:
        group_E = doc.createElement("Group")
        group_E.setAttribute("name", file_name.split('.')[0])
        for name, value in data.items():
            item_E = doc.createElement("Item")
            item_E.setAttribute("desc", "")
            item_E.setAttribute("name", name)
            item_E.setAttribute("type", "String")
            value_text = doc.createTextNode(str(value))
            item_E.appendChild(value_text)
            group_E.appendChild(item_E)

        caseVars_E.appendChild(group_E)

    output_file = os.path.join(OUTPUT_FOLDER, file_name)
    with open(output_file, 'w', encoding='utf-8') as f:
        # f.write("<!--csm build version: -->\n")
        doc.writexml(f, newl='\n', addindent='\t', encoding='utf-8')


def process_argv():
    parser = argparse.ArgumentParser(prog='xls2xml')
    parser.add_argument('--input', '-i',
                        help='The path of input xls file.',
                        required=True)
    parser.add_argument('--sheet', '-s',
                        help='The index of sheet to process in xls file (start from 0).',
                        default=1,
                        type=int,
                        required=False)
    parser.add_argument('--output', '-o',
                        help='The path of output folder.',
                        required=True)
    parser.add_argument('--version', '-v',
                        help='The build version of CSM.',
                        default="",
                        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    try:
        arg = process_argv()
        file_path = arg.input
        index = arg.sheet
        OUTPUT_FOLDER = arg.output
        CSM_BUILD_VERSION = CSM_BUILD_VERSION % arg.version

        file_name = re.split('/|\\\\', file_path)[-1].split('.')[0]
        ID = ID.format(file_name)
        TEXT = TEXT.format(file_name)

        # file_path = r'D:\cats\bugs\1647exceltoxml\Sample\Audio_App_properties_Details.xlsx'
        text_dict, id_dict, class_dict, package_dict = read_excel(file_path, index)

        write_xml(text_dict, TEXT, True)
        write_xml(id_dict, ID, True)
        write_xml(class_dict, CLASS)
        write_xml(package_dict, PACKAGE)
    except Exception as e:
        print(e)
        traceback.print_exc()

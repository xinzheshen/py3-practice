#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import xlrd
from xml.dom.minidom import Document, parse
from collections import OrderedDict, ChainMap
import re
import traceback
import logging


DEFAULT_GROUP = 'default'

SHEET_NAME = ''
OUTPUT_FOLDER = ''
OUTPUT_FOLDER_TEXT = 'texts'
OUTPUT_FOLDER_RESOURCE = 'resids'
OUTPUT_FOLDER_CLASSINFO = 'classinfos'
FOLDER_PATH_FOR_UPDATING_XML = ''

TMP_BUILD_VERSION = 'TMP build version: %s'

# column name
SCREEN_NAME = "Screen Name"
ELEMENTNAME = "ElementName"
TEXT = "Text"
RESOURCE_ID = "ResourceID"
CLASS = "Class"
APPPACKAGE = "Apppackage"
CONTENT_DESC = "Content - Desc"

ScreenName_COL_NO = 0
SubScreenName_COL_NO = 0
ElementName_COL_NO = 0
Text_COL_NO = 0
ResourceID_COL_NO = 0
Class_COL_NO = 0
AppPackage_COL_NO = 0
ContentDesc_COL_NO = 0

PATTERN = re.compile(r'[ ~!@#$%^&*().{}|<>?=\-+:"`\',\\;/]')

CURRENT_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_LOG = "xls2xml.log"
DEFAULT_OUTPUT_PATH = os.path.join(CURRENT_PATH, OUTPUT_LOG)
logging.basicConfig(level=logging.INFO,
                    filename=DEFAULT_OUTPUT_PATH,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )


def printInfo(msg):
    print(msg)
    logging.info(msg)


def get_excel_sheet(file_path):
    excel_file = xlrd.open_workbook(file_path)
    sheet_names = excel_file.sheet_names()
    return excel_file, sheet_names


def read_sheet_data(excel_obj, sheet_name):
    text_dict = OrderedDict()
    id_dict = OrderedDict()
    class_and_package_dict = OrderedDict()
    class_and_package_dict[DEFAULT_GROUP] = OrderedDict()

    groups = []
    element_names = []

    merged_cells_map = {}
    sheet = excel_obj.sheet_by_name(sheet_name)
    get_merged_cells_value(sheet, merged_cells_map)

    get_column_index(sheet.row_values(0))

    current_group = ""
    for row_no in range(1, sheet.nrows):
        row_values = []
        for col_no in range(ScreenName_COL_NO, ContentDesc_COL_NO + 1):
            if merged_cells_map.get((row_no, col_no)):
                cell_type = sheet.cell(*merged_cells_map.get((row_no, col_no))).ctype
                cell_value = sheet.cell_value(*merged_cells_map.get((row_no, col_no)))
            else:
                cell_type = sheet.cell(row_no, col_no).ctype
                cell_value = sheet.cell_value(row_no, col_no)
            # datetime
            if cell_type == 3:
                cell_value = \
                    str(xlrd.xldate_as_datetime(sheet.cell_value(row_no, col_no), excel_obj.datemode)).split(" ")[1][:5]
                if cell_value.startswith('0'):
                    cell_value = cell_value[1:]
            # number
            elif cell_type == 2 and cell_value == int(cell_value):
                cell_value = int(cell_value)
            row_values.append(cell_value)

        group = get_group_name(row_values[ScreenName_COL_NO:ElementName_COL_NO])
        if group and (group not in groups):
            groups.append(group)
            element_names.clear()
            current_group = group
            text_dict[current_group] = OrderedDict()
            id_dict[current_group] = OrderedDict()

        if current_group:
            # organize text and id data
            if str(row_values[ElementName_COL_NO]).lower().strip():
                # process the element as key
                element_name = clean_string(row_values[ElementName_COL_NO])
                text = str(row_values[Text_COL_NO]).lower().strip()
                resource_id = str(row_values[ResourceID_COL_NO]).lower().strip()
                # text_keys = text_dict[current_group].keys()
                # id_keys = id_dict[current_group].keys()
                # if element_name in text_keys or element_name in id_keys:
                #     element_name_bac = element_name
                #     element_name = element_name + "_" + clean_string(text)
                #     if element_name in text_keys or element_name in id_keys:
                #         element_name = element_name_bac + clean_string(resource_id)

                element_names.append(element_name)
                num = element_names.count(element_name)
                if num > 1:
                    element_name += "_" + str(num)

                # organize text data
                if text != 'no' and text != '':
                    text_dict[current_group][element_name] = row_values[Text_COL_NO]
                elif str(row_values[ContentDesc_COL_NO]).lower().strip() != 'no' and str(row_values[ContentDesc_COL_NO]).lower().strip() != '':
                    text_dict[current_group][element_name] = row_values[ContentDesc_COL_NO]
                else:
                    logging.info("The text content is empty for element_name: " + element_name + " in group: " + current_group)
                # organize id data
                if resource_id != 'no' and resource_id != '':
                    id_dict[current_group][element_name] = row_values[ResourceID_COL_NO]
                else:
                    logging.info("The resource_id content is empty for element_name: " + element_name + " in group: " + current_group)

            # organize class and package data
            class_data = clean_string(row_values[Class_COL_NO])
            if class_data != 'no' and class_data != "":
                class_name = "class_" + class_data
                class_and_package_dict[DEFAULT_GROUP][class_name] = row_values[Class_COL_NO]

            # organize package data
            package_data = clean_string(row_values[AppPackage_COL_NO])
            if package_data != 'no' and package_data != "":
                package_name = "package_" + package_data
                class_and_package_dict[DEFAULT_GROUP][package_name] = row_values[AppPackage_COL_NO]

    return text_dict, id_dict, class_and_package_dict


def get_group_name(values):
    screen_and_sub_screen_names = list(map(clean_string, values))
    group = "_".join(list(filter(lambda s: s and s.strip, screen_and_sub_screen_names)))
    return group


def get_merged_cells_value(sheet, merged_cells_map):
    if sheet.merged_cells:
        for item in sheet.merged_cells:
            for row in range(item[0], item[1]):
                for col in range(item[2], item[3]):
                    if (row, col) != (item[0], item[2]):
                        merged_cells_map.update({(row, col): (item[0], item[2])})


def get_column_index(first_row_values):
    global ScreenName_COL_NO
    global ElementName_COL_NO
    global Text_COL_NO
    global ResourceID_COL_NO
    global Class_COL_NO
    global AppPackage_COL_NO
    global ContentDesc_COL_NO

    ScreenName_COL_NO = first_row_values.index(SCREEN_NAME)
    ElementName_COL_NO = first_row_values.index(ELEMENTNAME)
    Text_COL_NO = first_row_values.index(TEXT)
    ResourceID_COL_NO = first_row_values.index(RESOURCE_ID)
    Class_COL_NO = first_row_values.index(CLASS)
    AppPackage_COL_NO = first_row_values.index(APPPACKAGE)
    ContentDesc_COL_NO = first_row_values.index(CONTENT_DESC)


def clean_string(s):
    s = str(s).lower().strip()
    s = re.sub(PATTERN, '_', s)
    s = re.sub(r'_{2,}', '_', s)
    if s.endswith("_"):
        s = s[:-1]
    return s


def update_and_write_xml(data, sub_output_folder):
    global SHEET_NAME
    old_data = ''
    if FOLDER_PATH_FOR_UPDATING_XML:
        try:
            old_data = read_xml_file(sub_output_folder)
        except Exception as e:
            logging.error("Failed to read pre-existing xml file, and will generate the new xml file just according to the excel file.")
        else:
            if old_data:
                printInfo("To update the data of %s in sheet %s." % (sub_output_folder, SHEET_NAME))
                try:
                    data = update_data(old_data, data)
                except Exception as e:
                    logging.error("Failed to update the data of %s in sheet %s." % (sub_output_folder, SHEET_NAME) + ", error:" + str(e))

    write_xml_file(data, sub_output_folder)


def update_data(old_data, new_data):
    updated_data = OrderedDict()
    old_data_groups = old_data.keys()

    for group, values in new_data.items():
        if group in old_data_groups:
            updated_data[group] = ChainMap(values, old_data[group])
        else:
            if values:
                printInfo("Added group: " + group)
            updated_data[group] = values

    missing_groups = old_data_groups - new_data.keys()
    if missing_groups:
        printInfo("Missing groups: " + str(missing_groups))
        for group in missing_groups:
            updated_data[group] = old_data[group]

    return updated_data


def write_xml_file(data, sub_output_folder):
    doc = Document()
    doc.appendChild(doc.createComment(TMP_BUILD_VERSION))
    caseVars_E = doc.createElement("CaseVars")
    doc.appendChild(caseVars_E)
    for group, values in data.items():
        # if the group is empty, annotation it.
        if not values:
            caseVars_E.appendChild(doc.createComment("<Group name=\"%s\"/>" % group))
            continue

        group_E = doc.createElement("Group")
        group_E.setAttribute("name", group)
        for name, value in sorted(values.items()):
            item_E = doc.createElement("Item")
            item_E.setAttribute("desc", "")
            item_E.setAttribute("name", name)
            item_E.setAttribute("type", "String")
            value_text = doc.createTextNode(str(value))
            item_E.appendChild(value_text)
            group_E.appendChild(item_E)

        caseVars_E.appendChild(group_E)

    output_folder = os.path.join(OUTPUT_FOLDER, sub_output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = os.path.join(output_folder, SHEET_NAME) + ".xml"
    with open(output_file, 'w', encoding='utf-8') as f:
        doc.writexml(f, newl='\n', addindent='\t', encoding='utf-8')


def read_xml_file(sub_folder):
    file_path = os.path.join(FOLDER_PATH_FOR_UPDATING_XML, sub_folder, SHEET_NAME + ".xml")
    data_dict = None
    if os.path.isfile(file_path):
        try:
            data_dict = OrderedDict()
            DOMTree = parse(file_path)
            collection = DOMTree.documentElement
            groups = collection.getElementsByTagName("Group")
            for group in groups:
                group_value = group.getAttribute("name")
                data_dict[group_value] = OrderedDict()
                items = group.getElementsByTagName('Item')
                for item in items:
                    data_dict[group_value][item.getAttribute("name")] = item.childNodes[0].data
        except Exception as e:
            traceback.print_exc(file=open(DEFAULT_OUTPUT_PATH, "a+"))
            raise Exception("Failed to read xml.") from e
    else:
        print("File does not exist: " + file_path)
        logging.warning("File does not exist: " + file_path)
    return data_dict


def process_argv():
    parser = argparse.ArgumentParser(prog='xls2xml')
    parser.add_argument('--input', '-i',
                        help='The path of input xls file.',
                        required=True)
    parser.add_argument('--selection', '-s',
                        help='The selection about which sheet index and column to process in xls file (The sheet index starts from 0).',
                        default="",
                        required=False)
    parser.add_argument('--output', '-o',
                        help='The path of output folder.',
                        default='./output',
                        required=False)
    parser.add_argument('--version', '-v',
                        help='The build version of TMP.',
                        default="",
                        required=False)
    parser.add_argument('--folder', '-f',
                        help='The folder path containing texts, resids or classinfos, for updating the xml files.',
                        default=None,
                        required=False)
    return parser.parse_args()


def main():
    global TMP_BUILD_VERSION
    global SHEET_NAME
    global OUTPUT_FOLDER
    global FOLDER_PATH_FOR_UPDATING_XML

    arg = process_argv()
    file_path = arg.input
    indexes = arg.selection
    OUTPUT_FOLDER = arg.output
    TMP_BUILD_VERSION = TMP_BUILD_VERSION % arg.version
    FOLDER_PATH_FOR_UPDATING_XML = arg.folder
    printInfo("Start xls2xml, -i: %s, -s: %s, -o: %s, -f: %s" % (file_path, indexes, OUTPUT_FOLDER, FOLDER_PATH_FOR_UPDATING_XML))

    # indexes = "0-texts,resids,classinfos;1-texts;3"
    index_dict = {}
    if indexes:
        for index in indexes.strip().split(";"):
            tmp = index.split("-")
            index_dict[tmp[0]] = [x for x in tmp[1].split(",")] if len(tmp) > 1 else None

    excel_obj, sheet_names = get_excel_sheet(file_path)

    if index_dict:
        for key, value in index_dict.items():
            try:
                SHEET_NAME = sheet_names[int(key)]
                printInfo("------------- Start process the sheet: " + SHEET_NAME + ", index: " + str(key))
                text_dict, id_dict, class_and_package_dict = read_sheet_data(excel_obj, SHEET_NAME)
                if value:
                    if OUTPUT_FOLDER_TEXT in value:
                        update_and_write_xml(text_dict, OUTPUT_FOLDER_TEXT)
                    if OUTPUT_FOLDER_RESOURCE in value:
                        update_and_write_xml(id_dict, OUTPUT_FOLDER_RESOURCE)
                    if OUTPUT_FOLDER_CLASSINFO in value:
                        update_and_write_xml(class_and_package_dict, OUTPUT_FOLDER_CLASSINFO)
                    printInfo("Success to process the sheet with index: " + key + ", column: " + ",".join(value))
                else:
                    update_and_write_xml(text_dict, OUTPUT_FOLDER_TEXT)
                    update_and_write_xml(id_dict, OUTPUT_FOLDER_RESOURCE)
                    update_and_write_xml(class_and_package_dict, OUTPUT_FOLDER_CLASSINFO)
                    printInfo("Success to process the sheet with index: " + key)
            except Exception as e:
                print("Failed to process the sheet with index: " + key + ", error: " + str(e))
                logging.error("Failed to process the sheet with index: " + key + ", error: " + str(e))
                traceback.print_exc(file=open(DEFAULT_OUTPUT_PATH, "a+"))
    else:
        for sheet_name in sheet_names:
            try:
                SHEET_NAME = sheet_name
                printInfo("------------- Start process the sheet: " + SHEET_NAME)
                text_dict, id_dict, class_and_package_dict = read_sheet_data(excel_obj, sheet_name)
                update_and_write_xml(text_dict, OUTPUT_FOLDER_TEXT)
                update_and_write_xml(id_dict, OUTPUT_FOLDER_RESOURCE)
                update_and_write_xml(class_and_package_dict, OUTPUT_FOLDER_CLASSINFO)
                printInfo("Success to process the sheet: " + sheet_name)
            except ValueError as e:
                print("Failed to process the sheet: " + sheet_name + ", error: " + str(e) + ". Maybe the sheet content is wrong.")
                logging.error("Failed to process the sheet: " + sheet_name + ", error: " + str(e) + ". Maybe the sheet content is wrong.")
                traceback.print_exc(file=open(DEFAULT_OUTPUT_PATH, "a+"))
            except Exception as e:
                print("Failed to process the sheet: " + sheet_name + ", error: " + str(e))
                logging.error("Failed to process the sheet: " + sheet_name + ", error: " + str(e))
                traceback.print_exc(file=open(DEFAULT_OUTPUT_PATH, "a+"))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        logging.error(e)
        traceback.print_exc(file=open(DEFAULT_OUTPUT_PATH, "a+"))

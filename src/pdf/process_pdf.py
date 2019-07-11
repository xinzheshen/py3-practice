# -*- coding: utf-8 -*-
import pdfplumber
import xlwt
from collections import OrderedDict

word_index_dict = OrderedDict()
last_word = ""
strokes_number = ""
title = "筆畫目錄"
separation = "……………………………………………"

def read_pdf(file):
    print("Reading pdf file...")
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text_lines = page.extract_text()
            process_data(text_lines, page.page_number)
            # words = page.extract_words()


def process_data(text_lines, page_number):
    global word_index_dict, last_word, strokes_number
    text_lines = text_lines.split("\n")
    for line in text_lines:
        words = line.split(" ")
        if len(words) == 1:
            if "畫" in words[0] and "筆畫檢索" != words[0]:
                strokes_number = words[0]
                word_index_dict[strokes_number] = OrderedDict()
                # print(" "*5 + strokes_number + " "*5)
        else:
            current_word = words[0][0]
            if current_word != last_word:
                word_index_dict[strokes_number][current_word] = str(page_number)
                # print(current_word + "."*8 + str(page_number))
                last_word = current_word


def set_style(name, height, bold=False, right=False):
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
    else:
        alignment.horz = 0x02
    # 0x00(上端对齐)、 0x01(垂直方向上居中对齐)、0x02(底端对齐)
    alignment.vert = 0x01

    style.font = font
    style.alignment = alignment
    return style


def write_excel(output_file):
    global word_index_dict
    print("Wtring excel file...")
    f = xlwt.Workbook()
    sheet = f.add_sheet('sheet',cell_overwrite_ok=True)
    sheet.write_merge(0, 0, 0, 2, title, style=set_style("黑体", 20*16, bold=True))
    strokes_style = set_style("宋体", 20*14, bold=True)
    detail_style1 = set_style("宋体", 20*12)
    detail_style2 = set_style("宋体", 20*12, right=True)
    row_num = 0
    for strokes, value in word_index_dict.items():
        row_num += 1

        sheet.write_merge(row_num, row_num, 0, 2, strokes, style=strokes_style)
        for word, page in value.items():
            row_num += 1
            sheet.write(row_num, 0, word, style=detail_style1)
            sheet.write(row_num, 1, separation, style=detail_style1)
            sheet.write(row_num, 2, page, style=detail_style2)

    sheet.col(0).width = int(256*12.61)
    sheet.col(1).width = int(256*39.23)
    sheet.col(2).width = int(256*5.74)
    f.save(output_file)


if __name__ == '__main__':
    file_path = ""
    with open("./fileName.txt", "br") as f:
        file_path = str(f.readline(), encoding="utf8").strip()
    read_pdf(file_path)
    output_file = file_path[0:-4] + "_筆畫目錄.xls"
    write_excel(output_file)
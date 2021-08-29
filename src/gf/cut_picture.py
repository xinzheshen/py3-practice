import os
import datetime
import json
import sys
import pdfplumber
import fitz  # 对应的是PyMuPDF

from argparse import ArgumentParser

def get_column_num():
    column_num = 6
    if page_range_info[0] == page_range_info[2]:
        column_num = page_range_info[3] // 4
        remainder_num = page_range_info[3] // 4

        if remainder_num != 0:
            column_num += 1



def cut_picture_from_pdf():
    """
    https://blog.csdn.net/zbj18314469395/article/details/98329442
    """

    column_num = 6

    pdf_doc = fitz.open(pdf_file_path)
    for pg in range(pdf_doc.pageCount):
        if page_range_info[0] <= (pg + 1) <= page_range_info[1]:
            page = pdf_doc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
            # 此处若是不做设置，默认图片大小为：792X612, dpi=72
            zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
            zoom_y = 1.33333333
            mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            rect = page.rect  # 页面大小
            # mp = rect.tl + (rect.bl - (0, 400 / zoom_x))  # 矩形区域    56=75/1.3333
            # clip = fitz.Rect(mp, rect.br)  # 想要截取的区域
            width = rect.x1
            x_start = width - right_side
            y_start = top_side
            x = x_start
            if start_num != -1:
                count = start_num
            else:
                # todo 计数
                count = page_range_info[3] + (pg - page_range_info[2]) * (6*4) + 1
            for i in range(6):
                y = y_start
                for j in range(4):
                    tl = (x - x_step, y)
                    br = (x, y + y_step)
                    # print(tl, br)

                    clip = fitz.Rect(tl, br)  # 想要截取的区域
                    pix = page.getPixmap(matrix=mat, alpha=False, clip=clip)

                    pix.writePNG(os.path.join(image_output_dir, f'{count}_{pg+1}.png'))  # 将图片写入指定的文件夹内

                    print(f"截取了第{chapter_num}章第{pg+1}页的总第{count}个字的图片。")

                    count += 1
                    y += y_step

                x -= x_step
            if page_num != 9999:
                break

    # endTime_pdf2img = datetime.datetime.now()  # 结束时间
    # print('pdf2img时间=', (endTime_pdf2img - startTime_pdf2img).seconds)


def get_process_pages():
    with open(r"./chapter_page_info.json", "r") as f:
        map_info = json.load(f)
    page_info = None
    if chapter_num is not None:
        page_info = map_info.get(str(chapter_num))

    if page_info is None:
        # print(f"chapter_page_info.json 中没有设置第{chapter_num}章的页码信息，请补充。")
        raise Exception(f"chapter_page_info.json 中没有设置第{chapter_num}的页码信息，请补充。")

    # 不处理章节起始页，因为零散不好计数
    start_page_num = page_info[0] + 1
    word_num_in_first_page = page_info[1]
    stop_page_num = 99999

    next_chapter_num = chapter_num + 1
    next_page_info = map_info.get(str(next_chapter_num))
    if next_page_info is not None:
        stop_page_num = next_page_info[0]

    if page_num != 9999:
        if page_num < start_page_num or page_num > stop_page_num:
            raise Exception(f"指定要处理的第{page_num}页，不在第{chapter_num}章范围内{start_page_num, stop_page_num}")
        else:
            start_page_num = page_num
            stop_page_num = page_num

    return start_page_num, stop_page_num, page_info[0], word_num_in_first_page


def process_argv():
    parser = ArgumentParser(prog='cut_picture')
    parser.add_argument('--pdf_file', help='PDF文件路径', type=str, required=True)
    parser.add_argument('--picture_path', help='截图存放路径', type=str, required=True)
    parser.add_argument('--chapter_num', help='第几章', type=int, default=16, required=False)
    parser.add_argument('--page_num', help='第几页', type=int, default=9999, required=False)
    parser.add_argument('--top_side', help='上边界距离截图区宽度', type=float, default=170, required=False)
    parser.add_argument('--right_side', help='右边界距离截图区宽度', type=float, default=80, required=False)
    parser.add_argument('--x_step', help='水平方向每次换列截图时增加的步长', type=float, default=73, required=False)
    parser.add_argument('--y_step', help='竖直方向每次换行截图时增加的步长', type=float, default=139, required=False)

    return parser.parse_args()


if __name__ == '__main__':
    # read_pdf(file_path)

    # arg = process_argv()

    # pdf_file_path = arg.pdf_file
    # picture_output_path = arg.picture_path
    # chapter_num = arg.chapter_num
    # page_num = arg.page_num
    # top_side = arg.top_side
    # right_side = arg.right_side
    # x_step = arg.x_step
    # y_step = arg.y_step

    pdf_file_path = r"D:\work\gf\截图\世尊寺本字镜.pdf"
    picture_output_path = r"D:\work\gf\截图\pictures"
    chapter_num = 15
    page_num = 88
    top_side = 205
    right_side = 77
    x_step = 70
    y_step = 133
    start_num = -1

    page_range_info = get_process_pages()

    image_output_dir = os.path.join(picture_output_path, str(chapter_num))

    if not os.path.exists(image_output_dir):  # 判断存放图片的文件夹是否存在
        os.makedirs(image_output_dir)  # 若图片文件夹不存在就创建

    cut_picture_from_pdf()


import xlrd


def read_excel(file_path):
    # 获取数据
    data = xlrd.open_workbook(file_path)
    # 获取所有sheet名字
    sheet_names = data.sheet_names()
    for sheet in sheet_names[1:]:
        # 获取sheet
        table = data.sheet_by_name(sheet)
        # 获取总行数
        nrows = table.nrows  # 包括标题
        # 获取总列数
        ncols = table.ncols

        # 计算出合并的单元格有哪些
        colspan = {}
        if table.merged_cells:
            for item in table.merged_cells:
                for row in range(item[0], item[1]):
                    for col in range(item[2], item[3]):
                        # 合并单元格的首格是有值的，所以在这里进行了去重
                        if (row, col) != (item[0], item[2]):
                            colspan.update({(row, col): (item[0], item[2])})
        # 读取每行数据
        for i in range(1, nrows):
            row = []
            for j in range(ncols):
                # 假如碰见合并的单元格坐标，取合并的首格的值即可
                if colspan.get((i, j)):
                    row.append(table.cell_value(*colspan.get((i, j))))
                else:
                    row.append(table.cell_value(i, j))
            print(row)

        # 读取每列数据
        print("*" * 40)
        for j in range(ncols):
            col = []
            for i in range(1, nrows):
                # 假如碰见合并的单元格坐标，取合并的首格的值即可
                if colspan.get((i, j)):
                    col.append(table.cell_value(*colspan.get((i, j))))
                else:
                    col.append(table.cell_value(i, j))
            print(col)

file_path = r"D:\cats\bugs\1647exceltoxml\Settings_ResourceIDs_New_Sample.xlsx"
read_excel(file_path)
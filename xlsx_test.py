import xlrd
import xlwt
import csv
import io


def xlsx_to_csv(xlsx_data: bytes):
    workbook = xlrd.open_workbook(file_contents=xlsx_data)
    table = workbook.sheet_by_index(0)
    csv_data = io.StringIO()
    write = csv.writer(csv_data)
    for row_num in range(table.nrows):
        row_value = table.row_values(row_num)
        write.writerow(row_value)
    csv_data.seek(0)
    print(csv_data.read())


def csv_to_xlsx(csv_data: str):
    f = io.StringIO(csv_data)
    read = csv.reader(f)
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('数据表1')  # 创建一个sheet表格
    l = 0
    for line in read:
        print(line)
        r = 0
        for i in line:
            print(i)
            sheet.write(l, r, i)  # 一个一个将单元格数据写入
            r = r + 1
        l = l + 1
    xlsx_io = io.BytesIO()
    workbook.save(filename_or_stream=xlsx_io)  # 保存Excel
    xlsx_io.seek(0)
    return xlsx_io.read()


if __name__ == '__main__':
    # with open('1.xlsx', 'rb') as _f:
    #     xlsx_to_csv(_f.read())
    with open('1.csv', 'r', encoding='utf8') as _f:
        print(csv_to_xlsx(_f.read()))

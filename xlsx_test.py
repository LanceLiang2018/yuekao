import xlrd
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


if __name__ == '__main__':
    with open('1.xlsx', 'rb') as _f:
        xlsx_to_csv(_f.read())

import copy
import hashlib
import json
import os
import time
import copy
from upload import *
from datetime import datetime
import requests


class DataBase:
    def __init__(self):
        self.file_db_init = "db_init.sql"

        self.tables = ['raw_data', 'student']

        self.hosts = ['127.0.0.1:5000', 'yuekao.herokuapp.com']

        # self.sql_type = "PostgreSQL"
        self.sql_types = {"SQLite": 0, "PostgreSQL": 1}
        # self.sql_type = self.sql_types['PostgreSQL']
        # self.sql_type = self.sql_types['SQLite']
        if os.environ.get('PORT', '5000') == '50001':
            # Local
            self.sql_type = self.sql_types['SQLite']
        else:
            # Remote
            self.sql_type = self.sql_types['PostgreSQL']
        self.sql_chars = ["?", "%s"]
        self.sql_char = self.sql_chars[self.sql_type]

        self.max_retry = 5

        self.connect_init()

    def v(self, string: str):
        return string.replace('%s', self.sql_char)

    def new_execute_write(self, string: str, args=(), retry=0):
        if retry > self.max_retry:
            raise Exception("Reach max retry times!")
        cursor = self.cursor_get()
        cursor.execute("BEGIN")
        try:
            if len(args) == 0:
                cursor.execute(self.v(string))
            else:
                cursor.execute(self.v(string), args)
        except Exception:
            cursor.execute("ROLLBACK")
            self.cursor_finish(cursor)
            self.new_execute_write(string, args=args, retry=retry+1)
            return
        self.cursor_finish(cursor)

    def new_execute_read(self, string: str, args=(), retry=0):
        if retry > self.max_retry:
            raise Exception("Reach max retry times!")
        cursor = self.cursor_get()
        cursor.execute("BEGIN")
        try:
            if len(args) == 0:
                cursor.execute(self.v(string))
            else:
                cursor.execute(self.v(string), args)
            data = cursor.fetchall()
            self.cursor_finish(cursor)
            return data
        except Exception as e:
            print('Exception:', e)
            cursor.execute("ROLLBACK")
            self.cursor_finish(cursor)
            return self.new_execute_write(string, args=args, retry=retry + 1)

    def connect_init(self):
        if self.sql_type == self.sql_types['SQLite']:
            import sqlite3 as sql
            self.conn = sql.connect('data_sql.db', check_same_thread=False)
        else:
            import psycopg2 as sql
            '''
            self.conn = sql.connect(host='ec2-23-21-160-38.compute-1.amazonaws.com',
                                    database='d6bagosv2bo9p8',
                                    user='dtzixfehvkttfq',
                                    port='5432',
                                    password='55e46bbde1772cb32715d4f52f51ad847ba3fe5af88902161336d56eb6c8a3c5')
            '''
            self.conn = sql.connect(host='ec2-23-21-160-38.compute-1.amazonaws.com',
                                    database='d7trt1mao0h1fm',
                                    user='miurmoscuiovyg',
                                    port='5432',
                                    password='ae48f928cb75b0554574e5acb7c60053cdcde42125896c80d627abfacd8771d6')

    def cursor_get(self):
        cursor = self.conn.cursor()
        return cursor

    def cursor_finish(self, cursor):
        self.conn.commit()
        cursor.close()

    def db_init(self):
        try:
            cursor = self.cursor_get()
            for table in self.tables:
                try:
                    cursor.execute("DROP TABLE IF EXISTS %s" % table)
                except Exception as e:
                    print('Error when dropping:', table, '\nException:\n', e)
                    self.cursor_finish(cursor)
                    cursor = self.cursor_get()
            self.cursor_finish(cursor)
        except Exception as e:
            print(e)
        self.conn.close()
        self.connect_init()
        cursor = self.cursor_get()
        # 一次只能执行一个语句。需要分割。而且中间居然不能有空语句。。
        with open(self.file_db_init, encoding='utf8') as f:
            string = f.read()
            for s in string.split(';'):
                try:
                    if s != '':
                        cursor.execute(s)
                except Exception as e:
                    print('Error:\n', s, 'Exception:\n', e)
        self.cursor_finish(cursor)

    def db_backup(self):
        backup = {}
        if self.sql_type == self.sql_types['SQLite']:
            is_sqlite = True
        else:
            is_sqlite = False
        for table in self.tables:
            backup[table] = {}
            try:
                if is_sqlite:
                    labels_data = self.new_execute_read("PRAGMA table_info('%s')" % table)
                else:
                    labels_data = self.new_execute_read("select name from sys.syscolumns where id=object_id('%s');" % table)
            except Exception:
                with open(self.file_db_init) as f:
                    labels_data = f.read()
            backup[table]['labels'] = labels_data
            backup[table]['data'] = self.new_execute_read("SELECT * FROM %s" % table)

        backup_json = json.dumps(backup)
        backup_json_io = io.BytesIO(backup_json.encode('utf8'))
        timedata = time.localtime(time.time())
        cndata = datetime(timedata[0], timedata[1], timedata[2], timedata[3], timedata[4], timedata[5])
        upload_file('backups/database/%s.json' % str(cndata), backup_json_io)

        csv_data = requests.get('http://%s/data?download=True&start_month=all&'
                                'start_date=all&end_month=all&end_date=all&'
                                'group_name=all&subject=all&'
                                'conclude=False' % self.hosts[self.sql_type]).content
        csv_io = io.BytesIO(csv_data)
        upload_file('backups/csv/%s.csv' % str(cndata), csv_io)

    def new_submit(self, group_name, student, student_id, subject, score, file_url, feedback, submit_time):
        # self.new_execute_write("REPLACE INTO raw_data (group_name, student, subject, score, file_url, "
        #                  "feedback, submit_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        #                  (group_name, student, subject, score, file_url, feedback, submit_time))
        # self.new_execute_write("UPDATE raw_data SET group_name = %s, student = %s, subject = %s, score = %s, "
        #                        "file_url = %s, feedback = %s, submit_time = %s WHERE student = %s AND subject = %s",
        #                        (group_name, student, subject, score, file_url, feedback, submit_time, student, subject))
#         sql_string = '''IF EXISTS (SELECT 1 FROM raw_data WHERE student = %s AND subject = %s)
# UPDATE raw_data SET group_name = %s, student = %s, subject = %s, score = %s, file_url = %s, feedback = %s, submit_time = %s
# ELSE
# INSERT INTO raw_data (group_name, student, subject, score, file_url, feedback, submit_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
# '''
#         sql_data = (student, subject,
#                     group_name, student, subject, score, file_url, feedback, submit_time,
#                     group_name, student, subject, score, file_url, feedback, submit_time)
#         self.new_execute_write(sql_string, sql_data)
        submit_time_date = time.localtime(submit_time).tm_mday
        data = self.new_execute_read("SELECT 1 FROM raw_data WHERE student = %s AND subject = %s AND submit_date = %s", (student, subject, submit_time_date))
        if len(data) != 0:
            self.new_execute_write("UPDATE raw_data SET group_name = %s, student = %s, subject = %s, score = %s, "
                                   "file_url = %s, feedback = %s, submit_time = %s, student_id = %s "
                                   "WHERE student = %s AND subject = %s AND submit_date = %s",
                                   (group_name, student, subject, score, file_url, feedback, submit_time, student,
                                    student_id, subject, submit_time_date))
        else:
            self.new_execute_write("INSERT INTO raw_data (group_name, student, subject, score, file_url, "
                             "feedback, submit_time, submit_date, student_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                             (group_name, student, subject, score, file_url, feedback, submit_time, submit_time_date, student_id))

    def get_raw_data(self, limit_str=''):
        sql_string = "SELECT group_name, student, student_id, subject, score, " \
                     "file_url, feedback, submit_time FROM raw_data"
        if limit_str != '':
            sql_string += ' WHERE %s' % limit_str
        data = self.new_execute_read(sql_string)
        return data

    def get_students_data(self):
        data = self.new_execute_read("SELECT id, name FROM student")
        return data

    def get_students_group(self, student_name: str):
        data = self.new_execute_read("SELECT group_name FROM raw_data WHERE student = %s", (student_name, ))
        return data

    def get_group_list(self):
        data = self.new_execute_read("SELECT group_name FROM raw_data")
        result = []
        for d in data:
            if d[0] not in result:
                result.append(d[0])
        return result

    def check_student_info(self, name: str, student_id: int):
        data = self.new_execute_read("SELECT 1 FROM student WHERE id = %s AND name = %s", (student_id, name))
        if len(data) == 0:
            # print(data)
            return False
        return True

    def parse_csv_data(self, csv_data: str):
        lines = csv_data.split('\n')
        results = []
        unit = [0, '']
        for line in lines:
            # print(line)
            if len(line) == 0 or ',' not in line:
                continue
            u = copy.deepcopy(unit)
            try:
                d1, d2 = line.split(',')
                try:
                    u[0] = int(float(d1))
                except ValueError:
                    u[0] = int(str(d1))
                u[1] = str(d2)
                u[1] = u[1].replace(' ', '').replace('\n', '').replace('\r', '')
                results.append(u)
            except ValueError:
                return None
        # print(results)
        return results

    def update_student_info(self, csv_data: str):
        data = self.parse_csv_data(csv_data)
        if data is None:
            return False
        self.new_execute_write("DELETE FROM student")
        # print(data)
        for line in data:
            self.new_execute_write("INSERT INTO student (id, name) VALUES (%s, %s)", (line[0], line[1]))
        return True


if __name__ == '__main__':
    db = DataBase()
    db.db_init()
    # with open('StudentID2.csv', 'r', encoding='gbk') as f:
    #     db.update_student_info(f.read())
    # print(db.get_students_data())
    # db.db_backup()

    # for i in range(10):
    #     db.new_submit('a', 'b', 'c', 100.5, '', '', int(time.time()))
    # db.new_submit('a', 'b', 'd', 10.5, '', '', int(time.time()))
    # print(db.get_raw_data())
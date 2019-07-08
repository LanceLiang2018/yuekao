import copy
import hashlib
import json
import os
import time


class DataBase:
    def __init__(self):
        self.file_db_init = "db_init.sql"

        self.tables = ['raw_data', ]

        # self.sql_type = "PostgreSQL"
        self.sql_types = {"SQLite": 0, "PostgreSQL": 1}
        # self.sql_type = self.sql_types['PostgreSQL']
        # self.sql_type = self.sql_types['SQLite']
        if os.environ.get('PORT', '5000') == '5000':
            # Local
            self.sql_type = self.sql_types['SQLite']
        else:
            # Remote
            self.sql_type = self.sql_types['PostgreSQL']
        self.sql_chars = ["?", "%s"]
        self.sql_char = self.sql_chars[self.sql_type]

        self.connect_init()

    def v(self, string: str):
        return string.replace('%s', self.sql_char)

    def new_execute_write(self, string: str, args=()):
        cursor = self.cursor_get()
        cursor.execute(self.v(string), args)
        self.cursor_finish(cursor)

    def new_execute_read(self, string: str, args=()):
        cursor = self.cursor_get()
        cursor.execute(self.v(string), args)
        data = cursor.fetch_all()
        self.cursor_finish(cursor)
        return data

    def connect_init(self):
        if self.sql_type == self.sql_types['SQLite']:
            import sqlite3 as sql
            self.conn = sql.connect('data_sql.db', check_same_thread=False)
        else:
            import psycopg2 as sql
            self.conn = sql.connect(host='ec2-23-21-160-38.compute-1.amazonaws.com',
                                    database='d6bagosv2bo9p8',
                                    user='dtzixfehvkttfq',
                                    port='5432',
                                    password='55e46bbde1772cb32715d4f52f51ad847ba3fe5af88902161336d56eb6c8a3c5')

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

    def new_submit(self, group_name, student, subject, score, file_url, feedback, submit_time):
        self.new_execute_write("INSERT INTO raw_data (group_name, student, subject, score, file_url, "
                         "feedback, submit_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                         (group_name, student, subject, score, file_url, feedback, submit_time))

    def get_raw_data(self):
        data = self.new_execute_read("SELECT ")


if __name__ == '__main__':
    db = DataBase()
    db.db_init()




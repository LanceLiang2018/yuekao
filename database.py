import json
import os
import time
import copy
from upload import *
from datetime import datetime
import requests
import pymongo


class DataBase:
    def __init__(self):
        self.file_db_init = "db_init.sql"

        self.tables = ['raw_data', 'student']

        self.hosts = ['127.0.0.1:5000', 'yuekao.herokuapp.com']
        if os.getenv('PORT', '5000') == '5000':
            self.host = self.hosts[0]
        else:
            self.host = self.hosts[1]

        self.sql_types = {"SQLite": 1, "MongoDB": 1}
        # Remote
        self.sql_type = self.sql_types['MongoDB']

        # self.max_retry = 5

        self.client = None
        self.db = None
        self.col = None
        self.stu = None

        # 原来建立的表结构
        '''
        CREATE TABLE raw_data (
            group_name VARCHAR(32),
            student VARCHAR(32),
            student_id INT,
            subject VARCHAR(32),
            score REAL,
            file_url VARCHAR(512),
            feedback VARCHAR(4096),
            submit_time INT,
            submit_date INT
        );
        
        CREATE TABLE student (
            id INT primary key,
            name VARCHAR(64)
        );'''
        self.tables_struct = {
            'raw_data': ['group_name', 'student', 'student_id', 'subject', 'score',
                         'file_url', 'feedback', 'submit_time', 'submit_date'],
            'student': ['id', 'name']
        }

        self.connect_init()

    def connect_init(self):
        self.client = pymongo.MongoClient("mongodb+srv://lanceliang:1352040930database@lanceliang-9kkx3.azure."
                                          "mongodb.net/test?retryWrites=true&w=majority")
        # self.client = pymongo.MongoClient()
        self.db = self.client.yuekao
        self.col = self.db.yuekao
        self.stu = self.db.students

    def db_init(self):
        collection_names = self.db.list_collection_names()
        if 'yuekao' in collection_names:
            self.db.drop_collection('yuekao')
        if 'students' in collection_names:
            self.db.drop_collection('students')
        self.col = self.db.yuekao
        self.stu = self.db.students
        # 只有在插入一个数据之后才会建立Collection
        # print(dict(self.col.find({})))
        # self.col.insert_one({'created': True})

    def db_backup(self):
        backup = {}
        for table in self.tables_struct:
            backup[table] = {}
            data = list(self.col.find({}, {'_id': 0}))
            backup[table]['labels'] = self.tables_struct[table]
            backup[table]['data'] = data

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
        submit_time_date = time.localtime(submit_time).tm_mday
        data = dict(self.col.find({'student': student, 'subject': subject, 'submit_date': submit_time_date}))
        if len(data) != 0:
            # 已经存在当天的数据
            self.col.update_one(
                {'sutdent': student, 'subject': subject, 'submit_date': submit_time_date},
                {"$set": {'group_name': group_name, 'student': student, 'subject': subject,
                          'score': score, 'file_url': file_url, 'feedback': feedback,
                          'submit_time': submit_time, 'student_id': student_id}}
            )
        else:
            # 当天数据不存在
            self.col.insert_one(
                {'group_name': group_name, 'student': student, 'subject': subject,
                 'score': score, 'file_url': file_url, 'feedback': feedback,
                 'submit_time': submit_time, 'submit_date': submit_time_date,
                 'student_id': student_id}
            )

    def get_raw_data(self, select=None, query=None):
        if select is None:
            select = {}
        if query is None:
            query = {}
        data = list(self.col.find(query, select))
        # data = dict(self.col.find({}, select))
        return data

    def get_students_data(self):
        data = list(self.stu.find({}, {'_id': 0}))
        return data

    def get_students_group(self, student_name: str):
        data = list(self.col.find({'student': student_name}, {'group_name': 1, '_id': 0}))
        return data

    def get_group_list(self):
        data = self.col.find({}, {'group_name': 1, '_id': 0})
        result = []
        for d in data:
            if 'group_name' not in d:
                continue
            if d['group_name'] not in result:
                result.append(d['group_name'])
        return result

    def check_student_info(self, name: str, student_id: int):
        data = list(self.stu.find({'id': student_id, 'name': name}))
        if len(data) == 0:
            # print(data)
            return False
        return True

    @staticmethod
    def parse_csv_data(csv_data: str):
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
        self.stu.drop()
        # print(data)
        for line in data:
            # self.new_execute_write("INSERT INTO student (id, name) VALUES (%s, %s)", (line[0], line[1]))
            self.stu.insert_one({'id': line[0], 'name': line[1]})
        return True


if __name__ == '__main__':
    db = DataBase()
    db.db_init()

    db.new_submit('梁鑫嵘', '梁鑫嵘', 170236, '语文', 100.0, 'https://github.com',
                  '', int(time.time()))
    db.new_submit('梁鑫嵘', '梁鑫嵘', 170236, '英语', 140.0, 'https://github.com',
                  '', int(time.time()))
    rdata = db.get_raw_data(select={'_id': 0}, query={})
    print(rdata)

    with open('StudentID2.csv', 'r', encoding='gbk') as f:
        db.update_student_info(f.read())
    print(db.get_students_data())
    db.db_backup()

    # for i in range(10):
    #     db.new_submit('a', 'b', 'c', 100.5, '', '', int(time.time()))
    # db.new_submit('a', 'b', 'd', 10.5, '', '', int(time.time()))
    # print(db.get_raw_data())

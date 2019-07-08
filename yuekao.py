from flask import *
from random import randint
import os
import time
import io
import hashlib
from datetime import datetime
import pytz
from upload import *
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, static_folder='tmp')


def captcha_get(string: str):
    empty = Image.new("RGB", (12, 12))
    font = ImageFont.truetype("segoeprb.ttf", 15)
    empty_draw = ImageDraw.Draw(empty)
    text_size = empty_draw.textsize(string, font=font)
    print(text_size)
    im = Image.new("RGB", text_size, color='white')
    draw = ImageDraw.Draw(im)
    draw.ink = 0
    draw.text((0, 0), string, font=font)
    return im


def generate_pass_port(limit=100):
    a = randint(0, limit)
    b = randint(0, limit)
    fun = [
        lambda x, y: x + y,
        lambda x, y: x - y,
    ]
    chars = '+-'
    p = randint(0, 1)
    s = '%d %s %d' % (a, chars[p], b)
    res = str(fun[p](a, b))
    return s, res


file_path = './files/'
g_debug = True


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        s, res = generate_pass_port()
        md5 = hashlib.md5()
        md5.update(res.encode())
        p = md5.hexdigest()
        # print('p=', p)
        captcha_get(s).save('tmp/%s.jpg' % p)
        return render_template('index.html', passport='/captcha/%s' % p, s=p)
    if request.method == 'POST':
        form = request.form
        if not g_debug:
            s = form['s']
            passport = form['passport']
            md5 = hashlib.md5()
            md5.update(passport.encode())
            p = md5.hexdigest()
            # print('in: passport=', passport, ' s=', s, ' p=', p)
            if p != s:
                return '验证码错误。'
        if 'file' not in request.files:
            return '没有选择文件。'
        file = request.files['file']
        if file.filename == '':
            return '没有选择文件。'
        filename = str(file.filename)
        file_type = filename.split('.')[-1]
        filedata = io.BytesIO()
        file.save(filedata)
        filedata.seek(0)
        # print(filedata)
        # file.save(os.path.abspath(os.path.join(file_path, filename)))

        timedata = time.localtime(time.time())
        cndata = datetime(timedata[0], timedata[1], timedata[2], timedata[3], timedata[4], timedata[5])
        central = pytz.timezone('Asia/Shanghai')
        time_cn = central.localize(cndata)
        # time_result = str(time_cn.year).zfill(4) + '/' + str(time_cn.month).zfill(2) + '/' + \
        #               str(time_cn.day).zfill(2) + ' ' + \
        #               str(time_cn.hour).zfill(2) + ':' + str(time_cn.minute).zfill(2),

        subject = form['subject']
        group_name = form['group_name']
        student_name = form['student_name']
        score = form['score']

        if group_name == '' or student_name == '' or subject == '' or score == '':
            return '表单填写错误，请重新填写。'

        time_date = str(time_cn.year).zfill(4) + '/' + str(time_cn.month).zfill(2) + '/' + str(time_cn.day).zfill(2)
        file_key = "%s/%s/%s/%s.%s" % (time_date, subject, group_name, student_name, file_type)
        print(file_key)
        upload_file_threaded(file_key, filedata)
        return '上传成功启动。请等待服务器CDN缓存(约30秒，视文件大小而定)'


@app.route('/captcha/<string:cid>')
def captcha_get_img(cid: str):
    # print(cid)
    return redirect(url_for('static',filename='%s.jpg' % cid))


if __name__ == '__main__':
    _li = os.listdir('tmp')
    for _i in _li:
        if _i != '.nomedia':
            os.remove('tmp/%s' % _i)
    app.run('0.0.0.0', port=os.getenv("PORT", "5000"), debug=True)
    # captcha_get("12 + 32").show()


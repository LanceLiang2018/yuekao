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
from database import DataBase
import textwrap

app = Flask(__name__, static_folder='tmp')
app.secret_key = 'LianGunJianPanDaChuLaiDeZiNiXInBuXin'
db = DataBase()
with open('loss.txt', 'r', encoding='utf8') as f:
    captcha_data = f.read().split('\n\n')
print(len(captcha_data))


def captcha_get(string: str):
    empty = Image.new("RGB", (12, 12))
    font_num = ImageFont.truetype("segoeprb.ttf", 120)
    empty_draw = ImageDraw.Draw(empty)
    text_size = empty_draw.textsize(string, font=font_num)
    # print(text_size)
    im = Image.new("RGB", text_size, color='white')
    draw = ImageDraw.Draw(im)
    draw.ink = 0
    draw.text((0, 0 - 32), string, font=font_num)

    # 加入椒盐噪声
    for i in range(500):
        draw.point((randint(0, im.size[0] - 1), randint(0, im.size[1] - 1)), fill='white')
        draw.point((randint(0, im.size[0] - 1), randint(0, im.size[1] - 1)), fill='black')

    # 加上斜线
    for i in range(30):
        rand = (randint(0, im.size[0] - 1), randint(0, im.size[1] - 1))
        rand2 = (randint(0, im.size[0] - 1), randint(0, im.size[1] - 1))
        colors = ['white', 'black']
        # print(rand)
        draw.line((rand[0] * 2 - rand[0] // 2, rand[1] * 2 - rand[1] // 2,
                   rand2[0] * 2 - rand2[0] // 2, rand2[1] * 2 - rand2[1] // 2),
                  fill=colors[randint(0, 1)], width=randint(1, 3))

    # 画上背景
    rand_index = randint(0, len(captcha_data)-1)
    loss = captcha_data[rand_index]
    height = 32
    width = im.size[0] // height
    para = textwrap.wrap(loss, width=width)
    font_char = ImageFont.truetype('FZLTCXHJW.TTF', height)
    for line in para:
        draw.text((0, para.index(line) * height), line, font=font_char)

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

        # 在主页删除角色状态
        if 'character' in session:
            session['character'] = None

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
        feedback = form['feedback']

        if group_name == '' or student_name == '' or subject == '' or score == '':
            return '表单填写错误，请重新填写。'

        time_date = str(time_cn.year).zfill(4) + '/' + str(time_cn.month).zfill(2) + '/' + str(time_cn.day).zfill(2)
        file_key = "%s/%s/%s/%s.%s" % (time_date, subject, group_name, student_name, file_type)
        file_url = get_upload_prefix() + file_key
        submit_time = int(time.time())
        # print(file_key)
        upload_file_threaded(file_key, filedata)

        db.new_submit(group_name, student_name, subject, score, file_url, feedback, submit_time)

        return '上传成功启动。请等待服务器CDN缓存(约30秒，视文件大小而定)'


@app.route('/data', methods=["GET", "POST"])
def show_data():
    form = request.form
    if request.method == 'GET':
        # 还没选择角色
        # if 'character' not in session:
        #     return render_template('character_choose.html')
        # character = session['character']
        # if character not in ['组长', '班长', '管理员']:
        #     session['character'] = None
        #     return redirect('/data')
        print(db.get_raw_data())
        return 'OK'
    if request.method == 'POST':
        # if 'password' in form and 'character' in form:
        #     password = form['password']
        #     character = form['character']
        #     if password == 'ltyz13579':
        #         session['character'] = character
        #         return '<a href="/data">返回上一页</a>'
        #     else:
        #         return '密码错误！ <a href="/data">返回上一页</a>'
        if 'password' in form:
            password = form['password']
            if password == 'ltyz13579':
                session['login'] = True
                return '<a href="/data">返回上一页</a>'
            else:
                return '密码错误！ <a href="/data">返回上一页</a>'
        return '提交错误！ <a href="/data">返回上一页</a>'


@app.route('/hello')
def hello():
    return render_template('data_show.html', labels=['A', 'B'], content=[[1, 2], [3, 4]])


@app.route('/captcha/<string:cid>')
def captcha_get_img(cid: str):
    # print(cid)
    return redirect(url_for('static', filename='%s.jpg' % cid))


@app.route('/res/<string:filename>')
def res(filename: str):
    return redirect(url_for('static', filename=filename))


@app.route('/mo_test')
def mo_test():
    return render_template('mo.html')


@app.route('/debug_clear')
def clear_all():
    db.db_init()
    return 'OK.'


@app.route('/favicon.ico')
def icon():
    return redirect('https://s.gravatar.com/avatar/544b5009873b27f5e0aa6dd8ffc1d3d8?s=144')


if __name__ == '__main__':
    _li = os.listdir('tmp')
    for _i in _li:
        # if _i != '.nomedia':
        if '.jpg' in _i:
            os.remove('tmp/%s' % _i)
    app.run('0.0.0.0', port=os.getenv("PORT", "5000"), debug=False)
    # captcha_get("12 + 32").show()


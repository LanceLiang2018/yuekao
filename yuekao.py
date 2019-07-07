from flask import *
from random import randint
import os
import io
import hashlib

app = Flask(__name__)


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
        print('p=', p)
        return render_template('index.html', passport=s, s=p)
    if request.method == 'POST':
        form = request.form
        if not g_debug:
            s = form['s']
            passport = form['passport']
            md5 = hashlib.md5()
            md5.update(passport.encode())
            p = md5.hexdigest()
            print('in: passport=', passport, ' s=', s, ' p=', p)
            if p != s:
                return '验证码错误。'
        if 'file' not in request.files:
            return '没有选择文件。'
        file = request.files['file']
        if file.filename == '':
            return '没有选择文件。'
        filename = file.filename
        filedata = io.BytesIO()
        file.save(filedata)
        print(filedata)
        # file.save(os.path.abspath(os.path.join(file_path, filename)))
        return '上传成功。'


if __name__ == '__main__':
    app.run('0.0.0.0', port=os.getenv("PORT", "5000"), debug=True)

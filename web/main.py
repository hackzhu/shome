from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import os
import IPy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp/upload'
app.config['TMP_FOLDER'] = 'tmp'

## 创建所需目录
if not os.path.exists('tmp/upload'):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    os.mkdir('tmp/upload')
if not os.path.exists('tmp/userhost'):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    os.system('touch tmp/userhost')

## 检测ip合法性
def checkip(address):
    try:
        version = IPy.IP(address).version()
        if version == 4 or version == 6:
            return True
        else:
            return False
    except Exception as e:
        return False


@app.route('/')
def index():
    with open('tmp/userhost') as hf:
        user_host = hf.read().splitlines()
    context = {
        "userhost": user_host
    }
    return render_template('index.html', **context)


# BUG 中文文件名
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        print(request.files)
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return 'file uploaded successlly'
    else:
        return render_template('index.html')


@app.route('/userhost', methods=['GET', 'POST'])
def hostip():
    if request.method == 'POST':
        hosts = request.form['host'].splitlines()
        userhost = []
        for h in hosts:
            if checkip(h) == True:
                userhost.append(h)
        return userhost


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp/upload'
app.config['TMP_FOLDER'] = 'tmp'

if not os.path.exists('tmp/upload'):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    os.mkdir('tmp/upload')
if not os.path.exists('tmp/userhost'):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    os.system('touch tmp/userhost')


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
def hostname():
    if request.method == 'POST':
        hosts = request.form['host']
        # for h in hosts:

        return 'host file uploaded successlly'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

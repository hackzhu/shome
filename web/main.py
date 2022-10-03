from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'web/upload/'


if not os.path.exists('web/upload'):
    os.mkdir('web/upload')

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        print(request.files)
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

        return 'file uploaded successfully'

    else:

        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

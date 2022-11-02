from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
# from camera import VideoCamera
from pypinyin import lazy_pinyin

import os
import IPy
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp/upload'
app.config['TMP_FOLDER'] = 'tmp'

# 创建所需目录
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    if not os.path.exists(app.config['TMP_FOLDER']):
        os.mkdir(app.config['TMP_FOLDER'])
    os.mkdir(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['TMP_FOLDER']+'/userhost'):
    if not os.path.exists(app.config['TMP_FOLDER']):
        os.mkdir(app.config['TMP_FOLDER'])
    os.system('touch ' + app.config['TMP_FOLDER'] + '/userhost')


# 检测ip合法性
def checkip(address):
    try:
        version = IPy.IP(address).version()
        if version == 4 or version == 6:
            return True
        else:
            return False
    except Exception as e:
        return False


# 视频推流
def video_push():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        detector = cv2.CascadeClassifier(
            'opencv/haarcascade_frontalface_default.xml')
        faces = detector.detectMultiScale(frame, 1.2, 6)
        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    with open(app.config['TMP_FOLDER']+'/userhost') as hf:
        user_host = hf.read().splitlines()
    context = {
        "userhost": user_host
    }
    return render_template('index.html', **context)


@app.route('/video_pull')
def video_pull():
    return Response(video_push(), mimetype='multipart/x-mixed-replace; boundary=frame')


#! 中文转拼音上传
@app.route('/uploader', methods=['POST'])
def uploader():
    f = request.files['file']
    print(request.files)
    f.save(os.path.join(
        app.config['UPLOAD_FOLDER'], secure_filename(''.join(lazy_pinyin(f.filename)))))
    return '上传成功'


@app.route('/userhost', methods=['POST'])
def hostip():
    hosts = request.form['host'].splitlines()
    userhost = []
    for h in hosts:
        if checkip(h) == True:
            userhost.append(h)
    return userhost


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

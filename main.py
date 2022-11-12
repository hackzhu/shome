#!/usr/bin/env python

from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin

import os
import cv2
import init

app = Flask(__name__)

cvfont = cv2.FONT_HERSHEY_SIMPLEX
config = init.config_read()


# 视频推流
def video_push():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        detector = cv2.CascadeClassifier(
            'haarcascades/haarcascade_frontalface_default.xml')
        faces = detector.detectMultiScale(frame, 1.2, 6)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(frame, 'test text', (x + 5, y - 5),
                        cvfont, 1, (255, 255, 255), 2)
            cv2.putText(frame, '50%', (x + 5, y + h - 5),
                        cvfont, 1, (255, 255, 0), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# @app.before_request
# def at_home():
#     global config
#     for ui in config['userip']:
#         ping = os.system("ping -c 1 -W 500 " + ui + " >/dev/null 2>&1")
#         if ping == 0:
#             break
#         else:
#             ping = 1
#     with open(init.configfile, 'w', encoding='utf8') as ah:
#         if ping == 0:
#             config['athome'] = '1'
#         else:
#             config['athome'] = '1'
#     init.config_update(config)
#     return None


@app.route('/')
def index():
    context = {
        "userip": config['userip'],
        "athome": config['athome']
    }
    return render_template('index.html', **context)


@app.route('/userip_update', methods=['POST'])
def user_ip():
    global config
    userips = request.form['userips'].splitlines()
    userips = list(set(userips))  # 去重但乱
    config['userip'].clear()
    for h in userips:
        if init.check_ip(h) == True:
            config['userip'].append(h)
    init.config_update(config)
    return index()


# BUG 中文无法安全上传
# 现使用中文转拼音上传
# 后续可能从secure_filename源码处修改
# opencv putText的中文问题该解决
@app.route('/face_upload', methods=['POST'])
def face_upload():
    f = request.files['file']
    print(request.files)
    f.save(os.path.join(
        init.facedir, secure_filename(''.join(lazy_pinyin(f.filename)))))
    return index()


@app.route('/video_pull')
def video_pull():
    return Response(video_push(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

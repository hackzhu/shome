#!/usr/bin/env python

from flask import Flask, render_template, request, Response

import os
import IPy
import cv2

app = Flask(__name__)
app.config['TMP'] = 'tmp/'

# camera = cv2.VideoCapture('rtsp://localhost:8554/cam') # 网络摄像头

try:
    os.makedirs(app.config['TMP'] + 'faces/')
except OSError as error:
    pass
try:
    os.mknod(app.config['TMP'] + 'userip')
except OSError as error:
    pass


with open(app.config['TMP'] + '/userip') as hi:
    userip = hi.read().splitlines()


def check_ip(address):
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
        success, frame = camera.read()
        detector = cv2.CascadeClassifier(
            'haarcascades/haarcascade_frontalface_default.xml')
        faces = detector.detectMultiScale(frame, 1.2, 6)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    context = {
        "userip": userip
    }
    return render_template('index.html', **context)


@app.route('/', methods=['POST'])
def user_ip():
    global userip
    hostips = request.form['hostip'].splitlines()
    hostips = list(set(hostips))  # 去重
    useripfile = open(app.config['TMP'] + '/userip', "w")
    userip.clear()
    for h in hostips:
        if check_ip(h) == True:
            userip.append(h)
            useripfile.write(h+'\n')
    useripfile.close()
    return index()


@app.route('/video_pull')
def video_pull():
    return Response(video_push(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

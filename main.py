#!/usr/bin/env python

from flask import Flask, render_template, request, Response
from pathlib import Path

import os
import IPy
import cv2
import json
import paho.mqtt.client as mqttclient

app = Flask(__name__)

tmpdir = os.path.join(os.getcwd(), 'tmp')
useripfile = os.path.join(tmpdir, 'userip')
athomefile = os.path.join(tmpdir, 'athome')
mqtthost = "home.hackzhu.com"
mqttport = 1883
cvfont = cv2.FONT_HERSHEY_SIMPLEX

try:
    os.mkdir(tmpdir)
except OSError as error:
    pass
try:
    os.mknod(useripfile)
except OSError:
    pass
try:
    os.mknod(useripfile)
except OSError:
    print()
try:
    os.mknod(athomefile)
    with open(athomefile, 'w') as ah:
        ah.write('0')
except OSError:
    pass


with open(useripfile, 'r') as ui:
    userip = ui.read().splitlines()


def check_ip(address):
    try:
        version = IPy.IP(address).version()
        if version == 4 or version == 6:
            return True
        else:
            return False
    except Exception as e:
        return False


def mqtt_pub(payload="payload", topic="mqtt", qos=0):
    mclient = mqttclient.Client()
    mclient.connect(mqtthost, mqttport, 60)
    mclient.publish('homeassistant/' + topic, payload, qos)


def at_home():
    for ui in userip:
        ping = os.system("ping -c 1 -W 500 " + ui + " >/dev/null 2>&1")
        if ping == 0:
            break
        else:
            ping = 1
    with open(athomefile, 'w', encoding='utf8') as ah:
        if ping == 0:
            mqtt_pub('1', "athome", 0)
            ah.write('1')
            return 1
        else:
            mqtt_pub('0', "athome", 0)
            ah.write('0')
            return 0


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


@app.route('/')
def index():
    context = {
        "userip": userip
    }
    return render_template('index.html', **context)


@app.route('/', methods=['POST'])
def user_ip():
    global userip
    userips = request.form['userips'].splitlines()
    userips = list(set(userips))  # 去重
    userip.clear()
    with open(useripfile, 'w', encoding='utf8') as ui:
        for h in userips:
            if check_ip(h) == True:
                userip.append(h)
                ui.write(h+'\n')
    return index()


@app.route('/video_pull')
def video_pull():
    return Response(video_push(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
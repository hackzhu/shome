#!/usr/bin/env python

from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
from xiaoai import *

import os
import cv2
import init
import requests

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


def xiaoai_output(toSpeakText, is_session_end, openMic=True):
    xiaoAIResponse = XiaoAIResponse(to_speak=XiaoAIToSpeak(
        type_=0, text=toSpeakText), open_mic=openMic)
    response = xiaoai_response(XiaoAIOpenResponse(version="1.0",
                                                  is_session_end=is_session_end,
                                                  response=xiaoAIResponse))
    return response


def xiaoai_input(event):
    req = xiaoai_request(event)
    if req.request.type == 0:
        return '0'
    elif req.requests.type == 1:
        return '1'
    else:
        return '2'


@app.route('/')
def index():
    context = {
        "userip": config['userip'],
        "athome": config['athome']
    }
    return render_template('index.html', **context)


@app.route('/xiaoai', methods=['POST'])
def xiaoai():
    response = xiaoai_input(request.json)
    return response


@app.route('/userip_update', methods=['POST'])
def user_ip():
    userips = request.form['userips'].splitlines()
    userips = list(set(userips))  # 去重但乱
    config['userip'].clear()
    for h in userips:
        if init.check_ip(h) is True:
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

# BUG 无法使用摄像头
@app.route('/ddns', methods=['POST'])
def ddnspod():
    newip = r"2001:0250:3401:6000:0000:0000:30c6:ceb7"
    token = r"336294,4da657cefe9db0f9ee4e882cf9a8986a"
    subdomain = "home"
    domain = "hackzhu.com"
    recordtype = "AAAA"
    listurl = r"https://dnsapi.cn/Record.List"
    ddnsurl = r"https://dnsapi.cn/Record.Ddns"
    headers = {'User-Agent': r'hackddns/1.0.0(3110497917@qq.com)'}
    data = {
        'login_token': token,
        'format': 'json',
        'domain': domain,
        'sub_domain': subdomain
    }
    list = requests.post(url=listurl, headers=headers, data=data).text
    lists = json.loads(list)
    recordid = lists['records'][0]['id']
    oldip = lists['records'][0]['value']
    if newip != oldip:
        ddnsdata = {
            'login_token': token,
            'format': 'json',
            'domain': domain,
            'sub_domain': subdomain,
            'record_id': recordid,
            'record_type': recordtype,
            'value': newip,
            'record_line_id': '0'
        }
        requests.post(url=ddnsurl, headers=headers, data=ddnsdata)
        config['ip'] = newip
        init.config_update(config)
    return index()


if __name__ == '__main__':
    print('https://home.hackzhu.com:8443')
    app.run(host='0.0.0.0', port=8443, debug=True, ssl_context=(
        'ssl_certs/home.hackzhu.com_bundle.pem', 'ssl_certs/home.hackzhu.com.key'))

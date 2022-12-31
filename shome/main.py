#!/usr/bin/env python

import os
import cv2
import init
import json

from flask import Flask, render_template, request, Response
from flask_mqtt import Mqtt
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
# from xiaoai import *  # 小爱同学不支持IPv6

app = Flask(__name__)
# app.config['MQTT_CLIENT_ID'] = '' #默认随机
app.config['MQTT_BROKER_URL'] = r'127.0.0.1'
# app.config['MQTT_BROKER_URL'] = 'home.hackzhu.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_PASSWORD'] = ''  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_KEEPALIVE'] = 5  # 设置心跳时间，单位为秒
app.config['MQTT_TLS_ENABLED'] = False  # 如果你的服务器支持 TLS，请设置为 True
mqtttopic = 'dev/+'
mqttclient = Mqtt(app)
cvfont = cv2.FONT_HERSHEY_SIMPLEX
config = init.config_read()


@mqttclient.on_connect()
def mqtt_connect(client, userdata, flags, rc) -> None:
    if rc == 0:
        print('Connected successfully')  # BUG 无输出，可能是多线程的问题
        mqttclient.publish(topic=init.configtopic, payload='online')
        mqttclient.subscribe(mqtttopic)
    else:
        print('Bad connection. Code:', rc)


@mqttclient.on_message()
def mqtt_callback(client, userdata, message) -> None:
    try:
        # ! mosqutto_pub 要用单引号括着内容，内容里要用双引号'{"light":"on"}'
        payload = message.payload.decode()
        topic = message.topic
        if payload == 'online':
            config['device'][topic.split(r'/', 1)[1]] = 1
            init.config_update(config)
            return None
        elif payload == 'offline':
            config['device'][topic.split(r'/', 1)[1]] = 0
            init.config_update(config)
            return None
        elif payload == 'delete':
            del config['device'][topic.split(r'/', 1)[1]]
            init.config_update(config)
            return None
        elif payload == 'test':
            print(topic+':test')
            return None
        payloadjson = json.loads(payload)
        if payloadjson['test'] == 'testext':
            print('test successfully')
            return None
        return None
    except KeyError:
        print('Key Error')
        return None
    except:
        print('Other Error')
        return None


# 视频推流
def video_push():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if success:
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
        else:
            pass


'''
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
'''


@app.route('/')
def index():
    context = {
        'userip': config.get('userip'),
        'athome': config.get('athome'),
        'ddnsip': config.get('ddnsip'),
        'device': config.get('device')
    }
    return render_template('index.html', **context)


'''
@app.route('/xiaoai', methods=['POST'])
def xiaoai():
    response = xiaoai_input(request.json)
    return response
'''


@app.route('/userip_update', methods=['POST', 'GET'])
def user_ip():
    if request.method == 'POST':
        userips = request.form['userips'].splitlines()
        userips = list(set(userips))  # 去重但顺序乱
        config['userip'].clear()
        for h in userips:
            if init.check_ip(h) is True:
                config['userip'].append(h)
        init.config_update(config)
        return index()
    else:
        return index()


# TODO 自动获取ip
@app.route('/ddns', methods=['POST', 'GET'])
def ddns():
    if request.method == 'POST':
        ddnsip = request.form['ddnsips']
        if ddnsip == '':
            ddnsip = None
        # ddnsip = r'2001:0250:3401:6000:0000:0000:30c6:ceb7'
        if init.check_ip(ddnsip) is True or ddnsip is None:
            ddnsip = init.ddnspod(ddnsip)
            if config['ddnsip'] != ddnsip:
                config['ddnsip'] = ddnsip
                init.config_update(config)
        return index()
    else:
        return index()


# BUG 中文无法安全上传
# 现使用中文转拼音上传
# 后续可能从secure_filename源码处修改
# opencv putText的中文问题该解决
@app.route('/face_upload', methods=['POST', 'GET'])
def face_upload():
    if request.method == 'POST':
        f = request.files['file']
        print(request.files)
        f.save(os.path.join(
            init.tmpdir, secure_filename(''.join(lazy_pinyin(f.filename)))))
        return index()
    else:
        return index()


@app.route('/mqtt_publish', methods=['POST', 'GET'])
def mqtt_publish():
    try:
        if request.method == 'POST':
            device = request.form['devices'].splitlines()
            devs = dict()
            config['device'].clear()
            for d in device:
                dev = d.split(r':', 1)
                if dev[0] == '':
                    break
                if dev[1] == '':
                    dev[1] == 0
                dev[1] = int(dev[1])
                if dev[1] == 0:
                    break
                else:
                    dev[1] = 1
                devs[dev[0]] = dev[1]
                print(devs)
            config['device'] = devs
            init.config_update(config)
            return index()
        else:
            return index()
    except:
        config = init.config_read()
        return index()


@app.route('/video_pull')
def video_pull():
    return Response(video_push(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# TODO 改换nginx
def main():
    # print('https://home.hackzhu.com:8443')
    # app.run(host='0.0.0.0', port=8443, debug=False, ssl_context=(
    # 'nginx/ssl_certs/home.hackzhu.com_bundle.pem', 'nginx/ssl_certs/home.hackzhu.com.key'))
    app.run(host='0.0.0.0', port=8443, debug=False)  # debug=True时，mqtt会回调两次


if __name__ == '__main__':
    main()

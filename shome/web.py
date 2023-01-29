#!/usr/bin/env python

import os
import cv2
import json
import func
import logging

from config import Config
from flask import Flask, render_template, request, Response, redirect, url_for
from flask_mqtt import Mqtt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
# from xiaoai import *  # 小爱同学不支持IPv6

tmpdir = os.path.join(os.getcwd(), 'tmp')
try:
    os.mkdir(tmpdir)
except OSError:
    pass
logfile = os.path.join(tmpdir, 'shome.log')
try:
    os.mknod(logfile)
except OSError:
    pass

config = Config()
app = Flask(__name__)
# app.config['MQTT_CLIENT_ID'] = '' #默认随机
app.config['MQTT_BROKER_URL'] = config.config['mqtt']['brober']
app.config['MQTT_BROKER_PORT'] = config.config['mqtt']['port']
app.config['MQTT_USERNAME'] = config.config['mqtt']['username']
app.config['MQTT_PASSWORD'] = config.config['mqtt']['password']
app.config['MQTT_KEEPALIVE'] = config.config['mqtt']['keepalive']  # 设置心跳时间，单位为秒
# 如果你的服务器支持 TLS，请设置为 True
app.config['MQTT_TLS_ENABLED'] = config.config['mqtt']['tls']
try:
    mqttclient = Mqtt(app)
except:
    pass
app.config['SECRET_KEY'] = 'abc'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # /login
logformat = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
loghandler = logging.FileHandler(logfile, encoding='UTF-8')
loghandler.setLevel(logging.DEBUG)
loghandler.setFormatter(logformat)
app.logger.addHandler(loghandler)
cvfont = cv2.FONT_HERSHEY_SIMPLEX

try:
    @mqttclient.on_connect()
    def mqtt_connect(client, userdata, flags, rc) -> None:
        try:
            if rc == 0:
                print('mqtt connected')
                mqttclient.publish(
                    topic=config.config['mqtt']['pubtopic'], payload='online')
                mqttclient.subscribe(config.config['mqtt']['subtopic'])
            else:
                print('bad connection with code:', rc)
        except:
            print('mqtt connection error')

    @mqttclient.on_message()
    def mqtt_callback(client, userdata, message) -> None:
        try:
            # ! mosqutto_pub 要用单引号括着内容，内容里要用双引号'{"light":"on"}'
            payload = message.payload.decode()
            topic = message.topic
            if payload == 'online':
                config.config['mqtt']['payload'][topic.split('/', 1)[1]] = 1
                config.update()
                return None
            elif payload == 'offline':
                config.config['mqtt']['payload'][topic.split('/', 1)[1]] = 0
                config.update()
                return None
            elif payload == 'delete':
                del config.config['mqtt']['payload'][topic.split('/', 1)[1]]
                config.update()
                return None
            elif payload == 'test':
                print(topic+':test')
                return None
            payloadjson = json.loads(payload)
            if payloadjson['test'] == 1:
                print('test successfully')
                return None
            return None
        except KeyError:
            print('key error')
            return None
        except:
            print('mqtt callback error')
            return None
except NameError:
    pass


class LoginForm(FlaskForm):
    username = StringField('用户', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])


class User(UserMixin):
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    @staticmethod
    def get(userid):
        if not userid:
            return None
        for user in config.config['users']:
            if user.get('id') == userid:
                return User(user)
        return None


def get_user(username):
    for user in config.config['users']:
        if user.get("name") == username:
            return user
    return None


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


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
@login_required  # 需要登录才能访问
def index():
    context = {
        'userip': config.config['athome']['ip'],
        'athome': config.config['athome']['status'],
        'ddnsip': config.config['ddns']['ip'],
        'device': config.config['mqtt']['payload'],
        'username': current_user.username
    }
    return render_template('index.html', **context)


@app.route('/login', methods=('GET', 'POST'))  # 登录
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_info = get_user(username)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
            app.logger.error('login false with ' + username + ' ' + password)
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get('next') or url_for('index'))
            else:
                emsg = "用户名或密码密码有误"
                app.logger.error('login false with ' + username + ' ' + password)
    return render_template('login.html', form=form, emsg=emsg)


@app.route('/logout')  # 登出
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


'''
@app.route('/xiaoai', methods=['POST'])
def xiaoai():
    response = xiaoai_input(request.json)
    return response
'''


@app.route('/userip_update', methods=['POST', 'GET'])
@login_required
def user_ip():
    try:
        if request.method == 'POST':
            userips = request.form['userips'].splitlines()
            userips = list(set(userips))  # 去重但顺序乱
            config.config['athome']['ip'].clear()
            for h in userips:
                if func.check_ip(h) is True:
                    config.config['athome']['ip'].append(h)
            config.update()
            app.logger.warning('userip config update')
            return index()
        else:
            return index()
    except:
        return index()


# TODO 多方式自动获取ip
@app.route('/ddns', methods=['POST', 'GET'])
@login_required
def ddns():
    try:
        if request.method == 'POST':
            ddnsip = request.form['ddnsips']
            if ddnsip == '' or func.check_ip(ddnsip) is False:
                ddnsip = None
            # ddnsip = '2001:0250:3401:6000:0000:0000:30c6:ceb7'
            ddnsip = func.ddnspod(ddnsip)
            if config.config['ddns']['ip'] != ddnsip:
                config.config['ddns']['ip'] = ddnsip
                config.update()
                app.logger.warning('ddnsip config update')
            return index()
        else:
            return index()
    except:
        return index()


# BUG 中文无法安全上传
# 现使用中文转拼音上传
# 后续可能从secure_filename源码处修改
# opencv putText的中文问题该解决
@app.route('/face_upload', methods=['POST', 'GET'])
@login_required
def face_upload():
    try:
        if request.method == 'POST':
            f = request.files['file']
            print(request.files)
            f.save(os.path.join(
                'tmp', secure_filename(''.join(lazy_pinyin(f.filename)))))
            return index()
        else:
            return index()
    except:
        return index()


@app.route('/device_update', methods=['POST', 'GET'])
@login_required
def device_update():
    try:
        if request.method == 'POST':
            device = request.form['devices'].splitlines()
            devs = dict()
            for d in device:
                if ':' in d:
                    dev = d.split(':', 1)
                    if dev[0] == '':
                        break
                    if dev[1] == '':
                        dev[1] == 0
                    try:
                        dev[1] = int(dev[1])
                    except ValueError:
                        dev[1] = 0
                    if dev[1] > 0:
                        dev[1] = 1
                    else:
                        dev[1] = 0
                    devs[dev[0]] = dev[1]
                else:
                    devs[dev[0]] = 0
            config.config['mqtt']['payload'] = devs
            config.update()
            app.logger.warning('device config update')
            # TODO 具体到什么设备
            return index()
        else:
            return index()
    except:
        return index()


@app.route('/video_pull')
@login_required
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

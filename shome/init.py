#!/usr/bin/env python

import json
import os

import paho.mqtt.publish as mqttpublish
from werkzeug.security import generate_password_hash

tmpdir = os.path.join(os.getcwd(), 'tmp')
configfile = os.path.join(tmpdir, 'config.json')
initdata = {
    'userip': ['127.0.0.1', '::1'],
    'athome': 0,
    'ddnsip': '::1',
    'device': {
        'esp0': 0,
        'esp1': 0
        # 可直接通过mqtt发送'online'和'offline'至'dev/{设备名}'主题实现添加，发送'delete'则删除
        # 也可通过网页更改
        # TODO 命名有待商榷
    },
    'test': 'testext'
}
initconfig = {
    "mqtt": {
        "brober": "localhost",
        "port": 1883,
        "username": "",
        "password": "",
        "keepalive": 5,
        "tls": False,
        "pubtopic": "etc/config",
        "subtopic": "dev/+",
        "payload": {
            "esp0": 0,
            "esp1": 0,
            "light0": 0,
            "test": "testext"
            # 可直接通过mqtt发送"online"和"offline"至"dev/{设备名}"主题实现添加，发送"delete"则删除
            # 也可通过网页更改
            # TODO 命名有待商榷
        }
    },
    "athome": {
        "status": 1,
        "ip": ["127.0.0.1", "::1"]
    },
    "ddns": {
        "domain": "home.hackzhu.com",
        "token": "336294,4da657cefe9db0f9ee4e882cf9a8986a",
        "ip": "::1"
    },
    "mail": {
        "server": "smtp.qq.com",
        "user": "3110497917",
        "password": "xjdgrnzdmauidfea",
        "sender": "3110497917@qq.com",
        "receivers": ["zhu@hackzhu.com"]
    },
    "users": [
        {
            "id": 1,
            "name": "li",
            "password": generate_password_hash("123")
        },
        {
            "id": 2,
            "name": "tom",
            "password": generate_password_hash("123")
        }
    ]
}


def mkfile() -> None:
    try:
        os.mkdir(tmpdir)
    except OSError:
        pass
    try:
        os.mknod(configfile)
        with open(configfile, 'w') as cf:
            json.dump(obj=initconfig, fp=cf, indent=4)
    except OSError:
        pass


def config_read() -> dict:
    try:
        with open(configfile, 'r') as cf:
            data = json.load(cf)
        return data
    except:
        return initdata


def config_check(data) -> bool:
    try:
        if isinstance(data, dict) is False:
            return False
        # if isinstance(data['device'], dict) is False:
        #     return False
        return True
    except:
        return False


def config_update(data) -> None:
    try:
        if config_check(data):
            with open(configfile, 'w') as cf:
                json.dump(obj=data, fp=cf, indent=4)
            payload = json.dumps(obj=data)
            config = config_read()
            mqttpublish.single(config['mqtt']['pubtopic'], payload, qos=0, retain=True,
                               hostname=config['mqtt']['brober'], port=config['mqtt']['port'])
        else:
            print('config update undone')
    except:
        print('error')


def main():
    pass


if __name__ == '__main__':
    main()

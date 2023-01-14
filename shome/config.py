#!/usr/bin/env python

import json
import os

import paho.mqtt.publish as mqttpublish
from werkzeug.security import generate_password_hash


class Config(object):
    tmpdir = os.path.join(os.getcwd(), 'tmp')
    configfile = os.path.join(tmpdir, 'config.json')
    config = dict()
    configinit = {
        "init": True,
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

    def __init__(self) -> None:
        try:
            os.mkdir(self.tmpdir)
        except OSError:
            pass
        try:
            os.mknod(self.configfile)
            self.write(config=self.configinit)
            self.config = self.configinit
        except OSError:
            self.read()

    def write(self, config) -> None:
        try:
            with open(self.configfile, 'w') as cf:
                json.dump(obj=config, fp=cf, indent=4)
        except:
            pass

    def read(self) -> None:
        try:
            with open(self.configfile, 'r') as cf:
                self.config = json.load(cf)
        except:
            self.config = dict()

    def check(self) -> bool:
        try:
            if isinstance(self.config, dict) is False:
                return False
            # if isinstance(data['device'], dict) is False:
            # return False
            return True
        except:
            return False

    def update(self) -> None:
        try:
            if self.check():
                if self.config['init'] is True:
                    self.config['init'] = False
                self.write(config=self.config)
                payload = json.dumps(obj=self.config)
                mqttpublish.single(self.config['mqtt']['pubtopic'], payload, qos=0, retain=True,
                                   hostname=self.config['mqtt']['brober'], port=self.config['mqtt']['port'])
            else:
                print('config update undone')
        except:
            print('config update error')


def main():
    config = Config()
    print(config.config)


if __name__ == '__main__':
    main()

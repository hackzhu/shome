#!/usr/bin/env python

import json
import os
import IPy
import requests
import re

import paho.mqtt.publish as mqttpublish

tmpdir = os.path.join(os.getcwd(), 'tmp')
configfile = os.path.join(tmpdir, 'config.json')
# mqttbroker = "home.hackzhu.com"
mqttbroker = "127.0.0.1"
mqttport = 1883
configtopic = 'etc/config'
ddnsdomain = 'home.hackzhu.com'
ddnstoken = '336294,4da657cefe9db0f9ee4e882cf9a8986a'
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

try:
    os.mkdir(tmpdir)
except OSError:
    pass
try:
    os.mknod(configfile)
    with open(configfile, 'w') as cf:
        json.dump(obj=initdata, fp=cf, indent=4)
except OSError:
    pass


def check_ip(ip) -> bool:
    try:
        version = IPy.IP(ip).version()
        if version == 4 or version == 6:
            return True
        else:
            return False
    except:
        return False


def get_ip(strict=0) -> str:
    try:
        res = requests.get('http://ip6only.me')
        ip = re.search(r'\+3>(.*?)</', res.content.decode('utf-8')).group(1)
        if check_ip(ip):
            if strict == 1:
                if ping(ip) is False:
                    raise ConnectionError
            return ip
        else:
            raise ConnectionError
    except ConnectionError:
        return '::1'


def ping(ip=None, domain=None) -> bool:
    if domain == None:
        version = IPy.IP(ip).version()
        response = os.system("ping -c 1 -W 500 -" +
                            str(version) + ' ' + ip + " >/dev/null 2>&1")
    else:
        response = os.system("ping -c 1 -W 500 " + domain + " >/dev/null 2>&1")
    if response == 0:
        return True
    return False


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
        if isinstance(data['device'], dict) is False:
            return False
        return True
    except:
        return False


def config_update(data) -> None:
    if config_check(data):
        with open(configfile, 'w') as cf:
            json.dump(obj=data, fp=cf, indent=4)
        payload = json.dumps(obj=data)
        mqttpublish.single(configtopic, payload, qos=0, retain=True,
                           hostname=mqttbroker, port=mqttport)
    else:
        print('config update undone')


# TODO 寻找更适合的方法
def at_home():
    config = config_read()
    for ui in config['userip']:
        pingstatus = ping(ui)
        if pingstatus is True:
            config['athome'] = 1
            break
        else:
            config['athome'] = 0
    config_update(config)
    return config['athome']


def ddnspod(ip=None) -> str:
    if ip is None:
        ip = get_ip()
    subdomain, domain = ddnsdomain.split('.', 1)
    ipversion = IPy.IP(ip).version()
    if ipversion == 4:
        recordtype = "A"
    else:
        recordtype = "AAAA"
    listurl = r"https://dnsapi.cn/Record.List"
    ddnsurl = r"https://dnsapi.cn/Record.Ddns"
    headers = {'User-Agent': r'hackddns/1.0.0(3110497917@qq.com)'}
    data = {
        'login_token': ddnstoken,
        'format': 'json',
        'domain': domain,
        'sub_domain': subdomain
    }
    list = requests.post(url=listurl, headers=headers, data=data).text
    list = json.loads(list)
    recordid = list['records'][0]['id']
    oldip = list['records'][0]['value']
    if ip != oldip:
        ddnsdata = {
            'login_token': ddnstoken,
            'format': 'json',
            'domain': domain,
            'sub_domain': subdomain,
            'record_id': recordid,
            'record_type': recordtype,
            'value': ip,
            'record_line_id': '0'
        }
        requests.post(url=ddnsurl, headers=headers, data=ddnsdata)
    return ip


# 用以测试
def main():
    # print(get_ip())
    try:
        if ping(domain='baidu.com'):
            print('q')
    except ConnectionError:
        print('0')


if __name__ == '__main__':
    main()

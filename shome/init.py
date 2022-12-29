import json
import os
import IPy
import requests

import paho.mqtt.publish as mqttpublish

tmpdir = os.path.join(os.getcwd(), 'tmp')
configfile = os.path.join(tmpdir, 'config.json')
mqttbroker = r"home.hackzhu.com"
mqttport = 1883
configtopic = r'etc/config'
ddnsdomain = r'home.hackzhu.com'
ddnstoken = r"336294,4da657cefe9db0f9ee4e882cf9a8986a"

try:
    os.mkdir(tmpdir)
except OSError:
    pass
try:
    os.mknod(configfile)
    initdata = {
        'userip': ['127.0.0.1', '::1'],
        'athome': 0,
        'ddnsip': r'2001:0250:3401:6000:0000:0000:30c6:ceb7',
        'device':{
                'esp0': 0,
                'esp1': 0
                #可直接通过mqtt发送'online'和'offline'至'dev/{设备名}'主题实现添加，发送'delete'则删除
        },
        'test': 'testext'
    }
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
    except Exception:
        return False


def ping(ip) -> bool:
    version = IPy.IP(ip).version()
    response = os.system("ping -c 1 -W 500 -" +
                         str(version) + ' ' + ip + " >/dev/null 2>&1")
    if response == 0:
        return True
    return False


def config_read() -> dict:
    with open(configfile, 'r') as cf:
        data = json.load(cf)
    return data


def config_update(data) -> None:
    with open(configfile, 'w') as cf:
        json.dump(obj=data, fp=cf, indent=4)
    payload = json.dumps(obj=data)
    mqttpublish.single(configtopic, payload, qos=0, retain=True,
                       hostname=mqttbroker, port=mqttport)


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


def ddnspod(ip=None) -> int:
    if ip != None:
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
            return 1
        else:
            return 2
    else:
        return 0


# 用以测试
def main():
    pass


if __name__ == '__main__':
    main()
import json
import os
import IPy

import paho.mqtt.publish as mqttpublish

tmpdir = os.path.join(os.getcwd(), 'tmp')
facedir = os.path.join(tmpdir, 'face')
configfile = os.path.join(tmpdir, 'config.json')
mqtthost = "home.hackzhu.com"
mqttport = 1883
configtopic = 'homeassistant/config'

try:
    os.makedirs(facedir)
except OSError:
    pass
try:
    os.mknod(configfile)
    initdata = {
        'userip': ['127.0.0.1', '::1'],
        'athome': 0,
        'hostip': '2001:0250:3401:6000:0000:0000:30c6:ceb7',
        'esp': 0,
        'curtain': 0,
        'light': 0
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
                       hostname=mqtthost, port=mqttport)

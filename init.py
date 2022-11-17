import json
import os
import IPy

import paho.mqtt.client as mqttclient

tmpdir = os.path.join(os.getcwd(), 'tmp')
facedir = os.path.join(tmpdir, 'face')
configfile = os.path.join(tmpdir, 'config.json')
mqtthost = "home.hackzhu.com"
mqttport = 1883
mqttid = 'c6774a3a08e85c2dc815bd9c4210d372'
initdata = {
    'userip': ['127.0.0.1', '::1'],
    'athome': 0,
    'temperature': u'37℃',
    'humidity': '30%'
}

try:
    os.makedirs(facedir)
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
    mclient = mqttclient.Client()
    mclient.connect(mqtthost, mqttport, 60)
    payload = json.dumps(obj=data)
    mclient.publish('homeassistant/config', payload, 0)


def mqtt_pub(payload="nothing", topic="mqtt", qos=0) -> None:
    mclient = mqttclient.Client(mqttid)
    mclient.connect(mqtthost, mqttport, 60)
    mclient.publish('homeassistant/' + topic, payload, qos)


def mqtt_msg(client, userdata, msg) -> None:
    mpayload = str(msg.payload)[2:-1]
    match mpayload:
        case '1':
            print('this is 1')
        case '2':
            print('this is 2')


def mqtt_sub(topic) -> None:
    mqttclient.connect(mqtthost, mqttport, 60)
    mqttclient.loop_start()
    mqttclient.subscribe('homeassistant/' + topic)
    mqttclient.on_message = mqtt_msg  # 用于回调

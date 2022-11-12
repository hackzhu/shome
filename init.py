import json
import os

import paho.mqtt.client as mqttclient

tmpdir = os.path.join(os.getcwd(), 'tmp')
configfile = os.path.join(tmpdir, 'config.json')
mqtthost = "home.hackzhu.com"
mqttport = 1883
initdata = {
    'userip': ['127.0.0.1', '::1', '123.456.789.0'],
    'athome': 0,
    'temperature': '37℃',
    'humidity': '30%'
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


def config_read() -> dict:
    with open(configfile, 'r') as cf:
        data = json.load(cf)
    return data


def config_write(data):
    with open(configfile, 'w') as cf:
        json.dump(obj=data, fp=cf, indent=4)


def mqtt_pub(payload="nothing", topic="config", qos=0):
    mclient = mqttclient.Client()
    mclient.connect(mqtthost, mqttport, 60)
    payload=json.dumps(obj=payload)
    mclient.publish('homeassistant/' + topic, payload, qos)


def mqtt_msg(client, userdata, msg):
    mpayload = str(msg.payload)[2:-1]
    match mpayload:
        case '1':
            print('this is 1')
        case '2':
            print('this is 2')


def mqtt_sub(topic):
    mqttclient.connect(mqtthost, mqttport, 60)
    mqttclient.loop_start()
    mqttclient.subscribe('homeassistant/' + topic)
    mqttclient.on_message = mqtt_msg  # 用于回调
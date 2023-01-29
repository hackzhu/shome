import json
import os
import random

import paho.mqtt.client as mqttclient

tmpdir = os.path.join(os.getcwd(), 'tmp')
facedir = os.path.join(tmpdir, 'face')
configfile = os.path.join(tmpdir, 'config.json')
mqtthost = "home.hackzhu.com"
mqttport = 1883
configtopic = 'homeassistant/config'


def mqtt_connected(client, userdata, flags, rc) -> None:
    print('Connected with result code '+str(rc))
    client.subscribe(r'dev/+')


def mqtt_callback(client, userdata, msg) -> None:
    # ! mosqutto_pub 要用单引号括着内容，内容里要用双引号'{"light":"on"}'
    status = json.loads(msg.payload)
    if msg.topic == 'esp':
        if status['light'] == 'on':
            print('light on')
        else:
            print('light off')


clientid = f'client-{random.randint(0, 1000)}'
client = mqttclient.Client(clientid)
client.on_connect = mqtt_connected
client.on_message = mqtt_callback
client.connect(mqtthost, mqttport, 60)


# class mqtt:
#     def __init__(self, client, clientid, topic) -> None:
#         self.client = client
#         self.clientid = clientid
#         self.topic = topic
#         self.clientid = f'client-{random.randint(0, 1000)}'
#         self.client = mqttclient.Client(self.clientid)

#     def __del__(self) -> None:
#         self.client.disconnect()

#     def mqtt_connect(self) -> None:
#         self.client.on_connect = lambda a,b,c,d:print('mqtt connected')
#         self.client.connect(mqtthost, mqttport, 60)

#     def mqtt_subscribe(self) -> None:
#         mqttclient.subscribe(self.topic)

#     def mqtt_callback(self, client, userdata, msg) -> None:
#         mpayload = str(msg.payload)[2:-1]
#         match mpayload:
#             case '1':
#                 print('this is 1')
#             case '2':
#                 print('this is 2')

#     def mqtt_public(self, payload="nothing", topic="mqtt", qos=0) -> None:
#         self.client.publish(topic, payload, qos)

def main():
    client.loop_forever()


if __name__ == '__main__':
    main()

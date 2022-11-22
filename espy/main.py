import gc
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import json
esp.osdebug(None)
gc.collect()

ssid = 'wifiboxs-2.4G'
password = 'gxdx28b312'
mqtt_server = 'home.hackzhu.com'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'homeassistant/config'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('WiFi connection successful')


def mqtt_callback(topic, msg):
    client.publish(topic_pub, msg)
    configjson = json.loads(msg)
    for key, value in configjson.items():
        print(key, value, '\n')


def mqtt_subscribe():
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' %
          (mqtt_server, topic_sub))
    return client


def restart():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()


try:
    client = mqtt_subscribe()
except OSError as e:
    restart()

while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1
    except OSError:
        restart()

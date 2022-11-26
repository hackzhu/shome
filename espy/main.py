import time
import ubinascii
import machine
import json

Debug = True
Mqtt = False
Wifi = Mqtt
Motion = False
Dht = False
Light = False

ssid = 'wifiboxs-2.4G'
password = 'gxdx28b312'
hostname = 'esp'

mqtthost = b'home.hackzhu.com'
mqttport = 1883
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'homeassistant/config'
topic_pub = b'hello'

ledpin = machine.Pin(2, machine.Pin.OUT)


def wifi_connect(ssid, password, hostname='esp'):
    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname=hostname, reconnects=10)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        led_blink()


def led_blink():
    ledpin.on()
    time.sleep_ms(250)
    ledpin.off()
    time.sleep_ms(250)


def restart():
    led_blink()
    led_blink()
    led_blink()
    machine.reset()


def dht11():
    import dht
    d = dht.DHT11(machine.Pin(4))
    return d


def mqtt_callback(topic, msg):
    configjson = json.loads(msg)
    for key, value in configjson.items():
        led_blink()


def mqtt_connect():
    from umqtt.simple import MQTTClient
    client = MQTTClient(client_id, mqtthost, mqttport)
    client.set_callback(mqtt_callback)
    try:
        client.connect()
        client.publish(topic_pub, 'online')
        client.subscribe(topic_sub)
    except OSError:
        ledpin.on()
        restart()
    return client


# TODO 按键去抖动
def light_interupt(pin):
    led_blink()


def motion_interupt(pin):
    led_blink()


def debug_output(msg):
    if Debug:
        print(msg)


def main():
    debug_output('start')
    if Wifi:
        debug_output('wifi connecting')
        wifi_connect(ssid, password, hostname)
        debug_output('wifi connected')
    if Mqtt and Wifi:
        mqttclient = mqtt_connect()
    if Motion:
        motionpin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)
        motionpin.irq(motion_interupt, machine.Pin.IRQ_RISING)
    if Light:
        lightpin = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)
        lightpin.irq(light_interupt, machine.Pin.IRQ_RISING)
    if Dht:
        d = dht11()
    while True:
        try:
            if Dht:
                d.measure()
                dhtstatus = {
                    'temperature': d.temperature(),
                    'humidity': d.humidity()
                }
                if Debug:
                    print("temperature:", dhtstatus['temperature'])
                    print('humidity:', dhtstatus['humidity'])
                    time.sleep(5)
            if Mqtt:
                mqttclient.check_msg()
                if Dht:
                    dhtjson = json.dumps(dhtstatus)
                    mqttclient.publish(topic_pub, dhtjson)
                    time.sleep(5)
        except OSError as e:
            debug_output(e)
            restart()


if __name__ == '__main__':
    main()

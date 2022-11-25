import gc
import time
import ubinascii
import machine
import micropython
import json
gc.collect()

ssid = 'wifiboxs-2.4G'
password = 'gxdx28b312'
mqtthost = b'home.hackzhu.com'
mqttport = 1883
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'homeassistant/config'
topic_pub = b'hello'

ledpin = machine.Pin(2, machine.Pin.OUT)

def wifi_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        led_blink()

def led_blink():
    global ledpin
    ledpin.on()
    time.sleep(0.5)
    ledpin.off()
    time.sleep(0.5)


def restart():
    led_blink()
    led_blink()
    led_blink()
    machine.reset()


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

def main():
    wifi_connect()
    mqttclient = mqtt_connect()
    lightpin = machine.Pin(13, machine.Pin.IN)
    lightpin.irq(trigger=machine.Pin.IRQ_RISING, handler=light_interupt)
    while True:
        try:
            mqttclient.check_msg()
        except OSError:
            restart()
        pass


if __name__ == '__main__':
    main()
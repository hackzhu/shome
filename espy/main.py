import time
import ubinascii
import machine
import json

Debug = True
Wifi = False
Mqtt = False
if Mqtt:
    Wifi = True
Motion = False
Dht = True
Light = False

hostname = 'esp'
ssid = 'wifiboxs-2.4G'
password = 'gxdx28b312'

mqtthost = 'home.hackzhu.com'
mqttport = 1883
clientid = ubinascii.hexlify(machine.unique_id())
subtopic = 'etc/' + hostname
pubtpoic = 'dev/' + hostname

ledpin = machine.Pin(2, machine.Pin.OUT)
lightstatus = 0


def wifi_connect(ssid, password, hostname='esp') -> None:
    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname=hostname, reconnects=10)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        led_blink()


def led_blink() -> None:
    ledpin.on()
    time.sleep_ms(250)
    ledpin.off()
    time.sleep_ms(250)


def restart() -> None:
    led_blink()
    led_blink()
    led_blink()
    machine.reset()


def dht11() -> None:
    import dht
    d = dht.DHT11(machine.Pin(4))
    return d


def mqtt_callback(topic, payload) -> None:
    configjson = json.loads(payload)
    if configjson['light'] == 'on':
        pass
        # light_on
    else:
        pass
        # light_off
    if configjson['motion'] == 'on':
        pass
        # motion_on
    else:
        pass
        # motion_off

def mqtt_connect() -> None:
    from umqtt.simple import MQTTClient
    client = MQTTClient(clientid, mqtthost, mqttport)
    client.set_callback(mqtt_callback)
    try:
        client.connect()
        client.publish(pubtpoic, 'online')
        client.subscribe(subtopic)
    except OSError:
        restart()
    return client


# TODO 按键去抖动
def light_interupt(pin) -> None:
    global lightstatus
    lightstatus = 1


def motion_interupt(pin) -> None:
    led_blink()


def debug_output(*msg) -> None:
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
        debug_output('looping')
        try:
            if Light:
                debug_output('light')
                global lightstatus
                if lightstatus == 1:
                    lightstate = machine.disable_irq()
                    led_blink()
                    lightstatus = 0
                    if Mqtt:
                        mqttclient.publish(pubtpoic, 'light on')
                    debug_output('light on')
                    machine.enable_irq(lightstate)
                    # TODO 虽可能解决，还需做硬件防抖动
            if Dht:
                debug_output('dht11')
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
                debug_output('mqtt')
                mqttclient.check_msg()
                if Dht:
                    dhtjson = json.dumps(dhtstatus)
                    mqttclient.publish(pubtpoic, dhtjson)
                    time.sleep(5)
        except Exception as e:
            debug_output('looped for ' + e)
            restart()


if __name__ == '__main__':
    main()

#!/usr/bin/python3

import asyncio
import os
import time

import paho.mqtt.client as mqttc
from bleak import BleakScanner as blcs

# from bleak import BleakClient as blec


host_devices = ("94:37:F7:40:8F:1C", "9C:19:C2:45:5A:20")
mqtt_host = "hackzhu.com"
mqtt_port = 1883
ping_host = ("192.168.2.151", "192.168.2.186")


def ping():
    for h in ping_host:
        response = os.system("ping -c 1 -W 500 " + h + " >/dev/null 2>&1")
        if response == 0:
            return 1
    return 0


def mqtt_pub():
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish("hass/athome", "1", 0)
    # mclient.loop_forever()


def mqtt_pub1():
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish("hass/athome", "0", 0)

# TODO 先wifi后蓝牙
# TODO 蓝牙多设备逻辑优化


async def athomescan():
    nearby_devices = await blcs.discover()
    athome_status = 0
    ping_satus = ping()
    for n in nearby_devices:
        for d in host_devices:
            if n.address == d:
                athome_status = 1
                break
    if (athome_status == 1 or ping_satus == 1):
        mqtt_pub()
    else:
        mqtt_pub1()
    time.sleep(1)

if __name__ == "__main__":
    while 1:
        asyncio.gather(athomescan())

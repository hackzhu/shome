import os
from time import sleep
import paho.mqtt.client as mqttc

ping_host = ("192.168.2.150", "192.168.2.160")
mqtt_host = "hackzhu.com"
mqtt_port = 1883


def mpub(mpayload="1", mtopic="hass/athome", mqos=0):
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish(mtopic, mpayload, mqos)


def ping():
    for h in ping_host:
        response = os.system("ping -c 1 -W 500 " + h + " >/dev/null 2>&1")
        if response == 0:
            return 1
    return 0

# TODO 应使用虚拟按键来做第一判断项，要是有孩子最好是实体按键加虚拟按键并在主页显示
def main():
    ping_status = ping()
    if ping_status == 1:
        mpub(1)
        return 1
    else:
        mpub(0)
        return 0


if __name__ == "__main__":
    main()

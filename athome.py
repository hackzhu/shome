import os
from time import sleep
import paho.mqtt.client as mqttc

ping_host = ("192.168.2.151", "192.168.2.186")
mqtt_host = "hackzhu.com"
mqtt_port = 1883


def mpub(mpayload="1", mtopic="home/athome", mqos=0):
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish(mtopic, mpayload, mqos)


def ping():
    for h in ping_host:
        response = os.system("ping -c 1 -W 500 " + h + " >/dev/null 2>&1")
        if response == 0:
            return 1
    return 0


if __name__ == "__main__":
    while 1:
        sleep(10)
        pingstatus = ping()
        if pingstatus == 1:
            mpub(1)
            break
        else:
            continue

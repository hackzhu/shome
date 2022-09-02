import os
import paho.mqtt.client as mqttc

with open('userhost') as hf:
    user_host = hf.read().splitlines()
mqtt_host = "hackzhu.com"
mqtt_port = 1883


def mpub(mpayload="1", mtopic="hass/athome", mqos=0):
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish(mtopic, mpayload, mqos)


def ping():
    for h in user_host:
        response = os.system("ping -c 1 -W 500 " + h + " >/dev/null 2>&1")
        if response == 0:
            return 1
    return 0

# TODO 应使用虚拟按键来做第一判断项，要是有孩子最好是实体按键加虚拟按键并在主页显示


def main():
    ping_status = ping()
    if not os.path.exists('tmp/athome_old_status'):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        os.system('touch tmp/athome_old_status')
    old_status_file = open('tmp/athome_old_status', 'w+')
    old_status_file.seek(0, 0)
    old_status = old_status_file.read()
    if ping_status == 1:
        if old_status != 1:
            mpub(1)
            old_status_file.write('1')
        old_status_file.close()
        return 1
    else:
        if old_status != 0:
            mpub(0)
            old_status_file.write('0')
        old_status_file.close()
        return 0


if __name__ == "__main__":
    main()

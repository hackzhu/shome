from time import sleep
import paho.mqtt.client as mqtt
import asyncio

mhost = "home.hackzhu.com"
mport = 1883
mqttc = mqtt.Client()


def mcon():
    mqttc.connect(mhost, mport, 60)
    mqttc.loop_start()



def mmsg(client, userdata, msg):
    mpayload = str(msg.payload)[2:-1]
    match mpayload:
        case '1':
            print('this is 1')
            sleep(2)
        case '2':
            print('this is 2')
            sleep(2)


def msub():
    mqttc.subscribe("homeassistant/test")
    mqttc.on_message = mmsg


def main():
    mcon()
    msub()
    while 1:
        pass


if __name__ == '__main__':
    main()

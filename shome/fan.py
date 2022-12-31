#!/usr/bin/env python

from time import sleep
import datetime
import RPi.GPIO as GPIO

timenoset = True

def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as t:
        return float(t.read())/1000


def main():
    channel = 14
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setwarnings(False)
    while 1:
        if not timenoset:
            start_time = datetime.datetime.strptime(
                str(datetime.datetime.now().date()) + '00:30', '%Y-%m-%d%H:%M')
            end_time = datetime.datetime.strptime(
                str(datetime.datetime.now().date()) + '07:00', '%Y-%m-%d%H:%M')
            now_time = datetime.datetime.now()
        if not ((now_time > start_time and now_time < end_time) or timenoset):
            temp = cpu_temp()
            if temp > 50.0:
                GPIO.output(channel, GPIO.LOW)
            if temp < 45.0:
                GPIO.output(channel, GPIO.HIGH)
        sleep(10)


if __name__ == '__main__':
    main()

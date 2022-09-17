import RPi.GPIO as GPIO


def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as t:
        return float(t.read())/1000


def main():
    channel = 14
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setwarnings(False)
    while 1:
        temp = cpu_temp()
        if temp > 50.0:
            GPIO.output(channel, GPIO.LOW)
        if temp < 40.0:
            GPIO.output(channel, GPIO.HIGH)


if __name__ == '__main__':
    main()

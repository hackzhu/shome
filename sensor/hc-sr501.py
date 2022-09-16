import RPi.GPIO as GPIO    # 导入库，并进行别名的设置
import time     # 导入time模块
import paho.mqtt.client as mqttc   # 引入MQTT协议

mqtt_host="home.hackzhu.com"
mqtt_port=1883

def mpub(mpayload="1", mtopic="homeassistant/person", mqos=0):
    mclient = mqttc.Client()
    mclient.connect(mqtt_host, mqtt_port, 60)
    mclient.publish(mtopic, mpayload, mqos)


#初始化
def init():
    GPIO.setwarnings(False)     # 禁用警告
    GPIO.setmode(GPIO.BOARD)    # 选择BOARD编码方式
    GPIO.setup(12,GPIO.IN)      # 设置12号引脚为输入模式
    GPIO.setup(21,GPIO.OUT)     # 设置21号引脚为输出模式
    pass

#蜂鸣器鸣叫函数
def beep():
    while GPIO.input(12):           # 执行一个循环
        GPIO.output(21,GPIO.LOW)    # 将21号引脚设置为低电平
        time.sleep(0.5)             # 延时0.5s
        GPIO.output(21,GPIO.HIGH)   # 将21号引脚设置为高电平
        time.sleep(0.5)

#感应器侦测函数
def detct():

    #因为是仅仅试验，所以只让它循环运行100次
    for i in range(1,101):
        #如果感应器针脚输出为True，则打印信息并执行蜂鸣器函数
        if GPIO.input(12) == True:
            print ("Someone isclosing!")
            mpub("Someone isclosing!", "homeassistant/person")
            beep()


        #否则将蜂鸣器的针脚电平设置为HIGH
        else:
            GPIO.output(21,GPIO.HIGH)
#            print("Noanybody!")
            mpub("Noanybody!","homeassistant/person")
        time.sleep(2)

time.sleep(5)
init()
detct()

#脚本运行完毕执行清理工作
GPIO.cleanup()

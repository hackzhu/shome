/*******************************************************
          ESP32 使用中断
   功能：使用中断来实现LED的状态切换
   引脚： [ESP32 GIO12 - BUTTON] [ESP32 GIO14 - LED ]
   Designer: Code_Mouse
   Date:2018-9-16
 *******************************************************/
byte ledPin = 14;          // LED的引脚
byte interruptPin = 12;    //中断引脚
volatile byte state = LOW; //状态为低电平

void setup()
{
    pinMode(ledPin, OUTPUT);

    pinMode(interruptPin, INPUT_PULLUP);                                 //将中断的引脚设置为输入PULLUP模式
    attachInterrupt(digitalPinToInterrupt(interruptPin), blink, CHANGE); //设置触发中断的模式和中断服务函数
}

void loop()
{
}

//中断服务函数
void blink()
{
    state = !state;
    digitalWrite(ledPin, state);
}
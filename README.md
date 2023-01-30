# 基于树莓派的智能家居系统设计

## 封面

## 中文摘要

## 外文摘要

## 目录

## 正文

### 第一章 绪论

#### 研究目的及意义

#### 国内外{发展,研究}现状

### 第二章 硬件平台

#### 硬件设备

##### 树莓派

##### arduino

##### esp32

> wifi

连接 wifi
自定义主机名 ESP32

> mqtt

> 中断

- 中断 1 mqtt 主题
- 中断 2 wifi 通断

#### 传感器

##### 温湿度传感器

DHT-11

##### 人体传感器

HC-SR501

##### 声音传感器

##### 光传感器

##### 门窗传感器

#### 语音控制模块

SU-10A
小爱同学

#### 摄像模块

### 第三章 软件平台

#### linux

树莓派官方 64 位系统，基于 Debian

#### docker

#### homeassistant

#### mqtt

> broker

docker:emqx

```emqx
docker run -d --restart always --name emqx -p 1883:1883 -p 8083:8083 -p 8084:8084 -p 8883:8883 -p 18083:18083 emqx/emqx
```

可用 docker-compose 代替

面板控制端口：18083
mqtt 端口：1883
mqtt with ssl 端口：8883

默认用户名：admin
默认密码：public

> client

shell:mosquitto

mosquitto_sub -h localhost -t test
mosquitto_pub -h localhost -t test -m 'test'

mosquitto_pub 命令参数说明

1. -d  打印debug信息
2. -f  将指定文件的内容作为发送消息的内容
3. -h  指定要连接的域名  默认为localhost
4. -i  指定要给哪个clientId的用户发送消息
5. -I  指定给哪个clientId前缀的用户发送消息
6. -m  消息内容
7. -n  发送一个空（null）消息
8. -p  连接端口号
9. -q  指定QoS的值（0,1,2）
10. -t  指定topic
11. -u  指定broker访问用户
12. -P  指定broker访问密码
13. -V  指定MQTT协议版本
14. --will-payload  指定一个消息，该消息当客户端与broker意外断开连接时发出。该参数需要与--will-topic一起使用
15. --will-qos  Will的QoS值。该参数需要与--will-topic一起使用
16. --will-retain 指定Will消息被当做一个retain消息（即消息被广播后，该消息被保留起来）。该参数需要与--will-topic一起使用
17. --will-topic  用户发送Will消息的topic

python:paho.mqtt
<PubSubClient.h>

#### opencv

获取摄像头图像，显示色彩图像，检测用灰度图
加载官方训练好的人脸分类器，使用LBPH方法


### 第四章 管理

#### 前端管理

hass 侧边仪表盘添加网页卡片（可以不用 supervisor）
将私人配置和 opencv 的都基于 flask 开发
只在访问时用flask,其余都在后台运行

#### 远程管理

##### ipv6

介绍 ipv6 优点、国内外发展状况，与 ipv4 的区别
与内网穿透的优劣性比较，突出 ipv6 优点
简单介绍国家开始推广 ipv6

##### DDNS

ipv6 的地址太长，难记，说不准哪时还会变，需要 DDNS

### 第五章 结论

## 参考文献

## 附录

## 致谢

## 封底

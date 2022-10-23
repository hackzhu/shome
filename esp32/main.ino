#include <WiFi.h>
#include <PubSubClient.h>

// WIFI
const char *ssid = "wifiboxs-2.4G";
const char *password = "gxdx28b312";
String hostname = "ESP32";

// MQTT
const char *mqtt_broker = "home.hackzhu.com";
const char *mqtt_username = "biye";
const char *mqtt_password = "dachuang";
const char *topic = "esp";
const int mqtt_port = 1883;

WiFiClient espClient;
void callback(char *topic, byte *payload, unsigned int length);
PubSubClient client(mqtt_broker, mqtt_port, callback, espClient);
String client_id = "ESP32";

void initWiFi()
{
    WiFi.hostname(hostname.c_str());
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(2000);
        Serial.println("未连接Wifi");
    }
    Serial.println("已连接Wifi");
}

void initmqtt()
{
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected())
    {
        Serial.println("正连接至MQTT服务器...");
        if (client.connect("测试", mqtt_username, mqtt_password))
        {
            Serial.println("登录成功...");
        }
        else
        {
            Serial.println("登陆失败,重新连接...");
            Serial.println(client.state());
            delay(2000);
        }
        client.subscribe(topic);
        client.publish(topic, "测试测试");
        Serial.println("已发送测试消息");
    }
}

void callback(char *topic, byte *payload, unsigned int length)
{
    Serial.print("来自主题：");
    Serial.println(topic);
    Serial.print("内容:");
    for (int i = 0; i < length; i++)
    {
        Serial.print((char)payload[i]);
    }
    Serial.println("");
    Serial.println("------------------------------------");
}

void setup()
{
    Serial.begin(115200);
    initWiFi();
    initmqtt();
}

void loop()
{
    client.loop();
}
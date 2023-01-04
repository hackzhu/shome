import json
import os
import IPy
import requests
import re
import smtplib
import init

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

tmpdir = os.path.join(os.getcwd(), 'tmp')
configfile = os.path.join(tmpdir, 'config.json')
mqttbroker = "127.0.0.1"
mqttport = 1883
configtopic = 'etc/config'
ddnsdomain = 'home.hackzhu.com'
ddnstoken = '336294,4da657cefe9db0f9ee4e882cf9a8986a'


def check_ip(ip) -> bool:
    try:
        version = IPy.IP(ip).version()
        if version == 4 or version == 6:
            return True
        else:
            return False
    except:
        return False


def get_ip(strict=0) -> str:
    try:
        res = requests.get('http://ip6only.me')
        ip = re.search(r'\+3>(.*?)</', res.content.decode('utf-8')).group(1)
        if check_ip(ip):
            if strict == 1:
                if ping(ip) is False:
                    return '::1'
            return ip
        else:
            return '::1'
    except:
        return '::1'


def ping(ip=None, domain=None) -> bool:
    try:
        if domain == None:
            version = IPy.IP(ip).version()
            response = os.system("ping -c 1 -W 500 -" +
                                 str(version) + ' ' + ip + " >/dev/null 2>&1")
        else:
            response = os.system("ping -c 1 -W 500 " +
                                 domain + " >/dev/null 2>&1")
        if response == 0:
            return True
        return False
    except:
        return False


# TODO 寻找更适合的方法
def at_home() -> int:
    try:
        config = init.config_read()
        for ui in config['athome']['userip']:
            pingstatus = ping(ui)
            if pingstatus is True:
                athome = 1
                break
            else:
                athome = 0
        return athome
    except:
        print('error')
        return 2


def ddnspod(ip=None) -> str:
    try:
        if ip is None:
            ip = get_ip()
        subdomain, domain = ddnsdomain.split('.', 1)
        ipversion = IPy.IP(ip).version()
        if ipversion == 4:
            recordtype = "A"
        else:
            recordtype = "AAAA"
        listurl = r"https://dnsapi.cn/Record.List"
        ddnsurl = r"https://dnsapi.cn/Record.Ddns"
        headers = {'User-Agent': r'hackddns/1.0.0(3110497917@qq.com)'}
        data = {
            'login_token': ddnstoken,
            'format': 'json',
            'domain': domain,
            'sub_domain': subdomain
        }
        list = requests.post(url=listurl, headers=headers, data=data).text
        list = json.loads(list)
        recordid = list['records'][0]['id']
        oldip = list['records'][0]['value']
        if ip != oldip:
            ddnsdata = {
                'login_token': ddnstoken,
                'format': 'json',
                'domain': domain,
                'sub_domain': subdomain,
                'record_id': recordid,
                'record_type': recordtype,
                'value': ip,
                'record_line_id': '0'
            }
            requests.post(url=ddnsurl, headers=headers, data=ddnsdata)
        return ip
    except:
        return '::1'


def mail_send():
    try:
        config = init.config_read()
        mailserver = config['mail']['server']
        mailuser = config['mail']['user']
        mailpass = config['mail']['password']
        sender = config['mail']['sender']
        receivers = config['mail']['receivers']

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = receivers[0]
        message['Subject'] = 'title test'

        content = MIMEText('content test', 'plain', 'utf-8')
        with open('tmp/konqi.png', 'rb')as pic:
            picture = MIMEImage(pic.read())
            picture['Content-Type'] = 'application/octet-stream'
            picture['Content-Disposition'] = 'attachment;filename="konqi.png"'
        # TODO 图片路径放进形参

        message.attach(content)
        message.attach(picture)

        smtpObj = smtplib.SMTP_SSL(mailserver)
        smtpObj.login(mailuser, mailpass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print('success')
    except FileNotFoundError:
        print('picture file error')
    except smtplib.SMTPException as e:
        print('error', e)
    except:
        print('error')


def main():
    print(get_ip())


if __name__ == '__main__':
    main()

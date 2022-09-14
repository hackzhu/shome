#/usr/bin/bash

token="336294,4da657cefe9db0f9ee4e882cf9a8986a"
sub_domain="home"
domain="hackzhu.com"
record_type="AAAA"
agent="hackddns/1.0.0(3110497917@qq.com)"
dnsapi_list="https://dnsapi.cn/Record.List"
dnsapi_ddns="https://dnsapi.cn/Record.Ddns"
data="login_token=$token&format=json&domain=$domain&sub_domain=$sub_domain"
list_json=$(curl -X POST -s -A $agent -d $data $dnsapi_list)
old_ip=$(echo $list_json | sed 's/.*,"value":"\([0-9a-fA-F\.\:]*\)".*/\1/')
record_id=$(echo $list_json | sed 's/.*"id":"\([0-9]*\)".*/\1/')
new_ip=$(ip -6 a|grep inet6|grep -v ::1|cut -d "/" -f1|awk '{print $2}'|head -n 1)
ddns_data="$data&record_id=$record_id&record_type=$record_type&value=$new_ip&record_line=%e9%bb%98%e8%ae%a4"
if [ $old_ip != $new_ip ]
then
    curl -X POST -s -A $agent -d $ddns_data $dnsapi_ddns
fi
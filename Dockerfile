## 参考 https://developer.aliyun.com/article/484262
## Set the base image to CentOS  基于centos镜像
FROM centos
# File Author / Maintainer  作者信息
MAINTAINER hackzhu 3110497917@qq.com
# Install necessary tools  安装一些依赖的包
RUN yum install -y pcre-devel wget net-tools gcc zlib zlib-devel make openssl-devel
# Install Nginx  安装nginx
ADD http://nginx.org/download/nginx-1.8.0.tar.gz .  # 添加nginx的压缩包到当前目录下
RUN tar zxvf nginx-1.8.0.tar.gz  # 解包
RUN mkdir -p /usr/local/nginx  # 创建nginx目录
RUN cd nginx-1.8.0 && ./configure --prefix=/usr/local/nginx && make && make install  # 编译安装
RUN rm -fv /usr/local/nginx/conf/nginx.conf  # 删除自带的nginx配置文件
ADD http://www.apelearn.com/study_v2/.nginx_conf /usr/local/nginx/conf/nginx.conf  # 添加nginx配置文件
# Expose ports  开放80端口出来
EXPOSE 80
# Set the default command to execute when creating a new container  这里是因为防止服务启动后容器会停止的情况，所以需要多执行一句tail命令
ENTRYPOINT /usr/local/nginx/sbin/nginx && tail -f /etc/passwd
FROM selenium/standalone-chrome

USER root

COPY ./get-pip.py ./get-pip.py
COPY ./requirements.txt ./requirements.txt

RUN   sed -i "s/\/\/.*archive.ubuntu.com/\/\/mirrors.aliyun.com/g;s/\/\/.*security.ubuntu.com/\/\/mirrors.aliyun.com/g" /etc/apt/sources.list

RUN apt update -y
RUN apt install python3-distutils -y

RUN python3 get-pip.py -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
RUN pip3 install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

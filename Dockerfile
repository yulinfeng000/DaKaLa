FROM yulinfeng/dakala-base:1.0

LABEL maintainer="yulinfeng<yulinfeng.mail@foxmail.com>"

RUN echo "Asia/Shanghai" > /etc/timezone

COPY ./requirements.txt .

RUN pip install -r requirements.txt

ENV APP_SECRET_KEY='9438e1d80dc365bc4609df5e3269a4b01845d587f51cd6d7a222fc0d0e0b809d'
ENV APP_ADMIN_KEY='Tomcat!'
RUN mkdir -p /dakala/app

RUN mkdir -p /dakala/data/log

RUN mkdir -p /dakala/data/pic

RUN mkdir -p /dakala/data/db

WORKDIR /dakala

VOLUME /dakala/data

COPY ./app/* ./app/

COPY ./gunicorn.conf.py ./gunicorn.conf.py

EXPOSE 8000

CMD [ "gunicorn","-b",":8000","-k","gevent","app.main:app","--log-config","app/log.conf","--preload"]

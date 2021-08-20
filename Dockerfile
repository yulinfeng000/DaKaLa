FROM yulinfeng/dakala-base:1.0

LABEL maintainer="yulinfeng<yulinfeng.mail@foxmail.com>"

RUN echo "Asia/Shanghai" > /etc/timezone

COPY ./requirements.txt .

RUN pip install -r requirements.txt

ENV APP_SECRET_KEY='123456'

ENV APP_ADMIN_KEY=''

RUN mkdir -p /dakala/app

RUN mkdir -p /dakala/data/log

RUN mkdir -p /dakala/data/pic

RUN mkdir -p /dakala/data/db

WORKDIR /dakala

VOLUME /dakala/data

COPY ./app/* ./app/

COPY ./gunicorn.conf.py ./gunicorn.conf.py

EXPOSE 8000

CMD ["gunicorn","app.main:app","--log-config","app/log.conf"]

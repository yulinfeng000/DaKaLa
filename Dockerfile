FROM yulinfeng/dakala-base:1.0

USER root

RUN mkdir -p /usr/local/dakala/templates

RUN mkdir -p /usr/local/dakala/static/vc_images

RUN mkdir -p /usr/local/dakala/data/log

RUN mkdir -p /usr/local/dakala/data/db

WORKDIR /usr/local/dakala

COPY ./logsetting.py ./logsetting.py

COPY ./daka.py ./daka.py

COPY ./app.py ./app.py

COPY ./userdb.py ./userdb.py

COPY ./get-pip.py ./get-pip.py

COPY ./templates/* ./templates/

VOLUME /usr/local/dakala/static/

VOLUME /usr/local/dakala/db

EXPOSE 5000

CMD ["python3" , "app.py"]

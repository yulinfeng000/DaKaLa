FROM yulinfeng/dakala-base:1.0

USER root

RUN mkdir -p /usr/local/dakala/templates

RUN mkdir -p /usr/local/dakala/static/vc_images

RUN mkdir -p /usr/local/dakala/static/js

RUN mkdir -p /usr/local/dakala/data/log

RUN mkdir -p /usr/local/dakala/data/db

WORKDIR /usr/local/dakala

COPY ./static/js/rolldate.min.js ./static/js/rolldate.min.js

COPY app/logsetting.py ./logsetting.py

COPY app/daka.py ./daka.py

COPY app/app.py ./app.py

COPY app/userdb.py ./userdb.py

COPY ./get-pip.py ./get-pip.py

COPY ./templates/* ./templates/

VOLUME /usr/local/dakala/static/vc_images

VOLUME /usr/local/dakala/db

EXPOSE 5000

CMD ["python3" , "app.py"]

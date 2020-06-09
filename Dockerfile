FROM yulinfeng/dakala-base:1.0
USER root
RUN mkdir -p /usr/local/dakala
RUN mkdir -p /usr/local/dakala/templates
RUN mkdir -p /usr/local/dakala/static/vc_images
RUN mkdir -p /usr/local/dakala/static/log
RUN mkdir -p /usr/local/dakala/qbotor
RUN mkdir -p /usr/local/dakala/qbotor/plugins
WORKDIR /usr/local/dakala

ENV QBOT_IP 129.28.124.34
COPY ./logsetting.py ./logsetting.py
COPY ./daka.py ./daka.py
COPY ./app.py ./app.py
COPY ./userdb.py ./userdb.py
COPY ./get-pip.py ./get-pip.py
COPY ./requirements.txt ./requirements.txt
COPY  ./templates/index.html ./templates/index.html
COPY ./templates/info.html ./templates/info.html
COPY ./templates/photo.html ./templates/photo.html
COPY ./templates/success.html ./templates/success.html
COPY ./qbotor/plugins/dakala.py  ./qbotor/plugins/dakala.py
COPY ./qbotor/config.py  ./qbotor/config.py
COPY ./qbotor/qbot.py ./qbotor/qbotor.py
VOLUME /usr/local/dakala/static/
EXPOSE 5000 
CMD ["python3" , "app.py"]

FROM yulinfeng/dakala-base:1.0
USER root
RUN mkdir -p /usr/local/dakala
RUN mkdir -p /usr/local/dakala/templates
RUN mkdir -p /usr/local/dakala/static/vc_images

WORKDIR /usr/local/dakala

COPY ./daka.py ./daka.py
COPY ./app.py ./app.py
COPY ./userdb.py ./userdb.py
COPY ./get-pip.py ./get-pip.py
COPY ./requirements.txt ./requirements.txt
COPY  ./templates/index.html ./templates/index.html
COPY ./templates/info.html ./templates/info.html
COPY ./templates/photo.html ./templates/photo.html
COPY ./templates/success.html ./templates/success.html

VOLUME /usr/local/dakala/static/
EXPOSE 5000 
CMD ["python3" , "app.py"]

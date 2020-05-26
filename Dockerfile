FROM elgalu/selenium
USER root
RUN mkdir -p /usr/local/dakala
RUN mkdir -p /usr/local/dakala/templates
RUN mkdir -p /usr/local/dakala/static
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

RUN python3 ./get-pip.py

VOLUME /usr/local/dakala/static/
RUN pip3 install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000
CMD ["python3" , "app.py"]
# 打卡啦 DaKaLa

[打卡地址](http://dakala.merborn.fun)

**觉得好用给个 star 呗，各位老板这个对我真的很重要**

## 介绍

> 成都信息工程大学疫情打卡解决器，每天为你自动打卡

每天重复的工作很快会燃烧自己对生活的热情，本项目旨在帮兄弟萌燃起对生活的热情 2333

## 推荐 Docker 运行

- 现成镜像
  
  建立 data/db,data/log,data/pic 三个文件夹
   结构如下图所示
   ```
    data-
         |_  db
         |_  log
         |_  pic
    ```
    docker-compose.yml 文件
    请不要拆分该文件分别启动镜像
    ```yaml
    services:
      dakala:
          container_name: dakala
          image: yulinfeng/dakala2:1.9
          init: true
          environment: 
              APP_SECRET_KEY:  # jwt 密钥
              APP_ADMIN_KEY:  # 管理员 密钥
              TZ: "Asia/Shanghai" # 时区 请不要修改
          volumes:
              - ./data:/dakala/data # 容器数据挂载到当前目录下的data文件夹下
          ports:
              - 8000:8000
      frontend:
          image: yulinfeng/dakala2-frontend:uni-1.0
          container_name: dk2f
          ports:
            - 5000:5000
          depends_on:
            - dakala
    ```

## 本地搭建运行环境开发

1. 前提: 需要 selenium chrome-driver chrome
2. 在项目根目录建立
   data/db,data/log,data/pic 三个文件夹
   结构如下图所示
   ```
    data-
         |_  db
         |_  log
         |_  pic
   ```
3. 安装必要依赖并启动服务端: 

   `pip install -r requirements.txt`

   `gunicorn -b :8000 -k gevent app.main:app --reload --preload`
4. 构建并启动前端:  
   `cd frontend && yarn`

   `yarn rw-build`

   `node ./server/index.js`
5. 访问 localhost:5000 即可
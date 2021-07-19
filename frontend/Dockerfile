FROM node:12.20
LABEL MAINTAINER=yulinfeng<791774086@qq.com>
# 初始化
WORKDIR /app
RUN npm init -y
RUN npm install express
# 拷贝内容
COPY ./build  ./build
COPY ./server ./server

# 默认端口5000
ENV PORT=5000
# 暴露端口
EXPOSE $PORT
# 启动服务器
ENTRYPOINT ["node","./server/index.js"]
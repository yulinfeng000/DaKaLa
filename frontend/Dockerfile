FROM node:12.20
LABEL MAINTAINER=yulinfeng<791774086@qq.com>
# 初始化
ENV REACT_APP_BASE_URL=http://localhost:8000

# 默认端口5000
ENV PORT=5000

# 暴露端口
EXPOSE $PORT

WORKDIR /app

RUN npm install -g serve

COPY ./ ./

RUN npm install

# 启动服务器
ENTRYPOINT ["sh","docker-entrypoint.sh"]
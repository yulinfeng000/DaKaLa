# 注入环境变量
touch .env && rm .env;
echo REACT_APP_BASE_URL=$REACT_APP_BASE_URL >> .env;
npm run rw-build;
serve -l $PORT -s build;
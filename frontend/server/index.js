const express = require('express')
const path = require('path');
const app = express()

//react静态文件路径
const static_path = path.resolve('build');
app.use(express.static(static_path));

app.get('/*', (req, res) => {
    res.sendFile(path.join(static_path, 'index.html'));
});


const port = process.env.PORT || 5000;
app.listen(port)

console.log(`服务器启动成功，监听0.0.0.0:${port}`)

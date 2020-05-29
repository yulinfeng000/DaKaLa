import time
from flask import Flask, request, render_template, Response
import userdb
from daka import dakala
import threading
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask_apscheduler import APScheduler
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, static_folder='./static')
scheduler = APScheduler(app=app)
http_server = HTTPServer(WSGIContainer(app), xheaders=True)


@app.route('/', methods=['GET'])
def hello_world():
    cok = request.cookies
    stuid = cok.get("stuid")
    if stuid is None:
        return render_template('index.html')
    elif userdb.db_get_user_by_stuid(stuid) is None:
        resp = Response(render_template('index.html'))
        resp.delete_cookie("stuid")
        return resp
    else:
        return render_template('info.html', stuid=stuid)


@app.route('/api/register', methods=['POST'])
def api_register():
    print("收到注册请求")
    required = ['stuid', 'password', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.json

    if not all(k in values for k in required):
        resp = Response('有必要信息微填写')
        resp.status_code = 403
        return resp
    stuid = values.get('stuid')
    password = values.get('password')
    config = {
        'homeStatus': values.get('homeStatus'),
        'livingStatus': values.get('livingStatus'),
        'healthStatus': values.get('healthStatus'),
        'workingPlace': values.get('workingPlace'),
        'cityStatus': values.get('cityStatus')
    }
    userdb.db_put_user_info(stuid, password)
    userdb.db_put_user_config(stuid, config)

    resp = Response('成功', 200)
    return resp


@app.route("/register", methods=['POST'])
def register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    password = values.get('password')
    config = {
        'homeStatus': values.get('homeStatus'),
        'livingStatus': values.get('livingStatus'),
        'healthStatus': values.get('healthStatus'),
        'workingPlace': values.get('workingPlace'),
        'cityStatus': values.get('cityStatus')
    }
    userdb.db_put_user_info(stuid, password)
    userdb.db_put_user_config(stuid, config)

    resp = Response(render_template('success.html'))
    resp.set_cookie("stuid", stuid)
    return resp


@app.route('/delete', methods=['POST'])
def del_info():
    required = ['stuid']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    userdb.db_delete_user_info(stuid)
    resp = Response("<h1>delete success</h1>")
    resp.delete_cookie("stuid")
    return resp, 200


@app.route('/api/delete/<stuid>', methods=['POST'])
def api_del_info(stuid):
    print("删除", stuid)
    userdb.db_delete_user_info(stuid)
    return 200


@app.route('/photo/<stuid>', methods=['POST'])
def photo(stuid):
    vc_path = f'{stuid}_img.png'
    return render_template('photo.html', img_src=vc_path)


def daka_worker(stuid):
    print("打卡中", stuid)
    student = userdb.db_get_user_by_stuid(stuid)
    config = userdb.db_get_user_config(stuid)
    dakala(student, config)  # 测试用暂时注解，


@app.route('/daka/nophoto/<stuid>', methods=['POST'])
def dakanophoto(stuid):
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    return "打卡成功", 200


@app.route('/api/daka/nophoto/<stuid>', methods=['POST'])
def api_dakanophoto(stuid):
    """
    api 接口
    :param stuid: 学号
    :return:
    """
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    return "打卡成功", 200


@app.route('/daka/<stuid>', methods=['POST'])
def daka(stuid):
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    while t1.is_alive():
        time.sleep(1)
    return photo(stuid), 200


@scheduler.task(id="cycle_daka", trigger='cron', timezone='Asia/Shanghai', day_of_week='0-6', hour=7, minute=1)
def cycle_daka():
    print("开始执行定时打卡")
    pool = ThreadPoolExecutor(2)
    mylist = userdb.find_all_user()
    for stu in mylist:
        pool.submit(daka_worker, stu['stuid'])
        # _t = threading.Thread(target=daka_worker, args=(stu['stuid'],), daemon=True)
        # _t.start()
    return "批量打卡成功", 200


if __name__ == '__main__':
    http_server.listen(5000, "0.0.0.0")
    scheduler.start()
    IOLoop.instance().start()

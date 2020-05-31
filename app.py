import random
import string
import logsetting  # 不能删！！
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
from tornado.log import gen_log
import os
from datetime import timedelta

app = Flask(__name__, static_folder='./static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=5)
scheduler = APScheduler(app=app)
http_server = HTTPServer(WSGIContainer(app), xheaders=True)
t_pool = ThreadPoolExecutor(2)  # 别设置太大，打卡很要求性能，同时执行太多会顶不住


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


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
        ck_info = userdb.db_get_dk_callback_info(stuid)
        if ck_info is None:
            ck_info = "还没在服务器上打过卡呢"
        return render_template('info.html', stuid=stuid, callback=ck_info)


@app.route('/api/register', methods=['POST'])
def api_register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.json

    if not all(k in values for k in required):
        resp = Response('有必要信息未填写')
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
    gen_log.info(f'学号 {stuid} , 移动端注册成功')
    return resp


@app.route('/api/ck/<stuid>', methods=['POST'])
def api_get_ck_info(stuid):
    ck_info = userdb.db_get_dk_callback_info(stuid)
    if ck_info is None:
        ck_info = "还没在服务器上打过卡呢"
    return ck_info,200


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
    gen_log.info(f'学号 {stuid} , 浏览器注册成功')
    return resp


@app.route('/delete', methods=['POST'])
def del_info():
    required = ['stuid']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    userdb.db_delete_user_info(stuid)
    stu_img_path = os.path.abspath(f'./static/vc_images/{stuid}_img.png')
    if os.path.exists(stu_img_path):
        os.remove(stu_img_path)
    resp = Response("<h1>delete success</h1>")
    resp.delete_cookie("stuid")
    gen_log.warning(f'学号 {stuid} ,通过浏览器删除了自己信息')
    return resp, 200


@app.route('/api/delete/<stuid>', methods=['POST'])
def api_del_info(stuid):
    userdb.db_delete_user_info(stuid)
    stu_img_path = os.path.abspath(f'./static/vc_images/{stuid}_img.png')
    if os.path.exists(stu_img_path):
        os.remove(stu_img_path)
    gen_log.warning(f'学号 {stuid} ,通过移动端删除了自己信息')
    return "success", 200


@app.route('/photo/<stuid>', methods=['POST'])
def photo(stuid):
    vc_path = f'{stuid}_img.png'
    random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
    return render_template('photo.html', img_src=vc_path, random=random_str)


def daka_worker(stuid):
    # print("打卡中", stuid)
    student = userdb.db_get_user_by_stuid(stuid)
    config = userdb.db_get_user_config(stuid)
    # time.sleep(11)
    # print("打卡成功", stuid)
    dakala(student, config)


@app.route('/daka/nophoto/<stuid>', methods=['POST'])
def dakanophoto(stuid):
    t_pool.submit(daka_worker, stuid)
    # t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    # t1.start()
    gen_log.info(f'学号 {stuid},执行了手动打卡')
    return "打卡成功", 200


@app.route('/api/daka/nophoto/<stuid>', methods=['POST'])
def api_dakanophoto(stuid):
    """
    api 接口
    :param stuid: 学号
    :return:
    """
    # t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    # t1.start()
    t_pool.submit(daka_worker, stuid)
    gen_log.info(f'学号 {stuid},执行了手动打卡')
    return "打卡成功", 200


@app.route('/daka/<stuid>', methods=['POST'])
def daka(stuid):
    gen_log.info(f'学号 {stuid},执行了手动打卡')
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    while t1.is_alive():
        time.sleep(1)
    return photo(stuid), 200


@scheduler.task(id="cycle_daka", trigger='cron', timezone='Asia/Shanghai', day_of_week='0-6', hour=7, minute=1)
# @app.route('/admin/daka/all',methods=['GET'])
def cycle_daka():
    gen_log.info("今日批量打卡开始执行")
    mylist = userdb.find_all_user()
    for stu in mylist:
        t_pool.submit(daka_worker, stu['stuid'])
        # t_pool.submit(daka_worker, stu['stuid'])
        # _t = threading.Thread(target=daka_worker, args=(stu['stuid'],), daemon=True)
        # _t.start()
    #  return "daka成公",200


if __name__ == '__main__':
    scheduler.start()
    http_server.listen(5000, "0.0.0.0")

    IOLoop.instance().start()

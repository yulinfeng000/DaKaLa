import random
import string
from logsetting import gen_log  # 不能删！！
import time
from flask import Flask, request, render_template, Response, redirect
import userdb
from daka import dakala
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask_apscheduler import APScheduler
from concurrent.futures import ThreadPoolExecutor
import os
from datetime import timedelta
import datetime

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
    user_ip = request.remote_addr
    cok = request.cookies
    print(user_ip)
    stuid = cok.get("stuid")
    cok_password = cok.get('password')
    if stuid is None:
        return render_template('index.html')

    _target_user = userdb.db_get_user_by_stuid(stuid)
    if _target_user is None:
        resp = Response(render_template('index.html'))
        resp.delete_cookie("stuid")
        resp.delete_cookie("password")
        return resp

    if _target_user['password'] != cok_password:
        resp = Response(render_template('index.html'))
        resp.delete_cookie("stuid")
        resp.delete_cookie("password")
        return render_template('index.html')

    _last_ip = userdb.db_get_user_last_ip(stuid)

    if _last_ip is not None:  # 如果你以前登录过
        if _last_ip != user_ip:  # 如果异地登录
            resp = Response(render_template('index.html'))
            resp.delete_cookie("stuid")
            resp.delete_cookie("password")
            return resp

    # 续费cookie
    ck_info = userdb.db_get_dk_callback_info(stuid)
    if ck_info is None:
        ck_info = "还没在服务器上打过卡呢"
    stu_config = userdb.db_get_user_config(stuid)
    resp = Response(render_template('info.html', stuid=stuid, callback=ck_info, config=stu_config))
    resp.set_cookie("stuid", stuid, max_age=60 * 60 * 24 * 7)
    resp.set_cookie("password", cok_password, max_age=60 * 60 * 24 * 7)
    return resp


@app.route("/updateconfig", methods=['POST'])
def updateConfig():
    required = ['stuid', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.form
    if not all(k in values for k in required):
        resp = Response('有必要信息未填写')
        resp.status_code = 403
        return resp

    stuid = values.get('stuid')
    config = {
        'homeStatus': values.get('homeStatus'),
        'livingStatus': values.get('livingStatus'),
        'healthStatus': values.get('healthStatus'),
        'workingPlace': values.get('workingPlace'),
        'cityStatus': values.get('cityStatus')
    }
    userdb.db_put_user_config(stuid, config)
    return redirect("/")


@app.route('/api/register', methods=['POST'])
def api_register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.json

    if not all(k in values for k in required):
        resp = Response('有必要信息未填写')
        resp.status_code = 403
        return resp
    password = values.get('password')
    stuid = values.get('stuid')
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
    return ck_info, 200


@app.route('/login', methods=['POST'])
def login():
    required = ['stuid', 'password']
    values = request.form
    if not all(k in values for k in required):
        return redirect("/")

    stuid = values.get('stuid')
    input_password = values.get('password')
    _target_user = userdb.db_get_user_by_stuid(stuid)
    if _target_user is None:
        return redirect("/")

    if _target_user['password'] != input_password:
        return redirect("/")

    ck_info = userdb.db_get_dk_callback_info(stuid)
    if ck_info is None:
        ck_info = "还没在服务器上打过卡呢"

    user_ip = request.remote_addr
    userdb.db_put_user_ip(stuid, user_ip)  # 更新你的上次登录ip
    stu_config = userdb.db_get_user_config(stuid)
    resp = Response(render_template('info.html', stuid=stuid, callback=ck_info, config=stu_config))
    resp.set_cookie("stuid", stuid, max_age=60 * 60 * 24 * 7)
    resp.set_cookie('password', input_password)
    return resp


@app.route('/goregister', methods=['GET', 'POST'])
def go_register():
    return render_template('register.html')


@app.route("/register", methods=['POST'])
def do_register():
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
    gen_log.info(f"学号 {stuid} , 浏览器注册成功,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    return resp


@app.route('/quit', methods=['POST'])
def quit():
    required = ['stuid']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    cok = request.cookies
    stuid = cok.get("stuid")
    # cok_password = cok.get('password')
    resp = Response(render_template("quit.html"))
    resp.delete_cookie("stuid")
    resp.delete_cookie("password")
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
    gen_log.warning(f"学号 {stuid} ,通过浏览器删除了自己信息,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
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
    gen_log.info(f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
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
    gen_log.info(f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    return "打卡成功", 200


@app.route('/daka/<stuid>', methods=['POST'])
def daka(stuid):
    gen_log.info(f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    task = t_pool.submit(daka_worker, stuid)
    while not task.done():
        time.sleep(1)
    """
    放弃独立线程，交给线程池执行
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    while t1.is_alive():
        time.sleep(1)
    """
    return photo(stuid), 200


@scheduler.task(id="cycle_daka", trigger='cron', timezone='Asia/Shanghai', day_of_week='0-6', hour=8, minute=10)
def cycle_daka():
    gen_log.info(f"今日批量打卡开始执行,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    mylist = userdb.find_all_user()
    for stu in mylist:
        t_pool.submit(daka_worker, stu['stuid'])
        # t_pool.submit(daka_worker, stu['stuid'])
        # _t = threading.Thread(target=daka_worker, args=(stu['stuid'],), daemon=True)
        # _t.start()
    #  return "daka成公",200


@app.route('/admin/daka/all', methods=['GET'])
def admin_command_daka():
    gen_log.info(f'超级管理员手动全局打卡执行，时间为{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    supercode = request.values.get("supercode")
    if supercode is None:
        return "YOU DONT CONFIG SUPER DAKA COMMAND!", 404
    __APP_SUPER_CODE = os.getenv("SUPER_CODE")
    # print(__APP_SUPER_CODE)
    if supercode == __APP_SUPER_CODE:
        mylist = userdb.find_all_user()
        for stu in mylist:
            t_pool.submit(daka_worker, stu['stuid'])
        return "SUPER COMMAND EXEC SUCCESS !"
    return "Permission Error!"


if __name__ == '__main__':
    scheduler.start()
    http_server.listen(5000, "0.0.0.0")
    IOLoop.instance().start()

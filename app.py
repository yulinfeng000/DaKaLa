import os
import random
import string
import time
from concurrent.futures.process import ProcessPoolExecutor

from flask import Flask, request, render_template, Response, redirect
import userdb
from daka import dakala
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from flask_apscheduler import APScheduler
from datetime import timedelta
import datetime
from logsetting import logger

app = Flask(__name__, static_folder=os.path.abspath('./static/'))
app_logger = logger

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=5)
scheduler = APScheduler(app=app)
http_server = HTTPServer(WSGIContainer(app), xheaders=True)

thread_executor = ProcessPoolExecutor(max_workers=3)


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
    resp = Response(render_template('info.html', stuid=stuid,
                                    callback=ck_info, config=stu_config))
    resp.set_cookie("stuid", stuid, max_age=60 * 60 * 24 * 7)
    resp.set_cookie("password", cok_password, max_age=60 * 60 * 24 * 7)
    return resp


@app.route("/updateconfig", methods=['POST'])
def updateConfig():
    required = [
        'stuid', 'cityStatus', 'workingPlace', 'healthStatus',
        'livingStatus', 'homeStatus', 'application_location',
        'application_reason', 'application_start_time',
        'application_start_day', 'application_end_day',
        'application_end_time', "scheduler_time_segment",
        "scheduler_start_time"
    ]
    values = request.form
    print(values)
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
        'cityStatus': values.get('cityStatus'),
        'application_location': values.get('application_location'),
        'application_reason': values.get('application_reason'),
        'application_start_time': values.get('application_start_time') if values.get('application_start_time') != 'None'
        else None,
        'application_start_day': values.get('application_start_day') if values.get('application_start_day') != 'None'
        else None,
        'application_end_day': values.get('application_end_day') if values.get('application_end_day') != 'None'
        else None,
        'application_end_time': values.get('application_end_time') if values.get('application_end_time') != 'None'
        else None,
        "scheduler_time_segment": values.get("scheduler_time_segment") if values.get('scheduler_time_segment') != ''
        else None,
        "scheduler_start_time": values.get("scheduler_start_time") if values.get("scheduler_start_time") != ''
        else None,
    }

    userdb.db_put_user_config(stuid, config)
    return redirect("/")


@app.route('/api/register', methods=['POST'])
def api_register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace',
                'healthStatus', 'livingStatus', 'homeStatus']
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
        'cityStatus': values.get('cityStatus'),
    }
    userdb.db_put_user_info(stuid, password)
    userdb.db_put_user_config(stuid, config)

    resp = Response('成功', 200)
    app_logger.info(f'学号 {stuid} , 移动端注册成功')
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
    resp = Response(render_template('info.html', stuid=stuid,
                                    callback=ck_info, config=stu_config))
    resp.set_cookie("stuid", stuid, max_age=60 * 60 * 24 * 7)
    resp.set_cookie('password', input_password)
    return resp


@app.route('/goregister', methods=['GET', 'POST'])
def go_register():
    return render_template('register.html')


@app.route("/register", methods=['POST'])
def do_register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace',
                'healthStatus', 'livingStatus', 'homeStatus']
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
    app_logger.info(
        f"学号 {stuid} , 浏览器注册成功,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
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
    app_logger.warning(
        f"学号 {stuid} ,通过浏览器删除了自己信息,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    return resp, 200


@app.route('/api/delete/<stuid>', methods=['POST'])
def api_del_info(stuid):
    userdb.db_delete_user_info(stuid)
    stu_img_path = os.path.abspath(f'./static/vc_images/{stuid}_img.png')
    if os.path.exists(stu_img_path):
        os.remove(stu_img_path)
    app_logger.warning(f'学号 {stuid} ,通过移动端删除了自己信息')
    return "success", 200


@app.route('/photo/<stuid>', methods=['POST'])
def photo(stuid):
    vc_path = f'{stuid}_img.png'
    random_str = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(3))
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
    import threading
    # t_pool = ThreadPoolExecutor(2)  # 别设置太大，打卡很要求性能，同时执行太多会顶不住
    # t_pool.submit(daka_worker, stuid)
    thread_executor.submit(daka_worker, stuid)
    app_logger.info(
        f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    return render_template("dakasucess.html")


@app.route('/api/daka/nophoto/<stuid>', methods=['POST', 'PUT'])
def api_dakanophoto(stuid):
    """
    api 接口
    :param stuid: 学号
    :return:
    """
    # t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    # t1.start()
    app_logger.info(
        f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    with ProcessPoolExecutor(max_workers=1) as executor:
        executor.submit(daka_worker, stuid)
    return "打卡成功", 200


@app.route('/daka/<stuid>', methods=['POST', 'PUT'])
def daka(stuid):
    app_logger.info(
        f"学号 {stuid},执行了手动打卡,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")

    task = thread_executor.submit(daka_worker, stuid)
    while not task.done():
        time.sleep(1)
    return photo(stuid), 200


@scheduler.task(id="cycle_daka", trigger='cron', timezone='Asia/Shanghai', day_of_week='0-6', hour=8, minute=10)
def cycle_daka():
    from concurrent.futures import ThreadPoolExecutor
    app_logger.info(
        f"今日批量打卡开始执行,时间为{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    mylist = userdb.find_all_user()

    for stu in mylist:
        thread_executor.submit(daka_worker, stu['stuid'])

    return "success"


@app.route('/admin/daka/all', methods=['GET'])
def admin_command_daka():
    app_logger.info(
        f'超级管理员手动全局打卡执行，时间为{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    supercode = request.values.get("supercode")
    if supercode is None:
        return "YOU DONT CONFIG SUPER DAKA COMMAND!", 404
    __APP_SUPER_CODE = os.getenv("SUPER_CODE")
    # print(__APP_SUPER_CODE)
    if supercode == __APP_SUPER_CODE:
        mylist = userdb.find_all_user()
        for stu in mylist:
            thread_executor.submit(daka_worker, stu['stuid'])
        return "SUPER COMMAND EXEC SUCCESS !"
    return "Permission Error!"


# @app.route('/admin/daka/clean/exectime', methods=['GET'])
def admin_command_clean_last_exec_time():
    app_logger.info(
        f'超级管理员手动清除上次打卡时间执行，时间为{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    supercode = request.values.get("supercode")
    if supercode is None:
        return "YOU DONT CONFIG SUPER DAKA COMMAND!", 404
    __APP_SUPER_CODE = os.getenv("SUPER_CODE")
    # print(__APP_SUPER_CODE)
    if supercode == __APP_SUPER_CODE:
        userdb.clean_all_user_last_scheduler_exec_time()
        return "SUPER COMMAND EXEC SUCCESS !"
    return "Permission Error!"


if __name__ == '__main__':
    from multiprocessing import cpu_count
    import tornado.ioloop

    scheduler.start()
    http_server.bind(5000, "0.0.0.0")

    http_server.start(cpu_count(), max_restarts=5)
    tornado.ioloop.IOLoop.current().start()
    # app.run("0.0.0.0", 5000,debug=False)

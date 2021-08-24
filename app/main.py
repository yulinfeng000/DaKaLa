from datetime import timedelta, datetime
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler

import os
import logging
from flask_jwt_extended.utils import create_access_token
from werkzeug.security import safe_str_cmp
import fcntl
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, send_file, jsonify
from flask_jwt_extended import JWTManager, jwt_required, current_user
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import atexit
from flask_cors import CORS
from app.service.daka import dakala
from app.service.record import dkrecords
from app.config import APP_ADMIN_KEY, APP_SECRET_KEY
import app.userdb as userdb


app = Flask(__name__)

jwt = JWTManager(app)


@jwt.user_lookup_loader
def user_lookup(header, data):
    stuid = data["sub"]
    return userdb.db_get_user_by_stuid(stuid)


# gunicorn logger intergation
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

CORS(app, resources={r"/*": {"origins": "*"}})

# jwt auth init
app.config["JWT_SECRET_KEY"] = APP_SECRET_KEY  # jwt secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)  # jwt expire time
# jsonify config
app.config["JSON_AS_ASCII"] = False

scheduler = APScheduler(scheduler=GeventScheduler())

# thread_pool
thread_pool = ThreadPoolExecutor(os.cpu_count() + 2)

# scheduler init
JOBS_STORE_LOCATION = os.path.abspath("./data/db/job.db")
app.logger.info(f"定时任务文件位置: {JOBS_STORE_LOCATION}")


class SchedulerConfig:
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url=f"sqlite:///{JOBS_STORE_LOCATION}")
    }
    SCHEDULER_TIMEZONE = "Asia/Shanghai"


app.config.from_object(SchedulerConfig())


SCHEDULE_LOCK_FILE = os.path.abspath("./data/db/schedule.lock")
app.logger.info(f"锁文件位置: {SCHEDULE_LOCK_FILE}")


def register():
    f = open(SCHEDULE_LOCK_FILE, "wb")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info("定时任务启动")
    except:
        pass

    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

    atexit.register(unlock)


register()


@app.route("/stu/login", methods=["POST"])
def user_login():
    rf = request.json
    stuid = rf.get("stuid", None)
    password = rf.get("password", None)
    if not stuid or not password:
        return jsonify({"msg": "用户名或密码错误", "code": 403})
    stu = userdb.db_get_user_by_stuid(stuid)
    if not stu:
        return jsonify({"msg": "用户名或密码错误", "code": 403})
    if not safe_str_cmp(stu["password"], password):
        return jsonify({"msg": "用户名或密码错误", "code": 403})
    token = create_access_token(identity=stuid)
    config = userdb.db_get_user_config(stuid)
    trigger = userdb.db_get_user_daka_trigger(stuid)
    if trigger is None:
        trigger = True
    ck_info = userdb.db_get_dk_callback_info(stuid)
    return jsonify(
        {
            "msg": "登录成功",
            "code": 200,
            "trigger": trigger,
            "ck": ck_info,
            "token": token,
            "stuid": stuid,
            "config": config,
        }
    )


@app.route("/stu/register", methods=["POST"])
def user_register():
    rf = request.json
    required = [
        "stuid",
        "password",
        "cityStatus",
        "workingPlace",
        "healthStatus",
        "livingStatus",
        "homeStatus",
    ]
    if not rf or not all(k in rf for k in required):
        return jsonify({"msg": "必要信息未填写", "code": 403})
    password = rf.get("password", None)
    stuid = rf.get("stuid", None)
    if not stuid.strip() or not password.strip():
        return jsonify({"msg": "学号或密码不正确", "code": 403})
    if len(stuid) < 10:
        return jsonify({"msg": "学号长度不正确", "code": 403})
    if userdb.db_get_user_by_stuid(stuid):
        return jsonify({"msg": "已经被注册", "code": 403})

    config = {
        "homeStatus": rf.get("homeStatus", None),
        "livingStatus": rf.get("livingStatus", None),
        "healthStatus": rf.get("healthStatus", None),
        "workingPlace": rf.get("workingPlace", None),
        "cityStatus": rf.get("cityStatus", None),
        "application_location": rf.get("application_location", None),
        "application_reason": rf.get("application_reason", None),
        "application_start_time": rf.get("application_start_time", None),
        "application_start_day": rf.get("application_start_day", None),
        "application_end_day": rf.get("application_end_day", None),
        "application_end_time": rf.get("application_end_time", None),
        "scheduler_time_segment": rf.get("scheduler_time_segment", None),
        "scheduler_start_time": rf.get("scheduler_start_time", None),
    }
    userdb.db_put_user_info(stuid, password)
    userdb.db_put_user_config(stuid, config)

    app.logger.info(f"学号 {stuid} , 移动端注册成功")
    return jsonify({"msg": "注册成功", "code": 200})


@app.route("/stu/<stuid>/info", methods=["GET"])
@jwt_required()
def user_info(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    stu_config = userdb.db_get_user_config(stuid)
    trigger = userdb.db_get_user_daka_trigger(stuid)
    ck_info = userdb.db_get_dk_callback_info(stuid)
    if trigger is None:
        trigger = True
    return jsonify(
        {
            "stuid": stuid,
            "trigger": trigger,
            "ck": ck_info,
            "config": stu_config,
            "code": 200,
        }
    )


@app.route("/stu/<stuid>/daka", methods=["POST"])
@jwt_required()
def user_daka(stuid):
    app.logger.debug(stuid)
    app.logger.debug(current_user["stuid"])
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    app.logger.info(
        f"学号 {stuid},执行了手动打卡,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}"
    )
    student = userdb.db_get_user_by_stuid(stuid)
    config = userdb.db_get_user_config(stuid)
    thread_pool.submit(daka_task, student, config)
    return jsonify({"msg": "打卡命令执行成功", "code": 200})


@app.route("/stu/<stuid>/info/update", methods=["POST"])
@jwt_required()
def update_config(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    required = ["stuid"]
    rf = request.json
    if not rf or not all(k in rf for k in required):
        return jsonify({"msg": "必要信息缺失", "code": 403})
    origin_conf = userdb.db_get_user_config(rf.get("stuid"))

    config = {
        "homeStatus": rf.get("homeStatus", origin_conf["homeStatus"]),
        "livingStatus": rf.get("livingStatus", origin_conf["livingStatus"]),
        "healthStatus": rf.get("healthStatus", origin_conf["healthStatus"]),
        "workingPlace": rf.get("workingPlace", origin_conf["workingPlace"]),
        "cityStatus": rf.get("cityStatus", origin_conf["cityStatus"]),
        "application_location": rf.get(
            "application_location", origin_conf["application_location"]
        ),
        "application_reason": rf.get(
            "application_reason", origin_conf["application_reason"]
        ),
        "application_start_time": rf.get(
            "application_start_time", origin_conf["application_start_time"]
        ),
        "application_start_day": rf.get(
            "application_start_day", origin_conf["application_start_day"]
        ),
        "application_end_day": rf.get(
            "application_end_day", origin_conf["application_end_day"]
        ),
        "application_end_time": rf.get(
            "application_end_time", origin_conf["application_end_time"]
        ),
        "scheduler_time_segment": rf.get(
            "scheduler_time_segment", origin_conf["scheduler_time_segment"]
        ),
        "scheduler_start_time": rf.get(
            "scheduler_start_time", origin_conf["scheduler_start_time"]
        ),
    }
    userdb.db_put_user_config(stuid, config)

    if rf.get("password", None):
        userdb.db_put_user_info(stuid, rf.get("password"))

    return jsonify({"msg": "更新成功", "config ": config, "code": 200})


@app.route("/stu/<stuid>/photo", methods=["GET"])
@jwt_required()
def user_photo(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    pic_path = os.path.abspath(f"./data/pic/{stuid}_img.png")
    if os.path.exists(pic_path):
        return send_file(pic_path)
    return bytes(0)


@app.route("/stu/<stuid>/callback", methods=["GET"])
@jwt_required()
def user_callback(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    ck_info = userdb.db_get_dk_callback_info(stuid)
    return jsonify({"ck": ck_info, "code": 200})


@app.route("/stu/<stuid>/del", methods=["POST"])
@jwt_required()
def user_del(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    userdb.db_delete_user_info(stuid)
    pic_path = os.path.abspath(f"./data/pic/{stuid}_img.png")
    if os.path.exists(pic_path):
        os.remove(pic_path)
    return jsonify({"msg": "删除成功", "code": 401})


@app.route("/stu/<stuid>/dakatrigger/update", methods=["POST"])
@jwt_required()
def trigger_daka_update(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    rf = request.json
    required = ["daka_trigger"]
    if not rf or not all(k in rf for k in required):
        return jsonify({"msg": "必要信息缺失", "code": 403})
    trigger = rf.get("daka_trigger", True)
    userdb.db_put_user_daka_trigger(stuid, trigger)
    return jsonify({"msg": "更新成功", "code": 200, "trigger": trigger})


@app.route("/stu/<stuid>/dakatrigger/info", methods=["GET"])
@jwt_required()
def daka_trigger_info(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    flag = userdb.db_get_user_daka_trigger(stuid)
    if flag is None:
        # 默认trigger开启
        flag = True
    return jsonify({"msg": "查询成功", "code": 200, "trigger": flag})


@app.route("/stu/<stuid>/dkrecords/info", methods=["GET"])
@jwt_required()
def get_dk_record(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    combo = userdb.db_get_user_daka_combo(stuid)
    records = userdb.db_get_user_daka_records(stuid)
    return jsonify({"msg": "查询成功", "code": 200, "combo": combo, "records": records})


@app.route("/stu/<stuid>/dkrecords/reflush", methods=["POST"])
@jwt_required()
def reflush_dk_record(stuid):
    if not safe_str_cmp(stuid, current_user["stuid"]):
        return jsonify({"msg": "不允许访问", "code": 401})
    lasttime = userdb.db_get_user_relfush_daka_record_time(stuid)
    combo = userdb.db_get_user_daka_combo(stuid)
    records = userdb.db_get_user_daka_records(stuid)
    if lasttime + 60 > int(datetime.now().timestamp()):
        return jsonify({"msg": "刷新成功", "code": 200, "records": records, "combo": combo})
    student = userdb.db_get_user_by_stuid(stuid)
    userdb.db_put_user_reflush_daka_record_time(stuid, datetime.now())
    thread_pool.submit(dkrecords, student)
    return jsonify({"msg": "刷新成功", "code": 200, "records": records, "combo": combo})


@app.route("/admin/daka/all", methods=["GET"])
def admin_daka_for_all():
    supercode = request.args.get("supercode", None)
    if not supercode:
        return jsonify({"msg": "缺少参数", "code": 403})
    if not APP_ADMIN_KEY:
        return jsonify({"msg": "拒绝访问", "code": 403})
    if not safe_str_cmp(supercode, APP_ADMIN_KEY):
        return jsonify({"msg": "拒绝访问", "code": 401})
    app.logger.info(f'admin daka exec {datetime.now().strftime("%Y/%m/%d")}')
    thread_pool.submit(daka_worker)
    return jsonify({"msg": "执行成功", "code": 200})


def daka_task(student, config):
    dakala(student, config)
    dkrecords(student)
    userdb.db_put_user_reflush_daka_record_time(student["stuid"], datetime.now())


def daka_worker():
    all_stu = userdb.find_all_user()
    for stu in all_stu:
        trigger = userdb.db_get_user_daka_trigger(stu["stuid"])
        if trigger is None or trigger is True:
            config = userdb.db_get_user_config(stu["stuid"])
            thread_pool.submit(daka_task, stu, config)
        else:
            sid = stu["stuid"]
            userdb.db_put_dk_callback_info(
                sid, f'{datetime.now().strftime("%Y/%m/%d")} 已暂停打卡'
            )
            app.logger.info(f"{sid} 关闭了每日打卡")


@scheduler.task(
    "cron",
    id="interval_daka",
    timezone="Asia/Shanghai",
    day_of_week="0-6",
    hour=8,
    minute=10,
    misfire_grace_time=36000,
)
# @scheduler.task('cron', id="d", minute='*')  # for test
def interval_daka():
    app.logger.info(f'每日打卡任务执行 {datetime.now().strftime("%Y/%m/%d")}')
    thread_pool.submit(daka_worker)

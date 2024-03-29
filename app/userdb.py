from datetime import datetime
import json
import os
from typing import Dict, Optional
import plyvel
import logging
from app.lock import NamedAtomicLock

logger = logging.getLogger("gunicorn.error")

# 由于leveldb设计一次只能由一个线程访问，现设置访问锁
DB_ACC_LOCK = NamedAtomicLock("leveldbAccessLock")

DB_LOCATION = os.path.abspath("./data/db")
logger.info(f"db文件地址：{DB_LOCATION}")

STUDENT_TABLE = "STUDENT_"
STUDENT_CONFIG_TABLE = "CONFIG_TABLE_"
DAKA_CALLBACK_INFO = "DAKA_CALLBACK_INFO_"
USER_IP = "USER_IP_"
LAST_SCHEDULER_EXEC_TIME = "LAST_SCHEDULER_EXEC_TIME_"
APSC = "APSC_"
DAKA_TRIGGER = "DAKA_TRIGGER_"
DAKA_COMBO = "DAKA_COMBO_"
DAKA_RECORDS = "DAKA_RECORDS_"
LAST_DAKA_REFLUSH_RECORDS_TIME = "LAST_DAKA_REFLUSH_RECORDS_TIME_"
QMSG_CHAN_KEY = "QMSG_KEY_"
SERVER_CHAN_KEY = "SERVER_CHAN_KEY_"
USER_EMAIL = "USER_EMAIL_"
PUSH_TYPE = "PUSH_TYPE_"


class DBA:
    def __enter__(self) -> plyvel.DB:
        DB_ACC_LOCK.acquire(timeout=15)
        self.db = plyvel.DB(DB_LOCATION, create_if_missing=True)
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.db.close()
        finally:
            DB_ACC_LOCK.release()


dba = DBA()


def KEY(key):
    return bytes(key, encoding="utf-8")


def VALUE(value):
    return bytes(value, encoding="utf-8")


def delete(key):
    with dba as db:
        db.delete(KEY(key))


def get_object(key) -> Optional[Dict]:
    with dba as db:
        res = db.get(KEY(key))
        if res is None:
            return None
        return json.loads(res)


def put_object(key, value):
    with dba as db:
        db.put(KEY(key), VALUE(json.dumps(value, sort_keys=True, ensure_ascii=False)))


def put_value(key, value):
    if value is None:
        return  # 没法转换None
    with dba as db:
        db.put(KEY(key), VALUE(value))


def get_value(key):
    with dba as db:
        res = db.get(KEY(key))
        if res is None:
            return res
        return str(res, encoding="utf=8")


def db_put_user_info(stuid, password):
    put_object(f"{STUDENT_TABLE}{stuid}", {"stuid": stuid, "password": password})


def db_get_user_by_stuid(stuid: str) -> Dict:
    return get_object(f"{STUDENT_TABLE}{stuid}")


def db_put_user_config(stuid, conf: dict):
    put_object(f"{STUDENT_CONFIG_TABLE}{stuid}", conf)


def db_get_user_config(stuid) -> dict:
    return get_object(f"{STUDENT_CONFIG_TABLE}{stuid}")


def db_delete_user_info(stuid):
    delete(f"{STUDENT_TABLE}{stuid}")
    delete(f"{STUDENT_CONFIG_TABLE}{stuid}")


def db_put_dk_callback_info(stuid, info):
    put_value(f"{DAKA_CALLBACK_INFO}{stuid}", info)


def db_get_dk_callback_info(stuid):
    return get_value(f"{DAKA_CALLBACK_INFO}{stuid}")


def db_put_last_scheduler_exec_time(stuid, time: str):
    put_value(f"{LAST_SCHEDULER_EXEC_TIME}{stuid}", time)


def db_get_last_scheduler_exec_time(stuid):
    return get_value(f"{LAST_SCHEDULER_EXEC_TIME}{stuid}")


def find_all_user():
    with dba as db:
        with db.snapshot() as sp:
            with sp.iterator(prefix=KEY(f"{STUDENT_TABLE}")) as itor:
                res = [json.loads(v) for _, v in itor]
                return res


def db_put_user_ip(stuid, ip):
    put_value(f"{USER_IP}{stuid}", ip)


def db_get_user_last_ip(stuid):
    return get_value(f"{USER_IP}{stuid}")


def clean_all_user_last_scheduler_exec_time():
    with dba as db:
        with db.snapshot() as sp:
            with sp.iterator(prefix=KEY(f"{LAST_SCHEDULER_EXEC_TIME}")) as itor:
                for key in itor:
                    delete(key)


def db_get_user_daka_trigger(stuid):
    v = get_value(f"{DAKA_TRIGGER}{stuid}")
    if v is None or v == "True":
        return True
    else:
        return False


def db_put_user_daka_trigger(stuid, v):
    if v:
        put_value(f"{DAKA_TRIGGER}{stuid}", "True")
    else:
        put_value(f"{DAKA_TRIGGER}{stuid}", "False")


def db_put_user_daka_combo(stuid, count):
    put_value(f"{DAKA_COMBO}{stuid}", str(count))


def db_get_user_daka_combo(stuid):
    v = get_value(f"{DAKA_COMBO}{stuid}")
    if not v:
        return None
    return int(v)


def db_put_user_daka_records(stuid, records):
    put_object(f"{DAKA_RECORDS}{stuid}", records)


def db_get_user_daka_records(stuid):
    v = get_object(f"{DAKA_RECORDS}{stuid}")
    if not v:
        return []
    return v


def db_put_user_reflush_daka_record_time(stuid, time: datetime):
    put_value(f"{LAST_DAKA_REFLUSH_RECORDS_TIME}{stuid}", str(int(time.timestamp())))


def db_get_user_relfush_daka_record_time(stuid):
    v = get_value(f"{LAST_DAKA_REFLUSH_RECORDS_TIME}{stuid}")
    if not v:
        return 0
    return int(v)


def db_get_qmsg_key(stuid):
    return get_value(f"{QMSG_CHAN_KEY}{stuid}")


def db_put_qmsg_key(stuid, key):
    put_value(f"{QMSG_CHAN_KEY}{stuid}", key)


def db_put_server_chan_key(stuid, key):
    put_value(f"{SERVER_CHAN_KEY}{stuid}", key)


def db_get_server_chan_key(stuid):
    return get_value(f"{SERVER_CHAN_KEY}{stuid}")


def db_put_user_email(stuid, email):
    put_value(f"{USER_EMAIL}{stuid}", email)


def db_get_user_email(stuid):
    return get_value(f"{USER_EMAIL}{stuid}")


def db_put_push_type(stuid, tp):
    put_value(f"{PUSH_TYPE}{stuid}", tp)


def db_get_push_type(stuid):
    v = get_value(f"{PUSH_TYPE}{stuid}")
    if not v or v == "" or v == "None":
        return None
    return v


def db_get_push_key_by_type(stuid, ptype):
    if ptype == "qmsg":
        return db_get_qmsg_key(stuid)
    elif ptype == "serverchan":
        return db_get_server_chan_key(stuid)
    elif ptype == "email":
        return db_get_user_email(stuid)
    else:
        return None

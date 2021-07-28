import json
import os
from typing import Dict, Optional
import plyvel
import logging
from app.lock import NamedAtomicLock

logger = logging.getLogger('gunicorn.error')

# 由于leveldb设计一次只能由一个线程访问，现设置访问锁
DB_ACC_LOCK = NamedAtomicLock('leveldbAccessLock')

DB_LOCATION = os.path.abspath("./data/db")
logger.info(f"db文件地址：{DB_LOCATION}")
STUDENT_TABLE = "STUDENT_"
STUDENT_CONFIG_TABLE = "CONFIG_TABLE_"
DAKA_CALLBACK_INFO = "DAKA_CALLBACK_INFO_"
USER_IP = "USER_IP_"
LAST_SCHEDULER_EXEC_TIME = "LAST_SCHEDULER_EXEC_TIME_"
APSC = "APSC_"
DAKA_TRIGGER = "DAKA_TRIGGER_"


class DBA():

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
    return bytes(key, encoding='utf-8')


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
        db.put(KEY(key), VALUE(json.dumps(
            value, sort_keys=True, ensure_ascii=False)))


def put_value(key, value):
    with dba as db:
        db.put(KEY(key), VALUE(value))


def get_value(key):
    with dba as db:
        res = db.get(KEY(key))
        if res is None:
            return res
        return str(res, encoding='utf=8')


def db_put_user_info(stuid, password):
    put_object(f'{STUDENT_TABLE}{stuid}', {
        'stuid': stuid,
        'password': password
    })


def db_get_user_by_stuid(stuid: str) -> Dict:
    return get_object(f'{STUDENT_TABLE}{stuid}')


def db_put_user_config(stuid, conf: dict):
    put_object(f'{STUDENT_CONFIG_TABLE}{stuid}', conf)


def db_get_user_config(stuid) -> dict:
    return get_object(f'{STUDENT_CONFIG_TABLE}{stuid}')


def db_delete_user_info(stuid):
    delete(f'{STUDENT_TABLE}{stuid}')
    delete(f'{STUDENT_CONFIG_TABLE}{stuid}')


def db_put_dk_callback_info(stuid, info):
    put_value(f'{DAKA_CALLBACK_INFO}{stuid}', info)


def db_get_dk_callback_info(stuid):
    return get_value(f'{DAKA_CALLBACK_INFO}{stuid}')


def db_put_last_scheduler_exec_time(stuid, time: str):
    put_value(f'{LAST_SCHEDULER_EXEC_TIME}{stuid}', time)


def db_get_last_scheduler_exec_time(stuid):
    return get_value(f'{LAST_SCHEDULER_EXEC_TIME}{stuid}')


def find_all_user():
    with dba as db:
        with db.snapshot() as sp:
            with sp.iterator(prefix=KEY(f'{STUDENT_TABLE}')) as itor:
                res = [json.loads(v) for _, v in itor]
                return res


def db_put_user_ip(stuid, ip):
    put_value(f'{USER_IP}{stuid}', ip)


def db_get_user_last_ip(stuid):
    return get_value(f'{USER_IP}{stuid}')


def clean_all_user_last_scheduler_exec_time():
    with dba as db:
        with db.snapshot() as sp:
            with sp.iterator(prefix=KEY(f'{LAST_SCHEDULER_EXEC_TIME}')) as itor:
                for key in itor:
                    delete(key)


def db_get_user_daka_trigger(stuid):
    v = get_value(f'{DAKA_TRIGGER}{stuid}')
    if v is None or v == "True":
        return True
    else:
        return False


def db_put_user_daka_trigger(stuid, v):
    if v:
        put_value(f'{DAKA_TRIGGER}{stuid}', "True")
    else:
        put_value(f'{DAKA_TRIGGER}{stuid}', "False")

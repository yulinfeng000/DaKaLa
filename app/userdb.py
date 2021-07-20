import json
import os
from typing import Dict, Optional
import plyvel
import logging
from apscheduler.jobstores.base import BaseJobStore
from apscheduler.job import Job

logger = logging.getLogger('gunicorn.error')

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
        self.db = plyvel.DB(DB_LOCATION, create_if_missing=True)
        # logger.debug("db connected")
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        # logger.debug("db exited")


def KEY(key):
    return bytes(key, encoding='utf-8')


def VALUE(value):
    return bytes(value, encoding="utf-8")


def delete(key):
    with DBA() as db:
        db.delete(KEY(key))


def get_object(key) -> Optional[Dict]:
    with DBA() as db:
        res = db.get(KEY(key))
        if res is None:
            return None
        return json.loads(res)


def put_object(key, value):
    with DBA() as db:
        db.put(KEY(key), VALUE(json.dumps(value, sort_keys=True)))


def put_value(key, value):
    with DBA() as db:
        db.put(KEY(key), VALUE(value))


def get_value(key):
    with DBA() as db:
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
    with DBA() as db:
        itor = db.iterator(prefix=KEY(f'{STUDENT_TABLE}'))
        res = [json.loads(v) for _, v in itor]
        return res


def db_put_user_ip(stuid, ip):
    put_value(f'{USER_IP}{stuid}', ip)


def db_get_user_last_ip(stuid):
    return get_value(f'{USER_IP}{stuid}')


def clean_all_user_last_scheduler_exec_time():
    with DBA() as db:
        itor = db.iterator(prefix=KEY(f'{LAST_SCHEDULER_EXEC_TIME}'))
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


class LevelDBJobStore(BaseJobStore):
    def __init__(self) -> None:
        super().__init__()

    def add_job(self, job: Job):
        put_object(f"{APSC}{job.id}", job)

    def get_all_jobs(self):
        with DBA() as db:
            res = []
            itor = db.iterator(prefix=KEY(f'{APSC}'))
            for key, value in itor:
                res.append(value)
            return res

    def lookup_job(self, job_id):
        return get_object(job_id)

    def remove_all_jobs(self):
        with DBA() as db:
            itor = db.iterator(prefix=KEY(f'{APSC}'))
            for key in itor:
                delete(key)

    def remove_job(self, job_id):
        delete(job_id)

    def update_job(self, job):
        put_object(f"{APSC}{job.id}", job)

    def get_due_jobs(self, now):
        from operator import attrgetter
        jobs = self.get_all_jobs()
        sorted(jobs, key=attrgetter('next_run_time'))

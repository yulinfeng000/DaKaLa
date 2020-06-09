import json

import plyvel
from os import path

STUDENT_TABLE = "STUDENT_"
STUDENT_CONFIG_TABLE = "CONFIG_TABLE_"
DAKA_CALLBACK_INFO = "DAKA_CALLBACK_INFO_"
STUDENT_QQ_TABLE = 'STUDENT_QQ_'

DB_LOCATION = path.join(path.dirname(__file__), "static", "db")
db = plyvel.DB(DB_LOCATION, create_if_missing=True)


def KEY(key):
    return bytes(key, encoding='utf-8')


def VALUE(value):
    return bytes(value, encoding="utf-8")


def delete(key):
    db.delete(KEY(key))


def get_object(key):
    res = db.get(KEY(key))
    if res is None:
        return None
    return json.loads(res)


def put_object(key, value):
    db.put(KEY(key), VALUE(json.dumps(value, sort_keys=True)))


def put_value(key, value):
    db.put(KEY(key), VALUE(value))


def get_value(key):
    res = db.get(KEY(key))
    if res is None:
        return res
    return str(res, encoding='utf=8')


def db_put_user_info(stuid, password):
    put_object(f'{STUDENT_TABLE}{stuid}', {
        'stuid': stuid,
        'password': password
    })


def db_get_user_by_stuid(stuid):
    return get_object(f'{STUDENT_TABLE}{stuid}')


def db_put_user_config(stuid, conf):
    put_object(f'{STUDENT_CONFIG_TABLE}{stuid}', conf)


def db_get_user_config(stuid):
    return get_object(f'{STUDENT_CONFIG_TABLE}{stuid}')


def db_delete_user_info(stuid):
    delete(f'{STUDENT_TABLE}{stuid}')
    delete(f'{STUDENT_CONFIG_TABLE}{stuid}')


def db_put_dk_callback_info(stuid, info):
    put_value(f'{DAKA_CALLBACK_INFO}{stuid}', info)


def db_get_dk_callback_info(stuid):
    return get_value(f'{DAKA_CALLBACK_INFO}{stuid}')


def db_put_user_qq_id(qqid, stuinfo):
    put_object(f'{STUDENT_QQ_TABLE}{qqid}', {
        'stuid': stuinfo[0],
        'password': stuinfo[1]
    })


def db_get_user_qq_id(qqid):
    return get_object(f'{STUDENT_QQ_TABLE}{qqid}')


def db_delete_user_qq_id(qqid):
    return delete(f'{STUDENT_QQ_TABLE},{qqid}')


def find_all_user():
    itor = db.iterator(prefix=KEY(f'{STUDENT_TABLE}'))
    res = []
    for key, value in itor:
        res.append(json.loads(value))
    return res


if __name__ == '__main__':
    print(find_all_user())
    print(db_get_user_config('123456'))

import logging
from urllib import request, parse
from app import userdb

logger = logging.getLogger("gunicorn.error")


def push_qmsg(key, msg):
    req = request.Request(f"https://qmsg.zendee.cn/send/{key}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.urlopen(req, parse.urlencode({"msg": msg}).encode("utf-8"))


def push_serverchan(key, msg):
    req = request.Request(
        f'https://sctapi.ftqq.com/{key}.send?title={parse.quote("打卡异常推送")}&desp={parse.quote(msg)}'
    )
    request.urlopen(req)


def push_email(email, msg):
    pass


def push_msg_to_user(stuid, msg):
    ptype = userdb.db_get_push_type(stuid)
    if not ptype:
        logger.info(f"{stuid} 打卡异常推送失败,没有配置推送")
        return

    if ptype == "qmsg":
        key = userdb.db_get_qmsg_key(stuid)
        if not key:
            logger.info(f"{stuid} 打卡异常推送失败,没有配置 qmsg key")
            return
        push_qmsg(key, msg)
    elif ptype == "serverchan":
        key = userdb.db_get_server_chan_key(stuid)
        if not key:
            logger.info(f"{stuid} 打卡异常推送失败,没有配置 serverchan key")
            return
        push_serverchan(key, msg)
    elif ptype == "email":
        email = userdb.db_get_user_email(stuid)
        if not email:
            logger.info(f"{stuid} 打卡异常推送失败,没有配置 email")
            return
        push_email(email, msg)
    else:
        logger.info(f"{stuid} 打卡异常推送失败,开启了推送但未正确设置推送参数")

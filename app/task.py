from datetime import datetime
from app.service.daka import dakala
from app.service.record import dkrecords
from app import userdb
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from app.main import app,thread_pool

scheduler = APScheduler(scheduler=GeventScheduler())

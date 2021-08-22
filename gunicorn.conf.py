import multiprocessing
import gevent.monkey

gevent.monkey.patch_all()
preload_app = True
bind = "0.0.0.0:8000"
worker_class = "gevent"
debug = False
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 1  # for dev
# reload = True

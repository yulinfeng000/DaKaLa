import multiprocessing
import gevent.monkey

gevent.monkey.patch_all()

workers = multiprocessing.cpu_count() * 2 + 1
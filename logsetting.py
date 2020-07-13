import logging
from tornado.log import gen_log, app_log, access_log
import os

log_file_path = os.path.abspath('./static/log/main.log')
logging.basicConfig(level=logging.INFO, filename=log_file_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
gen_log.addHandler(console_handler)
app_log.addHandler(console_handler)
access_log.addHandler(console_handler)

import logging
from tornado.log import gen_log
logging.basicConfig(level=logging.INFO, filename='./static/log/main.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
gen_log.addHandler(console_handler)
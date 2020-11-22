from loguru import logger
import os

logger.add(os.path.abspath("./data/log/main.log"), rotation="1 week", compression="zip", enqueue=True)

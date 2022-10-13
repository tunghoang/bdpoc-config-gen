import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", datefmt="%H:%M:%S", handlers=[RotatingFileHandler("logger.log", maxBytes=50000, backupCount=5)])

check_logger = logging.getLogger("check")

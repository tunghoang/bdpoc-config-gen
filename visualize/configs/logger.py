import logging
from logging.handlers import RotatingFileHandler

check_logger = logging.getLogger("check")
handler = RotatingFileHandler("logger.log", maxBytes=50000, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
check_logger.addHandler(handler)

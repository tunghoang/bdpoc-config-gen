import logging
import os
from logging.handlers import RotatingFileHandler

logFile = os.environ.get("CHECK_MACHINE") or 'logger.log'

check_logger = logging.getLogger(logFile)
handler = RotatingFileHandler(logFile, maxBytes=50000, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
if check_logger.hasHandlers():
  check_logger.handlers.clear()
check_logger.addHandler(handler)
check_logger.setLevel(logging.INFO)

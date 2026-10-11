import logging
import os
from app.utils.config import ROOT_DIR

LOG_DIR = os.path.join(ROOT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "application.log")

_listeners = []


def add_log_listener(fn):
    _listeners.append(fn)


class BroadcastHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        for fn in list(_listeners):
            try:
                fn(record.levelname, msg)
            except Exception:
                pass


def get_logger(name="deepsat"):
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    bh = BroadcastHandler()
    bh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(bh)

    return logger


log = get_logger()

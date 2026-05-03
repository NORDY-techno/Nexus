import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    l = logging.getLogger("Nexus")
    l.setLevel(logging.INFO)
    if l.hasHandlers(): l.handlers.clear()

    f = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    fh = RotatingFileHandler("nexus.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(f)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', '%H:%M:%S'))

    l.addHandler(fh)
    l.addHandler(ch)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    return l

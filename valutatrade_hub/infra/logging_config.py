import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "actions.log"

def setup_logging(level=logging.INFO):
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

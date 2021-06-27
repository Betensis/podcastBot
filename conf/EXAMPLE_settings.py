import os
from pathlib import Path

TELEGRAM_TOKEN = ""

# all file system files or dirs should and with _FILE or _DIR
# all file system variables should be instances of Path
BASE_DIR = Path(os.path.curdir).parent
LOG_DIR = BASE_DIR.joinpath("log")
MEDIA_DIR = BASE_DIR.joinpath("media")


LOGGING_SETTINGS = {
    "level": "DEBUG",
    "rotation": "100 MB",
    "serialize": True,
    "compression": "zip",
    "backtrace": True,
    "catch": True,
}

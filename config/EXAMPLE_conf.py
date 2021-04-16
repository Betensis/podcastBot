import os
from pathlib import Path

TELEGRAM_TOKEN = "Your tlg token"

BASE_DIR = Path(os.path.curdir).parent
LOG_DIR = BASE_DIR.joinpath("log")
MEDIA_DIR = BASE_DIR.joinpath("media")
LOGGING_LVL = "DEBUG"

# don't delete this!
MEDIA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

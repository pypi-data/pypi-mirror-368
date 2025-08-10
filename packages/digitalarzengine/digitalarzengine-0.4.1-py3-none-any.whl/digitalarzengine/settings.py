import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
DATA_DIR = os.path.join(BASE_DIR, 'data')
PAK_DATA_DIR= os.path.join(DATA_DIR, 'pak')
MRDA_DATA_DIR= os.path.join(DATA_DIR, 'mrda')
MEDIA_DIR = os.path.join(BASE_DIR, '../media')

local_data_dir = '/Users/atherashraf/Documents/data'

APP_NAME="DigitalArzEngine"
LOG_LEVEL="DEBUG"


env_path = os.path.join(CONFIG_DIR, ".env")
load_dotenv(env_path)

DATABASES = {
    "drm": {
        "ENGINE": "postgresql+psycopg2",
        "NAME": "drm",
        "USER": "dafast",
        "PASSWORD": "gAAAAABoQpUNv0nRVWIaukDZUYf2S2y1vSjJv_xTMp8GHgbrW2zc2gzjb9ls0HWLmNWWiafYabVCuGNsziooGU4xWCHu0VL3gw==",
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": "5432",
    }
}
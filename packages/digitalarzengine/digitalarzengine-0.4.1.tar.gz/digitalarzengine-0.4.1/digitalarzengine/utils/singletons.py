# dafastmap/utils/singletons.py
from digitalarzengine.settings import APP_NAME, LOG_LEVEL
from digitalarzengine.utils.loggers import DALogger

da_logger = DALogger(
    name=APP_NAME,
    min_level=LOG_LEVEL,
    log_to_file=True,
    log_file_path=f"{APP_NAME.lower()}.log"
)


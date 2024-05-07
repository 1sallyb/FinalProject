import logging
import os
from datetime import datetime

from from_root import from_root

LOG_FILE = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"

log_dir = 'logs'

full_log_path = os.path.join(from_root(), log_dir)

logs_path = os.path.join(full_log_path, LOG_FILE)

print(logs_path)

os.makedirs(full_log_path, exist_ok=True)

logging.basicConfig(
    filename = logs_path,
    level= logging.INFO,
    format = '[%(asctime)s] %(name)s%(levelname)s %(message)s',
    )
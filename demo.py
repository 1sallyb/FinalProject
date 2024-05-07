from final_project.logger import logging
from final_project.exception import final_except
import sys

logging.info("This is a logger test.")

try:
    a = 1/2

except Exception as e:
    logging.info(e)
    raise final_except(e,sys) from e


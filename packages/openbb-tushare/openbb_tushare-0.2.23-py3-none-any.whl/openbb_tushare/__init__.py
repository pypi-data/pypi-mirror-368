import logging
from mysharelib import get_project_name
from mysharelib.tools import setup_logger

project_name = __name__

setup_logger(project_name)
logger = logging.getLogger(project_name)

logger.info(f"Current openbb_tushare module name: {project_name}")

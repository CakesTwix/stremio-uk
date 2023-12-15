import glob
import importlib
from main import app
import logging

logger = logging.getLogger(__name__)

module_paths = glob.glob("parsers/**/api.py", recursive=True)
for module_path in module_paths:
    module_name = module_path.replace("/", ".")[:-3]
    logger.info(module_name)
    importlib.import_module(module_name)

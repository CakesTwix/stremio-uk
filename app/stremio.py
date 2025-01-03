import glob
import importlib
from app.main import app
import logging
import os

logger = logging.getLogger(__name__)

# Log the current working directory to verify correct path resolution
logger.info(f"Current working directory: {os.getcwd()}")

# Find all `api.py` modules inside `app/parsers`
module_paths = glob.glob("app/parsers/**/api.py", recursive=True)

# Import each found module
for module_path in module_paths:
    # Convert file path to module name (e.g., "app.parsers.module_name.api")
    module_name = module_path.replace("/", ".")[:-3]  # Remove `.py`
    logger.info(f"Importing module: {module_name}")
    importlib.import_module(module_name)

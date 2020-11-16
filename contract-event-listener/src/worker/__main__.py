import os  # pragma: no cover
from src.config import Config  # pragma: no cover
from . import Worker  # pragma: no cover

Worker(Config.from_file(os.environ['CONFIG_FILE'])).run()  # pragma: no cover

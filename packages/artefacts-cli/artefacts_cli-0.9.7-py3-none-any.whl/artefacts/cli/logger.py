import logging
import os
import sys

logger = logging.getLogger("artefacts")
if os.environ.get("ARTEFACTS_CLI_ENV") == "development":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


# INFO and WARNING messages go to stdout
class InfoWarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in [logging.INFO, logging.WARNING]


info_handler = logging.StreamHandler(stream=sys.stdout)
info_handler.setLevel(logging.INFO)
info_handler.addFilter(InfoWarningFilter())
info_handler.setFormatter(logging.Formatter("%(message)s"))

# ERROR and above go to stderr
error_handler = logging.StreamHandler(stream=sys.stderr)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.propagate = False

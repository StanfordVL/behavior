import logging

__version__ = "0.0.1"

log = logging.getLogger(__name__)
_LOG_LEVEL = os.environ.get("IG_LOG_LEVEL", "INFO").upper()
log.setLevel(level=_LOG_LEVEL)

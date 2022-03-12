import logging
import os

__version__ = "1.0.0"

log = logging.getLogger(__name__)
_LOG_LEVEL = os.environ.get("IG_LOG_LEVEL", "INFO").upper()
log.setLevel(level=_LOG_LEVEL)

examples_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "examples")
configs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs")

log.debug("Example path: {}".format(examples_path))
log.debug("Example config path: {}".format(configs_path))

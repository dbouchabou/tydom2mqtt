import logging
import logging.config

logging.config.fileConfig("logging.conf")
_LOGGER = logging.getLogger(__name__)

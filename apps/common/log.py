import logging
import traceback
import sys

logger = logging.getLogger(__name__)


def print(e, msg):
    logger.error(msg)
    logger.error(e.with_traceback(traceback.print_exc(file=sys.stdout)))

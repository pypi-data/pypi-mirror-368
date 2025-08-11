import logging

import pykka
from mopidy.core import CoreListener

from .mem import cranberry

# import logger
logger = logging.getLogger(__name__)


class CranberryFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        super().__init__()

        # Pass our Mopidy config and core to the CranberryCore instance
        cranberry.config = config
        cranberry.core = core

    def on_start(self):
        cranberry.start()

    def on_stop(self):
        cranberry.stop()

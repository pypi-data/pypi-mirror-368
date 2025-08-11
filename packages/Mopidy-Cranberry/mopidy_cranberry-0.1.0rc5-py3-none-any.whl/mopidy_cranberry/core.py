import json
import logging
import sys
import urllib

import pykka
from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient

from . import Extension

if sys.platform == "win32":
    pass

# import logger
logger = logging.getLogger(__name__)


class CranberryCore(pykka.ThreadingActor):
    version = ""

    def setup(self, config, core):
        self.config = config
        self.core = core

    ##
    # Mopidy server is starting
    ##
    def start(self):
        logger.info("Starting Cranberry " + Extension.version)

    ##
    # Mopidy is shutting down
    ##
    def stop(self):
        logger.info("Stopping Cranberry")

    ##
    # System controls
    #
    # Faciitates upgrades and configuration fetching
    ##

    async def get_version(self, *args, **kwargs):
        callback = kwargs.get("callback", False)
        url = "https://pypi.python.org/pypi/Mopidy-Cranberry/json"
        http_client = AsyncHTTPClient()

        try:
            http_response = await http_client.fetch(url)
            response_body = json.loads(http_response.body)
            latest_version = response_body["info"]["version"]
            current_version = Extension.version

            # compare our versions, and convert result to boolean
            upgrade_available = parse_version(latest_version) > parse_version(
                current_version
            )
            upgrade_available = upgrade_available == 1

        except (urllib.request.HTTPError, urllib.request.URLError):
            latest_version = "0.0.0"
            upgrade_available = False

        response = {
            "version": {
                "current": current_version,
                "latest": latest_version,
                "is_root": self.is_root(),
                "upgrade_available": upgrade_available,
            }
        }
        if callback:
            callback(response)
        else:
            return response

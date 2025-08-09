import json
import logging
import tornado
import tornado.web
import shlex
import subprocess
import sys

from logging import Logger
from shutil import which

from jupyter_server.base.handlers import APIHandler

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class CondaHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.info("Getting conda env list")
        try:
            response = None
            conda_cmd_split = shlex.split(f"{which('conda')} env list --json")
            with subprocess.Popen(
                conda_cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process:
                out, error = process.communicate()

                if out:
                    logger.info(json.loads(out))
                    response = json.dumps(json.loads(out))

                if error:
                    logger.error(error)

        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 200
            self.finish(response)

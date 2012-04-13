import json
import logging

from .errors import NBYumException, WTFException


class NBYumLogger(logging.Logger):
    def handle(self, record):
        level = record.levelname.lower()


        if level not in ("debug", "info", "warning", "error"):
            if level in ("critical", "fatal"):
                level = "error"

            # Parse those multilevel from Yum into something meaningful
            elif level.startswith("debug"):
                level = "debug"
            elif level.startswith("info"):
                level = "info"

            else:
                raise WTFException("Got unexpected logging level: %s" % level)

        print(json.dumps({level: record.getMessage()}))

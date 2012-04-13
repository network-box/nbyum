import json
import logging

from .errors import NBYumException, WTFException


class NBYumLogger(logging.Logger):
    def handle(self, record):
        level = record.levelname.lower()

        if level in ("critical", "fatal"):
            level = "error"

        if level not in ("debug", "info", "warning", "error"):
            # Parse those annoying multilevel from Yum into something meaningful
            if level.startswith("debug"):
                level = "debug"
            elif level.startswith("info"):
                level = "info"
            else:
                raise WTFException("Got unexpected level: %s" % level)

        print(json.dumps({level: record.getMessage()}))

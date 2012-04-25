import json
import logging

from .errors import NBYumException, WTFException


class NBYumLogger(logging.Logger):
    def handle(self, record):
        level = record.levelname.lower()

        # We don't differentiate between those 3
        if level in ("critical", "fatal"):
            level = "error"

        # Parse those multilevel from Yum into something meaningful
        if level.startswith("debug"):
            level = "debug"
        if level.startswith("info"):
            level = "info"

        if level in ("debug", "info", "warning", "error"):
            print(json.dumps({"type": level, "message": record.getMessage()}))

        else:
            raise WTFException("Got unexpected logging level: %s" % level)

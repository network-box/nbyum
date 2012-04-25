import json
import logging

from .errors import NBYumException, WTFException


# Our custom log levels
PROGRESS_LEVEL  = 3141592653


class NBYumLogger(logging.Logger):
    log_progress  = lambda self, msg: self.log(PROGRESS_LEVEL, msg)

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

        elif level == "progress":
            # `record.msg` is a dict
            print(json.dumps({"type": level,
                              "current": record.msg["current"],
                              "total": record.msg["total"],
                              "hint": record.msg["hint"]}))

        else:
            raise WTFException("Got unexpected logging level: %s" % level)

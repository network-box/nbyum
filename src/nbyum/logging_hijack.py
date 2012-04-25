import json
import logging

from yum.constants import (TS_UPDATE, TS_ERASE, TS_INSTALL, TS_TRUEINSTALL,
                           TS_OBSOLETED, TS_OBSOLETING, TS_UPDATED)
from yum.rpmtrans import RPMBaseCallback

from .errors import NBYumException, WTFException


# Our custom log levels
PROGRESS_LEVEL  = 3141592653
INFOS_LEVEL     = 31415926535897
INSTALLED_LEVEL = 314159265358979
AVAILABLE_LEVEL = 3141592653589793


class NBYumLogger(logging.Logger):
    log_progress  = lambda self, msg: self.log(PROGRESS_LEVEL, msg)
    log_infos     = lambda self, msg: self.log(INFOS_LEVEL, msg)
    log_installed = lambda self, msg: self.log(INSTALLED_LEVEL, msg)
    log_available = lambda self, msg: self.log(AVAILABLE_LEVEL, msg)

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

        elif level in ("pkginfos", "installed", "available"):
            # `record.msg` is a list of dicts, each representing a package
            print(json.dumps({"type": level, "pkgs": record.msg}))

        elif level == "progress":
            # `record.msg` is a dict
            print(json.dumps({"type": level,
                              "current": record.msg["current"],
                              "total": record.msg["total"],
                              "hint": record.msg["hint"]}))

        else:
            raise WTFException("Got unexpected logging level: %s" % level)


class NBYumRPMCallback(RPMBaseCallback):
    def __init__(self):
        RPMBaseCallback.__init__(self)

        self.fileaction = {TS_INSTALL: 'Installed',
                           TS_TRUEINSTALL: 'Installed',
                           TS_OBSOLETING: 'Installed',
                           TS_UPDATE: 'Installed',
                           TS_OBSOLETED: 'Removed',
                           TS_UPDATED: 'Removed',
                           TS_ERASE: 'Removed',
                           }

    def event(self, package, action, te_current, te_total, ts_current, ts_total):
        """Log progression of the transaction."""
        if te_current != te_total:
            # No progress bar, we only print packages completely processed
            return

        if action in self.fileaction:
            self.logger.log(PROGRESS_LEVEL,
                            {"current": ts_current,
                             "total": ts_total,
                             "hint": "%s: %s" % (self.fileaction[action],
                                                 package)})

        else:
            raise WTFException("Package %s from transaction had action set " \
                               "to %s" % (package, action))

    def filelog(self, package, action):
        """Log that a package has been entirely installed/removed/..."""
        # We don't get packages removed as part of an update here, so we do
        # everything in self.event() instead, acting only if the package is
        # done with
        pass

    def scriptout(self, package, msgs):
        """Log errors in the package scriptlets."""
        if msgs:
            for msg in msgs:
                self.logger.error(msg)

    def errorlog(self, msg):
        """Log Yum errors occuring **during** the transaction."""
        self.logger.error(msg)

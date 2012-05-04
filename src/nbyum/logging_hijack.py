import json
import logging

from yum.constants import (TS_UPDATE, TS_ERASE, TS_INSTALL, TS_TRUEINSTALL,
                           TS_OBSOLETED, TS_OBSOLETING, TS_UPDATED)
from yum.rpmtrans import RPMBaseCallback

from .errors import NBYumException, WTFException


# Our custom log levels
PROGRESS_LEVEL  = 3141592653
INSTALL_LEVEL   = 31415926535
UPDATE_LEVEL    = 314159265358
REMOVE_LEVEL    = 3141592653589
INFOS_LEVEL     = 31415926535897
RECAP_LEVEL     = 31415926535897932


class NBYumLogger(logging.Logger):
    log_progress  = lambda self, msg: self.log(PROGRESS_LEVEL, msg)
    log_install   = lambda self, msg: self.log(INSTALL_LEVEL, msg)
    log_update    = lambda self, msg: self.log(UPDATE_LEVEL, msg)
    log_remove    = lambda self, msg: self.log(REMOVE_LEVEL, msg)
    log_infos     = lambda self, msg: self.log(INFOS_LEVEL, msg)
    log_recap     = lambda self, msg: self.log(RECAP_LEVEL, msg)

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
            print(json.dumps({"type": "log", level: record.getMessage()}))

        elif level in ("install", "update", "remove",
                       "pkginfos"):
            # `record.msg` is a list of dicts, each representing a package
            print(json.dumps({"type": level, "pkgs": record.msg}))

	elif level == "recap":
            d = {"type": level}

            # `record.msg` is a dict where for each (k, v) :
            #   - `k` is one of ("install", "update", "remove", "pkginfos",
            #                  "installed", "available")
            #   - `v` is a list of dicts, each representing a package
            d.update(record.msg)

            print(json.dumps(d))

        elif level == "progress":
            # `record.msg` is a dict
            print(json.dumps({"type": level,
                              "current": record.msg["current"],
                              "total": record.msg["total"],
                              "hint": record.msg["hint"]}))

        else:
            raise WTFException("Got unexpected logging level: %s" % level)


class NBYumRPMCallback(RPMBaseCallback):
    def __init__(self, installroot="/"):
        RPMBaseCallback.__init__(self)

        self.fileaction = {TS_INSTALL: 'Installed',
                           TS_TRUEINSTALL: 'Installed',
                           TS_OBSOLETING: 'Installed',
                           TS_UPDATE: 'Installed',
                           TS_OBSOLETED: 'Removed',
                           TS_UPDATED: 'Removed',
                           TS_ERASE: 'Removed',
                           }

        # FIXME: We only need this whole thing to work around a Yum bug:
        #     https://bugzilla.redhat.com/show_bug.cgi?id=684686#c6
        # When it's fixed, just nuke it out of here
        self.__installroot = installroot

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
        # FIXME: We only need this whole thing to work around a Yum bug:
        #     https://bugzilla.redhat.com/show_bug.cgi?id=684686#c6
        # When it's fixed, just nuke it out of here
        if self.__installroot != "/" and msg.startswith("could not open ts_done file: [Errno 2] No such file or directory: '"):
            return

        self.logger.error(msg)

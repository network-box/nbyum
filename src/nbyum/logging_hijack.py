import json
import logging
import sys

from yum.constants import (TS_UPDATE, TS_ERASE, TS_INSTALL, TS_TRUEINSTALL,
                           TS_OBSOLETED, TS_OBSOLETING, TS_UPDATED)
from yum.rpmtrans import RPMBaseCallback

from .errors import NBYumException, WTFException


# Our custom log levels
PROGRESS_LEVEL  = 314159
RECAP_LEVEL = 3141592


class NBYumLogger(logging.Logger):
    log_progress = lambda self, msg: self.log(PROGRESS_LEVEL, msg)
    log_recap = lambda self, msg: self.log(RECAP_LEVEL, msg)

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
            hdlr = self._get_syslog_handler()
            if hdlr:
                if record.levelno >= hdlr.level:
                    hdlr.handle(record)

            else:
                sys.stdout.write("%s\n" % json.dumps({"type": "log",
                                                      level: record.getMessage()}))

        elif level == "recap":
            d = {"type": level}

            # `record.msg` is a dict where for each (k, v) :
            #   - `k` is one of ("install", "update", "remove", "pkginfos",
            #                  "installed", "available")
            #   - `v` is a list of dicts, each representing a package
            d.update(record.msg)

            sys.stdout.write("%s\n" % json.dumps(d))

        elif level == "progress":
            # `record.msg` is a dict
            sys.stdout.write("%s\n" % json.dumps({"type": level,
                                                  "current": record.msg["current"],
                                                  "total": record.msg["total"],
                                                  "hint": record.msg["hint"]}))

        else:
            raise WTFException("Got unexpected logging level: %s" % level)

        sys.stdout.flush()

    def _get_syslog_handler(self):
        """Get Yum's syslog handler, if there is one for this logger."""
        for hdlr in self.handlers:
            if isinstance(hdlr, logging.handlers.SysLogHandler):
                return hdlr

        if self.propagate:
            return self.parent._get_syslog_handler()


class NBYumRPMCallback(RPMBaseCallback):
    def __init__(self, installroot="/"):
        RPMBaseCallback.__init__(self)

        self.action = {TS_INSTALL: 'Installed',
                       TS_TRUEINSTALL : 'Installed',
                       TS_OBSOLETING: 'Installed',
                       TS_UPDATE : 'Installed',
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

        if action in self.action:
            self.logger.log_progress({"current": ts_current, "total": ts_total,
                                      "hint": "%s: %s" % (self.action[action],
                                                          package)})

        else:
            self.logger.error("The package %s from the transaction had its "
                              "action set to %s, which should never have "
                              "happened. Please report it as a bug."
                                  % (package, action))

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
        yumbug_error = "could not open ts_done file: [Errno 2] No such file" \
                       " or directory: '"
        if self.__installroot != "/" and msg.startswith(yumbug_error):
            return

        self.logger.error(msg)

    def verify_txmbr(self, base, txmbr, count):
        """Log progression of the post-transaction verifications."""
        self.logger.log_progress({"current": count, "total": len(base.tsInfo),
                                  "hint": "Verified: %s" % str(txmbr.po)})

import logging

from .logging_hijack import (NBYumLogger, NBYumTextMeter,
                             PROGRESS_LEVEL, RECAP_LEVEL)
from .utils import (DummyOpts, timestamp_to_pretty_local_datetime,
                    timestamp_to_iso_local_datetime, locked)
from .yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args):
        self.args = args

        # -- Hijack the Yum logging ------------------------------------------
        logging.setLoggerClass(NBYumLogger)
        logging.addLevelName(PROGRESS_LEVEL, "progress")
        logging.addLevelName(RECAP_LEVEL, "recap")

        self.base = NBYumBase()

        # -- Deal with the preconfig stuff -----------------------------------
        if not args.debug:
            self.base.preconf.debuglevel = 0
        else:
            self.base.preconf.debuglevel = 6

        if args.config:
            self.base.preconf.fn = args.config

        self.base.prerepoconf.progressbar = NBYumTextMeter()

        # This sets up a bunch of stuff
        self.base.conf

        if self.args.func == "last_updated":
            args.force_cache = True

        if args.force_cache:
            if self.args.func == "rebuild_cache":
                self.base.logger.warning("Ignoring --force-cache argument, as"
                                         " we are rebuilding the cache")

            else:
                self.base.conf.cache = 1

    @locked
    def prepare(self):
        self.base.prepare()
        self.base.logger.log_progress({"current": 0, "total": 1,
                                       "hint": "Processing the package "
                                               "metadata..."})

    def run(self):
        try:
            # -- Prepare our Yum base for the user's request -----------------
            if self.args.func not in ("last_updated", "rebuild_cache"):
                self.prepare()

            # -- Then do what we were asked ----------------------------------
            func = getattr(self, self.args.func)
            func()
            return 0

        except Exception, e:
            if self.args.debug:
                import traceback
                e = traceback.format_exc()

            self.base.logger.error(e)
            return 1

    # -- Functions corresponding to commands ---------------------------------
    @locked
    def check_update(self):
        """Check for updates to installed packages."""
        last_update = self.base.get_last_updated()

        if last_update != None:
            last_update = timestamp_to_pretty_local_datetime(last_update)
            self.base.verbose_logger.info("Last updated on %s"
                                          % last_update)

        self.base.update_packages(self.args.patterns, apply=False)
        self.base.recap_transaction()

    def info(self):
        """Get some infos about packages."""
        self.base.get_infos(self.args.patterns)

    @locked
    def install(self):
        """Install packages and security modules."""
        self.base.plugins.setCmdLine(DummyOpts(nuke_newsave=True,
                                               posttrans_triggers=True),
                                     None)

        self.base.install_packages(self.args.type, self.args.patterns)
        self.base.recap_transaction()

    def last_updated(self):
        """Get the date of the last system update"""
        last_update = self.base.get_last_updated()

        if last_update != None:
            last_update = timestamp_to_iso_local_datetime(last_update)
            self.base.logger.log_recap({"last_update": last_update})

    def list(self):
        """List packages and security modules."""
        self.base.list_packages(self.args.type, self.args.filter,
                                self.args.patterns, self.args.show_hidden)

    @locked
    def rebuild_cache(self):
        """Clean and rebuild the cache."""
        self.base.clean_cache()
        self.base.prepare()

    @locked
    def remove(self):
        """Remove packages and security modules."""
        self.base.plugins.setCmdLine(DummyOpts(remove_leaves=True,
                                               posttrans_triggers=True),
                                     None)

        self.base.remove_packages(self.args.type, self.args.patterns)
        self.base.recap_transaction()

    @locked
    def update(self):
        """Actually update the whole system."""
        self.base.plugins.setCmdLine(DummyOpts(nuke_newsave=True,
                                               posttrans_triggers=True),
                                     None)

        self.base.update_packages(self.args.patterns, apply=True)
        self.base.recap_transaction()

from contextlib import contextmanager
import errno
import logging
import pwd

from yum.Errors import LockError
from yum.rpmtrans import NoOutputCallBack

from .errors import NBYumException, WTFException
from .logging_hijack import (NBYumLogger, PROGRESS_LEVEL, INSTALL_LEVEL,
                             UPDATE_LEVEL, REMOVE_LEVEL, INFOS_LEVEL,
                             INSTALLED_LEVEL, AVAILABLE_LEVEL)
from .utils import DummyOpts, ensure_privileges
from .yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args):
        self.args = args

        # -- Hijack the Yum logging ------------------------------------------
        logging.setLoggerClass(NBYumLogger)
        logging.addLevelName(PROGRESS_LEVEL,  "progress")
        logging.addLevelName(INSTALL_LEVEL,   "install")
        logging.addLevelName(UPDATE_LEVEL,    "update")
        logging.addLevelName(REMOVE_LEVEL,    "remove")
        logging.addLevelName(INFOS_LEVEL,     "pkginfos")
        logging.addLevelName(INSTALLED_LEVEL, "installed")
        logging.addLevelName(AVAILABLE_LEVEL, "available")

        # -- Deal with the preconfig stuff -----------------------------------
        self.base = NBYumBase()

        if not args.debug:
            # Shut yum up
            self.base.preconf.debuglevel = 0
        else:
            self.base.preconf.debuglevel = 6

        if args.config:
            self.base.preconf.fn = args.config

        self.base.setCacheDir()

        self.base.logger.log_progress({"current": 0, "total": 1, "hint": "Downloading the packages metadata..."})
        self.base._getSacks()

        self.base.logger.log_progress({"current": 0, "total": 1, "hint": "Processing the packages metadata..."})

    @contextmanager
    def __lock_yum(self):
        """Acquire the Yum global lock.

        This method works as a context manager, to be used in a `with' block.
        """
        # -- Acquire the lock ------------------------------------------------
        try:
            self.base.doLock()

        except LockError as e:
            if e.errno in (errno.EPERM, errno.EACCES):
                raise WTFException("Can't create the lock file: %s" % e)

            else:
                lock_owner = {"pid": int(e.pid)}

                with open("/proc/%(pid)s/status" % lock_owner) as status:
                    for line in status:
                        if line.startswith("Name:"):
                            exe = line.strip().split()[-1]

                            with open("/proc/%(pid)s/cmdline" % lock_owner) as cmdline_file:
                                cmdline = cmdline_file.read().split("\x00")

                            for index, token in enumerate(cmdline):
                                if token.startswith("/") and token.endswith(exe):
                                    # Everything after now are options
                                    lock_owner["cmd"] = " ".join([exe, cmdline.pop(index+1)])
                                    break
                            else:
                                lock_owner["cmd"] = exe

                        if line.startswith("Uid:"):
                            uid = int(line.strip().split()[-1])
                            lock_owner["user"] = pwd.getpwuid(uid)[0]

                msg = "The package system is being used by another " \
                      "administrator - please try again later (user: " \
                      "%(user)s, cmd: '%(cmd)s', pid: %(pid)s)" % lock_owner

                raise NBYumException(msg)

        # -- Do the work, protected by the acquired lock ---------------------
        yield

        # -- Work is finished, release the lock ------------------------------
        self.base.closeRpmDB()
        self.base.doUnlock()

    def run(self):
        try:
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
    def check_update(self):
        """Check for updates to installed packages."""
        with self.__lock_yum():
            self.base.update_packages(self.args.patterns, apply=False)
            self.base.recap_transaction()

    def info(self):
        """Get some infos about packages."""
        self.base.get_infos(self.args.patterns)

    @ensure_privileges
    def install(self):
        """Install packages and security modules."""
        self.base.plugins.setCmdLine(DummyOpts(nuke_newsave=True,
                                               posttrans_triggers=True),
                                     None)

        with self.__lock_yum():
            self.base.install_packages(self.args.type, self.args.patterns)
            self.base.recap_transaction()

    def list(self):
        """List packages and security modules."""
        with self.__lock_yum():
            self.base.list_packages(self.args.type, self.args.filter,
                                    self.args.patterns)

    @ensure_privileges
    def remove(self):
        """Remove packages and security modules."""
        self.base.plugins.setCmdLine(DummyOpts(remove_leaves=True,
                                               posttrans_triggers=True),
                                     None)

        with self.__lock_yum():
            self.base.remove_packages(self.args.type, self.args.patterns)
            self.base.recap_transaction()

    @ensure_privileges
    def update(self):
        """Actually update the whole system."""
        self.base.plugins.setCmdLine(DummyOpts(nuke_newsave=True,
                                               posttrans_triggers=True),
                                     None)

        with self.__lock_yum():
            self.base.update_packages(self.args.patterns, apply=True)
            self.base.recap_transaction()

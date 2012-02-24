import json

from yum.rpmtrans import NoOutputCallBack

from errors import NBYumException, WTFException
from utils import DummyOpts, ensure_privileges
from yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args):
        self.args = args

        # -- Deal with the preconfig stuff -----------------------------------
        self.base = NBYumBase()

        if not args.debug:
            # Shut yum up
            self.base.preconf.debuglevel = 0
            self.base.preconf.errorlevel = 0
            self.base.nbyum_rpmDisplay = NoOutputCallBack()
        else:
            self.base.preconf.debuglevel = 99
            self.base.preconf.errorlevel = 99
            self.base.nbyum_rpmDisplay = None

        if args.config:
            self.base.preconf.fn = args.config

        self.base.setCacheDir()

        # We don't care about it, but calling it initializes the plugins...
        self.base.conf

        # -- Monkey-patch the YumBase for what can't be done as preconfig ----
        # The Yum API prints warnings and errors instead of making them
        # available and useful. As a result, if we want to retrieve them,
        # we must play dirty tricks on the YumBase loggers. :(
        def new_warning(msg, *args):
            if len(args) == msg.count("%s"):
                print(json.dumps({'warning': '%s' % (msg%args)}))

            else:
                msg = "Something unexpected happened while trying to print " \
                      "a warning.\n\nThe warning message to print was the " \
                      "following:\n  %s\n\nHowever, some additional " \
                      "arguments were passed, but it is not clear how they\n" \
                      "should have been handled:\n  %s\n\nPlease report a " \
                      "bug, providing the above information." % (msg, args)
                raise WTFException(msg)

        def new_critical(msg):
            raise NBYumException(msg)

        self.base.verbose_logger.warning = new_warning
        self.base.logger.critical = new_critical

    def run(self):
        try:
            func = getattr(self, self.args.func)
            func()
            return 0

        except Exception, e:
            if self.args.debug:
                import traceback
                e = traceback.format_exc()

            print(json.dumps({'error': '%s' % e}))
            return 1

    # -- Functions corresponding to commands ---------------------------------
    def check_update(self):
        """Check for updates to installed packages."""
        self.base.update_packages(self.args.patterns, apply=False)
        self.base.recap_transaction()

    def info(self):
        """Get some infos about packages."""
        self.base.get_infos(self.args.patterns)

    @ensure_privileges
    def install(self):
        """Install packages and security modules."""
        self.base.install_packages(self.args.type, self.args.patterns)
        self.base.recap_transaction()

    def list(self):
        """List packages and security modules."""
        self.base.list_packages(self.args.type, self.args.filter,
                                self.args.patterns)

    @ensure_privileges
    def remove(self):
        """Remove packages and security modules."""
        self.base.plugins.setCmdLine(DummyOpts(remove_leaves=True), None)

        self.base.remove_packages(self.args.type, self.args.patterns)
        self.base.recap_transaction()

    @ensure_privileges
    def update(self):
        """Actually update the whole system."""
        self.base.update_packages(self.args.patterns, apply=True)
        self.base.recap_transaction()

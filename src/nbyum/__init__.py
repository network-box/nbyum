from yum.rpmtrans import NoOutputCallBack

from errors import NBYumException
from utils import ensure_privileges
from yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args):
        self.args = args

        self.base = NBYumBase()

        if not args.debug:
            # Shut yum up
            self.base.preconf.debuglevel = 0
            self.base.preconf.errorlevel = 0
            self.base.nbyum_rpmDisplay = NoOutputCallBack()
        else:
            self.base.nbyum_rpmDisplay = None

        if args.config:
            self.base.preconf.fn = args.config

        self.base.setCacheDir()

        # The Yum API is just hopeless, it prints errors instead of raising
        # them. As a result, if we want to retrieve it, we must trick the
        # YumBase logger.
        # /me feels dirty :(
        def new_critical(msg):
            raise NBYumException(msg)

        self.base.logger.critical = new_critical

    def run(self):
        try:
            func = getattr(self, self.args.func)
            func()
            return 0

        except Exception, e:
            import json

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
    def update(self):
        """Actually update the whole system."""
        self.base.update_packages(self.args.patterns, apply=True)
        self.base.recap_transaction()

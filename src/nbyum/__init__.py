from yum.rpmtrans import NoOutputCallBack
from yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args, yumconf=None):
        self.args = args

        self.base = NBYumBase()

        if not args.debug:
            # Shut yum up
            self.base.preconf.debuglevel = 0
            self.base.preconf.errorlevel = 0
            self.base.nbyum_rpmDisplay = NoOutputCallBack()
        else:
            self.base.nbyum_rpmDisplay = None

        if yumconf:
            self.base.preconf.fn = yumconf

        self.base.setCacheDir()

    def run(self):
        try:
            func = getattr(self, self.args.func)
            func()
            return 0

        except Exception, e:
            print("{'error': '%s'}" % e)
            return 1

    # -- Functions corresponding to commands ---------------------------------
    def check_update(self):
        """Check for updates to installed packages."""
        self.base.update_packages(self.args.packages, apply=False)
        self.base.recap_transaction()

    def update(self):
        """Actually update the whole system."""
        self.base.update_packages(self.args.packages, apply=True)
        self.base.recap_transaction()

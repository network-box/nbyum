from yumbase import NBYumBase


class NBYumCli(object):
    def __init__(self, args):
        self.args = args

        self.base = NBYumBase()

        if not args.debug:
            # Shut yum up
            self.base.preconf.debuglevel = 0
            self.base.preconf.errorlevel = 0

        self.base.setCacheDir()

    def run(self):
        func = getattr(self, self.args.func)
        func()

    def check_update(self):
        """Check for updates to installed packages."""
        self.base.populate_updates()
        self.base.recap_transaction()

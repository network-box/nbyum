import yum


class NBYum(yum.YumBase):
    def __init__(self, args):
        super(NBYum, self).__init__()

        if not args.debug:
            # Shut yum up
            self.preconf.debuglevel = 0
            self.preconf.errorlevel = 0

        self.setCacheDir()

        self.args = args

    def run(self):
        func = getattr(self, self.args.func)
        func()

import yum


class NBYum(yum.YumBase):
    def __init__(self):
        super(NBYum, self).__init__()

        # Shut yum up
        self.preconf.debuglevel = 0
        self.preconf.errorlevel = 0

        self.setCacheDir()

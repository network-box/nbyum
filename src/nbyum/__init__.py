import yum


class NBYum(object):
    def __init__(self):
        self.yum = yum.YumBase()

        # Shut yum up
        self.yum.preconf.debuglevel = 0
        self.yum.preconf.errorlevel = 0

        self.yum.setCacheDir()

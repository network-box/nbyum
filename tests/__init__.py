import cStringIO
import os
import subprocess
import sys
import unittest2


global_dataroot = os.path.join(os.path.abspath(os.getcwd()), "tests/data")
conf_template = os.path.join("/etc/yum.conf")
setuprepo_baseurl = os.path.join(global_dataroot, "setup.repo")


class TestCase(unittest2.TestCase):
    def setUp(self):
        # -- We will need a parser ---------------------------------
        from nbyum.utils import get_parser
        self.parser = get_parser()

        # -- A few useful definitions ------------------------------
        self.dataroot = os.path.join(global_dataroot, self.command)
        self.yumconf = os.path.join(self.dataroot,
                                    "%s.conf" % self._testMethodName)
        self.installroot = os.path.join(self.dataroot,
                                        "%s.root" % self._testMethodName)
        self.reposdir = os.path.join(self.dataroot,
                                     "%s.repos.d" % self._testMethodName)
        self.cachedir = os.path.join(self.dataroot,
                                "%s.cache" % self._testMethodName)

        testrepo_conf = os.path.join(self.reposdir, "test.repo")
        testrepo_baseurl = os.path.join(self.dataroot,
                                        "%s.repo" % self._testMethodName)

        # -- Set up the yum config and repos -----------------------
        if not os.path.isdir(self.reposdir):
            os.makedirs(self.reposdir)

        with open(conf_template, "r") as input:
            with open(self.yumconf, "w") as output:
                for line in input.readlines():
                    if line.startswith("cachedir="):
                        output.write("cachedir=%s\n" % self.cachedir)
                    else:
                        output.write(line)

                if hasattr(self, "installonlypkgs"):
                    output.write("installonlypkgs=%s\n" % self.installonlypkgs)

                output.write("installroot=%s\n" % self.installroot)
                output.write("reposdir=%s\n" % self.reposdir)
                output.write("\n")
                output.write("[setup]\n")
                output.write("name=Setup test repo\n")
                output.write("enabled=1\n")
                output.write("baseurl=file://%s\n" % setuprepo_baseurl)
                output.write("gpgcheck=0\n")

        # -- Install a handful of packages, to test transactions ---
        cmd = ["sudo", "yum", "install", "*", "-c", self.yumconf, "-y"]
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with open(testrepo_conf, "w") as f:
            f.write("[test]\n")
            f.write("name=Dummy test repo\n")
            f.write("enabled=1\n")
            f.write("baseurl=file://%s\n" % testrepo_baseurl)
            f.write("gpgcheck=0\n")

    def tearDown(self):
        cmd = ["yum", "clean", "all", "-c", self.yumconf]
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # -- Cleanup, with super user permissions ------------------
        cmd = ["sudo", "rm", "-fr", self.yumconf,
                                    self.installroot,
                                    self.reposdir,
                                    self.cachedir,
               ]
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _run_nbyum_test(self, args):
        """This is not a test method, just a helper to avoid duplication."""
        # Make sure we use our own test config
        args.config = self.yumconf

        # All nbyum does is print its output, so let's capture it
        self.old_stdout = sys.stdout
        self.new_stdout = cStringIO.StringIO()
        sys.stdout = self.new_stdout

        from nbyum import NBYumCli
        yummy = NBYumCli(args)
        yummy.run()

        # And restore stdout now that we finished
        sys.stdout = self.old_stdout

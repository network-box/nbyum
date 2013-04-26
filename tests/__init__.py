from itertools import izip_longest
import json
from operator import attrgetter
import os
import subprocess
import unittest

import rpm


global_dataroot = os.path.join(os.path.abspath(os.getcwd()), "tests/data")
conf_template = "/etc/yum.conf"
setuprepo_baseurl = os.path.join(global_dataroot, "setup.repo")


class TestCase(unittest.TestCase):
    def setUp(self):
        # -- A few useful definitions ------------------------------
        self.dataroot = os.path.join(global_dataroot, self.command)
        self.yumconf = os.path.join(self.dataroot,
                                    "%s.conf" % self._testMethodName)
        self.installroot = os.path.join(self.dataroot,
                                        "%s.root" % self._testMethodName)
        self.reposdir = os.path.join(self.dataroot,
                                     "%s.repos.d" % self._testMethodName)

        testrepo_baseurl = os.path.join(self.dataroot,
                                        "%s.repo" % self._testMethodName)

        # -- Write the yum config and setup repo -------------------
        if not os.path.isdir(self.reposdir):
            os.makedirs(self.reposdir)

        with open(conf_template, "r") as input:
            with open(self.yumconf, "w") as output:
                for line in input.readlines():
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
        self._install_packages_setup(["*"])

        # -- Set up the test repo ----------------------------------
        self._add_repo("test", testrepo_baseurl)

    def _add_repo(self, name, baseurl):
        """Not a test, just a handy helper."""
        testrepo_conf = os.path.join(self.reposdir, "%s.repo" % name)

        with open(testrepo_conf, "w") as f:
            f.write("[%s]\n" % name)
            f.write("name=Dummy test repo\n")
            f.write("enabled=1\n")
            f.write("baseurl=file://%s\n" % baseurl)
            f.write("gpgcheck=0\n")

    def tearDown(self):
        cmd = ["/usr/bin/yum", "clean", "all", "-c", self.yumconf]
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # -- Cleanup, with super user permissions ------------------
        cmd = ["/bin/rm", "-fr", self.yumconf,
                                    self.installroot,
                                    self.reposdir,
               ]
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _run_nbyum_test(self, args, expected):
        """This is not a test method, just a helper to avoid duplication."""
        cmd = ["./nbyum", "-c", self.yumconf] + args
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, unused = proc.communicate()

        result = [json.loads(line) for line in stdout.split("\n") if line]

        self.assertEqual(result, expected,
                         msg="\n".join(self._gen_diff(result, expected)))

    def _check_installed_rpms(self, expected):
        """Not a test, just a handy helper.

        This compares the list of installed packages to the provided expected
        list.
        """
        result = []

        for h in sorted(rpm.TransactionSet(self.installroot).dbMatch(),
                        key=attrgetter("name", "version", "release")):
            if h["epoch"] is None:
                h["epoch"] = 0
            result.append("%(epoch)s:%(name)s-%(version)s-%(release)s.%(arch)s" % h)

        self.assertEqual(result, expected)

    def _install_packages_setup(self, pkgs):
        """Not a test, just a handy helper.

        This installs a few packages using yum, which is needed as part of the
        setup for some tests.
        """
        cmd = ["/usr/bin/yum", "install",
                                                "-c", self.yumconf,
                                                "-y"]
        cmd.extend(pkgs)

        subprocess.check_call(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

    def _gen_diff(self, result, expected):
        yield "We didn't get the expected result:"
        yield "-expected result"
        yield "+actual result"
        yield "================"
        for res, exp in izip_longest(result, expected):
            if res == exp:
                yield " %s" % res
            else:
                if exp is not None:
                    yield "-%s" % exp
                if res is not None:
                    yield "+%s" % res


# Make sure the unit tests are discovered
from test_checkupdate import *
from test_info import *
from test_install_sms import *
from test_list import *
from test_list_sms import *
from test_remove_sms import *
from test_update import *

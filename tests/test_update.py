import os
import unittest2

from tests import TestCase


class TestUpdate(TestCase):
    command = "update"
    installonlypkgs = "bar"

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_no_updates(self):
        """Update from a repo with no available updates."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"info": "Packages are all up to date"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_updates(self):
        """Update from a repo with only updates available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_install(self):
        """Update from a repo with only new installs available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': {"name": "bar", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_obsoletes(self):
        """Update from a repo with only obsoletes available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': [{"name": "bar", "epoch": "0", "version": "1",
                                   "release": "1.nb5.0", "arch": "noarch"},
                                  {"name": "baz", "epoch": "0", "version": "2",
                                   "release": "1.nb5.0", "arch": "noarch"}]},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_install_as_dep(self):
        """Update from a repo with an update requiring a new install."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_ordering(self):
        """Update from a repo with a bit of everything available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': [{"name": "bar", "epoch": "0", "version": "1",
                                   "release": "1.nb5.0", "arch": "noarch"},
                                  {"name": "baz", "epoch": "0", "version": "2",
                                   "release": "1.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_ordering_bis(self):
        """Update from a repo with a bit of everything available, bis."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': {"name": "bar", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}},
                    {'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_no_newsave(self):
        """Update and make sure no rpmnew/rpmsave files were left."""
        args = [self.command]

        # -- Quick modification of the config files ----------------
        with open("/etc/foo.conf", "w") as f:
            f.write("foo=0\n")
        with open("/etc/foo-noreplace.conf", "w") as f:
            f.write("foo=0\n")

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "nbsm-foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "nbsm-foo", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-2-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

        # -- Check that no rpmnew/rpmsave files were left ----------
        self.assertFalse(os.path.exists("/etc/foo.conf.rpmsave"))
        self.assertFalse(os.path.exists("/etc/foo-noreplace.conf.rpmnew"))

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_posttrans_triggers(self):
        "Make sure we correctly use the posttrans-triggers yum plugin."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "nbsm-foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "nbsm-foo", "epoch": "0", "version": "3",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {"info": "All packages updated successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-3-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

        # -- Check that the posttrans trigger was run --------------
        self.assertTrue(os.path.exists("/tmp/trigger_was_run"))
        os.unlink("/tmp/trigger_was_run")

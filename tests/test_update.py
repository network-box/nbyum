import os

from tests import TestCase


class TestUpdate(TestCase):
    command = "update"
    installonlypkgs = "bar"

    def test_no_updates(self):
        """Update from a repo with no available updates."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "info", "message": "Packages are all up to date"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_only_updates(self):
        """Update from a repo with only updates available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 2, "hint": "Installed: foo-1-2.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 2, "hint": "Removed: foo"},
                    {"type": "update", "pkgs": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_only_install(self):
        """Update from a repo with only new installs available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 1, "hint": "Installed: bar-1-2.nb5.0.noarch"},
                    {"type": "install", "pkgs": [{"name": "bar", "new": "1-2.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_only_obsoletes(self):
        """Update from a repo with only obsoletes available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 2, "hint": "Installed: baz-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 2, "hint": "Removed: bar"},
                    {"type": "remove", "pkgs": [{"name": "bar", "old": "1-1.nb5.0", "reason": "Replaced by baz-2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_install_as_dep(self):
        """Update from a repo with an update requiring a new install."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 3, "hint": "Installed: plouf-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 3, "hint": "Installed: toto-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 3, "total": 3, "hint": "Removed: toto"},
                    {"type": "install", "pkgs": [{"name": "plouf", "new": "2-1.nb5.0"}]},
                    {"type": "update", "pkgs": [{"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_mixup(self):
        """Update from a repo with a bit of everything available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 7, "hint": "Installed: plouf-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 7, "hint": "Installed: toto-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 3, "total": 7, "hint": "Installed: foo-1-2.nb5.0.noarch"},
                    {"type": "progress", "current": 4, "total": 7, "hint": "Installed: baz-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 5, "total": 7, "hint": "Removed: foo"},
                    {"type": "progress", "current": 6, "total": 7, "hint": "Removed: bar"},
                    {"type": "progress", "current": 7, "total": 7, "hint": "Removed: toto"},
                    {"type": "install", "pkgs": [{"name": "plouf", "new": "2-1.nb5.0"}]},
                    {"type": "update", "pkgs": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"},
                                                {"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]},
                    {"type": "remove", "pkgs": [{"name": "bar", "old": "1-1.nb5.0", "reason": "Replaced by baz-2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_mixup_bis(self):
        """Update from a repo with a bit of everything available, bis."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 6, "hint": "Installed: plouf-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 6, "hint": "Installed: toto-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 3, "total": 6, "hint": "Installed: bar-1-2.nb5.0.noarch"},
                    {"type": "progress", "current": 4, "total": 6, "hint": "Installed: foo-1-2.nb5.0.noarch"},
                    {"type": "progress", "current": 5, "total": 6, "hint": "Removed: foo"},
                    {"type": "progress", "current": 6, "total": 6, "hint": "Removed: toto"},
                    {"type": "install", "pkgs": [{"name": "bar", "new": "1-2.nb5.0"},
                                                 {"name": "plouf", "new": "2-1.nb5.0"}]},
                    {"type": "update", "pkgs": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"},
                                                {"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_no_newsave(self):
        """Update and make sure no rpmnew/rpmsave files were left."""
        args = [self.command]

        # -- Quick modification of the config files ----------------
        with open("/etc/foo.conf", "w") as f:
            f.write("foo=0\n")
        with open("/etc/foo-noreplace.conf", "w") as f:
            f.write("foo=0\n")

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 2, "hint": "Installed: nbsm-foo-2-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 2, "hint": "Removed: nbsm-foo"},
                    {"type": "update", "pkgs": [{"name": "nbsm-foo", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]}]
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

    def test_posttrans_triggers(self):
        "Make sure we correctly use the posttrans-triggers yum plugin."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 2, "hint": "Installed: nbsm-foo-3-1.nb5.0.noarch"},
                    {"type": "progress", "current": 2, "total": 2, "hint": "Removed: nbsm-foo"},
                    {"type": "update", "pkgs": [{"name": "nbsm-foo", "old": "1-1.nb5.0", "new": "3-1.nb5.0"}]}]
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

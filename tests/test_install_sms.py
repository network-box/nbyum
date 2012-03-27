import os

from tests import TestCase


class TestInstallSms(TestCase):
    command = "install"

    def test_no_sm_match(self):
        """Try installing an unexisting security module."""
        args = [self.command, "sms", "no_such_security_module"]

        # -- Check the error message -------------------------------
        expected = [{"error": "No package(s) available to install"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the no-op ----------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_already_installed_sm(self):
        """Try installing an already installed security module."""
        args = [self.command, "sms", "foo"]

        # -- Check the warning message -----------------------------
        expected = [{"warning": "Package nbsm-foo-1-1.nb5.0.noarch already installed and latest version"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the no-op ----------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_install_sm(self):
        """Try installing a security module."""
        args = [self.command, "sms", "nbsm-bar"]

        # Check the installation summary ---------------------------
        expected = [{"install": {"name": "nbsm-bar", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All requested packages installed successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the install --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-bar-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_install_sm_with_deps(self):
        """Try installing a security module and its dependencies."""
        args = [self.command, "sms", "nbsm-plouf"]

        # Check the installation summary ---------------------------
        expected = [{"install": {"name": "nbsm-plouf", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"}},
                    {"installdep": {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All requested packages installed successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the install --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:nbsm-plouf-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_install_multiple_sms(self):
        """Try installing several security modules and their dependencies."""
        args = [self.command, "sms", "nbsm-plouf", "toto"]

        # Check the installation summary ---------------------------
        expected = [{"install": {"name": "nbsm-plouf", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"}},
                    {"install": {"name": "nbsm-toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"}},
                    {"installdep": {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}},
                    {"info": "All requested packages installed successfully"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the install --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:nbsm-plouf-1-1.nb5.0.noarch",
                    "0:nbsm-toto-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

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
        expected = []
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_updates(self):
        """Update from a repo with only updates available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': ['0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch']}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_install(self):
        """Update from a repo with only new installs available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': '0:bar-1-2.nb5.0.noarch'}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_only_obsoletes(self):
        """Update from a repo with only obsoletes available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': ['0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch']}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_install_as_dep(self):
        """Update from a repo with an update requiring a new install."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': ['0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch']},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_ordering(self):
        """Update from a repo with a bit of everything available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': ['0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch']},
                    {'update': ['0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch']},
                    {'update': ['0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch']},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

    @unittest2.skipIf(os.getuid() != 0, "Updates must be run as root")
    def test_ordering_bis(self):
        """Update from a repo with a bit of everything available, bis."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': '0:bar-1-2.nb5.0.noarch'},
                    {'update': ['0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch']},
                    {'update': ['0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch']},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._check_installed_rpms(expected)

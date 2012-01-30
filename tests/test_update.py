from operator import attrgetter
import os
import unittest2

import rpm

from tests import TestCase


class TestUpdate(TestCase):
    command = "update"
    installonlypkgs = "bar"

    def _get_installed_rpms(self):
        """Not a test, just a handy helper.

        This returns the list of installed packages, to compare with what was
        expected after the update.
        """
        result = []

        for h in sorted(rpm.TransactionSet(self.installroot).dbMatch(),
                        key=attrgetter("name", "version", "release")):
            if h["epoch"] is None:
                h["epoch"] = 0
            result.append("%(epoch)s:%(name)s-%(version)s-%(release)s.%(arch)s" % h)

        return result

    def test_no_updates(self):
        """Update from a repo with no available updates."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = []

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_only_updates(self):
        """Update from a repo with only updates available."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'update': ('0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch')}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_only_install(self):
        """Update from a repo with only new installs available."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'install': '0:bar-1-2.nb5.0.noarch'}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_only_obsoletes(self):
        """Update from a repo with only obsoletes available."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': ('0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch')}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_install_as_dep(self):
        """Update from a repo with an update requiring a new install."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'update': ('0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch')},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_ordering(self):
        """Update from a repo with a bit of everything available."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': ('0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch')},
                    {'update': ('0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch')},
                    {'update': ('0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch')},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:baz-2-1.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    def test_ordering_bis(self):
        """Update from a repo with a bit of everything available, bis."""
        if os.getuid() != 0:
           raise SkipTest("Updates must be run as root")

        args = self.parser.parse_args([self.command])
        self._run_nbyum_test(args)

        # -- Check the update summary ------------------------------
        expected = [{'install': '0:bar-1-2.nb5.0.noarch'},
                    {'update': ('0:foo-1-1.nb5.0.noarch', '0:foo-1-2.nb5.0.noarch')},
                    {'update': ('0:toto-1-1.nb5.0.noarch', '0:toto-2-1.nb5.0.noarch')},
                    {'installdep': '0:plouf-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.new_stdout.getvalue().split("\n") if line]
        self.assertEqual(result, expected)

        # -- Check the installed packages after the update ---------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bar-1-2.nb5.0.noarch",
                    "0:foo-1-2.nb5.0.noarch",
                    "0:plouf-2-1.nb5.0.noarch",
                    "0:toto-2-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

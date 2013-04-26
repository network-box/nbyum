import os

from tests import TestCase


class TestListPackages(TestCase):
    command = "list"

    def test_list_installed_packages(self):
        """List installed packages."""
        args = [self.command, "installed", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "bar", "version": "1-1.nb5.0", "summary": "Get some Bar"},
                                   {"name": "foo", "version": "1-1.nb5.0", "summary": "Get some Foo"},
                                   {"name": "toto", "version": "1-1.nb5.0", "summary": "Get some Toto"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_available_packages(self):
        """List available packages."""
        args = [self.command, "available", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap",
                     "available": [{"name": "baz", "version": "2-1.nb5.0", "summary": "Get some Baz"},
                                   {"name": "foo", "version": "1-2.nb5.0", "summary": "Get some Foo"},
                                   {"name": "plouf", "version": "2-1.nb5.0", "summary": "Get some Plouf"},
                                   {"name": "toto", "version": "2-1.nb5.0", "summary": "Get some Toto"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_packages(self):
        """List all packages."""
        args = [self.command, "all", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "bar", "version": "1-1.nb5.0", "summary": "Get some Bar"},
                                   {"name": "foo", "version": "1-1.nb5.0", "summary": "Get some Foo"},
                                   {"name": "toto", "version": "1-1.nb5.0", "summary": "Get some Toto"}],
                     "available": [{"name": "baz", "version": "2-1.nb5.0", "summary": "Get some Baz"},
                                   {"name": "foo", "version": "1-2.nb5.0", "summary": "Get some Foo"},
                                   {"name": "plouf", "version": "2-1.nb5.0", "summary": "Get some Plouf"},
                                   {"name": "toto", "version": "2-1.nb5.0", "summary": "Get some Toto"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_no_packages_match(self):
        """Make sure no packages are returned with a bogus pattern."""
        args = [self.command, "all", "packages", "no_such_package"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."}]
        self._run_nbyum_test(args, expected)

    def test_list_packages_match(self):
        """List only matching packages."""
        args = [self.command, "all", "packages", "foo", "*lou*"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "foo", "version": "1-1.nb5.0", "summary": "Get some Foo"}],
                     "available": [{"name": "plouf", "version": "2-1.nb5.0", "summary": "Get some Plouf"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_available_packages_deduped(self):
        """List only once a package present in multiple repositories."""
        args = [self.command, "available", "packages", "foo"]

        # -- Do some preparation first -----------------------------
        secondrepo_baseurl = os.path.join(self.dataroot,
                                          "%s2.repo" % self._testMethodName)
        self._add_repo("test2", secondrepo_baseurl)

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap",
                     "available": [{"name": "foo", "version": "1-3.nb5.0", "summary": "Get some Foo"}]}]
        self._run_nbyum_test(args, expected)

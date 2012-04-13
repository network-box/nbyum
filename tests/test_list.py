from tests import TestCase


class TestListPackages(TestCase):
    command = "list"

    def test_list_installed_packages(self):
        """List installed packages."""
        args = [self.command, "installed", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "bar", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Bar"},
                    {"status": "installed", "name": "foo", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Foo"},
                    {"status": "installed", "name": "toto", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Toto"}]
        self._run_nbyum_test(args, expected)

    def test_list_available_packages(self):
        """List available packages."""
        args = [self.command, "available", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "available", "name": "baz", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Baz"},
                    {"status": "available", "name": "foo", "epoch": "0", "version": "1",
                     "release": "2.nb5.0", "arch": "noarch", "summary": "Get some Foo"},
                    {"status": "available", "name": "plouf", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Plouf"},
                    {"status": "available", "name": "toto", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Toto"}]
        self._run_nbyum_test(args, expected)

    def test_list_packages(self):
        """List all packages."""
        args = [self.command, "all", "packages"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "bar", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Bar"},
                    {"status": "installed", "name": "foo", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Foo"},
                    {"status": "installed", "name": "toto", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Toto"},
                    {"status": "available", "name": "baz", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Baz"},
                    {"status": "available", "name": "foo", "epoch": "0", "version": "1",
                     "release": "2.nb5.0", "arch": "noarch", "summary": "Get some Foo"},
                    {"status": "available", "name": "plouf", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Plouf"},
                    {"status": "available", "name": "toto", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Toto"}]
        self._run_nbyum_test(args, expected)

    def test_list_no_packages_match(self):
        """Make sure no packages are returned with a bogus pattern."""
        args = [self.command, "all", "packages", "no_such_package"]

        # -- Check the listing -------------------------------------
        expected = []
        self._run_nbyum_test(args, expected)

    def test_list_packages_match(self):
        """List only matching packages."""
        args = [self.command, "all", "packages", "foo", "*lou*"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "foo", "epoch": "0", "version": "1",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Foo"},
                    {"status": "available", "name": "plouf", "epoch": "0", "version": "2",
                     "release": "1.nb5.0", "arch": "noarch", "summary": "Get some Plouf"}]
        self._run_nbyum_test(args, expected)

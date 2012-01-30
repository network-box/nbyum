from tests import TestCase


class TestListPackages(TestCase):
    command = "list"

    def test_list_installed_packages(self):
        """List installed packages."""
        args = [self.command, "installed", "packages"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:bar-1-1.nb5.0.noarch'},
                    {'installed': '0:foo-1-1.nb5.0.noarch'},
                    {'installed': '0:toto-1-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_available_packages(self):
        """List available packages."""
        args = [self.command, "available", "packages"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'available': '0:baz-2-1.nb5.0.noarch'},
                    {'available': '0:foo-1-2.nb5.0.noarch'},
                    {'available': '0:plouf-2-1.nb5.0.noarch'},
                    {'available': '0:toto-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_packages(self):
        """List all packages."""
        args = [self.command, "all", "packages"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:bar-1-1.nb5.0.noarch'},
                    {'installed': '0:foo-1-1.nb5.0.noarch'},
                    {'installed': '0:toto-1-1.nb5.0.noarch'},
                    {'available': '0:baz-2-1.nb5.0.noarch'},
                    {'available': '0:foo-1-2.nb5.0.noarch'},
                    {'available': '0:plouf-2-1.nb5.0.noarch'},
                    {'available': '0:toto-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_no_packages_match(self):
        """Make sure no packages are returned with a bogus pattern."""
        args = [self.command, "all", "packages", "no_such_package"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = []

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_packages_match(self):
        """List only matching packages."""
        args = [self.command, "all", "packages", "foo", "*lou*"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:foo-1-1.nb5.0.noarch'},
                    {'available': '0:plouf-2-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

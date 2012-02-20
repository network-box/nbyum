from tests import TestCase


class TestInfo(TestCase):
    command = "info"

    def test_info_no_match(self):
        """Make sure we don't print anything if no package match."""
        args = [self.command, "no_such_package"]

        # -- Check the infos ---------------------------------------
        expected = []
        self._run_nbyum_test(args, expected)

    def test_info_simple(self):
        """Print the infos for a package."""
        args = [self.command, "foo"]

        # -- Check the infos ---------------------------------------
        expected = [{'name': 'foo', 'base_package_name': 'foo', 'license': 'MIT',
                     'epoch': '0', 'version': '1', 'release': '1.nb5.0',
                     'arch': 'noarch', 'summary': 'Get some Foo',
                     'description': 'This package provides you the joy of ' \
                                    'getting some Foo.'}]
        self._run_nbyum_test(args, expected)

    def test_info_patterns(self):
        """Print the infos for a list of packages matching a few patterns."""
        args = [self.command, "*foo*", "bar*"]

        # -- Check the infos ---------------------------------------
        expected = [{'name': 'bar', 'base_package_name': 'bar', 'license': 'MIT',
                     'epoch': '0', 'version': '1', 'release': '1.nb5.0',
                     'arch': 'noarch', 'summary': 'Get some Bar',
                     'description': 'This package provides you the joy of ' \
                                    'getting some Bar.'},
                    {'name': 'foo', 'base_package_name': 'foo', 'license': 'MIT',
                     'epoch': '0', 'version': '1', 'release': '1.nb5.0',
                     'arch': 'noarch', 'summary': 'Get some Foo',
                     'description': 'This package provides you the joy of ' \
                                    'getting some Foo.'},
                    {'name': 'nbsm-foo', 'base_package_name': 'nbsm-foo',
                     'license': 'MIT', 'epoch': '0', 'version': '1',
                     'release': '1.nb5.0', 'arch': 'noarch',
                     'summary': 'Security Module to get some Foo',
                     'description': 'This package provides you the joy of ' \
                                    'getting some Foo.'},
                    ]
        self._run_nbyum_test(args, expected)

    def test_info_apostrophes(self):
        """Print the infos, including apostrophes."""
        args = [self.command, "bdummy"]

        # -- Check the infos ---------------------------------------
        expected = [{'name': 'bdummy', 'base_package_name': 'bdummy', 'license': 'MIT',
                     'epoch': '0', 'version': '1', 'release': '1.nb5.0',
                     'arch': 'noarch', 'summary': 'Not just any dummy',
                     'description': 'This package provides bochecha\'s ' \
                                    'dummy.\n\nThe main "feature" is to make' \
                                    ' it\'s alright to have apostrophes in a' \
                                    ' field, so\nlet\'s add one more :\'}"'}]
        self._run_nbyum_test(args, expected)

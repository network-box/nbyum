from tests import TestCase


class TestInfo(TestCase):
    command = "info"

    def test_info_no_match(self):
        """Make sure we don't print anything if no package match."""
        args = [self.command, "no_such_package"]

        # -- Check the infos ---------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."}]
        self._run_nbyum_test(args, expected)

    def test_info_simple(self):
        """Print the infos for a package."""
        args = [self.command, "foo"]

        # -- Check the infos ---------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap", "pkginfos": [{"name": "foo", "license": "MIT", "base_package_name": "foo",
                                                    "version": "1-1.nb5.0", "arch": "noarch", "summary": "Get some Foo",
                                                    "description": "This package provides you the joy of getting some Foo."}]}]
        self._run_nbyum_test(args, expected)

    def test_info_patterns(self):
        """Print the infos for a list of packages matching a few patterns."""
        args = [self.command, "*foo*", "bar*"]

        # -- Check the infos ---------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap", "pkginfos": [{"name": "bar", "license": "MIT", "base_package_name": "bar",
                                                    "version": "1-1.nb5.0", "arch": "noarch", "summary": "Get some Bar",
                                                    "description": "This package provides you the joy of getting some Bar."},
                                                   {"name": "foo", "license": "MIT", "base_package_name": "foo",
                                                    "version": "1-1.nb5.0", "arch": "noarch", "summary": "Get some Foo",
                                                    "description": "This package provides you the joy of getting some Foo."},
                                                   {"name": "nbsm-foo", "license": "MIT", "base_package_name": "nbsm-foo",
                                                    "version": "1-1.nb5.0", "arch": "noarch", "summary": "Security Module to get some Foo",
                                                    "description": "This package provides you the joy of getting some Foo."}]}]
        self._run_nbyum_test(args, expected)

    def test_info_apostrophes(self):
        """Print the infos, including apostrophes."""
        args = [self.command, "bdummy"]

        # -- Check the infos ---------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the package metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the package metadata..."},
                    {"type": "recap", "pkginfos": [{"name": "bdummy", "license": "MIT", "base_package_name": "bdummy",
                                                    "version": "1-1.nb5.0", "arch": "noarch", "summary": "Not just any dummy",
                                                    "description": "This package provides bochecha's dummy.\n\nThe " \
                                                                   "main \"feature\" is to make it's alright to have " \
                                                                   "apostrophes in a field, so\nlet's add one more :'}\""}]}]
        self._run_nbyum_test(args, expected)

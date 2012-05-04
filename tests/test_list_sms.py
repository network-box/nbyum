from tests import TestCase


class TestListSMs(TestCase):
    command = "list"

    def test_list_installed_sms(self):
        """List installed sms."""
        args = [self.command, "installed", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "nbsm-foo", "version": "1-1.nb5.0", "summary": "Security Module to get some Foo"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_available_sms(self):
        """List available sms."""
        args = [self.command, "available", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "available": [{"name": "nbsm-bar", "version": "1-1.nb5.0", "summary": "Security Module to meet Toto"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_sms(self):
        """List all sms."""
        args = [self.command, "all", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "nbsm-foo", "version": "1-1.nb5.0", "summary": "Security Module to get some Foo"}],
                     "available": [{"name": "nbsm-bar", "version": "1-1.nb5.0", "summary": "Security Module to meet Toto"}]}]
        self._run_nbyum_test(args, expected)

    def test_list_no_sms_match(self):
        """Make sure no sms are returned with a bogus pattern."""
        args = [self.command, "all", "sms", "no_such_sm"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."}]
        self._run_nbyum_test(args, expected)

    def test_list_sms_match(self):
        """List only matching sms."""
        args = [self.command, "all", "sms", "nbsm-foo", "*a*"]

        # -- Check the listing -------------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "installed": [{"name": "nbsm-foo", "version": "1-1.nb5.0", "summary": "Security Module to get some Foo"}],
                     "available": [{"name": "nbsm-bar", "version": "1-1.nb5.0", "summary": "Security Module to meet Toto"}]}]
        self._run_nbyum_test(args, expected)

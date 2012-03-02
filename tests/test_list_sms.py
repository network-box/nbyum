from tests import TestCase


class TestListSMs(TestCase):
    command = "list"

    def test_list_installed_sms(self):
        """List installed sms."""
        args = [self.command, "installed", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "nbsm-foo", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"}]
        self._run_nbyum_test(args, expected)

    def test_list_available_sms(self):
        """List available sms."""
        args = [self.command, "available", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "available", "name": "nbsm-bar", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"}]
        self._run_nbyum_test(args, expected)

    def test_list_sms(self):
        """List all sms."""
        args = [self.command, "all", "sms"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "nbsm-foo", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"},
                    {"status": "available", "name": "nbsm-bar", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"}]
        self._run_nbyum_test(args, expected)

    def test_list_no_sms_match(self):
        """Make sure no sms are returned with a bogus pattern."""
        args = [self.command, "all", "sms", "no_such_sm"]

        # -- Check the listing -------------------------------------
        expected = []
        self._run_nbyum_test(args, expected)

    def test_list_sms_match(self):
        """List only matching sms."""
        args = [self.command, "all", "sms", "nbsm-foo", "*a*"]

        # -- Check the listing -------------------------------------
        expected = [{"status": "installed", "name": "nbsm-foo", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"},
                    {"status": "available", "name": "nbsm-bar", "epoch": "0",
                                   "version": "1", "release": "1.nb5.0",
                                   "arch": "noarch"}]
        self._run_nbyum_test(args, expected)

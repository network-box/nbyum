from tests import TestCase


class TestListSMs(TestCase):
    command = "list"

    def test_list_installed_sms(self):
        """List installed sms."""
        args = [self.command, "installed", "sms"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:nbsm-foo-1-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_available_sms(self):
        """List available sms."""
        args = [self.command, "available", "sms"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'available': '0:nbsm-bar-1-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_sms(self):
        """List all sms."""
        args = [self.command, "all", "sms"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:nbsm-foo-1-1.nb5.0.noarch'},
                    {'available': '0:nbsm-bar-1-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_no_sms_match(self):
        """Make sure no sms are returned with a bogus pattern."""
        args = [self.command, "all", "sms", "no_such_sm"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = []

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

    def test_list_sms_match(self):
        """List only matching sms."""
        args = [self.command, "all", "sms", "nbsm-foo", "*a*"]
        self._run_nbyum_test(args)

        # -- Check the listing -------------------------------------
        expected = [{'installed': '0:nbsm-foo-1-1.nb5.0.noarch'},
                    {'available': '0:nbsm-bar-1-1.nb5.0.noarch'}]

        result = [eval(line) for line in self.stdout.split("\n") if line]
        self.assertEqual(result, expected)

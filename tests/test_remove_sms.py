import os
import unittest2

from tests import TestCase


class TestRemoveSms(TestCase):
    command = "remove"

    @unittest2.skipIf(os.getuid() != 0, "Removals must be run as root")
    def test_no_match(self):
        """Try removing an unexisting security module."""
        args = [self.command, "sms", "no_such_security_module"]

        # -- Check the error message -------------------------------
        expected = [{"error": "No Match for argument: nbsm-no_such_security_module"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the no-op ----------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    @unittest2.skipIf(os.getuid() != 0, "Removals must be run as root")
    def test_remove_sm(self):
        """Try removing a security module."""
        args = [self.command, "sms", "nbsm-foo"]

        # -- Check the removal summary -----------------------------
        expected = [{"remove": "0:nbsm-foo-1-1.nb5.0.noarch"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the removal --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    @unittest2.skipIf(os.getuid() != 0, "Removals must be run as root")
    def test_remove_sm_with_deps(self):
        """Try removing a security module and the *packages* it depends on."""
        args = [self.command, "sms", "nbsm-bidule"]

        # -- Check the removal summary -----------------------------
        expected = [{"remove": "0:nbsm-bidule-1-1.nb5.0.noarch"},
                    {"removedep": "0:bidule-1-1.nb5.0.noarch"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the removal --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]

        result = self._get_installed_rpms()
        self.assertEqual(result, expected)

    @unittest2.skipIf(os.getuid() != 0, "Removals must be run as root")
    def test_fail_to_remove_sm_with_sms_deps(self):
        """Make sure we can't remove a security module if others require it."""
        raise NotImplementedError("This test is not yet implemented")

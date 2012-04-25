import os

from tests import TestCase


class TestRemoveSms(TestCase):
    command = "remove"

    def test_no_match(self):
        """Try removing an unexisting security module."""
        args = [self.command, "sms", "no_such_security_module"]

        # -- Check the error message -------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "error", "message": "No Match for argument: nbsm-no_such_security_module"}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the no-op ----------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_remove_sm(self):
        """Try removing a security module."""
        args = [self.command, "sms", "nbsm-foo"]

        # -- Check the removal summary -----------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 1, "hint": "Removed: nbsm-foo"},
                    {"type": "remove", "pkgs": [{"name": "nbsm-foo", "old": "1-1.nb5.0", "reason": ""}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the removal --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_remove_sm_with_deps(self):
        """Try removing a security module and the *packages* it depends on."""
        # -- Setup: install a security module with deps ------------
        # This can't be done as part of the setUp because then yum
        # won't identify the leaves to remove
        self._install_packages_setup(["nbsm-bidule"])

        args = [self.command, "sms", "nbsm-bidule"]

        # -- Check the removal summary -----------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "progress", "current": 1, "total": 2, "hint": "Removed: nbsm-bidule"},
                    {"type": "progress", "current": 2, "total": 2, "hint": "Removed: bidule"},
                    {"type": "remove", "pkgs": [{"name": "nbsm-bidule", "old": "1-1.nb5.0", "reason": ""},
                                                {"name": "bidule", "old": "1-1.nb5.0", "reason": ""}]}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the removal --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

    def test_fail_to_remove_sm_with_sms_deps(self):
        """Make sure we can't remove a security module if others require it."""
        # -- Setup: install a security module with deps ------------
        # This can't be done as part of the setUp because then yum
        # won't identify the leaves to remove
        self._install_packages_setup(["nbsm-trucmuche", "nbsm-machin"])

        args = [self.command, "sms", "nbsm-bidule"]

        # -- Check the removal summary -----------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "error", "message": "Proceeding would remove the following security modules:\n  - nbsm-machin\n  - nbsm-trucmuche\nTransaction aborted."}]
        self._run_nbyum_test(args, expected)

        # -- Check the installed packages after the removal --------
        expected = ["0:bar-1-1.nb5.0.noarch",
                    "0:bidule-1-1.nb5.0.noarch",
                    "0:foo-1-1.nb5.0.noarch",
                    "0:nbsm-bidule-1-1.nb5.0.noarch",
                    "0:nbsm-foo-1-1.nb5.0.noarch",
                    "0:nbsm-machin-1-1.nb5.0.noarch",
                    "0:nbsm-trucmuche-1-1.nb5.0.noarch",
                    "0:toto-1-1.nb5.0.noarch"]
        self._check_installed_rpms(expected)

from tests import TestCase


class TestCheckUpdate(TestCase):
    command = "check-update"
    installonlypkgs = "bar"

    def test_no_updates(self):
        """Check a repo with no available updates."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = []
        self._run_nbyum_test(args, expected)

    def test_only_updates(self):
        """Check a repo with only updates available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]}]
        self._run_nbyum_test(args, expected)

    def test_only_install(self):
        """Check a repo with only new installs available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': {"name": "bar", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}}]
        self._run_nbyum_test(args, expected)

    def test_only_obsoletes(self):
        """Check a repo with only obsoletes available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': [{"name": "bar", "epoch": "0", "version": "1",
                                   "release": "1.nb5.0", "arch": "noarch"},
                                  {"name": "baz", "epoch": "0", "version": "2",
                                   "release": "1.nb5.0", "arch": "noarch"}]}]
        self._run_nbyum_test(args, expected)

    def test_install_as_dep(self):
        """Check a repo with an update requiring a new install."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}}]
        self._run_nbyum_test(args, expected)

    def test_ordering(self):
        """Check the ordering of the summary for a repo with a bit of everything available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'obsolete': [{"name": "bar", "epoch": "0", "version": "1",
                                   "release": "1.nb5.0", "arch": "noarch"},
                                  {"name": "baz", "epoch": "0", "version": "2",
                                   "release": "1.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}}]
        self._run_nbyum_test(args, expected)

    def test_ordering_bis(self):
        """Check the ordering of the summary for a repo with a bit of everything available, bis."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{'install': {"name": "bar", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}},
                    {'update': [{"name": "foo", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "foo", "epoch": "0", "version": "1",
                                 "release": "2.nb5.0", "arch": "noarch"}]},
                    {'update': [{"name": "toto", "epoch": "0", "version": "1",
                                 "release": "1.nb5.0", "arch": "noarch"},
                                {"name": "toto", "epoch": "0", "version": "2",
                                 "release": "1.nb5.0", "arch": "noarch"}]},
                    {'installdep': {"name": "plouf", "epoch": "0", "version": "2",
                                    "release": "1.nb5.0", "arch": "noarch"}}]
        self._run_nbyum_test(args, expected)

from tests import TestCase


class TestCheckUpdate(TestCase):
    command = "check-update"
    installonlypkgs = "bar"

    def test_no_updates(self):
        """Check a repo with no available updates."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "log", "info": "Packages are all up to date"}]
        self._run_nbyum_test(args, expected)

    def test_only_updates(self):
        """Check a repo with only updates available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "update": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

    def test_only_install(self):
        """Check a repo with only new installs available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "install": [{"name": "bar", "new": "1-2.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

    def test_only_obsoletes(self):
        """Check a repo with only obsoletes available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "remove": [{"name": "bar", "old": "1-1.nb5.0", "reason": "Replaced by baz-2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

    def test_install_as_dep(self):
        """Check a repo with an update requiring a new install."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "install": [{"name": "plouf", "new": "2-1.nb5.0"}],
                     "update": [{"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

    def test_mixup(self):
        """Check a repo with a bit of everything available."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "install": [{"name": "plouf", "new": "2-1.nb5.0"}],
                     "update": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"},
                                {"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}],
                     "remove": [{"name": "bar", "old": "1-1.nb5.0", "reason": "Replaced by baz-2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

    def test_mixup_bis(self):
        """Check a repo with a bit of everything available, bis."""
        args = [self.command]

        # -- Check the update summary ------------------------------
        expected = [{"type": "progress", "current": 0, "total": 1, "hint": "Downloading the packages metadata..."},
                    {"type": "progress", "current": 0, "total": 1, "hint": "Processing the packages metadata..."},
                    {"type": "recap",
                     "install": [{"name": "bar", "new": "1-2.nb5.0"},
                                 {"name": "plouf", "new": "2-1.nb5.0"}],
                     "update": [{"name": "foo", "old": "1-1.nb5.0", "new": "1-2.nb5.0"},
                                {"name": "toto", "old": "1-1.nb5.0", "new": "2-1.nb5.0"}]}]
        self._run_nbyum_test(args, expected)

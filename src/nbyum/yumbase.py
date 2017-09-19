import fnmatch
from itertools import groupby, ifilter
from operator import attrgetter
import os

import yum
from yum.update_md import UpdateMetadata

from .errors import NBYumException, WTFException
from .logging_hijack import NBYumRPMCallback
from .utils import get_version, list_ordergetter, transaction_ordergetter


class NBYumBase(yum.YumBase):
    def clean_cache(self):
        """Clean the local cache"""
        self.logger.log_progress({"current": 0, "total": 1,
                                  "hint": "Cleaning up the Yum cache..."})

        def run_clean(func_name, obj):
            clean_func = getattr(self, func_name)
            code, results = clean_func()

            if code != 0:
                raise NBYumException("Could not clean cached %s:\n    - %s"
                                     % (obj, "\n    - ".join(pkgresults)))

        # TODO: How to clean all repositories, even disabled ones?
        run_clean("cleanPackages", "packages")
        run_clean("cleanHeaders", "headers")
        run_clean("cleanMetadata", "XML metadata")
        run_clean("cleanSqlite", "SQLite metadata")
        run_clean("cleanRpmDB", "RPM DB")

        self.plugins.run('clean')

    def prepare(self):
        """Prepare for the user's request

        This implies getting the various repository metadata.
        """
        self.setCacheDir()

        if not self.conf.cache:
            # If we force the cache usage, the next operation will not imply a
            # download, so don't log in that case
            self.logger.log_progress({"current": 0, "total": 1,
                                      "hint": "Downloading the package "
                                              "metadata..."})

        self._getSacks()

        self.updatemd = UpdateMetadata(self.repos.listEnabled())

    def __cleanup_transaction_file(self):
        """Remove the saved transaction file.

        Yum will always save a transaction file every time we use the
        buildTransaction() function.

        That's quite useful for yum-complete-transaction.

        But then, when we don't run processTransaction() (e.g on check-update),
        we need to remove those files ourselves.
        """
        if self._ts_save_file is not None:
            try:
                os.unlink(self._ts_save_file)
            except (IOError, OSError), e:
                self.verbose_logger.warning(
                        "Could not remove transaction file (%s): %s",
                        self._ts_save_file, e)
            self._ts_save_file = None

    def __get_packages_list(self, patterns, type_filter=None,
                            hidden_filter=None, status="all"):
        """Get a packages list."""
        if type_filter is None:
            type_filter = lambda x: True

        if hidden_filter is None:
            hidden_filter = lambda x: True

        if status == "installed":
            source = self.rpmdb

        else:
            source = self.pkgSack

        # match_tuple is (exact_matches, glob_matches, unmatched_patterns)
        match_tuple = source.matchPackageNames(patterns)
        matches = set(match_tuple[0] + match_tuple[1])

        # Filter on sms or packages
        pkgs = ifilter(type_filter, matches)

        if status == "available":
            # Don't show installed packages if we asked for available ones
            pkgs = ifilter(lambda x: not self.rpmdb.installed(po=x), pkgs)

        def actually_match_on_name(pkg):
            """Do what matchPackageNames should already be doing

            Yum developers, if you name an API matchPackage**Names**, make it
            match packages on their name, not envra!
            """
            for pattern in patterns:
                if fnmatch.fnmatch(pkg.name, pattern):
                    return True

        if patterns != ['*']:
            pkgs = ifilter(actually_match_on_name, pkgs)

        # We need to sort before using groupby
        pkgs = sorted(pkgs, key=attrgetter("name"))

        for name, group in groupby(pkgs, attrgetter("name")):
            best = self.bestPackagesFromList(group)
            for pkg in best:
                if hidden_filter(pkg):
                    yield pkg

    def __get_unexpected_sms(self, patterns):
        """List the security modules we didn't expect in the transation"""
        unexpected = []
        for pkg in self.tsInfo.getMembers():
            if pkg.name.startswith("nbsm-"):
                unexpected.append(pkg.name)
                for pattern in patterns:
                    if fnmatch.fnmatch(pkg.name, pattern):
                        unexpected.remove(pkg.name)
                        break

        return unexpected

    def __smsize_patterns(self, patterns):
        """Pre-process patterns when matching security modules.

        If a user specifies a pattern like 'b*', then the 'nbsm-base' security
        module should match.
        """
        result = []
        for pattern in patterns:
            if not pattern.startswith("nbsm"):
                pattern = "nbsm-%s" % pattern

            result.append(pattern)

        return result

    def __hidden_filter(self, pkg):
        return pkg.group != "nbhidden"

    def __pkgs_filter(self, pkg):
        return not pkg.name.startswith("nbsm-")

    def __sms_filter(self, pkg):
        return pkg.name.startswith("nbsm-")

    def __sanitize_patterns(self, patterns, type_):
        """Make sure the patterns are sound."""
        if not patterns:
            patterns = ["*"]

        if type_ == "sms":
            # Special case for the security modules
            patterns = self.__smsize_patterns(patterns)

        return patterns

    def get_infos(self, patterns):
        """Get some infos on packages."""
        pkgs = []
        for pkg in sorted(self.__get_packages_list(patterns),
                          key=list_ordergetter):
            pkgdict = {"name": pkg.name, "arch": pkg.arch,
                       "version": get_version(pkg), "license": pkg.license,
                       "summary": pkg.summary, "description": pkg.description,
                       "base_package_name": pkg.base_package_name,
                       }

            # Filter multiarch dupes for arches others than the system one.
            # We can just compare with the previous one because packages
            # are ordered by nevra.
            if len(pkgs) and \
               pkgs[-1].get("name", None) == pkgdict["name"] and \
               pkgs[-1].get("version", None) == pkgdict["version"]:
                # This is a multiarch dupe

                if pkgs[-1]["arch"] == self.arch.basearch and \
                   pkg.arch != self.arch.basearch:
                    continue

                elif pkgs[-1]["arch"] != self.arch.basearch and \
                     pkg.arch == self.arch.basearch:
                    pkgs.pop()

            pkgs.append(pkgdict)

        if pkgs:
            self.logger.log_recap({"pkginfos": pkgs})

    def get_last_updated(self):
        # Transactions seem to already be ordered reverse-chronologically, but
        # who knows if we can depend on that :x
        old_tx = sorted(self.history.old([], complete_transactions_only=True),
                        key=attrgetter("end_timestamp"), reverse=True)

        for tx in old_tx:
            for pkg in tx.trans_data:
                # Search for at least one package having been updated
                if pkg.state not in ("Update", "Obsoleted", "Install"):
                    continue

                return tx.end_timestamp

    def install_packages(self, type_, patterns):
        """Install packages and security modules."""
        patterns = self.__sanitize_patterns(patterns, type_)

        for pattern in patterns:
            # FIXME: What if a pattern matches `nbsm-*' and type is `packages'?
            self.install(pattern=pattern)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s"
                                 % str.join("\n", resmsg))

        # Check that this won't install security modules unexpectedly
        unexpectedly_installed_sms = self.__get_unexpected_sms(patterns)

        if unexpectedly_installed_sms:
            msg = ("Installation depends on the following security "
                   "module%s:\n  %s\nTransaction aborted.\nPlease explicitly "
                   "install all required security modules."
                   % (len(unexpectedly_installed_sms)>1 and "s" or "",
                      " ".join(unexpectedly_installed_sms)))
            raise NBYumException(msg)

        if len(self.tsInfo.getMembers()):
            self.processTransaction(rpmDisplay=NBYumRPMCallback())

    def list_packages(self, type_, status, patterns, show_hidden=False):
        """List packages and security modules."""
        if type_ == "sms":
            type_filter = self.__sms_filter

        else:
            type_filter = self.__pkgs_filter

        if not show_hidden:
            hidden_filter = self.__hidden_filter

        else:
            hidden_filter = lambda x: True

        patterns = self.__sanitize_patterns(patterns, type_)

        installed = []
        if status in ("all", "installed"):
            pkgs = self.__get_packages_list(patterns, type_filter,
                                            status="installed")

            for pkg in sorted(pkgs, key=list_ordergetter):
                pkgdict = {"name": pkg.name, "version": get_version(pkg),
                           "summary": pkg.summary,
                           "description": pkg.description}

                # Filter multiarch dupes for arches others than the system one.
                # We can just compare with the previous one because packages
                # are ordered by nevra.
                if len(installed) and \
                   installed[-1].get("name", None) == pkgdict["name"] and \
                   installed[-1].get("version", None) == pkgdict["version"]:
                    # This is a multiarch dupe

                    if previous_arch == self.arch.basearch and \
                       pkg.arch != self.arch.basearch:
                        continue

                    elif previous_arch != self.arch.basearch and \
                         pkg.arch == self.arch.basearch:
                        installed.pop()

                installed.append(pkgdict)

                # Keep for next iteration
                previous_arch = pkg.arch

        available = []
        if status in ("all", "available"):
            pkgs = self.__get_packages_list(patterns, type_filter,
                                            hidden_filter=hidden_filter,
                                            status="available")

            for pkg in sorted(pkgs, key=list_ordergetter):
                if type_ == "sms" and self.rpmdb.installed(name=pkg.name):
                    # For security modules, we only want to show the ones that
                    # are **not installed**, even if in a different version
                    continue

                pkgdict = {"name": pkg.name, "version": get_version(pkg),
                           "summary": pkg.summary,
                           "description": pkg.description}

                # Filter multiarch dupes for arches others than the system one.
                # We can just compare with the previous one because packages
                # are ordered by nevra.
                if len(available) and \
                   available[-1].get("name", None) == pkgdict["name"] and \
                   available[-1].get("version", None) == pkgdict["version"]:
                    # This is a multiarch dupe!

                    if previous_arch == self.arch.basearch and \
                       pkg.arch != self.arch.basearch:
                        continue

                    elif previous_arch != self.arch.basearch and \
                         pkg.arch == self.arch.basearch:
                        available.pop()

                available.append(pkgdict)

                # Keep for next iteration
                previous_arch = pkg.arch

        pkgs = {}
        if installed:
            pkgs["installed"] = installed
        if available:
            pkgs["available"] = available

        if pkgs:
            self.logger.log_recap(pkgs)

    def remove_packages(self, type_, patterns):
        """Remove packages and security modules."""
        patterns = self.__sanitize_patterns(patterns, type_)

        for pattern in patterns:
            # FIXME: What if a pattern matches `nbsm-*' and type is `packages'?
            self.remove(pattern=pattern)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        # Check that this won't remove security modules unexpectedly
        unexpectedly_removed_sms = self.__get_unexpected_sms(patterns)

        if unexpectedly_removed_sms:
            msg = "Proceeding would remove the following " \
                  "security module%s:\n  - %s\nTransaction aborted." \
                      % (len(unexpectedly_removed_sms)>1 and "s" or "",
                         '\n  - '.join(unexpectedly_removed_sms))
            raise NBYumException(msg)

        if len(self.tsInfo.getMembers()):
            # FIXME: We only need the installroot parameter to work around a Yum bug:
            #     https://bugzilla.redhat.com/show_bug.cgi?id=684686#c6
            # When it's fixed, just nuke it out of here
            self.processTransaction(rpmDisplay=NBYumRPMCallback(installroot=self.conf.installroot))

    def update_packages(self, patterns, apply=False):
        """Check for updates and optionally apply."""
        if patterns:
            for pattern in patterns:
                self.update(pattern=pattern)
        else:
            self.update()

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        if not len(self.tsInfo.getMembers()):
            self.verbose_logger.info("All packages are up to date.")

        elif apply:
            self.processTransaction(rpmDisplay=NBYumRPMCallback())

        else:
            self.__cleanup_transaction_file()

    def recap_transaction(self):
        """Print a summary of the transaction."""
        suggest_reboot = False

        pkgs = {}

        for member in sorted(self.tsInfo.getMembers(),
                             key=transaction_ordergetter):
            pkg = {"name": member.name}

            if not suggest_reboot:
                for po in self.rpmdb.searchNevra(name=member.po.name,
                                                 arch=member.po.arch):
                    notices = self.updatemd.get_applicable_notices(po.pkgtup)

                    for (pkgtup, notice) in notices:
                        if notice["reboot_suggested"]:
                            suggest_reboot = True

            # Packages newly installed (install_only when running an update)
            if member.ts_state == "i":
                pkg.update({"new": get_version(member.po)})

                if not pkgs.has_key("install"):
                    pkgs["install"] = []

                pkgs["install"].append(pkg)

            # Packages being removed
            elif member.ts_state == "e":
                pkg.update({"old": get_version(member.po), "reason": ""})

                if not pkgs.has_key("remove"):
                    pkgs["remove"] = []

                pkgs["remove"].append(pkg)

            # Packages obsoleted by a new one
            elif member.ts_state == "od":
                # Those are handled along with their obsoleter
                continue

            # Packages replaced by a newer update
            elif member.ts_state == "ud":
                # Those are handled along with their updater
                continue

            # Packages being the actual update/obsoleter...
            # or a new dependency, or even a new install >_<
            elif member.ts_state == "u":
                pkg.update({"new": get_version(member.po)})

                if not member.updates and not member.obsoletes:
                    # This is a new install
                    if not pkgs.has_key("install"):
                        pkgs["install"] = []

                    pkgs["install"].append(pkg)

                else:
                    for old in member.updates:
                        pkg.update({"old": get_version(old)})

                        if not pkgs.has_key("update"):
                            pkgs["update"] = []

                        pkgs["update"].append(pkg)

                    # Obsoletions are sometimes an install...
                    if member.obsoletes and not member.updates:
                        if not pkgs.has_key("install"):
                            pkgs["install"] = []

                        pkgs["install"].append(pkg)

                    # ... but they always are removals
                    for old in member.obsoletes:
                        pkg = {"name": old.name, "old": get_version(old),
                               "reason": "Replaced by %s-%s" % \
                                   (member.name, get_version(member))}

                        if not pkgs.has_key("remove"):
                            pkgs["remove"] = []

                        pkgs["remove"].append(pkg)

            else:
                msg = "The package %s has the state '%s' in the current " \
                      "transaction. We don't handle those states yet. Please" \
                      " report it as a bug." % (member.po, member.ts_state)
                raise WTFException(msg)

        if pkgs:
            self.logger.log_recap(pkgs)

        if suggest_reboot:
            self.verbose_logger.info("This update requires a reboot")

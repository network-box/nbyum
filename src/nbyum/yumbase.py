import fnmatch
import os

import yum

from .errors import NBYumException, WTFException
from .logging_hijack import NBYumRPMCallback
from .utils import get_version, list_ordergetter, transaction_ordergetter


class NBYumBase(yum.YumBase):
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

    def __get_packages_list(self, patterns, filter_, status="all"):
        """Get a packages list."""
        if status == "installed":
            source = self.rpmdb
        else:
            source = self.pkgSack

        # match_tuple is (exact_matches, glob_matches, unmatched_patterns)
        match_tuple = source.matchPackageNames(patterns)
        matches = set(match_tuple[0] + match_tuple[1])

        for pkg in filter(filter_, matches):
            if status == "available" and self.rpmdb.installed(po=pkg):
                continue

            for pattern in patterns:
                # Yum developers, if you name an API matchPackageNames,
                # make it match packages on their name, not envra!
                if fnmatch.fnmatch(pkg.name, pattern):
                    yield pkg
                    break

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

    def __type_and_patterns_preprocessor(self, type_, patterns):
        """Get the type filter and make sure the patterns are sound."""
        if not patterns:
            patterns = ["*"]

        if type_ == "sms":
            type_filter = lambda x: x.name.startswith("nbsm-")

            # Special case for the security modules
            patterns = self.__smsize_patterns(patterns)

        elif type_ == "packages":
            type_filter = lambda x: not x.name.startswith("nbsm-")

        else:
            raise WTFException("Somehow you managed to pass an unhandled " \
                               "value for the listing type (%s). Please " \
                               "report it as a bug." % type_)

        return type_filter, patterns

    def get_infos(self, patterns):
        """Get some infos on packages."""
        # We don't want to filter here, unlike for listings
        type_filter = lambda x: True

        pkgs = []
        for pkg in sorted(self.__get_packages_list(patterns, type_filter),
                          key=list_ordergetter):
            pkgdict = {"name": pkg.name, "arch": pkg.arch,
                       "version": get_version(pkg), "license": pkg.license,
                       "summary": pkg.summary, "description": pkg.description,
                       "base_package_name": pkg.base_package_name,
                       }

            pkgs.append(pkgdict)

        if pkgs:
            self.logger.log_recap({"pkginfos": pkgs})

    def install_packages(self, type_, patterns):
        """Install packages and security modules."""
        type_filter, patterns = self.__type_and_patterns_preprocessor(type_,
                                                                      patterns)

        for pattern in patterns:
            # FIXME: What if a pattern matches `nbsm-*' and type is `packages'?
            self.install(pattern=pattern)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        if len(self.tsInfo.getMembers()):
            self.processTransaction(rpmDisplay=NBYumRPMCallback())

    def list_packages(self, type_, status, patterns):
        """List packages and security modules."""
        type_filter, patterns = self.__type_and_patterns_preprocessor(type_,
                                                                      patterns)

        installed = []
        if status in ("all", "installed"):
            for pkg in sorted(self.__get_packages_list(patterns, type_filter,
                                                       status="installed"),
                              key=list_ordergetter):
                pkgdict = {"name": pkg.name, "version": get_version(pkg),
                           "summary": pkg.summary}

                installed.append(pkgdict)

        available = []
        if status in ("all", "available"):
            for pkg in sorted(self.__get_packages_list(patterns, type_filter,
                                                       status="available"),
                              key=list_ordergetter):
                if type_ == "sms" and self.rpmdb.installed(name=pkg.name):
                    # For security modules, we only want to show the ones that
                    # are **not installed**, even if in a different version
                    continue

                pkgdict = {"name": pkg.name, "version": get_version(pkg),
                           "summary": pkg.summary}

                available.append(pkgdict)

        pkgs = {}
        if installed:
            pkgs["installed"] = installed
        if available:
            pkgs["available"] = available

        if pkgs:
            self.logger.log_recap(pkgs)

    def remove_packages(self, type_, patterns):
        """Remove packages and security modules."""
        type_filter, patterns = self.__type_and_patterns_preprocessor(type_,
                                                                      patterns)

        for pattern in patterns:
            # FIXME: What if a pattern matches `nbsm-*' and type is `packages'?
            self.remove(pattern=pattern)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        # Check that this won't remove security modules unexpectedly
        unexpectedly_removed_sms = []
        for pkg in self.tsInfo.getMembers():
            if pkg.name.startswith("nbsm-"):
                unexpectedly_removed_sms.append(pkg.name)
                for pattern in patterns:
                    if fnmatch.fnmatch(pkg.name, pattern):
                        unexpectedly_removed_sms.remove(pkg.name)
                        break

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
        pkgs = {}

        for member in sorted(self.tsInfo.getMembers(),
                             key=transaction_ordergetter):
            pkg = {"name": member.name}

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
                    if not pkgs.has_key("install"):
                        pkgs["install"] = []

                    pkgs["install"].append(pkg)
                else:
                    for old in member.updates:
                        pkg.update({"old": get_version(old)})

                        if not pkgs.has_key("update"):
                            pkgs["update"] = []

                        pkgs["update"].append(pkg)

                    # Obsoletions are considered as removals, start fresh
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

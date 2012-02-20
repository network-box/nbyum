import fnmatch
import json
import os

import yum

from errors import NBYumException, WTFException
from utils import get_envra, list_ordergetter, transaction_ordergetter


info_attrs = ("name", "base_package_name", "license", "epoch", "version",
              "release", "arch", "summary", "description")


class NBYumBase(yum.YumBase):
    def __get_packages_list(self, patterns, filter_):
        """Get a packages list."""
        # match_tuple is (exact_matches, glob_matches, unmatched_patterns)
        match_tuple = self.pkgSack.matchPackageNames(patterns)
        matches = set(match_tuple[0] + match_tuple[1])

        for pkg in filter(filter_, matches):
            if self.rpmdb.installed(po=pkg):
                status = "installed"
            else:
                status = "available"

            for pattern in patterns:
                # Yum developers, if you name an API matchPackageNames,
                # make it match packages on their name, not envra!
                if fnmatch.fnmatch(pkg.name, pattern):
                    yield status, pkg
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

    def get_infos(self, patterns):
        """Get some infos on packages."""
        # We don't want to filter here, unlike for listings
        type_filter = lambda x: True

        for pkg_status, pkg in sorted(self.__get_packages_list(patterns,
                                                               type_filter),
                                      key=list_ordergetter):
            print(json.dumps(dict((name, getattr(pkg, name)) for name in info_attrs)))

    def install_packages(self, type_, patterns):
        """Install packages and security modules."""
        if type_ == "sms":
            # Special case for the security modules
            patterns = self.__smsize_patterns(patterns)
        else:
            raise WTFException("Somehow you managed to pass an unhandled " \
                               "value for the installing type (%s). Please " \
                               "report it as a bug." % type_)

        for pattern in patterns:
            self.install(pattern=pattern)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2 and len(self.tsInfo.getMembers()):
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        if len(self.tsInfo.getMembers()):
            self.processTransaction(rpmDisplay=self.nbyum_rpmDisplay)

    def list_packages(self, type_, status, patterns):
        """List packages and security modules."""
        if type_ == "sms":
            type_filter = lambda x: x.name.startswith("nbsm-")
        elif type_ == "packages":
            type_filter = lambda x: not x.name.startswith("nbsm-")
        else:
            raise WTFException("Somehow you managed to pass an unhandled " \
                               "value for the listing type (%s). Please " \
                               "report it as a bug." % type_)

        if not patterns:
            patterns = ["*"]

        if type_ == "sms":
            # Special case for the security modules
            patterns = self.__smsize_patterns(patterns)

        for pkg_status, pkg in sorted(self.__get_packages_list(patterns,
                                                               type_filter),
                                      key=list_ordergetter):
            if status == "all" or status == pkg_status:
                print(json.dumps({pkg_status: get_envra(pkg)}))

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

        if apply and len(self.tsInfo.getMembers()):
            self.processTransaction(rpmDisplay=self.nbyum_rpmDisplay)

    def recap_transaction(self):
        """Print a summary of the transaction."""
        # Interesting stuff for the future:
        #   - member.repoid (string: 'experimental', 'installed', ...
        for member in sorted(self.tsInfo.getMembers(),
                             key=transaction_ordergetter):
            # Packages newly installed (install_only when running an update)
            if member.ts_state == "i":
                print(json.dumps({"install": get_envra(member)}))
                continue

            # Packages obsoleted by a new one
            elif member.ts_state == "od":
                envra_old = get_envra(member)

                if len(member.obsoleted_by) > 1:
                    # TODO: Why would that ever happen? o_O
                    msg = ["For some reason, '%s' is obsoleted by a bunch of packages:" % envra_old]
                    for pkg in member.obsoleted_by:
                        msg.append("    %s" % (get_envra(pkg)))
                    raise WTFException("\n".join(msg))

                print(json.dumps({"obsolete": (envra_old,
                                               get_envra(member.obsoleted_by[0]))}))
                continue

            # Packages replaced by a newer update
            elif member.ts_state == "ud":
                envra_old = get_envra(member)

                if len(member.updated_by) > 1:
                    # TODO: Why would that ever happen? o_O
                    msg = ["For some reason, '%s' is updated by a bunch of packages:" % envra_old]
                    for pkg in member.updated_by:
                        msg.append("    %s" % (get_envra(pkg)))
                    raise WTFException("\n".join(msg))

                print(json.dumps({"update": (envra_old,
                                             get_envra(member.updated_by[0]))}))
                continue

            # Packages being the actual update/obsoleter...
            # or a new dependency, or even a new install >_<
            elif member.ts_state == "u":
                if member.isDep:
                    print(json.dumps({"installdep": get_envra(member)}))
                    continue

                if not member.updates and not member.obsoletes:
                    # Packages newly installed (when running 'install')
                    print(json.dumps({"install": get_envra(member)}))
                    continue

            else:
                msg = "The transaction includes a package of state '%s'," \
                      " but those are not handled yet." \
                      " Ask your friendly nbyum developer!" % member.ts_state
                raise WTFException(msg)

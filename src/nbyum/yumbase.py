from operator import attrgetter

import yum

from errors import NBYumException, WTFException
from utils import get_envra


install_tmpl = "{'install': '%s'}"
installdep_tmpl = "{'installdep': '%s'}"
update_tmpl = "{'update': ('%s', '%s')}"


class NBYumBase(yum.YumBase):
    def update_packages(self, packages, apply=False):
        """Check for updates and optionally apply."""
        updates = self.up

        if updates is None:
            # we're _only_ called after updates are setup
            # TODO: is that really an error case?
            raise WTFException("Not sure what happened here, ask Mathieu :-/")

        # Get packages to be updated
        for (new, old) in updates.getUpdatesTuples():
            if not old.name in packages:
                continue

            updating = self.getPackageObject(new)
            updated = self.rpmdb.searchPkgTuple(old)[0]

            self.tsInfo.addUpdate(updating, updated)

        # Get packages to be obsoleted
        for (obs, inst) in updates.getObsoletesTuples():
            if not inst.name in packages:
                continue

            obsoleting = self.getPackageObject(obs)
            installed = self.rpmdb.searchPkgTuple(inst)[0]

            self.tsInfo.addObsoleting(obsoleting, installed)
            self.tsInfo.addObsoleted(installed, obsoleting)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2:
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

        if apply:
            self.processTransaction()

    def recap_transaction(self):
        """Print a summary of the transaction."""
        # Interesting stuff for the future:
        #   - member.obsoleted_by (other member)
        #   - member.repoid (string: 'experimental', 'installed', ...
        for member in sorted(self.tsInfo.getMembers(),
                             key=attrgetter("ts_state")):
            # Packages newly installed
            if member.ts_state == "i":
                envra = get_envra(member)

                if member.isDep:
                    tmpl = installdep_tmpl
                else:
                    tmpl = install_tmpl

                print(tmpl % envra)
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

                new = member.updated_by[0]
                envra_new = get_envra(new)

                print(update_tmpl % (envra_old, envra_new))
                continue

            # Packages being the actual update
            elif member.ts_state == "u":
                # Those are handled with the packages to be updated above
                # TODO: Should we check that they actually are?
                continue

            else:
                msg = "The transaction includes a package of state '%s'," \
                      " but those are not handled yet." \
                      " Ask your friendly nbyum developer!"
                raise WTFException(msg)

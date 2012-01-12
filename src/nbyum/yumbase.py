import yum

from errors import NBYumException, WTFException


class NBYumBase(yum.YumBase):
    def populateUpdates(self):
        """Get the updates."""
        updates = self.up

        if updates is None:
            # we're _only_ called after updates are setup
            # TODO: is that really an error case?
            raise WTFException("Not sure what happened here, ask Mathieu :-/")

        # Get packages to be updated
        for (new, old) in updates.getUpdatesTuples():
            updating = self.getPackageObject(new)
            updated = self.rpmdb.searchPkgTuple(old)[0]

            self.tsInfo.addUpdate(updating, updated)

        # Get packages to be obsoleted
        for (obs, inst) in updates.getObsoletesTuples():
            obsoleting = self.getPackageObject(obs)
            installed = self.rpmdb.searchPkgTuple(inst)[0]

            self.tsInfo.addObsoleting(obsoleting, installed)
            self.tsInfo.addObsoleted(installed, obsoleting)

        # Get new packages to be installed as dependencies
        res, resmsg = self.buildTransaction()

        if res != 2:
            raise NBYumException("Failed to build transaction: %s" % str.join("\n", resmsg))

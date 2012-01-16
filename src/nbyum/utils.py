def get_envra(pkg):
    """Get the Epoch:Name-Version-Release.Arch representation of a package."""
    return "%s:%s-%s-%s.%s" % (pkg.epoch, pkg.name, pkg.version,
                               pkg.release, pkg.arch)

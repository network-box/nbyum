def get_envr(pkg):
    return "%s:%s-%s-%s.%s" % (pkg.epoch, pkg.name, pkg.version,
                               pkg.release, pkg.arch)

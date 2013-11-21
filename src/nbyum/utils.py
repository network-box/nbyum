import argparse
import datetime
import os
import time

from errors import NBYumException


class DummyOpts(object):
    """Just a dummy class to get the plugins to run.

    Plugins expect to be passed an optparse object so they can check if the
    user specified certain command-line arguments.

    Instances of this class will simply emulate those by providing to plugins
    the parameters they want.
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        # It seems some parts of Yum (or its plugins) have certain expectations
        # regarding the command line options. Make sure to please them
        if self.repos is None: self.repos = []

    def __getattr__(self, name):
        # We use different options depending on the case, so we might
        # sometimes try to access an option which we didn't pass to the
        # constructor. Return None for all those cases.
        return None


def get_parser():
    """Get the argument parser for the main nbyum command line tool."""
    # -- Root level arguments (-h/--help is added by default) ----------------
    parser = argparse.ArgumentParser(description="Just like yum, "
                                                 "but with a usable output")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Print some useful debug information")
    parser.add_argument("-c", "--config",
                        help="Yum configuration file to use "
                             "(default: /etc/yum.comf)")
    parser.add_argument("--force-cache", action="store_true",
                        help="Force Yum to use its local cache, as old as it "
                             "may be.")

    subparsers = parser.add_subparsers(title="subcommands")

    # -- Subcommand: check-update --------------------------------------------
    parser_checkupdate = subparsers.add_parser("check-update",
                                               help="Check for updates to "
                                                    "installed packages")
    parser_checkupdate.add_argument("patterns", nargs="*", metavar="PATTERN",
                                    help="A (list of) glob-like patterns to "
                                         "match names against, for example "
                                         "'nb*'. If none is specified, "
                                         "updates for the whole system are "
                                         "checked.")
    parser_checkupdate.set_defaults(func="check_update")

    # -- Subcommand: info ----------------------------------------------------
    parser_info = subparsers.add_parser("info",
                                        help="Get some infos about packages")
    parser_info.add_argument("patterns", nargs="+", metavar="PATTERN",
                             help="A (list of) glob-like pattern(s) to match "
                                  "names against, for example 'nb*'.")
    parser_info.set_defaults(func="info")

    # -- Subcommand: install -------------------------------------------------
    parser_install = subparsers.add_parser("install",
                                           help="Install available packages "
                                                "and security modules")
    parser_install.add_argument("type", metavar="sms",
                                choices=["sms"],
                                help="Choose between installing packages and "
                                     "security modules. The only possible "
                                     "value is 'sms' as packages installation"
                                     " is not implemented yet.")
    parser_install.add_argument("patterns", nargs="+", metavar="PATTERN",
                                help="A (list of) glob-like pattern(s) to "
                                     "match names against, for example 'nb*'.")
    parser_install.set_defaults(func="install")

    # -- Subcommand: list ----------------------------------------------------
    parser_list = subparsers.add_parser("list",
                                        help="List packages and security "
                                             "modules")
    parser_list.add_argument("filter", metavar="FILTER",
                             choices=["all", "installed", "available"],
                             help="List all, or filter on installed/available"
                                  "only. Possible values are 'all', "
                                  "'installed' and 'available'.")
    parser_list.add_argument("type", metavar="TYPE",
                             choices=["packages", "sms"],
                             help="Choose between listing packages and "
                                  "security modules. Possible values are "
                                  "'packages' and 'sms'.")
    parser_list.add_argument("patterns", nargs="*", metavar="PATTERN",
                             help="A (list of) glob-like pattern(s) to match"
                                  "names against, for example 'nb*'.")
    parser_list.set_defaults(func="list")

    # -- Subcommand: remove --------------------------------------------------
    parser_remove = subparsers.add_parser("remove",
                                          help="Remove installed packages and"
                                               "security modules")
    parser_remove.add_argument("type", metavar="sms",
                               choices=["sms"],
                               help="Choose between removing packages and "
                                    "security modules. The only possible "
                                    "value is 'sms' as packages removal is "
                                    "not implemented yet.")
    parser_remove.add_argument("patterns", nargs="+", metavar="PATTERN",
                               help="A (list of) glob-like pattern(s) to "
                                    "match names against, for example 'nb*'.")
    parser_remove.set_defaults(func="remove")

    # -- Subcommand: update --------------------------------------------------
    parser_update = subparsers.add_parser("update",
                                          help="Update packages or the whole "
                                               "system")
    parser_update.add_argument("patterns", nargs="*", metavar="PATTERN",
                               help="A (list of) glob-like patterns to match "
                                    "names against, for example 'nb*'. If "
                                    "none is specified, the whole system is "
                                    "updated.")
    parser_update.set_defaults(func="update")

    return parser

def get_version(pkg):
    """Get the Epoch:Version-release of a package."""
    if int(pkg.epoch) > 0:
        return "%s:%s-%s" % (pkg.epoch, pkg.version, pkg.release)
    else:
        return "%s-%s" % (pkg.version, pkg.release)

def list_ordergetter(pkg):
    """Return a simple ordering for package lists.

    In listings, we want the order to be defined as follows:
        - packages are ordered first by name, alphabetically,
          case-insensitively,
        - packages are then ordered by epoch, version, release and finally
          architecture.
    """
    envra = dict([(attr, getattr(pkg, attr))
                  for attr in ("name", "epoch", "version", "release", "arch")])

    # The order should be case-insensitive
    envra['name'] = envra['name'].lower()

    return "%(name)s-%(epoch)s:%(version)s-%(release)s.%(arch)s" % envra

def transaction_ordergetter(pkg):
    """Return a simple ordering for package lists.

    In the transaction summary, we want the order to be loosely defined:
        - packages should be 'grouped' by their `ts_state` (all updates
          together, all new packages together, etc...)
        - installations first, then obsoletes, then updates, etc...

    This last requirement is what makes a purely alphabetical order unsuitable,
    so we need to be more clevererer.
    """
    # Everything we don't specifically handle is ordered way last
    index = 99

    if pkg.ts_state == "i":
        # Packages coming as installonly with `nbyum update'
        index = 5
    elif pkg.ts_state == "u":
        if pkg.isDep:
            # Packages installed as dependencies
            index = 30
        elif pkg.obsoletes:
            # Packages obsoleting others
            index = 10
        elif pkg.updates:
            # Packages updating others
            index = 20
        else:
            # Packages installed with 'nbyum install' are first
            index = 0
    elif pkg.ts_state == "e":
        # Packages being removed with `nbyum remove'
        index = 40

    if not pkg.name.startswith("nbsm-"):
        index+=1

    return "%02d %s" % (index, list_ordergetter(pkg))

def ensure_privileges(command):
    """Used as a decorator to ensure a command is run as root."""
    def wrapper(self):
        if os.getuid() != 0:
            raise NBYumException("This command must be run as root")

        command(self)

    return wrapper

def get_local_datetime(timestamp):
    """Present a UTC timestamp as a datetime string in the local timezone."""
    local_datetime = datetime.datetime.fromtimestamp(timestamp).strftime("%c")

    local_tz = time.timezone / 3600.0

    if local_tz <= 0:
        # Yes, the positive offsets are negative values of time.timezones
        local_tz_sign = "+"
    else:
        local_tz_sign = "-"

    local_tz = abs(local_tz)

    local_tz_h = int(local_tz)

    def round_to_quarter(f):
        return round(f * 4.0) / 4.0

    local_tz_min = int(round_to_quarter(local_tz - local_tz_h) * 100)
    local_tz_min = (local_tz_min / 25) * 15

    if local_tz_min == 60:
        local_tz_h += 1
        local_tz_min = 0

    return "%s %s%02d%02d" % (local_datetime,
                              local_tz_sign, local_tz_h, local_tz_min)

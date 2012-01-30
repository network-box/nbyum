import argparse
import os

from errors import NBYumException


def get_parser():
    """Get the argument parser for the main nbyum command line tool."""
    # -- Root level arguments (-h/--help is added by default) ----------------
    parser = argparse.ArgumentParser(description="Just like yum, " \
                                                 "but with a usable output")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Print some useful debug information")
    parser.add_argument("-c", "--config",
                        help="Yum configuration file to use " \
                             "(default: /etc/yum.comf)")

    subparsers = parser.add_subparsers(title="subcommands")

    # -- Subcommand: check-update --------------------------------------------
    parser_checkupdate = subparsers.add_parser("check-update",
                                               help="Check for updates to " \
                                                    "installed packages")
    parser_checkupdate.add_argument("packages", nargs="*", metavar="PACKAGE",
                                    help="The package(s) for which to check " \
                                         "if an update is available. An " \
                                         "arbitrary number can be specified." \
                                         " If none is, updates for the whole" \
                                         " system are checked.")
    parser_checkupdate.set_defaults(func="check_update")

    # -- Subcommand: list -----------------------------------------------------
    parser_list = subparsers.add_parser("list",
                                        help="List packages and security " \
                                             "modules")
    parser_list.add_argument("filter", metavar="FILTER",
                             choices=["all", "installed", "available"],
                             help="List all, or filter on installed/available" \
                                  "only. Possible values are 'all', " \
                                  "'installed' and 'available'.")
    parser_list.add_argument("type", metavar="TYPE",
                             choices=["packages", "sms"],
                             help="Choose between listing packages and " \
                                  "security modules. Possible values are " \
                                  "'packages' and 'sms'.")
    parser_list.add_argument("patterns", nargs="*", metavar="PATTERN",
                             help="A glob-like pattern to match " \
                                  "names against, for example 'nb*'.")
    parser_list.set_defaults(func="list")

    # -- Subcommand: update ---------------------------------------------------
    parser_update = subparsers.add_parser("update",
                                          help="Update packages or the " \
                                               "whole system")
    parser_update.add_argument("packages", nargs="*", metavar="PACKAGE",
                               help="The package(s) to update. An arbitrary " \
                                    "number can be specified. If none is, " \
                                    "the whole system is updated.")
    parser_update.set_defaults(func="update")

    return parser

def get_envra(pkg):
    """Get the Epoch:Name-Version-Release.Arch representation of a package."""
    return "%s:%s-%s-%s.%s" % (pkg.epoch, pkg.name, pkg.version,
                               pkg.release, pkg.arch)

def get_nevra(pkg, ordering=False):
    """Get the Name-Epoch:Version-Release.Arch representation of a package."""
    name = pkg.name

    if ordering:
        # If we're trying to order packages, then we need a bit of work
        name = name.lower()

    return "%s-%s:%s-%s.%s" % (name, pkg.epoch, pkg.version,
                               pkg.release, pkg.arch)

def list_ordergetter(pkg_tuple):
    """Return a simple ordering for package lists.

    In a list of packages, we want the order to be defined as following:
        - first, installed packages
        - next, available packages
        - for each group, order by nevra

    :param pkg_tuple: A 2-tuple composed of the package status ("installed"
                      or "available") and the actual package.
    """
    reference = ["installed", "available"]

    return "%s %s" % (reference.index(pkg_tuple[0]),
                      get_nevra(pkg_tuple[1], ordering=True))

def transaction_ordergetter(pkg):
    """Return a simple ordering for package lists.

    In the transaction summary, we want the order to be loosely defined:
        - packages should be 'grouped' by their `ts_state` (all updates
          together, all new packages together, etc...)
        - updates should come before the new packages coming as dependencies

    This last requirement is what makes the alphabetical order unsuitable, so
    we need a reference list.
    """
    reference = ["i", "od", "ud", "u"]

    return "%s %s" % (reference.index(pkg.ts_state),
                      get_nevra(pkg, ordering=True))

def ensure_privileges(command):
    """Used as a decorator to ensure a command is run as root."""
    def wrapper(self):
        if os.getuid() != 0:
            raise NBYumException("This command must be run as root")

        command(self)

    return wrapper

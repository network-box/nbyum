Here's the doc for `nbyum`.

Each command is described below.

Check for available updates
===========================

Usage
-----

This is all quite simple::

    # ./nbyum check-update -h
    usage: nbyum check-update [-h] [PACKAGE [PACKAGE ...]]

    positional arguments:
      PACKAGE     The package(s) for which to check if an update is available. An
                  arbitrary number can be specified. If none is, updates for the
                  whole system are checked.

    optional arguments:
      -h, --help  show this help message and exit

Most of the time, the only interesting thing to do is to just run the command::

    # nbyum check-update

Alternatively, one can check updates for specific packages::

    # nbyum check-update systemd nbconfig

Output
------

The command prints one action of the transaction (that we'd execute if we were
actually updating the system) per line, each line being a JSON dictionary.

The only key of the dictionary is a string. It specifies the type of the
action. The value contains the details of the action, and it depends on the
type, as described below:

* key = `install`

** This means that the package would be installed if we'd actually run the
   transaction. (e.g: the `kernel` package is only ever installed, never
   updated)
** The value of the hash is the envra of the package to be installed.
** Example::

    {'install': '0:kernel-3.1.7-4.nb5.0.4.x86_64'}

* key = `obsolete`

** This means that the package would be obsoleted if we'd actually run the
   transaction.
** The value of the hash is a 2-tuple containing the envra of the package
   which would be obsolated and the envra of the package which would obsolete
   it.
** Example::

    {'obsolete': ('0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch')}

* key = `update`

** This means that the package would be updated if we'd actually run the
   transaction.
** The value of the hash is a 2-tuple containing the envra of the package
   which would be updated and the envra of the package which would update it.
** Example::

    {'update': ('0:systemd-37-3.nb5.0.9.x86_64', '0:systemd-37-5.nb5.0.9.x86_64')}

* key = `installdep`

** This means that the package would be installed if we'd actually run the
   transaction, because an update now requires it.
** The value of the hash is the envra of the package to be installed.
** Example::

    {'installdep': '0:plouf-2-1.nb5.0.noarch'}

Of course, nbyum might return several lines of output, since a transaction can
be formed of several updates, installations, obsoletions, or any combination
of those.

In such a case, lines of output will be grouped by type ("transaction states"
states in Yum parlance), and those types will be ordered as they have been
described above. As an example, one could have the following summary::

    {'install': '0:kernel-3.1.7-4.nb5.0.4.x86_64'}
    {'obsolete': ('0:upstart-1.2.2-1.nb5.0.noarch', '0:systemd-26-2.nb5.0.noarch')}
    {'update': ('0:bash-4.2.10-4.nb5.0.9.x86_64', '0:bash-4.2.20-1.nb5.0.9.x86_64')}
    {'update': ('0:glibc-2.14.90-14.nb5.0.9.x86_64', '0:glibc-2.14.90-24.nb5.0.9.x86_64')}
    {'installdep': '0:systemd-units-26-2.nb5.0.noarch'}

Update the system
=================

Usage
-----

This follows exactly the same syntax as the `check-update` command::

    # ./nbyum update -h
    usage: nbyum update [-h] [PACKAGE [PACKAGE ...]]

    positional arguments:
      PACKAGE     The package(s) to update. An arbitrary number can be specified.
                  If none is, the whole system is updated.

    optional arguments:
      -h, --help  show this help message and exit

Again, one can optionally specify the packages to update, otherwise the whole
system is updated.

Output
------

The output is exactly the same as for the `check-update` command. In fact, the
only difference between those two is that the transaction is processed in this
case, whereas the previous command merely display what would happen if it had
been.

.. note::
    The summary is printed **after** the transaction has been processed. In
    other words, once you get the output, the updates have already been
    applied.

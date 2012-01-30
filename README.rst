Here's the doc for nbyum.

The usage should be self-documented thanks to Python's awesome argparse module,
so just run ``nbyum`` with the ``-h`` or ``--help`` option for details::

    # nbyum -h

Each command has its own help as well, for example, if you want help on the
``check-update`` command, you can pass the ``-h`` or ``--help`` option to that
command rather than to the global tool::

    # nbyum check-update -h

The really interesting part though is the output of the commands, which are
described below.

Check for available updates
===========================

The command prints one action of the transaction (that we'd execute if we were
actually updating the system) per line, each line being a JSON dictionary.

The only key of the dictionary is a string. It specifies the type of the
action. The value contains the details of the action, and it depends on the
type, as described below:

* key = ``install``

** This means that the package would be installed if we'd actually run the
   transaction. (e.g: the ``kernel`` package is only ever installed, never
   updated)
** The value of the hash is the envra of the package to be installed.
** Example::

    {'install': '0:kernel-3.1.7-4.nb5.0.4.x86_64'}

* key = ``obsolete``

** This means that the package would be obsoleted if we'd actually run the
   transaction.
** The value of the hash is a 2-tuple containing the envra of the package
   which would be obsolated and the envra of the package which would obsolete
   it.
** Example::

    {'obsolete': ('0:bar-1-1.nb5.0.noarch', '0:baz-2-1.nb5.0.noarch')}

* key = ``update``

** This means that the package would be updated if we'd actually run the
   transaction.
** The value of the hash is a 2-tuple containing the envra of the package
   which would be updated and the envra of the package which would update it.
** Example::

    {'update': ('0:systemd-37-3.nb5.0.9.x86_64', '0:systemd-37-5.nb5.0.9.x86_64')}

* key = ``installdep``

** This means that the package would be installed if we'd actually run the
   transaction, because an update now requires it.
** The value of the hash is the envra of the package to be installed.
** Example::

    {'installdep': '0:plouf-2-1.nb5.0.noarch'}

Of course, nbyum might return **several lines of output**, since a transaction
can be formed of several updates, installations, obsoletions, or any
combination of those.

In such a case, lines of output will be **grouped by type**
("transaction states" states in Yum parlance), and those types will be
**ordered** as they have been described above. As an example, one could have
the following summary::

    {'install': '0:kernel-3.1.7-4.nb5.0.4.x86_64'}
    {'obsolete': ('0:upstart-1.2.2-1.nb5.0.noarch', '0:systemd-26-2.nb5.0.noarch')}
    {'update': ('0:bash-4.2.10-4.nb5.0.9.x86_64', '0:bash-4.2.20-1.nb5.0.9.x86_64')}
    {'update': ('0:glibc-2.14.90-14.nb5.0.9.x86_64', '0:glibc-2.14.90-24.nb5.0.9.x86_64')}
    {'installdep': '0:systemd-units-26-2.nb5.0.noarch'}

Update the system
=================

The output is **exactly the same** as for the ``check-update`` command. In
fact, the only difference between those two is that the transaction is
processed in this case, whereas the previous command merely display what would
happen if it had been.

.. note::
    The summary is printed **after** the transaction has been processed. In
    other words, once you get the output, the updates have already been
    applied.

List packages and security modules
==================================

The command prints a JSON dictionary per line. Its only key is a string
representing the status of the package. The only two possible keys are
``installed`` and ``available``.

Below is an example output of a packages listing::

    {'installed': '0:nbsm-base-5.0.0-0.1.nb5.0.18.noarch'}
    {'available': '0:nbsm-noc-provisioning-5.0.0-0.1.nb5.0.0.noarch'}

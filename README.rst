Here's the doc for `nbyum`.

Each command is described below.

Check for available updates
===========================

Usage
-----

Not a lot to see here::

    # nbyum check-update -h
    usage: nbyum check-update [-h]

    optional arguments:
      -h, --help  show this help message and exit

Really, the only possible thing to do is to just run the command::

    # nbyum check-update

Output
------

The command prints one action of the transaction (that we'd execute if we were
actually updating the system) per line, each line being a JSON dictionary.

The only key of the dictionary is a string. It specifies the type of the
action. The value contains the details of the action, and it depends on the
type, as described below:

.. toto:
   Document any other key I didn't think of yet but which would be implemented
   in the future.

* key = `install`

** This means that the package would be installed if we'd actually run the
   transaction. (e.g: the `kernel` package is only ever installed, never
   updated)
** The value of the hash is the envr of the package to be installed.
** Example::

    {'install': '0:kernel-3.1.7-4.nb5.0.4.x86_64'}

* key = `update`

** This means that the package would be updated if we'd actually run the
   transaction.
** The value of the hash is a 2-tuple containing the envr of the package
   which would be updated and the envr of the package which would update it.
** Example::

    {'update': ('0:systemd-37-3.nb5.0.9.x86_64', '0:systemd-37-5.nb5.0.9.x86_64')}

* key = `installdep`

.. todo:
   Document that stuff once it's been implemented/tested.

* key = `obsolete`

.. todo:
   Document that stuff once it's been implemented/tested.


The `nbyum` tool is a wrapper around yum. Why wrap? Simply because we need a
way to call the yum API from a Perl program.

As such, we could easily write a Perl binding to the yum API (which would be
quite painful and would require someone with knowledge both in Python and
Perl, which I don't have), or wrap it all into a simpler Python command-line
tool we can then call as needed.

However, such a tool needs a nicely formatted output, automatically parsable by
the caller program.

Thus nbyum, doing a subset of the yum functionality (only what we need), and
printing a parser-friendly JSON output on stdout.

## Usage

The usage should be self-documented thanks to Python's awesome argparse module,
so just run `nbyum` with the `-h` or `--help` option for details:

```
# nbyum -h
```

Each command has its own help as well, for example, if you want help on the
`check-update` command, you can pass the `-h` or `--help` option to that
command rather than to the global tool:

```
# nbyum check-update -h
```

## General considerations for the output

Each line of output is a JSON object with **at least** a `type` member,
representing the type of output.

The rest of the JSON object depends on this value, which is detailed in the
following sections.

## Good ol' logging messages (debug, errors,...)

For those, the `type` member will always be set to `log`. The "level" of
the log message is then the **name** of the second member, which will be one of
`debug`, `info`, `warning` or `error`.

The value of that second member is the actual logging message.

Unless running nbyum in debug mode, only messages with a level of `info`,
`warning` or `error` are shown.

**Note:** Not all `info` messages are even shown, only the actually important
ones.

A few examples of logging messages:

```
# nbyum update
[... snip ...]
{"type": "log", "info": "Packages are all up to date"}
```

```
# nbyum install sms base
[... snip ...]
{"type": "log", "warning": "Package nbsm-base-5.0.0-0.1.nb5.0.18.noarch already installed and latest version"}
```

```
# nbyum check-update nosuchpackage
[... snip ...]
{"type": "log", "error": "No Match for argument: nosuchpackage"}
```

## Progression messages

We print some progress messages while `nbyum` is performing, so that the user
doesn't fall asleep or hammers his keyboard impatiently.

These messages are indicated by the `type` member of the JSON object being set
to `progress`.

The rest of the object is composed of three members:

* `total` is the number of steps to perform. For example, if there are 3
  packages to install, then `total` would be `3`.
* `current` is where the process is currently, out of the `total`. For
  example, if we are installing the second out of 3 packages, then `current`
  would be `2`.
* `hint` is a message indicating what is the current step, so that the user
  is not left in the dark.

Here is an example of progression message:

```
# nbyum install sms nbsm-foo
[... snip ...]
{"type": "progress", "current": 2, "total": 3, "hint": "Installing foo-1.0-1.noarch"}
```

The above shows that we are installing the package `foo-1.0-1.noarch`, which
is the second out of three packages to install during this transaction.

**Note:** Some operations happen before we even know how many steps we will
have to perform during the transaction. For all of those, `current` would be
set to `0` and `total` to `1`. The idea is to provide some feedback to the
user as to what is happening, without showing a "fake" progress bar which
might "go back" once we know how many operations we will actually perform.

## Action messages

There are several possible actions in `nbyum`. They all share the same value
for the `type` member of the JSON object: `recap`.

Also, since they represent a summary of what has been done, then there is only
one message (and so only one JSON object) with all the data inside.

The other member depends on each action requested by the user:

* when `list`-ing packages and security modules, it will be either `installed`
  or `available`, depending on the package(s) being listed.
* when printing `info`-rmations about packages and security modules, it will
  be `pkginfos`
* when `install`-ing, `update`-ing or `remove`-ing packages and security
  modules, it will be `install`, `update` or `remove`, as appropriate.

Of course, there could be more than one of those. For example the user could
have requested to list both installed and available packages.

Each one of those members will have the list of corresponding packages as its
value. It will always be a list, even if it contains only one package.

### Modifying the system

Except for the `pkginfos` and `list` cases, each package is a JSON object with
up to 4 members:

* the `name` of the package.
* the `old` version, being removed during the transaction.
* the `new` version, being installed during the transaction.
* an eventual `reason` for the package to be removed (and **only for packages
  being removed**), for example if it is being obsoleted by another one.

Of course, packages being installed will only have a `new` version, whereas
packages being removed will only have an `old` version and packages being
updated will have both.

**Note:** By the time those messages appear, it is only as a summary of the
transaction which has just been executed. As such, they act as a confirmation
that everything went fine, and no additional confirmation message will be
printed.

To make things crystal clear, here are a couple of examples:

```
# nbyum install sms nbsm-foo
[... snip ...]
{"type": "recap", "install": [{"name": "nbsm-foo", "new": "5.0-1"},
                              {"name": "foo", "new": "1:5.0-1"}]}
```

As you can see, we do not make any differences between packages the user
requested to install and the ones that come in as dependencies.

Here is what happens on updates:

```
# nbyum update
[... snip ...]
{"type": "recap", "install": [{"name": "baz", "new": "5.0-1"},
                              {"name": "kernel", "new": "3.3.3-1"}],
                  "update": [{"name": "foo", "old": "5.0-1", "new": "1:5.0-1"}],
                  "remove": [{"name": "kernel", "old": "3.2.0-1", "reason": ""},
                             {"name": "bar", "old": "5.0-1", "reason": "Replaced by baz-5.0-1"}]}
```

A couple of things are interesting here. First, running an update can of course
update packages, but it can also install some and remove others.

Secondly, the `kernel` is an "**installonly**" package in Yum-speak, and as
such it is only ever installed, never updated. But since we only keep three
versions, we also have to remove the older one. Note how the `reason` member
is always present, even when in this case it is empty.

Finally, we are installing the package `baz-5.0-1` which is obsoleting the
installed `bar` package. This shows up as a removal.

### Listing packages

We will often want to list `installed` and `available` packages.

This works pretty much the same as above, except that each item of the `pkgs`
member will also contain the `summary` of the package, to make the listing a
touch more user-friendly:

```
# nbyum list all packages
[... snip ...]
{"type": "recap", "installed": [{"name": "foo", "version": "5.0-1", "summary": "Foo foo foo"}]
{"type": "recap", "available": [{"name": "foo", "version": "5.0-2", "summary": "Foo foo foo"},
                                {"name": "bar", "version": "5.0-1", "summary": "Bar bar bar"}]
```

Notice how `foo` is both `installed` and `available`? That's because there is
an update in the repositories, waiting to be installed.

**Note:** We don't show updates of `installed` **security modules** as
`available`, because in this case, what the user wants to know is which
modules he has activated, which is a very different thing from listing
packages.

### Obtaining informations

The case for `pkginfos` is also very similar to all the above, except that we
show much more details.

Indeed, each item of the `pkginfos` member will contain lots of information
about the package, like its `arch`, `license` or even full `description`.
The following examples shows all the printed attributes:

```
# nbyum info \*foo\*
[... snip ...]
{"type": "recap", "pkginfos": [{"name": "nbsm-foo", "version": "5.0-1",
                                "arch": "noarch", "license": "MIT",
                                "summary": "Un module foo",
                                "basepackage": "nbsm-foo",
                                "description": "Blabla about nbsm-foo"},
                               {"name": "foo", "version": "5.0-1",
                                "arch": "noarch", "license": "MIT",
                                "summary": "Foo foo foo",
                                "basepackage": "foo",
                                "description": "Blabla about foo"}]}
```

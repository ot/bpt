==========================
 Boxed Package Tool (BPT)
==========================

* `Git repository <https://github.com/ot/bpt>`_
* `Issue tracker <https://github.com/ot/bpt/issues>`_

What is BPT
===========

BPT is a Python library (``bpt``) and a command line application
(``box``) to create and manage isolated enviroments, or *boxes*. 

- Boxes are *relocatable*, which means that they can be moved to a
  different directory or even distributed to other machines (provided
  that the architecture is compatible).

- Packages inside the box can be easily disabled, enabled and removed,
  so that different versions of the same software can be installed
  simultaneously, allowing to switch between them. 

- Boxes can be *nested*, in the sense that it is possible to activate
  a box environment while inside another box environment, so that all
  the packages installed in both boxes are available, and so on.

BPT is similar in some ways to `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_, but it is not restricted
to Python packages, allowing to install virtually any Unix
software. It also takes some ideas from `jhbuild
<http://live.gnome.org/Jhbuild>`_, but without the dependency
resolution and automatic downloading machinery, and the ``bpt-rules``
format is inspired by `Gentoo <http://www.gentoo.org/>`_'s ebuilds.

A fork of PIP_ is included to make installation of python packages
easier, and as an example of use of the BPT API.

How to use it
=============

A *box* is a directory whose structure resembles ``/usr/`` (as defined
in the `Filesystem Hierarchy Standard
<http://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard>`_), that
can contain one or more software *packages*. Each package is contained
in a subdirectory of the ``pkgs`` directory in the box. A box contains
a script, ``env``, which sets up the environment, putting all the
libraries, executables, etc. in the path.

The command to create a box is::

    $ bpt/box create my_first_box

(We assume that the source distribution of BPT is in the directory ``bpt``) 

This creates the basic structure::

    $ find my_first_box
    my_first_box
    my_first_box/bin
    my_first_box/bpt_meta
    my_first_box/bpt_meta/box_info
    my_first_box/env
    my_first_box/include
    my_first_box/lib
    my_first_box/man
    my_first_box/pkgs
    my_first_box/share

To execute a command within the box environment, use the ``env`` script::

   $ my_first_box/env 'echo $PATH'
   /tmp/box_87a482cc-34fc-11de-865a-001ec21bf2c7/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/X11/bin:/usr/local/bin

Even if it may not seem obvious at first, the first path points to the
box's ``bin``. We'll talk about this later in the `How it works`_
section. Prefixing ``env`` to every command can be boring, so
``box`` has a ``shell`` command that spawns a shell with the
environment set up. The ``env`` script exports also an environment
variable, ``BPT_BOX_PATH``, that ``box`` uses to know the location of
the current box::

    $ bpt/box -b my_first_box/ shell
    (my_first_box) ot@brian ~ $ echo $BPT_BOX_PATH 
    /Users/ot/my_first_box

To install packages into a box, ``box`` offers two different commands:
``build`` and ``autobuild``. Alternatively, external programs can use
the BPT API to install packages. An example is given by ``pip-box``,
included in the distribution.


``build``
---------

The ``build`` command works with *sourcedirs*: a *sourcedir* is a
directory that contains a ``bpt-rules`` file, which contains the
instructions to build the software. A good practice is to install BPT
itself into the box (the source distribution of BPT is a
*sourcedir*)::

    (my_first_box) ot@brian ~ $ bpt/box build bpt
    INFO:BPT:Using current box "my_first_box"
    INFO:BPT:Building application bpt, in sourcedir work/experimental/bpt
    ...
    (my_first_box) ot@brian ~ $ which box
    /tmp/box_87a482cc-34fc-11de-865a-001ec21bf2c7/bin/box

Now we can run the shell using the box's ``box``::

    $ my_first_box/env box shell
    INFO:BPT:Using current box "my_first_box"

    (my_first_box) ot@brian ~ $ 

Another example of *sourcedir* is given by ``python30`` in the
``examples`` directory, which installs python 3.0.1::

    (my_first_box) ot@brian ~ $ box build examples/python30/
    ...

    (my_first_box) ot@brian ~ $ python3.0 --version
    Python 3.0.1

``autobuild``
-------------

The ``autobuild`` command, when invoked with a vanilla source tarball
or a source directory, tries to build and install it by guessing the
build commands. It works when the software builds using the usual
``configure``/``make`` or ``setup.py``::

    (my_first_box) ot@brian ~ $ box autobuild Downloads/ipython-0.9.1.tar.gz 
    INFO:BPT:Using current box "my_first_box"
    INFO:BPT:Guessed application name "ipython", version "0.9.1". Unpacking the file...
    INFO:BPT:Building and installing as package ipython-0.9.1
    ...

    (my_first_box) ot@brian ~ $ which ipython
    /tmp/box_87a482cc-34fc-11de-865a-001ec21bf2c7/bin/ipython

    (my_first_box) ot@brian ~ $ box autobuild Downloads/sqlite-amalgamation-3.6.3.tar.gz 
    INFO:BPT:Using current box "my_first_box"
    INFO:BPT:Guessed application name "sqlite-amalgamation", version "3.6.3". Unpacking the file...
    INFO:BPT:Building and installing as package sqlite-amalgamation-3.6.3
    ...

    (my_first_box) ot@brian ~ $ which sqlite3
    /tmp/box_87a482cc-34fc-11de-865a-001ec21bf2c7/bin/sqlite3

To guess name and version of the package, the tarball/directory name
is used, so it has to be of the form ``<name>-<version><extension>``.

``pip-box``
-----------

``pip-box`` is a fork of PIP_ 0.3.1 where only
``InstallRequirement.install{,_editable}`` have been replaced to
install every package inside the current box::

     $ new_box/env pip-box install -qI sphinx
     INFO:BPT:Enabling package Jinja2-2.1.1
     INFO:BPT:Linking package Jinja2-2.1.1
     INFO:BPT:Created env script
     INFO:BPT:Enabling package Pygments-1.0
     INFO:BPT:Linking package Pygments-1.0
     INFO:BPT:Created env script
     INFO:BPT:Enabling package sphinx-0.6.1
     INFO:BPT:Linking package sphinx-0.6.1
     INFO:BPT:Created env script
     INFO:BPT:Enabling package docutils-0.5
     INFO:BPT:Linking package docutils-0.5
     INFO:BPT:Created env script

     $ new_box/env box status
     INFO:BPT:Using current box "new_box"

     PACKAGE                       | NAME                | VERSION   | STATUS    |

     Jinja2-2.1.1                  | Jinja2              | 2.1.1     | enabled   |
     sphinx-0.6.1                  | sphinx              | 0.6.1     | enabled   |
     docutils-0.5                  | docutils            | 0.5       | enabled   |
     Pygments-1.0                  | Pygments            | 1.0       | enabled   |

Since only the install functions where changed, it is completely
command-line-compatible with PIP_. (Interaction with virtualenv was
not tested and probably it won't work)

``pip-box`` is just a working proof-of-concept of an external
application that uses the BPT API. If future versions of PIP_ allow to
override the install commands, probably the fork will be removed and
the PIP_ API will be used instead.

Notice that to use ``pip-box``, ``setuptools`` is needed. It can be
installed in the underlying system, or inside the box using
``autobuild``::

     $ wget -q http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz
     $ box -b my_box/ autobuild setuptools-0.6c9.tar.gz
     INFO:BPT:Unpacking the file...
     INFO:BPT:Guessed application name "setuptools", version "0.6c9"
     INFO:BPT:Building and installing as package setuptools-0.6c9
     ...
     
Other commands
--------------

The ``status`` command shows the installed packages::

    (my_first_box) ot@brian ~ $ box status
    INFO:BPT:Using current box "my_first_box"
    
    PACKAGE                       | NAME                | VERSION   | STATUS    |
    
    bpt-0.1                       | bpt                 | 0.1       | enabled   |
    ipython-0.8.4                 | ipython             | 0.8.4     | disabled  |
    ipython-0.9.1                 | ipython             | 0.9.1     | enabled   |
    python30-3.0.1                | python30            | 3.0.1     | enabled   |
    sqlite-amalgamation-3.6.3     | sqlite-amalgamation | 3.6.3     | enabled   |

Packages can be enabled/disabled with the ``enable``/``disable`` commands::

    (my_first_box) ot@brian ~ $ box disable python30-3.0.1

    (my_first_box) ot@brian ~ $ python3.0
    bash: python3.0: command not found

    (my_first_box) ot@brian ~ $ box enable python30-3.0.1

    (my_first_box) ot@brian ~ $ python3.0 --version
    Python 3.0.1

Executing ``disable`` with the ``--remove`` switch deletes permanently
the package files.

Use cases
=========

- The main purpose of BPT is to create self-contained environments to
  be deployed in case it is not possible to install packages
  system-wide (for example because of non-friendly sysadmins or
  providers) or when different applications on the same machine need
  different versions of their dependencies. The box can be built on a
  development machine and then sent to deployment machines without
  having to take care of paths, thanks to relocatability of
  boxes. Several boxes with different versions of packages can be run
  on the same machine, as long as they have different ``box_id``
  (i.e. they have been created independently). 

- BPT is also a convenient alternative to cluttering ``/usr/local``
  when packages that are not packaged by the system distribution (or a
  different version is packaged) are needed. For example it is
  possible to add to ``.bashrc`` a line like::

    source ~/my_box/env  

  so that we are always inside a common box where we can install new
  software with ``autobuild`` (or by writing the ``bpt-rules`` when
  needed). Notice that since boxes can be nested, this creates no
  problems with other boxes.

How it works
============

BPT is designed to work around two problems common to Unix
applications and libraries:

- Often the prefix (like ``/usr/local``) is hardcoded in the binary
  during compilation. This implies that once a software its compiled,
  its installation path cannot change. In other words, it is not
  *relocatable*.

- Everything is installed in the same directories (``bin``, ``lib``,
  etc...). Hence is difficult or impossible to remove an installed
  software without using a packaging system, and is virtually
  impossible to keep different versions of the same software installed
  on the system. 

Both problems are solved by BPT by using symlinks. When an application
is compiled, the prefix passed to the compilation script has the form::
  
  /tmp/box_<uuid>/pkgs/<pkg_name>

where ``<uuid>`` is a unique identifier of the box, and ``<pkg_name>``
identifies the (name, version) pair of the software. The ``env``
script ensures that ``/tmp/box_<uuid>`` is a symlink to the box.
Then, when a package is installed/enabled, all the contents of the
package are symlinked to the box root (where the ``PATH`` variables
point to).

- If we relocate the box, the ``env`` script will fix the symlink.

- Disabling a package is just matter of removing its symlinks, while
  if we remove its ``pkgs`` subdirectory, all the package files are
  removed.

If packages are manually removed by deleting their directories,
symlinks may be broken. The ``sync`` command can be used to restore
the consistency of the box by recreating all the symlinks and the
``env`` script. 

Writing the ``bpt-rules`` file
==============================

*TODO* For now, see the ``examples/python30`` example, it is quite
self-explanatory. Keep in mind that, for most software, ``autobuild``
just works.

Also, the ``bpt-rules`` format may soon change (or, more probably, a
new syntax will be added alongside)

TODO
====

Some features planned for next releases. Ideas and patches are very
welcome.

* Dependencies. Would be very convenient to have automatic dependency
  resolution. I would like to achieve the following goals:

  * It should be very easy to install a package with a set of packages
    satisfying its dependencies.

  * Boxes are mainly meant for deploy, so it is needed a system to
    freeze a set of versions (instead of downloading the newest
    satisfying version, as easy_install and most packaging systems do,
    because it can break things)
    
  * It should be possible to specify mirrors for the packages so that
    a build bot has not to be connected to the Internet.

  * The system should not rely on a centralized repository. Maybe,
    specify via configuration a set of repositories, a-la
    apt/sources.list.

  * A PIP-like "editable" package mode should be available, for
    development (and so, also integration with VCSs)

  PIP_ gets most of these things right, so I could just copy or
  integrate its model. 

* Investigate Windows support (native, not cygwin, which should
  already work). This would need at least the following:

  * Generate a env.bat instead of env script using Windows batch files

  * Do not use ``bash`` as a syntax for bpt-rules (talk about this
    later)
  
  * See if the directories/symlinks/environment variables (PATHs) can
    be adapted to Windows. This requires a Windows guru, I do not know
    almost anything about it.

* Get rid of ``bash`` as syntax for bpt-rules. Maybe a Python DSEL
  would be ideal: something like scons or waf, so that the
  declarations can be abstract enough to be cross-platform.
  
* Buildout support? 

* The ``/tmp/box_...`` trick has some drawbacks: it is not possible to
  install two boxes with the same uuid in the same machine, because
  the symlink can point to only one of the two. Would be good to find
  a different solution (as portable as possible).

* It has been suggested that ``box`` is too generic for the script
  name, and there could be collisions. If I receive enough feedback
  about this issue, I could rename the script to ``pbox`` or something
  similar.

Supported operating systems
===========================

BPT should work with any POSIX operating system. It has been tested on
Mac OS X Leopard and several Ubuntu releases.

License
=======

BPT is distributed under the terms of the GPL License. The full
license is in the file COPYING, distributed as part of this software.

Credits
=======

* Giuseppe Ottaviano <giuott at gmail dot com>

.. _PIP: http://pypi.python.org/pypi/pip


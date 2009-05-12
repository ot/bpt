# -*- coding: utf-8 -*-
'''\
autobuild command
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

from optparse import make_option

from bpt import UserError
from bpt.ui.command import Command
from bpt.box import require_box
from bpt.autobuild import autobuild as autobuild_, UnsupportedPath

class autobuild(Command):
    '''Try to build a set of tarballs into the box, guessing the build commands'''

    usage_args = '<tarball> ...'

    def __init__(self):
        options = [make_option('-k', '--keep-intermediate', action='store_true',
                               dest='keep',
                               help='Do not delete intermediate files.'),
                   make_option('-c', '--configure_options', action='store',
                               dest='configure_options',
                               default='',
                               help='Options to pass to the configure/setup.py command line.')
                   ]
        Command.__init__(self, options)
        

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)
        require_box(config)

        try:
            for tarball in cmd_args:
                autobuild_(config.box, tarball, cmd_options.configure_options, cmd_options.keep)
        except UnsupportedPath, exc:
            raise UserError(str(exc))

# -*- coding: utf-8 -*-
'''\
Build command
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

from optparse import make_option

from bpt.ui.command import Command
from bpt.box import require_box
from bpt.build import SourceDir

class build(Command):
    '''Build a set of sourcedirs into the box'''

    usage_args = '<source package> ...'

    def __init__(self):
        options = [make_option('-c', '--clean-before', action='store_true',
                               dest='clean_before',
                               help='Clean sourcedir before building it.'),
                   make_option('-s', '--suffix', action='store',
                               dest='suffix',
                               default='',
                               help='Append a suffix to the package name.'),
                   make_option('-t', '--test', action='store_true',
                               dest='test',
                               help='Run the tests after building the package.')
                   ]
        Command.__init__(self, options)
        

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)
        require_box(config)

        for sourcedir in cmd_args:
            sd = SourceDir(sourcedir)
            if cmd_options.clean_before:
                sd.clean()
            sd.build(config.box, cmd_options.suffix)
            if cmd_options.test:
                sd.unittest()

class clean(Command):
    '''Clean a set of sourcedirs'''

    usage_args = '<source package> ...'

    def __init__(self):
        options = [make_option('-d', '--deep', action='store_true',
                               dest='deep',
                               help='Deep clean: erase also downloaded files, etc...')
                   ]
        Command.__init__(self, options)

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)

        for sourcedir in cmd_args:
            sd = SourceDir(sourcedir)
            sd.clean(cmd_options.deep)

class unittest(Command):
    '''Run unit tests inside a set of sourcedirs. 
    Should be invoked only after a build command.'''

    usage_args = '<source package> ...'

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)

        for sourcedir in cmd_args:
            sd = SourceDir(sourcedir)
            sd.unittest()

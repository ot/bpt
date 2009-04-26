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

import os
from optparse import make_option

from bpt.ui.command import Command
from bpt.box import Box, require_box
from bpt.build import SourceDir

class build(Command):
    doc = 'Build a package inside the sandbox'

    name = 'build'
    usage_args = '<source package> ...'

    def __init__(self):
	options = [make_option('-c', '--clean-before', action='store_true',
			       dest='clean_before',
			       help='Clean sourcedir before building it.'),
                   make_option('-s', '--suffix', action='store',
			       dest='suffix',
                               default='',
			       help='Append a suffix to the package name.')
		   ]
	Command.__init__(self, options)
	

    def _run(self, config, cmd_options, cmd_args):
	if not cmd_args:
	    self.parser.print_help()
	    return 1

        require_box(config)

	for sourcedir in cmd_args:
	    if cmd_options.clean_before:
		# XXX(ot): clean
                pass
            sd = SourceDir(sourcedir)
            sd.build(config.box, cmd_options.suffix)

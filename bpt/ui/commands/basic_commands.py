# -*- coding: utf-8 -*-
'''\
Basic BPT commands
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

from bpt.ui.commands import Command


class create(Command):
    
    doc = 'Create a new package box'
    name = 'create'
    usage_args = '<box path>'

    def _run(self, config, options, args):
	if len(args) != 1:
	    self.parser.print_help()
	    return 1

	print 'Not implemented'

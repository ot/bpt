# -*- coding: utf-8 -*-
'''\
Command line frontend for BPT
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import sys
import logging
from optparse import OptionParser

import bpt
from bpt import log
from bpt import ui

def help_commands(option, opt_str, value, parser):
    commands = [(x.name, x.doc) for x in ui.commands.get_commands()]
    commands.sort()
    for name, description in commands:
        print '  %-15s %s' % (name, description)
    print
    print 'For more informations about <command> run "%s <command> --help"' % parser.get_prog_name()
    parser.exit()
    

def setup_optparse():
    parser = OptionParser(
        usage='%prog command [ options ... ]',
        description='Tool for creating/managing package boxes',
        version='%%prog %s' % bpt.__version__)
    parser.disable_interspersed_args()

    parser.add_option('--help-commands', action='callback',
                      callback=help_commands,
                      help='informations about available commands')
    parser.add_option('-b', '--box', action='store',
                      type='string', dest='box',
		      help='box path. If not specified, use the current one.')

    return parser
    
def main(argv):
    # set up default logging 
    # TODO(giuott): Add a verbosity option
    logging.basicConfig()
    log.setLevel(logging.INFO)
    
    parser = setup_optparse()
    options, args = parser.parse_args(argv[1:])
    
    command = args[0]
    cmd_args = args[1:]
    config = None # XXX(ot) put a real config

    try:
        return ui.commands.dispatch(command, config, cmd_args)
    except ui.commands.CommandNotFound:
        log.error("Command %s not found", command)
	parser.print_help()
	return 255
    
    

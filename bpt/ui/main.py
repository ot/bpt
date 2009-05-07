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

import logging
from optparse import OptionParser

import bpt
from bpt import log
from bpt import ui
from bpt.ui.config import Config
from bpt.box import Box, get_current_box

def help_commands(option, opt_str, value, parser):
    commands = [(x.__name__, x.__doc__) for x in ui.command.get_commands()]
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
                      type='string', dest='box_path',
                      help='box path. If not specified, use the current one.')

    return parser
    
def main(argv, do_log=True):
    # set up default logging 
    # TODO(giuott): Add a verbosity option
    if do_log:
        logging.basicConfig()
        log.setLevel(logging.INFO)
    
    parser = setup_optparse()
    options, args = parser.parse_args(argv[1:])
    
    if not args:
        parser.print_help()
        return 255

    command = args[0]
    cmd_args = args[1:]
    config = Config()

    try:
        if options.box_path is not None:
            config.box = Box(options.box_path)
        else:
            config.box = get_current_box()
            if config.box is not None:
                log.info('Using current box "%s"', config.box.name)

        return ui.command.dispatch(command, config, cmd_args)
    except ui.command.CommandNotFound:
        log.error("Command %s not found", command)
        parser.print_help()
        return 255
    except bpt.UserError, exc:
        log.error('Aborting: %s', str(exc))
        return 1
    

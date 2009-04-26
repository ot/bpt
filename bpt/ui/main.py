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

def help_commands():
    pass

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
    logging.basicConfig()
    log.setLevel(logging.INFO)
    
    parser = setup_optparse()
    options, args = parser.parse_args(argv[1:])
    
    

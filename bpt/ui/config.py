# -*- coding: utf-8 -*-
'''\
Configuration classes for BPT
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

from optparse import OptionParser

class ParserExit(Exception):
    '''Exception used by the option parser to signal program exit'''

class BPTOptionParser(OptionParser):
    def exit(self):
        raise ParserExit

class Config(object):
    '''Just a simple container of configuration values'''

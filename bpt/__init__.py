# -*- coding: utf-8 -*-
'''\
Common data for the SPT project
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

__version__ = '0.2a'
__author__ = 'Giuseppe Ottaviano <giuott@gmail.com>'

import logging
log = logging.getLogger('BPT')

class UserError(Exception):
    '''Error to be reported to the user'''

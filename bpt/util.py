# -*- coding: utf-8 -*-
'''\
Utility functions
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
from pprint import pprint, isreadable

# Simple functions to store small dicts in human readable format
# WARNING: the stored data is evaluated, so it must be trusted
# XXX(ot): use another representation format?
# XXX(ot): write tests

def store_info(filename, data):
     if not isreadable(data):
          raise Exception('Recursive or nonserializable data')

     f = open(filename, 'w')
     try:
          pprint(data, f)
     finally:
          f.close()

def load_info(filename):
     f = open(filename)
     try:
          return eval(f.read())
     finally:
          f.close()

# Other util functions

def get_arch():
     u = os.uname()
     return (u[0], u[4])


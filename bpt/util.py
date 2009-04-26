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
from tempfile import mktemp # for doctests

# Simple functions to store small dicts in human readable format
# WARNING: the stored data is evaluated, so it must be trusted
# XXX(ot): use another representation format?

def store_info(filename, data):
    r'''Pretty print roundtrippable data into filename
    
    >>> f = mktemp()
    >>> store_info(f, dict(a='hello', b=[1, 2, 3]))
    >>> open(f).read()
    "{'a': 'hello', 'b': [1, 2, 3]}\n"
    '''
    if not isreadable(data):
        raise Exception('Recursive or nonserializable data')
    
    f = open(filename, 'w')
    try:
        pprint(data, f)
    finally:
        f.close()

def load_info(filename):
    r'''Read data writen with store_info

    >>> f = mktemp()
    >>> data = dict(a='hello', b=[1, 2, 3])
    >>> store_info(f, data)
    >>> read_data = load_info(f)
    >>> read_data == data
    True
    '''
    f = open(filename)
    try:
        return eval(f.read())
    finally:
        f.close()
        
# Other util functions

def get_arch():
    u = os.uname()
    return (u[0], u[4])

def path_diff(start, path):
    '''\
    Returns the relative path of a path from directory start,
    and backwards
    XXX: Not sure this is robust or portable
    >>> path_diff('/a/', '/a/b/c')
    ('b/c', '../..')
    
    >>> path_diff('a', '/a/b/c')
    ('b/c', '../..')
    '''
    start_list = filter(None, start.split(os.path.sep))
    path_list = filter(None, path.split(os.path.sep))
    i = len(start_list)
    p = len(path_list)
    
    if start_list != path_list[:i]:
        raise Exception('path is not a subpath of start')
    
    if p == i:
        return '', ''
    else:
        return os.path.join(*(path_list[i:])), os.path.join(*((os.path.pardir,)*(p-i)))


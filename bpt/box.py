# -*- coding: utf-8 -*-
'''\
Box class implementation
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
import sys
from uuid import uuid1

from bpt import log, UserError
from bpt.util import store_info, load_info, get_arch

STANDARD_DIRS = ['pkgs', 'bpt_meta', 'bin', 'lib', 'man', 'share', 'include']

class Box(object):
    '''\
    Represents a package box in the filesystem. 
    
    The constructor expects an existing box. A new one can be created with the class method create()
    '''

    def __init__(self, box_path):
        # XXX(ot): check that the path is indeed a box
        self._path = box_path

        try:
            box_info = load_info(os.path.join(self.path, 'bpt_meta', 'box_info'))
        except OSError:
            raise UserError('Invalid box: impossible to read box_info')

        try:
            self._id = box_info['id']
            self._arch = box_info['arch']
        except KeyError, e:
            raise UserError('Invalid box_info: missing "%s"', e.message)

    def __repr__(self):
        return "Box('%s')" % self.path
    
    @property
    def path(self):
        return self._path
    
    @property
    def box_id(self):
        return self._id
    
    @classmethod
    def create(klass, dest_path):
        
        # Safety checks
        if os.path.exists(dest_path):
            raise UserError('Destination already exists')

        try:
            os.makedirs(dest_path)
            for d in STANDARD_DIRS:
                os.makedirs(os.path.join(dest_path, d))
        except OSError, e:
            raise UserError('Impossible to create destination directories: "%s"', e.message)

        box_info = dict()
        box_info['id'] = str(uuid1())
        box_info['arch'] = get_arch()
        store_info(os.path.join(dest_path, 'bpt_meta', 'box_info'), box_info)

        box = klass(dest_path)
        box.sync()
    
    def sync(self):
        # XXX(ot): implement
        pass

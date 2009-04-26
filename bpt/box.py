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
from uuid import uuid1

from bpt import log, UserError
from bpt.util import store_info, load_info, get_arch

STANDARD_DIRS = ['pkgs', 'bpt_meta', 'bin', 'lib', 'man', 'share', 'include']

STANDARD_PATH_VARS = [('PATH', 'bin'), 
                      ('LIBRARY_PATH', 'lib'), 
                      ('LD_LIBRARY_PATH', 'lib'),
                      ('DYLD_LIBRARY_PATH', 'lib'), 
                      ('CPATH', 'include'), 
                      ('MANPATH', 'man'), 
                      ('PKG_CONFIG_PATH', os.path.join('lib', 'pkgconfig'))]

ENV_SCRIPT_TMPL = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'env_script.tmpl'))

class Box(object):
    '''\
    Represents a package box in the filesystem. 

    The constructor expects an existing box. A new one can be created
    with the class method create()
    '''

    def __init__(self, box_path):
        # XXX(ot): check that the path is indeed a box
        self._path = box_path

        try:
            box_info = load_info(os.path.join(self.path, 
                                              'bpt_meta', 
                                              'box_info'))
        except OSError:
            raise UserError('Invalid box: impossible to read box_info')

        try:
            self._id = box_info['id']
            self._arch = box_info['arch']
        except KeyError, exc:
            raise UserError('Invalid box_info: missing "%s"', exc.message)

    def __repr__(self):
        return "Box('%s')" % self.path
    
    @property
    def box_id(self):
        '''Unique id of the box, used to build the virtual path'''
        return self._id
    
    @property
    def path(self):
        '''Actual path of the box'''
        return self._path

    @property
    def virtual_path(self):
        '''Virtual (or relocatable) path of the box. It is a symlink
        that points to the box, but does not depend on the actual path'''
        return os.path.join('/tmp', 'box_' + self.box_id)

    @classmethod
    def create(cls, dest_path):
        '''Creates a directory dest_path and initialize a package box
        in it.  Returns the initialized box'''
        # Safety checks
        if os.path.exists(dest_path):
            raise UserError('Destination already exists')

        try:
            os.makedirs(dest_path)
            for directory in STANDARD_DIRS:
                os.makedirs(os.path.join(dest_path, directory))
        except OSError, exc:
            raise UserError('Impossible to create destination directories: "%s"', 
                            exc.message)

        box_info = dict()
        box_info['id'] = str(uuid1())
        box_info['arch'] = get_arch()
        store_info(os.path.join(dest_path, 'bpt_meta', 'box_info'), box_info)

        box = cls(dest_path)
        box.sync()
        log.info('Created box with id %s in directory %s', box.box_id, box.path)
        return box
    
    def sync(self):
        # XXX(ot): implement linking of packages
        self._create_env_script()

    def _create_env_script(self):
        virtual_path = self.virtual_path
        path_updates = '\n'.join('export %s="$VIRTUAL_PATH/%s${%s:+:$%s}"' % (v, d, v, v) 
                                 for v, d in STANDARD_PATH_VARS)
        pkg_env_scripts = '' # XXX 
        
        env_script = open(ENV_SCRIPT_TMPL).read() % locals() # XXX(ot) close file?
        
        env_script_path = os.path.join(self.path, 'env')
        env_script_file = open(env_script_path, 'w')

        try: 
            env_script_file.write(env_script)
        finally:
            env_script_file.close()
        os.chmod(env_script_path, 0755)

        log.info('Created env script')

def require_box(config):
    '''Raise an exception if config.box is None'''
    if config.box is None:
        raise UserError('No box given')

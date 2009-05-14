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
import re
import shutil
from uuid import uuid1
from tempfile import mktemp # for doctests, pylint: disable-msg=W0611

import bpt
from bpt import log, UserError
from bpt.util import store_info, load_info
from bpt.linkdir import linkdir, unlinkdir
from bpt.package import Package

# Directories created inside the box
STANDARD_DIRS = ['pkgs', 'bpt_meta', 'bin', 'lib', 'man', 'share', 'include']

# Directories whose contents are linked from every package to the box
DYN_DIRS = ['bin', 'lib', 'man', 'share', 'include']

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
        self._path = os.path.abspath(box_path)

        try:
            box_info = load_info(os.path.join(self.path, 
                                              'bpt_meta', 
                                              'box_info'))
        except (OSError, IOError):
            raise UserError('Invalid box: impossible to read box_info')

        try:
            self._id = box_info['id']
            self._platform = box_info['platform']
        except KeyError, exc:
            raise UserError('Invalid box_info: missing "%s"', str(exc))
        
        # Ensure that the virtual path symlink is existing and points
        # to the correct location
        try:
            os.symlink(self.path, self.virtual_path)
        except OSError, exc:
            if exc.errno == 17 and \
                    not os.path.samefile(self.path, self.virtual_path):
                raise UserError('Virtual path symlink %s exists but ' 
                                'does not point to this box. Please remove '
                                'it manually', self.virtual_path)

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

    @property
    def name(self):
        '''The name of the box, defined as the basename of the directory'''
        return os.path.basename(os.path.abspath(self.path))

    @property
    def env_script(self):
        '''Path of the env script'''
        return os.path.join(self.path, 'env')

    def __eq__(self, other):
        ''' Compare equality by box_id

        >>> box1 = Box.create(mktemp())
        >>> box2 = Box.create(mktemp())
        >>> box1 == box1
        True
        >>> box1 == box2
        False
        '''
        return isinstance(other, Box) and self.box_id == other.box_id

    @classmethod
    def create(cls, dest_path):
        '''Creates a directory dest_path and initialize a package box
        in it.  Returns the initialized box.

        >>> box_path = mktemp()
        >>> box = Box.create(box_path)
        >>> box.path == box_path
        True
        '''
        # Safety checks
        if os.path.exists(dest_path):
            raise UserError('Destination already exists')

        try:
            os.makedirs(dest_path)
            for directory in STANDARD_DIRS:
                os.makedirs(os.path.join(dest_path, directory))
        except OSError, exc:
            raise UserError('Impossible to create destination directories: "%s"', 
                            str(exc))

        box_info = dict()
        box_info['id'] = str(uuid1())
        box_info['platform'] = _get_platform()
        box_info['bpt_version'] = bpt.__version__
        store_info(os.path.join(dest_path, 'bpt_meta', 'box_info'), box_info)

        box = cls(dest_path)
        box.sync()
        log.info('Created box with id %s in directory %s', box.box_id, box.path)
        return box
    
    def sync(self):
        '''Recreate all the symlinks and the env script, restoring the
        consistency of the box.'''

        # Clean all symlinks
        for d in DYN_DIRS:
            d_path = os.path.join(self.path, d)
            shutil.rmtree(d_path)
            os.makedirs(d_path)

        # Relink all packages    
        for package in self.packages(only_enabled=True):
            self._link_package(package)

        self._create_env_script()
        log.info('Synchronized box')

    def get_package(self, pkgname):
        pkgs_dir = os.path.join(self.virtual_path, 'pkgs')
        return Package(os.path.join(pkgs_dir, pkgname))

    def packages(self, only_enabled=False, matching=None):
        '''Iterates on the installed packages. If only_enabled is
        True, only enabled packages are returned. matching can be a
        list of regexps, if it is given a package is returned only if
        it matches at least one regexp
        '''
        if matching is not None:
            regexps = [re.compile(pattern + '$', re.IGNORECASE) for pattern in matching]
        for pkgname in os.listdir(os.path.join(self.virtual_path, 'pkgs')):
            try:
                pkg = self.get_package(pkgname)
            except UserError:
                log.warning('Invalid entry in pkgs: %s', pkgname)
                continue
            if not only_enabled or pkg.enabled:
                if matching is None:
                    yield pkg
                else:
                    for regexp in regexps:
                        if regexp.match(pkg.name):
                            yield pkg
                            break
                            
    def create_package(self, pkg_name, **pkg_info):
        pkg_prefix = os.path.join(self.virtual_path, 'pkgs', pkg_name)

        # This creates also the directory pkg_prefix
        pkg = Package.create(pkgdir=pkg_prefix,
                             **pkg_info)
        return pkg


    def enable_package(self, package):

        # Disable other versions of the same application
        for other in self.packages(only_enabled=True):
            if other is not package and other.app_name.lower() == package.app_name.lower():
                self.disable_package(other)

        log.info('Enabling package %s', package)
        package.enabled = True
        self._link_package(package)
        self._create_env_script()
        

    def disable_package(self, package, remove=False):
        if not remove:
            log.info('Disabling package %s', package)
        else:
            log.info('Removing package %s', package)

        package.enabled = False
        self._unlink_package(package)
        self._create_env_script()
        if remove:
            shutil.rmtree(package.path)

    def check_platform(self):
        '''Check that the current platform is the same as box's one'''
        return self._platform == _get_platform()

    def _link_package(self, package):
        log.info('Linking package %s' % package.name)

        for d in DYN_DIRS:
            src_path = os.path.abspath(os.path.join(package.path, d))
            dest_path = os.path.abspath(os.path.join(self.virtual_path, d))
            linkdir(src_path, dest_path)

    def _unlink_package(self, package):
        log.info('Unlinking package %s' % package.name)

        for d in DYN_DIRS:
            src_path = os.path.abspath(os.path.join(package.path, d))
            dest_path = os.path.abspath(os.path.join(self.virtual_path, d))
            unlinkdir(src_path, dest_path)

    def _create_env_script(self):
        virtual_path = self.virtual_path
        path_updates = '\n'.join('export %s="$VIRTUAL_PATH/%s${%s:+:$%s}"' % (v, d, v, v) 
                                 for v, d in STANDARD_PATH_VARS)

        # Collect package env scripts
        pkg_env_scripts = []
        for pkg in self.packages(only_enabled=True):
            local_env_script = os.path.join(pkg.path, 'bpt_meta', 'env_script')
            if os.path.exists(local_env_script):
                f = open(local_env_script)
                try:
                    pkg_env_scripts.append(f.read())
                finally:
                    f.close()

        pkg_env_scripts = '\n'.join(pkg_env_scripts)
        
        env_script = open(ENV_SCRIPT_TMPL).read() % locals() # XXX(ot) close file?
        
        env_script_file = open(self.env_script, 'w')

        try: 
            env_script_file.write(env_script)
        finally:
            env_script_file.close()
        os.chmod(self.env_script, 0755)

        log.info('Created env script')


def require_box(config):
    '''Raise an exception if config.box is None'''
    if config.box is None:
        raise UserError('No box given')

def get_current_box():
    ''' If we are in a box environment, return the current box.
    Otherwise None.'''
    box_path = os.environ.get('BPT_BOX_PATH', None)
    if box_path is not None:
        try:
            box = Box(box_path)
            return box
        except UserError, exc:
            log.warning('Not using current box %s because of error "%s"', box_path, str(exc))
    return None
    
def _get_platform():
    u = os.uname()
    return (u[0], u[4])


# -*- coding: utf-8 -*-
'''\
Utility script to automate installation of packages with common build patterns
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
import sys
import re
from tempfile import mkdtemp
from subprocess import check_call
from shutil import rmtree

from bpt import log, UserError
from bpt.box import Box
from bpt.util import getstatusoutput

SETUPTOOLS_WORKAROUND = True 

class UnsupportedFile(Exception): pass

def guess_unpack_cmd(filename):
    '''
    >>> guess_unpack_cmd('/tmp/python-2.5.tar.gz')
    ('python-2.5', ['tar', 'zsxf', '/tmp/python-2.5.tar.gz'])
    
    >>> guess_unpack_cmd('/tmp/unsupported.7z')
    Traceback (most recent call last):
    ...
    UnsupportedFile: Unsupported file extension
    '''

    cmd = []
    root = os.path.basename(filename)
    root, ext = os.path.splitext(root)
    if ext == '.gz':
        root, ext = os.path.splitext(root)
        if ext != '.tar':
            raise UnsupportedFile('Unsupported extension')
        cmd = ['tar', 'zsxf']
    elif ext == '.bz2':
        root, ext = os.path.splitext(root)
        if ext != '.tar':
            raise UnsupportedFile('Unsupported extension')
        cmd = ['tar', 'jsxf']
    elif ext == '.tar':
        cmd = ['tar', 'sxf']
    elif ext == '.tgz':
        cmd = ['tar', 'zsxf']
    elif ext == '.zip':
        cmd = ['unzip']
    else:
        raise UnsupportedFile('Unsupported file extension')

    cmd.append(os.path.abspath(filename))
    
    return root, cmd

FILENAME_RE = re.compile(r'^(.*)-(\d.*)$')
def guess_name_version(basename):
    '''
    >>> guess_name_version('python-2.5')
    ('python', '2.5')

    >>> guess_name_version('abc.25')
    Traceback (most recent call last):
    ...
    UnsupportedFile: Unable to guess name and version
    '''

    match = FILENAME_RE.match(basename)
    if not match:
        raise UnsupportedFile('Unable to guess name and version')
    name, version = match.groups()
    return name, version

def autobuild(box, filename, configure_options='', keep_temp=False):
    if not os.path.exists(filename):
        raise UserError('File %s does not exist' % filename)
    build_dir = mkdtemp()
    try:
        basename, unpack_cmd = guess_unpack_cmd(filename)
        name, version = guess_name_version(basename)

        log.info('Guessed application name "%s", version "%s". Unpacking the file...', name, version)
        check_call(unpack_cmd, cwd=build_dir)

        unpacked_files = [os.path.join(build_dir, f) for f in os.listdir(build_dir)]
        unpacked_dirs = filter(os.path.isdir, unpacked_files)
        if len(unpacked_dirs) != 1:
            raise UnsupportedFile('Could not find source directory')
        source_dir, = unpacked_dirs
        
        # XXX(ot): disable package if something goes wrong?
        pkg = box.create_package(basename, 
                                 app_name=name, 
                                 app_version=version,
                                 enabled=False)

        if os.path.exists(os.path.join(source_dir, 'configure')):
            cmd_list = [
                "./configure --prefix '%s' %s" % (pkg.path, configure_options),
                "make install"
                ]
        elif os.path.exists(os.path.join(source_dir, 'setup.py')):
            envvars = ''
            if SETUPTOOLS_WORKAROUND:
                # Workaround two bugs of setuptools (fixed in http://bugs.python.org/setuptools/issue54 )
                # - Put the site-packages path in python's path
                # - Create the site-packages directory

                # XXX(ot): find a better solution
                # XXX(ot): this assumes that python inside the box is the same as the current
                python_version = '.'.join([str(x) for x in sys.version_info[:2]])
                site_path = '%s/lib/python%s/site-packages/' % (pkg.path, python_version)
                envvars = 'PYTHONPATH="%s${PYTHONPATH:+:$PYTHONPATH}"' % site_path
                try: os.makedirs(site_path)
                except OSError: pass
            cmd_list = [
                "%s python setup.py install --prefix '%s' %s" % (envvars, pkg.path, configure_options),
                ]
        else:
            raise UnsupportedFile('Do not know how to build source')

        log.info('Building and installing as package %s', pkg.name)
        for cmd in cmd_list:
            check_call(['bash', '-e', box.env_script, cmd], cwd=source_dir)
                
        box.enable_package(pkg)
    finally:
        if keep_temp:
            log.info('Not deleting temporary files in directory %s', build_dir)
        else:
            rmtree(build_dir)
    

        
# -*- coding: utf-8 -*-
'''\
Utility functions to link (and unlink) recursively directories
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os

from bpt import log
from bpt.util import path_diff

def linkdir(src_path, dst_path):
    rel_src_path, _ = path_diff(dst_path, src_path)
    
    for root, dirs, files in os.walk(src_path):
        rel_path, rel_parents = path_diff(src_path, root)
        
        for d in dirs:
            dpath = os.path.join(dst_path, rel_path, d)
            if not os.path.exists(dpath):
                os.makedirs(dpath)
            else:
                assert os.path.isdir(dpath), '%d is a directory in package and a non-directory in destination' % dpath
        
        for f in files:
            spath = os.path.join(rel_parents, rel_src_path, rel_path, f)
            dpath = os.path.join(dst_path, rel_path, f)
            if os.path.lexists(dpath):
                if os.path.islink(dpath):
                    os.unlink(dpath)
                else:
                    log.warn('Existing file (not a symlink): %s' % dpath)
                    continue
            
            os.symlink(spath, dpath)

def unlinkdir(src_path, dst_path):
    for root, dirs, files in os.walk(src_path, topdown=False):
        rel_path, rel_parents = path_diff(src_path, root)
        
        for d in dirs:
            dpath = os.path.join(dst_path, rel_path, d)
            try:
                os.rmdir(dpath)
            except OSError:
                pass
        
        for f in files:
            dpath = os.path.join(dst_path, rel_path, f)
            if not os.path.exists(dpath): 
                continue

            if os.path.islink(dpath):
                if os.path.samefile(dpath, os.path.join(root, f)):
                    os.unlink(dpath)
            else:
                log.warn('%s not a symlink, not removing', dpath)



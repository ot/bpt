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

from bpt.util import path_diff

def linkdir(src_path, dest_path):
    rel_src_path, _ = path_diff(dest_path, src_path)
    
    for root, dirs, files in os.walk(src_path):
        rel_path, rel_parents = path_diff(src_path, root)
        
        for d in dirs:
            dpath = os.path.join(dest_path, rel_path, d)
            if not os.path.exists(dpath):
                os.makedirs(dpath)
            else:
                assert os.path.isdir(dpath), '%d is a directory in package and a non-directory in destination' % dpath
        
        for f in files:
            spath = os.path.join(rel_parents, rel_src_path, rel_path, f)
            dpath = os.path.join(dest_path, rel_path, f)
            if os.path.lexists(dpath):
		if os.path.islink(dpath):
		    os.unlink(dpath)
		else:
		    log.warn('Existing file (not a symlink): %s' % dpath)
		    continue
            
            os.symlink(spath, dpath)



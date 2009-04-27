# -*- coding: utf-8 -*-
'''\
Package class
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os

from bpt import UserError
from bpt.util import load_info

class Package(object):
    '''A package installed in a box, i.e. a subdirectory of <box>/pkgs'''
    def __init__(self, pkgdir):
        # XXX(ot): better exceptions? metadata version handling?

        self.path = pkgdir
        self.name = os.path.basename(pkgdir)

        try:
            pkg_info = load_info(os.path.join(pkgdir, 'bpt_meta', 'pkg_info'))
        except OSError:
            raise UserError('Invalid package')
        
        try:
            self.app_name = pkg_info['app_name']
            self.app_version = pkg_info['app_version']
            self.enabled = pkg_info['enabled']
        except KeyError:
            raise UserError('Invalid package')
        

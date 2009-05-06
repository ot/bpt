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
from bpt.util import store_info, load_info

class Package(object):
    '''A package installed in a box, i.e. a subdirectory of
    <box>/pkgs. The attributes are kept in sync with the stored
    pkg_info'''

    _PackagePool = dict()

    def __new__(cls, pkgdir):
        # Ensure that there is only one instance of Package for every
        # directory, so that no other instance can change pkg_info
        # contents, invalidating our _dict. 

        # XXX(ot): This is obviously not thread safe
        # XXX(ot): This keeps all the packages in memory. Use a
        # weakrefdict instead?

        return Package._PackagePool.setdefault(pkgdir, object.__new__(cls))
        

    def __init__(self, pkgdir):
        # XXX(ot): better exceptions? metadata version handling?

        self._path = pkgdir
        self._name = os.path.basename(pkgdir)
        self._dict = load_info(_pkg_info_file(pkgdir))

        # Sanity check
        for k in ['app_name', 'app_version', 'enabled']:
            if k not in self._dict:
                raise UserError('Invalid package')

    @classmethod
    def create(cls, pkgdir, **kwArgs):
        try:
            os.makedirs(os.path.join(pkgdir, 'bpt_meta'))
        except OSError, exc:
            if exc.errno != 17: # directory exists
                raise

        store_info(_pkg_info_file(pkgdir), kwArgs)
        return cls(pkgdir)
        

    def __getattr__(self, attr):
        try:
            return self._dict[attr]
        except KeyError, exc:
            raise AttributeError(str(exc))

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            return object.__setattr__(self, attr, value)

        self._dict[attr] = value
        store_info(_pkg_info_file(self._path), self._dict)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

def _pkg_info_file(pkgdir):
    return os.path.join(pkgdir, 'bpt_meta', 'pkg_info')

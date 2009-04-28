# -*- coding: utf-8 -*-
'''\
Functions to build sourcedirs into a package box
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
from subprocess import call

from bpt import log, UserError
from bpt.util import getstatusoutput, store_info, load_info
from bpt.package import Package

class SourceDir(object):
    def __init__(self, sourcedir):
        self._sourcedir = sourcedir
        self._rulesfile = os.path.join(sourcedir, 'bpt-rules')
        if not os.path.exists(self._rulesfile):
            raise UserError('Invalid sourcedir')

    @property
    def path(self): return self._sourcedir
    
    def get_var(self, var, can_be_empty=False):
        # XXX(ot) find a better way to do this
        sh_line = ('cd %s;' % self._sourcedir
                   + 'source bpt-rules;'
                   + 'echo ${%s};' % var
                   )
        exitstatus, outtext = getstatusoutput("bash -e -c '%s'" % sh_line)
        assert exitstatus == 0, (exitstatus, outtext)

        outtext = outtext.strip()
        if outtext == '' and not can_be_empty:
            raise Exception('No variable %s' % var)

        return outtext

    def build(self, box, name_suffix=''):
        appname = self.get_var('BPT_APP_NAME')
        version = self.get_var('BPT_APP_VERSION')

        pkg_name = '%s-%s%s' % (appname, version, name_suffix)
        pkg = box.create_package(pkg_name,
                                 app_name=appname,
                                 app_version=version,
                                 enabled=False)
        # XXX(ot): check last box built
        
        if not box.check_platform():
            raise UserError('Current platform is different from box\'s platform')

        log.info('Building application %s, in sourcedir %s', appname, self._sourcedir)

        # Build
        sh_line = ('cd %s;' % self._sourcedir
                   + 'export BPT_PKG_PREFIX="%s";' % pkg.path
                   + 'source bpt-rules;'
                   + 'build;'
                   )
        retcode = call(['bash', '-e', '%s/env' % box.path, sh_line])
        assert retcode == 0, 'FATAL: build script exited with status %s' % retcode

        box.enable_package(pkg)
        
    def clean(self, deep=False):
        log.info('Cleaning sourcedir %s', self.path)
        sh_line = ('cd %s;' % self.path
                   + 'source bpt-rules;'
                   + 'clean;'
                   )
        if deep: 
            sh_line += 'deepclean;'
        exitstatus, outtext = getstatusoutput("bash -e -c '%s'" % sh_line)
        assert exitstatus == 0, (exitstatus, outtext)

    def unittest(self):
        log.info('Testing sourcedir %s', self.path)
        sh_line = ('cd %s;' % self.path
                   + 'source bpt-rules;'
                   + 'unittest'
                   )
        exitstatus = call(['bash', '-e', '-c', sh_line])
        if exitstatus != 0:
            log.warning('unittest exited with exit code %s. Some tests may have failed', exitstatus)
        
    

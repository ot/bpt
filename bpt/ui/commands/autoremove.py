# -*- coding: utf-8 -*-
'''\
autoremove command
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import re
from optparse import make_option

from bpt import UserError, log
from bpt.ui.command import Command
from bpt.box import require_box

class autoremove(Command):
    '''Remove disabled packages not matching the given regexps'''

    usage_args = ''

    def __init__(self):
        options = [make_option('-e', '--exclude', action='append',
                               dest='exclude',
                               default=[],
                               help='Do not remove packages matching REGEX. Can be specified multiple times.',
                               metavar='REGEX')
                   ]
        Command.__init__(self, options)
        

    def _run(self, config, cmd_options, cmd_args):
        require_box(config)
        box = config.box

        regexps = [re.compile(pattern + '$', re.IGNORECASE) for pattern in cmd_options.exclude]

        to_remove = []
        for pkg in box.packages():
            if pkg.enabled: 
                continue
            for regexp in regexps:
                if regexp.match(pkg.name):
                    break
            else: # no exclude regexp matched
                to_remove.append(pkg)

        if not to_remove:
            log.info('No packages to remove')
            return 0

        print 'The following packages will be removed:'
        for pkg in to_remove:
            print '\t%s' % pkg.name
        answer = raw_input('Are you sure [y/N]? ')
        if answer.lower() != 'y':
            return 0
        for pkg in to_remove:
            box.disable_package(pkg, remove=True)
                

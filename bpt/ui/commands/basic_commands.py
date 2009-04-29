# -*- coding: utf-8 -*-
'''\
Basic BPT commands
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
from optparse import make_option
from subprocess import call

from bpt.ui.command import Command
from bpt.box import Box, require_box, get_current_box

class create(Command):
    '''Create a new package box'''

    usage_args = '<box path>'

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1, 1)

        box_path = cmd_args[0]
        Box.create(box_path)

class sync(Command):
    '''Synchronize a package box'''

    usage_args = ''

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 0, 0)

        require_box(config)
        config.box.sync()

class shell(Command):
    '''Run a shell in the box\'s environment'''

    usage_args = ''

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 0, 0)
        require_box(config)

        box_name = '(%s)' % config.box.name
        shell_prompt = r'\[\033[01;31m\]%(box_name)s\[\033[01;32m\] \u@\h\[\033[01;34m\] \w \$\[\033[00m\] ' % locals()

        cur_box = get_current_box()
        if cur_box and cur_box == config.box:
            # Already inside the box env, just execute a shell with the new prompt
            new_env = dict(os.environ)
            new_env['PS1'] = shell_prompt
            call(['bash', '-norc', '-noprofile'], env=new_env)
        else:
            # Have to set the correct environment, so execute a shell using the env script
            # XXX(ot): does this spawn two bashs?
            call(['bash', config.box.env_script, 'PS1="%s"' % shell_prompt, 'bash', '-norc', '-noprofile'])

class status(Command):
    '''Show the installed packages. Packages can be narrowed down using a regex'''

    usage_args = '[pattern1 pattern2 ...]'

    def _run(self, config, cmd_options, cmd_args):
        require_box(config)
        
        fmt = '%-30s| %-20s| %-10s| %-10s|'

        print
        print fmt % ('PACKAGE', 'NAME', 'VERSION', 'STATUS')
        print 

        if len(cmd_args) == 0:
            patterns = None
        else:
            patterns = cmd_args 

        for package in config.box.packages(matching=patterns):
            if package.enabled:
                pkg_status = 'enabled'
            else:
                pkg_status = 'disabled'
            print fmt % (package.name,
                         package.app_name,
                         package.app_version,
                         pkg_status)
        print

class disable(Command):
    '''Disable the packages that match the patterns'''

    usage_args = '[pattern1 pattern2 ...]'

    def __init__(self):
        options = [make_option('-r', '--remove', action='store_true',
                               dest='remove',
                               help='Remove the packages after disabling them.')
                   ]
        Command.__init__(self, options)
        

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)
        require_box(config)

        patterns = cmd_args

        for package in config.box.packages(matching=patterns):
            config.box.disable_package(package, remove=cmd_options.remove)

class enable(Command):
    '''Enable the packages that match the patterns'''

    usage_args = '[pattern1 pattern2 ...]'

    def _run(self, config, cmd_options, cmd_args):
        self._require_args(cmd_args, 1)
        require_box(config)

        patterns = cmd_args

        for package in config.box.packages(matching=patterns):
            config.box.enable_package(package)

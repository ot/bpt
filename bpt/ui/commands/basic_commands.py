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
from subprocess import call

from bpt.ui.command import Command
from bpt.box import Box, require_box, get_current_box

class create(Command):
    
    doc = 'Create a new package box'
    name = 'create'
    usage_args = '<box path>'

    def _run(self, config, cmd_options, cmd_args):
	if len(args) != 1:
	    self.parser.print_help()
	    return 1

        box_path = args[0]
	Box.create(box_path)

class sync(Command):
    doc = 'Synchronize a sandbox'
    name = 'sync'
    usage_args = ''

    def _run(self, config, cmd_options, cmd_args):
	if len(args) != 0:
	    self.parser.print_help()
	    return 1

        require_box(config)
        config.box.sync()

class shell(Command):
    doc = 'Run a shell in the box\'s environment'

    name = 'shell'
    usage_args = ''

    def _run(self, config, cmd_options, cmd_args):
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
            env_script = os.path.join(config.box.path, 'env')
            call(['bash', env_script, 'PS1="%s"' % shell_prompt, 'bash', '-norc', '-noprofile'])

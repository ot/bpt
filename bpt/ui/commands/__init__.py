# -*- coding: utf-8 -*-
'''\
Command dispatching framework for BPT.
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import optparse

# This code is inspired by jhbuild's commands framework

class Command(object):
    '''Base class for Command objects'''
    
    def __init__(self, options=[]):
        assert self.name is not None
        self.options = options

    def execute(self, config, cmd_args):
        options, pos_args = self._parse_args(cmd_args)
        return self._run(config, options, pos_args)

    def _parse_args(self, args):
        self.parser = optparse.OptionParser(
            usage='%%prog %s %s' % (self.name, self.usage_args),
            description=self.doc)
        self.parser.add_options(self.options)
        return self.parser.parse_args(args)

    # Override the following
    doc = ''
    name = None
    usage_args = '[ options ... ]'

    def _run(self, config, options, pos_args):
        raise NotImplementedError

class CommandNotFound(Exception):
    pass

def get_commands():
    return Command.__subclasses__()

def dispatch(command, config, cmd_args):
    '''Run a command. Raises CommandNotFound if command does not exist'''
    
    for cmd_class in get_commands():
        if cmd_class.name == command:
            break
    else:
        raise CommandNotFound
    
    cmd = cmd_class()
    ret = cmd.execute(config, cmd_args)
    if ret is None: ret = 0
    return ret

from bpt.ui.commands import \
    basic_commands

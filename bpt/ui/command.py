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
    '''Base class for Command objects.'''
    
    def __init__(self, options=None):
        if options is None:
            options = []
        self.options = options

    def execute(self, config, cmd_args):
        options, pos_args = self._parse_args(cmd_args)
        try:
            return self._run(config, options, pos_args)
        except InvalidCommandLine:
            self.parser.print_help()
            return 1

    def _parse_args(self, args):
        self.parser = optparse.OptionParser(
            usage='%%prog %s %s' % (type(self).__name__, self.usage_args),
            description=type(self).__doc__)
        self.parser.add_options(self.options)
        return self.parser.parse_args(args)

    def _require_args(self, cmd_args, at_least=0, at_most=None):
        l = len(cmd_args)
        if l < at_least:
            raise InvalidCommandLine
        if at_most is not None and l > at_most:
            raise InvalidCommandLine
        

    # Override the following 
    # __doc__ = ...
    usage_args = '[ options ... ]'

    def _run(self, config, options, pos_args):
        raise NotImplementedError

class InvalidCommandLine(Exception): pass

class CommandNotFound(Exception): pass

def get_commands():
    return Command.__subclasses__() # pylint: disable-msg=E1101

def dispatch(command, config, cmd_args):
    '''Run a command. Raises CommandNotFound if command does not exist'''
    
    for cmd_class in get_commands():
        if cmd_class.__name__ == command:
            break
    else:
        raise CommandNotFound
    
    cmd = cmd_class()
    ret = cmd.execute(config, cmd_args)
    if ret is None: ret = 0
    return ret


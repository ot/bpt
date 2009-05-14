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

import re

from bpt.ui.config import BPTOptionParser

# XXX(ot): is there something standard for this?
class classproperty(object):
    def __init__(self, fget):
        self._fget = fget

    def __get__(self, obj, objtype):
        return self._fget(objtype)

# This code is inspired by jhbuild's commands framework
class Command(object):
    '''Base class for Command objects.'''
    
    def __init__(self, options=None):
        if options is None:
            options = []
        self.options = options

    # Override the following 
    # __doc__ = ...
    usage_args = '[ options ... ]'

    @classproperty
    def name(cls):
        return cls.__name__
    
    @classproperty
    def description(cls):
        return re.sub('\s+', ' ', cls.__doc__)

    def execute(self, config, cmd_args):
        options, pos_args = self._parse_args(cmd_args)
        try:
            return self._run(config, options, pos_args)
        except InvalidCommandLine:
            self.parser.print_help()
            return 1

    def _parse_args(self, args):
        self.parser = BPTOptionParser(
            usage='%%prog %s %s' % (self.name, self.usage_args),
            description=self.description)
        self.parser.add_options(self.options)
        return self.parser.parse_args(args)

    def _require_args(self, cmd_args, at_least=0, at_most=None):
        l = len(cmd_args)
        if l < at_least:
            raise InvalidCommandLine
        if at_most is not None and l > at_most:
            raise InvalidCommandLine
        

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


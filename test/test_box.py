# -*- coding: utf-8 -*-
'''\
Unit tests for bpt.box
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

import os
from tempfile import mktemp
from shutil import rmtree

from nose.tools import assert_raises, with_setup

from bpt import UserError
from bpt.box import Box
from bpt.package import Package

def setup():
    global box1_path
    box1_path = mktemp()

def rmbox():
    try:
        rmtree(box1_path)
    except OSError:
        pass

@with_setup(teardown=rmbox)
def test_create():
    assert_raises(UserError, Box, box1_path) # No box, should raise
    box = Box.create(box1_path)
    assert box.path == box1_path
    assert_raises(UserError, Box.create, box1_path)

@with_setup(teardown=rmbox)
def test_packages():
    box = Box.create(box1_path)
    foo = box.create_package('foo-0.1', app_name='foo', app_version='0.1', enabled=True)
    bar = box.create_package('bar-0.2', app_name='bar', app_version='0.2', enabled=False)
    
    assert len(list(box.packages())) == 2
    l = list(box.packages(only_enabled=True))
    assert len(l) == 1
    assert l[0] is foo
    
    box.disable_package(foo)
    assert len(list(box.packages(only_enabled=True))) == 0
    
    box.enable_package(foo)
    box.enable_package(bar)
    assert len(list(box.packages(only_enabled=True))) == 2
    assert len(list(box.packages(only_enabled=True, matching=['foo.*']))) == 1

    box.disable_package(foo)
    assert len(list(box.packages(only_enabled=True, matching=['foo.*']))) == 0
    assert len(list(box.packages(matching=['foo.*']))) == 1
    
    box.disable_package(bar, remove=True)
    assert len(list(box.packages())) == 1
    
    
    
    
    
    
    
    
    

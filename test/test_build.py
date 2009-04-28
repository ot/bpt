# -*- coding: utf-8 -*-
'''\
Unit tests for bpt.build
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
from bpt.build import SourceDir

def setup():
    global box1_path
    global box2_path
    box1_path = mktemp()
    box2_path = mktemp()

    global sourcedirs_path
    sourcedirs_path = os.path.join(os.path.dirname(__file__), 'fake_sourcedirs')

def rmbox():
    try:
        rmtree(box1_path)
        rmtree(box2_path)
    except OSError:
        pass
def test_sourcedir():
    assert_raises(UserError, SourceDir, box1_path) # Not a sourcedir, should raise

@with_setup(teardown=rmbox)
def test_build():
    box = Box.create(box1_path)
    box2 = Box.create(box2_path)

    foo_path = os.path.join(sourcedirs_path, 'foo')
    foo_source = SourceDir(foo_path)
    assert foo_source.path == foo_path
    bar_path = os.path.join(sourcedirs_path, 'bar')
    bar_source = SourceDir(bar_path)

    foo = foo_source.build(box)
    bar = bar_source.build(box)
    foo_new = foo_source.build(box, name_suffix='-new')

    assert foo.enabled == False
    assert foo_new.enabled == True

    assert os.path.samefile(os.path.join(box.virtual_path, 'lib', 'd', 'foo'),
                            os.path.join(foo_new.path, 'lib', 'd', 'foo'))
    
    assert foo_source.unittest() == True
    assert bar_source.unittest() == False
    
    foo_source.build(box2) # Should clean before

    assert len(list(box.packages(only_enabled=True))) == 2

    box.disable_package(foo_new)
    assert not os.path.exists(os.path.join(box.virtual_path, 'lib', 'd', 'foo'))

    foo_source.clean()
    bar_source.clean()

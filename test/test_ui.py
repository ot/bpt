# -*- coding: utf-8 -*-
'''\
Unit tests for box ui
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

from bpt.ui.main import main

def setup():
    global box1_path
    box1_path = mktemp()

def rmbox():
    try:
        rmtree(box1_path)
    except OSError:
        pass

def box(args):
    return main(['box'] + args, do_log=False)

@with_setup(teardown=rmbox)
def test_ui():
    assert box(['-b', box1_path, 'status']) != 0 # No box, error
    assert box(['create', box1_path]) == 0
    assert box(['create', box1_path]) != 0 # Box already existing

    assert box(['-b', box1_path, 'build', 'test/fake_sourcedirs/bar']) == 0
    assert box(['-b', box1_path, 'build', 'test/fake_sourcedirs/foo']) == 0
    assert box(['-b', box1_path, 'build', '-s', '-new', 'test/fake_sourcedirs/foo']) == 0

    assert box(['-b', box1_path, 'clean', '--deep', 'test/fake_sourcedirs/bar']) == 0
    assert box(['-b', box1_path, 'unittest', 'test/fake_sourcedirs/bar']) == 0
    
    assert box(['-b', box1_path, 'status']) == 0

    assert box(['-b', box1_path, 'disable', 'bar.*']) == 0
    assert box(['-b', box1_path, 'enable', 'bar.*']) == 0
    assert box(['-b', box1_path, 'disable', '-r', 'foo-0.1']) == 0

    assert box(['-b', box1_path, 'sync']) == 0

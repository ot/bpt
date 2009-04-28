# -*- coding: utf-8 -*-
'''\
Basic setup.py for BPT using distutils
'''
#*****************************************************************************
#       Copyright (C) 2009 Giuseppe Ottaviano <giuott@gmail.com>
#
#  Distributed under the terms of the GPL License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

app_name='bpt'
from bpt import __version__ as app_version

if __name__ == '__main__':
    from distutils.core import setup
    setup(name=app_name,
          version=app_version,
          description='Tool to create isolated environments',
          author='Giuseppe Ottaviano',
          author_email='giuott@gmail.com',
          url='http://pypi.python.org/pypi/bpt',
          packages=['bpt',
                    'bpt.ui',
                    'bpt.ui.commands'
                    ],
	  package_data={'bpt':['env_script.tmpl']},
          scripts=['box'],
          classifiers=['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Intended Audience :: Developers',
                       'Intended Audience :: System Administrators',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Operating System :: POSIX',
                       'Topic :: Software Development :: Build Tools']
          )


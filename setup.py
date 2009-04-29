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
    import os
    from distutils.core import setup

    f = open(os.path.join(os.path.dirname(__file__), 'README'))
    long_description = f.read().strip()
    f.close()

    setup(name=app_name,
          version=app_version,
          description='Tool to create isolated environments',
          long_description=long_description,
          author='Giuseppe Ottaviano',
          author_email='giuott@gmail.com',
          url='http://pypi.python.org/pypi/bpt',
          packages=['bpt',
                    'bpt.ui',
                    'bpt.ui.commands'
                    ],
	  package_data={'bpt':['env_script.tmpl', 'bpt_base_script.sh']},
          scripts=['box'],
          classifiers=['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Intended Audience :: Developers',
                       'Intended Audience :: System Administrators',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Operating System :: POSIX',
                       'Topic :: Software Development :: Build Tools']
          )


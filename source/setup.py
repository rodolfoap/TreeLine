#!/usr/bin/env python
from distutils.core import setup
import py2exe

guiProg = {'script': 'treeline.py',
           'icon_resources': [(1, '../win/treeline.ico')],
           'dest_base': 'treeline'}

consoleProg = {'script': 'treeline.py',
               'icon_resources': [(1, '../win/treeline.ico')],
               'dest_base': 'treeline_dos'}

options = {'py2exe': {'includes': ['sip', 'urllib2'],
                      'dist_dir': 'dist/lib'}}

setup(windows=[guiProg], console=[consoleProg], options=options)

# run with: python setup.py py2exe

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creates a single executable in thisdir/build/ directory with a subdir
starting with the letters 'exe'. Allows for multiple platform builds
without conflicts.

To build:
    'python setup.py build' (in the directory of this file)
To make a Windows installer instead of binary:
    'python setup.py bdist_msi'
To make a Mac installer instead of binary:
    'python setup.py bdist_dmg'
"""

import sys
from cx_Freeze import setup, Executable

# #######################
# OPTIONS AREA

# Dependencies are supposed to be auto detected but might need fine tuning.
# uncomment this and adjust if needed. And uncomment setup[options] below.
# build_exe_options = {"packages": ["Tkinter"], "excludes": []}

##executableslist = [
##    Executable("records_manager_Tk_GUI.py", base=base),
##    Executable("records.py")
##]

# GUI applications require a different base on Windows (default is console)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# END OPTIONS
# #######################

# BUILD
# distutils module looks for this below when run as:
# $> python setup.py build
setup(name="records",
      version="1.0",
      description="Records Management Application for CASC",
      # options = {"build_exe": build_exe_options},
      executables=[Executable("records_manager_Tk_GUI.py", base=base)]
      )

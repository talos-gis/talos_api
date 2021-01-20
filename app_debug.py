#!/usr/bin/env python3

# Copyright (c) 2016 PyWPS Project Steering Committee
# 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import flask

# we need to set the root before we import the main_page as there are relative paths to this root (i.e. config files)
import sys
import os


my_modules = [
    r'D:\dev\gis\gdal\gdal\swig\python\gdal-utils',
    r'D:\dev\gis\pywps',
    r'D:\dev\gis\gdalos\src',
    r'D:\dev\gis\TaLoS\1\p\talos\src',
]
for m in my_modules:
    print(f'adding {m} to path')
    sys.path.insert(0, m)

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

if __name__ == "__main__":
    from demo import main
    main()

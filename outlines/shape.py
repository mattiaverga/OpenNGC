# -*- coding:utf-8 -*-
#
# MIT License
#
# Copyright (c) 2019 Mattia Verga <mattia.verga@tiscali.it>
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
#

"""A simple script to create a Catgen readable input file.

The script will read all the files in the 'objects' directory
and outputs a single file with simplified objects outlines.

If you want to increase objects shape definition you can modify the
shape_precision value, but be aware that this will also
increase the output file size.
"""

import csv
from shapely.geometry import LineString
from os import walk
from os.path import join


shape_precision = 0.002

files_list = []
for (dirpath, dirnames, filenames) in walk('objects'):
    files_list.extend(filenames)
    break

output = open('outlines_catgen.dat', 'w')

print(f'Processing {len(files_list)} object files...')

for dso in files_list:
    with open(join('objects', dso), 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        points = []
        for line in reader:
            points.append((float(line["RAJ2000"]), float(line["DEJ2000"])))
        outline = LineString(points).simplify(shape_precision)
        for idx, p in enumerate(outline.coords, 1):
            if idx == 1:
                output.write(' '.join([f'{p[0]:.5f}',
                                       f'{p[1]:.5f}',
                                       f'{"0":6s}',
                                       dso.split('.')[0], ]))
            elif idx < len(outline.coords):
                output.write(' '.join([f'{p[0]:.5f}',
                                       f'{p[1]:.5f}',
                                       f'{"2":6s}', ]))
            else:
                output.write(' '.join([f'{p[0]:.5f}',
                                       f'{p[1]:.5f}',
                                       f'{"1":6s}', ]))
            output.write('\n')

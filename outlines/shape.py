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

"""A simple script to create nebula outlines catalog for several software.

The script will read all the files in the 'objects' directory
and outputs a single file with simplified objects outlines.

If you want to increase objects shape definition you can modify the
shape_precision value, but be aware that this will also
increase the output file size.
"""

import csv
import re
from os import walk
from os.path import join

import click
from shapely.geometry import LineString


shape_precision = 0.002
supported_outputs = ['catgen', 'stellarium', ]
level_color_map = {'1': '#222222',
                   '2': '#555555',
                   '3': '#888888',
                   }

@click.group()
def create_cat():
    """Create nebulae catalog files."""
    pass

def catgen(dso, points_counter, idx, p, level=None):
    """Format point entry for Skychart's Catgen."""
    if idx == 1:
        # Starting point identified by 0
        # also set the object name
        # and optionally the brightness level
        if level is None:
            return(f'{p[0]:<9.5f} {p[1]:<9.5f} 0 {dso.split(".")[0]:7s}\n')
        else:
            return(f'{p[0]:<9.5f} {p[1]:<9.5f} 0 {level} '
                   f'{dso.split(".")[0]:7s}\n')
    elif idx < points_counter:
        # Intermediate point identified by 2
        return(f'{p[0]:<9.5f} {p[1]:<9.5f} 2\n')
    else:
        # Final point identified by 1
        return(f'{p[0]:<9.5f} {p[1]:<9.5f} 1\n')

def stellarium(dso, points_counter, idx, p, level=None):
    """Format point entry for Stellarium."""
    ra = float(p[0]) / 15
    if idx == 1:
        # Starting point identified by "start"
        # also set the object name
        return(f'{ra:08.5f} {p[1]:+09.5f} start  {dso.split("_")[0]:7s}\n')
    elif idx < points_counter:
        # Intermediate point identified by "vertex"
        return(f'{ra:08.5f} {p[1]:+09.5f} vertex\n')
    else:
        # Final point identified by "end"
        return(f'{ra:08.5f} {p[1]:+09.5f} end   \n')


@click.option('--software', type=click.Choice(supported_outputs),
              prompt=True, help='The software you want to make the catalog for.')
@click.option('--level', type=click.Choice([None, '1', '2' ,'3']), default = None,
              help='The brightness level to calculate the shape for.')
@create_cat.command()
def create_outlines(software, level):
    """Generate the outlines catalog file for the given software.

    Args:
        software: the software you would like to generate the catalog for.
        level: the brightness level you want to use to calculate the shape.
            If you don't enter any value, the catalog file will contain
            all levels.
    """
    files_list = []
    for (dirpath, dirnames, filenames) in walk('objects'):
        if level is not None:
            for fname in filenames:
                if f'_lv{level}.' in fname or not f'_lv' in fname:
                    files_list.append(fname)
        else:
            files_list.extend(filenames)

    output = open(f'outlines_{software}.dat', 'w')

    print(f'Processing {len(files_list)} object files...')

    for dso in files_list:
        match = re.search(r'_lv(\d).', dso)
        level = match.group(1) if match is not None else '2'
        with open(join('objects', dso), 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            points = [[], ]
            shape_nbr = 0
            for line in reader:
                points[shape_nbr].append((float(line["RAJ2000"]), float(line["DEJ2000"])))
                if line["Cont_Flag"] == '*':
                    points.append([])
                    shape_nbr += 1
            for shape in points:
                if shape:
                    outline = LineString(shape).simplify(shape_precision)
                    points_counter = len(outline.coords)
                    for idx, p in enumerate(outline.coords, 1):
                        output.write(eval(software)(dso, points_counter, idx, p, level))


@click.option('--software', type=click.Choice(supported_outputs),
              prompt=True, help='The software you want to make the catalog for.')
@create_cat.command()
def create_surfaces(software):
    """Generate the surfaces catalog file for the given software.

    Args:
        software: the software you would like to generate the catalog for.
    """
    files_list = []
    for (dirpath, dirnames, filenames) in walk('objects'):
        files_list.extend(filenames)

    output = open(f'surfaces_{software}.dat', 'w')

    print(f'Processing {len(files_list)} object files...')

    for dso in files_list:
        match = re.search(r'_lv(\d).', dso)
        level = match.group(1) if match is not None else '2'
        with open(join('objects', dso), 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            points = [[], ]
            shape_nbr = 0
            for line in reader:
                points[shape_nbr].append((float(line["RAJ2000"]), float(line["DEJ2000"])))
                if line["Cont_Flag"] == '*':
                    points.append([])
                    shape_nbr += 1
            for shape in points:
                if shape:
                    outline = LineString(shape).simplify(shape_precision)
                    points_counter = len(outline.coords)
                    for idx, p in enumerate(outline.coords, 1):
                        output.write(eval(software)(dso, points_counter, idx, p, level))


if __name__ == '__main__':
    create_cat()

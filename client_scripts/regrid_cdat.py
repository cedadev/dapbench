#!/usr/bin/env python
# regrid_cdat.py
#
#
# Scripts implementing this test should do simple bilinear interpolation
# regridding on the dataset.  Scripts can assume the dataset contains
# a single variable.
#
#  usage: %prog dataset lons lats outfile
#
# where lons and lats are integers representing number of grid points

import sys

dataset, lons, lats, outfile = sys.argv[1:]

lons = int(lons)
lats = int(lats)

#!TODO

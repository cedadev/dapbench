#!/usr/bin/env python
# BSD Licence
# Copyright (c) 2011, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

# subset_2d_cdat.py
#
#
# Scripts implementing this test should subset a dataset to a given
# bounding box.  Scripts can assume the given variable is a 2D field.
#
#  usage: %prog dataset variable bbox outputfile
#
# where bbox = 'lon0,lon1,lat0,lat1'

import sys
import netCDF4

dataset, variable, bbox, outfile = sys.argv[1:]

lon0, lon1, lat0, lat1 = (float(x) for x in bbox.split(','))

ds = netCDF4.Dataset(dataset)
var = ds.variables[variable]

# Find lat and lon
slices = []
for dimname in var.dimensions:
    if not dimname in ds.variables:
        slices.append(None)

    dim = ds.variables[dimname]
    if 'axis' in dim.ncattrs():
        if dim.axis == 'X':
            slices.append(dim >= lon0 && dim <= lon1)
        elif dim.axis == 'Y':
            slices.append(dim >= lat0 && dim <= lat1)

print slices
    

subset = var[*slices]

#!TODO: output subset

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
import cdms2

dataset, lons, lats, outfile = sys.argv[1:]

lons = int(lons)
lats = int(lats)

#!TODO: should I check order='yx'
#!TODO: refine grid spec
dest_grid = cdms2.createUniformGrid(-90, lats, 180./lats, 
                                    0, lons, 360./lons)


ds = cdms2.open(dataset)
# Select first variable with a grid
for var in ds.variables.values():
    if var.getGrid():
        print 'Regridding variable %s' % var.id
        break
else:
    raise Exception("No variable with grid found")

new_var = var.regrid(dest_grid)

out = cdms2.open(outfile, 'w')
out.write(new_var, extend=0)

out.close()
ds.close()

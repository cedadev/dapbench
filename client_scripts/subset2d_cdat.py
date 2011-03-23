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
import cdms2

dataset, variable, bbox, outfile = sys.argv[1:]

lon0, lon1, lat0, lat1 = (float(x) for x in bbox.split(','))

ds = cdms2.open(dataset)
var = ds[variable]

subset = var(longitute=(lon0, lon1),
             latitude=(lat0, lat1))

out_ds = cdms2.open(outfile, 'w')
out_ds.write(subset)

out_ds.close()

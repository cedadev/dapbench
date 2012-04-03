# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Tools for creating test data.

"""

import netCDF4

def anonymise(ncpath):
    """
    Remove metadata from the netetcdf file ncpath.

    @warning: This function is destructive and isn't written to be generic
        for any CF-NetCDF file.

    """
    exclude_attrs = set(['standard_name', 'missing_value', '_FillValue',
                         'Conventions', 'cell_bounds', 'cell_methods',
                         'bounds', 'units', 'axis', 'long_name',
                         'positive', 'calendar'])
    d = netCDF4.Dataset(ncpath, 'r+')

    def del_attrs(context):
        for attr in context.ncattrs():
            if attr not in exclude_attrs:
                context.__delattr__(attr)

    del_attrs(d)
    for var in d.variables.values():
        del_attrs(var)
    
    d.close()

def extrude(ncpath, times):
    """
    Extend the time dimension of a dataset.

    """
    d = netCDF4.Dataset(ncpath, 'r+')

    # Get time
    t_dim = d.dimensions['time']
    t = d.variables['time']
    t_len = t.shape[0]
    assert t.axis == 'T'
    assert t.dimensions == ('time', )

    # For each axis containing time
    for varname in d.variables:
        if varname == 'time':
            continue
        var = d.variables[varname]

        if 'time' not in var.dimensions:
            continue

        if 'time' != var.dimensions[0]:
            raise ValueError('Only supports time as first dimension')

        for i in range(times):
            n2 = var.shape[0]
            var[n2:n2+t_len] = var[:t_len]

    # For the time dimension
    # Make some simple assumptions about it's monotonicity
    a = t[:t_len]
    dt = t[1] - t[0]
    for i in range(times):
        a = a + (t[-1] + dt)
        n2 = t.shape[0]
        t[n2:n2+t_len] = a

    d.close()

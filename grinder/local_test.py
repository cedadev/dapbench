"""
Try running sequential scan on a local file.

"""

from dapbench.jython.grinder import DapTestRunner

local_file = '/home/spascoe/git/dapbench/ta_20101129/ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197812010600-197901010000.nc'


# Make 20 requests to variable ta
TestRunner = DapTestRunner.configure('Local NetCDF test',
                                     local_file, 'ta',
                                     {'time': 20})
                                     

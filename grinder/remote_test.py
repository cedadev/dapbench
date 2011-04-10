"""
Try running sequential scan on a local file.

"""

from dapbench.jython.grinder import DapTestRunner

url = 'http://esg-dev1.badc.rl.ac.uk:8081/ta_20101129/ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197812010600-197901010000.nc'


# Make 120 requests to variable ta
TestRunner = DapTestRunner.configure('Remote NetCDF test',
                                     url, 'ta',
                                     {'time': 120})
                                     

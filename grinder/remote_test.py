"""
Try running sequential scan on a local file.

"""

from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

from dapbench.jython.util import generate_subset_requests
from dapbench.jython.netcdf import Dataset


import data_urls

partition_dict = {'time': 120}               
variable = 'ta'


# Take the first dataset at all 3 bases
tests = []
i = 1
for base in data_urls.DAP_BASES:
    url = data_urls.make_dataset_list(base).next()
    test = Test(i, base)
    i += 1

    print test
    def f(req):
        return req()
    test.record(f)

    ds = Dataset(url)
    var = ds.variables[variable]
    
    requests = generate_subset_requests(var, partition_dict)

    tests.append((url, test, f, requests))


class TestRunner(object):
    def __call__(self):
        for url, test, f, requests in tests:
            grinder.logger.output('Scanning dataset %s' % url)
            
            # Each invocation of f is recorded
            for req in requests:
                grinder.logger.output('Requesting %s' % req)
                data = f(req)
                grinder.logger.output('Data returned of shape %s' % data.shape)

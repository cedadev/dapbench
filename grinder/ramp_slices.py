"""
Ramp-up the number of slices to split the request into on each run

"""

import random

from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

from dapbench.jython.util import generate_subset_requests
from dapbench.jython.netcdf import Dataset


#
# Select a dataset to test.  This selection is specific to the
# BADC test server.  Adapt to suite your test server.
#
import data_urls

# The BADC test datasets contain variable 'ta' with 1440 timepoints
variable = 'ta'
server = 'tds'

dataset_url = random.choice(list(data_urls.make_dataset_list(server)))
ds = Dataset(dataset_url)
variable = ds.variables[variable]

#
# partitions dictate into how many slices each run will divide the request
#
partitions = [15, 30, 60, 120, 240, 480, 720, 1440]

class Instrumented(object):
    next_test = 1
    def __init__(self, partition):
        self.test = Test(Instrumented.next_test, 
                         'Partition into %d slices' % partition)
        Instrumented.next_test += 1

        self.test_tot = Test(Instrumented.next_test,
                             'Total for %d slices' % partition)
        Instrumented.next_test += 1

        self.requests = generate_subset_requests(variable, {'time': partition})

        # Create a fresh callable to instrument
        def f(req):
            return req()
        self.test.record(f)
        self.f = f

        def f2():
            for req in self.requests:
                grinder.logger.output('Requesting %s' % req)
                data = self.f(req)
                grinder.logger.output('Data returned of shape %s' % data.shape)

        self.test_tot.record(f2)
        self.f2 = f2
    
    def __call__(self):
        self.f2()


# Create tests
tests = []
for partition in partitions:
    tests.append(Instrumented(partition))

class TestRunner(object):
    def __call__(self):
        for test in tests:
            test()

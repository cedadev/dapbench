"""
Ramp-up the number of slices to split the request into on each run

"""

import random

from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

from dapbench.jython.util import generate_subset_requests
from dapbench.jython.netcdf import Dataset

import data_urls

time_len = 1440
partitions = [15, 30, 60, 120, 240, 480, 720, 1440]

server = 'pydap'
variable = 'ta'

# Select random dataset
dataset_url = random.choice(list(data_urls.make_dataset_list(server)))
ds = Dataset(dataset_url)
variable = ds.variables[variable]


class Instrumented(object):
    next_test = 1
    def __init__(self, partition):
        self.test = Test(Instrumented.next_test, 
                         'Partition into %d slices' % partition)
        Instrumented.next_test += 1

        self.requests = generate_subset_requests(variable, {'time': partition})

        # Create a fresh callable to instrument
        def f(req):
            return req()
        self.test.record(f)
        self.f = f
    
    def __call__(self):
        for req in self.requests:
            grinder.logger.output('Requesting %s' % req)
            data = self.f(req)
            grinder.logger.output('Data returned of shape %s' % data.shape)


# Create tests
tests = []
for partition in partitions:
    tests.append(Instrumented(partition))

class TestRunner(object):
    def __call__(self):
        for test in tests:
            test()

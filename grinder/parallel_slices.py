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
partition_dict = {'time': 120}

server = 'pydap'
variable = 'ta'

test = Test(1, "Parallel slice request")
def call_request(req):
    return req()
test.record(call_request)

dataset_list = list(data_urls.make_dataset_list(server))

class TestRunner(object):
    def __init__(self):
        self.thread = grinder.getThreadNumber()
        # Select random dataset
        self.dataset_url = random.choice(dataset_list)
        self.ds = Dataset(self.dataset_url)
        self.variable = self.ds.variables[variable]
        self.requests = generate_subset_requests(self.variable,
                                                 partition_dict)

        grinder.logger.output('Thread %d selecting %s' % (self.thread,
                                                          self.dataset_url))

    def __call__(self):
        grinder.sleep(5000*self.thread, 0)
        grinder.logger.output('Thread %d starting requests' % self.thread)

        for req in self.requests:
            grinder.logger.output('Requesting %s' % req)
            data = call_request(req)
            grinder.logger.output('Data returned of shape %s' % data.shape)



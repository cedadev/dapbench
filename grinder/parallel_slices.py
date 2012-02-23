"""
Request slices in parallel.

"""

import random

from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

from dapbench.jython.util import generate_subset_requests
from dapbench.jython.netcdf import Dataset

import data_urls

properties = grinder.properties.getPropertySubset('dapbench.')

variable = properties['variable']
server = properties['server']
time_len = int(properties['time_len'])
req_sample_size = properties['req_sample_size']

partition_dict = {'time': time_len}
dataset_list = list(data_urls.make_dataset_list(server))

test = Test(1, "Parallel slice request")
def call_request(req):
    return req()
test.record(call_request)

class TestRunner(object):
    def __init__(self):
        self.thread = grinder.getThreadNumber()
        # Select random dataset
        #!TODO: select dataset by Thread number?
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

        # Each thread randomly selects a sample requests
        requests = random.choice(list(self.requests), req_sample_size)
        
        for req in requests:
            grinder.logger.output('Requesting %s' % req)
            data = call_request(req)
            grinder.logger.output('Data returned of shape %s' % data.shape)




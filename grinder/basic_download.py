# Simple HTTP example
#
# A simple example using the HTTP plugin that shows the retrieval of a
# single page via HTTP. The resulting page is written to a file.
#
# More complex HTTP scripts are best created with the TCPProxy.

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest

import data_urls
import jarray
import random

test1 = Test(1, "Request random dataset")
req = HTTPRequest()
req.setReadResponseBody(False)
chunk = 1024*512

properties = grinder.properties.getPropertySubset('dapbench.')

server = properties['server']

def streamed_get(url):
    buf = jarray.zeros(chunk, 'b')
    total = 0
    resp = req.GET(url)
    stream = resp.getInputStream()
    ret = 0
    while ret != -1:
        ret = stream.read(buf)
        total += ret

    return total
streamed_get = test1.wrap(streamed_get)

class TestRunner:
    def __call__(self):
        dataset_url = random.choice(list(data_urls.make_dataset_list(server)))
        grinder.logger.output('Downloading %s' % dataset_url)
        result = streamed_get(dataset_url)
        grinder.logger.output('Transfered %d bytes' % result)
    

# Test dapbench installation

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test


# Check configured path
import sys
print 'Python path is %s' % sys.path

# Check dapbench is importable
from dapbench.jython.netcdf import Dataset


# A shorter alias for the grinder.logger.output() method.
log = grinder.logger.output

# Create a Test with a test number and a description. The test will be
# automatically registered with The Grinder console if you are using
# it.
test1 = Test(1, "Dapbench log method")
logWrapper = test1.wrap(log)

class TestRunner(object):
    def __call__(self):
        logWrapper("Hello from dapbench")

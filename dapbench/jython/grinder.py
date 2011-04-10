"""
Utilities for running load testing processes within `The Grinder`_ framework.

.. _`The Grinder`: http://grinder.sourceforge.net

"""

from dapbench.jython.util import generate_subset_requests
from dapbench.jython.netcdf import Dataset

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test

class DapTestRunner(object):
    """
    A grinder test runner which requests a single variable
    from an OPeNDAP dataset in a configurable number of chunks.
    These chunks are stored in a class-wide queue and therefore
    when there are more than one thread the variable will be
    requested in parallel.
    
    """

    # Subclass or set in classmethod
    requests = None
    test = None

    def __call__(self):
        for req in self.requests:
            grinder.logger.output('Requesting %s' % req)
            data = self.test.wrap(req)()
            grinder.logger.output('Data returned of shape %s' % data.shape)

    @classmethod
    def configure(klass, name, location, variable, partition_dict):
        ds = Dataset(location)
        var = ds.variables[variable]

        klass.requests = generate_subset_requests(var, partition_dict)
        #!TODO: detect next test number
        klass.test = Test(1, name)

        return klass
        

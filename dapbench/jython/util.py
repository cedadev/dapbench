# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Utilities for running jython performance tests.

"""

from dapbench.jython.netcdf import Dataset

def partition_shape(shape, partitions):
    """
    Yields slices of an array described by <shape> that split into Nx-parts
    allong each axis where partions = (N0, N1, N2, ...)

    """
    assert len(shape) == len(partitions)

    N = partitions[0]
    steps = range(0, shape[0], shape[0] / N)
    while steps:
        if len(steps) == 1:
            s = slice(steps[0], None)
        else:
            s = slice(steps[0], steps[1])

        if len(shape) == 1:
            yield [s]
        else:
            for slices in partition_shape(shape[1:], partitions[1:]):
                yield [s] + slices
            
        steps = steps[1:]


def partition_variable(variable, partition_dict):
    """
    As partition_shape() but takes a mapping of dimension-name to number
    of partitions as it's second argument.  <variable> is a VariableWrapper
    instance.

    """
    partitions = []
    for dim in variable.dimensions:
        if dim.name in partition_dict:
            partitions.append(partition_dict[dim.name])
        else:
            partitions.append(1)

    return partition_shape(variable.shape, partitions)
                              

class DapVarSubset(object):
    """
    Encapsulates a variable and a subset.  When called it makes the
    variable request.

    """
    def __init__(self, variable, subset):
        self.variable = variable
        self.subset = subset

    def __repr__(self):
        return '<DapVarSubset %s%s>' % (self.variable.name, 
                                        _repr_slices(self.subset))

    def __call__(self):
        return self.variable[tuple(self.subset)]


def _repr_slices(slices):
    sl = []
    for s in slices:
        def f(v):
            if v is None:
                return ''
            else:
                return str(v)

        p = [f(s.start), f(s.stop), f(s.step)]
        sl.append('[%s]' % ':'.join(p))
    return ''.join(sl)


def generate_subset_requests(variable, partition_dict):
    """
    Yields callables which when called makes a subset request
    to <variable> according to the partitions specified.

    Made threadsafe with a lock.

    """

    def gen():
        for subset in partition_variable(variable, partition_dict):
            yield DapVarSubset(variable, subset)
    
    return LockedIterator(gen())



#
# From stackoverflow question 1131430
#
import threading
class LockedIterator(object):
    def __init__(self, it):
        self.lock = threading.Lock()
        self.it = it.__iter__()

    def __iter__(self): return self

    def next(self):
        self.lock.acquire()
        try:
            return self.it.next()
        finally:
            self.lock.release()


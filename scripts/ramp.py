#!/usr/bin/env python
"""
Stand-alone equivilent of ramp_slices.py for individual execution
without dependencies.

"""

import datetime
import urllib
import sys

DATASET = 'http://esg-dev1.badc.rl.ac.uk:8080/opendap/ta_20101129/ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197901010600-198001010000.nc'
VARIABLE = 'ta'
SHAPE = [1440,4,144,192]

BLOCK = 2**20 / 2

time_partitions = [15, 30, 60, 120, 240, 480, 720, 1440]


def main():
    for tp in time_partitions:
        print '=== Partition into %d time slices ===' % tp
        print_timestamp()
        p = [tp]+[1]*(len(SHAPE)-1)
        partitions = partition_shape(SHAPE, p)
        request_partitions(partitions)
        print_timestamp()

def request_partitions(partitions):
    for partition in partitions:
        subset = ''.join(_repr_slice(s) for s in partition)
        url =  '%s.dods?%s%s' % (DATASET, VARIABLE, subset)
        download(url)
        sys.stdout.write('.'); sys.stdout.flush()
    print

def download(url):
    fh = urllib.urlopen(url)
    # read and discard
    for line in fh:
        pass

def print_timestamp(msg=''):
    print '=== %s %s ===' % (msg, datetime.datetime.now())

#
# From dapbench.jython.util with some modifications
#
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
            s = slice(steps[0], shape[0]-1)
        else:
            s = slice(steps[0], steps[1])

        if len(shape) == 1:
            yield [s]
        else:
            for slices in partition_shape(shape[1:], partitions[1:]):
                yield [s] + slices
            
        steps = steps[1:]


                              
def _repr_slice(s):
    def f(v):
        if v is None:
            return ''
        else:
            return str(v)

    p = [f(s.start), f(s.stop)]
    return '[%s]' % ':'.join(p)


if __name__ == '__main__':
    main()

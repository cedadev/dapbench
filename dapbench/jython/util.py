"""
Utilities for running jython performance tests.

"""

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
            s = slice(steps[0], steps[1]-1)

        if len(shape) == 1:
            yield [s]
        else:
            for slices in partition_shape(shape[1:], partitions[1:]):
                yield [s] + slices
            
        steps = steps[1:]


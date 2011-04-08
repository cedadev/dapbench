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
                              

"""
A wrapper around the NetCDF4 Java API

@note: currently read-only

"""

from ucar.na2.dataset import NetcdfDataset

class AttributeDict(object):
    def __init__(self, ref, is_global=True):
        self._ref = ref
        self._is_global = is_global

    def __getitem__(self, key):
        try:
            if self._is_global:
                return self._ref.findGlobalAttribute(key)
            elif:
                return self._ref.findAttribute(key)
        except:
            raise KeyError(key)

    def keys(self):
        if self._is_global:
            return [x.name for x in self.getGlobalAttributes()]
        else:
            return [x.name for x in self.getAttributes()]

    def items(self):
        if self._is_global:
            return [(x.name, x.values) for x in self.getGlobalAttributes()]
        else:
            return [(x.name, x.values) for x in self.getAttributes()]

    def values(self):
        if self._is_global:
            return [x.values for x in self.getGlobalAttributes()]
        else:
            return [x.values for x in self.getAttributes()]


class VariableDict(object):
    def __init__(self, ref):
        self._ref = ref
    
    def __getitem__(self, key):
        try:
            return self._ref.findVariable(key)
        except:
            raise KeyError(key)

    def keys(self):
        return [x.name for x in self.getVariables()]

    def items(self):
        return [(x.name, x) for x in self.getVariables()]

    def values(self):
        return [x for x in self.getVariables()]


class VariableWrapper(object):
    def __init__(self, ref):
        self._ref = ref

    def __getitem__(self, item):
        if type(item) = tuple:
            range_spec = ','.join([spec_to_rangespec(x) for x in item])
        else:
            range_spec = spec_to_rangespec(x)
            
        return self._ref.read(range_spec)

def _slice_to_rangespec(slice):
    parts = [str(x) for x in [s.start or '', s.end or '', s.step or '']]
    while parts[-1] == '':
        parts.pop()
    return ':'.join(parts)

def spec_to_rangespec(spec):
        if type(spec) is slice:
            return _slice_to_rangespec(spec)
        elif type(spec) is int:
            str(spec)
        else:
            raise ValueError("Can't handle item %s" % spec)


class Dataset(object):
    def __init__(self, location):
        self._ds = NetcdfDataset.open(location)
        self.variables = VariableDict(self)
        self.attributes = AttributeDict(self)


"""
A wrapper around the NetCDF4 Java API

@note: currently read-only

"""

from ucar.nc2.dataset import NetcdfDataset
from UserDict import DictMixin

class AttributeDict(DictMixin):
    def __init__(self, ref, is_global=True):
        self._ref = ref
        self._is_global = is_global

    def __getitem__(self, key):
        try:
            if self._is_global:
                return self._ref.findGlobalAttribute(key).values
            else:
                return self._ref.findAttribute(key).values
        except:
            raise KeyError(key)

    def keys(self):
        if self._is_global:
            return [x.name for x in self._ref.getGlobalAttributes()]
        else:
            return [x.name for x in self._ref.getAttributes()]



class VariableDict(DictMixin):
    def __init__(self, ref):
        self._ref = ref
    
    def __getitem__(self, key):
        try:
            return VariableWrapper(self._ref.findVariable(key))
        except:
            raise KeyError(key)

    def keys(self):
        return [x.name for x in self._ref.getVariables()]



class VariableWrapper(object):
    def __init__(self, ref):
        self._ref = ref
        self.attributes = AttributeDict(ref, is_global=False)

    def __getitem__(self, item):
        if type(item) == tuple:
            range_spec = ','.join([spec_to_rangespec(x) for x in item])
        else:
            range_spec = spec_to_rangespec(item)
            
        return self._ref.read(range_spec)

    @property
    def shape(self):
        return tuple(self._ref.shape)

    @property
    def dimensions(self):
        return self._ref.dimensions

    @property
    def name(self):
        return self._ref.name


def _slice_to_rangespec(s):
    #!FIXME: this doesn't interpret slice(x, None, None) right
    if s == slice(None, None, None) or s == slice(0, None, None):
        return ':'
    parts = [str(x) for x in [s.start or '0', s.stop or '', s.step or '']]
    while parts[-1] == '':
        parts.pop()
    return ':'.join(parts)

def spec_to_rangespec(spec):
        if type(spec) is slice:
            return _slice_to_rangespec(spec)
        elif type(spec) is int:
            return str(spec)
        else:
            raise ValueError("Can't handle item %s" % spec)


class Dataset(object):
    def __init__(self, location):
        self._ds = NetcdfDataset.open(location)
        self.variables = VariableDict(self._ds)
        self.attributes = AttributeDict(self._ds)


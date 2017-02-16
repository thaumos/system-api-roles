
import collections

class Bool(object):
    def __init__(self):
        self.default = False

    def __str__(self):
        return 'bool'

    def load(self, value):
        return bool(value)


class Int8(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value >= 0xff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'int8'


class UInt8(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value < 0 or value >= 0xff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'uint8'


class Int16(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value >= 0xffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'int16'


class UInt16(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value < 0 or value >= 0xffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'uint16'


class Int32(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value >= 0xffffffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'int32'


class UInt32(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value < 0 or value >= 0xffffffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'uint32'


class Int64(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value >= 0xffffffffffffffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'int64'


class UInt64(object):
    def __init__(self):
        self.default = 0

    def load(self, value):
        if value < 0 or value >= 0xffffffffffffffff:
            raise ValueError('invalid value %d for varlink type %s' % (value, self))
        return int(value)

    def __str__(self):
        return 'uint64'


class Float32(object):
    def __init__(self):
        self.default = 0.0

    def load(self, value):
        return float(value)

    def __str__(self):
        return 'float32'


class Float64(object):
    def __init__(self):
        self.default = 0.0

    def load(self, value):
        return float(value)

    def __str__(self):
        return 'float64'


class String(object):
    def __init__(self):
        self.default = ''

    def __str__(self):
        return 'string'

    def load(self, value):
        return str(value)


class Struct(object):
    def __init__(self, interface, fields=[]):
        self.interface = interface
        self.fields = collections.OrderedDict(fields)

        self.default = {}
        for name, vtype in self.fields.iteritems():
            self.default[name] = vtype.default

    def add_field(self, name, vtype):
        self.fields[name] = vtype
        self.default[name] = vtype.default

    def __str__(self):
        pairs = [n + ': ' + str(t) for n, t in self.fields.iteritems()]
        return '(' + ', '.join(pairs) + ')'

    def load(self, value):
        if not isinstance(value, dict):
            raise ValueError('cannot create varlink struct from `%s`' % type(value))

        if not set(value).issubset(set(self.fields)):
            extra = set(value).difference(set(self.fields))
            raise ValueError('value contains extraneous fields `%s` for struct %s' % (', '.join(extra), self))

        v = {}
        for name, vtype in self.fields.iteritems():
            v[name] = vtype.load(value[name]) if name in value else vtype.default
        return v


class Array(object):
    def __init__(self, element_type):
        self.element_type = element_type
        self.default = []

    def load(self, value):
        a = []
        try:
            for element in iter(value):
                a.append(self.element_type.load(element))
        except TypeError:
            raise ValueError('cannot create varlink array from `%s`' % type(value))

        return a

    def __str__(self):
        return str(self.element_type) + '[]'


class Nullable(object):
    def __init__(self, subtype):
        self.subtype = subtype
        self.default = None

    def __str__(self):
        return str(self.subtype) + '?'

    def load(self, value):
        if value is not None:
            return self.subtype.load(value)


class CustomType(object):
    def __init__(self, interface, name):
        self.name = name
        if not interface:
            raise TypeError('cannot resolve custom type without an interface')
        self.subtype = interface.get_type(name)
        if not self.subtype:
            raise TypeError('interface %s does not have a type `%s`' % (interface.name, name))

        self.default = self.subtype.default

    def __str__(self):
        return self.name

    def load(self, value):
        return self.subtype.load(value)

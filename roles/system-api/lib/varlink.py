
import re
import collections

__all__ = [ 'Variant', 'Interface' ]

whitespace = re.compile(r'[ \n\t]+')
comment_start = re.compile(r'/\*')
comment_end = re.compile(r'\*/')
interface_name = re.compile(r'[a-z0-9]+(\.[a-z0-9][a-z0-9-]*)+')
type_keyword = re.compile(r'\btype\b')
basic_type = re.compile(r'\bbool|u?int8|u?int16|u?int32|u?int64|float32|float64|string\b')
custom_type = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')
field_name = re.compile(r'\b[a-z][a-z0-9_]*\b')

class Scanner:
    def __init__(self, string):
        self.string = string
        self.pos = 0

    def source_position(self):
        line = len(re.compile(r'\n').findall(self.string[:self.pos])) + 1
        lastnl = self.string.rfind('\n', 0, self.pos)
        column = self.pos - lastnl
        return line, column

    def skip_whitespace(self):
        m = whitespace.match(self.string, self.pos)
        if m:
            self.pos = m.end()

        m = comment_start.match(self.string, self.pos)
        if m:
            end = comment_end.search(self.string, self.pos)
            if not end:
                raise SyntaxError('unclosed comment at %i:%i' % self.source_position())
            self.pos = end.end()
            return self.skip_whitespace()

    def get(self, expected):
        if self.pos >= len(self.string):
            return

        self.skip_whitespace()

        if type(expected) == str:
            if self.string.startswith(expected, self.pos):
                self.pos += len(expected)
                return expected
        else:
            m = expected.match(self.string, self.pos)
            if m:
                self.pos = m.end()
                return m.group(0)

    def get_one_of(self, **expecteds):
        for token, expected in expecteds.items():
            value = self.get(expected)
            if value:
                return token, value
        raise SyntaxError('unexpected token at %i:%i' % self.source_position())

    def expect(self, expected):
        value = self.get(expected)
        if not value:
            raise SyntaxError('unexpected token at %i:%i' % self.source_position())
        return value

    def at_end(self):
        self.skip_whitespace()
        return self.pos >= len(self.string)


class Type:
    def __init__(self, interface, kind, *args):
        self.interface = interface
        self.kind = kind
        self.nullable = False

        if kind == 'struct':
            self.fields = args[0]
        elif kind == 'array':
            self.element_type = args[0]

    def resolve(self):
        if not self.kind[0].isupper():
            return self
        return self.interface.types.get(self.kind).resolve()

    def __str__(self):
        if self.kind == 'struct':
            pairs = ['%s: %s' % (n, str(t)) for n, t in self.fields.iteritems()]
            r = '(' + ', '.join(pairs) + ')'
        elif self.kind == 'array':
            r = str(self.element_type) + '[]'
        else:
            r = self.kind
        if self.nullable:
            r += '?'
        return r

    def __repr__(self):
        return str(self)


def parse_type(scanner, interface=None):
    token, value = scanner.get_one_of(struct='(', basic=basic_type, custom=custom_type)
    t = None
    if token == 'struct':
        fields = collections.OrderedDict()
        while not scanner.get(')'):
            if len(fields) > 0:
                scanner.expect(',')
            name = scanner.expect(field_name)
            scanner.expect(':')
            fields[name] = parse_type(scanner, interface)
        t = Type(interface, 'struct', fields)
    elif token == 'basic':
        t = Type(interface, value)
    elif token == 'custom':
        if not interface or value not in interface.types:
            raise ValueError('no such type: %s' % value)
        t = Type(interface, value)

    t.nullable = scanner.get('?') == '?'

    if scanner.get('['):
        scanner.expect(']')
        t = Type(interface, 'array', t)
        t.nullable = scanner.get('?') == '?'

    return t


class Interface:
    def __init__(self, description):
        self.methods = collections.OrderedDict()
        self.types = collections.OrderedDict()

        self._parse(description)

    def _parse(self, description):
        scanner = Scanner(description)

        self.name = scanner.expect(interface_name)
        scanner.expect('{')

        while not scanner.get('}'):
            if scanner.get(type_keyword):
                name = scanner.expect(custom_type)
                self.types[name] = parse_type(scanner, self)
            else:
                name = scanner.expect(custom_type)
                in_args = parse_type(scanner, self)
                scanner.expect('->')
                out_args = parse_type(scanner, self)
                self.methods[name] = (in_args, out_args)

        if not scanner.at_end():
            raise SyntaxError('trailing tokens')

def default_value(t):
    if t.nullable:
        return None
    if t.kind == 'bool':
        return False
    elif t.kind == 'string':
        return ''
    elif t.kind in ('int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64'):
        return 0
    elif t.kind in ('float32', 'float64'):
        return 0.0
    elif t.kind == 'array':
        return []
    elif t.kind == 'struct':
        return {}


class Variant:
    def __init__(self, interface, typestring, value):
        self.interface = interface
        scanner = Scanner(typestring)
        self.type = parse_type(scanner, interface)

        t = self.type.resolve()
        if (self.type.nullable or t.nullable) and value == None:
            self.value = None
        elif t.kind == 'bool':
            self.value = bool(value)
        elif t.kind == 'string':
            self.value = str(value)
        elif t.kind in ('int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64'):
            self.value = int(value)
        elif t.kind in ('float32', 'float64'):
            self.value = float(value)
        elif t.kind == 'array':
            self.value = [Variant(interface, str(t.element_type), element) for element in value]
        elif t.kind == 'struct':
            self.value = {}
            for field_name, field_value in value.iteritems():
                field_type = t.fields[field_name]
                self.value[field_name] = Variant(interface, str(field_type), field_value)

            for field_name, field_type in t.fields.iteritems():
                if field_name not in self.value:
                    self.value[field_name] = Variant(interface, str(field_type), default_value(field_type))

    def to_value(self):
        """converts this variant to a plain python value"""

        t = self.type.resolve()
        if (self.type.nullable or t.nullable) and self.value == None:
            return None
        elif t.kind == 'array':
            return [v.to_value() for v in self.value]
        elif t.kind == 'struct':
            return dict([(n, v.to_value()) for n, v in self.value.iteritems()])
        else:
            return self.value


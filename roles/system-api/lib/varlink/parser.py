
import re
from types import *
from interface import Interface


_tokens = [
    (None,             re.compile(r'[ \n\t]')),
    (None,             re.compile(r'\/\*(.|\n)*?\*\/')),
    ('',               re.compile(r'\btype\b')),
    ('basic-type',     re.compile(r'\bbool|u?int8|u?int16|u?int32|u?int64|float32|float64|string\b')),
    ('bool',           re.compile(r'\btrue|false\b')),
    ('',               re.compile(r'\bnull\b')),
    ('interface-name', re.compile(r'[a-z]+(\.[a-z0-9][a-z0-9-]*)+')),
    ('field-name',     re.compile(r'\b[a-z][a-z0-9_]*\b')),
    ('custom-type',    re.compile(r'\b[A-Z][A-Za-z0-9]*\b')),
    ('number',         re.compile(r'-?\d+(\.\d*)?(e\d+)?')),
    ('string',         re.compile(r'"[^\"]*"')),
    ('',               re.compile(r'[:,(){}\[\]?=]|->'))
]


basic_types = {
    'bool': Bool,
    'int8': Int8,
    'uint8': UInt8,
    'int16': Int16,
    'uint16': UInt16,
    'int32': Int32,
    'uint32': UInt32,
    'int64': Int64,
    'uint64': UInt64,
    'float32': Float32,
    'float64': Float64,
    'string': String
}


def _tokenize(string):
    pos = 0
    while pos < len(string):
        for tag, rx in _tokens:
            m = rx.match(string, pos)
            if m:
                if tag == '':
                    yield (m.group(0), None)
                elif tag is not None:
                    yield (tag, m.group(0))
                pos = m.end()
                break
        else:
            raise ValueError('invalid character: \'%s\'' % string[pos])

    while True:
        yield ('eof', None)


class Scanner(object):
    def __init__(self, string):
        self.tokens = _tokenize(string)
        self.token = next(self.tokens)

    def get(self, expected_tag=None):
        tag, value = self.token
        if tag == expected_tag or not expected_tag:
            self.token = next(self.tokens)
            return value or tag

    def expect(self, tag):
        value = self.get(tag)
        if not value:
            raise SyntaxError('expected %s, but got %s' % (tag, self.token[0]))
        return value


def _read_basic_type(scanner):
    kind = scanner.get('basic-type')
    if kind:
        return basic_types[kind]()


def _read_custom_type(scanner, interface):
    name = scanner.get('custom-type')
    if name:
        return CustomType(interface, name)


def _read_struct(scanner, interface):
    if scanner.get('('):
        struct = Struct(interface)
        if not scanner.get(')'):
            while True:
                field_name = scanner.expect('field-name')
                scanner.expect(':')
                field_type = _read_type(scanner, interface)
                if not field_type:
                    raise SyntaxError('expected type')
                struct.add_field(field_name, field_type)
                if not scanner.get(','):
                    break
            scanner.expect(')')
        return struct


def _expect_value(scanner, vtype):
    v = scanner.get('bool')
    if v:
        return vtype.load(v == 'true')

    v = scanner.get('null')
    if v:
        return vtype.load(None)

    v = scanner.get('number')
    if v:
        try:
            n = int(v)
        except ValueError:
            n = float(v)
        return vtype.load(n)

    v = scanner.get('string')
    if v:
        return vtype.load(v[1:-1])

    raise SyntaxError('expected value')


def _read_type(scanner, interface):
    t = _read_basic_type(scanner) or \
        _read_custom_type(scanner, interface) or \
        _read_struct(scanner, interface)

    if not t:
        return

    if scanner.get('?'):
        t = Nullable(t)

    if scanner.get('['):
        scanner.expect(']')
        t = Array(t)
        if scanner.get('?'):
            t = Nullable(t)

    if scanner.get('='):
        t.default = _expect_value(scanner, t)

    return t


def _read_interface(scanner):
    name = scanner.expect('interface-name')
    interface = Interface(name)
    scanner.expect('{')
    while not scanner.get('}'):
        if scanner.get('type'):
            name = scanner.expect('custom-type')
            t = _read_type(scanner, interface)
            interface.add_type(name, t)
        else:
            name = scanner.expect('custom-type')
            in_args = _read_struct(scanner, interface)
            scanner.expect('->')
            out_args = _read_struct(scanner, interface)
            interface.add_method(name, in_args, out_args)
    return interface


def read_type(typestring, interface=None):
    scanner = Scanner(typestring)
    return _read_type(scanner, interface)


def read_interface(description):
    scanner = Scanner(description)
    return _read_interface(scanner)


import collections


class Interface(object):
    def __init__(self, name):
        self.name = name
        self._types = collections.OrderedDict()
        self._methods = collections.OrderedDict()

    def types(self):
        return dict(self._types)

    def get_type(self, name):
        return self._types.get(name)

    def methods(self):
        return dict(self._methods)

    def get_method(self, name):
        return self._methods.get(name)

    def add_type(self, name, vtype):
        self._types[name] = vtype

    def add_method(self, name, in_args, out_args):
        self._methods[name] = (in_args, out_args)

    def __str__(self):
        types = ''.join(['type %s %s\n' % (n, str(t)) for n, t in self._types.iteritems()])
        methods = ''
        return self.name + ' {\n' + types + methods + '}'

    def __getattr__(self, key):
        attr = self._types.get(key) or self._methods.get(key)
        if not attr:
            raise AttributeError('%s does not have a type or method named `%s`' % (self.name, key))
        return attr

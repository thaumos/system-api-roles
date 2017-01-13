#!/usr/bin/python

from __future__ import absolute_import, division, print_function

# HACK: add import path for libraries shipped with this role
import sys, os
path = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.insert(0, os.path.normpath(path))

from ansible.plugins.action import ActionBase
import json
import varlink

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        interface_name = self._task.args.get('interface')
        if not interface_name:
            return dict(failed=True, msg='need "interface" task var')

        varlink_file = 'api/%s.api' % interface_name
        try:
            description = file(varlink_file).read()
            interface = varlink.Interface(description)
        except (ValueError, IOError) as error:
            return dict(failed=True, msg='cannot read interface file `%s`: %s' % (varlink_file, error.strerror))

        defaults_file = 'api/%s.defaults' % interface_name
        try:
            config = json.load(file(defaults_file))
        except (ValueError, IOError) as error:
            return dict(failed=True, msg='cannot read defaults from `%s`: %s' % (defaults_file, str(error)))

        config.update(task_vars.get(interface_name.replace('.', '_'), {}))

        try:
            variant = varlink.Variant(interface, 'Config', config)
        except ValueError as error:
            return dict(failed=True, msg=str(error))

        return variant.to_value()

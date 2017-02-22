#!/usr/bin/python

from __future__ import absolute_import, division, print_function

# HACK: add import path for libraries shipped with this role
import sys, os
path = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.insert(0, os.path.normpath(path))

from ansible.plugins.action import ActionBase
import os
import json
import varlink

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        interface_name = self._task.args.get('interface')
        if not interface_name:
            return dict(failed=True, msg='need "interface" task var')

        varlink_file = os.path.join(self._task._role._role_path, 'api/%s.api' % interface_name)
        try:
            description = file(varlink_file).read()
            interface = varlink.interface(description)
        except (ValueError, IOError) as error:
            return dict(failed=True, msg='cannot read interface file `%s`: %s' % (varlink_file, error.strerror))

        config_type = interface.get_type('Config')
        if not config_type:
            return dict(failed=True, msg='interface `%s` does not contain a type named `Config`' % interface_name)

        config = {}
        for name in config_type.fields.keys():
            value = task_vars.get(name)
            if value is not None:
                config[name] = value

        try:
            x = varlink.load(config_type, config)
            return x
        except ValueError as error:
            return dict(failed=True, msg=str(error))

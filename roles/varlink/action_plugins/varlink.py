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

        facts = {}

        for name in task_vars.get('interfaces', []):
            varname = name.replace('.', '_')

            varlink_file = 'varlink/%s.api' % name
            try:
                description = file(varlink_file).read()
                interface = varlink.Interface(description)
            except (ValueError, IOError) as error:
                return dict(failed=True, msg='cannot read interface file `%s`: %s' % (varlink_file, error.strerror))

            defaults_file = 'varlink/%s.defaults' % name
            try:
                config = json.load(file(defaults_file))
            except (ValueError, IOError) as error:
                return dict(failed=True, msg='cannot read defaults from `%s`: %s' % (defaults_file, str(error)))

            config.update(task_vars.get(varname, {}))

            try:
                variant = varlink.Variant(interface, 'Config', config)
            except ValueError as error:
                return dict(failed=True, msg=str(error))

            facts[varname] = variant.to_value()

        return dict(changed=True, ansible_facts=facts)

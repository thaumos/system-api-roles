
import machine
import os
import re


class TestDefaults(machine.Test):

    """
    Basic sanity check. Set default values for all known interfaces on the same
    machine.

    :avocado: enable
    """

    def interfaces(self):
        """
        Returns a generator that produces all known interfaces in this
        repository. Only roles that have reverse domain names are looked at.
        """
        rdn = re.compile('(com|org)_[^_]+_.+')
        for directory in os.listdir(os.path.join(self.basedir, '..', 'roles')):
            if rdn.match(directory):
                yield directory.replace('_', '.')

    def test(self):
        for interface in self.interfaces():
            self.machine.set_config(interface)

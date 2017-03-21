
import machine
import re
from avocado.utils import process


class TestTuned(machine.Test):

    """
    :avocado: enable
    """

    # reverse from the one in defaults/main.yaml
    legacy_profiles_map = { 'default': 'balanced', 'server-powersave': 'powersave'}

    def test(self):
        # run the playbook once with defaults to ensure that tuned is installed
        self.machine.set_config('com.redhat.tuned')

        # check if we're running on an old version of tuned, which doesn't accept --version
        try:
            self.machine.execute('sudo tuned-adm --version')
        except process.CmdError:
            self.legacy = True
        else:
            self.legacy = False

        # the default profile is 'balanced'
        self.assertEqual(self.get_active_profile(), 'balanced')

        for profile in ('balanced', 'powersave', 'throughput-performance', 'latency-performance'):
            self.machine.set_config('com.redhat.tuned', profile=profile)
            self.assertEqual(profile, self.get_active_profile())

        if not self.legacy:
            recommended = self.machine.execute('sudo tuned-adm recommend').strip()
        else:
            # legacy tuned doesn't have the notion of a recommended profile,
            # but should use 'default' (which maps to 'balanced')
            recommended = 'balanced'

        self.machine.set_config('com.redhat.tuned', use_recommended_profile=True)
        self.assertEqual(recommended, self.get_active_profile())

    def get_active_profile(self):
        output = self.machine.execute('sudo tuned-adm active')
        profile = re.match('^.*: (.*)$', output, re.MULTILINE).group(1)

        if self.legacy:
            return self.legacy_profiles_map.get(profile, profile)
        else:
            return profile

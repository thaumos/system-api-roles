
import machine
import re


class TestTuned(machine.Test):

    """
    :avocado: enable
    """

    def test(self):
        for profile in ('balanced', 'powersave', 'throughput-performance', 'latency-performance'):
            self.machine.set_config('com.redhat.tuned', profile=profile)
            self.assertEqual(profile, self.get_active_profile())

        recommended = self.machine.execute('sudo tuned-adm recommend').strip()
        self.machine.set_config('com.redhat.tuned', use_recommended_profile=True)
        self.assertEqual(recommended, self.get_active_profile())

    def get_active_profile(self):
        output = self.machine.execute('sudo tuned-adm active')
        return re.match('^.*: (.*)$', output).group(1)


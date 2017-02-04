#!/usr/bin/python2

from __future__ import absolute_import, division, print_function

import os
import subprocess
import time
import avocado
import yaml
import re
import tempfile
import logging


class Machine:
    def __init__(self, image, workdir, rolesdir):
        self.image = image
        self.workdir = workdir
        self.rolesdir = rolesdir

        self.identity = os.path.join(self.workdir, 'id_rsa')
        avocado.utils.process.run('ssh-keygen -q -f "%s" -N ""' % self.identity)

        with open(os.path.join(self.workdir, 'meta-data'), 'w') as f:
            f.write('instance-id: nocloud\n')
            f.write('local-hostname: system-api-test\n')

        with open(os.path.join(self.workdir, 'user-data'), 'w') as f:
            f.write('#cloud-config\n')
            f.write('user: admin\n')
            f.write('password: foobar\n')
            f.write('ssh_pwauth: True\n')
            f.write('chpasswd:\n')
            f.write('  expire: False\n')
            f.write('ssh_authorized_keys:\n')
            f.write('  - ' + open(self.identity + '.pub', 'r').read())

        cloudinit_iso = os.path.join(workdir, 'cloud-init.iso')
        argv = ['genisoimage',
                '-input-charset', 'utf-8',
                '-output', cloudinit_iso,
                '-volid', 'cidata',
                '-joliet', '-rock', '-quiet',
                os.path.join(workdir, 'user-data'),
                os.path.join(workdir, 'meta-data')]
        avocado.utils.process.run(' '.join(argv))

        argv = ['qemu-system-x86_64',
                '-m', '1024',
                self.image,
                '-snapshot',
                '-cdrom', cloudinit_iso,
                '-net', 'nic,model=virtio',
                '-net', 'user,hostfwd=tcp::2222-:22',
                '-display', 'none']
        if os.access('/dev/kvm', os.W_OK):
            argv.append('-enable-kvm')

        logging.info('Running %s', ' '.join(argv))
        self.qemu = subprocess.Popen(argv)

        # wait for ssh to come up
        for _ in range(10):
            r = self.execute('/bin/true', timeout=60)
            if r.exit_status == 0:
                break
            else:
                time.sleep(3)
        else:
            self.terminate()
            raise Exception('error connecting to the machine')

        # write an ansible inventory file for this host
        self.inventory_file = os.path.join(workdir, 'inventory')
        host = ('system-api-test'
                ' ansible_host=localhost'
                ' ansible_port=2222'
                ' ansible_user=admin'
                ' ansible_ssh_private_key_file="%s"'
                ' ansible_ssh_extra_args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"'
                % self.identity)
        with open(self.inventory_file, 'w') as f:
            f.write(host)

    def execute(self, command, timeout=None):
        argv = ['ssh',
                '-o', 'IdentityFile=' + self.identity,
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'PasswordAuthentication=no',
                 'admin@localhost', '-p', '2222', command]

        return avocado.utils.process.run(' '.join(argv), ignore_status=True, timeout=timeout)

    def terminate(self):
        self.qemu.terminate()
        self.qemu.wait()

    def set_config(self, interface, **config):
        play = {
                'hosts': 'system-api-test',
                'become': True,
                'roles': [ dict(role=interface.replace('.', '_'), **config) ]
        }
        playbook = [ play ]

        playbook_file = os.path.join(self.workdir, 'test.yml')
        with open(playbook_file, 'w') as f:
            f.write(yaml.dump(playbook))

        env = dict(ANSIBLE_ROLES_PATH=self.rolesdir, **os.environ)
        cmd = 'ansible-playbook -vvv -i %s %s' % (self.inventory_file, playbook_file)

        result = avocado.utils.process.run(cmd, env=env, ignore_status=True)
        if result.exit_status != 0:
            raise AssertionError('error setting configuration')


class Test(avocado.Test):

    """
    Base class for integration tests.

    Subclasses must include `:avocado: enable` in their docstring.
    """

    def setUp(self):
        image = self.fetch_asset(self.params.get('source'))
        self.machine = Machine(image,
                               workdir=tempfile.mkdtemp(dir=self.workdir),
                               rolesdir=os.path.join(self.basedir, '..', 'roles'))

        setup = self.params.get('setup')
        if setup:
            self.machine.execute(setup)

    def tearDown(self):
        self.machine.terminate()

    def assertOutput(self, command, expected):
        """
        Run 'command' on the vm and assert that the command's output matches
        the regular expression in 'expected'.
        """

        result = self.machine.execute(command)

        if result.exit_status != 0:
            raise AssertionError(str(result))

        if not re.match(expected + '$', result.stdout):
            raise AssertionError('output "%s" does not match expectation "%s"' % (result.stdout, expected))


import avocado
import machine
import os
import tempfile

class Test(avocado.Test):
    def setUp(self):
        workdir = tempfile.mkdtemp(dir=self.workdir)
        rolesdir = os.path.join(self.basedir, '..', 'roles')
        if self.params.get('source', path='/run/image/*'):
            self.setUpMux(workdir, rolesdir)
        else:
            self.setUpLocal(workdir, rolesdir)

    def tearDown(self):
        if self.params.get('source', path='/run/image/*'):
            self.tearDownMux()
        else:
            self.tearDownLocal()

    def setUpMux(self, workdir, rolesdir):
        image = self.fetch_asset(self.params.get('source', path='/run/image/*'))
        self.machine = machine.Virtualhost(image, workdir=workdir, rolesdir=rolesdir)

        setup = self.params.get('setup', path='/run/image/*')
        if setup:
            self.machine.execute(setup)

    def tearDownMux(self):
        self.machine.terminate()

    def setUpLocal(self, workdir, rolesdir):
        self.machine = machine.Localhost(workdir, rolesdir)

    def tearDownLocal(self):
        pass

    def test(self):
        role = self.params.get('name', path='/run/role/*')

        testpath = os.path.join(self.machine.rolesdir, role, 'test')
        if not os.path.isdir(testpath):
            return

        for fn in os.listdir(testpath):
            if fn.endswith('.yml'):
                self.machine.run_playbook(os.path.join(testpath, fn))

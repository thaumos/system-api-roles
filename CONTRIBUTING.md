# Contributing to these roles

Each subsystem role should follow the file and directory layout as described in the
[Playbooks Best Practices guide](http://docs.ansible.com/ansible/playbooks_best_practices.html#content-organization), as well as including an `example-playbook.yml` file in the top level directory that demonstrates its usage.

New roles should have an API described in the Varlink format and placed in the ```api/``` directory.

All changes should be tested via the tests found in the ```test/``` directory.
A pull request should contain appropriate changes to the tests to ensure that the
change works as expected.

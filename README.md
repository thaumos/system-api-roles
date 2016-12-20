poc-sysmgmt-roles
=================

_WARNING: These roles can be dangerous to use. They are experimental, proof of concepts that may or may not reach a usable state in the future._

Overview
--------

A collection of modules and supporting roles to configure common system subsystems utilizing the subsystems APIs whenever possible rather than common CLI tools.  This should allow improved performance, error handling, and consistency across future releases.

Each subsystem role follow the file and directory layout best practices as described at <http://docs.ansible.com/ansible/playbooks_best_practices.html>, as well as including an `example-plbk.yml` file in the top level directory that demonstrates its usage.

Current subsystems
------------------

- Networking
- Timesync

Future subsystems
-----------------
- Storage
- SELinux
- Firewall
- Kernel crash dump
- DNS
- SystemLog
- Registration
- more...


# poc-sysmgmt-roles

_WARNING: These roles can be dangerous to use. They are experimental, proof of concepts that may or may not reach a usable state in the future._

## Overview

A collection of modules and supporting roles to configure common system subsystems utilizing the subsystems APIs whenever possible rather than common CLI tools.  This should allow improved performance, error handling, and consistency across future releases.

Each subsystem role should follow the file and directory layout as described in the [Playbooks Best Practices guide](http://docs.ansible.com/ansible/playbooks_best_practices.html#content-organization), as well as including an `example-plbk.yml` file in the top level directory that demonstrates its usage.

## Current subsystems
- Kernel crash dump
- Networking
- Red Hat Subscription Manager
- SELinux
- Timesync

## Future subsystems
- DNS
- Firewall
- Storage
- SystemLog
- more to come...

## Usage

## Configuration
Current testing and development is primarily on RHEL/CentOS/Fedora applying the playbooks against KVM virtual machines.

### Vagrant

You can use [vagrant](http://vagrantup.com) to quickly test the example playbooks. The Vagrantfile in this repository defines [multiple machines](https://www.vagrantup.com/docs/multi-machine/) (for now `fedora` and `centos`) and runs all `vagrant` commands on all of them by default. To only run one machine, use

```shell
vagrant up MACHINE
```

None of the playbooks are run when creating and starting the VM with `vagrant up`. Instead, you can run then manually with

```shell
vagrant provision [MACHINE] --provision-with NAME
```

Where `NAME` is one of `selinux`, `kdump`, `system-api`, etc.

### Roles as System API

The System API is a generic way to configure a system according to formally defined API.
Various roles contribute toward the implementation of that API. The API is formally
described in the ```api/``` directory and an ```example-system-api.yml``` playbook example
that calls it.

### vault.yml
If using the optional Red Hat Subscription Manager example role, you will probably want to securely store your credentials in an encrypted [ansible vault](http://docs.ansible.com/ansible/playbooks_vault.html) file.  Currently this is the only role/module for this project that requires sensitive information.  It will need to include the following:

* rhn_username: your RHN user account
* rhn_password: your RHN password
* POOL_ID: your paid entitlement Pool ID to access content from Red Hat Subscription Manager

## Playbooks and SubSystem Roles and/or modules

### example-subscribe-plybk.yml
This is an example playbook using the redhat_subscription Ansible Core module (Preview status). This will register a guest, attach the entitlement, and enable the common server channels to install packages.  Note:  This calls `verify_supported_platform` to fail if not RHEL 6.4 or later in order to meet the scope of this Proof of Concept project.  It does all this using an intermediary role called `common_RHSM` to simplify the process and auto-define appropriate repository channels based on the major release.  This will most certainly be refined and possibly renamed or merged into something else.

### example-verify-supported-platform-plybk.yml
This role can be used by other roles using the `include_role` directive to help ensure that the minimum supported platform requirements are met.  It is really nothing more than a predefined set of conditional tasks.

### Kernel Crash Dump
This role is explained in [README-kdump.md](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/README-kdump.md) and demonstrated in [example-plbk-kdump.yml](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/example-plbk-kdump.yml).

### Networking
This module and role has not yet been merged into this repository and can instead be found at <https://github.com/NetworkManager/ansible-network-role>.

### Email: postfix
This role is explained in this [README.me](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/roles/postfix/README.md) which includes an example playbook.

### SELinux
This role is explained in [README.SELinux.adoc](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/README-SELinux.adoc) and demonstrated in [example-SELinux.yml](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/example-SELinux.yml) playbook.

### Storage
Example playbook [example-storage.yml](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/example-storage.yml) is provided which demonstrates basic storage configuration using the existing roles & modules already provided by Ansible.
This will provision LVM, filesystem, mount and user ownership of disks.  Modules used include:

- user
- lvg
- lvol
- filesystem
- file
- mount

### Timesync
This role is explained in this [README.md](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/roles/timesync/README.md) which includes example playbooks.

### tuned
This role is explained in this [README.md](https://github.com/cockpit-project/poc-sysmgmt-roles/blob/master/roles/tuned/README.md) which includes an example playbook.

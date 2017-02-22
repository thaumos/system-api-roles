
# Ansible Role: System API

Ansible role which provides the `varlink` module to roles that implement a [System API](https://github.com/cockpit-project/poc-sysmgmt-roles/wiki/System-Service-Configuration-API).

To use it, place an `.api` file into the `api/` directory of your role. This file should contain a `Config` type, which describes all configuration values of your service. Depend on the `system-api` role by adding it to `meta/main.yml`:

```yaml
dependencies:
  - system-api
```

To use it, gather configuration from default values and variables passed to your role, like this:

```yaml
- name: Gather config
  action: varlink interface=com.example.service
  register: config
```

You can then use the `config` variable, which is guaranteed to include all variables that are defined in your `.api` file.

# Role Variables

The only mandatory variable is `interface`, which should point to the interface

# License

MIT

This role includes [python-varlink](https://github.com/varlink/python-varlink), which is licensed under Apache 2.0.

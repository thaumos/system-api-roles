tuned
=====

Currently two non-compatible versions of Tuned exists - Tuned (RHEL-7+) and
Tuned legacy (RHEL-6).

This role can install, configure (only non-legacy Tuned), and start Tuned
daemon. It can also activate arbitrary Tuned profile or activate Tuned profile
which is recommended for the machine / product (the latter is supported only on
non-legacy Tuned). It can also deploy custom Tuned / Tuned legacy profiles.


Basic Tuned Profiles
--------------------

Following basic Tuned profiles are known to this role.

###balanced
General non-specialized Tuned profile balancing performance / power
consumption / latency.

###powersave
Tuned profile optimized for low power consumption.

###throughput-performance
Tuned profile with broadly applicable tuning providing excellent performance
across a variety of common server workloads.

###latency-performance
Tuned profile optimizing for low latency at the cost of increased power
consumption.


Additional Tuned Profiles
-------------------------

There may be more Tuned profiles available depending on OS version / product,
Tuned version, additional Tuned packages installed or third party Tuned
packages installed. Packages providing additional Tuned profiles are usually
prefixed by 'tuned-profiles-', e.g. 'tuned-profiles-oracle'. For list of all
installed Tuned profiles on the system see Role Facts bellow.


Role Variables
--------------

For list of supported role variables together with the description and preset
default values see:

./defaults/main.yml


Role Facts
----------

This role sets the following facts:

### tuned_legacy
True if there is Tuned legacy, false otherwise.

### tuned_recommended_profile
Name of the Tuned profile which is recommended as a default for the
machine / product. This is not supported on Tuned legacy, it's
set there to the empty string.

### tuned_available_profiles
List of Tuned profiles which are available (installed) on the machine.


Example Playbooks
-----------------

Install, configure, and enable Tuned. Change the default Tuned configuration
to enable dynamic tuning (non-legacy Tuned only). Also set profile which is
recommended for the machine / product where supported, otherwise set
throughput-performance profile (i.e. on Tuned legacy):

```
---
- hosts: all
  vars:
    tuned_set_recommended_profile: true
    tuned_profile: throughput-performance
    generate_tuned_main_conf: true
    tuned_main_conf_dynamic_tuning: "1"
  roles:
    - tuned
```

Install and enable Tuned. Use the default configuration (which is usually
good), set balanced Tuned profile and with Tuned legacy the profile which is
the most similar to the balanced (if there is known map):

```
---
- hosts: all
  vars:
    tuned_profile: balanced
  roles:
    - tuned
```

Install and enable Tuned. Set powersave profile on Tuned and
desktop-powersave profile on Tuned legacy (without
tuned_legacy_profile it would map to server-powersave profile
on Tuned legacy by default):

```
---
- hosts: all
  vars:
    tuned_profile: powersave
    tuned_legacy_profile: desktop-powersave
  roles:
    - tuned
```

Install and enable Tuned. Deploy custom Tuned profiles and activate profile
named 'myprofile1'. The Tuned profile 'myprofile1' has to be available under
../files/tuned (for Tuned) and ../files/tuned_legacy (for Tuned legacy):

```
---
- hosts: all
  vars:
    tuned_profile: myprofile1
    deploy_tuned_profiles: true
  roles:
    - tuned
```

Install and enable Tuned. Deploy custom Tuned profiles with Tuned and activate
profile named 'myprofile1'. With Tuned legacy do not deploy custom profiles
and do not change active profile. The Tuned profile 'myprofile1' has to be
available under ../files/tuned, the directory ../files/tuned_legacy has to
be empty:

```
---
- hosts: all
  vars:
    tuned_profile: myprofile1
    tuned_legacy_profile: ""
    deploy_tuned_profiles: true
  roles:
    - tuned
```


License
-------

Copyright (C) 2017 Jaroslav Škarvada <jskarvad@redhat.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

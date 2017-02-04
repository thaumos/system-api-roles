
Integration Tests
=================

This directory contains integration tests for the system api ansible roles.
Tests are written against the [avocado](http://avocado-framework.github.io/)
test framework.

Each test spins up a virtual machine based on cloud images of various operating
systems. Machines are defined in `images.yaml`, which has to be passed to
avocado along with the test name.

Tests are run in a docker container. To run them, execute

    $ sudo make check

Test images are stored in `test/.image-cache`. This path can be overriden by
setting `CACHEDIR` when invoking `make`.

To run tests manually, drop into the test container with

    $ sudo make test-shell

and run avocado like this:

    $ avocado run test -m images.yaml

To only run tests against a single image, use avocado's parameter filtering
mechanism:

    $ avocado run test -m images.yaml --filter-only /run/centos-7

To run a single test, replace the `test` by the test program you want to run.

To build the test container itself, run

    $ sudo make test-container

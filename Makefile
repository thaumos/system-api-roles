
CACHEDIR=$(shell pwd)/test/.image-cache

all:
	@printf "usage:\tmake check\n\
\tmake local-check\n\
\tmake test-shell\n\
\tmake test-container\n" >&2

test-container:
	docker build --tag cockpit/system-api-test test

test-shell:
	docker run --tty \
		   --interactive \
		   --rm \
		   --privileged \
		   --volume $(shell pwd):/system-api-test:ro \
		   --volume $(CACHEDIR):/cache \
		   cockpit/system-api-test \
		   /bin/bash

check:
	docker run --privileged \
		   --rm \
		   --volume $(shell pwd):/system-api-test \
		   --volume $(CACHEDIR):/cache \
		   cockpit/system-api-test

check-local:
	avocado run test/test-*.py --show-job-log

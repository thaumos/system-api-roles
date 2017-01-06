#!/bin/sh

. /etc/tune-profiles/functions

start() {
	set_cpu_governor ondemand

	return 0
}

stop() {
	restore_cpu_governor

	return 0
}

process $@

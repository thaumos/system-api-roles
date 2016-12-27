This playbook role for Kernel-Crash-Dump (kdump for shoft) is a draft
built for automation config.

The service operation part is very simple, just enable/disable/restart.
Only template for kdump.conf is a little complicated since its dumping
target type is exclusive. E.g currently file type plus storage device,
ssh dumping and nfs dumping are support. Only one of them can be chosen
and set.

And during testing I created two kvm guests:
master (system ansible playbook is played on):
192.168.124.254

slave (system controled by master):
192.168.124.214

ssh server:
192.168.124.1

Only one thing need be noticed that ssh dumping need put ssh private/public
key file separately to ssh server and ssh client. This has better be done
beforehand, it's not suggested to do in kdump, I personally think. Just
in test I did it in kdump ansible code. And the ssh dump target setting for
testing has been commented out, user can change according to their configuration.

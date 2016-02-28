#!/usr/bin/env python
#
# Multi-SSH Tail Demo
#
# Written by Fotis Gimian
# http://github.com/fgimian
#
# This script demonstrates the MultiSSHRunner class in the multi-ssh library
# tailing a file on multiple servers
#
import traceback
import paramikoe
from multissh import MultiSSHRunner


def tail_authlog(client, hostname):
    """The tail interaction function"""
    prompt = 'fots@fotsies-ubuntu-testlab:~\$ '
    line_prefix = hostname + ': '

    # Start a client interaction using the paramiko-expect class
    interact = paramikoe.SSHClientInteraction(client, display=False)
    interact.expect(prompt)

    # Begin tailing the file
    interact.send('tail -f /var/log/auth.log')
    interact.tail(line_prefix=line_prefix)


def main():
    # Set login credentials and the command to run
    connect_timeout = 30
    devices = ['server1', 'server2', 'server3']
    username = 'fots'
    password = 'password'

    try:
        # Create a multi-SSH runner.  Processes sets the number of processes
        # that can run at the same time.
        runner = MultiSSHRunner(processes=len(devices))

        # We must add jobs one at a time (allows for more flexibility)
        for device in devices:
            runner.add_ssh_job(
                hostname=device, connect_timeout=connect_timeout,
                username=username, password=password, interaction=tail_authlog)

        # Run the tail interactions
        runner.run()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()

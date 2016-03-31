#!/usr/bin/env python
#
# Multi-SSH Interact Demo
#
# Written by Fotis Gimian
# http://github.com/fgimian
#
# This script demonstrates the MultiSSHRunner class in the multi-ssh library
# interacting with multiple servers
#
import traceback
import paramikoe
from multissh import MultiSSHRunner


def server_interaction(client, hostname):
    """The server interaction function."""
    prompt = 'fots@fotsies-ubuntu-testlab:~\$ '

    # Start a client interaction using the paramiko-expect class
    interact = paramikoe.SSHClientInteraction(client, timeout=10,
                                              display=False)
    interact.expect(prompt)

    # Run the first command and capture the cleaned output.
    interact.send('cat /etc/*release')
    interact.expect(prompt)
    output1 = interact.current_output_clean

    # Now let's do the same for the uname command
    interact.send('uname -a')
    interact.expect(prompt)
    output2 = interact.current_output_clean

    # Send the exit command and expect EOF (a closed session)
    interact.send('exit')
    interact.expect()

    # Return a tuple of the results
    return output1, output2


def main():
    # Set login credentials and server details
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
                username=username, password=password,
                interaction=server_interaction)

        # Run the interactions, returned is a list of outputs (outputs are in
        # whatever format returned by the interaction function)
        outputs = runner.run()

        # Go through and print the command outputs
        for device, output in zip(devices, outputs):
            print '-- Device:', device, '--\n'
            output1, output2 = output
            print '/etc/*release output:'
            print output1
            print 'uname -a output:'
            print output2
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()

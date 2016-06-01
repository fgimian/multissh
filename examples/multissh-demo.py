#!/usr/bin/env python
#
# Multi-SSH Demo
#
# Written by Fotis Gimian
# http://github.com/fgimian
#
# This script demonstrates the MultiSSHRunner class in the multi-ssh library
#
import traceback
from multissh import MultiSSHRunner


def main():
    # Set login credentials and the command to run
    connect_timeout = 30
    devices = ['server1', 'server2', 'server3']
    username = 'fots'
    password = 'password'
    command = 'uname -a'

    try:
        # Create a multi-SSH runner.  Processes sets the number of processes
        # that can run at the same time.
        runner = MultiSSHRunner(processes=2)

        # We must add jobs one at a time (allows for more flexibility)
        for device in devices:
            runner.add_ssh_job(
                hostname=device, connect_timeout=connect_timeout,
                username=username, password=password, command=command)

        # Run the commands, returned is a list of tuples as follows:
        # (return_code, stdout, stderr)
        outputs = runner.run()

        # Process the output
        for device, output in zip(devices, outputs):
            if output:
                return_code, stdout, stderr = output

            # Check the return code was 0 (successful) and something was
            # returned in stdout
            if output and stdout and return_code == 0:
                print device, stdout,
            # If output has been set and we arrive here, then the return code
            # was non-zero or stdout was empty
            elif output:
                print device, 'Command did not run successfully'
            # Otherwise, we didn't connect successfully
            else:
                print device, "Couldn't connect to this server"
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()

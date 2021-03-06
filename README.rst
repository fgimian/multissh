Multi-SSH
=========

|License|

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/fgimian/multissh/blob/master/LICENSE

.. image:: https://raw.githubusercontent.com/fgimian/multissh/master/images/multissh-logo.png
   :alt: Multi-SSH Logo

Artwork courtesy of `Open Clip Art
Library <https://openclipart.org/detail/193012/man-working-at-computers>`_

Introduction
------------

Multi-SSH is my take on multiprocessing and Paramiko. I have huge respect and
admiration for projects such as `Fabric <http://fabfile.org/>`_ and
`Ansible <https://github.com/ansible/ansible/>`_ which were a great reference
while I was developing this library.

So the obvious question, why another library to do the same thing? Heres
where Multi-SSH stands apart:

- This library is completely abstract and made to run on Cisco IOS,
  Unix and any other device which supports SSH.  There are no
  Unix-specific commands or interactions used.
- The library allows integration with my paramiko-expect library,
  allowing complex interactions with servers.
- The library is made to be integrated with scripts and doesn't rely on
  config files for storing server names and other information. The user
  is requested to perform that task themselves via JSON or similar.
- The library implements tailing of a file across multiple servers in
  one session.

Quick Start
-----------

To install Multi-SSH, simply run the following at your prompt:

.. code:: bash

    pip install git+https://github.com/fgimian/multissh.git

Here's how we can use the library (please see
`multissh-demo.py <https://github.com/fgimian/multissh/blob/master/examples/multissh-demo.py>`_
for the complete code):

.. code:: python

    # Create a multi-SSH runner.  Processes sets the number of processes that
    # can run at the same time.
    runner = MultiSSHRunner(processes=2)

    # We must add jobs one at a time (allows for more flexibility)
    for device in devices:
        runner.add_ssh_job(hostname=device, connect_timeout=connect_timeout,
                           username=username, password=password, command=command)

    # Run the commands, returned is a list of tuples.  Tuples are as follows:
    # (return_code, stdout, stderr)
    outputs = runner.run()

    # Process the output
    for device, output in zip(devices, outputs):
        if output:
            return_code, stdout, stderr = output

        # Check the return code was 0 (successful) and something was returned in stdout
        if output and stdout and return_code == 0:
            print device, stdout,
        # If output has been set and we arrive here, then the return code was non-zero or stdout was empty
        elif output:
            print device, 'Command did not run successfully'
        # Otherwise, we didn't connect successfully
        else:
            print device, "Couldn't connect to this server"

As well as running basic commands, Multi-SSH also supports custom interactions.
A function (such as that shown below) can be written and passed into the
add_ssh_job function via the ``interaction`` variable (see
`multissh-interact-demo.py <https://github.com/fgimian/multissh/blob/master/examples/multissh-demo.py>`_
for the complete code):

.. code:: python

    def server_interaction(client, hostname):
        """The server interaction function"""
        prompt = 'fots@fotsies-ubuntu-testlab:~\$ '

        # Start a client interaction using the paramiko-expect class
        interact = paramikoe.SSHClientInteraction(client, timeout=10, display=False)
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

Similar to that above, you may use the special tail function to tail a
log on multiple servers in the one session. Gone are the days of logging
into 10 web servers to tail the apache access logs during a fault!
Here's how the interact function looks (full code listing is in
`multissh-tail-demo.py <https://github.com/fgimian/multissh/blob/master/examples/multissh-tail-demo.py>`_):

.. code:: python

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

License
-------

Multi-SSH is released under the **MIT** license. Please see the
`LICENSE <https://github.com/fgimian/multissh/blob/master/LICENSE>`_
file for more details.

TODO
----

- Piping scripts into other commands and then interrupting them with
  Ctrl+C causes an error message (shown below)> This only occurs when
  you attempt to print text inside the KeyboardInterrupt exception:
  ::

      close failed in file object destructor:
      sys.excepthook is missing
      lost sys.stderr

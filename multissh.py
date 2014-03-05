#
# Multi-SSH
#
# Written by Fotis Gimian
# http://github.com/fgimian
#
# This library allows for the execution of commands and the tailing of
# logs in parallel across multiple servers.
#
# You must have Paramiko installed in order to use this library.  If you
# wish to interact with servers, you should also consider using my
# paramiko-expect library.
#
import sys
sys.path.append('lib')
import multiprocessing
import signal
import paramiko
import Crypto.Random


class MultiSSHRunner:
    """This class provides a way to run commands and tail logs in parallel
    across multiple servers."""

    def __init__(self, processes=None):
        """The constructor for our MultiSSHRunner class.

        Keyword arguments:
        processes -- Number of concurrent processes to run at the same time
                     (e.g. if this was set to 2 and you had 5 servers, then
                     the commands would be run in 3 batches)

        """
        self.processes = processes
        self.job_details = []

    def add_ssh_job(self, hostname, username=None, password=None, command=None,
                    interaction=None, key_filename=None, connect_timeout=60):
        """This function adds a job to the SSH job list.

        Arguments:
        hostname -- The hostname of the server
        command or interaction -- See below, one of these is mandatory

        Keyword arguments:
        username -- The username to authenticate with
        password -- The password or passphrase to authenticate with
        command -- Option 1: The command to run either as a string or a list
                   of commands
        interaction -- Option 2: An interaction function which will take
                       control of the SSH Client.  The interaction function
                       prototype has to be:
                       def example_function(client, hostname)
        key_filename -- The SSH key file location
        connect_timeout -- The connection timeout in seconds

        Raises:
        Exception -- Raised if no command or interaction is provided

        """
        if command or interaction:
            self.job_details.append(
                {'hostname': hostname, 'username': username,
                 'password': password, 'command': command,
                 'interaction': interaction, 'key_filename': key_filename,
                 'connect_timeout': connect_timeout})
        else:
            raise Exception(
                'Job command information was missing and therefore the job '
                'could not be added')

    def run(self):
        """This function starts the SSH jobs in parallel.

        Returns:
        A list of outputs from each SSH process

        """

        def _init_pool():
            # Workaround: Run the atfork function each time we create a
            # connection to avoid the following errors:
            # 'No handlers could be found for logger "paramiko.transport"'
            Crypto.Random.atfork()

            # Workaround: Force ignoring of Ctrl+C so that we can handle it
            # ourselves
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Create our multiprocessing workers ensuring we don't waste workers
        pool = multiprocessing.Pool(
            processes=min(self.processes, len(self.job_details)),
            initializer=_init_pool)
        try:
            # Create a list of jobs by appending each process to the list
            jobs = []
            for job_detail in self.job_details:
                jobs.append(pool.apply_async(_run_job, [job_detail]))

            # Do not allow anymore jobs to be added
            pool.close()

            # Workaround: To ensure proper handling of KeyboardInterrupt, we
            # must wait for each job to complete with a timeout specified.
            # I have set the timeout to the maximum value possible as we
            # really want an infinite timeout.
            [job.wait(timeout=sys.maxint) for job in jobs]

            # Join the pool (not really necessary but cleaner)
            pool.join()

            # Return a list of results
            return [job.get() for job in jobs]
        except:
            pool.terminate()
            raise


def _run_job(job_detail):
    """Here is the function run in each thread which uses paramiko to run the
    appropriate command or interaction.  This must be outside the class as
    multiprocessing can't handle a function within a class for its threads.

    Arguments:
    job_detail -- A dict with all the information relating to the job, the
                  dict is formatted as follows:
                  {'hostname': hostname, 'username': username,
                   'password': password, 'command': command,
                   'interaction': interaction, 'key_filename': key_filename,
                   'connect_timeout': connect_timeout}

    Returns:
    - None: If the command fails
    - (return_code, stdout, stderr): If a single command has been sent through
    - List of tuples (as above): If multiple commands were sent through

    """
    try:
        # Create a new SSH client object
        client = paramiko.SSHClient()

        # Set SSH key parameters to auto accept unknown hosts
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the host
        client.connect(
            timeout=job_detail['connect_timeout'],
            hostname=job_detail['hostname'],
            key_filename=job_detail['key_filename'],
            username=job_detail['username'], password=job_detail['password'])

        # Run a single command
        if job_detail['command'] and isinstance(job_detail['command'], str):
            chan = client.get_transport().open_session()
            chan.exec_command(job_detail['command'])
            return_code = chan.recv_exit_status()
            stdout = chan.makefile('rb').read()
            stderr = chan.makefile_stderr('rb').read()
            client.close()
            return return_code, stdout, stderr

        # Run multiple commands one after the other
        elif job_detail['command']:
            output = []
            for command in job_detail['command']:
                chan = client.get_transport().open_session()
                chan.exec_command(command)
                return_code = chan.recv_exit_status()
                stdout = chan.makefile('rb').read()
                stderr = chan.makefile_stderr('rb').read()
                output.append((return_code, stdout, stderr))
            client.close()
            return output

        # Run an interaction function
        elif job_detail['interaction']:
            return job_detail['interaction'](client, job_detail['hostname'])
    except:
        try:
            client.close()
        except:
            pass
        return None

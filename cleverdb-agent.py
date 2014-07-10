#!/usr/bin/python
import subprocess
from time import sleep


def run():
    """
    -f tells ssh to go into the background (daemonize).
    -N tells ssh that you don't want to run a remote command.
    -q tells ssh to be quiet
    -R remote port forwarding
    -i private key file

    Ex: ssh -N -R 8080:localhost:3306 vagrant@192.168.100.3 -i key.priv
    """
    retry_count = 0

    while True:
        # get config from api:
        config = _get_config()
        local_part = "%i:localhost:%i" % (
            config['slave_port'],
            config['master_port'])

        ssh_options = ["ssh", "-N", "-R"]
        ssh_options.append(local_part)
        ssh_options.append(config['slave_host'])
        ssh_options.append("-i")
        ssh_options.append(config['private_key'])

        # start the SSH tunnel
        print "Starting ssh tunnel..."
        prog = subprocess.Popen(ssh_options, stdout=subprocess.PIPE)
        call_res = prog.communicate()

        # ssh tunnel broken at this point

        # retry getting latest config from api:
        retry_count += 1
        print "Sleeping...%i seconds" % retry_count
        sleep(retry_count)
        print "Retrying...%i" % retry_count


def _get_config():
    # TODO: get from api
    return {'slave_host': "192.168.100.4",
            'slave_port': 8080,
            'master_port': 3306,
            'private_key': "key.priv"}


if __name__ == '__main__':
    run()

#!/usr/bin/python
import subprocess
from time import sleep
import os
import sys
import logging
import urllib2
import base64
import json
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleverdb-agent")

KEY_PRIV = os.environ.get("CD_SSH_KEY",
                          "/usr/share/cleverdb-agent/key.priv")
# TODO: read-in CD_DB_ID from config:
DB_ID = os.environ.get("CD_DB_ID")

prog = None

def signal_handler(signo, frame):
    global prog
    logger.info("Got signqal %s, terminating", signo)
    if prog:
        logger.info("Stopping SSH client")
        prog.send_signal(signal.SIGTERM)
    sys.exit(0)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

def run():
    """
    -f tells ssh to go into the background (daemonize).
    -N tells ssh that you don't want to run a remote command.
    -R remote port forwarding
    -q tells ssh to be quiet
    -i private key file

    Ex: ssh -N -R 6789:localhost:3306 vagrant@192.168.100.3 -i key.priv -p 8080
    """
    retry_count = 0

    global prog

    while True:
        # get config from api:
        config = _get_config()
        local_part = "%s:localhost:%s" % (
            config['container_port'],
            config['master_port'])

        # save private key to disk
        # key = open("private.key", "w")
        # key.write(config['ssh_private_key'])
        # key.close()

        ssh_options = ["ssh"]

        # TODO: generate 2 key pair so we don't have to ignore host checking
        ssh_options.append("-o")
        ssh_options.append("UserKnownHostsFile=/dev/null")
        ssh_options.append("-o")
        ssh_options.append("StrictHostKeyChecking=no")

        ssh_options.append("-N")
        ssh_options.append("-R")
        ssh_options.append(local_part)
        ssh_options.append("%s@%s" % (config['user'], config['ip']))
        ssh_options.append("-i")
        ssh_options.append(config['ssh_private_key'])
        ssh_options.append("-p")
        ssh_options.append(config['port'])

        # start the SSH tunnel
        logger.info("Starting ssh tunnel...")
        logger.debug("SSH option is ")
        logger.debug(ssh_options)

        try:
            prog = subprocess.Popen(ssh_options, stdout=subprocess.PIPE)
            prog.communicate()
        except Exception, e:
            logger.debug(e)
        finally:
            prog = None

        # ssh tunnel broken at this point
        # retry getting latest config from api:
        retry_count += 1
        logger.info("Sleeping...%i seconds" % retry_count)
        sleep(retry_count)
        logger.info("Retrying...%i" % retry_count)


def _get_config():
    auth = base64.encodestring('%s:%s' % ('cleverdb', 'c13VRvDblc'))[:-1]
    url = 'http://cleverdb.com/api/agent/%s/configuration' % (DB_ID)
    req = urllib2.Request(url)
    req.add_header("Authorization", "Basic %s" % auth)

    retry_count = 0
    while True:
        try:
            handle = urllib2.urlopen(req)
            res = json.loads(handle.read())

            return res
        except Exception, e:
            retry_count += 1
            logger.info("Retrying to connect to api...")
            logger.info("Sleeping...%i seconds" % retry_count)
            sleep(retry_count)
            logger.error(e)

if __name__ == '__main__':
    run()

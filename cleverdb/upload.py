#!/usr/bin/python
import subprocess
from time import sleep
import os
import sys
import logging
import logging.handlers
import signal
import optparse
import pwd
import tempfile
import shutil
import hashlib
import glob
from cleverdb.compat import *
from cleverdb.version import __version__
from cleverdb.api import get_tunnel_config


logging.QUIET = 1000
logger = logging.getLogger("cleverdb-agent")

prog = None
temps = None


def signal_handler(signo, frame):
    global prog, temps
    logger.info("Got signqal %s, terminating", signo)
    if prog:
        logger.info("Stopping SSH client")
        prog.send_signal(signal.SIGTERM)
    if temps:
        shutil.rmtree(temps)
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)


class OptionParser(optparse.OptionParser):
    usage = '%prog'
    LOG_LEVELS = {
        'all': logging.NOTSET,
        'debug': logging.DEBUG,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'quiet': logging.QUIET,
    }

    # Make a list of log level names sorted by log level
    SORTED_LEVEL_NAMES = [
        l[0] for l in sorted(LOG_LEVELS.items(), key=lambda x: x[1])
    ]

    def __init__(self):
        optparse.OptionParser.__init__(self, version=__version__,
                                       usage='usage: %prog [options] filename')
        self.add_option(
            '-l', '--log-level',
            choices=list(self.LOG_LEVELS),
            dest='log_level',
            default='info',
            help='logging log level. One of {0}. '
                 'Default: \'{1}\'.'.format(
                ', '.join([repr(l) for l in self.SORTED_LEVEL_NAMES]),
                'info')
        )
        self.add_option(
            '--confdir',
            action='store',
            dest="confdir",
            default="/etc/cleverdb-agent",
            help="directory to store config files"
        )
        self.add_option(
            '--config',
            action='append',
            dest='configs',
            default=[],
            help='additional config files'
        )
        self.add_option(
            '--rsync',
            action='store_true',
            default=False,
            dest='rsync',
            help='upload file using rsync'
        )


def run(uploader, host, db_id, api_key, filename):
    retry_count = 0
    global prog, temps

    logger.info("Uploading file...")
    while True:
        # get config from api:
        config = get_tunnel_config(host, db_id, api_key)

        # save private key to disk
        temps = tempfile.mkdtemp()
        key = tempfile.NamedTemporaryFile(dir=temps, delete=False)
        os.chmod(key.name, int("400", 8))
        key.write(config['ssh_private_key'])
        key.close()

        try:
            dump_file = '{}.sql'.format(db_id)
            checksum_file = tempfile.NamedTemporaryFile(dir=temps, delete=False)
            checksum_file.write("{} {}\n".format(checksum(filename), dump_file))
            checksum_file.close()
            uploader(config, key.name, checksum_file.name,
                     "/uploads/{}.checksum".format(db_id))

            uploader(config, key.name, filename,
                     "/uploads/{}".format(dump_file))
            logger.info("File uploaded successfully. "
                        "Please refer to the website for additional "
                        "instructions.")
        except Exception as e:
            logger.debug(e)
        else:
            return
        finally:
            shutil.rmtree(temps)
            temps = None

        # ssh tunnel broken at this point
        # retry getting latest config from api:
        retry_count += 1
        logger.debug("Sleeping...%i seconds" % retry_count)
        sleep(retry_count)
        logger.info("Retry uploading file...%i" % retry_count)


def scp_cp(config, keyfile, src, dst):
    scp_commandline = [
        "scp",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "StrictHostKeyChecking=no",
        "-i", keyfile,
        "-P", byte_string(config['port']),
        src,
        byte_string("{}@{}:{}".format(config['user'], config['ip'], dst))
    ]
    logger.debug(scp_commandline)
    check_call(scp_commandline)


def rsync_cp(config, keyfile, src, dst):
    # TODO: generate 2 key pair so we don't have to ignore host checking
    ssh_commandline = [
        "ssh",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "StrictHostKeyChecking=no",
        "-i", keyfile,
        "-p", byte_string(config['port'])
    ]

    rsync_commandline = [
        "rsync",
        "-e", " ".join(ssh_commandline),
        src,
        byte_string("%s@%s:%s" % (config['user'], config['ip'], dst)),
    ]
    logger.info("Starting RSYNC...")
    logger.debug("RSYNC option is ")
    logger.debug(rsync_commandline)
    check_call(rsync_commandline)


def check_call(*args, **kwargs):
    """Modified version of subprocess.check_call """
    try:
        prog = subprocess.Popen(*args, **kwargs)
        prog.communicate()
    finally:
        if prog.returncode == 0:
            logger.info("Database dump uploaded successfully.")
        else:
            logger.error(
                "command terminated with non-zero error code: {}".format(
                    prog.returncode
                )
            )
            cmd = kwargs.get("args") or args[0]
            raise subprocess.CalledProcessError(prog.returncode, cmd)
        prog = None


def checksum(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'r') as f:
        while True:
            data = f.read(65535)
            if len(data) == 0:
                break
            sha1.update(data)
        return sha1.hexdigest()


def setup_logging(log_level):
    logging.basicConfig(level=log_level)


def main():
    option_parser = OptionParser()
    (options, args) = option_parser.parse_args()

    if len(args) != 1 or not os.path.isfile(args[0]):
        option_parser.error('A valid filename is required to upload')

    setup_logging(
        option_parser.LOG_LEVELS[options.log_level],
    )

    try:
        cp = ConfigParser()
        if os.path.isdir(options.confdir):
            configs = glob.iglob(os.path.join(options.confdir, "*.conf"))
            configs = list(sorted(configs))
        else:
            configs = []
        configs.extend(options.configs)

        logger.debug(configs)
        if not configs:
            logger.critical("Configuration file {0} does not exist or "
                            "not readable".format(options.configs))
            sys.exit(1)

        cp.read(configs)
        db_id = cp.get('agent', 'db_id')
        api_key = cp.get('agent', 'api_key')
        host = cp.get('agent', 'connect_host')
    except ConfigParserError as e:
        logger.critical("Error parsing configuration file {0}: {1}".format(
            options.configs,
            e.message
        ))
        sys.exit(1)

    uploader = options.rsync and rsync_cp or scp_cp
    run(uploader, host, db_id, api_key, args[0])


if __name__ == '__main__':
    main()

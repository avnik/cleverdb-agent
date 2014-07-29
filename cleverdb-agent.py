#!/usr/bin/python
import subprocess
from time import sleep
import os
import sys
import logging
import logging.handlers
import base64
import json
import signal
import optparse
import pwd
import tempfile
import shutil

# Python2 vs Python3 black magic
py_version = sys.version_info[:3]
# Python 2
if py_version < (3, 0, 0):
    import urllib2 as urllib
    from ConfigParser import ConfigParser
    from ConfigParser import Error as ConfigParserError

    chr = unichr
    native_string = str
    decode_string = unicode
    encode_string = str
    unicode_string = unicode
    string_type = basestring
    byte_string = str
else:
    import urllib.request as urllib
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError
    import builtins

    byte_string = bytes
    string_type = str
    native_string = str
    decode_string = bytes.decode
    encode_string = lambda s: bytes(s, 'utf-8')
    unicode_string = str
# end of magic block

__version__ = '0.2.2'
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
        optparse.OptionParser.__init__(self)
        self.add_option(
            '-l', '--log-level',
            choices=list(self.LOG_LEVELS),
            dest='log_level',
            default='critical',
            help='logging log level. One of {0}. '
                 'Default: \'{1}\'.'.format(
                ', '.join([repr(l) for l in self.SORTED_LEVEL_NAMES]),
                'critical')
        )
        self.add_option(
            '--syslog-level',
            choices=list(self.LOG_LEVELS),
            dest='syslog_level',
            default='info',
            help='logging log level. One of {0}. '
                 'Default: \'{1}\'.'.format(
                ', '.join([repr(l) for l in self.SORTED_LEVEL_NAMES]),
                'info')
        )
        self.add_option(
            '--syslog-facility',
            dest='facility',
            action='store',
            default='local5',
            help='Syslog facility'
        )
        self.add_option(
            '-d', '--daemon',
            help='daemonize',
            dest='daemon',
            action='store_true',
            default=False
        )
        self.add_option(
            '-U', '--run-as-user',
            dest='user',
            action='store',
        )
        self.add_option(
            '--pid',
            action='store',
            dest="pid_file"
        )
        self.add_option(
            '--config',
            action='store',
            dest='config',
            default='/etc/cleverdb-agent/config'
        )
        self.add_option(
            '--version',
            help='version of the agent',
            dest='version',
            action='store_true',
            default=False
        )


def run(db_id, api_key):
    """
    -f tells ssh to go into the background (daemonize).
    -N tells ssh that you don't want to run a remote command.
    -R remote port forwarding
    -q tells ssh to be quiet
    -i private key file

    Ex: ssh -N -R 6789:localhost:3306 vagrant@192.168.100.3 -i key.priv -p 8080
    """
    retry_count = 0

    global prog, temps

    while True:
        # get config from api:
        config = _get_config(db_id, api_key)
        local_part = "%s:localhost:%s" % (
            config['container_port'],
            config['master_port'])

        # save private key to disk
        temps = tempfile.mkdtemp()
        key = tempfile.NamedTemporaryFile(dir=temps, delete=False)
        os.chmod(key.name, int("400", 8))
        key.write(config['ssh_private_key'])
        key.close()

        ssh_options = ["ssh"]

        # TODO: generate 2 key pair so we don't have to ignore host checking
        ssh_options.append("-o")
        ssh_options.append("UserKnownHostsFile=/dev/null")
        ssh_options.append("-o")
        ssh_options.append("StrictHostKeyChecking=no")

        ssh_options.append("-N")
        ssh_options.append("-R")
        ssh_options.append(local_part)
        ssh_options.append(
            byte_string("%s@%s" % (config['user'], config['ip'])))
        ssh_options.append("-i")
        ssh_options.append(key.name)
        ssh_options.append("-p")
        ssh_options.append(byte_string(config['port']))

        # start the SSH tunnel
        logger.info("Starting SSH tunnel...")
        logger.debug("SSH option is ")
        logger.debug(ssh_options)

        try:
            prog = subprocess.Popen(ssh_options,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            prog.communicate()
        except Exception as e:
            logger.debug(e)
        finally:
            if prog.returncode != 0:
                logger.error(
                    "SSH terminated with non-zero error code: {}".format(
                        prog.returncode
                    )
                )
                logger.error("SSH: {}".format(prog.stderr))
            shutil.rmtree(temps)
            temps = None
            prog = None

        # ssh tunnel broken at this point
        # retry getting latest config from api:
        retry_count += 1
        logger.info("Sleeping...%i seconds" % retry_count)
        sleep(retry_count)
        logger.info("Retrying opening SSH tunnel...%i" % retry_count)


def _get_config(db_id, api_key):
    # TODO: remove basic auth
    auth = base64.encodestring(
        byte_string('{}:{}'.format('cleverdb', 'c13VRvDblc')))[:-1]
    url = 'http://cleverdb.com/api/agent/%s/configuration?api_key=%s' % (
        db_id, api_key)
    req = urllib.Request(url)
    req.add_header("Authorization", "Basic %s" % auth)

    retry_count = 0
    while True:
        try:
            handle = urllib.urlopen(req)
            res = json.loads(handle.read())
            return res
        except Exception as e:
            retry_count += 1
            logger.info("Retrying to connect to api...")
            logger.info("Sleeping...%i seconds" % retry_count)
            sleep(retry_count)
            logger.error(e)


def chugid(runas):
    '''
    Change the current process to belong to
    the imputed user (and the groups he belongs to)
    '''
    uinfo = pwd.getpwnam(runas)
    supgroups = []
    supgroups_seen = set()
    # The line below used to exclude the current user's primary gid.
    # However, when root belongs to more than one group
    # this causes root's primary group of '0' to be dropped from
    # his grouplist.  On FreeBSD, at least, this makes some
    # command executions fail with 'access denied'.
    #
    # The Python documentation says that os.setgroups sets only
    # the supplemental groups for a running process.  On FreeBSD
    # this does not appear to be strictly true.
    group_list = get_group_dict(runas, include_default=True)
    if sys.platform == 'darwin':
        group_list = [a for a in group_list
                      if not a.startswith('_')]
    for group_name in group_list:
        gid = group_list[group_name]
        if (gid not in supgroups_seen
            and not supgroups_seen.add(gid)):
            supgroups.append(gid)

    if os.getgid() != uinfo.pw_gid:
        try:
            os.setgid(uinfo.pw_gid)
        except OSError as err:
            logger.error(
                'Failed to change from gid {0} to {1}. Error: {2}'.format(
                    os.getgid(), uinfo.pw_gid, err
                )
            )
            sys.exit(os.EX_OSERR)

    # Set supplemental groups
    if sorted(os.getgroups()) != sorted(supgroups):
        try:
            os.setgroups(supgroups)
        except OSError as err:
            logger.error(
                'Failed to set supplemental groups to {0}. Error: {1}'.format(
                    supgroups, err
                )
            )

    if os.getuid() != uinfo.pw_uid:
        try:
            os.setuid(uinfo.pw_uid)
        except OSError as err:
            logger.error(
                'Failed to change from uid {0} to {1}. Error: {2}'.format(
                    os.getuid(), uinfo.pw_uid, err
                )
            )
            sys.exit(os.EX_OSERR)


def daemonize():
    '''
    Daemonize a process
    '''
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(os.EX_OK)
    except OSError as exc:
        log.error(
            'fork #1 failed: {0} ({1})'.format(exc.errno, exc.strerror)
        )
        sys.exit(os.EX_OSERR)
    # decouple from parent environment
    os.chdir('/')
    # noinspection PyArgumentList
    os.setsid()
    os.umask(18)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(os.EX_OK)
    except OSError as exc:
        logger.error(
            'fork #2 failed: {0} ({1})'.format(
                exc.errno, exc.strerror
            )
        )
        sys.exit(os.EX_OSERR)

    dev_null = open('/dev/null', 'r+')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    os.dup2(dev_null.fileno(), sys.stdout.fileno())
    os.dup2(dev_null.fileno(), sys.stderr.fileno())


def setup_logging(log_level, syslog_level, facility):
    logging.basicConfig(level=log_level)
    syslog = logging.handlers.SysLogHandler(address='/dev/log',
                                            facility=facility)
    syslog.setLevel(syslog_level)
    logger.addHandler(syslog)
    logger.info("Logger initialized")


def main():
    option_parser = OptionParser()
    (options, args) = option_parser.parse_args()

    # check for --version
    if options.version:
        exit(__version__)

    setup_logging(
        option_parser.LOG_LEVELS[options.log_level],
        option_parser.LOG_LEVELS[options.syslog_level],
        options.facility
    )

    # check if config file exist and readble:
    if (not os.path.isfile(options.config) or
            not os.access(options.config, os.R_OK)):
        logger.critical("Configuration file {0} does not exist or "
                        "not readable".format(options.config))
        sys.exit(1)

    try:
        cp = ConfigParser()
        cp.read(options.config)
        db_id = cp.get('agent', 'db_id')
        api_key = cp.get('agent', 'api_key')
    except ConfigParserError as e:
        logger.critical("Error parsing configuration file {0}: {1}".format(
            options.config,
            e.message
        ))
        sys.exit(1)

    if options.user:
        chugid(options.user)
    if options.daemon:
        daemonize()
    run(db_id, api_key)


if __name__ == '__main__':
    main()

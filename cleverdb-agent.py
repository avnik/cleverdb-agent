from subprocess import call
from optparse import OptionParser
import subprocess


def run():
    parser = OptionParser()
    parser.add_option(
        "-a", "--host", dest="host", type="str",
        help="The host address. Ex: -a host.example.com"
    )

    parser.add_option(
        "-s", "--source-port", dest="source_port", type="int",
        help="The source port. Ex: -s 3306"
    )

    parser.add_option(
        "-d", "--destination-port", dest="destination_port", type="int",
        help="The destination port. Ex: -d 8080"
    )

    parser.add_option(
        "-i", "--private-key", dest="private_key", type="str",
        help="The path to private key file. Ex: -i ~/.ssh/my_private.key"
    )

    (options, args) = parser.parse_args()

    if None in [options.host, options.source_port, options.destination_port]:
        exit("Host name and ports are required. "
             "Ex: -a example.com -s 3306 -d 8080")

    print "Host: %s. Source port: %s. Destination port: %s" % (
        options.host,
        options.source_port,
        options.destination_port)

    print "Starting port forwarding..."
    local_mapping = "%i:localhost:%i" % (options.destination_port,
                                         options.source_port)
    destination_mapping = options.host
    """
    -f tells ssh to go into the background (daemonize).
    -N tells ssh that you don't want to run a remote command.
    -q tells ssh to be quiet
    -L specifies the port forwarding
    -i private key file
    """
    # ssh -N -R 8080:localhost:3306 vagrant@192.168.100.3 -i key.priv
    ssh_options = ["ssh", "-N", "-R", local_mapping, destination_mapping]

    if options.private_key:
        ssh_options.append("-i")
        # TODO: this will later come from api
        ssh_options.append('key.priv')

    print "SSH options..."
    print ssh_options
    # call_res = call(ssh_options)
    prog = subprocess.Popen(ssh_options, stderr=subprocess.PIPE)
    call_res = prog.communicate()[1]

    print 'here?...'
    print call_res


# def _get_priv_key():
#     priv_key = open('key.priv', 'r')
#
#     return priv_key.read()

if __name__ == '__main__':
    run()
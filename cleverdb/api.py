import logging
import json
import base64
from time import sleep
from cleverdb.compat import *


logger = logging.getLogger("cleverdb-agent")


def get_tunnel_config(host, db_id, api_key):
    """
    Get configuration settings from api manager

    Sample return from api
    {
    "ports": [
        {
            "master": 3306,
            "slave": 6789
        }
    ],
    "ip": "54.227.103.172",
    "port": "49153",
    "user": "634391d4b5ed43038667ccd32c4d7c1b",
    "ssh_private_key": "-----BEGIN DSA PRIVATE KEY--END DSA PRIVATE KEY-----",
    "password": "xNudfraNTlVhRaVkoRcDWQcc"
    }
    """
    # TODO: remove basic auth
    auth = base64.encodestring(
        byte_string('{}:{}'.format('cleverdb', 'c13VRvDblc')))[:-1]
    url = '%s/v1/agent/%s/configuration?api_key=%s' % (
        host, db_id, api_key)
    req = urllib.Request(url)
    req.add_header("Authorization", "Basic %s" % auth)

    retry_count = 0
    while True:
        try:
            handle = urllib.urlopen(req)
            res = json.loads(handle.read())
            logger.debug(res)
            return res
        except Exception as e:
            retry_count += 1
            logger.info("Retrying to connect to api...")
            logger.info("Sleeping...%i seconds" % retry_count)
            sleep(retry_count)
            logger.error(e)

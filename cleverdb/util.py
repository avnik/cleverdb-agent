import sys


def py23():
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

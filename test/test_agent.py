import unittest
from cleverdb.agent import OptionParser


class CommandLineTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        parser = OptionParser()
        cls.parser = parser


class AgentTest(CommandLineTestCase):

    def test_version(self):
        (a, b) = self.parser.parse_args(['--version'])
        print a
        print b
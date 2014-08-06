"""cleverdb-agent - User agent to communicate with cleverdb service

The cleverdb-agent will open a secure tunnel to cleverdb service
"""

from setuptools import setup
from pip.req import parse_requirements
from cleverdb import __version__

doc = __doc__.splitlines()
requirements = parse_requirements("requirements.txt")

setup(
    name='cleverdb-agent',
    description=doc[0],
    long_description='\n'.join(doc[2:]),
    version=__version__,
    install_requires=[str(ir.req) for ir in requirements]
)

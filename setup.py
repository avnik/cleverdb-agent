"""cleverdb-agent - User agent to communicate with cleverdb service

The cleverdb-agent will open a secure tunnel to cleverdb service
"""

from setuptools import setup
from pip.req import parse_requirements

doc = __doc__.splitlines()
requirements = parse_requirements("requirements.txt")

setup(
    name='cleverdb-agent',
    description=doc[0],
    long_description='\n'.join(doc[2:]),
    version='0.1.0',
    install_requires=[str(ir.req) for ir in requirements]
)

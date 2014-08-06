"""cleverdb-agent - User agent to communicate with cleverdb service

The cleverdb-agent will open a secure tunnel to cleverdb service
"""

from setuptools import setup, find_packages
from cleverdb import __version__


## Requirements only for development builds using pip,
## This package haven't any runtime dependencies outside standard library
## and setuptools
requirements = ["setuptools"]
try:
    from pip.req import parse_requirements
except ImportError:
    pass
else:
    requirements.extend([str(ir.req) for ir in parse_requirements("requirements.txt")])

doc = __doc__.splitlines()

setup(
    name='cleverdb-agent',
    description=doc[0],
    long_description='\n'.join(doc[2:]),
    version=__version__,
    packages=find_packages(),
    namespace_packages=["cleverdb"],
    install_requires=requirements,
    entry_points = """
    [console_scripts]
    cleverdb-agent=cleverdb.agent:main
    cleverdb-upload=cleverdb.upload:main
    """,
)

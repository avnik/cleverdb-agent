"""cleverdb-agent - User agent to communicate with cleverdb service

The cleverdb-agent will open a secure tunnel to cleverdb service
"""

from setuptools import setup, find_packages
import sys
import os

versionfile = os.path.abspath(os.path.join(os.path.dirname(__file__), "cleverdb", "version.py"))
context = {}
exec(open(versionfile, "r").read(), context)
__version__ = context["__version__"]

# # Requirements only for development builds using pip,
## This package haven't any runtime dependencies outside standard library
## and setuptools
requirements = ["setuptools"]
try:
    from pip.req import parse_requirements
except ImportError:
    pass
else:
    requirements.extend(
        [str(ir.req) for ir in parse_requirements("requirements.txt")])

doc = __doc__.splitlines()

setup(
    name='cleverdb-agent',
    description=doc[0],
    long_description='\n'.join(doc[2:]),
    version=__version__,
    author="SendGrid Engineers",
    author_email="support@cleverdb.io",
    maintainer="SendGrid Engineers",
    maintainer_email="support@cleverdb.io",
    url="https://github.com/sendgridlabs/cleverdb-agent",
    license="MIT",
    packages=find_packages(exclude=['test']),
    namespace_packages=["cleverdb"],
    install_requires=requirements,
    entry_points="""
    [console_scripts]
    cleverdb-agent=cleverdb.agent:main
    cleverdb-upload=cleverdb.upload:main
    """,
)

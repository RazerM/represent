#!/usr/bin/env python3
import re
import sys

from setuptools import setup, Command, find_packages


INIT_FILE = 'represent/__init__.py'
init_data = open(INIT_FILE).read()

metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_data))

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
LICENSE = metadata['license']
DESCRIPTION = metadata['description']

AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

requires = []

setup(
    name='Represent',
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README').read(),
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/RazerM/represent',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    license=LICENSE,
    install_requires=requires)

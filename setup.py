# coding: utf-8
from __future__ import absolute_import, division, print_function

import re
import sys

from setuptools import setup, find_packages


INIT_FILE = 'represent/__init__.py'
init_data = open(INIT_FILE).read()

metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_data))

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
LICENSE = metadata['license']
DESCRIPTION = metadata['description']

AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

requires = ['six>=1.8.0']

extras_require = {
    'test': [
        'ipython',
        'pytest>=3.0.5',
        'mock; python_version<"3.3"',
    ],
}


setup(
    name='Represent',
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/RazerM/represent',
    project_urls={
        "Documentation": "https://represent.readthedocs.io",
    },
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    license=LICENSE,
    install_requires=requires,
    extras_require=extras_require)

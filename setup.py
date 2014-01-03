#!/usr/bin/env python

PROJECT = 'xearch'

# Change docs/sphinx/conf.py too!
VERSION = '1'

from setuptools import setup, find_packages

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Full text indexing tool',
    long_description=long_description,

    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',

    install_requires=['cliff'],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'xearch = xearch.main:main'
        ],
        'xearch': [
            'index = xearch.index:Index',
            'search = xearch.search:Search',
        ],
    },

    zip_safe=False,
)


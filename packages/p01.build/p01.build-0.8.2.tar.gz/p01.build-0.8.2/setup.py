##############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.build',
    version='0.8.2',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "A build system supporting application deploy and installation",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('src','p01','build','README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    long_description_content_type = 'text/x-rst',
    license = "ZPL 2.1",
    keywords = "Zope3 z3c p01 build release deploy install",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'https://pypi.org/pypi/p01.build',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'p01.checker',
            'zope.testing',
        ]),
    install_requires = [
        'beautifulsoup4',
        'setuptools',
        ],
    entry_points = {
        'console_scripts': [
            'build = p01.build.build:main',
            'build-package = p01.build.package:main',
            'deploy = p01.build.deploy:main',
            ],
        },
    zip_safe = False,
    )

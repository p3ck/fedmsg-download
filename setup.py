# This file is part of fedmsg-download.
# Copyright (C) 2012 Red Hat, Inc.
#
# fedmsg is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# fedmsg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>
# Authors:  Bill Peck <bpeck@redhat.com>
#

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import sys

# Ridiculous as it may seem, we need to import multiprocessing and
# logging here in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except Exception:
    pass


install_requires = [
    'fedmsg',
    'pexpect',
    #'daemon',

    # These are "optional" for now to make installation from pypi easier.
    #'M2Crypto',
    #'m2ext',
]
tests_require = [
    'nose',
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.extend([
        'argparse',
        'ordereddict',
    ])
    tests_require.extend([
        'unittest2',
    ])


setup(
    name='fedmsg-download',
    version='0.1.15',
    description="Fedora Messaging Downloading Consumer",
    long_description="Fedora Messaging Downloading Consumer",
    author='Bill Peck',
    author_email='bpeck@redhat.com',
    url='http://github.com/p3ck/fedmsg-download/',
    license='LGPLv2+',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    packages=[
        'fedmsg_download',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "fedmsg-download=fedmsg_download.command:download",
        ],
        'moksha.consumer': [
            "downloader=fedmsg_download.consumer:RsyncConsumer",
        ],
        'moksha.producer': [
        ],
    }
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from itertools import chain

from setuptools import setup, find_packages

with open('README.rst', encoding='utf8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding='utf8') as history_file:
    history = history_file.read()

test_requirements = ['pytest', 'requests-mock', 'pytest-mock', 'pytest-cov', 'pytest-runner']
EXTRAS_REQUIRE = {
    'hook': [
        'django',
        'djangorestframework'
    ],
    'shell': [
        'ipython',
        'pandas',
        'pytz',
        'ptable',
        'python-dateutil',
        'humanize',
        'click>8.0',
        'pyyaml',
        'requests-toolbelt',
        'requests-to-curl==1.1.0',
    ],
    'async': [
        'httpx>=0.24.0',
    ],
    'test': test_requirements,
}

EXTRAS_REQUIRE['all'] = list(set(chain(*EXTRAS_REQUIRE.values())))

setup(
    author="Malik Sulaimanov",
    author_email='malik.sulaimanov@symphonyai.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    description="API client and CLI tools for working with SymphonyAI Store Intelligence platform",
    entry_points={
        'console_scripts': [
            'admin=rebotics_sdk.cli.admin:api',
            'dataset=rebotics_sdk.cli.dataset:api',
            'retailer=rebotics_sdk.cli.retailer:api',
            'rebm=rebotics_sdk.cli.retailer:api',
            'rebotics=rebotics_sdk.cli.common:main',
            'fvm=rebotics_sdk.cli.fvm:api',
            'hawkeye=rebotics_sdk.cli.hawkeye:api',
            'hawkeye_camera=rebotics_sdk.cli.hawkeye:hawkeye_camera',
        ],
    },
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rebotics_sdk',
    name='rebotics_sdk',
    packages=find_packages(exclude=["tests*", 'archive_test_suite', 'benchmarks']),
    test_suite='tests',
    url='http://retechlabs.com/rebotics/',
    version='0.31.1',
    zip_safe=False,
    install_requires=[
        'requests',
        'dataclasses;python_version<"3.7"',
        'more-itertools',
        'tqdm',
        'chardet',
        'py7zr<1.0.0',
        'pydantic',
    ],
    # this one is deprecated
    tests_require=test_requirements,
    extras_require=EXTRAS_REQUIRE,
)

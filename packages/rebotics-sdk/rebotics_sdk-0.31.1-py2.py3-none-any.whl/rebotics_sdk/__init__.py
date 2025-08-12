# -*- coding: utf-8 -*-

"""Top-level package for rebotics_sdk."""

__author__ = """Malik Sulaimanov"""
__email__ = 'malik@retechlabs.com'
__version__ = '0.31.1'

import logging
from os import path

from rebotics_sdk.providers import (
    AdminProvider,
    RetailerProvider,
    HawkeyeProvider,
    HawkeyeCameraProvider,
    FVMProvider,
    CvatProvider,
    DatasetProvider,
)

__all__ = [
    'AdminProvider',
    'RetailerProvider',
    'HawkeyeProvider',
    'HawkeyeCameraProvider',
    'FVMProvider',
    'CvatProvider',
    'DatasetProvider',
]

try:
    from rebotics_sdk.cli.utils import app_dir  # noqa: F401

    if path.exists(app_dir):
        from rebotics_sdk.cli.authenticated_provider import get_provider  # noqa: F401

        __all__.append('get_provider')
except ImportError:
    logging.warning('Please install rebotics_sdk[cli] to use CLI related features')

__all__ = (*__all__,)

#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals

try:
    # Unit test (Python 3.8)
    from src.lib import *
except ImportError as e:
    # Bot (Python 2.7.17)
    from lib import *

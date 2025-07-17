#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import re
# JackBot
from lib import *


def replace_two_parameters_by_one(current_template, old_param1, old_param2, new_param):
    regex = r'(\| *)' + re.escape(old_param1) + r'( *=[^\|]+) ?(?: *\| *)' + re.escape(old_param2) + r'(?: *=) ?([^\|]+)\|'

    return re.sub(regex, r'\1' + new_param + r'\2 \3|', current_template)

# -*- coding: utf-8 -*-
"""Family module for test.wikipedia.org."""
#
# (C) Pywikibot team, 2007-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 49d169e1e7fa52a36a4c33f33d6a2e91cbfbaae5 $'

from pywikibot import family


# The test wikipedia family
class Family(family.SingleSiteFamily, family.WikimediaFamily):

    """Family class for test.wikipedia.org."""

    name = 'test'
    domain = 'test.wikipedia.org'
    test_codes = ('test', )

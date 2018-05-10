# -*- coding: utf-8 -*-
"""Family module for Wikitech."""
#
# (C) Pywikibot team, 2005-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 73cdb8bccbb87ac57e0932a1120c1d7e747c13fa $'

from pywikibot import family


# The Wikitech family
class Family(family.WikimediaOrgFamily):

    """Family class for Wikitech."""

    name = 'wikitech'
    code = 'en'

    def protocol(self, code):
        """Return the protocol for this family."""
        return 'https'

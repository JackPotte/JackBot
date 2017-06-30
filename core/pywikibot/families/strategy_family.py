# -*- coding: utf-8 -*-
"""Family module for Wikimedia Strategy Wiki."""
#
# (C) Pywikibot team, 2009-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 054df6031c6756659bc26a72918655db4952a557 $'

from pywikibot import family


# The Wikimedia Strategy family
class Family(family.WikimediaOrgFamily):

    """Family class for Wikimedia Strategy Wiki."""

    name = 'strategy'

    def __init__(self):
        """Constructor."""
        super(Family, self).__init__()

        self.interwiki_forward = 'wikipedia'

    def dbName(self, code):
        """Return the database name for this family."""
        return 'strategywiki_p'

# -*- coding: utf-8 -*-
"""Family module for Incubator Wiki."""
#
# (C) Pywikibot team, 2006-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 266d5e7b7e225427f229267a811c7e883cae8e05 $'

from pywikibot import family


# The Wikimedia Incubator family
class Family(family.WikimediaOrgFamily):

    """Family class for Incubator Wiki."""

    name = 'incubator'

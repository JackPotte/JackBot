# -*- coding: utf-8 -*-
"""Family module for MediaWiki wiki."""
#
# (C) Pywikibot team, 2006-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 5fd30f497c158166479ff15ef56e636e9053b2ec $'

from pywikibot import family


# The MediaWiki family
class Family(family.WikimediaFamily, family.SingleSiteFamily):

    """Family module for MediaWiki wiki."""

    name = 'mediawiki'
    domain = 'www.mediawiki.org'

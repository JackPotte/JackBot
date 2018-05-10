# -*- coding: utf-8 -*-
"""Family module for LyricWiki."""
#
# (C) Pywikibot team, 2007-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: c4dc48ed9b6c45a6b3dd004fc987a37bbc94d392 $'

from pywikibot import family


# The LyricWiki family

# user_config.py:
# usernames['lyricwiki']['en'] = 'user'
class Family(family.SingleSiteFamily, family.WikiaFamily):

    """Family class for LyricWiki."""

    name = 'lyricwiki'
    code = 'en'
    domain = 'lyrics.wikia.com'

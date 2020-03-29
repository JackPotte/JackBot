#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals

try:
    # Bot Python 3.6 ?
    from lib.PageProvider import *
    from lib.defaultSort import *
    from lib.html2Unicode import *
    from lib.frWiktionaryTemplates import *
    from lib.hyperlynx import *
    from lib.languages import *
    from lib.pageFunctions import *
    from lib.WiktionaryPageFunctions import *
except ImportError as e:
    # Bot (Python 2.7.17)
    try:
        from PageProvider import *
        from defaultSort import *
        from html2Unicode import *
        from hyperlynx import *
        from languages import *
        from pageFunctions import *
        from WiktionaryPageFunctions import *
    except ImportError as e:
        # Unit test (Python 2.7.17 & 3.8)
        from src.lib.PageProvider import *
        from src.lib.defaultSort import *
        from src.lib.html2Unicode import *
        from src.lib.hyperlynx import *
        from src.lib.languages import *
        from src.lib.pageFunctions import *
        from src.lib.WiktionaryPageFunctions import *

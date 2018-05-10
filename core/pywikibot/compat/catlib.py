# -*- coding: utf-8 -*-
"""
WARNING: THIS MODULE EXISTS SOLELY TO PROVIDE BACKWARDS-COMPATIBILITY.

Do not use in new scripts; use the source to find the appropriate
function/method instead.

"""
#
# (C) Pywikibot team, 2008
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: 346850a0806cb1bf7bce4f8279c91bb2865b315d $'


from pywikibot import Category
from pywikibot.tools import ModuleDeprecationWrapper


def change_category(article, oldCat, newCat, comment=None, sortKey=None,
                    inPlace=True):
    """Change the category of the article."""
    return article.change_category(oldCat, newCat, comment, sortKey, inPlace)


__all__ = ('Category', 'change_category',)

wrapper = ModuleDeprecationWrapper(__name__)
wrapper._add_deprecated_attr('Category', replacement_name='pywikibot.Category')
wrapper._add_deprecated_attr('change_category', replacement_name='Page.change_category')

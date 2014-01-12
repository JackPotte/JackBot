#!/usr/bin/python
# -*- coding: utf-8     -*-
"""
Checks whether MediaWiki:Disambiguationpages exists on a site and compares it
with Family.disambiguationTemplates dictionary

"""
#
# (C) xqt 2013
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys
sys.path.insert(1, '..')
import pywikibot

DEFAULT = '_default'
MESSAGE = 'Disambiguationspage'


def check_disambig(f):
    print u'Processing %s family:' % f.name
    for k in sorted(f.disambiguationTemplates.keys()):
        isdefault = False
        if k == DEFAULT:
            continue
        print k + ':'
        site = pywikibot.getSite(k)
        try:
            default = set(site.family.disambig(DEFAULT))
        except KeyError:
            default = set([u'Disambig'])
        try:
            distl = set(f.disambig(k, fallback=False))
        except KeyError:
            distl = set()
        try:
            disambigpages = pywikibot.Page(site, MESSAGE, defaultNamespace=8)
            disambigs = set(link.title(withNamespace=False)
                            for link in disambigpages.linkedPages()
                            if link.namespace() == 10)
        except pywikibot.NoPage:
            isdefault = True
            message = site.mediawiki_message(MESSAGE).strip('{[]}').split(':',
                                                                          1)[1]
            disambigs = set([message[:1].upper() + message[1:]]) | default
        print 'Using default MediaWiki message:', isdefault
        if distl != disambigs:
            if disambigs - distl:
                l = list(disambigs - distl)
                pywikibot.output("missing on family file:\n[u'%s'],"
                                 % "', u'".join(l))
            if distl - disambigs:
                l = list(distl - disambigs)
                pywikibot.output("missing on MediaWiki message:\n%s"
                                 % ", ".join(l))
        else:
            pywikibot.output('remove %s from family file' % k)
        print
    else:
        print 'No disambiguationTemplates dictionary found'


def main(*args):
    for arg in pywikibot.handleArgs(*args):
        continue
    check_disambig(pywikibot.getSite().family)


if __name__ == "__main__":
    pywikibot.stopme()
    main()

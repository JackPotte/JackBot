#!/usr/bin/python
# -*- coding: utf-8     -*-
"""
This utility's primary use is to find all mismatches between the namespace
naming in the family files and the language files on the wiki servers.

You may use the following options:

-all       Run through all known languages in a family

-langs     Check comma-seperated languages. If neighter this option nor -all
           option is given, it checks the default language given by maylang in
           your user-config.py

-families  Check comma-seperated families

-wikimedia All Wikimedia families are checked


Examples:

    python testfamily.py -family:wiktionary -lang:en

    python testfamily.py -family:wikipedia -all -log:logfilename.txt

    python testfamily.py -families:wikipedia,wiktionary -langs:en,fr

    python testfamily.py -wikimedia -all

"""
#
# (C) Yuri Astrakhan, 2005
# (C) Pywikipedia bot team, 2006-2013
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys
sys.path.insert(1, '..')

import wikipedia as pywikibot
import traceback

def testSite(site):
    try:
        pywikibot.getall(site, [pywikibot.Page(site, 'Any page name')])
    except KeyboardInterrupt:
        raise
    except pywikibot.NoSuchSite:
        pywikibot.output( u'No such language %s' % site.lang )
    except:
        pywikibot.output( u'Error processing language %s' % site.lang )
        pywikibot.output( u''.join(traceback.format_exception(*sys.exc_info())))

def main():
    all = False
    language = None
    fam = None
    wikimedia = False
    for arg in pywikibot.handleArgs():
        if arg == '-all':
            all = True
        elif arg[0:7] == '-langs:':
            language = arg[7:]
        elif arg[0:10] == '-families:':
            fam = arg[10:]
        elif arg[0:10] == '-wikimedia':
            wikimedia = True

    mySite = pywikibot.getSite()
    if wikimedia:
        families = ['commons', 'incubator', 'mediawiki', 'meta', 'species',
                    'test', 'wikibooks', 'wikidata', 'wikinews', 'wikipedia',
                    'wikiquote', 'wikisource', 'wikiversity', 'wikivoyage',
                    'wiktionary']
    elif fam is not None:
        families = fam.split(',')
    else:
        families = [mySite.family.name,]

    for family in families:
        try:
            fam = pywikibot.Family(family)
        except ValueError:
            pywikibot.output(u'No such family %s' % family)
            continue
        if all:
            for lang in fam.langs.iterkeys():
                testSite(pywikibot.getSite(lang, family))
        elif language is None:
            lang = mySite.lang
            if not lang in fam.langs.keys():
                lang = fam.langs.keys()[-1]
            testSite(pywikibot.getSite(lang, family))
        else:
            languages = language.split(',')
            for lang in languages:
                try:
                    testSite(pywikibot.getSite(lang, family))
                except pywikibot.NoSuchSite:
                    pywikibot.output(u'No such language %s in family %s'
                                     % (lang, family))

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot tag tag files available at Commons with the Nowcommons template.
"""
#
# (C) Multichill, 2011
# (C) xqt, 2012
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys, re, urllib
import wikipedia as pywikibot
import pagegenerators
import image
#FIXME: Move these lists to commons_lib.py
from imagetransfer import nowCommonsTemplate
from nowcommons import nowCommons
from pywikibot import i18n


skips = {
    '_default': [u'NowCommons'],
    'wikipedia': {
        'en': [u'NowCommons',
               u'CommonsNow',
               u'Nowcommons',
               u'NowCommonsThis',
               u'Nowcommons2',
               u'NCT',
               u'Nowcommonsthis',
               u'Moved to commons',
               u'Now Commons',
               u'Now at commons',
               u'Db-nowcommons',
               u'WikimediaCommons',
               u'Now commons',
               u'Do not move to Commons',
               u'KeepLocal',
               u'Keeplocal',
               u'NoCommons',
               u'Nocommons',
               u'NotMovedToCommons',
               u'Nmtc',
               u'Not moved to Commons',
               u'Notmovedtocommons',
               ],
        'fy': [u'NowCommons',
               u'Nowcommons',
               ],
    },
}


class NoEnoughData(pywikibot.Error):
    """ Error class for when the user doesn't specified all the data needed """


def tagNowCommons(page):
    
    imagepage = pywikibot.ImagePage(page.site(), page.title())
    site = page.site()
    language = site.language()
    family = site.family.name
    
    if not imagepage.fileIsOnCommons():

        if family in skips and language in skips[family]:
            localskips = skips[family][language]
        else:
            localskips = skips['_default']
            
        for template in imagepage.templates():
            #FIXME: Move the templates list to a lib.
            if template in localskips:
                pywikibot.output(u'The file %s is already tagged with NowCommons' % imagepage.title())
                return

        imagehash = imagepage.getHash()
        commons = pywikibot.getSite(u'commons', u'commons')
        duplicates = commons.getFilesFromAnHash(imagehash)
        if duplicates:
            duplicate = duplicates.pop()
            pywikibot.output(u'Found duplicate image at %s' % duplicate)
            comment = i18n.twtranslate(imagepage.site(),
                                       'commons-file-now-available',
                                       {'localfile': imagepage.title(withNamespace=False),
                                        'commonsfile': duplicate})
            template = pywikibot.translate(imagepage.site(), nowCommonsTemplate)
            newtext = imagepage.get() + template % (duplicate,)
            pywikibot.showDiff(imagepage.get(), newtext)
            try:
                imagepage.put(newtext, comment)
            except wikipedia.LockedPage:
                return

def main(args):
    generator = None;
    always = False

    # Load a lot of default generators
    genFactory = pagegenerators.GeneratorFactory()

    for arg in pywikibot.handleArgs():
        genFactory.handleArg(arg)


    generator = genFactory.getCombinedGenerator()
    if not generator:
        raise NoEnoughData('You have to specify the generator you want to use for the script!')

    pregenerator = pagegenerators.PreloadingGenerator(generator)

    for page in pregenerator:
        if page.exists() and (page.namespace() == 6) and \
            (not page.isRedirectPage()):
            tagNowCommons(page)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        pywikibot.stopme()

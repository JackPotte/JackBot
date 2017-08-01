#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles de Wikilivres

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# Global variables
debugLevel = 0
debugAliases = ['debug', 'd', '-d']
for debugAlias in debugAliases:
    if debugAlias in sys.argv:
        debugLevel= 1
        sys.argv.remove(debugAlias)

fileName = __file__
if debugLevel > 0: print fileName
if fileName.rfind('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
siteLanguage = fileName[:2]
if debugLevel > 1: print siteLanguage
siteFamily = fileName[3:]
siteFamily = siteFamily[:siteFamily.find('.')]
if debugLevel > 1: print siteFamily
site = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

checkURL = False
fixTags = False
fixFiles = True
addCategory = True

def treatPageByName(pageName):
    if debugLevel > -1: print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatage'
    page = Page(site, pageName)
    PageBegin = getContentFromPage(page, 'All')
    if PageBegin == 'KO' or PageBegin.find(u'{{en travaux') != -1 or PageBegin.find(u'{{En travaux') != -1: return
    PageTemp = PageBegin
    PageEnd = u''

    PageTemp = globalOperations(PageTemp)
    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
    if checkURL: PageTemp = hyperlynx(PageTemp)

    # Templates
    oldTemplates = []
    oldTemplates.append(u'lienDePage') # TODO

    regex = ur'({{[a|A]utres projets[^}]*)\|noclear *= *1'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1', PageTemp)
    if debugLevel > 1: raw_input(PageTemp.encode(config.console_encoding, 'replace'))

    if page.namespace() == 0:
        # Traitement des modèles
        regex = ur'\{\{[P|p]ortail([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des portails'
            PageTemp = re.sub(regex, ur'', PageTemp)
        regex = ur'\{\{[P|p]alette([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des palettes'
            PageTemp = re.sub(regex, ur'', PageTemp)
        PageTemp = PageTemp.replace(u'{{PDC}}', u'profondeur de champ')
        PageTemp = PageTemp.replace(u'{{reflist}}', u'{{Références}}')
        PageTemp = PageTemp.replace(u'{{Reflist}}', u'{{Références}}')

        PageTemp = PageTemp.replace(u'[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'{{BookCat}}', u'{{AutoCat}}')
        if addCategory:
            if trim(PageTemp) != '' and PageTemp.find(u'[[Catégorie:') == -1 and PageTemp.find(u'{{AutoCat}}') == -1 and PageTemp.find(u'{{imprimable') == -1:
                PageTemp = PageTemp + u'\n\n{{AutoCat}}'

        regex = ur'\(*ISBN +([0-9\-]+)\)*'
        if re.search(regex, PageTemp):
            if debugLevel > 0: u'ISBN'
            PageTemp = re.sub(regex, ur'{{ISBN|\1}}', PageTemp)
            summary += ', ajout de {{ISBN}}'

        # Clés de tri pour les noms propres
        if PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
            PageTemp = PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie')] + PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
        '''ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
        regex = ur'()\n{{DEFAULTSORT[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'()\n{{defaultsort[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        '''

    PageEnd = PageEnd + PageTemp
    if PageEnd != PageBegin:
        PageTemp = PageTemp.replace(u'<references/>', u'{{Références}}')
        PageTemp = PageTemp.replace(u'<references />', u'{{Références}}')
        savePage(page, PageEnd, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test':
            treatPageByName(u'Utilisateur:' + username + u'/test')
        elif sys.argv[1] == u'-test2':
            treatPageByName(u'Utilisateur:' + username + u'/test2')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            treatPageByName(u'Catégorie:Python')
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.pagesByXML(siteLanguage + siteFamily + '.*xml', regex)
        elif sys.argv[1] == u'-u':
            p.pagesByUser(u'User:' + username)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'chinois')
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Modèle:autres projets')
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat':
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Catégorie:Python', afterPage = afterPage)
        elif sys.argv[1] == u'-redirects':
            p.pagesByRedirects()
        elif sys.argv[1] == u'-all':
           p.pagesByAll()
        elif sys.argv[1] == u'-RC':
            while 1:
                p.pagesByRCLastDay()
        elif sys.argv[1] == u'-nocat':
            p.pagesBySpecialNotCategorized()
        elif sys.argv[1] == u'-lint':
            p.pagesBySpecialLint()
        elif sys.argv[1] == u'-extlinks':
            p. pagesBySpecialLinkSearch('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        while 1:
            p.pagesByRC()

if __name__ == "__main__":
    main(sys.argv)

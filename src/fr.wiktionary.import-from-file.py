#!/usr/bin/env python
# coding: utf-8
# Ce script importe les définitions dans le Wiktionnaire depuis un fichier

from __future__ import absolute_import, unicode_literals
import re, sys
from lib import *
import pywikibot
from pywikibot import *

debugLevel = 0
debugAliases = ['-debug', '-d']
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
username = config.usernames[siteFamily][siteLanguage]
site = pywikibot.Site(siteLanguage, siteFamily)

languageCode = u'fr'
domain = u'{{cartographie|' + languageCode + u'}} '
reference = u'<ref>{{Import:CFC}}</ref>'
summary = u'Importation de définition CFC'
separator = u','
i = {}
i['Terme'] = 0
i['Terme ancien'] = 1           # O / N
i['Sigle'] = 2                  # O / N
i['Terme commercial'] = 3       # O / N
i['Catégorie grammaticale'] = 4 # adj. / n.m. / n.f.

i['Définition 1'] = 5
i['Domaine 1'] = 6              # toujours vide
i['Section 1'] = 7
i['Synonymes 1'] = 8
i['Exemples 1'] = 9
i['Termes associés 1'] = 10
i['Illustration 1'] = 11        # toujours vide
i['Commentaires 1'] = 12        # maintenance

i['Définition 2'] = 13
i['Domaine 2'] = 14
i['Section 2'] = 15
i['Synonymes 2'] = 16
i['Exemples 2'] = 17
i['Termes associés 2'] = 18
i['Illustration 2'] = 19
i['Commentaires 2'] = 20

i['Définition 3'] = 21
i['Domaine 3'] = 22
i['Section 3'] = 23
i['Synonymes 3'] = 24
i['Exemples 3'] = 25
i['Termes associés 3'] = 26
i['Illustration 3'] = 27
i['Commentaires 3'] = 28


def treatPage(line):
    l = line.split(separator)
    l = map(unicode.strip, l)
    pageName = l[i['Terme']]

    if pageName == '':
        if debugLevel > 0: print 'Ligne vide'
        return
    regex = ur' *(\([^\)]*\)) *'
    pageName = re.sub(regex, ur'', pageName)
    print(pageName.encode(config.console_encoding, 'replace'))
    return

    if l[i['Définition 1']] == '':
        if debugLevel > 0: print 'Définition vide'
        return

    page = Page(site, pageName.replace(u'’', u'\''))
    if not page.exists() and page.namespace() == 0:
        if debugLevel > 0: print u'Création d\'une redirection apostrophe'
        savePage(page, u'#REDIRECT[[' + pageName + ']]', u'Redirection pour apostrophe')
    page = Page(site, pageName)
    currentPageContent = getContentFromPage(page, 'All')
    if currentPageContent == 'KO':
        if debugLevel > 0: print u' Page vide'
        return
    pageContent = currentPageContent
    finalPageContent = u''

    if currentPageContent.find(domain) != -1:
        if debugLevel > 0: print u' Définition déjà présente'
        return

    definition = domain
    if l[i['Sigle']] != '': definition += l[i['Sigle']] # O / N
    if l[i['Catégorie grammaticale']] != '': definition += l[i['Catégorie grammaticale']] # adj. / n.m. / n.f
    if l[i['Terme ancien']] != '': definition += l[i['Terme ancien']] # O / N
    if l[i['Section 1']] != '': definition += l[i['Section 1']] # {{term|}}
    if l[i['Définition 1']] != '': definition += l[i['Définition 1']]
    if l[i['Exemples 1']] != '': definition += l[i['Exemples 1']]
    if l[i['Synonymes 1']] != '': definition += l[i['Synonymes 1']]
    if l[i['Termes associés 1']] != '': definition += l[i['Termes associés 1']]

    if debugLevel > 0: raw_input(definition)

    # Sauvegarde
    if finalPageContent != currentPageContent: savePage(page1, finalPageContent, summary)

def main(*args):
    from lib import html2Unicode
    pagesList = open(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'_CFC.csv', 'r')
    while 1:
        line = pagesList.readline().decode(config.console_encoding, 'replace')
        fin = line.find("\t")
        line = line[:fin]
        if line == '': break
        # Conversion ASCII => Unicode (pour les .txt)
        treatPage(html2Unicode(line))
    pagesList.close()

if __name__ == "__main__":
    main(sys.argv)

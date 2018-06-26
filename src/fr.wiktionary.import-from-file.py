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
etymology = u': {{cartographie|nocat=1}} {{sigle|fr}}'
if debugLevel > 0: 
    reference = u'<ref>{{Import:CFC}}</ref>'
else:
    reference = u'<ref>{{Import:CFC|relu=non}}</ref>'
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
i['Domaine 2'] = 14         # toujours vide
i['Section 2'] = 15
i['Synonymes 2'] = 16
i['Exemples 2'] = 17        # toujours vide
i['Termes associés 2'] = 18 # brouillon
i['Illustration 2'] = 19    # toujours vide
i['Commentaires 2'] = 20    # toujours vide

i['Définition 3'] = 21
i['Domaine 3'] = 22         # toujours vide
i['Section 3'] = 23         # toujours vide
i['Synonymes 3'] = 24       # toujours vide
i['Exemples 3'] = 25        # toujours vide
i['Termes associés 3'] = 26 # toujours vide
i['Illustration 3'] = 27    # toujours vide
i['Commentaires 3'] = 28    # toujours vide

natures = {}
natures[u'adj.'] = u'adjectif'
natures[u'n.m.'] = u'nom'
natures[u'n.f.'] = u'nom'


def treatPage(line):
    l = line.split(separator)
    l = map(unicode.strip, l)
    pageName = l[i['Terme']]

    if pageName == '':
        if debugLevel > 0: print 'Ligne vide'
        return
    regex = ur' *(\([^\)]*\)) *'
    pageName = re.sub(regex, ur'', pageName)
    pageName = pageName.replace(u'\'', u'’')
    print(pageName.encode(config.console_encoding, 'replace'))

    if l[i['Définition 1']] == '':
        if debugLevel > 0: print 'Définition vide'
        return

    if l[i['Catégorie grammaticale']] == '':
        if debugLevel > 0: print 'Nature vide'
        return
    nature = natures[l[i['Catégorie grammaticale']]]
    natureTemplate = u'{{S|' + nature + u'|fr'

    if pageName.find(u'’') != -1:
        page = Page(site, pageName.replace(u'’', u'\''))
        if not page.exists() and page.namespace() == 0:
            if debugLevel > 0: print u'Création d\'une redirection apostrophe'
            savePage(page, u'#REDIRECT[[' + pageName + ']]', u'Redirection pour apostrophe')
    page = Page(site, pageName)

    definition = u'# ' + domain
    if l[i['Terme ancien']] == 'O': definition += u'{{vieilli|fr}} '
    if l[i['Section 1']] != '': definition += u'{{term|' + l[i['Section 1']] + u'}} '
    definition += l[i['Définition 1']]
    if definition.count(u'"') == 1: definition = definition.replace(u'"', u'')
    if definition[-1:] == '.': definition = definition[:-1]
    definition += reference + u'.\n'
    if l[i['Exemples 1']] != '': definition += u"#* ''" + l[i['Exemples 1']] + u"''\n"

    if l[i['Définition 2']] != '':
        definition += u'# ' + domain
        if l[i['Terme ancien']] == 'O': definition += u'{{vieilli|fr}} '
        if l[i['Section 2']] != '': definition += u'{{term|' + l[i['Section 2']] + u'}} '
        definition += l[i['Définition 2']]
        if definition.count(u'"') == 1: definition = definition.replace(u'"', u'')
        if definition[-1:] == '.': definition = definition[:-1]
        definition += reference + u'.\n'
        if l[i['Exemples 2']] != '': definition += u"#* ''" + l[i['Exemples 2']] + u"''\n"

        if l[i['Définition 3']] != '':
            definition += u'# ' + domain
            if l[i['Terme ancien']] == 'O': definition += u'{{vieilli|fr}} '
            if l[i['Section 3']] != '': definition += u'{{term|' + l[i['Section 3']] + u'}} '
            definition += l[i['Définition 3']]
            if definition.count(u'"') == 1: definition = definition.replace(u'"', u'')
            if definition[-1:] == '.': definition = definition[:-1]
            definition += reference + u'.\n'
            if l[i['Exemples 3']] != '': definition += u"#* ''" + l[i['Exemples 3']] + u"''\n"

    currentPageContent = getContentFromPage(page, 'All')
    pageContent = currentPageContent
    finalPageContent = u''

    if currentPageContent == 'KO':
        if debugLevel > 0: print u' Page vide : création'
        pageContent = u'== {{langue|fr}} ==\n'
        pageContent += u'=== {{S|étymologie}} ===\n'
        pageContent += u'{{ébauche-étym|fr}}\n'
        if l[i['Sigle']] == 'O':
            pageContent += etymology + u'\n'
        pageContent += u'\n'
        pageContent += u'=== ' + natureTemplate + u'}} ===\n'
        pageContent += u"'''{{subst:PAGENAME}}'''"
        if l[i['Catégorie grammaticale']][-2:] == 'm.':
            pageContent += u' {{m}}'
        if l[i['Catégorie grammaticale']][-2:] == 'f.':
            pageContent += u' {{f}}'
        pageContent += u'\n' + definition.replace(u'  ', u', ')
        if l[i['Synonymes 1']] != '':
            pageContent += u'\n==== {{S|synonymes}} ====\n'
            synonyms = l[i['Synonymes 1']].split(u';')
            for s in synonyms:
                pageContent += u'* [[' + trim(s) + u']]\n'
            if l[i['Synonymes 2']] != '':
                synonyms = l[i['Synonymes 2']].split(u';')
                for s in synonyms:
                    pageContent += u'* [[' + trim(s) + u']] (2)\n'
        elif l[i['Synonymes 2']] != '':
            if l[i['Synonymes 2']] != '':
                synonyms = l[i['Synonymes 2']].split(u';')
                for s in synonyms:
                    pageContent += u'* [[' + trim(s) + u']] (2)\n'
        if l[i['Termes associés 1']] != '': 
            pageContent += u'\n==== {{S|vocabulaire}} ====\n'
            terms = l[i['Termes associés 1']].split(u';')
            for t in terms:
                print t
                pageContent += addLine(pageContent, languageCode, 'vocabulaire', u'* [[' + trim(t) + u']]')
        pageContent += u'\n==== {{S|traductions}} ====\n'
        pageContent += u'{{trad-début}}\n'
        pageContent += u'{{ébauche-trad}}\n'
        pageContent += u'{{trad-fin}}\n'
        pageContent += u'\n=== {{S|références}} ===\n'
        pageContent += u'{{Références}}\n'

        savePage(page, pageContent, summary)
        return

    if currentPageContent.find(domain) != -1 or currentPageContent.find(u'{{Import:CFC') != -1 or \
        pageName in ['cahier', 'couleurs complémentaires', 'demi-teintes', 'droits d’auteur']:
        if debugLevel > 0: print u' Définition déjà présente'
        return

    if l[i['Sigle']] == 'O': pageContent = addLine(pageContent, languageCode, 'étymologie', etymology)
    pageContent = addLine(pageContent, languageCode, nature, definition)
    if l[i['Synonymes 1']] != '':
        synonyms = l[i['Synonymes 1']].split(u';')
        for s in synonyms:
            pageContent = addLine(pageContent, languageCode, 'synonymes', u'* [[' + trim(s) + u']] {{cartographie|nocat=1}} (1)')
    if l[i['Synonymes 2']] != '':
        synonyms = l[i['Synonymes 2']].split(u';')
        for s in synonyms:
            pageContent = addLine(pageContent, languageCode, 'synonymes', u'* [[' + trim(s) + u']] {{cartographie|nocat=1}} (2)')
    if l[i['Termes associés 1']] != '':
        terms = l[i['Termes associés 1']].split(u';')
        for t in terms:
            pageContent = addLine(pageContent, languageCode, 'vocabulaire', u'* [[' + trim(t) + u']] {{cartographie|nocat=1}}')
    pageContent = addLine(pageContent, languageCode, 'références', u'{{Références}}')

    finalPageContent = pageContent
    if finalPageContent != currentPageContent: savePage(page, finalPageContent, summary)

setGlobals(debugLevel, site, username)
setGlobalsWiktionary(debugLevel, site, username)

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

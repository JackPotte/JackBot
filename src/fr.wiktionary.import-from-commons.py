#!/usr/bin/env python
# coding: utf-8
# Ce script importe les sons de Commons

# Importation des modules
from __future__ import absolute_import, unicode_literals
import re, sys
from lib import *
import pywikibot
from pywikibot import *

# Global variables
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
siteDest = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

site = pywikibot.Site(u'commons', u'commons')
summary = u'Ajout du son depuis [[commons:Category:Pronunciation]]'


def treatPageByName(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    if pageName[-4:] != u'.ogg' and pageName[-4:] != u'.oga' and pageName[-4:] != u'.wav': return

    mot = pageName[len(u'File:'):len(pageName)-4]
    if mot.find(u'-') == -1:
        if debugLevel > 0: print u' Son sans langue'
        return
    codelangue = mot[:mot.find(u'-')].lower()
    if debugLevel > 0: u'Mot de code langue : ' + codelangue
    if codelangue == u'qc': codelangue = u'fr'
    mot = mot[mot.find(u'-')+1:]
    mot = mot.replace(u'-',' ')
    mot = mot.replace(u'_',' ')
    mot = mot.replace(u'\'',u'’')
    if debugLevel > 1: print u' Mot de Commons : ' + mot.encode(config.console_encoding, 'replace')
    region = u''
    
    page1 = Page(siteDest, mot)
    try:
        PageBegin = page1.get()
    except pywikibot.exceptions.NoPage:
        # Retrait d'un éventuel article ou une région dans le nom du fichier
        mot1 = mot
                
        if codelangue == u'de':
            if mot[0:4] == u'der ' or mot[0:4] == u'die ' or mot[0:4] == u'das ' or mot[0:4] == u'den ':
                mot = mot[mot.find(u' ')+1:]
            if mot[0:3] == u'at ':
                region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
                mot = mot[mot.find(u' ')+1:]
                
        elif codelangue == u'en':
            if mot[0:4] == u'the ' or mot[0:2] == u'a ':
                mot = mot[mot.find(u' ')+1:]
            if mot[0:3] == u'au ' or mot[0:3] == u'gb ' or mot[0:3] == u'ca ' or mot[0:3] == u'uk ' or mot[0:3] == u'us ':
                region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
                mot = mot[mot.find(u' ')+1:]
            
        elif codelangue == u'es':
            if mot[0:3] == u'el ' or mot[0:3] == u'lo ' or mot[0:3] == u'la ' or mot[0:3] == u'un ' or mot[0:4] == u'uno ' or mot[0:4] == u'una ' or mot[0:5] == u'unos ' or mot[0:5] == u'unas ' or mot[0:4] == u'los ':
                mot = mot[mot.find(u' ')+1:]
            if mot[0:3] == u'mx ' or mot[0:3] == u'ar ':
                region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
                mot = mot[mot.find(u' ')+1:]
            if mot[0:7] == u'am lat ':
                region = u'{{AM|nocat=1}}'
                mot = mot[mot.find(u' ')+1:]
                mot = mot[mot.find(u' ')+1:]
                
        elif codelangue == u'fr':
            if mot[:3] == u'le ' or mot[:3] == u'la ' or mot[:4] == u'les ' or mot[:3] == u'un ' or mot[:3] == u'une ' or mot[:4] == u'des ':
                mot = mot[mot.find(u' ')+1:]
            if mot[:3] == u'ca ' or mot[:3] == u'be ':
                region = u'{{' + mot[:2].upper() + u'|nocat=1}}'
                mot = mot[mot.find(u' ')+1:]
            if mot[:6] == u'Paris ':
                region = u'Paris (France)'
                mot = mot[mot.find(u' ')+1:]
                
        elif codelangue == u'it':
            if mot[0:3] == u"l'" or mot[0:3] == u'la ' or mot[0:3] == u'le ' or mot[0:3] == u'lo ' or mot[0:4] == u'gli ' or mot[0:3] == u'un ' or mot[0:4] == u'uno ' or mot[0:4] == u'una ':
                mot = mot[mot.find(u' ')+1:]
        
        elif codelangue == u'nl':
            if mot[0:3] == u'de ' or mot[0:4] == u'een ' or mot[0:4] == u'het ':
                mot = mot[mot.find(u' ')+1:]
                            
        elif codelangue == u'pt':
            if mot[0:2] == u'a ' or mot[0:2] == u'o ' or mot[0:3] == u'as ' or mot[0:3] == u'os ':
                mot = mot[mot.find(u' ')+1:]
            if mot[0:3] == u'br ' or mot[0:3] == u'pt ':
                region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'

        elif codelangue == u'sv':
            if mot[0:3] == u'en ' or mot[0:4] == u'ett ':
                mot = mot[mot.find(u' ')+1:]                
        
        if debugLevel > 1: print u' Mot potentiel : ' + mot.encode(config.console_encoding, 'replace')
        # Deuxième tentative de recherche sur le Wiktionnaire    
        if mot != mot1:
            page1 = Page(siteDest, mot)
            try:
                PageBegin = page1.get()
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u' Page introuvable 1'
                return
            except pywikibot.exceptions.IsRedirectPage:
                PageBegin = page1.get(get_redirect=True)
        else:
            if debugLevel > 0: print u' Page introuvable 2'
            return
    except pywikibot.exceptions.IsRedirectPage:
        PageBegin = page1.get(get_redirect=True)
    # à faire : 3e tentative en retirant les suffixes numériques (ex : File:De-aber2.ogg)

    regex = ur'{{pron\|[^\}|]*\|' + codelangue + u'}}'
    if re.compile(regex).search(PageBegin):
        prononciation = PageBegin[re.search(regex,PageBegin).start()+len(u'{{pron|'):re.search(regex,PageBegin).end()-len(u'|'+codelangue+u'}}')]
    else:
        prononciation = u''
    if debugLevel > 1: print prononciation.encode(config.console_encoding, 'replace')
    
    if debugLevel > 1: print u' Mot du Wiktionnaire : ' + mot.encode(config.console_encoding, 'replace')
    Son = pageName[len(u'File:'):]
    if PageBegin.find(Son) != -1 or PageBegin.find(Son[:1].lower() + Son[1:]) != -1 or PageBegin.find(Son.replace(u' ', u'_')) != -1 or PageBegin.find((Son[:1].lower() + Son[1:]).replace(u' ', u'_')) != -1:
        if debugLevel > 0: print u' Son déjà présent'
        return
    if PageBegin.find(u'{{langue|' + codelangue) == -1:
        if debugLevel > 0: print u' Paragraphe absent'
        return
    PageTemp = PageBegin

    PageEnd = addLine(PageTemp, codelangue, u'prononciation', u'* {{écouter|' + region + u'|' + prononciation + u'|lang=' + codelangue + u'|audio=' + Son + u'}}')

    # Sauvegarde
    if PageEnd != PageBegin: savePage(page1, PageEnd, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
setGlobalsWiktionary(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'-test2':
            treatPageByName(u'User:' + username + u'/test2')
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
            p.pagesByLink(u'Template:autres projets')
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat':
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Category:German pronunciation of nouns', afterPage = afterPage)
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
        else:
            treatPageByName(sys.argv[1])
    else:
        p.pagesByCat(u'Category:Pronunciation', recursive = True, notCatNames = ['spoken ', 'Wikipedia', 'Wikinews'])

if __name__ == "__main__":
    main(sys.argv)

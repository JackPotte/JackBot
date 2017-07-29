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
siteDest = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

site = pywikibot.Site(u'commons', u'commons')
summary = u'Ajout du son depuis [[commons:Category:Pronunciation]]'

Sections = []
Niveau = []
Sections.append(u'étymologie')
Niveau.append(u'===')
Sections.append(u'nom')
Niveau.append(u'===')
Sections.append(u'variantes orthographiques')
Niveau.append(u'====')
Sections.append(u'synonymes')
Niveau.append(u'====')
Sections.append(u'antonymes')
Niveau.append(u'====')
Sections.append(u'dérivés')
Niveau.append(u'====')
Sections.append(u'apparentés')
Niveau.append(u'====')
Sections.append(u'vocabulaire')
Niveau.append(u'====')
Sections.append(u'hyperonymes')
Niveau.append(u'====')
Sections.append(u'hyponymes')
Niveau.append(u'====')
Sections.append(u'méronymes')
Niveau.append(u'====')
Sections.append(u'holonymes')
Niveau.append(u'====')
Sections.append(u'traductions')
Niveau.append(u'====')
Sections.append(u'prononciation')
Niveau.append(u'===')
Sections.append(u'homophones')
Niveau.append(u'====')
Sections.append(u'paronymes')
Niveau.append(u'====')
Sections.append(u'anagrammes')
Niveau.append(u'===')
Sections.append(u'voir aussi')
Niveau.append(u'===')
Sections.append(u'références')
Niveau.append(u'===')
Sections.append(u'catégorie')
Niveau.append(u'')
Sections.append(u'clé de tri')
Niveau.append(u'')

# Modification du wiki
def treatPageByName(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    if pageName[-4:] != u'.ogg' and pageName[-4:] != u'.oga' and pageName[-4:] != u'.wav': return

    mot = pageName[len(u'File:'):len(pageName)-4]
    if mot.find(u'-') == -1:
        if debugLevel > 0: print u'Son sans langue'
        return
    codelangue = mot[:mot.find(u'-')].lower()
    if debugLevel > 0: u'Mot de code langue : ' + codelangue
    if codelangue == u'qc': codelangue = u'fr'
    mot = mot[mot.find(u'-')+1:]
    mot = mot.replace(u'-',' ')
    mot = mot.replace(u'_',' ')
    mot = mot.replace(u'\'',u'’')
    if debugLevel > 1: print u'Mot de Commons : ' + mot.encode(config.console_encoding, 'replace')
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
        
        if debugLevel > 1: print u'Mot potentiel : ' + mot.encode(config.console_encoding, 'replace')
        # Deuxième tentative de recherche sur le Wiktionnaire    
        if mot != mot1:
            page1 = Page(siteDest, mot)
            try:
                PageBegin = page1.get()
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u'Page introuvable 1'
                return
            except pywikibot.exceptions.IsRedirectPage:
                PageBegin = page1.get(get_redirect=True)
        else:
            if debugLevel > 0: print u'Page introuvable 2'
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
    
    if debugLevel > 1: print u'Mot du Wiktionnaire : ' + mot.encode(config.console_encoding, 'replace')
    Son = pageName[len(u'File:'):]
    if PageBegin.find(Son) != -1 or PageBegin.find(Son[:1].lower() + Son[1:]) != -1 or PageBegin.find(Son.replace(u' ', u'_')) != -1 or PageBegin.find((Son[:1].lower() + Son[1:]).replace(u' ', u'_')) != -1:
        if debugLevel > 0: print u'Son déjà présent'
        return
    if PageBegin.find(u'{{langue|' + codelangue) == -1:
        if debugLevel > 0: print u'Paragraphe absent'
        return
    PageTemp = PageBegin

    PageEnd = addLine(PageTemp, codelangue, u'prononciation', u'* {{écouter|' + region + u'|' + prononciation + u'|lang=' + codelangue + u'|audio=' + Son + u'}}')

    # Sauvegarde
    if PageEnd != PageBegin: savePage(page1, PageEnd, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        DebutScan = u''
        if len(sys.argv) > 2:
            if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
                debugLevel = 1
            else:
                DebutScan = sys.argv[2]
        if sys.argv[1] == u'test':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'ta':
            testAdd(u'User:' + username + u'/test')
        elif sys.argv[1] == u'p':
            treatPageByName(u'File:De-Dominikanische Republik.ogg')
        elif sys.argv[1] == u'cat':
            p.pagesByCat2(u'Category:Pronunciation‎', True, u'')
        elif sys.argv[1] == u'lien':
            p.pagesByLink(u'Modèle:vx',u'')
        elif sys.argv[1] == u'page':
            treatPageByName(u'Utilisateur:JackPotte/test2')
        elif sys.argv[1] == u'trad':
            p.pagesByLink(u'Modèle:trad-',u'')
        elif sys.argv[1] == u's':
            p.pagesBySearch(u'File:fr-Paris--')    # à faire : renommer les "File:Fr-œsophagienne-fr FR-Paris.ogg" avec "{{rename|Fr-Paris--œsophagienne.ogg|4|Pronunciation norm for Wiktionaries sync}}"
        elif sys.argv[1] == u'u':
            p.pagesByUser(u'Utilisateur:JackPotte', 1000,u'')
    else:
        p.pagesByCat2(u'Category:Pronunciation', True, u'')

'''
    p.pagesByCat2(u'Category:U.S. English pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:German pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Arabic pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Armenian pronunciation‎‎', True, u'')
    p.pagesByCat2(u'Category:Belarusian pronunciation‎‎‎', True, u'')
    p.pagesByCat2(u'Category:Chinese pronunciation‎‎‎‎', True, u'')
    p.pagesByCat2(u'Category:Czech pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Hungarian pronunciation‎‎', True, u'')
    p.pagesByCat2(u'Category:Swedish pronunciation‎‎‎', True, u'')
    p.pagesByCat2(u'Category:Ukrainian pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Russian pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Polish pronunciation‎‎', True, u'')
    p.pagesByCat2(u'Category:Dutch pronunciation‎‎‎‎‎', True, u'')
    p.pagesByCat2(u'Category:French pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:Spanish pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:English pronunciation‎', True, u'')
    p.pagesByCat2(u'Category:British English pronunciation‎', True, u'')

 TODO :
    Insérer avant les clés de tri : https://fr.wiktionary.org/w/index.php?title=Orthop%C3%A4de&diff=prev&oldid=21702612
    pb avec p.pagesBycat non récursif Commons (test l 333). Ex : ne traite que les "a*" de [[Catégorie:French pronunciations]]
    try save except service unavailable, wait
    niveau de récursivité limite
    ignorer [[Category:Ogg sound files of spoken French]] ou Wikinews, Wikipedia

'''

if __name__ == "__main__":
    main(sys.argv)

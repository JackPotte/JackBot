#!/usr/bin/env python
# coding: utf-8
# Ce script importe les sons de Commons dans le Wiktionnaire en français

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
siteDest = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

site = pywikibot.Site(u'commons', u'commons')
summary = u'Ajout du son depuis [[commons:Category:Pronunciation]]'


def treatPageByName(pageName):
    print pageName.encode(config.console_encoding, 'replace')
    if username in pageName:
        fileName = u'LL-Q143 (epo)-Robin van der Vliet-lipharoj.wav'
    else:
        if pageName[-4:] != u'.ogg' and pageName[-4:] != u'.oga' and pageName[-4:] != u'.wav':
            if debugLevel > 0: print u' No supported file format found'
            return
        fileName = pageName
        if pageName.find(u'File:') == 0: fileName = fileName[len(u'File:'):]
    fileDesc = fileName[:-len(u'.ogg')]

    if fileDesc.find(u'-') == -1:
        if debugLevel > 0: print u' No language code found'
        return

    languageCode = fileDesc[:fileDesc.find(u'-')]
    if languageCode == 'LL':
        if debugLevel > 0: print u' Lingua Libre formats'
        # LL-<Qid de la langue> (<code iso 693-3>)-<Username>-<transcription> (<précision>).wav

        if fileDesc.count('-') > 3:
            if debugLevel > 0: print u' Compound word'
            word = fileDesc
            for i in range(3):
                word = word[word.find(u'-')+1:]
        else:
            word = fileDesc[fileDesc.rfind(u'-')+1:]

        s = re.search(ur'\(([^\)]+)\)', fileDesc)
        if s:
            languageCode = getLanguageCodeISO693_1FromISO693_3(s.group(1))
        else:
            if debugLevel > 0: print u' No parenthesis found'
            s = re.search(ur'\-([^\-]+)\-[^\-]+$', fileDesc)
            if not s:
                if debugLevel > 0: print u' No language code found'
                return
            languageCode = getLanguageCodeISO693_1FromISO693_3(s.group(1))

    else:
        languageCode = languageCode.lower()
        if languageCode == u'qc': languageCode = u'fr'
        word = fileDesc[fileDesc.find(u'-')+1:]
        word = word.replace(u'-',' ')
        word = word.replace(u'_',' ')
        word = word.replace(u'\'',u'’')

    if debugLevel > 0:
        print u' Language code: ' + languageCode
        print u' Word: ' + word

    region = u''
    if username in pageName:
        page1 = Page(siteDest, pageName)
    else:
        page1 = Page(siteDest, word)
    try:
        currentPageContent = page1.get()
    except pywikibot.exceptions.NoPage:
        # Retrait d'un éventuel article ou une région dans le nom du fichier
        word1 = word

        if languageCode == u'de':
            if word[0:4] == u'der ' or word[0:4] == u'die ' or word[0:4] == u'das ' or word[0:4] == u'den ':
                word = word[word.find(u' ')+1:]
            if word[0:3] == u'at ':
                region = u'{{' + word[0:2].upper() + u'|nocat=1}}'
                word = word[word.find(u' ')+1:]
                
        elif languageCode == u'en':
            if word[0:4] == u'the ' or word[0:2] == u'a ':
                word = word[word.find(u' ')+1:]
            if word[0:3] == u'au ' or word[0:3] == u'gb ' or word[0:3] == u'ca ' or word[0:3] == u'uk ' or word[0:3] == u'us ':
                region = u'{{' + word[0:2].upper() + u'|nocat=1}}'
                word = word[word.find(u' ')+1:]
            
        elif languageCode == u'es':
            if word[0:3] == u'el ' or word[0:3] == u'lo ' or word[0:3] == u'la ' or word[0:3] == u'un ' or word[0:4] == u'uno ' or word[0:4] == u'una ' or word[0:5] == u'unos ' or word[0:5] == u'unas ' or word[0:4] == u'los ':
                word = word[word.find(u' ')+1:]
            if word[0:3] == u'mx ' or word[0:3] == u'ar ':
                region = u'{{' + word[0:2].upper() + u'|nocat=1}}'
                word = word[word.find(u' ')+1:]
            if word[0:7] == u'am lat ':
                region = u'{{AM|nocat=1}}'
                word = word[word.find(u' ')+1:]
                word = word[word.find(u' ')+1:]
                
        elif languageCode == u'fr':
            if word[:3] == u'le ' or word[:3] == u'la ' or word[:4] == u'les ' or word[:3] == u'un ' or word[:3] == u'une ' or word[:4] == u'des ':
                word = word[word.find(u' ')+1:]
            if word[:3] == u'ca ' or word[:3] == u'be ':
                region = u'{{' + word[:2].upper() + u'|nocat=1}}'
                word = word[word.find(u' ')+1:]
            if word[:6] == u'Paris ':
                region = u'Paris (France)'
                word = word[word.find(u' ')+1:]
                
        elif languageCode == u'it':
            if word[0:3] == u"l'" or word[0:3] == u'la ' or word[0:3] == u'le ' or word[0:3] == u'lo ' or word[0:4] == u'gli ' or word[0:3] == u'un ' or word[0:4] == u'uno ' or word[0:4] == u'una ':
                word = word[word.find(u' ')+1:]
        
        elif languageCode == u'nl':
            if word[0:3] == u'de ' or word[0:4] == u'een ' or word[0:4] == u'het ':
                word = word[word.find(u' ')+1:]
                            
        elif languageCode == u'pt':
            if word[0:2] == u'a ' or word[0:2] == u'o ' or word[0:3] == u'as ' or word[0:3] == u'os ':
                word = word[word.find(u' ')+1:]
            if word[0:3] == u'br ' or word[0:3] == u'pt ':
                region = u'{{' + word[0:2].upper() + u'|nocat=1}}'

        elif languageCode == u'sv':
            if word[0:3] == u'en ' or word[0:4] == u'ett ':
                word = word[word.find(u' ')+1:]                
        
        if debugLevel > 1: print u' Mot potentiel : ' + word.encode(config.console_encoding, 'replace')
        # Deuxième tentative de recherche sur le Wiktionnaire    
        if word != word1:
            page1 = Page(siteDest, word)
            try:
                currentPageContent = page1.get()
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u' Page not found 1'
                return
            except pywikibot.exceptions.IsRedirectPage:
                currentPageContent = page1.get(get_redirect=True)
        else:
            if debugLevel > 0: print u' Page not found 2'
            return
    except pywikibot.exceptions.IsRedirectPage:
        currentPageContent = page1.get(get_redirect=True)
    # à faire : 3e tentative en retirant les suffixes numériques (ex : File:De-aber2.ogg)

    prononciation = u''
    '''
    TODO: getPronunciationFromArticle()
    regex = ur'{{pron\|[^\}|]*\|' + languageCode + u'}}'
    if re.compile(regex).search(currentPageContent):
        prononciation = currentPageContent[re.search(regex, currentPageContent).start()+len(u'{{pron|'):re.search(regex,currentPageContent).end()-len(u'|'+languageCode+u'}}')]
    if debugLevel > 1: print prononciation.encode(config.console_encoding, 'replace')
    
    TODO: getUserRegion()
    '''

    if debugLevel > 1: print u' Mot du Wiktionnaire : ' + word.encode(config.console_encoding, 'replace')
    if currentPageContent.find(u'{{langue|' + languageCode) == -1:
        if debugLevel > 0: print u' Language section absent'
        return

    if fileName[:1].lower() == fileName[:1]:
        fileNameCap = fileName[:1].upper() + fileName[1:]
    else:
        fileNameCap = fileName[:1].lower() + fileName[1:]
    if fileName in currentPageContent or fileNameCap in currentPageContent or \
        fileName.replace(u' ', u'_') in currentPageContent or fileNameCap.replace(u' ', u'_') in currentPageContent:
        if debugLevel > 0: print u' File already present'
        if debugLevel > 1: raw_input(currentPageContent.encode(config.console_encoding, 'replace'))
        return

    pageContent = currentPageContent
    finalPageContent = addPronunciation(pageContent, languageCode, u'prononciation', u'* {{écouter|' + region + u'|' + prononciation + u'|lang=' + languageCode + u'|audio=' + fileName + u'}}')
    if finalPageContent is not None:
        # Hardfixes
        regex = ur'{{S\|prononciation}} ===\*'
        if re.search(regex, finalPageContent):
            finalPageContent = re.sub(regex, ur'{{S|prononciation}} ===\n*', finalPageContent)
        regex = ur'\n\n+(\* {{écouter\|)'
        if re.search(regex, finalPageContent):
            finalPageContent = re.sub(regex, ur'\n\1', finalPageContent)

        if finalPageContent != currentPageContent:
            savePage(page1, finalPageContent, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
setGlobalsWiktionary(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test' or sys.argv[1] == u'-t':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'-test2' or sys.argv[1] == u'-tu':
            treatPageByName(u'User:' + username + u'/test unitaire')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            if len(sys.argv) > 2:
                sound = sys.argv[2]
            else:
                sound = u'File:LL-Q150 (fra)-Pamputt-suivant.wav'
            treatPageByName(sound)
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.pagesByXML(siteLanguage + siteFamily + '\-.*xml', regex)
        elif sys.argv[1] == u'-u':
            p.pagesByUser(u'User:' + username)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'chinois')
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Template:autres projets')
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat' or sys.argv[1] == u'-c':
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Canadian English pronunciation', afterPage = afterPage, recursive = True, namespaces = [6])
            p.pagesByCat(u'Australian English pronunciation', afterPage = afterPage, recursive = True, namespaces = [6])
            p.pagesByCat(u'British English pronunciation', afterPage = afterPage, recursive = True, namespaces = [6])
            p.pagesByCat(u'U.S. English pronunciation‎', afterPage = afterPage, recursive = True, namespaces = [6])
            #Bug: too long? p.pagesByCat(u'Lingua Libre pronunciation-fr', afterPage = afterPage, recursive = True, namespaces = [6])
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
        p.pagesByCat(u'Category:Pronunciation', recursive = True, notNames = ['spoken ', 'Wikipedia', 'Wikinews'])

if __name__ == "__main__":
    main(sys.argv)

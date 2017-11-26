#!/usr/bin/env python
# coding: utf-8
# Ce script importe les flexions d'un Wiktionary dans un autre où le lemme se trouve

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

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
site = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

addDefaultSort = False
siteSource = pywikibot.Site('en', siteFamily)
templateSource = u'en-past of'
textTranslated = u'Passé de'
DebutScan = u'interspersed'
# TODO pluriels fr + en


def treatPageByName(pageName):
    if debugLevel > 0: print u'------------------------------------'
    print(pageName.encode(config.console_encoding, 'replace'))
    page = Page(site, pageName)
    if not hasMoreThanTime(page, 1440): return
    if page.exists():
        if page.namespace() != 0 and page.title() != u'User:JackBot/test':
            print u' Autre namespace l 45'
            return
    else:
        print u' Page inexistante'
        return
    PageSing = getContentFromPage(page, 'All')
    if PageSing.find(u'{{formater') != -1 or PageSing.find(u'{{SI|') != -1 or PageSing.find(u'{{SI}}') != -1 or \
        PageSing.find(u'{{supp|') != -1 or PageSing.find(u'{{supp}}') != -1 or PageSing.find(u'{{supprimer|') != -1 or \
        PageSing.find(u'{{supprimer') != -1 or PageSing.find(u'{{PàS') != -1 or PageSing.find(u'{{S|faute') != -1 or \
        PageSing.find(u'{{S|erreur') != -1:
        if debugLevel > 0: print u'Page en travaux : non traitée l 65'
        return

    template = [] # Liste des modèles du site à traiter
    param  = [] # paramètre du lemme associé
    template.append(u'fr-rég-x')
    param.append(u's')
    template.append(u'fr-rég')
    param.append(u's')
    template.append(u'fr-accord-cons')
    param.append(u'ms')
    #TODO: ajouter Catégorie:Modèles d’accord en français
    template.append(u'fr-accord-eur')
    param.append(u'1')

    for m in range(0, len(template)):
        languageCode = template[m][:2]
        # Parcours de la page pour chaque modèle
        if debugLevel > 1: print ' début du for ' + str(m) + u', recherche du modèle : ' + template[m]
        if PageSing.find(template[m] + u'|') == -1 and PageSing.find(template[m] + u'}') == -1:
            if debugLevel > 1: pywikibot.output(u' Modèle : \03{blue}' + template[m] + u'\03{default} absent')
            continue
        else:
            if debugLevel > 0: pywikibot.output(u' Modèle : \03{blue}' + template[m] + u'\03{default} trouvé')
            pageContent = PageSing
        
        while pageContent.find(template[m]) != -1:
            if len(template[m]) < 3:
                if debugLevel > 0: print u' bug'
                break
            if debugLevel > 1: 
                print template[m].encode(config.console_encoding, 'replace')
                print pageContent.find(template[m])
                
            # Parcours de la page pour chaque occurence du modèle
            nature = pageContent[:pageContent.find(template[m])]
            nature = nature[nature.rfind(u'{{S|')+len(u'{{S|'):]
            nature = nature[:nature.find(u'|')]
            if debugLevel > 0:
                try:
                    print u'  Nature : ' + nature.encode(config.console_encoding, 'replace')
                except UnicodeDecodeError:
                    print u'  Nature à décoder'
                except UnicodeEncodeError:
                    print u'  Nature à encoder'
            if nature == u'erreur' or nature == u'faute':
                print u'  section erreur'
                return
                
            pageContent = pageContent[pageContent.find(template[m])+len(template[m]):]
            suffix = getParameter(pageContent, u'inv')
            singular = getParameter(pageContent, u's')
            plural = u''
            if suffix != u'':
                if singular == u'':
                    if debugLevel > 0: print u'  inv= sans s='
                    break
                plural = singular + u's ' + suffix
                singular = singular + u' ' + suffix
            elif singular != u'' and singular != pageName:
                if debugLevel > 0:
                    print u'  s= ne correspond pas'
                    print singular.encode(config.console_encoding, 'replace')
                break

            pron = getPronunciationFromContent(pageContent, languageCode)
            if debugLevel > 0: raw_input(pron)
            if pageContent.find(u'|pp=') != -1 and pageContent.find(u'|pp=') < pageContent.find(u'}}'):
                if debugLevel > 0: print ' pp='
                pageContent2 = pageContent[pageContent.find(u'|pp=')+4:pageContent.find(u'}}')]
                if pageContent2.find(u'|') != -1:
                    pron = pageContent[pageContent.find(u'|pp=')+4:pageContent.find(u'|pp=')+4+pageContent2.find(u'|')]
                else:
                    pron = pageContent[pageContent.find(u'|pp=')+4:pageContent.find(u'}}')]
            else:
                if debugLevel > 1: print '  prononciation identique au singulier'
                pron = pageContent[:pageContent.find(u'}}')]
                if debugLevel > 1: print u'  pron avant while : ' + pron.encode(config.console_encoding, 'replace')
                if pron.find(u'|pron=') != -1:
                    pron = u'|' + pron[pron.find(u'|pron=')+len(u'|pron='):]
                
                TabPron = pron.split(u'|')
                # {{fr-rég|a.kʁɔ.sɑ̃.tʁik|mf=oui}}
                n = 0
                while n < len(TabPron) and (TabPron[n] == '' or TabPron[n].find(u'=') != -1):
                    if debugLevel > 1: print TabPron[n].find(u'=')
                    n += 1
                if n == len(TabPron):
                    pron = u'|'
                else:
                    pron = u'|' + TabPron[n]
                '''
                while pron.find(u'=') != -1:
                    pron2 = pron[:pron.find(u'=')]
                    pron3 = pron[pron.find(u'='):]
                    if debugLevel > 0: print u'  pron2 : ' + pron2.encode(config.console_encoding, 'replace')
                    if pron2.find(u'|') == -1:
                        pron = pron[pron.find(u'|')+1:]
                        if debugLevel > 1: print u'  pron dans while1 : ' + pron.encode(config.console_encoding, 'replace')
                    else:
                        if debugLevel > 0: print u'  pron3 : ' + pron3.encode(config.console_encoding, 'replace')
                        if pron3.rfind(u'|') == -1:
                            limitPron = len(pron3)
                        else:
                            limitPron = pron3.rfind(u'|')
                        if debugLevel > 0: print u'  limitPron : ' + str(limitPron)
                        pron = pron[pron.find(u'=')+limitPron:]
                        if debugLevel > 0: print u'  pron dans while2 : ' + pron.encode(config.console_encoding, 'replace')
                '''
                if debugLevel > 1: print u'  pron après while : ' + pron.encode(config.console_encoding, 'replace')
            pron = trim(pron)
            if pron.rfind(u'|') > 0:
                pronM = pron[:pron.rfind(u'|')]
                while pronM.rfind(u'|') > 0:
                    pronM = pronM[:pronM.rfind(u'|')]
            else:
                pronM = pron
            if pronM[:1] != u'|': pronM = u'|' + pronM
            if debugLevel > 0:
                try:
                    print u'  Prononciation : ' + pronM.encode(config.console_encoding, 'replace')
                except UnicodeDecodeError:
                    print u'  Prononciation à décoder'
                except UnicodeEncodeError:
                    print u'  Prononciation à encoder'
            
            # h aspiré
            H = u''
            if pageContent.find(u'|prefpron={{h aspiré') != -1 and pageContent.find(u'|prefpron={{h aspiré') < pageContent.find(u'}}'):
                H = u'|prefpron={{h aspiré}}'
            if pageContent.find(u'|préfpron={{h aspiré') != -1 and pageContent.find(u'|préfpron={{h aspiré') < pageContent.find(u'}}'):
                H = u'|préfpron={{h aspiré}}'
            # gender
            gender = u''
            pageContent2 = pageContent[pageContent.find(u'\n')+1:len(pageContent)]
            while pageContent2[:1] == u'[' or pageContent2[:1] == u'\n' and len(pageContent2) > 1:
                pageContent2 = pageContent2[pageContent2.find(u'\n')+1:len(pageContent2)]
            if pageContent2.find(u'{{m}}') != -1 and pageContent2.find(u'{{m}}') < pageContent2.find(u'\n'): gender = u' {{m}}'    
            if pageContent2.find(u'{{f}}') != -1 and pageContent2.find(u'{{f}}') < pageContent2.find(u'\n'): gender = u' {{f}}'
            MF = u''
            if pageContent2.find(u'{{mf}}') != -1 and pageContent2.find(u'{{mf}}') < pageContent2.find(u'\n'):
                gender = u' {{mf}}'
                MF = u'|mf=oui'
                if PageSing.find(u'|mf=') == -1:
                    PageSing = PageSing[:PageSing.find(template[m])+len(template[m])] + u'|mf=oui' + PageSing[PageSing.find(template[m])+len(template[m]):]
                    savePage(page, PageSing, u'|mf=oui')
            if pageContent.find(u'|mf=') != -1 and pageContent.find(u'|mf=') < pageContent.find(u'}}'): MF = u'|mf=oui' 
            # Pluriel
            summary = u'Création du pluriel de [[' + pageName + u']]'
            if plural == u'':
                if (pageContent.find(u'|p=') != -1 and pageContent.find(u'|p=') < pageContent.find(u'}}')):
                    plural = pageContent[pageContent.find(u'|p=')+3:pageContent.find(u'}}')]
                    if plural.find(u'|') != -1: plural = plural[:plural.find(u'|')]
                if not plural:
                    if template[m][-1:] == u'x':
                        plural = pageName + u'x'
                    else:
                        plural = pageName + u's'
                if (plural[-2:] == u'ss' or plural.find(u'{') != -1) and suffix == u'':
                    print u' pluriel en -ss'
                    return
                if debugLevel > 1:
                    print '  paramètre du modèle du lemme : ' + pageContent[:pageContent.find(u'}}')].encode(config.console_encoding, 'replace')
            
            page2 = Page(site, plural)
            if page2.exists():
                pluralPage = getContentFromPage(page2)
                if pluralPage.find(u'{{langue|' + languageCode + u'}}') != -1:
                    if debugLevel > 0: print u'  Pluriel existant l 216 : ' + plural
                    break
            else:
                if debugLevel > 0: print u'  Pluriel introuvable l 219'
                pluralPage = u''

            # **************** Pluriel 1 ****************
            if debugLevel > 1: print u'  Pluriel n°1'
            if plural[-2:] == u'xs':
                print u' Pluriel en xs : erreur'
                return
            elif plural[-2:] == u'ss':
                lemmaParam = u'|' + param[m] + u'=' + plural[:-2]
                PageSing = PageSing[:PageSing.find(template[m])+len(template[m])] + lemmaParam + \
                    PageSing[PageSing.find(template[m])+len(template[m]):]
                savePage(page, PageSing, u'{{' + template[m] + u'|s=...}}')
                break
            elif param[m] == '1':
                lemmaParam = ''
            else:
                lemmaParam = '|' + param[m] + u'=' + pageName

            flexionTemplate = u'{{' + template[m] + pronM + H + MF + lemmaParam
            if plural != pageName + u's' and plural != pageName + u'x':
                flexionTemplate += u'|p={{subst:PAGENAME}}'
            flexionTemplate += u'}}'

            PageEnd = u'== {{langue|' + languageCode + u'}} ==\n=== {{S|' + nature + u'|' + \
                languageCode + u'|flexion}} ===\n' + flexionTemplate + u'\n\'\'\'' + plural + u'\'\'\' {{pron' + pronM + \
                '|' + languageCode + u'}}' + gender + u'\n# \'\'Pluriel de\'\' [[' + pageName +']].\n'
            while PageEnd.find(u'{{pron|' + languageCode + u'}}') != -1:
                PageEnd = PageEnd[:PageEnd.find(u'{{pron|' + languageCode + u'}}')+7] + u'|' + \
                    PageEnd[PageEnd.find(u'{{pron|' + languageCode + u'}}')+7:]
            PageEnd = PageEnd + u'\n' + pluralPage

            CleTri = defaultSort(plural)
            if addDefaultSort:
                if PageEnd.find(u'{{clé de tri') == -1 and CleTri != u'' and CleTri.lower() != plural.lower():
                    PageEnd = PageEnd +  u'\n{{clé de tri|' + CleTri + u'}}\n'
            PageEnd = html2Unicode(PageEnd)
            savePage(page2, PageEnd, summary)

            # TODO: pluriel n°2
            #raw_input(pageContent.encode(config.console_encoding, 'replace'))
            if debugLevel > 1: print u'  Fin du while'
        if debugLevel > 1: print u' Fin du for ' + str(m)


def createPluralFromForeignWiki(Page2):
    page2 = Page(siteSource, Page2)
    page1 = Page(site,Page2)
    if debugLevel > 0: print Page2.encode(config.console_encoding, 'replace')
    if page2.exists() and page2.namespace() == 0 and not page1.exists():
        pageContent = getPage(page2)
        if pageContent == u'': return
        # Nature grammaticale
        pageContent2 = pageContent[:pageContent.find(templateSource)]
        # Code langue
        pageContent = pageContent[pageContent.find(templateSource)+len(templateSource)+1:len(pageContent)]
        if pageContent.find("lang=") != -1 and pageContent.find("lang=") < pageContent.find(u'}}'):
            pageContent2 = pageContent[pageContent.find("lang=")+5:len(pageContent)]
            if pageContent2.find(u'|') != -1 and pageContent2.find(u'|') < pageContent2.find(u'}}'):
                languageCode = pageContent2[:pageContent2.find("|")]
                pageContent = pageContent[:pageContent.find("lang=")] + pageContent[pageContent.find("lang=")+5+pageContent2.find("|"):]
            else:
                languageCode = pageContent2[:pageContent2.find("}}")]
                pageContent = pageContent[:pageContent.find("lang=")] + pageContent[pageContent.find("lang=")+5+pageContent2.find("}"):]
            if languageCode == u'': languageCode = u'en'
            elif languageCode == u'Italian': languageCode = u'it'
            elif languageCode == u'Irish': languageCode = u'ga'
            elif languageCode == u'German': languageCode = u'de'
            elif languageCode == u'Middle English': languageCode = u'enm'
            elif languageCode == u'Old English': languageCode = u'ang'
            elif languageCode == u'Dutch': languageCode = u'nl'
            elif languageCode == u'Romanian': languageCode = u'ro'
            elif languageCode == u'Spanish': languageCode = u'es'
            elif languageCode == u'Catalan': languageCode = u'ca'
            elif languageCode == u'Portuguese': languageCode = u'pt'
            elif languageCode == u'Russian': languageCode = u'ru'
            elif languageCode == u'French': languageCode = u'fr'
            elif languageCode == u'Scots': languageCode = u'sco'
            elif languageCode == u'Chinese': languageCode = u'zh'
            elif languageCode == u'Mandarin': languageCode = u'zh'
            elif languageCode == u'Japanese': languageCode = u'ja'
        else:
            languageCode = u'en'
        #if debugLevel > 0: print u' ' + languageCode
        
        while pageContent[:1] == u' ' or pageContent[:1] == u'|':
            pageContent = pageContent[1:len(pageContent)]
        # Lemme
        if pageContent.find(u']]') != -1 and pageContent.find(u']]') < pageContent.find(u'}}'): # Si on est dans un lien
            mot = pageContent[:pageContent.find(u']]')+2]
        elif pageContent.find(u'|') != -1 and pageContent.find(u'|') < pageContent.find(u'}}'):
            mot = pageContent[:pageContent.find(u'|')]
            # A faire : si dièse on remplace en même temps que les languageCode ci-dessous, à patir d'un tableau des langues
        else:
            mot = pageContent[:pageContent.find(u'}}')]
        if mot[:2] != u'[[': mot = u'[[' + mot + u']]'
        
        # On ne crée que les flexions des lemmes existant
        page3 = Page(site, mot[2:-2])
        if page3.exists() == u'False':
            print 'Page du lemme absente du Wiktionnaire'
            return
        PageLemme = getPage(page3)
        if PageLemme == u'': return
        if PageLemme.find(u'{{langue|' + languageCode + u'}}') == -1:
            print ' Paragraphe du lemme absent du Wiktionnaire'
            return
        else:
            # Prononciation
            pron = u''
            PageLemme = PageLemme[PageLemme.find(u'{{langue|' + languageCode + u'}}'):]
            if debugLevel > 1: raw_input(PageLemme.encode(config.console_encoding, 'replace'))

            p = re.compile(ur'{{pron\|([^}]+)\|en}}')
            result = p.findall(PageLemme)
            if len(result) > 0:
                if debugLevel > 0: print u' à partir de {{pron}}'
                r = 0
                while result[r] == u'' and r < len(result):
                    r += 1
                pron = result[r]

            elif PageLemme.find(u'{{en-conj-rég') != -1:
                if debugLevel > 0: print u' à partir de {{en-conj-rég'
                pron = PageLemme[PageLemme.find(u'{{en-conj-rég')+len(u'{{en-conj-rég'):]
                if pron.find(u'|inf.pron=') != -1 and pron.find(u'|inf.pron=') < pron.find(u'}}'):
                    pron = pron[pron.find(u'|inf.pron=')+len(u'|inf.pron='):]
                    if pron.find(u'}}') < pron.find(u'|') or pron.find(u'|') == -1:
                        pron = pron[:pron.find(u'}}')]
                    else:
                        pron = pron[:pron.find(u'|')]
                else:
                    pron = u''

            if pron != '':
                # Suffixe du -ed
                letter = pron[-1:]
                if letter in (u'f', u'k', u'p', u'θ', u's', u'ʃ'):
                    pron = pron + u't'
                elif letter in (u't', u'd'):
                    pron = pron + u'ɪd' 
                else:
                    pron = pron + u'd'
            if debugLevel > 0: print u' prononciation : ' + pron #.encode(config.console_encoding, 'replace')
        
        if pageContent2.rfind(u'===') == -1:
            return
        else:
            pageContent3 = pageContent2[:pageContent2.rfind(u'===')]
            nature = pageContent3[pageContent3.rfind(u'===')+3:]
            if debugLevel > 1: raw_input(nature.encode(config.console_encoding, 'replace'))
        if nature == 'Noun':
            nature = u'S|nom'
        elif nature == 'Adjective':
            nature = u'S|adjectif'
        elif nature == 'Pronoun':
            nature = u'S|pronom'
        elif nature == 'Verb':
            nature = u'S|verbe'
        else:
            if debugLevel > 0: print ' Nature inconnue'
            return
        if debugLevel > 0: print u' nature : ' + nature

        Page1 = u'== {{langue|' + languageCode + u'}} ==\n=== {{' + nature + u'|' + languageCode + u'|flexion}} ===\n\'\'\'' + \
            page2.title() + u'\'\'\' {{pron|'+pron+'|' + languageCode + u'}}\n# \'\'Prétérit de\'\' ' + mot + \
            u'.\n# \'\'Participe passé de\'\' ' + mot + u'.\n\n[[en:' + page2.title() + u']]\n'
        summary = u'Importation depuis [[en:' + page2.title() + u']]'
        savePage(page1, Page1, summary)


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
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        # Daily
        p.pagesByCat(u'Catégorie:Pluriels manquants en français', False, u'')
        # TODO: python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"

if __name__ == "__main__":
    main(sys.argv)

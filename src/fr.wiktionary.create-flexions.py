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
    if page.exists():
        if page.namespace() != 0 and page.title() != u'Utilisateur:JackBot/test':
            print u' Autre namespace l 45'
            return
    else:
        print u' Page inexistante'
        return
    if not hasMoreThanTime(page, 1440): return

    Modele = [] # Liste des modèles du site à traiter
    Param = [] # Paramètre du lemme associé
    Modele.append(u'fr-rég-x')
    Param.append(u's')
    Modele.append(u'fr-rég')
    Param.append(u's')
    Modele.append(u'fr-accord-cons')
    Param.append(u'ms')
    languageCode = siteLanguage
    #TODO: ajouter Catégorie:Modèles d’accord en français

    PageSing = getContentFromPage(page, 'All')
    if PageSing.find(u'{{formater') != -1 or PageSing.find(u'{{SI|') != -1 or PageSing.find(u'{{SI}}') != -1 or PageSing.find(u'{{supp|') != -1 or PageSing.find(u'{{supp}}') != -1 or PageSing.find(u'{{supprimer|') != -1 or PageSing.find(u'{{supprimer') != -1 or PageSing.find(u'{{PàS') != -1 or PageSing.find(u'{{S|faute') != -1 or PageSing.find(u'{{S|erreur') != -1:
        if debugLevel > 0: print u'Page en travaux : non traitée l 65'
        return
        
    for m in range(0, len(Modele)):
        # Parcours de la page pour chaque modèle
        if debugLevel > 1: print ' début du for ' + str(m) + u', recherche du modèle : ' + Modele[m]
        if PageSing.find(Modele[m] + u'|') == -1 and PageSing.find(Modele[m] + u'}') == -1:
            if debugLevel > 1: pywikibot.output(u' Modèle : \03{blue}' + Modele[m] + u'\03{default} absent')
            continue
        else:
            if debugLevel > 0: pywikibot.output(u' Modèle : \03{blue}' + Modele[m] + u'\03{default} trouvé')
            PageTemp = PageSing
        
        while PageTemp.find(Modele[m]) != -1:
            if len(Modele[m]) < 3:
                if debugLevel > 0: print u' bug'
                break
            if debugLevel > 1: 
                print Modele[m].encode(config.console_encoding, 'replace')
                print PageTemp.find(Modele[m])
                
            # Parcours de la page pour chaque occurence du modèle
            nature = PageTemp[:PageTemp.find(Modele[m])]
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
                
            PageTemp = PageTemp[PageTemp.find(Modele[m])+len(Modele[m]):]
            suffixe = getParameter(PageTemp, u'inv')
            singulier = getParameter(PageTemp, u's')
            pluriel = u''
            if suffixe != u'':
                if singulier == u'':
                    if debugLevel > 0: print u'  inv= sans s='
                    break
                pluriel = singulier + u's ' + suffixe
                singulier = singulier + u' ' + suffixe
            elif singulier != u'' and singulier != pageName:
                if debugLevel > 0:
                    print u'  s= ne correspond pas'
                    print singulier.encode(config.console_encoding, 'replace')
                break
                
            # Prononciation
            if PageTemp.find(u'|pp=') != -1 and PageTemp.find(u'|pp=') < PageTemp.find(u'}}'):
                if debugLevel > 0: print ' pp='
                PageTemp2 = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
                if PageTemp2.find(u'|') != -1:
                    pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'|pp=')+4+PageTemp2.find(u'|')]
                else:
                    pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
            else:
                if debugLevel > 1: print '  prononciation identique au singulier'
                pron = PageTemp[:PageTemp.find(u'}}')]
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
            while pron[:1] == u' ': pron = pron[1:len(pron)]
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
            if PageTemp.find(u'|prefpron={{h aspiré') != -1 and PageTemp.find(u'|prefpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|prefpron={{h aspiré}}'
            if PageTemp.find(u'|préfpron={{h aspiré') != -1 and PageTemp.find(u'|préfpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|préfpron={{h aspiré}}'
            # genre
            genre = u''
            PageTemp2 = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
            while PageTemp2[:1] == u'[' or PageTemp2[:1] == u'\n' and len(PageTemp2) > 1: PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
            if PageTemp2.find(u'{{m}}') != -1 and PageTemp2.find(u'{{m}}') < PageTemp2.find(u'\n'): genre = u' {{m}}'    
            if PageTemp2.find(u'{{f}}') != -1 and PageTemp2.find(u'{{f}}') < PageTemp2.find(u'\n'): genre = u' {{f}}'
            MF = u''
            if PageTemp2.find(u'{{mf}}') != -1 and PageTemp2.find(u'{{mf}}') < PageTemp2.find(u'\n'):
                genre = u' {{mf}}'
                MF = u'|mf=oui'
                if PageSing.find(u'|mf=') == -1:
                    PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|mf=oui' + PageSing[PageSing.find(Modele[m])+len(Modele[m]):len(PageSing)]
                    savePage(page, PageSing, u'|mf=oui')
            if PageTemp.find(u'|mf=') != -1 and PageTemp.find(u'|mf=') < PageTemp.find(u'}}'): MF = u'|mf=oui' 
            # Pluriel
            summary = u'Création du pluriel de [[' + pageName + u']]'
            if pluriel == u'':
                if (PageTemp.find(u'|p=') != -1 and PageTemp.find(u'|p=') < PageTemp.find(u'}}')):
                    pluriel = PageTemp[PageTemp.find(u'|p=')+3:PageTemp.find(u'}}')]
                    if pluriel.find(u'|') != -1: pluriel = pluriel[:pluriel.find(u'|')]
                if not pluriel:
                    if Modele[m][-1:] == u'x':
                        pluriel = pageName + u'x'
                    else:
                        pluriel = pageName + u's'
                if (pluriel[-2:] == u'ss' or pluriel.find(u'{') != -1) and suffixe == u'':
                    print u' pluriel en -ss'
                    return
                if debugLevel > 1:
                    print '  Paramètre du modèle du lemme : ' + PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
            
            page2 = Page(site, pluriel)
            if page2.exists():
                PagePluriel = getContentFromPage(page2)
                if PagePluriel.find(u'{{langue|' + languageCode + u'}}') != -1:
                    if debugLevel > 0: print u'  Pluriel existant l 216 : ' + pluriel
                    break
            else:
                if debugLevel > 0: print u'  Pluriel introuvable l 219'
                PagePluriel = u''
            
            # **************** Pluriel 1 ****************
            if debugLevel > 1: print u'  Pluriel n°1'
            flexionTemplate = u'{{' + Modele[m] + pronM + H + MF + '|' + Param[m] + u'=' + pageName
            if pluriel != pageName + u's' and pluriel != pageName + u'x':
                flexionTemplate += u'|p={{subst:PAGENAME}}'
            flexionTemplate += u'}}'
            PageEnd = u'== {{langue|fr}} ==\n=== {{S|' + nature + u'|fr|flexion}} ===\n' + flexionTemplate + u'\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pronM + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + pageName +']].\n'
            while PageEnd.find(u'{{pron|fr}}') != -1:
                PageEnd = PageEnd[:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]

            if pluriel[-2:] == u'ss':
                PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|' + Param[m] + u'=' + pluriel[:-2] + PageSing[PageSing.find(Modele[m])+len(Modele[m]):]
                savePage(page, PageSing, u'{{' + Modele[m] + u'|s=...}}')
            elif pluriel[-2:] == u'xs':
                print u' Pluriel en xs'
                return
            else:
                PageEnd = PageEnd + u'\n' + PagePluriel
                CleTri = defaultSort(pluriel)
                if addDefaultSort:
                    if PageEnd.find(u'{{clé de tri') == -1 and CleTri != u'' and CleTri.lower() != pluriel.lower():
                        PageEnd = PageEnd +  u'\n{{clé de tri|' + CleTri + u'}}\n'
                PageEnd = html2Unicode(PageEnd)
                savePage(page2, PageEnd, summary)

            # TODO: pluriel n°2
            #raw_input(PageTemp.encode(config.console_encoding, 'replace'))
            if debugLevel > 1: print u'  Fin du while'
        if debugLevel > 1: print u' Fin du for ' + str(m)


def createPluralFromForeignWiki(Page2):
    page2 = Page(siteSource,Page2)
    page1 = Page(site,Page2)
    if debugLevel > 0: print Page2.encode(config.console_encoding, 'replace')
    if page2.exists() and page2.namespace() == 0 and not page1.exists():
        PageTemp = getPage(page2)
        if PageTemp == u'': return
        # Nature grammaticale
        PageTemp2 = PageTemp[:PageTemp.find(templateSource)]
        # Code langue
        PageTemp = PageTemp[PageTemp.find(templateSource)+len(templateSource)+1:len(PageTemp)]
        if PageTemp.find("lang=") != -1 and PageTemp.find("lang=") < PageTemp.find(u'}}'):
            PageTemp2 = PageTemp[PageTemp.find("lang=")+5:len(PageTemp)]
            if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
                codelangue = PageTemp2[:PageTemp2.find("|")]
                PageTemp = PageTemp[:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("|"):len(PageTemp)]
            else:
                codelangue = PageTemp2[:PageTemp2.find("}}")]
                PageTemp = PageTemp[:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("}"):len(PageTemp)]
            if codelangue == u'': codelangue = u'en'
            elif codelangue == u'Italian': codelangue = u'it'
            elif codelangue == u'Irish': codelangue = u'ga'
            elif codelangue == u'German': codelangue = u'de'
            elif codelangue == u'Middle English': codelangue = u'enm'
            elif codelangue == u'Old English': codelangue = u'ang'
            elif codelangue == u'Dutch': codelangue = u'nl'
            elif codelangue == u'Romanian': codelangue = u'ro'
            elif codelangue == u'Spanish': codelangue = u'es'
            elif codelangue == u'Catalan': codelangue = u'ca'
            elif codelangue == u'Portuguese': codelangue = u'pt'
            elif codelangue == u'Russian': codelangue = u'ru'
            elif codelangue == u'French': codelangue = u'fr'
            elif codelangue == u'Scots': codelangue = u'sco'
            elif codelangue == u'Chinese': codelangue = u'zh'
            elif codelangue == u'Mandarin': codelangue = u'zh'
            elif codelangue == u'Japanese': codelangue = u'ja'
        else:
            codelangue = u'en'
        #if debugLevel > 0: print u' ' + codelangue
        
        while PageTemp[:1] == u' ' or PageTemp[:1] == u'|':
            PageTemp = PageTemp[1:len(PageTemp)]
        # Lemme
        if PageTemp.find(u']]') != -1 and PageTemp.find(u']]') < PageTemp.find(u'}}'): # Si on est dans un lien
            mot = PageTemp[:PageTemp.find(u']]')+2]
        elif PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find(u'}}'):
            mot = PageTemp[:PageTemp.find(u'|')] # A faire : si dièse on remplace en même temps que les codelangue ci-dessous, à patir d'un tableau des langues
        else:
            mot = PageTemp[:PageTemp.find(u'}}')]
        if mot[:2] != u'[[': mot = u'[[' + mot + u']]'
        
        # Demande de Lmaltier : on ne crée que les flexions des lemmes existant
        page3 = Page(site,mot[2:len(mot)-2])
        if page3.exists() == u'False':
            print 'Page du lemme absente du Wiktionnaire'
            return
        PageLemme = getPage(page3)
        if PageLemme == u'': return
        if PageLemme.find(u'{{langue|' + codelangue + u'}}') == -1:
            print ' Paragraphe du lemme absent du Wiktionnaire'
            return
        else:
            # Prononciation
            pron = u''
            PageLemme = PageLemme[PageLemme.find(u'{{langue|' + codelangue + u'}}'):]
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
                l = pron[-1:]
                if l in (u'f', u'k', u'p', u'θ', u's', u'ʃ'):
                    pron = pron + u't'
                elif l in (u't', u'd'):
                    pron = pron + u'ɪd' 
                else:
                    pron = pron + u'd'
            if debugLevel > 0: print u' prononciation : ' + pron #.encode(config.console_encoding, 'replace')
        
        if PageTemp2.rfind(u'===') == -1:
            return
        else:
            PageTemp3 = PageTemp2[:PageTemp2.rfind(u'===')]
            nature = PageTemp3[PageTemp3.rfind(u'===')+3:]
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

        # Interwikis
        interwikiInside = pywikibot.getLanguageLinks(PageTemp, siteSource)
        interwiki = replaceLanguageLinks(u'', interwikiInside, siteSource)
        while interwiki.find(u'[[wiktionary:') != -1:
            interwiki = interwiki[:interwiki.find(u'[[wiktionary:')+2] + interwiki[interwiki.find(u'[[wiktionary:')+len(u'[[wiktionary:'):len(interwiki)]

        Page1 = u'== {{langue|' + codelangue + u'}} ==\n=== {{' + nature + u'|' + codelangue + u'|flexion}} ===\n\'\'\'' + page2.title() + u'\'\'\' {{pron|'+pron+'|' + codelangue + u'}}\n# \'\'Prétérit de\'\' ' + mot + u'.\n# \'\'Participe passé de\'\' ' + mot + u'.\n\n[[en:' + page2.title() + u']]\n' + trim(interwiki)
        summary = u'Importation depuis [[en:' + page2.title() + u']]'
        savePage(page1, Page1, summary)


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
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        # Daily
        p.pagesByCat(u'Catégorie:Pluriels manquants en français', False, u'')
        # TODO: python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"

if __name__ == "__main__":
    main(sys.argv)

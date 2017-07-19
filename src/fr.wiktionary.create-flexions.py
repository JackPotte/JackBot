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
if len(sys.argv) > 2:
    if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
        debugLevel= 1
elif len(sys.argv) == 2:
    if sys.argv[1] == str('debug') or sys.argv[1] ==  str('d'):
        debugLevel= 1

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

siteSource = pywikibot.Site('en', siteFamily)
templateSource = u'en-past of'
textTranslated = u'Passé de'
DebutScan = u'interspersed'
# TODO pluriels fr + en


def modification(PageHS):
    if debugLevel > 0: print u'------------------------------------'
    print(PageHS.encode(config.console_encoding, 'replace'))
    page = Page(site,PageHS)
    if page.exists():
        if page.namespace() != 0 and page.title() != u'Utilisateur:JackBot/test':
            print u' Autre namespace l 26'
            return
    else:
        print u' Page inexistante'
        return
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
        if debugLevel > 0: print u'Page en travaux : non traitée l 60'
        return
        
    for m in range(0,len(Modele)):
        # Parcours de la page pour chaque modèle
        if debugLevel > 1: print ' début du for ' + str(m)
        while PageSing.find(Modele[m] + u'|') == -1 and PageSing.find(Modele[m] + u'}') == -1 and m < len(Modele)-1:
            if debugLevel > 0: print u' Modèle ' + Modele[m] + u' absent l 58'
            m += 1
        if m == len(Modele):
            break
        else:
            if debugLevel > 0: print Modele[m].encode(config.console_encoding, 'replace') #+ u' présent'
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
                    print u' Nature : ' + nature.encode(config.console_encoding, 'replace')
                except UnicodeDecodeError:
                    print u' Nature à décoder'
                except UnicodeEncodeError:
                    print u' Nature à encoder'
            if nature == u'erreur' or nature == u'faute':
                print u' section erreur'
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
            elif singulier != u'' and singulier != PageHS:
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
                if debugLevel > 1: print ' prononciation identique au singulier'
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
                    print u' Prononciation : ' + pronM.encode(config.console_encoding, 'replace')
                except UnicodeDecodeError:
                    print u' Prononciation à décoder'
                except UnicodeEncodeError:
                    print u' Prononciation à encoder'
            
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
            summary = u'Création du pluriel de [[' + PageHS + u']]'
            if pluriel == u'':
                if (PageTemp.find(u'|p=') != -1 and PageTemp.find(u'|p=') < PageTemp.find(u'}}')):
                    pluriel = PageTemp[PageTemp.find(u'|p=')+3:PageTemp.find(u'}}')]
                    if pluriel.find(u'|') != -1: pluriel = pluriel[:pluriel.find(u'|')]
                if not pluriel:
                    if Modele[m][-1:] == u'x':
                        pluriel = PageHS + u'x'
                    else:
                        pluriel = PageHS + u's'
                if (pluriel[-2:] == u'ss' or pluriel.find(u'{') != -1) and suffixe == u'':
                    print u' pluriel en -ss'
                    return
                if debugLevel > 1:
                    print ' Paramètre du modèle du lemme : ' + PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
            
            page2 = Page(site, pluriel)
            if page2.exists():
                PagePluriel = getContentFromPage(page2)
                if PagePluriel.find(u'{{langue|' + languageCode + u'}}') != -1:
                    if debugLevel > 0:
                        print u' Pluriel existant l 135'
                        print pluriel.encode(config.console_encoding, 'replace')
                    else:
                        break
            else:
                if debugLevel > 0: print u' Pluriel introuvable l 138'
                PagePluriel = u''
            
            # **************** Pluriel 1 ****************
            if debugLevel > 0: print u' Pluriel 1'
            Modele = u'{{' + Modele[m] + pronM + H + MF + '|' + Param[m] + u'=' + PageHS
            if pluriel != PageHS + u's' and pluriel != PageHS + u'x':
                Modele += u'|p={{subst:PAGENAME}}'
            Modele += u'}}'
            PageEnd = u'== {{langue|fr}} ==\n=== {{S|' + nature + u'|fr|flexion}} ===\n' + Modele + u'\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pronM + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + PageHS +']].\n'
            while PageEnd.find(u'{{pron|fr}}') != -1:
                PageEnd = PageEnd[:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]

            if pluriel[len(pluriel)-2:len(pluriel)] == u'ss':
                PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|' + Param[m] + u'=' + pluriel[:len(pluriel)-2] + PageSing[PageSing.find(Modele[m])+len(Modele[m]):len(PageSing)]
                savePage(page, PageSing, u'{{' + Modele[m] + u'|s=...}}')
            elif pluriel[len(pluriel)-2:len(pluriel)] == u'xs':
                print u' Pluriel en xs'
                return
            else:
                PageEnd = PageEnd + u'\n' + PagePluriel
                CleTri = defaultSort(pluriel)
                if PageEnd.find(u'{{clé de tri') == -1 and CleTri != u'' and CleTri.lower() != pluriel.lower():
                    PageEnd = PageEnd +  u'\n{{clé de tri|' + CleTri + u'}}\n'
                PageEnd = html2Unicode(PageEnd)
                savePage(page2, PageEnd, summary)
            #raw_input(PageTemp.encode(config.console_encoding, 'replace'))
            if debugLevel > 1: print u'Fin du while'
        if debugLevel > 1: print u'Fin du for'


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

        Page1 = u'=={{langue|' + codelangue + u'}}==\n=== {{' + nature + u'|' + codelangue + u'|flexion}} ===\n\'\'\'' + page2.title() + u'\'\'\' {{pron|'+pron+'|' + codelangue + u'}}\n# \'\'Prétérit de\'\' ' + mot + u'.\n# \'\'Participe passé de\'\' ' + mot + u'.\n\n[[en:' + page2.title() + u']]\n' + trim(interwiki)
        summary = u'Importation depuis [[en:' + page2.title() + u']]'
        savePage(page1, Page1, summary)


def getLemmaFromLocution(pageName):
    if debugLevel > 0: print u'\ngetLemmaFromLocution'
    pageLemma = getContentFromPageName(pageName[:pageName.find(u' ')])
    return pageLemma

def getLemmaFromPlural(PageTemp):
    if debugLevel > 0: print u'\ngetLemmaFromPlural'
    pageLemma = u''

    regex = ur"(=== {{S\|(nom|adjectif)\|fr\|flexion}} ===\n({{fr\-[^}]*}}\n)*'''[^\n]+\n# *'* *(Masculin|Féminin)* *'* *'*[P|p]luriel *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, PageTemp)
    if s:
        if debugLevel > 1:
            print(s.group(1).encode(config.console_encoding, 'replace')) # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            raw_input(s.group(6).encode(config.console_encoding, 'replace'))
        pageLemma = s.group(6)
    if debugLevel > 0: print u' pageLemma found: ' + pageLemma

    return pageLemma

def getLemmaFromConjugation(PageTemp):
    if debugLevel > 0: print u'\ngetLemmaFromConjugation'
    pageLemma = u''
    regex = ur"(=== {{S\|verbe\|fr\|flexion}} ===\n({{fr\-[^}]*}}\n)*'''[^\n]+\n#[^\n\[{]+(\[\[|{{li?e?n?\|))([^#\|\]}]+)}*\]*'*\."
    s = re.search(regex, PageTemp)
    if s:
        if debugLevel > 1:
            print(s.group(1).encode(config.console_encoding, 'replace')) # 2 fr-verbe-flexion, 3 = {{lien|, 4 = lemme
            raw_input(s.group(4).encode(config.console_encoding, 'replace'))
        pageLemma = s.group(4)
    if debugLevel > 0: print u' pageLemma found: ' + pageLemma

    return pageLemma

def getFlexionTemplate(pageName, language, nature):
    if debugLevel > 0: print u'\ngetFlexionTemplate'
    FlexionTemplate = u''
    PageTemp = getContentFromPageName(pageName)
    regex = ur"=== {{S\|" + nature + ur"\|" + language + ur"\|flexion(\|num=[0-9])?}} ===\n{{(" + language + ur"\-[^}]+)}}"
    if debugLevel > 1: print u' ' + regex
    s = re.search(regex, PageTemp)
    if s:
        if debugLevel > 1:
            if not s.group(1) is None: print u' ' + s.group(1)
            if not s.group(2) is None: print u' ' + s.group(2)
        FlexionTemplate = s.group(2)
    if debugLevel > 0: print u' FlexionTemplate found: ' + FlexionTemplate
    # TODO
    if FlexionTemplate.find('{{') != -1: FlexionTemplate = u''
    if FlexionTemplate.find(u'-inv') != -1: FlexionTemplate = u''

    return FlexionTemplate

def getFlexionTemplateFromLemma(pageName, language, nature):
    if debugLevel > 0: print u'\ngetFlexionTemplateFromLemma'
    FlexionTemplate = u''
    PageTemp = getContentFromPageName(pageName)
    regex = ur"=== {{S\|" + nature + ur"\|" + language + ur"(\|num=[0-9])?}} ===\n{{(" + language + ur"\-[^}]+)}}"
    if debugLevel > 1: print u' ' + regex
    s = re.search(regex, PageTemp)
    if s:
        if debugLevel > 1:
            if not s.group(1) is None: print u' ' + s.group(1)
            if not s.group(2) is None: print u' ' + s.group(2)
        FlexionTemplate = s.group(2)
    if debugLevel > 0: print u' FlexionTemplate found: ' + FlexionTemplate
    # TODO
    if FlexionTemplate.find('{{') != -1: FlexionTemplate = u''
    if FlexionTemplate.find(u'-inv') != -1: FlexionTemplate = u''

    return FlexionTemplate

def getContentFromPageName(pageName, allowedNamespaces = None):
    page = Page(site, pageName)
    return getContentFromPage(page, allowedNamespaces)

def getContentFromPage(page, allowedNamespaces = None):
    PageBegin = u''
    if page.exists():
        if type(allowedNamespaces) == type([]): #'list'
            if debugLevel > 1: print u' namespace : ' + str(page.namespace())
            condition = page.namespace() in allowedNamespaces
        elif allowedNamespaces == 'All':
            if debugLevel > 1: print u' all namespaces'
            condition = True
        else:
            if debugLevel > 1: print u' content namespaces'
            condition = page.namespace() in [0, 12, 14, 100] or page.title().find(username) != -1
        if condition:
            try:
                PageBegin = page.get()
            except pywikibot.exceptions.BadTitle:
                if debugLevel > 0: print u'IsRedirect l 5658'
                return 'KO'
            except pywikibot.exceptions.IsRedirectPage:
                if debugLevel > 0: print u'IsRedirect l 5662'
                if page.namespace() == 'Template:':
                    PageBegin = page.get(get_redirect=True)
                    if PageBegin[:len(u'#REDIRECT')] == u'#REDIRECT':
                        regex = ur'\[\[([^\]]+)\]\]'
                        s = re.search(regex, PageBegin)
                        if s:
                            PageBegin = getContentFromPageName(s.group(1), allowedNamespaces = allowedNamespaces)
                        else:
                            return 'KO'
                    else:
                        return 'KO'
                else:
                    return 'KO'
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u'NoPage l 5665'
                return 'KO'
            except pywikibot.exceptions.ServerError:
                if debugLevel > 0: print u'NoPage l 5668'
                return 'KO'
        else:
            if debugLevel > 0: print u'Forbidden namespace l 5671'
            return 'KO'
    else:
        if debugLevel > 0: print u'No page l 5674'
        return 'KO'

    return PageBegin

def getWiki(language, family):
    if family is None:
        return site
    else:
        wiki = u'KO'
        try:
            wiki = pywikibot.Site(language, family)
        except pywikibot.exceptions.ServerError:
            if debugLevel > 1: print u'  ServerError in getWiki'
        except pywikibot.exceptions.NoSuchSite:
            if debugLevel > 1: print u'  NoSuchSite in getWiki'
        except UnicodeEncodeError:
            if debugLevel > 1: print u'  UnicodeEncodeError in getWiki'
        #TODO: WARNING: src/fr.wiktionary.format.py:4145: UserWarning: Site wiktionary:ro instantiated using different code "mo"
    return wiki

def getParameter(Page, p):                
    '''
    print pron.encode(config.console_encoding, 'replace')
    pattern = ur'.*\|([^}\|]*)}|\|'
    regex = re.search(pattern, pron)
    print regex.start()
    print regex.end()
    raw_input(pron[regex.start():regex.end()])
    '''
    if Page.find(p + u'=') == -1 or Page.find(u'}}') == -1 or Page.find(p + u'=') > Page.find(u'}}'): return u''
    Page = Page[Page.find(p + u'=')+len(p + u'='):]
    if Page.find(u'|') != -1 and Page.find(u'|') < Page.find(u'}}'):
        return trim(Page[:Page.find(u'|')])
    else:
        return trim(Page[:Page.find(u'}')])

def nextTemplate(PageEnd, PageTemp, currentTemplate = None, languageCode = None):
    if languageCode is None:
        PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
    else:
        PageEnd = PageEnd + currentTemplate + "|" + languageCode + '}}'
    PageTemp = PageTemp[PageTemp.find('}}')+2:]
    return PageEnd, PageTemp

def nextTranslationTemplate(PageEnd, PageTemp, result = u'-'):
    PageEnd = PageEnd + PageTemp[:len(u'trad')] + result
    PageTemp = PageTemp[PageTemp.find(u'|'):]
    return PageEnd, PageTemp
                      
def addCat(PageTemp, lang, cat):    # à remplacer par celle ci-dessous
    if lang != u'':
        if PageTemp.find(cat) == -1 and PageTemp.find(u'{{langue|' + lang + '}}') != -1:
            if cat.find(u'[[Catégorie:') == -1: cat = u'[[Catégorie:' + cat + u']]'
            PageTemp2 = PageTemp[PageTemp.find(u'{{langue|' + lang + '}}')+len(u'{{langue|' + lang + '}}'):]
            if PageTemp2.find(u'{{langue|') != -1:
                if debugLevel > 0: print u' catégorie ajoutée avant la section suivante'
                if PageTemp2.find(u'== {{langue|') != -1:
                    PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + '}}')+len(u'{{langue|' + lang + '}}')+PageTemp2.find(u'== {{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + '}}')+len(u'{{langue|' + lang + '}}')+PageTemp2.find(u'== {{langue|'):]
                elif PageTemp2.find(u'=={{langue|') != -1:
                    PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + '}}')+len(u'{{langue|' + lang + '}}')+PageTemp2.find(u'=={{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + '}}')+len(u'{{langue|' + lang + '}}')+PageTemp2.find(u'=={{langue|'):]
                else:
                     print u'Modèle {{langue| mal positionné'
            else:
                if debugLevel > 0: print u' catégorie ajoutée avant les interwikis'
                regex = ur'\n\[\[\w?\w?\w?:'
                if re.compile(regex).search(PageTemp):
                    try:
                        PageTemp = PageTemp[:re.search(regex,PageTemp).start()] + u'\n' + cat + u'\n' + PageTemp[re.search(regex,PageTemp).start():]
                    except:
                        print u'pb regex interwiki'
                else:
                    if debugLevel > 0: print u' catégorie ajoutée en fin de page'
                    PageTemp = PageTemp + u'\n' + cat
    return PageTemp


def addLine(Page, languageCode, Section, pageContent):
    if Page != '' and languageCode != '' and Section != '' and pageContent != '':
        if Page.find(pageContent) == -1 and Page.find(u'{{langue|' + languageCode + '}}') != -1:
            if Section == u'catégorie' and pageContent.find(u'[[Catégorie:') == -1: pageContent = u'[[Catégorie:' + pageContent + u']]'
            if Section == u'clé de tri' and pageContent.find(u'{{clé de tri|') == -1: pageContent = u'{{clé de tri|' + pageContent + '}}'

            # Recherche de l'ordre théorique de la section à ajouter
            NumSection = NumeroSection(Section)
            if NumSection == len(Sections):
                if debugLevel > 0:
                    print u''
                    print u' ajout de '
                    print Section.encode(config.console_encoding, 'replace')
                    print u' dans une section inconnue'
                    print u' (car ' + len(Sections) + u' = ' + str(NumSection) + u')'
                    print u''
                return Page
            if debugLevel > 1: print u' position S : ' + s

            # Recherche de l'ordre réel de la section à ajouter
            PageTemp2 = Page[Page.find(u'{{langue|' + languageCode + '}}')+len(u'{{langue|' + languageCode + '}}'):]
            #SectionPage = re.findall("{{S\|([^}]+)}}", PageTemp2) # Mais il faut trouver le {{langue}} de la limite de fin
            SectionPage = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", PageTemp2)
            if debugLevel > 1:
                o = 0
                while o < len(SectionPage):
                     print str(SectionPage[o]).encode(config.console_encoding, 'replace')
                     o = o + 1
                if o == len(SectionPage): o = o - 1
                raw_input()

            o = 0
            #raw_input(str(SectionPage[0][0].encode(config.console_encoding, 'replace')))
            # pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
            while o < len(SectionPage) and str(SectionPage[o][0].encode(config.console_encoding, 'replace')) != 'langue' and NumeroSection(SectionPage[o][0]) <= NumSection:
                if debugLevel > 0:
                    print SectionPage[o][0]
                    print NumeroSection(SectionPage[o][0])
                o = o + 1
            SectionLimite = str(SectionPage[o][0].encode(config.console_encoding, 'replace'))
            o = o - 1
            if debugLevel > 1: print u' position O : ' + o
            if debugLevel > 0:
                print u''
                print u'Ajout de '
                print Section.encode(config.console_encoding, 'replace')
                print u' avant '
                print SectionLimite
                print u' (car ' + str(NumeroSection(SectionLimite)) + u' > ' + str(NumSection) + u')'
                print u''

            # Ajout après la section trouvée
            if PageTemp2.find(u'{{S|' + SectionPage[o][0]) == -1:
                print 'Erreur d\'encodage'
                return

            PageTemp3 = PageTemp2[PageTemp2.find(u'{{S|' + SectionPage[o][0]):]
            if SectionPage[o][0] != Section and Section != u'catégorie' and Section != u'clé de tri':
                if debugLevel > 1: print u' ajout de la section'
                pageContent = u'\n' + Niveau[NumSection] + u' {{S|' + Section + u'}} ' + Niveau[NumSection] + u'\n' + pageContent

            # Ajout à la ligne
            if PageTemp3.find(u'\n==') == -1:
                regex = ur'\n\[\[\w?\w?\w?:'
                if re.compile(regex).search(Page):
                    interwikis = re.search(regex, Page).start()
                    categories = Page.find(u'\n[[Catégorie:')
                    defaultSort = Page.find(u'\n{{clé de tri|')

                    if (interwikis < categories or categories == -1) and (interwikis < defaultSort or defaultSort == -1):
                        if debugLevel > 0: print u' ajout avant les interwikis'
                        try:
                            Page = Page[:interwikis] + u'\n' + pageContent + u'\n' + Page[interwikis:]
                        except:
                            print u' pb regex interwiki'
                    elif categories != -1 and (categories < defaultSort or defaultSort == -1):
                        if debugLevel > 0: print u' ajout avant les catégories'
                        Page = Page[:Page.find(u'\n[[Catégorie:')] + pageContent + Page[Page.find(u'\n[[Catégorie:'):]
                    elif defaultSort != -1:
                        if debugLevel > 0: print u' ajout avant la clé de tri'
                        Page = Page[:Page.find(u'\n{{clé de tri|')] + pageContent + Page[Page.find(u'\n{{clé de tri|'):]
                    else:
                        if debugLevel > 0: print u' ajout en fin de page'
                        Page = Page + pageContent
                else:
                    if debugLevel > 0: print u' ajout en fin de page'
                    Page = Page + pageContent
            else:
                Page = Page[:-len(PageTemp2)] + PageTemp2[:-len(PageTemp3)] + PageTemp3[:PageTemp3.find(u'\n\n')] + u'\n' + pageContent + u'\n' + PageTemp3[PageTemp3.find(u'\n\n'):]
    return Page

def rec_anagram(counter):
    # Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1
def anagram(word):
    return rec_anagram(collections.Counter(word))

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
    PageTemp = getContentFromPageName(u'User talk:' + username)
    if PageTemp == 'KO': return
    if PageTemp != u"{{/Stop}}":
        pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
        exit(0)

def savePage(currentPage, pageContent, summary):
    result = "ok"
    if debugLevel > 0:
        if len(pageContent) < 6000:
            print(pageContent.encode(config.console_encoding, 'replace'))
        else:
            taille = 3000
            print(pageContent[:taille].encode(config.console_encoding, 'replace'))
            print u'\n[...]\n'
            print(pageContent[len(pageContent)-taille:].encode(config.console_encoding, 'replace'))
        result = raw_input((u'\nSauvegarder [[' + currentPage.title() + u']] ? (o/n) ').encode('utf-8'))
    if result != "n" and result != "no" and result != "non":
        if currentPage.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
        if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            currentPage.put(pageContent, summary)
        except pywikibot.exceptions.NoPage:
            print "NoPage in savePage"
            return
        except pywikibot.exceptions.IsRedirectPage:
            print "IsRedirectPage in savePage"
            return
        except pywikibot.exceptions.LockedPage:
            print "LockedPage in savePage"
            return
        except pywikibot.EditConflict:
            print "EditConflict in savePage"
            return
        except pywikibot.exceptions.ServerError:
            print "ServerError in savePage"
            return
        except pywikibot.exceptions.BadTitle:
            print "BadTitle in savePage"
            return
        except pywikibot.exceptions.OtherPageSaveError:
            print "OtherPageSaveError"
            time.sleep(10)
            savePage(currentPage, pageContent, summary)
            return
        except AttributeError:
            print "AttributeError in savePage"
            return

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    if source:
        PagesHS = open(source, 'r')
        while 1:
            pageName = PagesHS.readline().decode(config.console_encoding, 'replace')
            fin = pageName.find("\t")
            pageName = pageName[:fin]
            if pageName == '': break
            if pageName.find(u'[[') != -1:
                pageName = pageName[pageName.find(u'[[')+2:]
            if pageName.find(u']]') != -1:
                pageName = pageName[:pageName.find(u']]')]
            # Conversion ASCII => Unicode (pour les .txt)
            modification(html2Unicode(pageName))
        PagesHS.close()

# Lecture du dump
def crawlerXML(source, regex = u''):
    if debugLevel > 1: print u'crawlerXML'
    if source:
        from pywikibot import xmlreader
        dump = xmlreader.XmlDump(source)
        parser = dump.parse()
        outPutFile = open('src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt', 'a')

        for entry in parser:
            PageTemp = entry.text

            if regex != str(''):
                if re.search(regex, PageTemp):
                    outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

            else:
                '''
                if debugLevel > 1: print u' Pluriels non flexion'
                if entry.title[-2:] == u'es':
                    if debugLevel > 1: print entry.title
                    regex = ur"=== {{S\|adjectif\|fr[^}]+}} ===\n[^\n]*\n*{{fr\-rég\|[^\n]+\n*'''" + re.escape(entry.title) + ur"'''[^\n]*\n# *'*'*(Masculin|Féminin)+ *[P|p]luriel de *'*'* *\[\["
                    if re.search(regex, PageTemp):
                        if debugLevel > 0: print entry.title
                        #PageTemp = re.sub(regex, ur'\1|flexion\2', PageTemp)
                        #modification(html2Unicode(entry.title))

                if debugLevel > 1: print u' Ajout de la boite de flexion'
                if entry.title[-1:] == u's':
                    if (PageTemp.find(u'{{S|adjectif|fr|flexion}}') != -1 or PageTemp.find(u'{{S|nom|fr|flexion}}') != -1) and PageTemp.find(u'{{fr-') == -1:
                        #print entry.title # limite de 8191 lignes dans le terminal.
                        #modification(entry.title)
                        outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                '''
                if debugLevel > 1: print u' balises HTML désuètes'
                for deprecatedTag in deprecatedTags.keys():
                    if PageTemp.find(u'<' + deprecatedTag) != -1:
                        outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

        outPutFile.close()


# Traitement d'une catégorie
def crawlerCat(category, recursif, apres, ns = 0):
    modifier = u'False'
    print category.encode(config.console_encoding, 'replace')
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) # HS sur Commons
    #gen =  pagegenerators.CategorizedPageGenerator(cat)
    for Page in pagegenerators.PreloadingGenerator(gen, 100):
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'
    if recursif:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            print subcategory.title().encode(config.console_encoding, 'replace')
            pages = subcategory.articlesList(False)
            for Page in pagegenerators.PreloadingGenerator(pages,100):
                modification(Page.title())

def crawlerCat2(category, recursif, apres):
    import pywikibot
    from pywikibot import pagegenerators
    modifier = u'False'
    cat = pywikibot.Category(site, category)    # 'module' object has no attribute 'Category'
    gen =  pagegenerators.CategorizedPageGenerator(cat)
    for Page in gen:
        modification(Page.title())

# Traitement des pages liées
def crawlerLink(pageName, apres):
    modifier = u'False'
    #pageName = unicode(arg[len('-links:'):], 'utf-8')
    page = pywikibot.Page(site, pageName)
    gen = pagegenerators.ReferringPageGenerator(page)
    gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        print(Page.title().encode(config.console_encoding, 'replace'))
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pageName, apres):
    modifier = u'False'
    cat = catlib.Category(site, pageName)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        print Page.title().encode(config.console_encoding, 'replace')
        page = pywikibot.Page(site, Page.title())
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
            if not apres or apres == u'' or modifier == u'True':
                modification(PageLiee.title()) #crawlerLink(Page.title())
            elif PageLiee.title() == apres:
                modifier = u'True'

# Traitement d'une recherche
def crawlerSearch(pageName, ns = None):
    gen = pagegenerators.SearchPageGenerator(pageName, site = site, namespaces = ns)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Traitement des modifications récentes
def crawlerRCLastDay(site = site, nobots=True, namespace='0'):
    # Génère les modifications récentes de la dernière journée
    timeAfterLastEdition = 30 # minutes

    date_now = datetime.datetime.utcnow()
    # Date de la plus récente modification à récupérer
    date_start = date_now - datetime.timedelta(minutes=timeAfterLastEdition)
    # Date d'un jour plus tôt
    date_end = date_start - datetime.timedelta(1)

    start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
    end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

    for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
                    rcdir='older', rctype='edit|new', namespace=namespace,
                    includeredirects=True, repeat=False, user=None,
                    returndict=False, nobots=nobots):
        yield item[0]

def crawlerRC():
    gen = pagegenerators.RecentchangesPageGenerator(site = site)
    ecart_minimal_requis = 30 # min
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print str(timeAfterLastEdition(Page)) + ' =? ' + str(ecart_minimal_requis)
        if timeAfterLastEdition(Page) > ecart_minimal_requis:
            modification(Page.title())

def timeAfterLastEdition(page):
    # Timestamp au format MediaWiki de la dernière version
    time_last_edit = page.getVersionHistory()[0][1]
    match_time = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', time_last_edit)
    # Mise au format "datetime" du timestamp de la dernière version
    datetime_last_edit = datetime.datetime(int(match_time.group(1)), int(match_time.group(2)), int(match_time.group(3)),
        int(match_time.group(4)), int(match_time.group(5)), int(match_time.group(6)))
    datetime_now = datetime.datetime.utcnow()
    diff_last_edit_time = datetime_now - datetime_last_edit

    # Ecart en minutes entre l'horodotage actuelle et l'horodotage de la dernière version
    return diff_last_edit_time.seconds/60 + diff_last_edit_time.days*24*60

# Traitement des modifications d'un compte
def crawlerUser(username, jusqua, apres, regex = None):
    modifier = u'False'
    compteur = 0
    gen = pagegenerators.UserContributionsGenerator(username, site = site)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if not apres or apres == u'' or modifier == u'True':
            if regex is None:
                modification(Page.title())
            else:
                PageTemp = getContentFromPageName(Page.title(), allowedNamespaces = 'All')
                if re.search(regex, PageTemp):
                    print Page.title()
            compteur = compteur + 1
            if compteur > jusqua: break
        elif Page.title() == apres:
            modifier = u'True'

# Toutes les redirections
def crawlerRedirects():
    for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
        modification(Page.title())

# Traitement de toutes les pages du site
def crawlerAll(start):
    gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False, site = site)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())


def main(*args):
    if len(sys.argv) > 1:
        if sys.argv[1] == u'test':
            modification(u'User:' + username + u'/test')
        elif sys.argv[1] == u't':
            modification(u'User:' + username + u'/test court')
        elif sys.argv[1] == u'unit tests' or sys.argv[1] == u'tu':
            addLine(u"== {{langue|fr}} ==\n=== {{S|étymologie}} ===\n{{ébauche-étym|fr}}\n=== {{S|nom|fr}} ===\n{{fr-rég|}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||fr}} {{genre ?}}\n#\n#* ''''\n==== {{S|variantes orthographiques}} ====\n==== {{S|synonymes}} ====\n==== {{S|antonymes}} ====\n==== {{S|dérivés}} ====\n==== {{S|apparentés}} ====\n==== {{S|vocabulaire}} ====\n==== {{S|hyperonymes}} ====\n==== {{S|hyponymes}} ====\n==== {{S|méronymes}} ====\n==== {{S|holonymes}} ====\n==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n=== {{S|prononciation}} ===\n* {{pron||fr}}\n* {{écouter|<!--  précisez svp la ville ou la région -->||audio=|lang=}}\n==== {{S|homophones}} ====\n==== {{S|paronymes}} ====\n=== {{S|anagrammes}} ===\n=== {{S|voir aussi}} ===\n* {{WP}}\n=== {{S|références}} ===\n", u'fr', u'prononciation', u'* {{pron|boum|fr}}')
        elif sys.argv[1] == u'page':
            modification(u'télétransporter')
        elif sys.argv[1] == u'file' or sys.argv[1] == u'txt':
            crawlerFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            crawlerXML(u'dumps/frwiktionary-20170701-pages-meta-current.xml', regex)
        elif sys.argv[1] == u'link' or sys.argv[1] == u'm':
            crawlerLink(site, u'Modèle:ex',u'')
        elif sys.argv[1] == u'cat':
            crawlerCat(u'Caractères en braille', True, u'')
            #crawlerCat(u'suédois', False, u'')
            #crawlerCat(u'Gentilés en français', False, u'')
            #crawlerCat(u'Pluriels manquants en français', False, u'')
            #crawlerCat(u'Catégorie:Wiktionnaire:Sections de type avec locution forcée', False, u'')
            #crawlerCat(u'Catégorie:Genres manquants en français', False, u'')
        elif sys.argv[1] == u's':
            crawlerSearch(u'insource:/\<strong>\<strong>/')
        elif sys.argv[1] == u'u':
            crawlerUser(u'User:JackBot', 10000, u'')
        elif sys.argv[1] == u'redirects':
            crawlerRedirects()
        elif sys.argv[1] == u'all':
           crawlerAll()
        elif sys.argv[1] == u'RC':
            while 1:
                crawlerRCLastDay()
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            modification(html2Unicode(sys.argv[1]))
    else:
        # Daily
        crawlerCat(u'Catégorie:Pluriels manquants en français', False, u'')
        # TODO: python touch.py -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"

if __name__ == "__main__":
    main(sys.argv)

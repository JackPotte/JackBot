#!/usr/bin/env python
# coding: utf-8
# This script creates the flexions from their lemma

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, os, re, socket, sys, urllib
import defaultSort, html2Unicode, hyperlynx, langues, WikiPage

debugLevel= 1
fileName = __file__
if debugLevel > 0: print fileName

#pb : pas de module avec un . dans le nom
#if fileName.rfind('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
#siteLanguage = fileName[0:2]
#siteFamily = fileName[3:]
#siteFamily = siteFamily[:siteFamily.find('.')]
siteLanguage = u'fr'
siteFamily = u'wiktionary'
if debugLevel > 1: print siteLanguage
if debugLevel > 1: print siteFamily
PWB = os.getcwd().find(u'Pywikibot') != -1

if PWB:
    import pywikibot
    from pywikibot import *
    from pywikibot import pagegenerators #pywikibot.flow
    username = u'JackBot'    #KeyError: 'fr'
else:
    from wikipedia import *
    username = config.usernames[site.family.name][site.lang]


def getWiki(language = 'fr', family = 'wiktionary'):
    if debugLevel > 1: print u'get ' + language + u'.' + family
    if PWB:
        return pywikibot.Site(language, family)
    else:
        return getSite(language, family)

def debug(chaine):
    try:
        print chaine
    except UnicodeError:
        print "UnicodeError"
    return

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

site = getWiki(siteLanguage, siteFamily)
siteSource = getWiki('en', siteFamily)
templateSource = u'en-past of'
textTranslated = u'Passé de'
DebutScan = u'interspersed'

def creationByTemplate(pageName, template):
    regex = ur'{{S\|([a-z \-]+)\|([a-z]+)}}'
    s = re.search(regex, template)
    if s:
        nature = s.group(1)
        codeLangue = s.group(2)
        creation(site, pageName, codeLangue, nature, template)
    else:
        print u' Template incomplet'


def creation(site, pageName, codeLangue, nature, template = None):
    if debugLevel > 0: print pageName.encode(config.console_encoding, 'replace')

    if template:
        pageSource = WikiPage.WikiPage(site, pageName)
        if pageSource.getContent() == u'':
            if debugLevel > 0: print u' création'
            PageBegin = u''
            headerFile = open(u'scripts/JackBot/fr.wiktionary.header-fr.txt', 'r')
            PageEnd = html2Unicode.html2Unicode("".join(headerFile.readlines())) + template
        else:
            PageBegin = pageSource.getContent()
            PageTemp = PageBegin
            PageEnd = u''
            if PageTemp.find(u'{{S|' + nature + u'|' + codeLangue + u'}}') == -1:
                if debugLevel > 0: print u' modification'
                PageEnd = pageSource.addText(PageTemp, codeLangue, nature, template)
            else:
                if debugLevel > 0: print u' aucun changement'
                PageEnd = PageTemp

        if PageBegin != PageEnd:
            PageEnd = PageEnd.replace(u'  ', u' ')
            PageEnd = PageEnd.replace(u"\n\n\n", u"\n\n")
            PageEnd = PageEnd.replace(u".\n=", u".\n\n=")
            summary = u'[[WT:RBOT]] : création de noms de famille depuis une liste'
            pageSource.save(PageEnd, summary)

    elif codeLangue == u'fr':
        page = Page(site, pageName)
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
        # à faire : ajouter Catégorie:Modèles d’accord en français

        try:
            PageSing = page.get()
        except wikipedia.NoPage:
            print u' NoPage l 40'
            return
        except wikipedia.IsRedirectPage:
            print u' IsRedirectPage l 43'
            return
        except wikipedia.BadTitle:
            print u' BadTitle l 46'
            return
        except wikipedia.InvalidPage:
            print u' InvalidPage l 49'
            return
        except wikipedia.ServerError:
            print u' ServerError l 52'
            return

        if PageSing.find(u'{{formater') != -1 or PageSing.find(u'{{SI|') != -1 or PageSing.find(u'{{SI}}') != -1 or PageSing.find(u'{{supp|') != -1 or PageSing.find(u'{{supp}}') != -1 or PageSing.find(u'{{supprimer|') != -1 or PageSing.find(u'{{supprimer') != -1 or PageSing.find(u'{{PàS') != -1 or PageSing.find(u'{{S|faute') != -1 or PageSing.find(u'{{S|erreur') != -1:
            if debugLevel > 0: print u'Page en travaux : non traitée l 60'
            return

        for m in range(0,len(Modele)):
            # Parcours de la page pour chaque modèle
            if debugLevel > 1: print ' d�but du for ' + str(m)
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
                        pageSource.save(page, PageSing, u'|mf=oui')
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
                        print ' Paramètre du modèle du lemme : ' + PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')

                page2 = Page(site,pluriel)
                if page2.exists():
                    try:
                        PagePluriel = page2.get()
                    except wikipedia.NoPage:
                        print u' NoPage l 120'
                        return
                    except wikipedia.IsRedirectPage:
                        print u' IsRedirectPage l 123'
                        return
                    except wikipedia.BadTitle:
                        print u' BadTitle l 126'
                        return
                    except wikipedia.InvalidPage:
                        print u' InvalidPage l 129'
                        return
                    except wikipedia.ServerError:
                        print u' ServerError l 132'
                        return
                    if PagePluriel.find(u'{{langue|' + Langue + u'}}') != -1:
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
                Modele = u'{{' + Modele[m] + pronM + H + MF + '|' + Param[m] + u'=' + pageName
                if pluriel != pageName + u's' and pluriel != pageName + u'x':
                    Modele += u'|p={{subst:PAGENAME}}'
                Modele += u'}}'
                PageEnd = u'== {{langue|fr}} ==\n=== {{S|' + nature + u'|fr|flexion}} ===\n' + Modele + u'\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pronM + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + pageName +']].\n'
                while PageEnd.find(u'{{pron|fr}}') != -1:
                    PageEnd = PageEnd[:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]

                if pluriel[len(pluriel)-2:len(pluriel)] == u'ss':
                    PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|' + Param[m] + u'=' + pluriel[:len(pluriel)-2] + PageSing[PageSing.find(Modele[m])+len(Modele[m]):len(PageSing)]
                    pageSource.save(page, PageSing, u'{{' + Modele[m] + u'|s=...}}')
                elif pluriel[len(pluriel)-2:len(pluriel)] == u'xs':
                    print u' Pluriel en xs'
                    return
                else:
                    PageEnd = PageEnd + u'\n' + PagePluriel
                    CleTri = defaultSort.defaultSort(pluriel)
                    if PageEnd.find(u'{{clé de tri') == -1 and CleTri != u'' and CleTri.lower() != pluriel.lower():
                        PageEnd = PageEnd +  u'\n{{clé de tri|' + CleTri + u'}}\n'
                    PageEnd = html2Unicode.html2Unicode(PageEnd)
                    pageSource.save(page2, PageEnd, summary)
                #raw_input(PageTemp.encode(config.console_encoding, 'replace'))
                if debugLevel > 1: print u'Fin du while'
            if debugLevel > 1: print u'Fin du for'
        
        
    else:
        pageSource = WikiPage.WikiPage(siteSource, pageName)
        PageTemp = pageSource.getContent()
        if PageTemp != u'':
            pageResult = WikiPage.WikiPage(site, pageName)

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
            if debugLevel > 0: print u' ' + codelangue
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
            pageLemme = WikiPage.WikiPage(site, mot[2:-2])
            PageLemme = pageLemme.getContent()
            if PageLemme == u'':
                print 'Page du lemme absente du Wiktionnaire'
                return
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

            Page1 = u'=={{langue|' + codelangue + u'}}==\n=== {{' + nature + u'|' + codelangue + u'|flexion}} ===\n\'\'\'' + page2.title() + u'\'\'\' {{pron|'+pron+'|' + codelangue + u'}}\n# \'\'Prétérit de\'\' ' + mot + u'.\n# \'\'Participe passé de\'\' ' + mot + u'.\n\n'
            summary = u'Importation depuis [[en:' + page2.title() + u']]'
            pageSource.save(page1, Page1, summary)

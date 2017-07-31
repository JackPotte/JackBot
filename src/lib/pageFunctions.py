#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# Global variables
defaultLevel = 0
site = pywikibot.Site('fr', 'wiktionary')
username = 'JackBot'


deprecatedTags = {}
deprecatedTags['big'] = 'strong'
deprecatedTags['center'] = 'div style="text-align: center;"'
deprecatedTags['font color *= *"?'] = 'span style="color:'
deprecatedTags['font face *= *"?'] = 'span style="font-family:'
deprecatedTags['font size *= *"?\+?\-?'] = 'span style="font-size:'
#deprecatedTags['font '] = 'span ' #TODO: ajouter des ";" entre plusieurs param
deprecatedTags['strike'] = 's'
deprecatedTags['tt'] = 'code'
deprecatedTags['BIG'] = 'strong'
deprecatedTags['CENTER'] = 'div style="text-align: center;"'
deprecatedTags['FONT COLOR *= *"?'] = 'span style="color:'
deprecatedTags['FONT SIZE *= *"?\+?'] = 'span style="font-size:'
deprecatedTags['STRIKE'] = 's'
deprecatedTags['TT'] = 'code'
fontSize = {}
fontSize[1] = 0.63
fontSize[2] = 0.82
fontSize[3] = 1.0
fontSize[4] = 1.13
fontSize[5] = 1.5
fontSize[6] = 2.0
fontSize[7] = 3.0
fontColor = []
fontColor.append('black')
fontColor.append('blue')
fontColor.append('green')
fontColor.append('orange')
fontColor.append('red')
fontColor.append('white')
fontColor.append('yellow')
fontColor.append('#808080')


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


#*** Tested functions ***
def isPatrolled(version):
    #TODO: extensions Patrolled Edits & Flagged Revisions
    if debugLevel > 1: print version  #eg: [{u'timestamp': u'2017-07-25T02:26:15Z', u'user': u'27.34.18.159'}]
    if debugLevel > 0: print ' user: ' + version[0]['user']
    return False
    #admins = site.allusers(group='sysop')  #<pywikibot.data.api.ListGenerator object at 0x7f6ebc521fd0>
    #patrollers = site.allusers(group='patrollers')

def getLineNumber():
    # Bug des n° de lignes auto
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    return str(frameinfo.lineno)

def testAdd(PageHS, summary = '', site = site):
    page1 = Page(site, PageHS)
    try:
        PageBegin = page1.get()
    except pywikibot.exceptions.NoPage:
        print 'NoPage'
    PageEnd = PageBegin
    codelangue = u'fr'
    
    PageEnd = addLine(PageEnd, codelangue, u'prononciation', u'* {{écouter|||lang=fr|audio=test.ogg}}')
    PageEnd = addLine(PageEnd, codelangue, u'prononciation', u'* {{écouter|||lang=fr|audio=test2.ogg}}')
    PageEnd = addLine(PageEnd, codelangue, u'catégorie', u'Tests en français')
    PageEnd = addLine(PageEnd, codelangue, u'catégorie', u'[[Catégorie:Tests en français]]')
    PageEnd = addLine(PageEnd, codelangue, u'clé de tri', u'test')
    PageEnd = addLine(PageEnd, codelangue, u'étymologie', u':{{étyl|test|fr}}')
    if debugLevel > 1: raw_input(u'Fin')
    if PageEnd != PageBegin: savePage(page1, PageEnd, summary)

def replaceDepretacedTags(PageTemp):
    if debugLevel > 0: print u'Remplacements des balises HTML'

    PageTemp = PageTemp.replace(u'</br>', u'<br/>')
    PageTemp = PageTemp.replace(u'<source lang="html4strict">', u'<source lang="html">')

    #TODO: {{citation}} https://fr.wikiversity.org/w/index.php?title=Matrice%2FD%C3%A9terminant&action=historysubmit&type=revision&diff=669911&oldid=664849
    #TODO: multiparamètre
    PageTemp = PageTemp.replace('<font size="+1" color="red">', ur'<span style="font-size:0.63em; color:red;>')
    regex = ur'<font color="?([^>"]*)"?>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(PageTemp):
        if debugLevel > 1: print u'Remplacement de ' + match.group(0) + u' par <span style="color:' + match.group(1) + u'">'
        PageTemp = PageTemp.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
        PageTemp = PageTemp.replace('</font>', u'</span>')

    for oldTag, newTag in deprecatedTags.items():
        if debugLevel > 1: print "Clé : %s, valeur : %s." % (oldTag, newTag)
        if oldTag.find(u' ') == -1:
            closingOldTag = oldTag
        else:
            closingOldTag = oldTag[:oldTag.find(u' ')]
        if newTag.find(u' ') == -1:
            closingNewTag = newTag
        else:
            closingNewTag = newTag[:newTag.find(u' ')]
        #regex = ur'<' + oldTag + ur'([^>]*)>([^\n]*)</' + closingOldTag + '>' # bug https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:-flex-nom-fam-/Documentation&diff=prev&oldid=24027702
        regex = ur'< *' + oldTag + ur'([^>]*) *>'
        if re.search(regex, PageTemp):
            #summary = summary + u', ajout de ' + newTag
            #PageTemp = re.sub(regex, ur'<' + newTag + ur'\1>', PageTemp)
            pattern = re.compile(regex, re.UNICODE)
            for match in pattern.finditer(PageTemp):
                if debugLevel > 0: print str(match.group(1))
                if newTag.find(u'font-size') != -1:
                    size = match.group(1).replace('"', '')
                    try:
                        size = int(size)
                        if size > 7: size = 7
                        openingTag = newTag + str(fontSize[size]) + ur'em"'
                    except ValueError:
                        openingTag = newTag + size + '"'
                else:
                    openingTag = newTag + match.group(1)
                PageTemp = PageTemp.replace(match.group(0), ur'<' + openingTag + ur'>')

        regex = ur'</ *' + closingOldTag + ' *>'
        PageTemp = re.sub(regex, ur'</' + closingNewTag + '>', PageTemp)
    PageTemp = PageTemp.replace('<strong">', ur'<strong>')
    PageTemp = PageTemp.replace('<s">', ur'<s>')
    PageTemp = PageTemp.replace('<code">', ur'<code>')
    PageTemp = PageTemp.replace(';"">', ur';">')

    # Fix
    regex = ur'<span style="font\-size:([a-z]+)>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(PageTemp):
        #summary = summary + u', correction de color'
        PageTemp = PageTemp.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
    PageTemp = PageTemp.replace('</font>', u'</span>')
    PageTemp = PageTemp.replace('</font>'.upper(), u'</span>')

    regex = ur'<span style="font\-size:(#[0-9]+)"?>'
    s = re.search(regex, PageTemp)
    if s:
        #summary = summary + u', correction de color'
        PageTemp = re.sub(regex, ur'<span style="color:' + s.group(1) + ur'">', PageTemp)

    regex = ur'<span style="text\-size:([0-9]+)"?>'
    s = re.search(regex, PageTemp)
    if s:
        #summary = summary + u', correction de font-size'
        PageTemp = re.sub(regex, ur'<span style="font-size:' + str(fontSize[int(s.group(1))]) + ur'em">', PageTemp)

    # Fix :
    regex = ur'(<span style="font\-size:[0-9]+px;">)[0-9]+px</span>([^<]*)</strong></strong>'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1 \2</span>', PageTemp)

    PageTemp = PageTemp.replace(u'<strong><strong><strong><strong><strong><strong>', u'<span style="font-size:75px;">')
    PageTemp = PageTemp.replace(u'<strong><strong><strong><strong><strong>', u'<span style="font-size:50px;">')
    PageTemp = PageTemp.replace(u'<strong><strong><strong><strong>', u'<span style="font-size:40px;">')
    PageTemp = PageTemp.replace(u'<strong><strong><strong>', u'<span style="font-size:25px;">')
    PageTemp = PageTemp.replace(u'<strong><strong>', u'<span style="font-size:20px;">')
    PageTemp = re.sub(ur'</strong></strong></strong></strong></strong></strong>', ur'</span>', PageTemp)
    PageTemp = re.sub(ur'</strong></strong></strong></strong></strong>', ur'</span>', PageTemp)
    PageTemp = re.sub(ur'</strong></strong></strong></strong>', ur'</span>', PageTemp)
    PageTemp = re.sub(ur'</strong></strong></strong>', ur'</span>', PageTemp)
    PageTemp = re.sub(ur'</strong></strong>', ur'</span>', PageTemp)
    regex = ur'<strong>([^<]*)</span>'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'<strong>\1</strong>', PageTemp)
    regex = ur'<strong><span ([^<]*)</span></span>'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'<strong><span \1</span></strong>', PageTemp)
    #PageTemp = re.sub(ur'</span></span>', ur'</span>', PageTemp)

    return PageTemp

def replaceFilesErrors(PageTemp):
    #https://fr.wiktionary.org/wiki/Sp%C3%A9cial:LintErrors/bogus-image-options
    badFileParameters = []
    badFileParameters.append(u'')
    #badFileParameters.append(u'cadre')
    for badFileParameter in badFileParameters:
        regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *' + badFileParameter + ur' *(\||\])'
        if debugLevel > 1: print regex
        PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    # Doublons
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *thumb *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *vignette *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *vignette *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *thumb *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    return PageTemp


#*** Wiktionary functions ***
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


def addLine(Page, CodeLangue, Section, pageContent):
    if Page != '' and CodeLangue != '' and Section != '' and pageContent != '':
        if Page.find(pageContent) == -1 and Page.find(u'{{langue|' + CodeLangue + '}}') != -1:
            if Section == u'catégorie' and pageContent.find(u'[[Catégorie:') == -1: pageContent = u'[[Catégorie:' + pageContent + u']]'
            if Section == u'clé de tri' and pageContent.find(u'{{clé de tri|') == -1: pageContent = u'{{clé de tri|' + pageContent + '}}'

            # Recherche de l'ordre théorique de la section à ajouter
            NumSection = sectionNumber(Section)
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
            PageTemp2 = Page[Page.find(u'{{langue|' + CodeLangue + '}}')+len(u'{{langue|' + CodeLangue + '}}'):]
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
            while o < len(SectionPage) and str(SectionPage[o][0].encode(config.console_encoding, 'replace')) != 'langue' and sectionNumber(SectionPage[o][0]) <= NumSection:
                if debugLevel > 0:
                    print SectionPage[o][0]
                    print sectionNumber(SectionPage[o][0])
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
                print u' (car ' + str(sectionNumber(SectionLimite)) + u' > ' + str(NumSection) + u')'
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

def sectionNumber(Section):
    if debugLevel > 0: print u'sectionNumber()'
    if debugLevel > 1:
        print u''
        print Section
        print Sections[0]
        raw_input(Section == Sections[0])
    #UnicodeDecodeError: 'ascii' codec can't decode byte 0x82 in position 1: ordinal not in range(128)
    #if isinstance(Section, str): Section = Section
    #if isinstance(Section, str): Section = Section.encode(config.console_encoding, 'replace')
    #if isinstance(Section, str): Section = Section.encode('utf-8')
    #if isinstance(Section, str): Section = Section.decode('ascii')
    #if isinstance(Section, str): Section = Section.decode('ascii').encode(config.console_encoding, 'replace')
    #if isinstance(Section, str): Section = Section.decode('ascii').encode('utf-8')
    #if isinstance(Section, str): Section = unicode(Section)
    #if isinstance(Section, unicode): Section = Section.decode("utf-8")
    
    s = 0
    while s < len(Sections) and Section != Sections[s]:
        s = s + 1
    if s >= len(Sections):
        if debugLevel > 0: print u' ' + Section + u' non trouvé'
        s = 1    # pour éviter de lister les natures grammaticales
    if debugLevel > 1:
        print u''
        print Section
        print u' = ' + str(s)
        print u''
    return s

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


#*** General functions ***
def setGlobals(myDebugLevel, mySite, myUsername):
    global debugLevel
    global site
    global username
    debugLevel  = myDebugLevel
    site        = mySite
    username    = myUsername 

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def datePlusMonth(months):
	year, month, day = datetime.date.today().timetuple()[:3]
	new_month = month + months
	if new_month == 0:
		new_month = 12
		year = year - 1
	elif new_month == -1:
		new_month = 11
		year = year - 1
	elif new_month == -2:
		new_month = 10
		year = year - 1
	elif new_month == -3:
		new_month = 9
		year = year - 1
	elif new_month == -4:
		new_month = 8
		year = year - 1
	elif new_month == -5:
		new_month = 7
		year = year - 1
	if new_month == 2 and day > 28: day = 28
	return datetime.date(year, new_month, day)

def timeAfterLastEdition(page, site = None):
    # Timestamp au format Zulu de la dernière version
    lastEditTime = page.getVersionHistory()[0][1]
    if debugLevel > 1: print lastEditTime   # 2017-07-29T21:57:34Z
    matchTime = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(lastEditTime))
    # Mise au format "datetime" du timestamp de la dernière version
    dateLastEditTime = datetime.datetime(int(matchTime.group(1)), int(matchTime.group(2)), int(matchTime.group(3)),
        int(matchTime.group(4)), int(matchTime.group(5)), int(matchTime.group(6)))
    datetime_now = datetime.datetime.utcnow()
    diff_last_edit_time = datetime_now - dateLastEditTime

    # Ecart en minutes entre l'horodotage actuelle et l'horodotage de la dernière version
    return diff_last_edit_time.seconds/60 + diff_last_edit_time.days*24*60

def hasMoreThanTime(page, timeAfterLastEdition = 60): # minutes
    version = page.getLatestEditors(1)
    dateNow = datetime.datetime.utcnow()
    maxDate = dateNow - datetime.timedelta(minutes=timeAfterLastEdition)
    if debugLevel > 1:
        print maxDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        print version[0]['timestamp']
        print version[0]['timestamp'] < maxDate.strftime('%Y-%m-%dT%H:%M:%SZ')   
    if version[0]['timestamp'] < maxDate.strftime('%Y-%m-%dT%H:%M:%SZ') or username in page.title() or page.contributors(total=1).keys()[0] == 'JackPotte':
        return True
    if debugLevel > 0: print u' dernière version trop récente ' + version[0]['timestamp']
    return False

def isTrustedVersion(page, site = site):
    firstEditor = page.oldest_revision['user']
    lastEditor = page.contributors(total=1).keys()[0]
    if firstEditor == lastEditor:
        if debugLevel > 0: print u'Page crée et modifiée par ' + lastEditor
        return True
    userPage = u' user: ' + lastEditor
    page = Page(site, userPage)
    user = User(page)
    if u'autoconfirmed' in user.groups():
        if debugLevel > 0: print u'Page modifiée par l\'utilisateur autoconfirmed ' + lastEditor
        return True
    return False

def searchDoubles(PageTemp, parameter):
    if debugLevel > 0: u' Recherche de doublons dans le modèle : ' + parameter[1]
    PageEnd = u''
    regex = ur'{{' + parameter[1] + ur'[^\n]*{{' + parameter[1]
    while re.search(regex, PageTemp):
        raw_input(PageTemp[re.search(regex, PageTemp).start():re.search(regex, PageTemp).end()].encode(config.console_encoding, 'replace'))
    return PageEnd + PageTemp

def getContentFromPageName(pageName, allowedNamespaces = None, site = site):
    page = Page(site, pageName)
    return getContentFromPage(page, allowedNamespaces)

def getContentFromPage(page, allowedNamespaces = None, username = username):
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

def getWiki(language, family, site = site):
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

def addParameter(PageTemp, parameter, content = None):
    PageEnd = u''
    if parameter == u'titre' and content is None:
        # Détermination du titre d'un site web
        URL = getParameter(u'url')
        PageEnd = PageTemp

    else:
        print 'en travaux'
    return PageEnd
        
def replaceParameterValue(PageTemp, template, parameterKey, oldValue, newValue):
    regex = ur'({{ *(' + template[:1].lower() + ur'|' + template[:1].upper() + ur')' + template[1:] + ur' *\n* *\|[^}]*' + parameterKey + ur' *= *)' + oldValue
    if debugLevel > 0: print regex
    PageTemp = re.sub(regex, ur'\1' + newValue, PageTemp)

    return PageTemp

def log(source):        
    txtfile = codecs.open(u'JackBot.log', 'a', 'utf-8')
    txtfile.write(u'\n' + source + u'\n')
    txtfile.close()

def ArretDUrgence(username = username):
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
        if currentPage.title().find(u'JackBot/') == -1: ArretDUrgence()
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

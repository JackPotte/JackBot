#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

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


def setGlobalsWiktionary(myDebugLevel, mySite, myUsername):
    global debugLevel
    global site
    global username
    debugLevel  = myDebugLevel
    site        = mySite
    username    = myUsername 
    
def getFirstLemmaFromLocution(pageName):
    if debugLevel > 0: print u'\ngetFirstLemmaFromLocution'
    lemmaPageName = ''
    if pageName.find(u' ') != -1:
        if debugLevel > 0: print u' lemme de locution trouvé : ' + lemmaPageName
        lemmaPageName = pageName[:pageName.find(u' ')]
    return lemmaPageName

def getGenderFromPageName(pageName, languageCode = 'fr', nature = None):
    if debugLevel > 0: print u'\ngetGenderFromPageName'
    gender = u''
    pageContent = getContentFromPageName(pageName)
    if pageContent.find(u'|' + languageCode + '}} {{m}}') != -1:
        gender = u'{{m}}'
    elif pageContent.find(u'|' + languageCode + '}} {{f}}') != -1:
        gender = u'{{f}}'
    elif pageContent.find(u"''' {{m}}") != -1:
        gender = u'{{m}}'
    elif pageContent.find(u"''' {{f}}") != -1:
        gender = u'{{f}}'
    if debugLevel > 1: raw_input(gender)
    return gender

def getLemmaFromContent(pageContent, languageCode = 'fr'):
    lemmaPageName = getLemmaFromPlural(pageContent, languageCode)
    if lemmaPageName == '':
        lemmaPageName = getLemmaFromConjugation(pageContent, languageCode)
    return lemmaPageName

def getLemmaFromPlural(pageContent, languageCode = 'fr', natures = ['nom', 'adjectif', 'suffixe']):
    if debugLevel > 0: print u'\ngetLemmaFromPlural'
    lemmaPageName = u''
    regex = ur"(=== {{S\|(" + '|'.join(natures) + ")\|" + languageCode + "\|flexion}} ===\n({{" + languageCode + \
     "\-[^}]*}}\n)?'''[^\n]+\n# *'* *([Mm]asculin|[Ff]éminin)* *'* *'*[P|p]luriel *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, pageContent)
    if s:
        if debugLevel > 1:
            print(s.group(1).encode(config.console_encoding, 'replace')) # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            raw_input(s.group(6).encode(config.console_encoding, 'replace'))
        lemmaPageName = s.group(6)
    if debugLevel > 0: pywikibot.output(u" lemmaPageName found: \03{red}" + lemmaPageName + "\03{default}")
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return lemmaPageName

def getLemmaFromFeminine(pageContent, languageCode = 'fr', natures = ['nom', 'adjectif']):
    if debugLevel > 0: print u'\ngetLemmaFromFeminine'
    lemmaPageName = u''
    regex = ur"(=== {{S\|(" + '|'.join(natures) + ")\|" + languageCode + "\|flexion}} ===\n({{" + languageCode + \
     "\-[^}]*}}\n)?'''[^\n]+\n# *'* *[Ff]éminin *'* *'*(singulier|pluriel)? *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, pageContent)
    if s:
        if debugLevel > 1:
            print(s.group(1).encode(config.console_encoding, 'replace')) # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            raw_input(s.group(6).encode(config.console_encoding, 'replace'))
        lemmaPageName = s.group(6)
    if debugLevel > 0: pywikibot.output(u" lemmaPageName found: \03{red}" + lemmaPageName + "\03{default}")
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return lemmaPageName  

def getLemmaFromConjugation(pageContent, languageCode = 'fr'):
    if debugLevel > 0: print u'\ngetLemmaFromConjugation'
    lemmaPageName = u''
    regex = ur"(=== {{S\|verbe\|fr\|flexion}} ===\n({{fr\-[^}]*}}\n)*'''[^\n]+\n#[^\n\[{]+(\[\[|{{li?e?n?\|))([^#\|\]}]+)}*\]*'*\."
    s = re.search(regex, pageContent)
    if s:
        if debugLevel > 1:
            print(s.group(1).encode(config.console_encoding, 'replace')) # 2 fr-verbe-flexion, 3 = {{lien|, 4 = lemme
            raw_input(s.group(4).encode(config.console_encoding, 'replace'))
        lemmaPageName = s.group(4)
    if debugLevel > 0: pywikibot.output(u" lemmaPageName found: \03{red}" + lemmaPageName + "\03{default}")

    return lemmaPageName

def getFlexionTemplate(pageName, language, nature = None):
    if debugLevel > 1: print u'\ngetFlexionTemplate'
    flexionTemplate = u''
    if nature is None: nature = 'nom|adjectif|suffixe'
    pageContent = getContentFromPageName(pageName)
    regex = ur"=== {{S\|(" + nature + ur")\|" + language + ur"(\|flexion)?(\|num=[0-9])?}} ===\n{{(" + language + ur"\-[^}]+)}}"
    s = re.search(regex, pageContent)
    if s:
        if debugLevel > 1:
            if not s.group(1) is None: print u' ' + s.group(1) # Nature
            if not s.group(2) is None: print u' ' + s.group(2) # Flexion
            if not s.group(3) is None: print u' ' + s.group(3) # Number
            if not s.group(4) is None: print u' ' + s.group(4) # Template
        flexionTemplate = s.group(4)
    if debugLevel > 0: pywikibot.output(u" flexionTemplate found: \03{red}" + flexionTemplate + "\03{default}")
    # TODO
    if flexionTemplate.find('{{') != -1: flexionTemplate = u''
    if flexionTemplate.find(u'-inv') != -1: flexionTemplate = u''

    return flexionTemplate

def getFlexionTemplateFromLemma(pageName, language, nature):
    if debugLevel > 0: print u'\ngetFlexionTemplateFromLemma'
    FlexionTemplate = u''
    pageContent = getContentFromPageName(pageName)
    regex = ur"=== {{S\|" + nature + ur"\|" + language + ur"(\|num=[0-9])?}} ===\n{{(" + language + ur"\-[^}]+)}}"
    if debugLevel > 1: print u' ' + regex
    s = re.search(regex, pageContent)
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

def getLanguageSection(pageContent, languageCode):
    if pageContent.find(u'{{langue|' + languageCode + '}}') == -1: raw_input(' langue absente') #TODO
    regex = ur'\n=* *{{langue\|(^' + languageCode + ur')}}'
    position = len(pageContent)
    s = re.match(regex, pageContent)
    if s:
        print 'ok'
        position = s.start()
        pageContent = pageContent[:position]
        if debugLevel > 0: print position
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))
    return pageContent, position

def addCat(pageContent, languageCode, lineContent):
    if lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
    return addLine(pageContent, languageCode, 'catégorie', lineContent)

def addLine(pageContent, languageCode, Section, lineContent):
    d = 0
    if debugLevel > d:
        pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
        print u'\naddLine into "' + Section + '"'
    if pageContent != '' and languageCode != '' and Section != '' and lineContent != '':
        if pageContent.find(lineContent) == -1 and pageContent.find(u'{{langue|' + languageCode + '}}') != -1:
            if Section == u'catégorie' and lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
            if Section == u'clé de tri' and lineContent.find(u'{{clé de tri|') == -1: lineContent = u'{{clé de tri|' + lineContent + '}}'

            # Recherche de l'ordre théorique de la section à ajouter
            sectionToAddNumber = sectionNumber(Section)
            if sectionToAddNumber == len(Sections):
                if debugLevel > d:
                    print u' ajout de la sous-section : ' + Section.encode(config.console_encoding, 'replace') + u' dans une section inconnue'
                    print u'  (car ' + len(Sections) + u' = ' + str(sectionToAddNumber) + u')\n'
                return pageContent

            # Recherche de l'ordre réel de la section à ajouter
            languageSection, position = getLanguageSection(pageContent, languageCode)
            sectionsInPage = re.findall(ur"\n=+ *{{S\|?([^}/|]+)([^}]*)}}", languageSection)
            if debugLevel > d: raw_input(str(sectionsInPage))
            o = 0
            while o < len(sectionsInPage) and sectionNumber(sectionsInPage[o][0]) <= sectionToAddNumber:
                if debugLevel > d: print ' ' + sectionsInPage[o][0] + ' ' + str(sectionNumber(sectionsInPage[o][0]))
                o = o + 1
            if o > 0: o = o - 1
            if debugLevel > d:
                 print ' while ' + str(sectionNumber(sectionsInPage[o][0])) + ' <= ' + str(sectionToAddNumber) \
                  + ' and ' + str(o) + ' < ' + str(len(sectionsInPage)) + ' and ' + sectionsInPage[o][0] + ' != langue'

            #limitSection = str(sectionsInPage[o][0].encode(config.console_encoding, 'replace'))
            limitSection = sectionsInPage[o][0] # pb encodage : "étymologie" non fusionnée + "catégorie" = 1 au lieu de 20
            if languageSection.find(u'{{S|' + limitSection) == -1 and limitSection != 'langue':
                if debugLevel > d: print ' Erreur d\'encodage sur "' + limitSection + '"'
                if debugLevel > d: raw_input(languageSection.encode(config.console_encoding, 'replace'))
                return pageContent

            if limitSection == Section:
                if debugLevel > d: print u' ajout dans la sous-section existante "' + Section.encode(config.console_encoding, 'replace') + u'"'
                print u' (car ' + str(sectionNumber(limitSection)) + u' = ' + str(sectionToAddNumber) + u')\n'
            elif not Section in [u'catégorie', u'clé de tri']:
                sectionToAdd = u'\n\n' + Niveau[sectionToAddNumber] + u' {{S|' + Section + u'}} ' + Niveau[sectionToAddNumber] + u'\n'
                if sectionToAddNumber >= sectionNumber(limitSection):
                    if debugLevel > d:
                        print u' ajout de la sous-section "' + Section + u'" après "' + limitSection + u'"'
                        print u'  (car ' + str(sectionToAddNumber) + u' > ' + str(sectionNumber(limitSection)) + u')'
                    regex = u'{{S\|' + limitSection + u'[\|}]'
                    s = re.search(regex, languageSection)
                    if limitSection == sectionsInPage[len(sectionsInPage)-1][0]:
                        if debugLevel > d: print u' ajout de la sous-section après la dernière de la section langue : ' + limitSection
                        categories = languageSection.find(u'\n[[Catégorie:')
                        defaultSort = languageSection.find(u'\n{{clé de tri|')
                        if categories != -1 and (categories < defaultSort or defaultSort == -1):
                            if debugLevel > d: print u'  avant les catégories'
                            pageContent = languageSection[:categories] + sectionToAdd + languageSection[categories:] \
                             + pageContent[position:]
                        elif defaultSort != -1:
                            if debugLevel > d: print u'  avant la clé de tri'
                            pageContent = languageSection[:defaultSort] + u'\n' + sectionToAdd \
                             + languageSection[defaultSort:] + pageContent[position:]
                        else:
                            if debugLevel > d: print u'  sans catégorie'
                            pageContent = languageSection + sectionToAdd + pageContent[position:]
                        if debugLevel > d+1: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                    else:
                        if debugLevel > d: print u' ajout de la sous-section "' + Section + u'" avant "' + sectionsInPage[o+1][0] + u'"'
                        regex = ur'\n=* *{{S\|' + sectionsInPage[o+1][0]
                        s = re.search(regex, languageSection)
                        if s:
                            pageContent = languageSection[:s.start()] + sectionToAdd + languageSection[s.start():] + pageContent[position:]
                            languageSection, position = getLanguageSection(pageContent, languageCode)
                        else:
                            raw_input(' bug section')
                    languageSection, position = getLanguageSection(pageContent, languageCode)
                else:
                    if debugLevel > d:
                        print u' ajout de "' + Section + u'" avant "' + limitSection + u'"'
                        print u'  (car ' + str(sectionToAddNumber) + u' < ' + str(sectionNumber(limitSection)) + u')'
                    regex = ur'\n=* *{{S\|' + limitSection
                    s = re.search(regex, languageSection)
                    if s:
                        pageContent = languageSection[:s.start()] + sectionToAdd + languageSection[s.start():] + pageContent[position:]
                        languageSection, position = getLanguageSection(pageContent, languageCode)
                    else:
                        raw_input(' bug section')
            if debugLevel > d+1: raw_input(pageContent.encode(config.console_encoding, 'replace'))
            if debugLevel > d+1: raw_input(languageSection.encode(config.console_encoding, 'replace'))

            regex = ur'\n=* *{{S\|' + Section
            s = re.search(regex, languageSection)
            if s:
                if debugLevel > d: print u' ajout dans la sous-section'
                finalSection = languageSection[s.end():]

            else:
                regex = ur'\n=* *{{S\|' + sectionsInPage[len(sectionsInPage)-1][0]
                s = re.search(regex, languageSection)
                if s:
                    if debugLevel > d: print u' ajout après les sous-sections'
                    finalSection = languageSection[s.end():]
                else:
                    raw_input(' bug de section')

            regex = ur'\n==* *{{S\|'
            s = re.search(regex, finalSection)
            if s:
                if debugLevel > d: print u' ajout avant la sous-section suivante'
                pageContent = languageSection[:-len(finalSection)] + finalSection[:s.start()] \
                 + lineContent + u'\n' + finalSection[s.start():] + pageContent[position:]
            else:
                categories = languageSection.find(u'\n[[Catégorie:')
                defaultSort = languageSection.find(u'\n{{clé de tri|')
                if categories != -1 and (categories < defaultSort or defaultSort == -1):
                    if debugLevel > d: print u' ajout avant les catégories'
                    pageContent = languageSection[:languageSection.find(u'\n[[Catégorie:')] + u'\n' + lineContent \
                     + languageSection[languageSection.find(u'\n[[Catégorie:'):] + pageContent[position:]
                elif defaultSort != -1:
                    if debugLevel > d: print u' ajout avant la clé de tri'
                    pageContent = languageSection[:languageSection.find(u'\n{{clé de tri|')] \
                     + u'\n' + lineContent + languageSection[languageSection.find(u'\n{{clé de tri|'):] + pageContent[position:]
                else:
                    if debugLevel > d: print u' ajout en fin de section langue'
                    pageContent = languageSection + u'\n' + lineContent + u'\n' + pageContent[position:]

    pageContent = pageContent.replace(u'\n\n* {{écouter|', u'\n* {{écouter|')
    if debugLevel > d: pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
    return pageContent

def addLineTest(pageContent, languageCode = 'fr'):
    pageContent = addCat(pageContent, languageCode, u'Tests en français')
    pageContent = addLine(pageContent, languageCode, u'prononciation', u'* {{écouter|||lang=fr|audio=test.ogg}}')
    pageContent = addLine(pageContent, languageCode, u'prononciation', u'* {{écouter|||lang=fr|audio=test2.ogg}}')
    pageContent = addLine(pageContent, languageCode, u'étymologie', u':{{étyl|test|fr}}')
    pageContent = addLine(pageContent, languageCode, u'traductions', u'{{trad-début}}\n123\n{{trad-fin}}')
    return pageContent

def addPronunciation(pageContent, CodeLangue, Section, lineContent):
    if pageContent != '' and CodeLangue != '' and Section != '' and lineContent != '':
        if pageContent.find(lineContent) == -1 and pageContent.find(u'{{langue|' + CodeLangue + '}}') != -1:
            if Section == u'catégorie' and lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
            if Section == u'clé de tri' and lineContent.find(u'{{clé de tri|') == -1: lineContent = u'{{clé de tri|' + lineContent + '}}'

            # Recherche de l'ordre théorique de la section à ajouter
            NumSection = sectionNumber(Section)
            if NumSection == len(Sections):
                if debugLevel > 0:
                    print u' ajout de ' + Section + u' dans une section inconnue'
                    print u'  (car ' + len(Sections) + u' = ' + str(NumSection) + u')'
                return pageContent
            if debugLevel > 1: print u' position S : ' + s

            # Recherche de l'ordre réel de la section à ajouter
            lineContent2 = pageContent[pageContent.find(u'{{langue|' + CodeLangue + '}}')+len(u'{{langue|' + CodeLangue + '}}'):]
            #sectionsInPage = re.findall("{{S\|([^}]+)}}", lineContent2) # OK mais il faut trouver le {{langue}} de la limite de fin
            sectionsInPage = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", lineContent2)
            o = 0
            # pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
            while o < len(sectionsInPage) and sectionsInPage[o][0] != 'langue' \
             and sectionNumber(sectionsInPage[o][0]) <= NumSection:
                if debugLevel > 0:
                    print ' ' + sectionsInPage[o][0] + ' ' + str(sectionNumber(sectionsInPage[o][0]))
                o = o + 1
            if debugLevel > 0: print ' ' + str(len(sectionsInPage)) + ' >? ' + str(o)
            if o == len(sectionsInPage):
                if debugLevel > 0: print ' section à ajouter en fin de page'
                pageContent = pageContent + u'\n' + lineContent
            else:
                SectionLimite = str(sectionsInPage[o][0].encode(config.console_encoding, 'replace'))
                o = o - 1
                if debugLevel > 1: print u' position O : ' + o
                if debugLevel > 0:
                    print u' ajout de ' + Section + u' avant ' + SectionLimite
                    print u'  (car ' + str(sectionNumber(SectionLimite)) + u' > ' + str(NumSection) + u')'

                # Ajout après la section trouvée
                if lineContent2.find(u'{{S|' + sectionsInPage[o][0]) == -1:
                    print 'Erreur d\'encodage'
                    return

                lineContent3 = lineContent2[lineContent2.find(u'{{S|' + sectionsInPage[o][0]):]
                if sectionsInPage[o][0] != Section and Section != u'catégorie' and Section != u'clé de tri':
                    if debugLevel > 0: print u' ajout de la section ' + sectionsInPage[o][0]
                    lineContent = u'\n' + Niveau[NumSection] + u' {{S|' + Section + u'}} ' + Niveau[NumSection] + u'\n' + lineContent
                else:
                     if debugLevel > 0: print u' ajout dans la section existante'

                # Ajout à la ligne
                if lineContent3.find(u'\n==') == -1:
                    regex = ur'\n\[\[\w?\w?\w?:'
                    if re.compile(regex).search(pageContent):
                        interwikis = re.search(regex, pageContent).start()
                        categories = pageContent.find(u'\n[[Catégorie:')
                        defaultSort = pageContent.find(u'\n{{clé de tri|')

                        if (interwikis < categories or categories == -1) and (interwikis < defaultSort or defaultSort == -1):
                            if debugLevel > 0: print u' ajout avant les interwikis'
                            try:
                                pageContent = pageContent[:interwikis] + u'\n' + lineContent + u'\n' + pageContent[interwikis:]
                            except:
                                print u' pb regex interwiki'
                        elif categories != -1 and (categories < defaultSort or defaultSort == -1):
                            if debugLevel > 0: print u' ajout avant les catégories'
                            pageContent = pageContent[:pageContent.find(u'\n[[Catégorie:')] + lineContent + pageContent[pageContent.find(u'\n[[Catégorie:'):]
                        elif defaultSort != -1:
                            if debugLevel > 0: print u' ajout avant la clé de tri'
                            pageContent = pageContent[:pageContent.find(u'\n{{clé de tri|')] + lineContent + pageContent[pageContent.find(u'\n{{clé de tri|'):]
                        else:
                            if debugLevel > 0: print u' ajout en fin de page'
                            pageContent = pageContent + lineContent
                    else:
                        if debugLevel > 0: print u' ajout en fin de page'
                        pageContent = pageContent + lineContent
                else:
                    pageContent = pageContent[:-len(lineContent2)] + lineContent2[:-len(lineContent3)] + lineContent3[:lineContent3.find(u'\n\n')] \
                     + u'\n' + lineContent + u'\n' + lineContent3[lineContent3.find(u'\n\n'):]
        if pageContent.find(u'\n* {{écouter|') != -1 and pageContent.find(u'=== {{S|prononciation}} ===') == -1:
            pageContent = pageContent.replace(u'\n* {{écouter|', u'\n\n=== {{S|prononciation}} ===\n* {{écouter|')    
    return pageContent

def addLineIntoSection(pageContent, languageCode, Section, lineContent):
    d = 0
    if debugLevel > d:
        pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
        print u'\naddLineIntoSection "' + Section + '"'
    if pageContent != '' and languageCode != '' and Section != '' and lineContent != '':
        if pageContent.find(lineContent) == -1 and pageContent.find(u'{{langue|' + languageCode + '}}') != -1:
            if Section == u'catégorie' and lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
            if Section == u'clé de tri' and lineContent.find(u'{{clé de tri|') == -1: lineContent = u'{{clé de tri|' + lineContent + '}}'
    sections = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", pageContent)
    # TODO: complete parsing
    raw_input(str(sections))
    return pageContent

def sectionNumber(Section):
    if debugLevel > 1: print u'sectionNumber()'
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
        if debugLevel > 1: print u' ' + Section + u' non trouvé'
        s = 1 # Grammatical natures (ex: nom)
    if debugLevel > 1:
        print u''
        print Section
        print u' = ' + str(s)
        print u''
    return s
    
def nextTemplate(finalPageContent, currentPageContent, currentTemplate = None, languageCode = None):
    if languageCode is None:
        finalPageContent = finalPageContent + currentPageContent[:currentPageContent.find('}}')+2]
    else:
        finalPageContent = finalPageContent + currentTemplate + "|" + languageCode + '}}'
    currentPageContent = currentPageContent[currentPageContent.find('}}')+2:]
    return finalPageContent, currentPageContent

def nextTranslationTemplate(finalPageContent, currentPageContent, result = u'-'):
    finalPageContent = finalPageContent + currentPageContent[:len(u'trad')] + result
    currentPageContent = currentPageContent[currentPageContent.find(u'|'):]
    return finalPageContent, currentPageContent

def removeFalseHomophones(pageContent, languageCode, pageName, relatedPageName, summary):
    if debugLevel > 0: print u'\nremoveFalseHomophones(' + relatedPageName + u')'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *'''" + pageName + ur"''' *{{cf\|[^\|]*\|?" + relatedPageName + ur"[\|}][^\n]*\n"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, "==== {{S|homophones|" + languageCode + u"}} ====\n", pageContent)
        summary = summary + u', homophone erroné'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *\[\[[^}\n]+{{cf\|[^\|]*\|?" + relatedPageName + ur"[\|}][^\n]*\n?"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, "==== {{S|homophones|" + languageCode + u"}} ====\n", pageContent)
        summary = summary + u', homophone erroné'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *\[\[" + relatedPageName + ur"\]\](\n|$)"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, "==== {{S|homophones|" + languageCode + u"}} ====\n", pageContent)
        summary = summary + u', homophone erroné'

    regex = ur"=== {{S\|prononciation}} ===\n==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
    if re.search(regex, pageContent): pageContent = re.sub(regex, ur'\1', pageContent)
    regex = ur"==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
    if re.search(regex, pageContent): pageContent = re.sub(regex, ur'\1', pageContent)

    return pageContent, summary

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

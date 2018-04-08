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

# https://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Mod%C3%A8les_d%E2%80%99accord_en_fran%C3%A7ais
flexionTemplatesFrWithMs = []
flexionTemplatesFrWithMs.append(u'fr-accord-ain')
flexionTemplatesFrWithMs.append(u'fr-accord-al')
flexionTemplatesFrWithMs.append(u'fr-accord-an')
flexionTemplatesFrWithMs.append(u'fr-accord-cons')
flexionTemplatesFrWithMs.append(u'fr-accord-eau')
flexionTemplatesFrWithMs.append(u'fr-accord-el')
flexionTemplatesFrWithMs.append(u'fr-accord-en')
flexionTemplatesFrWithMs.append(u'fr-accord-er')
flexionTemplatesFrWithMs.append(u'fr-accord-et')
flexionTemplatesFrWithMs.append(u'fr-accord-in')
flexionTemplatesFrWithMs.append(u'fr-accord-mixte')
flexionTemplatesFrWithMs.append(u'fr-accord-on')
flexionTemplatesFrWithMs.append(u'fr-accord-ot')
flexionTemplatesFrWithMs.append(u'fr-accord-rég')
flexionTemplatesFrWithMs.append(u'fr-accord-s')
flexionTemplatesFrWithMs.append(u'fr-accord-un')

flexionTemplatesFrWithS = []
flexionTemplatesFrWithS.append(u'fr-rég')
flexionTemplatesFrWithS.append(u'fr-rég-x')

flexionTemplatesFr = []
flexionTemplatesFr.append(u'fr-accord-comp')
flexionTemplatesFr.append(u'fr-accord-comp-mf')
flexionTemplatesFr.append(u'fr-accord-eur')
flexionTemplatesFr.append(u'fr-accord-eux')
flexionTemplatesFr.append(u'fr-accord-f')
flexionTemplatesFr.append(u'fr-accord-ind')
flexionTemplatesFr.append(u'fr-accord-mf')
flexionTemplatesFr.append(u'fr-accord-mf-ail')
flexionTemplatesFr.append(u'fr-accord-mf-al')
flexionTemplatesFr.append(u'fr-accord-oux')
flexionTemplatesFr.append(u'fr-accord-personne')
flexionTemplatesFr.append(u'fr-accord-t-avant1835')
flexionTemplatesFr.append(u'fr-inv')

# https://fr.wiktionary.org/wiki/Module:types_de_mots/data
natures = [u'adjectif', u'adverbe', u'article', u'conjonction', u'copule', u'déterminant', u'nom', u'patronyme', \
    u'prénom', u'préposition', u'pronom', u'verbe', u'interjection', u'onomatopée', u'affixe', u'circonfixe' u'infixe', \
    u'interfixe', u'particule', u'postposition', u'préfixe', u'radical', u'suffixe', u'pré-verbe' u'pré-nom', \
    u'enclitique', u'proclitique', u'locution', u'proverbe', u'quantificateur', u'lettre', u'symbole', u'classificateur', \
    'numéral', u'sinogramme', u'erreur', u'gismu', u'rafsi', u'nom propre']

# https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_définitions
definitionTemplates = [u'abréviation de', u'comparatif de', u'exclamatif de', u'mutation de', u'superlatif de', \
    u'variante de', u'variante ortho de', u'variante orthographique de']

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

def getPageLanguages(pageContent):
    if debugLevel > 0: print u'\ngetPageLanguages()'
    regex = ur'{{langue\|([^}]+)}}'
    s = re.findall(regex, pageContent, re.DOTALL)
    if s: return s
    return []

def getLanguageSection(pageContent, languageCode = 'fr'):
    if debugLevel > 0: print u'\ngetLanguageSection(' + languageCode + u')'
    startPosition = 0
    endPosition = len(pageContent)

    regex = ur'=* *{{langue\|' + languageCode + '}}'
    s = re.search(regex, pageContent)
    if not s:
        if debugLevel > 0: print(' missing language!')
        return None, startPosition, endPosition

    startPosition = s.start()
    pageContent = pageContent[s.start():]
    regex = ur'\n== *{{langue\|(?!' + languageCode + ur').*}} *='
    s = re.search(regex, pageContent) #, re.MULTILINE
    if s:
        endPosition = s.start()
        pageContent = pageContent[:endPosition]
        if debugLevel > 1: print endPosition
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return pageContent, startPosition, endPosition

def getSections(pageContent):
    if debugLevel > 0: print u'\ngetSections()'
    regex = ur'{{S\|([^}\|]+)'
    s = re.findall(regex, pageContent, re.DOTALL)
    if s: return s
    return []

def getNotNaturesSections(pageContent):
    if debugLevel > 0: print u'\ngetNaturesSections()'
    sections = getSections(pageContent)
    return [item for item in sections if item not in natures]

def getNaturesSections(pageContent):
    if debugLevel > 0: print u'\ngetNaturesSections()'
    sections = getSections(pageContent)
    notNaturesSections = getNotNaturesSections(pageContent)
    return [item for item in sections if item not in notNaturesSections]

def getSection(pageContent, sectionName):
    if debugLevel > 0: print u'\ngetSection(' + sectionName + u')'
    startPosition = 0
    endPosition = len(pageContent)

    regex = ur'=* *{{S\|' + sectionName + ur'(\||})'
    s = re.search(regex, pageContent) # , re.DOTALL
    if not s:
        if debugLevel > 0: print(' missing section!')
        return None, startPosition, endPosition

    startPosition = s.start()
    pageContent = pageContent[s.start():]
    regex = ur'\n=* *{{S\|(?!' + sectionName + ur').*}} *='
    s = re.search(regex, pageContent, re.DOTALL)
    if s:
        endPosition = s.start()
        pageContent = pageContent[:endPosition]
        if debugLevel > 1: print endPosition
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return pageContent, startPosition, endPosition

def getDefinitions(pageContent):
    if debugLevel > 0: print u'\ngetDefinitions'
    if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
    regex = ur"\n'''[^\n]*\n(#.*?(\n\n|\n=|$))"
    s = re.search(regex, pageContent, re.DOTALL)
    if s is None:
        if debugLevel > 1: print 'No definition'
        return None
    if debugLevel > 1: print s.group(1)
    return s.group(1)

def countDefinitions(pageContent):
    if debugLevel > 0: print u'\ncountDefinitions'
    definitions = getDefinitions(pageContent)
    if definitions is None: return 0
    definitions = definitions.split('\n')
    total = 0
    for definition in definitions:
        if definition[:1] == u'#' and definition[:2] not in [u'#:', u'#*']:
            total += 1
    return total

def countFirstDefinitionSize(pageContent):
    if debugLevel > 0: print u'\ncountFirstDefinitionSize'
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    definition = getDefinitions(pageContent)
    if definition is None: return 0
    if definition.find(u'\n') != -1: definition = definition[:definition.find(u'\n')]
    if debugLevel > 1:
        print u' First definition:' #regex = ur"\n'''[^\n]*(\n#(!:\*)?.*(\n|$))"
        raw_input(definition.encode(config.console_encoding, 'replace'))

    regex = ur'^#( *{{[^}]*}})?( *{{[^}]*}})? *\[\[[^\]]+\]\]\.?$'
    if re.search(regex, definition):
        if debugLevel > 0: print u' The definition is just one link to another article'
        return 1

    regex = ur' *({{[^}]*}}|\([^\)]*\) *\.?)'
    definition = re.sub(regex, '', definition)
    if debugLevel > 1:
        print u' Parsed definition:'
        raw_input(definition.encode(config.console_encoding, 'replace'))
    words = definition.split(' ')
    if debugLevel > 0: print len(words)
    return len(words)

def getPronunciationFromContent(pageContent, languageCode, nature = None):
    regex = ur".*'''([^']+)'''.*"
    s = re.search(regex, pageContent, re.MULTILINE| re.DOTALL)
    if not s: return
    pageName = s.group(1)

    # Template {{pron}}
    regex = ur"{{pron\|([^}]+)\|" + languageCode + "}}"
    s = re.search(regex, pageContent)
    pronunciation = ''
    if s:
        pronunciation = s.group(1)
        pronunciation = pronunciation[:pronunciation.find(u'=')]
        pronunciation = pronunciation[:pronunciation.rfind(u'|')]
        if debugLevel > 0: raw_input(u' prononciation en ' + languageCode + u' : ' + pronunciation)
        pageContent = re.sub(ur'{{pron\|\|' + languageCode + '}}', \
            ur'{{pron|'+ pronunciation + ur'|' + languageCode + '}}', pageContent)
        return pronunciation

    # Templates {{fr-xxx}}
    if languageCode == 'fr':
        templates = '|'.join(flexionTemplatesFrWithS) + '|' + '|'.join(flexionTemplatesFrWithMs)
        templates2 = '|'.join(flexionTemplatesFr)
    else:
        return

    #TODO: templateContent = getTemplateContent(pageContent, template) ?
    regex = ur'{{(' + templates.replace('-', '\-') + u")\|([^{}\|=]+)([^{}]*}}\n\'\'\'" \
        + re.escape(pageName).replace(u'User:', u'') + ur"'\'\')( *{*f?m?n?}* *)\n"
    s = re.search(regex, pageContent)
    if s:
        pronunciation = s.group(1)
        if debugLevel > 0: print u' prononciation trouvée en {{{1}}} dans une boite de flexion : ' + pronunciation
        pageContent = re.sub(regex, ur'{{\1|\2\3 {{pron|\2|' + languageCode + '}}\4\n', pageContent)
        return pronunciation

    regex = ur'{{(' + templates.replace('-', '\-') + u")\|([^{}]+)}}"
    s = re.search(regex, pageContent)
    if s:
        template = s.group(1)
        if debugLevel > 0: print template.encode(config.console_encoding, 'replace')

    regex = ur'{{(' + templates2 + u")\|([^{}]+)}}"
    s = re.search(regex, pageContent)
    if s:
        template = s.group(1)
        parameters = s.group(2)
        if debugLevel > 0: print u' template trouvé : ' + template
        if debugLevel > 0: print u' paramètres : ' + parameters

        if template == u'fr-accord-comp':
            #pronunciation = getParameter(template, 3)
            pass
        elif template == u'fr-accord-comp-mf':
            #pronunciation = getParameter(template, 3)
            pass
        elif template == u'fr-accord-eur':
            #TODO pronunciation = getParameter(template, 2)
            pronunciation = parameters[parameters.rfind(u'|')+1:]
            pronunciation = pronunciation + u'œʁ'
        elif template == u'fr-accord-eux':
            #pronunciation = getParameter(template, 2)
            pronunciation = pronunciation + u'ø'
        elif template == u'fr-accord-f':
            #pronunciation = getParameter(template, 2)
            pronunciation = pronunciation + u'f'
        elif template == u'fr-accord-ind':
            pronunciation = getParameter(template, 'pm')
            pass
        elif template == u'fr-accord-mf':
            pronunciation = getParameter(template, 'pron')
        elif template == u'fr-accord-mf-ail':
            #pronunciation = getParameter(template, 2)
            pass
        elif template == u'fr-accord-mf-al':
            #pronunciation = getParameter(template, 2)
            pass
        elif template == u'fr-accord-oux':
            #pronunciation = getParameter(template, 2)
            pass
        elif template == u'fr-accord-personne':
            #pronunciation = getParameter(template, 'p1ms')
            #pronunciation = getParameter(template, 'p2s')
            pass
        elif template == u'fr-accord-t-avant1835':
            #pronunciation = getParameter(template, 2)
            pass
        elif template == u'fr-inv':
            #pronunciation = getParameter(template, 1)
            pass

        if pronunciation.find(u'.') != -1:
            if debugLevel > 0: print u' prononciation trouvée dans une boite de flexion : ' + pronunciation
    if debugLevel > 1: raw_input('Fin du test des flexions féminines')
    return pronunciation

def getPronunciation(pageContent, languageCode, nature = None):
    pronunciation = getPronunciationFromContent(pageContent, languageCode, nature)
    #TODO: from other pages or wikis
    '''
    if pronunciation == '':
        if pageContent.find(u'|' + languageCode + u'|flexion}}') != -1:
            pronunciation = getPronunciationFromFlexion(pageContent, languageCode, nature)
        else:
            pronunciation = getPronunciationFromLemma(pageContent, languageCode, nature)
    '''
    if debugLevel > 0: print u' Pronunciation found: ' + pronunciation
    return pronunciation

def addPronunciationFromContent(pageContent, languageCode, nature = None):
    if pageContent.find(u'{{pron||' + languageCode + u'}}') != -1:
        pronunciation = getPronunciation(pageContent, languageCode, nature = None)
        if pronunciation != u'':
            pageContent = pageContent.replace(u'{{pron||' + languageCode + u'}}', u'{{pron|' + pronunciation + u'|' + languageCode + u'}}')
    return pageContent

def addCategory(pageContent, languageCode, lineContent):
    if lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
    return addLine(pageContent, languageCode, 'catégorie', lineContent)

def removeCategory(pageContent, category, summary):
    if debugLevel > 0: print u'\nremoveCategory(' + category + u')'
    regexCategory = ur'(\n\[\[Catégorie:' + category + ur'(\||\])[^\]]*\]\]?)'
    newPageContent = re.sub(regexCategory, ur'', pageContent)
    if newPageContent != pageContent:
        summary = summary + u', retrait de [[Catégorie:' + category + u']]'
    return newPageContent, summary

def removeTemplate(pageContent, template, summary, language = None, inSection = None):
    if debugLevel > 0: print u'\nremoveTemplate(' + template + u')'
    #TODO: rattacher le bon template à la bonne ligne de l'étymologie, et s'il doit être déplacé plusieurs fois
    regexTemplate = ur'(,?( et| ou)? *{{' + template + ur'(\||})[^}]*}}?)'
    oldSection = pageContent
    if inSection is not None:
        if language is not None: oldSection, lStart, lEnd = getLanguageSection(oldSection, language)
        if oldSection is not None:
            for section in inSection:
                oldSubSection, sStart, sEnd = getSection(oldSection, section)
                if oldSubSection is not None:
                    if debugLevel > 2: raw_input(oldSubSection.encode(config.console_encoding, 'replace'))
                    newSubSection = re.sub(regexTemplate, ur'', oldSubSection)
                    if oldSubSection != newSubSection:
                        pageContent = pageContent.replace(oldSubSection, newSubSection)
                        if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                        summary = summary + u', retrait de {{' + template + u'}} dans {{S|' + section + u'}}'
    else:
        newSection = re.sub(regexTemplate, ur'', oldSection)
        if oldSection != newSection:
            pageContent = pageContent.replace(oldSection, newSection)
            summary = summary + u', retrait de {{' + template + u'}}'

    return pageContent, summary

def addLine(pageContent, languageCode, Section, lineContent):
    d = 1
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
            languageSection, startPosition, endPosition = getLanguageSection(pageContent, languageCode)
            if languageSection is None: return pageContent
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
                    if limitSection == sectionsInPage[-1][0]:
                        if debugLevel > d: print u' ajout de la sous-section après la dernière de la section langue : ' + limitSection
                        categories = languageSection.find(u'\n[[Catégorie:')
                        defaultSort = languageSection.find(u'\n{{clé de tri|')
                        if categories != -1 and (categories < defaultSort or defaultSort == -1):
                            if debugLevel > d: print u'  avant les catégories'
                            pageContent = pageContent[:startPosition] + languageSection[:categories] + sectionToAdd \
                                + languageSection[categories:] + pageContent[startPosition+endPosition:]
                        elif defaultSort != -1:
                            if debugLevel > d: print u'  avant la clé de tri'
                            pageContent = pageContent[:startPosition] + languageSection[:defaultSort] + u'\n' + \
                                sectionToAdd + languageSection[defaultSort:] + pageContent[startPosition+endPosition:]
                        else:
                            if debugLevel > d: print u'  sans catégorie'
                            pageContent = pageContent[:startPosition] + languageSection + sectionToAdd + pageContent[startPosition+endPosition:]
                        if debugLevel > d+1: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                    else:
                        if debugLevel > d: print u' ajout de la sous-section "' + Section + u'" avant "' + sectionsInPage[o+1][0] + u'"'
                        regex = ur'\n=* *{{S\|' + sectionsInPage[o+1][0]
                        s = re.search(regex, languageSection)
                        if s:
                            pageContent = pageContent[:startPosition] + languageSection[:s.start()] + \
                                sectionToAdd + languageSection[s.start():] + pageContent[startPosition+endPosition:]
                        else:
                            raw_input(' bug section')
                    languageSection, startPosition, endPosition = getLanguageSection(pageContent, languageCode)
                    if languageSection is None: return pageContent
                else:
                    if debugLevel > d:
                        print u' ajout de "' + Section + u'" avant "' + limitSection + u'"'
                        print u'  (car ' + str(sectionToAddNumber) + u' < ' + str(sectionNumber(limitSection)) + u')'
                    regex = ur'\n=* *{{S\|' + limitSection
                    s = re.search(regex, languageSection)
                    if s:
                        pageContent = pageContent[:startPosition] + languageSection[:s.start()] + sectionToAdd + \
                            languageSection[s.start():] + pageContent[startPosition+endPosition:]
                        languageSection, startPosition, endPosition = getLanguageSection(pageContent, languageCode)
                        if languageSection is None: return pageContent
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
                pageContent = pageContent[:startPosition] + languageSection[:-len(finalSection)] + finalSection[:s.start()] \
                 + lineContent + u'\n' + finalSection[s.start():] + pageContent[startPosition+endPosition:]
            else:
                categories = languageSection.find(u'\n[[Catégorie:')
                defaultSort = languageSection.find(u'\n{{clé de tri|')
                if categories != -1 and (categories < defaultSort or defaultSort == -1):
                    if debugLevel > d: print u' ajout avant les catégories'
                    pageContent = pageContent[:startPosition] + languageSection[:languageSection.find(u'\n[[Catégorie:')] + u'\n' + lineContent \
                     + languageSection[languageSection.find(u'\n[[Catégorie:'):] + pageContent[startPosition+endPosition:]
                elif defaultSort != -1:
                    if debugLevel > d: print u' ajout avant la clé de tri'
                    pageContent = pageContent[:startPosition] + languageSection[:languageSection.find(u'\n{{clé de tri|')] \
                     + u'\n' + lineContent + languageSection[languageSection.find(u'\n{{clé de tri|'):] + pageContent[startPosition+endPosition:]
                else:
                    if debugLevel > d: print u' ajout en fin de section langue'
                    pageContent = pageContent[:startPosition] + languageSection + u'\n' + lineContent + u'\n' + pageContent[startPosition+endPosition:]

    pageContent = pageContent.replace(u'\n\n* {{écouter|', u'\n* {{écouter|')
    if debugLevel > d: pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
    return pageContent

def addLineTest(pageContent, languageCode = 'fr'):
    pageContent = addCategory(pageContent, languageCode, u'Tests en français')
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
    d = 1
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

def sort_translations(pageContent, summary):
    debugLevel = 0
    if debugLevel > 0: print u'Classement des traductions et ajout des modèles T'
    if debugLevel > 1: print u'Détection d\'une première traduction aux normes'
    regex = u'\* ?{{[a-z][a-z][a-z]?\-?[a-z]?[a-z]?[a-z]?}} :'
    finalPageContent = u''
    while pageContent.find(u'{{trad-début')!=-1:
        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'{{trad-début')]
        pageContent = pageContent[pageContent.find(u'{{trad-début'):]
        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n')+1]
        pageContent = pageContent[pageContent.find(u'\n')+1:]
        if re.search(regex, pageContent):
            if re.search(regex, pageContent).start() < pageContent.find('{{'):
                if debugLevel > 0: print u'Ajout d\'un modèle T'
                pageContent = pageContent[:pageContent.find('{{')+2] + u'T|' + pageContent[pageContent.find('{{')+2:]
    pageContent = finalPageContent + pageContent
    finalPageContent = u''

    while pageContent.find(u'{{T|') != -1:
        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'{{T|')]
        pageContent = pageContent[pageContent.find(u'{{T|'):]
        if debugLevel > 2: print u' Ajout des T'
        pageContent2 = pageContent[pageContent.find(u'\n'):]
        if re.search(regex, pageContent2):
            if re.search(regex, pageContent2).start() < pageContent2.find('{{'):
                if debugLevel > 0: print u'Ajout d\'un modèle T'
                pageContent = pageContent[:pageContent.find(u'\n')+pageContent2.find('{{')+2] + u'T|' + \
                    pageContent[pageContent.find(u'\n')+pageContent2.find('{{')+2:]

        if debugLevel > 2: print u'Rangement de la ligne de la traduction par ordre alphabétique de la langue dans finalPageContent'
        langue1 = pageContent[pageContent.find(u'{{T|')+4:pageContent.find(u'}')]
        if langue1.find(u'|') != -1: langue1 = langue1[:langue1.find(u'|')]
        if debugLevel > 2: raw_input(finalPageContent.encode(config.console_encoding, 'replace'))
        if langue1 != u'' and (finalPageContent.find(u'<!--') == -1 or finalPageContent.find(u'-->') != -1):
            # Bug trop rare https://fr.wiktionary.org/w/index.php?title=User:JackBot/test&diff=15092317&oldid=15090227
            if debugLevel > 2 and finalPageContent.find(u'<!--') != -1:
                raw_input(finalPageContent[:finalPageContent.rfind(u'\n')].encode(config.console_encoding, 'replace'))
            if debugLevel > 1: print u' Langue 1 : ' + langue1
            if len(langue1) > 3 and langue1.find(u'-') == -1:
                langue = langue1
            else:
                try:
                    langue = defaultSort(languages[langue1].decode('utf8'), 'UTF-8')
                    if debugLevel > 1: print u' Nom de langue 1 : ' + langue
                except KeyError:
                    if debugLevel > 0: print "KeyError l 2556"
                    break
                except UnboundLocalError:
                    if debugLevel > 0: print "UnboundLocalError l 2559"
                    break
            langue2 = u'zzz'
            if finalPageContent.rfind(u'\n') == -1 or pageContent.find(u'\n') == -1: break
            TradCourante = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + pageContent[:pageContent.find(u'\n')]
            TradSuivantes = u''
            finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
            pageContent = pageContent[pageContent.find(u'\n'):]
            while finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{S|traductions') \
             and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{trad-début') and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{trad-fin') \
             and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{S|traductions à trier') and langue2 > langue \
             and finalPageContent.rfind(u'{{T') != finalPageContent.rfind(u'{{T|conv') and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{(') \
             and (finalPageContent.rfind('{{') > finalPageContent.rfind(u'|nocat') or finalPageContent.rfind(u'|nocat') == -1):
                langue2 = finalPageContent[finalPageContent.rfind(u'{{T|')+len(u'{{T|'):len(finalPageContent)]
                langue2 = langue2[:langue2.find('}}')]
                if langue2.find(u'|') != -1: langue2 = langue2[:langue2.find(u'|')]
                if debugLevel > 1: print u' Langue 2 : ' + langue2
                if len(langue2) > 3 and langue2.find(u'-') == -1:
                    langue = langue2
                else:
                    try:
                        langue2 = defaultSort(languages[langue2].decode('utf8'), 'UTF-8')
                        if debugLevel > 1: print u' Nom de langue 2 : ' + langue2
                    except KeyError:
                        if debugLevel > 0: print "KeyError l 2160"
                        break
                if langue2 != u'' and langue2 > langue:
                    if debugLevel > 0: langue2 + u' > ' + langue
                    if finalPageContent.rfind(u'\n') > finalPageContent.rfind(u'trad-début'):
                        TradSuivantes = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + TradSuivantes
                        finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
                        if debugLevel > 0: summary = summary + ', traduction ' + langue2 + u' > ' + langue
                    elif finalPageContent.rfind(u'\n') != -1:
                        # Cas de la première de la liste
                        TradCourante = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + TradCourante
                        finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
                    #print finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)].encode(config.console_encoding, 'replace')
                else:
                    break
            finalPageContent = finalPageContent + TradCourante + TradSuivantes
        elif pageContent.find(u'\n') != -1:
            if debugLevel > 0: print u' Retrait de commentaire de traduction : ' + pageContent[:pageContent.find(u'\n')+1]
            finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n')]
            pageContent = pageContent[pageContent.find(u'\n'):]
        else:
            finalPageContent = finalPageContent + pageContent
            pageContent = u''

        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n')+1]
        pageContent = pageContent[pageContent.find(u'\n')+1:]
        if debugLevel > 2: print(finalPageContent.encode(config.console_encoding, 'replace'))
        if debugLevel > 2: print(pageContent.encode(config.console_encoding, 'replace'))
        if debugLevel > 0: print ''
    pageContent = finalPageContent + pageContent
    if debugLevel > 0: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return pageContent, summary


# TODO: Classement des sections modifiables
"""
def sort_sections(pageContent):
    finalPageContent = u''
    while pageContent.find(u'{{langue|') != -1:
        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'{{langue|')+len(u'{{langue|')]
        pageContent = pageContent[pageContent.find(u'{{langue|')+len(u'{{langue|'):]
        if pageContent.find(u'{{langue|') != -1:
            # Rangement des paragraphes par ordre alphabétique de langue dans finalPageContent
            langue1 = pageContent[:pageContent.find(u'}')]
            if langue1.find(u'|') != -1: langue1 = langue1[:langue1.find(u'|')]
            if langue1 != u'':
                #print(langue1) # ca pt
                Langue1 = Page(site,u'Template:' + langue1)
                try: pageContent2 = Langue1.get()
                except pywikibot.exceptions.NoPage:
                    print "NoPage l 1521 : " + langue1
                    return
                except pywikibot.exceptions.IsRedirectPage:
                    pageContent2 = Langue1.getRedirectTarget().title() + u'<noinclude>'
                except pywikibot.exceptions.ServerError:
                    print "ServerError l 1527 : " + langue1
                    return
                except pywikibot.exceptions.BadTitle:
                    print "BadTitle l 1530 : " + langue1
                    return
                if pageContent2.find(u'<noinclude>') != -1:
                    langue = defaultSort(pageContent2[:pageContent2.find(u'<noinclude>')])
                    langue2 = u'zzz'
                    if pageContent.find(u'\n== {{langue|') != -1:
                        ParagCourant = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + pageContent[:pageContent.find(u'\n== {{langue|')]
                        pageContent = pageContent[pageContent.find(u'\n== {{langue|'):]
                    elif pageContent.find(u'\n=={{langue|') != -1:
                        ParagCourant = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + pageContent[:pageContent.find(u'\n=={{langue|')]
                        pageContent = pageContent[pageContent.find(u'\n=={{langue|'):]
                    else:
                        ParagCourant = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + pageContent
                        pageContent = u''
                    finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
                    ParagSuivants = u''
                    #raw_input (ParagCourant.encode(config.console_encoding, 'replace'))
                    # Comparaison du paragraphe courant avec le précédent, et rangement dans ParagSuivants de ce qui doit le suivre
                    while finalPageContent.rfind(u'{{langue|') != -1  and finalPageContent.rfind(u'{{langue|') < finalPageContent.rfind('}}') \
                        and finalPageContent.rfind(u'{{langue|') != finalPageContent.rfind(u'{{langue|fr'):
                        langue2 = finalPageContent[finalPageContent.rfind(u'{{langue|')+len(u'{{langue|'):len(finalPageContent)]
                        langue2 = langue2[:langue2.find('}}')]
                        if langue2.find(u'|') != -1: langue2 = langue2[:langue2.find(u'|')]
                        Langue2 = Page(site,u'Template:' + langue2)
                        try: pageContent3 = Langue2.get()
                        except pywikibot.exceptions.NoPage:
                            print "NoPage l 1607 : " + langue2
                            return
                        except pywikibot.exceptions.ServerError:
                            print "ServerError l 1610 : " + langue2
                            return
                        except pywikibot.exceptions.IsRedirectPage:
                            print u'Redirection l 1613 : ' + langue2
                            return
                        except pywikibot.exceptions.BadTitle:
                            print u'BadTitle l 1616 : ' + langue2
                            return
                        if pageContent3.find(u'<noinclude>') != -1:
                            langue2 = defaultSort(pageContent3[:pageContent3.find(u'<noinclude>')])
                            print langue2 # espagnol catalan
                            if langue2 > langue:
                                summary = summary + ', section ' + langue2 + u' > ' + langue
                                print langue2 + u' > ' + langue
                                ParagSuivants = finalPageContent[finalPageContent.rfind(u'{{langue|'):len(finalPageContent)] + ParagSuivants
                                finalPageContent = finalPageContent[:finalPageContent.rfind(u'{{langue|')]
                                ParagSuivants = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + ParagSuivants
                            else:
                                ParagCourant = finalPageContent[finalPageContent.rfind(u'{{langue|'):len(finalPageContent)] + ParagCourant
                                finalPageContent = finalPageContent[:finalPageContent.rfind(u'{{langue|')]
                                ParagCourant = finalPageContent[finalPageContent.rfind(u'\n'):len(finalPageContent)] + ParagCourant
                                #raw_input (ParagCourant.encode(config.console_encoding, 'replace')) catalan, espagnol, portugais
                            finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
                        else:
                            print u'l 1629'
                            return
                    #raw_input (finalPageContent.encode(config.console_encoding, 'replace'))
                    finalPageContent = finalPageContent + ParagCourant + ParagSuivants
            else:
                print u'l 1634'
                return
            finalPageContent = finalPageContent + pageContent[:pageContent.find(u'{{langue|')]
            pageContent = pageContent[pageContent.find(u'{{langue|'):]
            #raw_input (pageContent.encode(config.console_encoding, 'replace'))
        else:
            finalPageContent = finalPageContent + pageContent
            pageContent = u''
        #print(finalPageContent.encode(config.console_encoding, 'replace'))
        #print(pageContent.encode(config.console_encoding, 'replace'))
    pageContent = finalPageContent + pageContent
    finalPageContent = u''
"""
#!/usr/bin/env python
# coding: utf-8
#TODO: common Wiktionaries interfaces

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# https://fr.wiktionary.org/wiki/Module:types_de_mots/data
natures = [u'adjectif', u'adverbe', u'article', u'conjonction', u'copule', u'déterminant', u'nom', u'patronyme', \
    u'prénom', u'préposition', u'pronom', u'verbe', u'interjection', u'onomatopée', u'affixe', u'circonfixe', u'infixe', \
    u'interfixe', u'particule', u'postposition', u'préfixe', u'radical', u'suffixe', u'pré-verbe', u'pré-nom', \
    u'enclitique', u'proclitique', u'locution', u'proverbe', u'quantificateur', u'lettre', u'symbole', u'classificateur', \
    u'numéral', u'sinogramme', u'erreur', u'gismu', u'rafsi', u'nom propre']

# https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_définitions
definitionTemplates = [u'abréviation de', u'comparatif de', u'exclamatif de', u'mutation de', u'superlatif de', \
    u'variante de', u'variante ortho de', u'variante orthographique de']

definitionSentences = [u'abréviation de', u'ancienne orthographe de', u'autre nom de', u'autre orthographe', \
    u'comparatif de', u'exclamatif de', u'féminin de', u'graphie erronée', u'mauvaise orthographe de', u'mutation de', \
    u'nom scientifique de', u'pluriel de', u'superlatif de', u'synonyme de', u'variante', u'variante ortho de', \
    u'variante orthographique de']

Sections = []
sectionLevel = []
Sections.append(u'étymologie')
sectionLevel.append(u'===')
for nature in natures:
    Sections.append(nature)
    sectionLevel.append(u'===')
Sections.append(u'notes')
sectionLevel.append(u'====')
Sections.append(u'variantes orthographiques')
sectionLevel.append(u'====')
Sections.append(u'variantes')
sectionLevel.append(u'====')
Sections.append(u'synonymes')
sectionLevel.append(u'====')
Sections.append(u'antonymes')
sectionLevel.append(u'====')
Sections.append(u'dérivés')
sectionLevel.append(u'====')
Sections.append(u'apparentés')
sectionLevel.append(u'====')
Sections.append(u'vocabulaire')
sectionLevel.append(u'====')
Sections.append(u'hyperonymes')
sectionLevel.append(u'====')
Sections.append(u'hyponymes')
sectionLevel.append(u'====')
Sections.append(u'méronymes')
sectionLevel.append(u'====')
Sections.append(u'holonymes')
sectionLevel.append(u'====')
Sections.append(u'traductions')
sectionLevel.append(u'====')
Sections.append(u'traductions à trier')
sectionLevel.append(u'=====')
Sections.append(u'prononciation')
sectionLevel.append(u'===')
Sections.append(u'homophones')
sectionLevel.append(u'====')
Sections.append(u'paronymes')
sectionLevel.append(u'====')
Sections.append(u'anagrammes')
sectionLevel.append(u'===')
Sections.append(u'voir aussi')
sectionLevel.append(u'===')
Sections.append(u'références')
sectionLevel.append(u'===')
Sections.append(u'catégorie')
sectionLevel.append(u'')
Sections.append(u'clé de tri')
sectionLevel.append(u'')

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

def setGlobalsWiktionary(myDebugLevel, mySite, myUsername):
    global debugLevel
    global site
    global username
    debugLevel  = myDebugLevel
    site        = mySite
    username    = myUsername 
    
def getFirstLemmaFromLocution(pageName):
    if debugLevel > 1: print u'\ngetFirstLemmaFromLocution'
    lemmaPageName = ''
    if pageName.find(u' ') != -1:
        if debugLevel > 0: print u' lemme de locution trouvé : ' + lemmaPageName
        lemmaPageName = pageName[:pageName.find(u' ')]
    return lemmaPageName

def getGenderFromPageName(pageName, languageCode = 'fr', nature = None):
    if debugLevel > 1: print u'\ngetGenderFromPageName'
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
    if debugLevel > 1: print u'\ngetLemmaFromContent'
    lemmaPageName = getLemmaFromPlural(pageContent, languageCode)
    if lemmaPageName == '':
        lemmaPageName = getLemmaFromConjugation(pageContent, languageCode)
    return lemmaPageName

def getLemmaFromPlural(pageContent, languageCode = 'fr', natures = ['nom', 'adjectif', 'suffixe']):
    if debugLevel > 1: print u'\ngetLemmaFromPlural'
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
    if debugLevel > 1: print u'\ngetLemmaFromFeminine'
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
    if debugLevel > 1: print u'\ngetLemmaFromConjugation'
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
    if debugLevel > 0: pywikibot.output(u" flexionTemplate found: \03{green}" + flexionTemplate + "\03{default}")
    # TODO
    if flexionTemplate.find('{{') != -1: flexionTemplate = u''
    if flexionTemplate.find(u'-inv') != -1: flexionTemplate = u''

    return flexionTemplate

def getFlexionTemplateFromLemma(pageName, language, nature):
    if debugLevel > 1: print u'\ngetFlexionTemplateFromLemma'
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
    if debugLevel > 1: print u'\ngetPageLanguages()'
    regex = ur'{{langue\|([^}]+)}}'
    s = re.findall(regex, pageContent, re.DOTALL)
    if s: return s
    return []

def getLanguageSection(pageContent, languageCode = 'fr'):
    if debugLevel > 1: print u'\ngetLanguageSection(' + languageCode + u')'
    startPosition = 0
    endPosition = len(pageContent)

    regex = ur'=* *{{langue\|' + languageCode + '}}'
    s = re.search(regex, pageContent)
    if not s:
        if debugLevel > 0: print(' missing language!')
        return None, startPosition, endPosition

    startPosition = s.start()
    pageContent = pageContent[s.start():]
    regex = ur'\n== *{{langue\|(?!' + languageCode + ur'}).*} *='
    s = re.search(regex, pageContent)
    if s:
        endPosition = s.start()
        pageContent = pageContent[:endPosition]
        if debugLevel > 1: print endPosition
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    return pageContent, startPosition, endPosition

def getSections(pageContent):
    if debugLevel > 1: print u'\ngetSections()'
    regex = ur'{{S\|([^}\|]+)'
    s = re.findall(regex, pageContent, re.DOTALL)
    if s: return s
    return []

def getNotNaturesSections(pageContent):
    if debugLevel > 1: print u'\ngetNaturesSections()'
    sections = getSections(pageContent)
    return [item for item in sections if item not in natures]

def getNaturesSections(pageContent):
    if debugLevel > 1: print u'\ngetNaturesSections()'
    sections = getSections(pageContent)
    notNaturesSections = getNotNaturesSections(pageContent)
    return [item for item in sections if item not in notNaturesSections]

def getSection(pageContent, sectionName):
    if debugLevel > 1: print u'\ngetSection(' + sectionName + u')'
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
    if debugLevel > 1: print u'\ngetDefinitions'
    if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
    regex = ur"\n'''[^\n]*\n(#.*?(\n\n|\n=|$))"
    s = re.search(regex, pageContent, re.DOTALL)
    if s is None:
        if debugLevel > 1: print 'No definition'
        return None
    if debugLevel > 1: print s.group(1)
    return s.group(1)

def countDefinitions(pageContent):
    if debugLevel > 1: print u'\ncountDefinitions'
    definitions = getDefinitions(pageContent)
    if definitions is None: return 0
    definitions = definitions.split('\n')
    total = 0
    for definition in definitions:
        if definition[:1] == u'#' and definition[:2] not in [u'#:', u'#*']:
            total += 1
    return total

def countFirstDefinitionSize(pageContent):
    if debugLevel > 1: print u'\ncountFirstDefinitionSize'

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
    if debugLevel > 1: print u'\ngetPronunciationFromContent'
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
    if debugLevel > 1: print u'\ngetPronunciation'
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
    if debugLevel > 1: print u'\naddPronunciationFromContent'
    if pageContent.find(u'{{pron||' + languageCode + u'}}') != -1:
        pronunciation = getPronunciation(pageContent, languageCode, nature = None)
        if pronunciation != u'':
            pageContent = pageContent.replace(u'{{pron||' + languageCode + u'}}', u'{{pron|' + pronunciation + u'|' + languageCode + u'}}')
    return pageContent

def addCategory(pageContent, languageCode, lineContent):
    if debugLevel > 1: print u'\naddCategory'
    if lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'

    return addLine(pageContent, languageCode, 'catégorie', lineContent)

def removeCategory(pageContent, category, summary):
    if debugLevel > 1: print u'\nremoveCategory(' + category + u')'
    regexCategory = ur'(\n\[\[Catégorie:' + category + ur'(\||\])[^\]]*\]\]?)'
    newPageContent = re.sub(regexCategory, ur'', pageContent)
    if newPageContent != pageContent:
        summary = summary + u', retrait de [[Catégorie:' + category + u']]'

    return newPageContent, summary

def formatCategories(pageContent, summary):
    if debugLevel > 1: print u'\nformatCategory'

    regex = ur'([^\n])\[\[[Cc]atégorie:'
    pageContent = re.sub(regex, ur'\1\n[[Catégorie:', pageContent)

    regex = ur'(\[\[[Cc]atégorie:[^\n]+\n)\n+(\[\[[Cc]atégorie:)'
    pageContent = re.sub(regex, ur'\1\2', pageContent)

    return pageContent, summary

def removeTemplate(pageContent, template, summary, language = None, inSection = None):
    if debugLevel > 1: print u'\nremoveTemplate(' + template + u')'
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
    if debugLevel > 1: print u'\naddLine(' + languageCode + u', ' + Section + u')'
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
            languageSection, startPosition, endPosition = getLanguageSection(pageContent, languageCode)
            if languageSection is None: return pageContent
            sectionsInPage = re.findall(ur"\n=+ *{{S\|?([^}/|]+)([^}]*)}}", languageSection)
            if debugLevel > d+1: raw_input(str(sectionsInPage)) # ex : [(u'nom', u'|fr|num=1'), (u'synonymes', u'')]

            regex = ur'\n=* *{{S\|' + Section +  ur'[}\|]'
            if not re.search(regex, languageSection): 
                if debugLevel > d: u' section non trouvée'

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
                    if debugLevel > d:
                        print u' ajout dans la sous-section existante "' + Section + u'"'
                        print u' (car ' + str(sectionNumber(limitSection)) + u' = ' + str(sectionToAddNumber) + u')\n'
                elif not Section in [u'catégorie', u'clé de tri']:
                    sectionToAdd = u'\n\n' + sectionLevel[sectionToAddNumber] + u' {{S|' + Section + u'}} ' + sectionLevel[sectionToAddNumber] + u'\n'
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
                            if debugLevel > d+1:
                                print u'   Saut des sections incluses dans la précédente (de niveau titre inférieur)'
                                print u'   ' + str(sectionToAddNumber) + u' => ' + sectionLevel[sectionToAddNumber] + Section
                                print u'   ' + str(Sections.index(sectionsInPage[o+1][0])) + u' => ' + \
                                    sectionLevel[Sections.index(sectionsInPage[o+1][0])] + sectionsInPage[o+1][0]
                            while o < len(sectionsInPage) and len(sectionLevel[sectionToAddNumber]) < \
                                len(sectionLevel[Sections.index(sectionsInPage[o+1][0])]):
                                if debugLevel > d: print u' saut de ' + sectionsInPage[o+1][0]
                                o += 1

                            if debugLevel > d: print u' ajout de la sous-section "' + Section + u'" avant "' + sectionsInPage[o+1][0] + u'"'
                            regex = ur'\n=* *{{S\|' + sectionsInPage[o+1][0]
                            s = re.search(regex, languageSection)
                            if s:
                                if Section in natures:
                                    sectionToAdd = sectionToAdd.replace(u'}}', u'|' + languageCode + u'}}')
                                    if lineContent[:1] == u'#' or lineContent[:2] == u'\n#':
                                        sectionToAdd += u"'''{{subst:PAGENAME}}''' {{genre ?|" + languageCode + \
                                            u"}} {{pluriel ?|" + languageCode + u"}}\n"
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

            regex = ur'\n=* *{{S\|' + Section +  ur'[}\|]'
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

            lineContent = trim(lineContent)
            regex = ur'\n?\n==* *{{S\|'
            s = re.search(regex, finalSection)
            if s:
                if debugLevel > d: print u' ajout avant la sous-section suivante'
                pageContent = pageContent[:startPosition] + languageSection[:-len(finalSection)] + finalSection[:s.start()] \
                 + u'\n' + lineContent + finalSection[s.start():] + pageContent[startPosition+endPosition:]
            else:
                categories = languageSection.find(u'\n[[Catégorie:')
                defaultSort = languageSection.find(u'\n{{clé de tri|')
                if categories != -1 and (categories < defaultSort or defaultSort == -1):
                    if debugLevel > d: print u' ajout avant les catégories'
                    pageContent = pageContent[:startPosition] + languageSection[:languageSection.find(u'\n[[Catégorie:')] \
                        + lineContent + u'\n' + languageSection[languageSection.find(u'\n[[Catégorie:'):] + pageContent[startPosition+endPosition:]
                elif defaultSort != -1:
                    if debugLevel > d: print u' ajout avant la clé de tri'
                    pageContent = pageContent[:startPosition] + languageSection[:languageSection.find(u'\n{{clé de tri|')] \
                     + lineContent + u'\n' + languageSection[languageSection.find(u'\n{{clé de tri|'):] + pageContent[startPosition+endPosition:]
                else:
                    if debugLevel > d: print u' ajout en fin de section langue (donc saut de ligne)'
                    if languageSection[-1:] != u'\n':
                        lineContent = u'\n\n' + lineContent
                    elif languageSection[-2:] != u'\n\n':
                        lineContent = u'\n' + lineContent

                    pageContent = pageContent[:startPosition] + languageSection + lineContent + u'\n' + pageContent[startPosition+endPosition:]

    pageContent = pageContent.replace(u'\n\n* {{écouter|', u'\n* {{écouter|')
    if debugLevel > d: pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
    return pageContent

def addLineTest(pageContent, languageCode = 'fr'):
    pageContent = addCategory(pageContent, languageCode, u'Tests en français')
    pageContent = addLine(pageContent, languageCode, u'prononciation', u'* {{écouter|||lang=fr|audio=test.ogg}}')
    pageContent = addLine(pageContent, languageCode, u'prononciation', u'* {{écouter|||lang=fr|audio=test2.ogg}}')
    pageContent = addLine(pageContent, languageCode, u'étymologie', u':{{étyl|test|fr}}')
    pageContent = addLine(pageContent, languageCode, u'traductions', u'{{trad-début}}\n123\n{{trad-fin}}')
    pageContent = addLine(pageContent, languageCode, u'vocabulaire', u'* [[voc]]')
    pageContent = addLine(pageContent, languageCode, u'nom', u'# Définition')
    pageContent = addLine(pageContent, languageCode, u'nom', u'Note')
    return pageContent

def addPronunciation(pageContent, languageCode, section, lineContent):
    if pageContent != '' and languageCode != '' and section != '' and lineContent != '':
        if pageContent.find(lineContent) == -1 and pageContent.find(u'{{langue|' + languageCode + '}}') != -1:
            if section == u'catégorie' and lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
            if section == u'clé de tri' and lineContent.find(u'{{clé de tri|') == -1: lineContent = u'{{clé de tri|' + lineContent + '}}'

            # Recherche de l'ordre théorique de la section à ajouter
            NumSection = sectionNumber(section)
            if NumSection == len(Sections):
                if debugLevel > 0:
                    print u' ajout de ' + section + u' dans une section inconnue'
                    print u'  (car ' + len(Sections) + u' = ' + str(NumSection) + u')'
                return pageContent
            if debugLevel > 1: print u' position S : ' + s

            # Recherche de l'ordre réel de la section à ajouter
            oldLanguageSection, lStart, lEnd = getLanguageSection(pageContent, languageCode)
            if oldLanguageSection is None:
                return pageContent

            languageSection = oldLanguageSection
            #sectionsInPage = re.findall("{{S\|([^}]+)}}", languageSection)
            sectionsInPage = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", languageSection)
            o = 0
            # TODO pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
            while o < len(sectionsInPage) and sectionsInPage[o][0] != 'langue' \
             and sectionNumber(sectionsInPage[o][0]) <= NumSection:
                if debugLevel > 0:
                    print ' ' + sectionsInPage[o][0] + ' ' + str(sectionNumber(sectionsInPage[o][0]))
                o = o + 1
            if debugLevel > 0: print ' ' + str(len(sectionsInPage)) + ' >? ' + str(o)
            if o == len(sectionsInPage):
                if debugLevel > 0: print ' section à ajouter dans le dernier paragraphe'
                # TODO if section == sectionsInPage[-1][0]?
                if not section in [u'catégorie', u'clé de tri']:
                    if languageSection.find('[[Catégorie:') != -1:
                        if debugLevel > 0: print '  avant les catégories'
                        languageSection = languageSection[:languageSection.find('[[Catégorie:')] + \
                            lineContent + u'\n' + languageSection[languageSection.find('[[Catégorie:'):]
                    elif languageSection.find('{{clé de tri') != -1:
                        if debugLevel > 0: print '  avant la clé de tri'
                        languageSection = languageSection[:languageSection.find('{{clé de tri')] + \
                        lineContent + u'\n' + languageSection[languageSection.find('{{clé de tri'):]
                    else:
                        if debugLevel > 0: print ' section à ajouter en fin de section langue'
                        languageSection = languageSection + u'\n' + lineContent + u'\n'
                else:
                    if debugLevel > 0: print ' section à ajouter en fin de section langue'
                    languageSection = languageSection + u'\n' + lineContent + u'\n'
            else:
                sectionLimit = str(sectionsInPage[o][0].encode(config.console_encoding, 'replace'))
                o = o - 1
                if debugLevel > 1: print u' position O : ' + o
                if debugLevel > 0:
                    print u' ajout de "' + section + u'" avant "' + repr(sectionLimit) + u'"'
                    print u'  (car ' + str(sectionNumber(sectionLimit)) + u' > ' + str(NumSection) + u')'

                # Ajout après la section trouvée
                if languageSection.find(u'{{S|' + sectionsInPage[o][0]) == -1:
                    print 'Erreur d\'encodage'
                    return

                endOfLanguageSection = languageSection[languageSection.rfind(u'{{S|' + sectionsInPage[o][0]):]
                if debugLevel > 1: raw_input(endOfLanguageSection.encode(config.console_encoding, 'replace'))
                if sectionsInPage[o][0] != section and not section in [u'catégorie', u'clé de tri']:
                    if debugLevel > 0: print u' ajout de la section "' + section + u'" après "'+ sectionsInPage[o][0] + u'"'
                    lineContent = u'\n' + sectionLevel[NumSection] + u' {{S|' + section + u'}} ' + \
                        sectionLevel[NumSection] + u'\n' + lineContent
                else:
                     if debugLevel > 0: print u' ajout dans la section existante'
                if debugLevel > 1: raw_input(lineContent.encode(config.console_encoding, 'replace'))

                if endOfLanguageSection.find(u'\n==') == -1:
                    regex = ur'\n\[\[\w?\w?\w?:'
                    if re.compile(regex).search(languageSection):
                        interwikis = re.search(regex, languageSection).start()
                        categories = languageSection.find(u'\n[[Catégorie:')
                        defaultSort = languageSection.find(u'\n{{clé de tri|')

                        if (interwikis < categories or categories == -1) and (interwikis < defaultSort or defaultSort == -1):
                            if debugLevel > 0: print u'  ajout avant les interwikis'
                            try:
                                languageSection = languageSection[:interwikis] + u'\n' + lineContent + u'\n' + languageSection[interwikis:]
                            except:
                                print u' pb regex interwiki'
                        elif categories != -1 and (categories < defaultSort or defaultSort == -1):
                            if debugLevel > 0: print u'  ajout avant les catégories'
                            languageSection = languageSection[:languageSection.find(u'\n[[Catégorie:')] + lineContent + \
                                languageSection[languageSection.find(u'\n[[Catégorie:'):]
                        elif defaultSort != -1:
                            if debugLevel > 0: print u'  ajout avant la clé de tri'
                            languageSection = languageSection[:languageSection.find(u'\n{{clé de tri|')] + lineContent + \
                                languageSection[languageSection.find(u'\n{{clé de tri|'):]
                        else:
                            if debugLevel > 0: print u'  ajout en fin de section langue'
                            languageSection = languageSection + lineContent + u'\n'
                    else:
                        if debugLevel > 0: print u'  ajout en fin de section langue'
                        languageSection = languageSection + lineContent + u'\n'
                else:
                    if debugLevel > 0: print u'  ajout standard'
                    languageSection = languageSection[:-len(languageSection)] + languageSection[:-len(endOfLanguageSection)] + \
                        endOfLanguageSection[:endOfLanguageSection.find(u'\n==')] + lineContent + u'\n' + \
                        endOfLanguageSection[endOfLanguageSection.find(u'\n=='):]
            if languageSection.find(u'\n* {{écouter|') != -1 and languageSection.find(u'=== {{S|prononciation}} ===') == -1:
                languageSection = languageSection.replace(u'\n* {{écouter|', u'\n\n=== {{S|prononciation}} ===\n* {{écouter|')    

            languageSection = languageSection.replace(u'\n\n\n\n', u'\n\n\n')
            pageContent = pageContent.replace(oldLanguageSection, languageSection)

    return pageContent

def addLineIntoSection(pageContent, languageCode, section, lineContent):
    d = 1
    if debugLevel > d:
        pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
        print u'\naddLineIntoSection "' + section + '"'
    if pageContent != '' and languageCode != '' and section != '' and lineContent != '':
        if pageContent.find(lineContent) == -1 and pageContent.find(u'{{langue|' + languageCode + '}}') != -1:
            if section == u'catégorie' and lineContent.find(u'[[Catégorie:') == -1: lineContent = u'[[Catégorie:' + lineContent + u']]'
            if section == u'clé de tri' and lineContent.find(u'{{clé de tri|') == -1: lineContent = u'{{clé de tri|' + lineContent + '}}'
    sections = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", pageContent)
    # TODO: complete parsing
    raw_input(str(sections))
    return pageContent

def sectionNumber(section):
    if debugLevel > 1: print u'sectionNumber()'
    if debugLevel > 1:
        print u''
        print section
        print Sections[0]
        raw_input(section == Sections[0])
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
    while s < len(Sections) and section != Sections[s]:
        s = s + 1
    if s >= len(Sections):
        if debugLevel > 1: print u' ' + section + u' non trouvé'
        s = 1 # Grammatical natures (ex: nom)
    if debugLevel > 1:
        print u''
        print section
        print u' = ' + str(s)
        print u''
    return s

#TODO: def addLanguageCodeToTemplate(finalPageContent, pageContent, currentTemplate = None, languageCode = None):

def addLanguageCodeWithNamedParameterToTemplate(
    finalPageContent,
    pageContent,
    currentTemplate = None,
    languageCode = None,
    endPosition = 0
):        
    if debugLevel > 0: pywikibot.output(u"  Template with lang=: \03{green}" + currentTemplate + u"\03{default}")
    pageContent2 = pageContent[endPosition+1:]

    isCategory = currentTemplate != u'cf' or (pageContent2.find('}}') > endPosition+1 \
        and (pageContent2.find(':') == -1 or pageContent2.find(':') > pageContent2.find('}}')) \
        and pageContent2[:1] != '#')
    hasSubtemplateIncluded = False
    if pageContent.find('}}') > pageContent.find('{{') and pageContent.find('{{') != -1:
        # Inifnite loop in [[tomme]] on ^date\|[^{}]*({{(.*?)}}|.)+[^{}]*\|lang=
        regex = ur'^' + re.escape(currentTemplate) + ur'\|[^{}]*({{(.*?)}}|.)+[^{}]*\|lang='
        if re.search(regex, pageContent):
            hasSubtemplateIncluded = True
    if debugLevel > 1:
        print u'  ' + pageContent.find('lang=') == -1 or pageContent.find('lang=') > pageContent.find('}}')
        print u'  ' + isCategory
        print u'  ' + (not hasSubtemplateIncluded)
        print u'   ' + regex
        if hasSubtemplateIncluded:
            print ' ' + pageContent[re.search(regex, pageContent).start():re.search(regex, pageContent).end()]
        #raw_input(pageContent.encode(config.console_encoding, 'replace'))

    if (pageContent.find('lang=') == -1 or pageContent.find('lang=') > pageContent.find('}}')) and \
        isCategory and not hasSubtemplateIncluded and languageCode is not None:
        if debugLevel > 0: print u'   "lang=" addition'
        while pageContent2.find('{{') < pageContent2.find('}}') and pageContent2.find('{{') != -1:
            pageContent2 = pageContent2[pageContent2.find('}}')+2:]
        if pageContent.find('lang=') == -1 or pageContent.find('lang=') > pageContent.find('}}'):
            if debugLevel > 1: print u'    at ' + str(endPosition)
            finalPageContent = finalPageContent + currentTemplate + u'|lang=' + languageCode + pageContent[endPosition:pageContent.find('}}')+2]
            pageContent = pageContent[pageContent.find('}}')+2:]
            return finalPageContent, pageContent
        else:
            if debugLevel > 0: print u'    "lang=" addition cancellation'
            return nextTemplate(finalPageContent, pageContent)

    else:
        if debugLevel > 0: print u'   "lang=" already present'
        return nextTemplate(finalPageContent, pageContent)
                        
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
    if debugLevel > 1: print u'\nremoveFalseHomophones(' + relatedPageName + u')'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *'''" + re.escape(pageName) + \
        ur"''' *{{cf\|[^\|]*\|?" + re.escape(relatedPageName) + ur"[\|}][^\n]*\n"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, "==== {{S|homophones|" + languageCode + u"}} ====\n", pageContent)
        summary = summary + u', homophone erroné'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *\[\[[^}\n]+{{cf\|[^\|]*\|?" + re.escape(relatedPageName) + ur"[\|}][^\n]*\n?"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, "==== {{S|homophones|" + languageCode + u"}} ====\n", pageContent)
        summary = summary + u', homophone erroné'
    regex = ur"==== *{{S\|homophones\|" + languageCode + u"}} *====\n\* *\[\[" + re.escape(relatedPageName) + ur"\]\](\n|$)"
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

def sortTranslations(pageContent, summary):
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
        language1 = pageContent[pageContent.find(u'{{T|')+4:pageContent.find(u'}')]
        if language1.find(u'|') != -1: language1 = language1[:language1.find(u'|')]
        if debugLevel > 2: raw_input(finalPageContent.encode(config.console_encoding, 'replace'))
        if language1 != u'' and (finalPageContent.find(u'<!--') == -1 or finalPageContent.find(u'-->') != -1):
            # Bug trop rare https://fr.wiktionary.org/w/index.php?title=User:JackBot/test&diff=15092317&oldid=15090227
            if debugLevel > 2 and finalPageContent.find(u'<!--') != -1:
                raw_input(finalPageContent[:finalPageContent.rfind(u'\n')].encode(config.console_encoding, 'replace'))
            if debugLevel > 1: print u' Langue 1 : ' + language1
            if len(language1) > 3 and language1.find(u'-') == -1:
                language = language1
            else:
                try:
                    language = defaultSort(languages[language1].decode('utf8'), 'UTF-8')
                    if debugLevel > 1: print u' Nom de langue 1 : ' + language
                except KeyError:
                    if debugLevel > 0: print u'KeyError l 2556'
                    break
                except UnboundLocalError:
                    if debugLevel > 0: print u'UnboundLocalError l 2559'
                    break
            language2 = u'zzz'
            if finalPageContent.rfind(u'\n') == -1 or pageContent.find(u'\n') == -1: break
            TradCourante = finalPageContent[finalPageContent.rfind(u'\n'):] + pageContent[:pageContent.find(u'\n')]
            TradSuivantes = u''
            finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
            pageContent = pageContent[pageContent.find(u'\n'):]
            while finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{S|') and language2 > language \
                and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{trad-début') \
                and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{trad-fin') \
                and finalPageContent.rfind(u'{{T') != finalPageContent.rfind(u'{{T|conv') \
                and finalPageContent.rfind('{{') != finalPageContent.rfind(u'{{(') \
                and (finalPageContent.rfind('{{') > finalPageContent.rfind(u'|nocat') \
                or finalPageContent.rfind(u'|nocat') == -1):
                language2 = finalPageContent[finalPageContent.rfind(u'{{T|')+len(u'{{T|'):]
                language2 = language2[:language2.find('}}')]
                if language2.find(u'|') != -1: language2 = language2[:language2.find(u'|')]
                if debugLevel > 1: print u' Langue 2 : ' + language2
                if len(language2) > 3 and language2.find(u'-') == -1:
                    language = language2
                else:
                    try:
                        language2 = defaultSort(languages[language2].decode('utf8'), 'UTF-8')
                        if debugLevel > 1: print u' Nom de langue 2 : ' + language2
                    except KeyError:
                        if debugLevel > 0: print u'KeyError l 2160'
                        break
                if language2 != u'' and language2 > language:
                    if debugLevel > 0: language2 + u' > ' + language
                    if finalPageContent.rfind(u'\n') > finalPageContent.rfind(u'trad-début'):
                        TradSuivantes = finalPageContent[finalPageContent.rfind(u'\n'):] + TradSuivantes
                        finalPageContent = finalPageContent[:finalPageContent.rfind(u'\n')]
                        summary = summary + ', traduction ' + language2 + u' > ' + language
                    elif finalPageContent.rfind(u'\n') != -1:
                        # Cas de la première de la liste
                        TradCourante = finalPageContent[finalPageContent.rfind(u'\n'):] + TradCourante
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

def getLanguageCodeISO693_1FromISO693_3(code):
    if code == 'ben':
        return 'bn'
    elif code == 'epo':
        return 'eo'
    elif code == 'ori':
        return 'or'
    elif code == 'pol':
        return 'pl'
    elif code == 'por':
        return 'pt'
    elif code in ['afr', 'ara', 'cat', 'deu', 'eng', 'eus', 'fra', 'ita', 'nld', 'oci', 'rus', 'zho']:
        return code[:2]
    return code

def addSeeBanner(pageName, pageContent, summary):
    if debugLevel > 0: print u' {{voir}}'
    if debugLevel == 1: return pageContent, summary
    CleTri = defaultSort(pageName)

    if pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|')] + \
            pageName[:1].lower() + pageName[1:] + \
                pageContent[pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|{{lc:{{PAGENAME}}}}'):]
        summary = summary + u', subst de {{lc:{{PAGENAME}}}}'
    if pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|')] + \
            pageName[:1].upper() + pageName[1:] + \
                pageContent[pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|{{ucfirst:{{PAGENAME}}}}'):]
        summary = summary + u', subst de {{ucfirst:{{PAGENAME}}}}'
    if pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|')] + \
            pageName[:1].lower() + pageName[1:] + \
                pageContent[pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|{{LC:{{PAGENAME}}}}'):]
        summary = summary + u', subst de {{LC:{{PAGENAME}}}}'
    if pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|')] + \
            pageName[:1].upper() + pageName[1:] + \
                pageContent[pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|{{UCFIRST:{{PAGENAME}}}}'):]
        summary = summary + u', subst de {{UCFIRST:{{PAGENAME}}}}'
    if pageContent.find(u'{{voir|') == -1 and pageContent.find(u'{{voir/') == -1:
        PageVoir = u''
        # Liste de toutes les pages potentiellement "à voir"
        PagesCleTotal = pageName
        if PagesCleTotal.find(pageName.lower()) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName.lower()
        if PagesCleTotal.find(pageName.upper()) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName.upper()
        if PagesCleTotal.find(pageName[:1].lower() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].lower() + pageName[1:]
        if PagesCleTotal.find(pageName[:1].upper() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].upper() + pageName[1:]
        if PagesCleTotal.find(u'-' + pageName[:1].lower() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|-' + pageName[:1].lower() + pageName[1:]
        if PagesCleTotal.find(pageName[:1].lower() + pageName[1:] + u'-') == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].lower() + pageName[1:] + u'-'
        if PagesCleTotal.find(u'-') != -1: PagesCleTotal = PagesCleTotal + u'|' + PagesCleTotal.replace(u'-',u'')
        diacritics = []
        diacritics.append([u'a',u'á',u'à',u'ä',u'â',u'ã'])
        diacritics.append([u'c',u'ç'])
        diacritics.append([u'e',u'é',u'è',u'ë',u'ê'])
        diacritics.append([u'i',u'í',u'ì',u'ï',u'î'])
        diacritics.append([u'n',u'ñ'])
        diacritics.append([u'o',u'ó',u'ò',u'ö',u'ô',u'õ'])
        diacritics.append([u'u',u'ú',u'ù',u'ü',u'û'])
        for l in range(0,len(diacritics)):
            for d in range(0, len(diacritics[l])):
                if pageName.find(diacritics[l][d]) != -1:
                    if debugLevel > 1: print u'Titre contenant : ' + diacritics[l][d]
                    Lettre = diacritics[l][d]
                    for d in range(0,len(diacritics[l])):
                        PagesCleTotal = PagesCleTotal + u'|' + pageName.replace(Lettre,diacritics[l][d])
        if PagesCleTotal.find(CleTri) == -1:
            # exception ? and pageContent.find(u'{{langue|eo}}') == -1
            PagesCleTotal = PagesCleTotal + u'|' + CleTri

        # Filtre des pages de la liste "à voir"
        PagesCleRestant = PagesCleTotal + u'|'
        PagesCleTotal = u''
        PagesVoir = u''
        if debugLevel > 0: print u' Recherche des clés...'
        while PagesCleRestant != u'':
            if debugLevel > 1: print PagesCleRestant.encode(config.console_encoding, 'replace')
            currentPage = PagesCleRestant[:PagesCleRestant.find(u'|')]
            PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:]
            if currentPage == u'': continue
            pageCle = Page(site, currentPage)
            pageContentCle = getContentFromPage(pageCle)
            if pageContentCle != u'KO':
                if debugLevel > 1: print PagesCleTotal.encode(config.console_encoding, 'replace')
                if PagesCleTotal.find(u'|' + currentPage) == -1:
                    PagesCleTotal = PagesCleTotal + u'|' + currentPage
                if pageContentCle.find(u'{{voir|') != -1:
                    pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|'):]
                    PagesVoir = PagesVoir + u'|' + pageContentCle2[:pageContentCle2.find('}}')]
                elif pageContentCle.find(u'{{voir/') != -1:
                    pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir/')+len(u'{{voir/'):]
                    pageContent = u'{{voir/' + pageContentCle2[:pageContentCle2.find('}}')+3] + pageContent
                    pageMod = Page(site, u'Template:voir/' + pageContentCle2[:pageContentCle2.find('}}')])
                    pageContentModBegin = getContentFromPage(pageMod)
                    if pageContentModBegin == 'KO': break
                    pageContentMod = pageContentModBegin
                    if pageContentMod.find(u'!') == -1:
                        if pageContentMod.find(pageName) == -1:
                            pageContentMod = pageContentMod[:pageContentMod.find('}}')] + u'|' + pageName + \
                                pageContentMod[pageContentMod.find('}}'):len(pageContentMod)]
                        if pageContentMod.find(PageVoir) == -1:
                            pageContentMod = pageContentMod[:pageContentMod.find('}}')] + u'|' + PageVoir + \
                                pageContentMod[pageContentMod.find('}}'):len(pageContentMod)]
                    if debugLevel > 0:
                        print u'PagesCleRestant vide'
                    else:
                        if pageContentMod != pageContentModBegin: savePage(pageMod, pageContentMod, summary)
                    PagesCleRestant = u''
                    break

        if PagesVoir != u'':
            if debugLevel > 0: print u' Filtre des doublons...'
            if debugLevel > 1: print u'  avant : ' + PagesVoir
            PagesVoir = PagesVoir + u'|'
            while PagesVoir.find(u'|') != -1:
                if PagesCleTotal.find(PagesVoir[:PagesVoir.find(u'|')]) == -1:
                    PagesCleTotal = PagesCleTotal + u'|' + PagesVoir[:PagesVoir.find(u'|')]
                PagesVoir = PagesVoir[PagesVoir.find(u'|')+1:]
            if debugLevel > 1: print u'  après : ' + PagesCleTotal
        if debugLevel > 2: raw_input(PagesCleTotal.encode(config.console_encoding, 'replace'))

        if debugLevel > 0: print u' Balayage de toutes les pages "à voir"...'
        if PagesCleTotal != u'':
            while PagesCleTotal[:1] == u'|': PagesCleTotal = PagesCleTotal[1:]
        if PagesCleTotal != pageName:
            if debugLevel > 0: print u'  Différent de la page courante'
            PagesCleRestant = PagesCleTotal + u'|'
            while PagesCleRestant.find(u'|') != -1:
                currentPage = PagesCleRestant[:PagesCleRestant.find(u'|')]
                if currentPage == u'':
                    if debugLevel > 0: print u'currentPage vide'
                    break
                PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:]
                if currentPage != pageName and currentPage.find(u'*') == -1:
                    pageCle = Page(site, currentPage)
                    pageContentCleBegin = getContentFromPage(pageCle)
                else:
                    pageContentCleBegin = pageContent
                if pageContentCleBegin != u'KO' and not u':' in pageCle.title() and not u'{' in pageCle.title():
                    pageContentCle = pageContentCleBegin
                    if pageContentCle.find(u'{{voir/') != -1:
                        if debugLevel > 0: print u' {{voir/ trouvé'
                        break
                    elif pageContentCle.find(u'{{voir|') != -1:
                        if debugLevel > 0: print u' {{voir| trouvé'
                        if PagesCleTotal.find(u'|' + currentPage) != -1:
                            pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|'):]
                            pageContentCle = pageContentCle[:pageContentCle.find(u'{{voir|')+len(u'{{voir|')] \
                             + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] \
                             + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):] \
                             + pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|')+pageContentCle2.find('}}'):]
                        else:    # Cas du premier
                            pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir'):]
                            pageContentCle = pageContentCle[:pageContentCle.find(u'{{voir|')+len(u'{{voir|')] \
                             + PagesCleTotal[len(currentPage):] \
                             + pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir')+pageContentCle2.find('}}'):]
                        if pageContentCle != pageContentCleBegin:
                            if currentPage == pageName:
                                pageContent = pageContentCle
                            else:
                                if debugLevel > 0:
                                    print u' Première savePage dédiée à {{voir}}'
                                else:
                                    savePage(pageCle, pageContentCle, summary)
                    else:
                        if PagesCleTotal.find(u'|' + currentPage) != -1:
                            pageContentCle = u'{{voir|' + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] \
                             + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):] + u'}}\n' \
                             + pageContentCle
                        else:    # Cas du premier
                            pageContentCle = u'{{voir' + PagesCleTotal[len(currentPage):len(PagesCleTotal)] + u'}}\n' \
                            + pageContentCle
                        if currentPage == pageName:
                            pageContent = pageContentCle
                        else:    
                            if debugLevel > 0:
                                print u' Deuxième savePage dédiée à {{voir}}'
                            else:
                                savePage(pageCle, pageContentCle, summary)

    elif pageContent.find(u'{{voir|') != -1:
        if debugLevel > 0: print u'  Identique à la page courante'
        pageContent2 = pageContent[pageContent.find(u'{{voir|'):]
        if pageContent2.find(u'|' + pageName + u'|') != -1 and pageContent2.find(u'|' + pageName + u'|') < pageContent2.find('}}'):
            pageContent = pageContent[:pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'|')] \
                + pageContent[pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'|')+len(u'|' + pageName):]
        if pageContent2.find(u'|' + pageName + u'}') != -1 and pageContent2.find(u'|' + pageName + u'}') < pageContent2.find('}}'):
            pageContent = pageContent[:pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'}')] \
                + pageContent[pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'}')+len(u'|' + pageName):]

    if debugLevel > 0: print u' Nettoyage des {{voir}}...'
    if pageContent.find(u'{{voir}}\n') != -1: pageContent = pageContent[:pageContent.find(u'{{voir}}\n')] \
        + pageContent[pageContent.find(u'{{voir}}\n')+len(u'{{voir}}\n'):]
    if pageContent.find(u'{{voir}}') != -1: pageContent = pageContent[:pageContent.find(u'{{voir}}')] \
        + pageContent[pageContent.find(u'{{voir}}')+len(u'{{voir}}'):]
    pageContent = html2Unicode(pageContent)
    pageContent = pageContent.replace(u'}}&#32;[[', u'}} [[')
    pageContent = pageContent.replace(u']]&#32;[[', u']] [[')
    regex = ur'\[\[([^\]]*)\|\1\]\]'
    if re.search(regex, pageContent):
        if debugLevel > 0: print u'Lien interne inutile'
        pageContent = re.sub(regex, ur'[[\1]]', pageContent)

    return pageContent, summary

def formatSections(pageContent, summary):
    if debugLevel > 0: print u' formatSections()'
    regex = ur'{{=([a-z\-]+)=}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'{{langue|\1}}', pageContent)

    # Titres en minuscules
    #pageContent = re.sub(ur'{{S\|([^}]+)}}', ur'{{S|' + ur'\1'.lower() + ur'}}', pageContent)
    for f in re.findall("{{S\|([^}]+)}}", pageContent):
        pageContent = pageContent.replace(f, f.lower())

    # Alias peu intuitifs des sections avec langue
    pageContent = pageContent.replace(u'{{S|adj|', u'{{S|adjectif|')
    pageContent = pageContent.replace(u'{{S|adjectifs|', u'{{S|adjectif|')
    pageContent = pageContent.replace(u'{{S|adj-num|', u'{{S|adjectif numéral|')
    pageContent = pageContent.replace(u'{{S|adv|', u'{{S|adverbe|')
    pageContent = pageContent.replace(u'{{S|class|', u'{{S|classificateur|')
    pageContent = pageContent.replace(u'{{S|drv}}', u'{{S|dérivés}}')
    pageContent = pageContent.replace(u'{{S|homo|', u'{{S|homophones|')
    pageContent = pageContent.replace(u'{{S|homo}}', u'{{S|homophones}}')
    pageContent = pageContent.replace(u'{{S|interj|', u'{{S|interjection|')
    pageContent = pageContent.replace(u'{{S|locution adverbiale', u'{{S|adverbe')
    pageContent = pageContent.replace(u'{{S|locution phrase|', u'{{S|locution-phrase|')
    pageContent = pageContent.replace(u'{{S|nom commun|', u'{{S|nom|')
    pageContent = pageContent.replace(u'{{S|nom-fam|', u'{{S|nom de famille|')
    pageContent = pageContent.replace(u'{{S|nom-pr|', u'{{S|nom propre|')
    pageContent = pageContent.replace(u'{{S|pron}}', u'{{S|prononciation}}')
    pageContent = pageContent.replace(u'{{S|symb|', u'{{S|symbole|')
    pageContent = pageContent.replace(u'{{S|verb|', u'{{S|verbe|')
    pageContent = pageContent.replace(u'{{S|apparentés étymologiques', u'{{S|apparentés')
    # Alias peu intuitifs des sections sans langue
    pageContent = re.sub(ur'{{S\| ?abr(é|e)v(iations)?\|?[a-z\- ]*}}', u'{{S|abréviations}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?anagr(ammes)?\|?[a-z\- ]*}}', u'{{S|anagrammes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?anciennes orthographes?\|?[a-z\- ]*}}', u'{{S|anciennes orthographes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?ant(onymes)?\|?[a-z\- ]*}}', u'{{S|antonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?app(arentés)?\|?[a-zé]*}}', u'{{S|apparentés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?apr\|?[a-zé]*}}', u'{{S|apparentés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?compos(és)?\|?[a-zé]*}}', u'{{S|composés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?dial\|?[a-z\- ]*}}', u'{{S|variantes dialectales}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?dimin(inutifs)?\|?[a-z\- ]*}}', u'{{S|diminutifs}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?d(é|e)riv(é|e)s?(\|[a-z\- ]*}}|}})', u'{{S|dérivés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?drv\|?[a-z\- ]*}}', u'{{S|dérivés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?dérivés int\|?[a-z\- ]*}}', u'{{S|dérivés autres langues}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?drv\-int\|?[a-z\- ]*}}', u'{{S|dérivés autres langues}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?(é|e)tym(ologie)?\|?[a-z\- ]*}}', u'{{S|étymologie}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?exp(ressions)?\|?[a-z\- ]*}}', u'{{S|expressions}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?gent(ilés)?\|?[a-zé]*}}', u'{{S|gentilés}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?faux\-amis?\|?[a-zé]*}}', u'{{S|faux-amis}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?holo(nymes)?\|?[a-z\- ]*}}', u'{{S|holonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?hyper(onymes)?\|?[a-z\- ]*}}', u'{{S|hyperonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?hypo(nymes)?\|?[a-z\- ]*}}', u'{{S|hyponymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?m(é|e)ro(nymes)?\|?[a-z\- ]*}}', u'{{S|méronymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?notes?(\|?[a-z ]*)?}}', u'{{S|notes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?paro(nymes)?\|?[a-z\- ]*}}', u'{{S|paronymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?phrases?\|?[a-z\- ]*}}', u'{{S|phrases}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?pron(onciation)?\|?[a-z\- ]*}}', u'{{S|prononciation}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?q\-syn\|?[a-z\- ]*}}', u'{{S|quasi-synonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?quasi(\-| )syn(onymes)?\|?[a-z\- ]*}}', u'{{S|quasi-synonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?r(é|e)f[a-zé]*\|?[a-z\- ]*}}', u'{{S|références}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?syn(onymes)?\|?[a-z\- ]*}}', u'{{S|synonymes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?taux de reconnaissance\|?[a-z\- ]*}}', u'{{S|taux de reconnaissance}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?trad(uctions)?\|?[a-z]*}}', u'{{S|traductions}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?trad\-trier\|?[a-z\- ]*}}', u'{{S|traductions à trier}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?traductions à trier\|?[a-z\- ]*}}', u'{{S|traductions à trier}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?var(iantes)?\|?[a-z\-]*}}', u'{{S|variantes}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?variantes dial\|?[a-z\- ]*}}', u'{{S|variantes dialectales}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?variantes dialectales\|?[a-z\- ]*}}', u'{{S|variantes dialectales}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?var[a-z]*(\-| )ortho(graphiques)?\|?[a-z\- ]*}}', u'{{S|variantes orthographiques}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?voc(abulaire)?\|?[a-z\- ]*}}', u'{{S|vocabulaire}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?vocabulaire apparenté\|?[a-z\- ]*}}', u'{{S|vocabulaire}}', pageContent)
    pageContent = re.sub(ur'{{S\| ?voir( aussi)?\|?[a-z\- ]*}}', u'{{S|voir aussi}}', pageContent)
    pageContent = pageContent.replace(u'{{S|descendants}}', u'{{S|dérivés autres langues}}')
    pageContent = pageContent.replace(u'num=1|num=', u'num=1')

    regex = ur"(==== {{S\|dérivés autres langues}} ====" + ur"(:?\n\* *{{L\|[^\n]+)?"*10 + ur"\n\* *{{)T\|"
    for i in range(10):
        pageContent = re.sub(regex, ur'\1L|', pageContent)

    regex = ur"\n=* *({{langue\|[^}]+}}) *=*\n"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"\n== \1 ==\n", pageContent)

    regex = ur'({{S\|[^}]+)€'
    while re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\1⿕', pageContent)

    return pageContent, summary

def formatTranslations(pageContent, summary):
    if debugLevel > 0: print u' formatTranslations()'
    regex = ur'({{langue\|(?!fr}).*}[^€]*)\n=* *{{S\|traductions}} *=*\n*{{trad\-début}}\n{{ébauche\-trad}}\n{{trad\-fin}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\1', pageContent)
        summary = summary + u', retrait de {{S|traductions}}'

    regex = ur'({{langue\|(?!fr}).*}[^€]*)\n=* *{{S\|traductions}} *=*\n*{{\(}}\n{{ébauche\-trad}}\n{{\)}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\1', pageContent)
        summary = summary + u', retrait de {{S|traductions}}'

    # Formatage général des traductions
    pageContent = pageContent.replace(u'{{trad|', u'{{trad-|')
    pageContent = pageContent.replace(u'{{(}}\n{{ébauche-trad}}\n{{)}}', '')
    pageContent = pageContent.replace(u'{{trad-début|{{trad-trier}}}}', u'{{trad-trier}}\n{{trad-début}}')
    pageContent = pageContent.replace(u'{{trad-début|{{trad-trier|fr}}}}', u'{{trad-trier}}\n{{trad-début}}')

        # 1) Suppression de {{ébauche-trad|fr}} (WT:PPS)
    pageContent = pageContent.replace(ur'{{ébauche-trad|fr}}', u'{{ébauche-trad}}')
    regex = ur'{{ébauche\-trad\|fr}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, u'{{ébauche-trad}}', pageContent)

        # 2) Aucun modèle d'ébauche en dehors d'une boite déroulante
    pageContent = pageContent.replace(ur'{{ébauche-trad}}\n{{trad-début}}', u'{{trad-début}}\n{{ébauche-trad}}')
    regex = ur'{{ébauche\-trad}}\n{{trad\-début}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, u'{{trad-début}}\n{{ébauche-trad}}', pageContent)

    pageContent = pageContent.replace(ur'==== {{S|traductions}} ====\n{{ébauche-trad}}\n', 
        u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n')
    regex = ur'==== {{S\|traductions}} ====\n{{ébauche\-trad}}(\n<![^>]+>)*(\n|$)'
    if re.search(regex, pageContent):
        if debugLevel > 0: print ' ébauche sans boite'
        pageContent = re.sub(regex, u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad|en}}\n{{trad-fin}}\n',
            pageContent)

        # 3) Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
    pageContent = pageContent.replace(ur'<!--* {{T|en}} : {{trad|en|}}-->', '')     # bug ?
    regex = ur'<!\-\-[^{>]*{{T\|[^>]+>\n?'
    if re.search(regex, pageContent):
        if debugLevel > 0: print ' Commentaire trouvé l 1517'
        pageContent = re.sub(regex, u'', pageContent)
    regex = ur'{{ébauche\-trad}}{{'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, u'{{ébauche-trad}}\n{{', pageContent)

    while pageContent.find(u'{{trad-fin}}\n* {{T|') != -1:
        pageContent2 = pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|'):]
        delta = pageContent2.find(u'\n')+1
        pageContent2 = pageContent2[delta:]
        if pageContent2.find(u'\n') != -1:
            if debugLevel > 0: print pageContent2[:pageContent2.find(u'\n')+1].encode(config.console_encoding, 'replace')
            if pageContent2[:pageContent2.find(u'\n')+1].find(u'trier') != -1: break
            pageContent = pageContent[:pageContent.find(u'{{trad-fin}}\n* {{T|'):] + \
                pageContent2[:pageContent2.find(u'\n')+1] + u'{{trad-fin}}\n' + \
                pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|')+delta+pageContent2.find(u'\n')+1:]
        else:
            if debugLevel > 0: print pageContent2.encode(config.console_encoding, 'replace')
            if pageContent2[:len(pageContent2)].find(u'trier') != -1: break
            pageContent = pageContent[:pageContent.find(u'{{trad-fin}}\n* {{T|'):] + \
                pageContent2[:len(pageContent2)] + u'{{trad-fin}}\n' + \
                pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|')+delta+len(pageContent2):]
    regex = ur'}}{{trad\-fin}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, u'}}\n{{trad-fin}}', pageContent)

    while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(pageContent):
        i1 = re.search(u'{{T\|.*\n\n\*[ ]*{{T\|', pageContent).end()
        pageContent = pageContent[:i1][:pageContent[:i1].rfind(u'\n')-1] + pageContent[:i1][pageContent[:i1].rfind(u'\n'):len(pageContent[:i1])] + pageContent[i1:]

    if debugLevel > 1: print u'  Modèles à déplacer'
    regex = ur'(==== {{S\|traductions}} ====)(\n{{ébauche\-trad[^}]*}})(\n{{trad-début}})'
    pageContent = re.sub(regex, ur'\1\3\2', pageContent)

    regex = ur'({{trad\-début}})\n*{{trad\-début}}'
    pageContent = re.sub(regex, ur'\1', pageContent)

    regex = ur'({{trad\-fin}})\n*{{trad\-fin}}'
    pageContent = re.sub(regex, ur'\1', pageContent)

    return pageContent, summary


def addTemplates(pageContent, summary):
    regex = ur'\n#\* *(?:\'\')?\n'
    pageContent = re.sub(regex, ur'\n#* {{ébauche-exe}}\n', pageContent)

    return pageContent, summary


def renameTemplates(pageContent, summary):
    if debugLevel > 1: print u' Remplacements des anciens codes langue'
    pageContent = pageContent.replace(u'|ko-hani}}', u'|ko-Hani}}')
    ''' Bug https://fr.wiktionary.org/w/index.php?title=van&diff=prev&oldid=24107783&diffmode=source
    oldTemplate = []
    newTemplate = []
    oldTemplate.append(u'ko-hanja')
    newTemplate.append(u'ko-Hani')
    oldTemplate.append(u'be-x-old')
    newTemplate.append(u'be-tarask')
    oldTemplate.append(u'zh-min-nan')
    newTemplate.append(u'nan')
    oldTemplate.append(u'lsf')
    newTemplate.append(u'fsl')
    oldTemplate.append(u'arg')
    newTemplate.append(u'an')
    oldTemplate.append(u'nav')
    newTemplate.append(u'nv')
    oldTemplate.append(u'prv')
    newTemplate.append(u'oc')
    oldTemplate.append(u'nds-NL')
    newTemplate.append(u'nds-nl')
    oldTemplate.append(u'gsw-FR')
    newTemplate.append(u'gsw-fr')
    oldTemplate.append(u'zh-sc')
    newTemplate.append(u'zh-Hans')
    oldTemplate.append(u'roa-rup')
    newTemplate.append(u'rup')
    oldTemplate.append(u'gaul')
    newTemplate.append(u'gaulois')
    oldTemplate.append(u'xtg')
    newTemplate.append(u'gaulois')
    for p in range(1, len(oldTemplate)):
        regex = ur'((?!:voir).*[\|{=])' + oldTemplate[p] + ur'([\|}])'
        while re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1' + newTemplate[p] + ur'\2', pageContent)
    '''

    if debugLevel > 1: print u' Modèles des étymologies'
    regex = ur"(\n:? *(?:{{date[^}]*}})? *(?:\[\[calque\|)?[Cc]alque\]* d(?:u |e l['’]){{)étyl\|"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"\1calque|", pageContent)

    if debugLevel > 1: print u' Modèles trop courts'
    pageContent = pageContent.replace(u'{{f}} {{fsing}}', u'{{f}}')
    pageContent = pageContent.replace(u'{{m}} {{msing}}', u'{{m}}')
    pageContent = pageContent.replace(u'{{f}} {{p}}', u'{{fplur}}')
    pageContent = pageContent.replace(u'{{m}} {{p}}', u'{{mplur}}')
    pageContent = pageContent.replace(u'{{fp}}', u'{{fplur}}')
    pageContent = pageContent.replace(u'{{mp}}', u'{{mplur}}')
    pageContent = pageContent.replace(u'{{np}}', u'{{nlur}}')
    pageContent = pageContent.replace(u'{{fs}}', u'{{fsing}}')
    pageContent = pageContent.replace(u'{{mascul}}', u'{{au masculin}}')
    pageContent = pageContent.replace(u'{{fémin}}', u'{{au féminin}}')
    pageContent = pageContent.replace(u'{{femin}}', u'{{au féminin}}')
    pageContent = pageContent.replace(u'{{sing}}', u'{{au singulier}}')
    pageContent = pageContent.replace(u'{{plur}}', u'{{au pluriel}}')
    pageContent = pageContent.replace(u'{{pluri}}', u'{{au pluriel}}')
    pageContent = pageContent.replace(u'{{mascul|', u'{{au masculin|')
    pageContent = pageContent.replace(u'{{fémin|', u'{{au féminin|')
    pageContent = pageContent.replace(u'{{femin|', u'{{au féminin|')
    pageContent = pageContent.replace(u'{{sing|', u'{{au singulier|')
    pageContent = pageContent.replace(u'{{plur|', u'{{au pluriel|')
    pageContent = pageContent.replace(u'{{pluri|', u'{{au pluriel|')
    pageContent = pageContent.replace(u'{{dét|', u'{{déterminé|')
    pageContent = pageContent.replace(u'{{dén|', u'{{dénombrable|')
    pageContent = pageContent.replace(u'{{pl-cour}}', u'{{plus courant}}')
    pageContent = pageContent.replace(u'{{pl-rare}}', u'{{plus rare}}')
    pageContent = pageContent.replace(u'{{mf?}}', u'{{mf ?}}')
    pageContent = pageContent.replace(u'{{fm?}}', u'{{fm ?}}')
    pageContent = pageContent.replace(u'{{coll}}', u'{{collectif}}')

    if debugLevel > 1: print u' Modèles des définitions'
    pageContent = re.sub(ur'{{régio *\| *', ur'{{région|', pageContent)
    pageContent = re.sub(ur'{{terme *\| *', ur'{{term|', pageContent)
    pageContent = re.sub(ur'{{term *\|Registre neutre}} *', ur'', pageContent)

    regex = ur"{{ *dés *([\|}])"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"{{désuet\1", pageContent)
    regex = ur"{{ *fam *([\|}])"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"{{familier\1", pageContent)
    regex = ur"{{ *péj *([\|}])"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"{{péjoratif\1", pageContent)
    regex = ur"{{ *vx *([\|}])"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"{{vieilli\1", pageContent)

    if debugLevel > 1: print u' Modèles alias en doublon'
    regex = ur"(\{\{figuré\|[^}]*\}\}) ?\{\{métaphore\|[^}]*\}\}"
    pattern = re.compile(regex)
    pageContent = pattern.sub(ur"\1", pageContent)
    regex = ur"(\{\{métaphore\|[^}]*\}\}) ?\{\{figuré\|[^}]*\}\}"
    pattern = re.compile(regex)
    pageContent = pattern.sub(ur"\1", pageContent)

    regex = ur"(\{\{départements\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    pageContent = pattern.sub(ur"\1", pageContent)

    regex = ur"(\{\{localités\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    pageContent = pattern.sub(ur"\1", pageContent)

    regex = ur"(\{\{provinces\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    pageContent = pattern.sub(ur"\1", pageContent)

    regex = ur"(\#\* {{ébauche\-exe\|[^}]*}})\n\#\*: {{trad\-exe\|[^}]*}}"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"\1", pageContent)

    pageContent = pageContent.replace(u'{{arbre|', u'{{arbres|')
    pageContent = pageContent.replace(u'{{arme|', u'{{armement|')
    pageContent = pageContent.replace(u'{{astro|', u'{{astronomie|')
    pageContent = pageContent.replace(u'{{bota|', u'{{botanique|')
    pageContent = pageContent.replace(u'{{électro|', u'{{électronique|')
    pageContent = pageContent.replace(u'{{équi|', u'{{équitation|')
    pageContent = pageContent.replace(u'{{ex|', u'{{e|')
    pageContent = pageContent.replace(u'{{gastro|', u'{{gastronomie|')
    pageContent = pageContent.replace(u'{{légume|', u'{{légumes|')
    pageContent = pageContent.replace(u'{{minéral|', u'{{minéralogie|')
    pageContent = pageContent.replace(u'{{myth|', u'{{mythologie|')
    pageContent = pageContent.replace(u'{{oiseau|', u'{{oiseaux|')
    pageContent = pageContent.replace(u'{{péj|', u'{{péjoratif|')
    pageContent = pageContent.replace(u'{{plante|', u'{{plantes|')
    pageContent = pageContent.replace(u'{{psycho|', u'{{psychologie|')
    pageContent = pageContent.replace(u'{{réseau|', u'{{réseaux|')
    pageContent = pageContent.replace(u'{{typo|', u'{{typographie|')
    pageContent = pageContent.replace(u'{{vêtement|', u'{{vêtements|')
    pageContent = pageContent.replace(u'{{en-nom-rég-double|', u'{{en-nom-rég|')
    pageContent = pageContent.replace(u'{{Valence|ca}}', u'{{valencien}}')
    pageContent = pageContent.replace(u'{{abrév|', u'{{abréviation|')
    pageContent = pageContent.replace(u'{{abrév}}', u'{{abréviation}}')
    pageContent = pageContent.replace(u'{{acron|', u'{{acronyme|')
    pageContent = pageContent.replace(u'{{cours d\'eau', u'{{cours d’eau')

    if debugLevel > 1: print u' Modèles trop longs'
    pageContent = pageContent.replace(u'{{boîte début', u'{{(')
    pageContent = pageContent.replace(u'{{boîte fin', u'{{)')
    pageContent = pageContent.replace(u'\n{{-}}', u'')

    if debugLevel > 1: print u' Modèles en doublon'
    importedSites = ['DAF8', 'Littré']
    for importedSite in importedSites:
        regex = ur'\n\** *{{R:' + importedSite + ur'}} *\n\** *({{Import:' + importedSite + ur'}})'
        if re.search(regex, pageContent):
            summary = summary + u', doublon {{R:' + importedSite + ur'}}'
            pageContent = re.sub(regex, ur'\n* \1', pageContent)
        regex = ur'\n\** *({{Import:' + importedSite + ur'}}) *\n\** *{{R:' + importedSite + ur'}}'
        if re.search(regex, pageContent):
            summary = summary + u', doublon {{R:' + importedSite + ur'}}'
            pageContent = re.sub(regex, ur'\n* \1', pageContent)

    if debugLevel > 1: print u' Modèles bandeaux' 
    while pageContent.find(u'\n{{colonnes|') != -1:
        if debugLevel > 0: pywikibot.output(u'\n \03{green}colonnes\03{default}')
        pageContent2 = pageContent[:pageContent.find(u'\n{{colonnes|')]
        if pageContent2.rfind('{{') != -1 and pageContent2.rfind('{{') == pageContent2.rfind(u'{{trad-début'):    # modèles impriqués dans trad
            pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            if pageContent2.find(u'\n}}\n') != -1:
                if pageContent2[:len(u'titre=')] == u'titre=':
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début|' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] \
                     + '}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                else:
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            else:
                if debugLevel > 0: print u'pb {{colonnes}} 1'
                break

        elif pageContent2.rfind('{{') != -1 and pageContent2.rfind('{{') == pageContent2.rfind(u'{{('):    # modèles impriqués ailleurs
            if debugLevel > 0: pywikibot.output(u'\nTemplate: \03{blue}(\03{default}')
            pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            if pageContent2.find(u'\n}}\n') != -1:
                if pageContent2[:len(u'titre=')] == u'titre=':
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(|' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] + '}}' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                else:
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            else:
                if debugLevel > 0: print u'pb {{colonnes}} 2'
                break

        elif pageContent2.rfind('{{') != -1 and (pageContent2.rfind('{{') == pageContent2.rfind(u'{{trad-fin') or pageContent2.rfind('{{') == pageContent2.rfind(u'{{S|trad')):
            # modèle à utiliser dans {{S|trad
            pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(pageContent)]
            if pageContent2.find(u'\n}}\n') != -1:
                if pageContent2[:len(u'titre=')] == u'titre=':
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début|' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] + '}}' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                else:
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            else:
                if debugLevel > 0: print u'pb {{colonnes}} 3'
                break

        else:    # modèle ailleurs que {{S|trad
            pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            if pageContent2.find(u'\n}}\n') != -1:
                if pageContent2[:len(u'titre=')] == u'titre=':
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(|' \
                     + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] \
                     + '}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                else:
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                     + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                    pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
            else:
                if debugLevel > 0: print u'pb {{colonnes}} 4'
                break
        while pageContent.find(u'}}1=') != -1:
            pageContent = pageContent[:pageContent.find(u'}}1=')] + pageContent[pageContent.find(u'}}1=')+len(u'}}1='):len(pageContent)]

    pageContent = pageContent.replace(u'{{pron-rég|', u'{{écouter|')
    regex = ur'\* ?{{sound}} ?: \[\[Media:([^\|\]]*)\|[^\|\]]*\]\]'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'{{écouter|audio=\1}}', pageContent)
        summary = summary + u', conversion de modèle de son'
    regex = ur'\{{audio\|([^\|}]*)\|[^\|}]*}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'{{écouter|audio=\1}}', pageContent)
        summary = summary + u', conversion de modèle de son'

    pageContent = pageContent.replace(u'{{Citation needed}}', u'{{référence nécessaire}}')
    pageContent = pageContent.replace(u'{{Référence nécessaire}}', u'{{référence nécessaire}}')
    pageContent = pageContent.replace(u'{{clef de tri', u'{{clé de tri')

    # TODO: replace {{fr-rég|ɔs vɛʁ.tɛ.bʁal|s=os vertébral|p=os vertébraux|pp=ɔs vɛʁ.tɛ.bʁo}} by {{fr-accord-mf-al|

    # Hotfix
    regex = ur'\n{{\(}}nombre= *[0-9]*\|\n'
    pageContent = re.sub(regex, ur'\n{{(}}\n', pageContent)
    regex = ur'\n{{\(}}taille= *[0-9]*\|\n'
    pageContent = re.sub(regex, ur'\n{{(}}\n', pageContent)

    return pageContent, summary

def removeDoubleCategoryWhenTemplate(pageContent, summary):
    if debugLevel > 1: print u' Retrait des catégories contenues dans les modèles'

    if u'{{info|conv}}' in pageContent and u'[[Catégorie:Noms de domaine internet]]' in pageContent:
        pageContent = pageContent.replace(u'[[Catégorie:Noms de domaine internet]]', u'')
        pageContent = pageContent.replace(u'{{info|conv}}', u'{{noms de domaine}}')
    if u'{{informatique|conv}}' in pageContent and u'[[Catégorie:Noms de domaine internet]]' in pageContent:
        pageContent = pageContent.replace(u'[[Catégorie:Noms de domaine internet]]', u'')
        pageContent = pageContent.replace(u'{{informatique|conv}}', u'{{noms de domaine}}')

    if pageContent.find(u'\n[[Catégorie:Noms scientifiques]]') != -1 and pageContent.find(u'{{S|nom scientifique|conv}}') != -1:
        pageContent = pageContent.replace(u'\n[[Catégorie:Noms scientifiques]]', u'')

    if pageContent.find(u'[[Catégorie:Villes') != -1 and pageContent.find(u'{{localités|') != -1:
        summary = summary + u', {{villes}} -> {{localités}}'
        pageContent = re.sub(ur'\n\[\[Catégorie:Villes[^\]]*\]\]', ur'', pageContent)

    #TODO: retraiter toutes les paires catégorie / templates, dynamiquement, pour tous les codes langues
    if u'{{argot|fr}}' in pageContent:
        pageContent = re.sub(ur'\n\[\[Catégorie:Argot en français\]\]', ur'', pageContent)

    if pageContent.find(u'\n[[Catégorie:Gentilés en français]]') != -1 and pageContent.find(u'{{note-gentilé|fr}}') != -1:
        pageContent = pageContent.replace(u'\n[[Catégorie:Gentilés en français]]', u'')

    return pageContent, summary


def formatTemplates(pageContent, summary):
    pageContent = pageContent.replace(u'}} \n', '}}\n')
    pageContent = pageContent.replace(u'\n {{', u'\n{{')

    if debugLevel > 1: print u' Formatage de la ligne de forme'
    pageContent = pageContent.replace(u'{{PAGENAME}}', u'{{subst:PAGENAME}}')
    pageContent = pageContent.replace(u'-rég}}\'\'\'', u'-rég}}\n\'\'\'')
    pageContent = pageContent.replace(u']] {{imperf}}', u']] {{imperf|nocat=1}}')
    pageContent = pageContent.replace(u']] {{perf}}', u']] {{perf|nocat=1}}')
    pageContent = pageContent.replace(u'{{perf}} / \'\'\'', u'{{perf|nocat=1}} / \'\'\'')

    pageContent = pageContent.replace(u'|pinv= ', u'|pinv=')
    pageContent = pageContent.replace(u'|pinv=. ', u'|pinv=.')

    if pageContent.find(u'{{vérifier création automatique}}') != -1:
        if debugLevel > 0: print u' {{vérifier création automatique}} trouvé'
        pageContent2 = pageContent
        LanguesV = u'|'
        while pageContent2.find(u'{{langue|') > 0:
            pageContent2 = pageContent2[pageContent2.find(u'{{langue|')+len(u'{{langue|'):]
            LanguesV += u'|' + pageContent2[:pageContent2.find('}}')]
        if LanguesV != u'|':
            pageContent = pageContent.replace(u'{{vérifier création automatique}}', 
                u'{{vérifier création automatique' + LanguesV + '}}')
        if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    if debugLevel > 0: print u' {{étyl}}'
    # TODO: regex pour toutes les langues concernées
    pageContent = pageContent.replace(u'Du {{étyl|en|', u'De l’{{étyl|en|')
    pageContent = pageContent.replace(u'du {{étyl|en|', u'de l’{{étyl|en|')
    pageContent = pageContent.replace(u'Du {{étyl|fro|', u'De l’{{étyl|fro|')
    pageContent = pageContent.replace(u'du {{étyl|fro|', u'de l’{{étyl|fro|')

    pageContent = pageContent.replace(u'Du {{étyl|en|', u'De l’{{étyl|en|')
    pageContent = pageContent.replace(u'Du {{étyl|it|', u'De l’{{étyl|it|')

    regex = ur"({{cf|)lang=[^\|}]+\|(:Catégorie:)"
    pageContent = re.sub(regex, ur"\1\2", pageContent)

    pageContent = pageContent.replace(u'\n \n', u'\n\n')
    pageContent = pageContent.replace(u'myt=scandinave', u'myt=nordique')
    pageContent = pageContent.replace(u'{{pron|}}', u'{{pron}}')
    pageContent = pageContent.replace(u'{{prononciation|}}', u'{{prononciation}}')
    regex = ur'({{pron\|[^\|}]*)g([^\|}]*)'
    while re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"\1ɡ\2", pageContent)

    pageContent = pageContent.replace(u'#*: {{trad-exe|fr}}', u'')
    pageContent = pageContent.replace(u'\n{{WP', u'\n* {{WP')
    pageContent = pageContent.replace(u'{{Source-wikt|nan|', u'{{Source-wikt|zh-min-nan|')
    pageContent = pageContent.replace(u'— {{source|', u'{{source|')
    pageContent = pageContent.replace(u'- {{source|', u'{{source|')
    regex = ur"(\{\{source\|[^}]+ )p\. *([0-9])"
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur"\1page \2", pageContent)

    if debugLevel > 1: print u' Modèles de son'
    regex = ur'({{écouter\|lang=([^\|]+)\|{{Région \?)}}'
    pageContent = re.sub(regex, ur'\1|\2}}', pageContent)
    regex = ur'\n *{{écouter\|'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\n* {{écouter|', pageContent)
    regex = ur'{{S\|prononciation}} ===\*'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'{{S|prononciation}} ===\n*', pageContent)

    limitReg = 13
    ModRegion = range(1, limitReg)
    ModRegion[1] = u'AU'
    ModRegion[2] = u'AR'
    ModRegion[3] = u'AT'
    ModRegion[4] = u'BE'
    ModRegion[5] = u'BR'
    ModRegion[6] = u'CA'
    ModRegion[7] = u'MX'
    ModRegion[8] = u'PT'
    ModRegion[9] = u'QC'
    ModRegion[10] = u'UK'
    ModRegion[11] = u'US'
    for m in range(1, limitReg-1):
        while pageContent.find(u'{{écouter|' + ModRegion[m] + u'|') != -1:
            pageContent = pageContent[:pageContent.find(u'{{écouter|' + ModRegion[m] + u'|')+len('{{écouter|')-1] \
             + '{{' + ModRegion[m] + u'|nocat=1}}' + pageContent[pageContent.find(u'{{écouter|' + ModRegion[m] + u'|')+len(u'{{écouter|' + ModRegion[m]):]

    regex = ur"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation\|[^}]*)\|m=1}} de([ '])"
    pageContent = re.sub(regex, ur'\1}} De\2', pageContent)
    regex = ur"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation)\|m=1(\|[^}]*)}} de([ '])"
    pageContent = re.sub(regex, ur'\1\2}} De\3', pageContent)

    if debugLevel > 1: print u' Ajout des modèles de référence' # les URL ne contiennent pas les diacritiques des {{PAGENAME}}
    while pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=') != -1:
        pageContent2 = pageContent[pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')+len(u'[http://www.sil.org/iso639-3/documentation.asp?id='):]
        pageContent = pageContent[:pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')] + u'{{R:SIL|' + pageContent2[:pageContent2.find(u' ')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
        summary = summary + u', ajout de {{R:SIL}}'
    while pageContent.find(u'[http://www.cnrtl.fr/definition/') != -1:
        pageContent2 = pageContent[pageContent.find(u'[http://www.cnrtl.fr/definition/')+len(u'[http://www.cnrtl.fr/definition/'):len(pageContent)]
        pageContent = pageContent[:pageContent.find(u'[http://www.cnrtl.fr/definition/')] + u'{{R:TLFi|' + pageContent2[:pageContent2.find(u' ')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
        summary = summary + u', ajout de {{R:TLFi}}'
    while pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/') != -1:
        pageContent2 = pageContent[pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/')+len(u'[http://www.mediadico.com/dictionnaire/definition/'):len(pageContent)]
        pageContent = pageContent[:pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/')] + u'{{R:Mediadico|' + pageContent2[:pageContent2.find(u'/1')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
        summary = summary + u', ajout de {{R:Mediadico}}'

    # TODO: Factorisation des citations
    #regex = ur"(?:— \(|{{source\|)Cirad/Gret/MAE, ''Mémento de l['’]Agronome'', 1 *692 p(?:\.|ages), p(?:\.|age) ([0-9 ]+), 2002, Paris, France, Cirad/Gret/Ministère des Affaires [EÉ]trangères \(\+ 2 cdroms\)(?:\)|}})"
    #if re.search(regex, pageContent):
    #    pageContent = re.sub(regex, ur"{{Citation/Cirad/Gret/MAE/Mémento de l’Agronome|\1}}", pageContent)

    return pageContent, summary


def formatLanguagesTemplates(pageContent, summary, pageName):
    if debugLevel > 0: print u' Templates by language'
    rePageName = re.escape(pageName)

    regex = u'{{(Latn|Grek|Cyrl|Armn|Geor|Hebr|Arab|Syrc|Thaa|Deva|Hang|Hira|Kana|Hrkt|Hani|Jpan|Hans|Hant|zh-mot|kohan|ko-nom|la-verb|grc-verb|polytonique|FAchar)[\|}]'
    if not re.search(regex, pageContent):
        if debugLevel > 0: print u' Headword addition'
        pageContent = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n\{\{[^\n]*\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", pageContent)

    if u'{{langue|fr}}' in pageContent:
        regex = ur'^[ 0-9a-zàâçéèêëîôùûA-ZÀÂÇÉÈÊËÎÔÙÛ]+$' #/:
        if re.search(regex, pageName):
            regex = ur"\n{{clé de tri([^}]*)}}"
            if re.search(regex, pageContent):
                if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                summary = summary + u', retrait de {{clé de tri}}'
                pageContent = re.sub(regex, '', pageContent)

        if debugLevel > 0: print u' Catégories de prononciation'
        if pageName[-2:] == u'um' and pageContent.find(u'ɔm|fr}}') != -1:
            pageContent = addCategory(pageContent, u'fr', u'um prononcés /ɔm/ en français')
        if pageName[:2] == u'qu':
            regex = ur'{{pron\|kw[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'qu prononcés /kw/ en français')
        if pageName[:2] == u'qu' and pageName[:4] != u'quoi':
            regex = ur'{{fr\-rég\|kw[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'qu prononcés /kw/ en français')
        if pageName[:2] == u'ch':
            regex = ur'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'ch':
            regex = ur'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'Ch':
            regex = ur'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'Ch':
            regex = ur'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-2:] == u'ch':
            regex = ur'{{pron\|[^}\|]+k\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-2:] == u'ch':
            regex = ur'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-3:] == u'chs':
            regex = ur'{{pron\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-3:] == u'chs':
            regex = ur'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')

        regex = ur'({{fr\-[^}]*\|[\'’]+=[^}]*)\|[\'’]+=[oui|1]'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|s=[^}]*)\|s=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|ms=[^}]*)\|ms=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|fs=[^}]*)\|fs=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)

        pageContent = pageContent.replace(u'{{louchébem|fr}}', u'{{louchébem}}')
        pageContent = pageContent.replace(u'{{reverlanisation|fr}}', u'{{reverlanisation}}')
        pageContent = pageContent.replace(u'{{verlan|fr}}', u'{{verlan}}')

# Ajout des redirections des pronominaux
        if pageContent.find(u'{{S|verbe|fr}}') != -1 and pageName[:3] != u'se' and pageName[:2] != u's’':
            pageContent2 = pageContent[pageContent.find(u'{{S|verbe|fr}}'):]
            regex = ur'(\n|\')s(e |’)\'\'\''
            if re.search(regex, pageContent2) is not None:
                if re.search(regex, pageContent2) < pageContent2.find(u'{{S|') or pageContent2.find(u'{{S|') == -1:
                    regex = ur'^[aeiouyàéèêôù]'
                    if re.search(regex, pageName):    # ne pas prendre [:1] car = & si encodage ASCII du paramètre DOS / Unix
                        pageName2 = u's’' + pageName
                    else:
                        pageName2 = u'se ' + pageName
                    page2 = Page(site, pageName2)
                    if not page2.exists():
                        if debugLevel > 0: print u'Création de ' + defaultSort(pageName2)
                        summary2 = u'Création d\'une redirection provisoire catégorisante du pronominal'
                        savePage(page2, u'#REDIRECT[[' + pageName + u']]\n<!-- Redirection temporaire avant de créer le verbe pronominal -->\n[[Catégorie:Wiktionnaire:Verbes pronominaux à créer en français]]', summary2)

        # Ajout de modèles pour les gentités et leurs adjectifs
        if debugLevel > 0: print u' Gentilés'
        regex = ur'({{fr\-[^}]+)\\'
        while re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)

        ligne = 6
        colonne = 4
        # TODO : fusionner avec le tableau des modèles de flexion
        ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
        ModeleGent[1][1] = ur'fr-accord-mixte'
        ModeleGent[1][2] = ur's'
        ModeleGent[1][3] = ur'e'
        ModeleGent[1][4] = ur'es'
        ModeleGent[2][1] = ur'fr-accord-s'
        ModeleGent[2][2] = ur''
        ModeleGent[2][3] = ur'e'
        ModeleGent[2][4] = ur'es'
        ModeleGent[3][1] = ur'fr-accord-el'
        ModeleGent[3][2] = ur's'
        ModeleGent[3][3] = ur'le'
        ModeleGent[3][4] = ur'les'
        ModeleGent[4][1] = ur'fr-accord-en'
        ModeleGent[4][2] = ur's'
        ModeleGent[4][3] = ur'ne'
        ModeleGent[4][4] = ur'nes'
        ModeleGent[5][1] = ur'fr-accord-et'
        ModeleGent[5][2] = ur's'
        ModeleGent[5][3] = ur'te'
        ModeleGent[5][4] = ur'tes'
        ModeleGent[6][1] = ur'fr-rég'
        ModeleGent[6][2] = ur's'
        ModeleGent[6][3] = ur''
        ModeleGent[6][4] = ur's'

        for l in range(1, ligne + 1):
            # Depuis un masculin
            regex = ur'\({{p}} : [\[\']*' + rePageName + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + rePageName + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageName + ModeleGent[l][4] + ur'[\]\']*\)'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', pageContent)
                summary = summary + u', conversion des liens flexions en modèle boite'
            # Depuis un féminin
            if ModeleGent[l][1] == ur'fr-accord-s' and rePageName[-1:] == u'e' and rePageName[-2:-1] == u's':
                regex = ur'\({{p}} : [\[\']*' + rePageName + ur's[\]\']*, {{m}} : [\[\']*' + rePageName[:-1] + ur'[\]\']*\)'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|ms=' + rePageName[:-1].replace(u'\\', u'') + '}}', pageContent)
                    summary = summary + u', conversion des liens flexions en modèle boite'
            regex = ur'\({{f}} : [\[\']*' + rePageName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + rePageName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageName + ModeleGent[l][4] + ur'[\]\']*\)'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', pageContent)
                summary = summary + u', conversion des liens flexions en modèle boite'
            if debugLevel > 1: print u' avec son'
            regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|[pron\=]*)}}'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, ur'\n\4\2}}\1\2\3', pageContent)

            deplacement_modele_flexion = False
            # On différencie les cas pas d'espace avant le modèle / espace avant le modèle
            regex = ur'( ===\n)(\'\'\'[^\n]+[^ ])({{' + ModeleGent[l][1] + ur'\|[^}]*}})'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, ur'\1\3\n\2', pageContent)
                deplacement_modele_flexion = True
            # Espace avant le modèle
            regex_space = ur'( ===\n)(\'\'\'[^\n]+) ({{' + ModeleGent[l][1] + ur'\|[^}]*}})'
            if re.search(regex_space, pageContent):
                pageContent = re.sub(regex_space, ur'\1\3\n\2', pageContent)
                deplacement_modele_flexion = True
            if deplacement_modele_flexion:
                summary = summary + u', déplacement des modèles de flexions'
                
        regex = ur'({{fr\-accord\-comp\-mf[^}]*\| *trait *=) *([\|}])'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1&nbsp;\2', pageContent)

    elif u'{{langue|en}}' in pageContent:
        regex = ur'(\|en}} ===\n{{)fr\-rég'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1en-nom-rég', pageContent)

        regex = ur"({{S\|verbe\|en}} *=* *\n'*)to "
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"\1", pageContent)

        regex = ur'(=== {{S\|adjectif\|en}} ===\n[^\n]*) *{{pluriel \?\|en}}'
        pageContent = re.sub(regex, ur"\1", pageContent)

    elif u'{{langue|es}}' in pageContent:
        regex = ur'(\|es}} ===\n{{)fr\-rég'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1es-rég-voy', pageContent)

        ligne = 1
        colonne = 4
        ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
        ModeleGent[1][1] = ur'es-accord-oa'
        ModeleGent[1][2] = ur'os'
        ModeleGent[1][3] = ur'a'
        ModeleGent[1][4] = ur'as'
        rePageRadicalName = re.escape(pageName[:-1])

        for l in range(1, ligne + 1):
            regex = ur'\({{p}} : [\[\']*' + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' \
             + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', pageContent)
                summary = summary + u', conversion des liens flexions en modèle boite'
            regex = ur'\({{f}} : [\[\']*' + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' \
             + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
            if debugLevel > 1: print regex.encode(config.console_encoding, 'replace')
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', pageContent)
                summary = summary + u', conversion des liens flexions en modèle boite'
            # Son
            if debugLevel > 0: print u' son'
            regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|' + rePageRadicalName + ur')}}'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, ur'\n\4|\2}}\1\2\3', pageContent)

    languageCodes = [u'fc', u'fro', u'frm', u'pt', u'pcd']
    for l in languageCodes:
        regex = ur'(\|' + l + ur'(:?\|num=[0-9])?}} ===\n{{)fr(\-rég)'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1' + l + ur'\3', pageContent)
    regex = ur'\n{{fro\-rég[^}]*}}'
    pageContent = re.sub(regex, ur'', pageContent)

    pageLanguages = getPageLanguages(pageContent)
    for pageLanguage in pageLanguages:
        etymTemplates = ['abréviation', 'acronyme', 'sigle']
        if pageLanguage == 'fr': etymTemplates = etymTemplates + ['louchébem', 'reverlanisation', 'verlan']
        for etymTemplate in etymTemplates:
            languageSection, lStart, lEnd = getLanguageSection(pageContent, pageLanguage)
            if languageSection is not None and len(getNaturesSections(languageSection)) == 1 and languageSection.find(etymTemplate[1:]) != -1:
                # Si le modèle à déplacer est sur la ligne de forme ou de définition
                regexTemplate = ur"\n'''[^\n]+(\n#)? *({{[^}]+}})? *({{[^}]+}})? *{{" + etymTemplate + ur'(\||})'
                if re.search(regexTemplate, languageSection):
                    newLanguageSection, summary = removeTemplate(languageSection, etymTemplate, summary, inSection = natures)
                    #TODO generic moveFromNatureToEtymology = remove après (u'|'.join(natures)) + addToEtymology, = addToLine(languageCode, section, append, prepend)
                    etymology, sStart, sEnd = getSection(newLanguageSection, u'étymologie')
                    if etymology is None:
                        newLanguageSection = addLine(newLanguageSection, pageLanguage, u'étymologie', u': {{ébauche-étym|' + pageLanguage + u'}}')
                        etymology, sStart, sEnd = getSection(newLanguageSection, u'étymologie')
                    if etymology is not None and etymology.find(u'{{' + etymTemplate) == -1:
                        regexEtymology = ur'(=\n:* *(\'*\([^\)]*\)\'*)?) *'
                        if re.search(regexEtymology, pageContent):
                            etymology2 = re.sub(regexEtymology, ur'\1 {{' + etymTemplate + ur'}} ', etymology)
                            newLanguageSection = newLanguageSection.replace(etymology, etymology2)
                            if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                            summary = summary + u', [[Wiktionnaire:Prise de décision/Déplacer les modèles de contexte' \
                            + u' étymologiques dans la section « Étymologie »|ajout de {{' + etymTemplate + ur"}} dans l'étymologie]]"
                    pageContent = pageContent.replace(languageSection, newLanguageSection)

    return pageContent, summary

def formatWikicode(pageContent, summary, pageName):
    #pageContent = pageContent.replace(u'&nbsp;', u' ') # TODO: à faire hors modèles https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:fr-accord-comp-mf&oldid=prev&diff=26238109
    #pageContent = re.sub(ur'«[  \t]*', ur'« ', pageContent) # pb &#160;
    #pageContent = re.sub(ur'[  \t]*»', ur' »', pageContent)
    pageContent = pageContent.replace(u'{|\n|}', u'')

    if debugLevel > 0: print u' #* or #:'
    pageContent = pageContent.replace(u'\n #*', u'\n#*')
    pageContent = pageContent.replace(u'\n #:', u'\n#:')
    finalPageContent = u''
    while pageContent.find(u'\n#:') != -1:
        finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n#:')+2]
        if finalPageContent.rfind(u'{{langue|') == finalPageContent.rfind(u'{{langue|fr}}'):
            pageContent = u'*' + pageContent[pageContent.find(u'\n#:')+len(u'\n#:'):]
        else:
            pageContent = u':' + pageContent[pageContent.find(u'\n#:')+len(u'\n#:'):]
    pageContent = finalPageContent + pageContent

    pageContent = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", pageContent)
    pageContent = pageContent.replace(u'[[' + pageName + u']]', u'\'\'\'' + pageName + u'\'\'\'')

    return pageContent, summary

def addAppendixLinks(pageContent, summary, pageName):
    LanguesC = [ (u'es',u'ar',u'arsi',u'er',u'ersi',u'ir',u'irsi'),
                 (u'pt',u'ar',u'ar-se',u'er',u'er-se',u'ir',u'ir-se'),
                 (u'it',u'are',u'arsi',u'ere',u'ersi',u'ire',u'irsi'),
                 (u'fr',u'er',u'er',u'ir',u'ir',u're',u'ar'),
                 (u'ru',u'',u'',u'',u'',u'',u'')
               ]
    if not ' ' in pageName and pageContent.find(u'{{voir-conj') == -1 \
        and pageContent.find(u'{{invar') == -1 and pageContent.find(u'{{verbe non standard') == -1 \
        and pageContent.find(u'[[Image:') == -1:
            # Sinon bug https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687
        if debugLevel > 0: print u' {{conj}}'
        for l in LanguesC:
            if not (l[0] == u'fr' and pageName[-3:] == u'ave'):
                if re.compile(ur'{{S\|verbe\|'+l[0]+'}}').search(pageContent) and not \
                    re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[= ]+\n+[^\n]*\n*[^\n]*\n*{{(conj[a-z1-3\| ]*|invar)').search(pageContent):
                    if debugLevel > 0: print u' {{conj|'+l[0]+u'}} manquant'
                    if re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}').search(pageContent):
                        if debugLevel > 0: print u' ajout de {{conj|'+l[0]+u'}} après {{pron|...}}'
                        try:
                            i1 = re.search(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}', pageContent).end()
                            pageContent = pageContent[:i1] + u' {{conjugaison|'+l[0]+'}}' + pageContent[i1:]
                        except:
                            if debugLevel > 0: print u' Erreur l 5390'
                    else:
                        if debugLevel > 0: print u' pas de prononciation pour ajouter {{conj}}'

    return pageContent, summary

'''
TODO:
    deploy addPronunciationFromContent()
    def sortSections(pageContent):
    def uncategorizeDoubleTemplateWhenCategory(pageContent, summary):
    def checkTranslationParagraphsNumberBySense(pageContent, summary):

if pageContent.find(u'{{conj') != -1:
    if debugLevel > 0: print u' Ajout des groupes dans {{conj}}'
'''

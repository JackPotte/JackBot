#!/usr/bin/env python
# coding: utf-8
# Ce script formate les pages de la Wikiversité :
# 1) Il retire les clés de tri devenues inutiles.
# 2) Il complète les modèles {{Chapitre}} à partir des {{Leçon}}.
# 3) Ajoute {{Bas de page}}.
# Reste à faire :
# 4) Remplir les {{Département}} à remplir à partir des {{Leçon}}.
# 5) Compléter les {{Bas de page}} existants.

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

checkURL = False
CorrigerModeles = False
fixTags = True

deprecatedTags = {}
deprecatedTags['big'] = 'strong'
deprecatedTags['center'] = 'div style="text-align: center;"'
deprecatedTags['font color *= *"?'] = 'span style="color:'
deprecatedTags['font size *= *"?\+?\-?'] = 'span style="font-size:'
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

sizeT = 3
sizeP = 12

temp = range(1, sizeT)
Ttemp = range(1, sizeT)
temp[1] = u'numero'
Ttemp[1] = u'numéro'

# Modèle:Chapitre
param = range(1, sizeP)
param[1] = u'titre ' # espace pour disambiguiser
param[2] = u'idfaculté'
param[3] = u' leçon'
param[4] = u'page'
param[5] = u'numero'
param[6] = u'précédent'
param[7] = u'suivant'
param[8] = u'align'
param[9] = u'niveau'
param[10] = u'titre_leçon'


def modification(PageHS):
    summary = u'Formatage'
    PageEnd = "" # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première
    page = Page(site,PageHS)
    print(PageHS.encode(config.console_encoding, 'replace'))
    if page.exists():
        try:
            PageBegin = page.get()
        except pywikibot.exceptions.NoPage:
            print "NoPage"
            return
        except pywikibot.exceptions.IsRedirectPage:
            print "Redirect page"
            return
        except pywikibot.exceptions.LockedPage:
            print "Locked/protected page"
            return
    else:
        print u'Page inexistante'
        return
    PageTemp = PageBegin
 
    #https://fr.wiktionary.org/wiki/Sp%C3%A9cial:LintErrors/bogus-image-options
    badFileParameters = []
    badFileParameters.append(u'')
    for badFileParameter in badFileParameters:
        regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *' + badFileParameter + ur' *(\||\])'
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

    if fixTags:
        if debugLevel > 0: print u'Remplacements des balises'
        PageTemp = PageTemp.replace(u'</br>', u'<br/>')

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
                summary = summary + u', ajout de ' + newTag
                #PageTemp = re.sub(regex, ur'<' + newTag + ur'\1>', PageTemp)
                pattern = re.compile(regex, re.UNICODE)
                for match in pattern.finditer(PageTemp):
                    if debugLevel > 0: print match.group(1)
                    if newTag.find(u'font-size') != -1:
                        size = match.group(1).replace('"', '')
                        try:
                            size = int(size)
                            if size > 7: size = 7
                        except ValueError:
                            pass
                        openingTag = newTag + str(fontSize[size]) + ur'em"'
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
            summary = summary + u', correction de color'
            PageTemp = re.sub(regex, ur'<span style="color:' + s.group(1) + ur'">', PageTemp)

        regex = ur'<span style="text\-size:([0-9]+)"?>'
        s = re.search(regex, PageTemp)
        if s:
            summary = summary + u', correction de font-size'
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

        regex = ur'(\|(ar|fa)(\|flexion)*}} *===\n)<span style *= *"font\-size:[0-9\.]*em">\'\'\'([^\']*)\'\'\'</span>'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"\1'''{{Arab|\4}}'''", PageTemp)
        PageTemp = PageTemp.replace(u'[[Category:', u'[[Catégorie:')

    PageTemp = PageTemp.replace(u'<source lang="html4strict">', u'<source lang="html">')


    if page.namespace() == 0:
        templates = []
        templates.append('bas de page')
        templates.append('chapitre')
        templates.append('cfExo')
        templates.append('département')
        templates.append('évaluation')
        templates.append('leçon')
        for template in templates:
            PageTemp = replaceParameterValue(PageTemp, template, 'idfaculté', 'langues étrangères', 'langues')

        # Clés de tri
        sizeR = 7
        regex = range(1, sizeR+1)
        regex[1] = ur'()\n{{[Cc]lé de tri[^}]*}}'
        regex[2] = ur'({{[Cc]hapitre[^}]*)\| *clé *=[^}\|]*'
        regex[3] = ur'({{[Ll]eçon[^}]*)\| *clé *=[^}\|]*'
        regex[4] = ur'({{[Cc]ours[^}]*)\| *clé *=[^}\|]*'
        regex[5] = ur'({{[Dd]épartement[^}]*)\| *clé *=[^}\|]*'
        regex[6] = ur'({{[Ff]aculté[^}]*)\| *clé *=[^}\|]*'

        for p in range(1, sizeR-1):
            if re.search(regex[p], PageTemp):
                PageTemp = re.sub(regex[p], ur'\1', PageTemp)
                if summary.find(u'clé de tri') == -1: summary = summary + u', retrait de la clé de tri'

        # Remplacements consensuels
        for p in range(1,sizeT-1):
            if PageTemp.find(u'{{' + temp[p] + u'|') != -1 or PageTemp.find(u'{{' + temp[p] + u'}}') != -1:
                PageTemp = PageTemp[0:PageTemp.find(temp[p])] + Ttemp[p] + PageTemp[PageTemp.find(temp[p])+len(temp[p]):len(PageTemp)]
            #p=p+1

        # http://fr.wikiversity.org/wiki/Catégorie:Modèle_mal_utilisé
        if CorrigerModeles == True:
            if PageTemp.find('{Chapitre') != -1 or PageTemp.find('{chapitre') != -1:
                    ''' Bug du modèle tronqué :
                    if re.compile('{Chapitre').search(PageTemp):
                            if re.compile('{Chapitre[.\n]*(\n.*align.*=.*\n)').search(PageTemp):
                                    i1 = re.search(u'{{Chapitre[.\n]*(\n.*align.*=.*\n)',PageTemp).end()
                                    i2 = re.search(u'(\n.*align.*=.*\n)',PageTemp[:i1]).start()
                                    PageTemp = PageTemp[:i2] + u'\n' + PageTemp[i1:]
                            PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                            PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                    elif re.compile('{chapitre').search(PageTemp):
                            if re.compile('{chapitre[.\n]*(\n.*align.*=.*\n)').search(PageTemp):
                                    i1 = re.search(u'{{chapitre[.\n]*(\n.*align.*=.*\n)',PageTemp).end()
                                    i2 = re.search(u'(\n.*align.*=.*\n)',PageTemp[:i1]).start()
                                    PageTemp = PageTemp[:i2] + u'\n' + PageTemp[i1:]
                            PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
                            PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]

                            if re.compile('{{Chapitre[\n.]*(\n.*leçon.*=.*\n)').search(PageTemp):
                                    print "leçon1"
                            if re.compile('{{Chapitre.*\n.*\n.*(\n.*leçon.*=.*\n)').search(PageTemp):
                                    print "le�on2"
                            if re.compile('{{Chapitre.*\n.*\n.*\n.*(\n.*leçon.*=.*\n)').search(PageTemp):
                                    print "leçon3"
                            if re.compile('{{Chapitre[.\n]*(\n.*niveau.*=.*\n)').search(PageTemp):
                                    print "niveau"
                                    print re.compile('{{Chapitre[.\n]*(\n.*niveau.*=.*\n)').search(PageTemp)
                            if re.compile('{{Chapitre[.\n]*(\n.*précédent.*=.*\n)').search(PageTemp):
                                    print "précédent"
                            if re.compile('{{Chapitre[.\n]*(\n.*suivant.*=.*\n)').search(PageTemp):
                                    print "suivant"
                    else: # Pas de modèle chapitre
                            print u'Pas de chapitre dans :'
                            print (PageHS.encode(config.console_encoding, 'replace'))
                            return
                    raw_input (PageTemp.encode(config.console_encoding, 'replace'))'''

                    Lecon = u''
                    # Majuscule
                    if PageTemp.find(u'Leçon') != -1 and PageTemp.find(u'Leçon') < 100:
                            PageTemp2 = PageTemp[PageTemp.find(u'Leçon'):len(PageTemp)]
                            Lecon = Valeur(u'Leçon',PageTemp)
                    # Minuscule
                    elif PageTemp.find(u'leçon') != -1 and PageTemp.find(u'leçon') < 100:
                            PageTemp2 = PageTemp[PageTemp.find(u'leçon'):len(PageTemp)]
                            Lecon = Valeur(u'leçon',PageTemp)
                    #raw_input (Lecon.encode(config.console_encoding, 'replace'))

                    if Lecon.find(u'|') != -1:
                            Lecon = Lecon[0:Lecon.find(u'|')]
                    while Lecon[0:1] == u'[':
                            Lecon = Lecon[1:len(Lecon)]
                    while Lecon[len(Lecon)-1:len(Lecon)] == u']':
                            Lecon = Lecon[0:len(Lecon)-1]
                    if (Lecon == u'../' or Lecon == u'') and PageHS.find(u'/') != -1:
                            Lecon = PageHS[0:PageHS.rfind(u'/')]
                    #raw_input (Lecon.encode(config.console_encoding, 'replace'))

                    if Lecon != u'' and Lecon.find(u'.') == -1: 
                        page2 = Page(site,Lecon)
                        if page2.exists():
                            if page2.namespace() != 0 and page2.title() != u'Utilisateur:JackBot/test': 
                                return
                            else:
                                try:
                                    PageLecon = page2.get()
                                except pywikibot.exceptions.NoPage:
                                    print "NoPage"
                                    return
                                except pywikibot.exceptions.IsRedirectPage:
                                    PageLecon = page2.getRedirectTarget().get()
                                except pywikibot.exceptions.LockedPage:
                                    print "Locked/protected page"
                                    return
                            #raw_input (PageLecon.encode(config.console_encoding, 'replace'))

                            # Majuscule
                            if PageLecon.find(u'{{Leçon') != -1:
                                if Valeur(u'Leçon',PageTemp) == u'':
                                    if PageTemp.find(u'Leçon') < PageTemp.find(u'}}') or PageTemp.find(u'Leçon') < PageTemp.find(u'}}'):
                                        if Valeur(u'Leçon',PageTemp) == u'':
                                            PageTemp2 = PageTemp[PageTemp.find(u'Leçon')+len(u'Leçon'):len(PageTemp)]
                                            PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
                                            while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u' ' or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'\t':
                                                PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
                                            if PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'=':
                                                PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'Leçon')+len(u'Leçon')+PageTemp2.find(u'=')+1] + page2.title()
                                                PageTemp = PageTemp[PageTemp.find(u'Leçon')+len(u'Leçon')+PageTemp2.find(u'=')+1:len(PageTemp)]
                                            else:
                                                print u'Signe égal manquant dans :'
                                                print PageTemp2[len(PageTemp2)-1:len(PageTemp2)]
                                    else:
                                        PageEnd = PageEnd + u'\n|Leçon=' + page2.title()
                                PageEnd = PageEnd + PageTemp
                                if PageLecon.find(u'niveau') != -1:
                                    PageTemp = PageLecon[PageLecon.find(u'niveau'):len(PageLecon)]
                                    if PageTemp.find(u'=') < PageTemp.find(u'\n') and PageTemp.find(u'=') != -1:
                                        if Valeur(u'niveau',PageLecon) != -1:
                                            PageTemp = PageEnd
                                            if PageTemp.find(u'{{Chapitre') != -1:
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                            elif PageTemp.find(u'{{chapitre') != -1:
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
                                            else: return
                                            if PageTemp.find(u'niveau') < PageTemp.find(u'}}') and PageTemp.find(u'niveau') != -1:
                                                PageTemp2 = PageTemp[PageTemp.find(u'niveau')+len(u'niveau'):len(PageTemp)]
                                                while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                    PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                if PageTemp2[0:PageTemp2.find(u'\n')] == u'':
                                                    PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'niveau')+len(u'niveau')] + "=" + Valeur(u'niveau',PageLecon)
                                                    PageTemp = PageTemp2
                                                elif Valeur(u'niveau',PageLecon) != PageTemp2[0:PageTemp2.find(u'\n')]:
                                                    if debugLevel > 0: 
                                                        print u'Différence de niveau dans ' + PageHS.encode(config.console_encoding, 'replace') + u' : '
                                                        print Valeur(u'niveau',PageLecon)
                                                        print PageTemp2[0:PageTemp2.find(u'\n')].encode(config.console_encoding, 'replace')
                                            else:
                                                PageEnd = PageEnd + u'\n  | niveau      = ' + Valeur(u'niveau',PageLecon)
                                            #print (PageEnd.encode(config.console_encoding, 'replace'))
                                            #raw_input (PageTemp.encode(config.console_encoding, 'replace'))
                            # Minuscule
                            elif PageLecon.find(u'{{leçon') != -1:
                                if Valeur(u'leçon',PageTemp) == u'':
                                    if PageTemp.find(u'leçon') < PageTemp.find(u'}}') or PageTemp.find(u'leçon') < PageTemp.find(u'}}'):
                                        if Valeur(u'leçon',PageTemp) == u'':
                                            PageTemp2 = PageTemp[PageTemp.find(u'leçon')+len(u'leçon'):len(PageTemp)]
                                            PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
                                            while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u' ' or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'\t':
                                                PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
                                            if PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'=':
                                                PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'leçon')+len(u'leçon')+PageTemp2.find(u'=')+1] + page2.title()
                                                PageTemp = PageTemp[PageTemp.find(u'leçon')+len(u'leçon')+PageTemp2.find(u'=')+1:len(PageTemp)]
                                            else:
                                                print u'Signe égal manquant dans :'
                                                print PageTemp2[len(PageTemp2)-1:len(PageTemp2)]
                                    else:
                                        PageEnd = PageEnd + u'\n|leçon=' + page2.title()
                                PageEnd = PageEnd + PageTemp
                                PageTemp = u''
                                if PageLecon.find(u'niveau') != -1:
                                    niveauLecon = Valeur(u'niveau',PageLecon)
                                    print niveauLecon
                                    PageTemp = PageLecon[PageLecon.find(u'niveau'):len(PageLecon)]
                                    if PageTemp.find(u'=') < PageTemp.find(u'\n') and PageTemp.find(u'=') != -1:
                                        if niveauLecon != -1:
                                            PageTemp = PageEnd
                                            if PageTemp.find(u'{{Chapitre') != -1:
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                            elif PageTemp.find(u'{{chapitre') != -1:
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
                                            else: return
                                            if PageTemp.find(u'niveau') < PageTemp.find(u'}}') and PageTemp.find(u'niveau') != -1:
                                                PageTemp2 = PageTemp[PageTemp.find(u'niveau')+len(u'niveau'):len(PageTemp)]
                                                while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                    PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                niveauChapitre = PageTemp2[0:PageTemp2.find(u'\n')]
                                                if niveauChapitre == u'':
                                                    PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'niveau')+len(u'niveau')] + "=" + niveauLecon
                                                    PageTemp = PageTemp2
                                                elif niveauChapitre != niveauLecon:
                                                    print u'Niveau du chapitre différent de celui de la leçon dans ' + PageHS.encode(config.console_encoding, 'replace')
                                            else:
                                                PageEnd = PageEnd + u'\n|niveau=' + niveauLecon

                            PageEnd = PageEnd + PageTemp
                            PageTemp = u''
                            #raw_input (PageEnd.encode(config.console_encoding, 'replace'))

                            '''print Valeur(u'niveau',PageEnd)
                            print u'********************************************'
                            print Valeur(u'numéro',PageEnd)
                            print u'********************************************'
                            print Valeur(u'précédent',PageEnd)
                            print u'********************************************'
                            print Valeur(u'suivant',PageEnd)
                            raw_input(u'Fin de paramètres')'''
                            NumLecon = u''
                            PageTemp2 = u''
                            if Valeur(u'numéro',PageEnd) == u'' or Valeur(u'précédent',PageEnd) == u'' or Valeur(u'suivant',PageEnd) == u'':
                                if PageLecon.find(PageHS) != -1:
                                        PageTemp2 = PageLecon[0:PageLecon.find(PageHS)]    # Nécessite que le département ait un nom déifférent et que les leçons soient bien nommées différemment
                                elif PageLecon.find(PageHS[PageHS.rfind(u'/')+1:len(PageHS)]) != -1:
                                        PageTemp2 = PageLecon[0:PageLecon.find(PageHS[PageHS.rfind(u'/')+1:len(PageHS)])]
                                if PageTemp2 != u'':
                                        while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == " " or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "=" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "[" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "{" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "|" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{C" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{c" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{L" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{l":
                                                PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
                                        if PageTemp2.rfind(u' ') > PageTemp2.rfind(u'|'):
                                                NumLecon = PageTemp2[PageTemp2.rfind(u' ')+1:len(PageTemp2)]
                                        else:
                                                NumLecon = PageTemp2[PageTemp2.rfind(u'|')+1:len(PageTemp2)]
                                        #print (PageTemp2.encode(config.console_encoding, 'replace'))                
                                        if NumLecon != u'' and NumLecon != u'département':
                                            # Le numéro de la leçon permet de remplir les champs : |numéro=, |précédent=, |suivant=
                                            if Valeur(u'numéro',PageEnd) == u'':
                                                if PageEnd.find(u'numéro') == -1:
                                                    PageTemp = PageEnd
                                                    PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                    PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                                    if PageTemp.find(u'numéro') < PageTemp.find(u'}}') and PageTemp.find(u'numéro') != -1:
                                                        PageTemp2 = PageTemp[PageTemp.find(u'numéro')+len(u'numéro'):len(PageTemp)]
                                                        while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                            PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                        PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'numéro')+len(u'numéro')] + "=" + NumLecon
                                                        PageTemp = PageTemp2
                                                    else:
                                                        PageEnd = PageEnd + u'\n|numéro=' + NumLecon
                                                    PageEnd = PageEnd + PageTemp
                                                    PageTemp = u''
                                            if Valeur(u'précédent',PageEnd) == u'' and NumLecon    == 1:
                                                PageTemp = PageEnd
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                                if PageTemp.find(u'précédent') < PageTemp.find(u'}}') and PageTemp.find(u'précédent') != -1:
                                                    PageTemp2 = PageTemp[PageTemp.find(u'précédent')+len(u'précédent'):len(PageTemp)]
                                                    while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                        PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                    PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+len(u'précédent')] + "=" + NumLecon
                                                    PageTemp = PageTemp2
                                                else:
                                                    PageEnd = PageEnd + u'\n|précédent=' + NumLecon
                                                PageEnd = PageEnd + PageTemp
                                                PageTemp = u''                                
                                            elif Valeur(u'précédent',PageEnd) == u'' and Valeur(str(int(NumLecon)-1),PageLecon) != u'':
                                                PageTemp = PageEnd
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                                if PageTemp.find(u'précédent') < PageTemp.find(u'}}') and PageTemp.find(u'précédent') != -1:
                                                    PageTemp2 = PageTemp[PageTemp.find(u'précédent')+len(u'précédent'):len(PageTemp)]
                                                    while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                        PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                    PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+len(u'précédent')] + "=" + Valeur(str(int(NumLecon)-1),PageLecon)
                                                    PageTemp = PageTemp2
                                                else:
                                                    PageEnd = PageEnd + u'\n|précédent=' + Valeur(str(int(NumLecon)-1),PageLecon)
                                                PageEnd = PageEnd + PageTemp
                                                PageTemp = u''
                                            if Valeur(u'suivant',PageEnd) == u'' and Valeur(str(int(NumLecon)+1),PageLecon) != u'':                    
                                                PageTemp = PageEnd
                                                PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
                                                PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                                                if PageTemp.find(u'suivant') < PageTemp.find(u'}}') and PageTemp.find(u'suivant') != -1:
                                                    PageTemp2 = PageTemp[PageTemp.find(u'suivant')+len(u'suivant'):len(PageTemp)]
                                                    while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
                                                        PageTemp2 = PageTemp2[1:len(PageTemp2)]
                                                    PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'suivant')+len(u'suivant')] + "=" + Valeur(str(int(NumLecon)+1),PageLecon)
                                                    PageTemp = PageTemp2
                                                else:
                                                    if PageTemp.find(u'précédent') != -1:
                                                        PageTemp2 = PageTemp[PageTemp.find(u'précédent'):len(PageTemp)]
                                                        PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+PageTemp2.find(u'\n')] + u'\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
                                                        PageTemp = PageTemp[PageTemp.find(u'précédent')+PageTemp2.find(u'\n'):len(PageTemp)]
                                                    else:
                                                        PageEnd = PageEnd + u'\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
                                                PageEnd = PageEnd + PageTemp
                                                PageTemp = u''
                        else: # Pas de leçon
                            print u'Pas de leçon : '
                            print (Lecon.encode(config.console_encoding, 'replace'))
                            print u'dans : '
                            print (PageHS.encode(config.console_encoding, 'replace'))
                            #raw_input ('Attente')
                        PageEnd = PageEnd + PageTemp
                        PageTemp = u''
            elif PageTemp.find(u'{Leçon') != -1 or PageTemp.find(u'{leçon') != -1:
                # Evaluations
                page2 = Page(site,u'Discussion:' + PageHS)
                if page2.exists():
                    try:
                        PageDisc = page2.get()
                    except pywikibot.exceptions.NoPage:
                        print "NoPage"
                        return
                    except pywikibot.exceptions.IsRedirectPage:
                        print "Redirect page"
                        return
                    except pywikibot.exceptions.LockedPage:
                        print "Locked/protected page"
                        return
                else: 
                    PageDisc = u''
                if PageDisc.find(u'{{Évaluation') == -1 and PageDisc.find(u'{{évaluation') == -1: sauvegarde(page2, u'{{Évaluation|idfaculté=' + Valeur(u'idfaculté',PageTemp) + u'|avancement=?}}\n' + PageDisc, u'Ajout d\'évaluation inconnue')    

                # Synchronisations avec les niveaux des départements, et les évaluations des onglets Discussion:
                #...
            PageEnd = PageEnd + PageTemp

            # Bas de page
            if (PageEnd.find(u'{{Chapitre') != -1 or PageEnd.find(u'{{chapitre') != -1) and PageEnd.find(u'{{Bas de page') == -1 and PageEnd.find(u'{{bas de page') == -1:
                idfaculte = u''
                precedent = u''
                suivant = u''
                if PageEnd.find(u'idfaculté') != -1:
                    PageTemp = PageEnd[PageEnd.find(u'idfaculté'):len(PageEnd)]
                    idfaculte = PageTemp[0:PageTemp.find(u'\n')]    # pb si tout sur la même ligne, faire max(0,min(PageTemp.find(u'\n'),?))
                    if PageEnd.find(u'précédent') != -1:
                        PageTemp = PageEnd[PageEnd.find(u'précédent'):len(PageEnd)]
                        precedent = PageTemp[0:PageTemp.find(u'\n')]
                    if PageEnd.find(u'suivant') != -1:
                        PageTemp = PageEnd[PageEnd.find(u'suivant'):len(PageEnd)]
                        suivant = PageTemp[0:PageTemp.find(u'\n')]
                    PageEnd = PageEnd + u'\n\n{{Bas de page|' + idfaculte + u'\n|' + precedent + u'\n|' + suivant + u'}}'

            # Exercices (pb http://fr.wikiversity.org/w/index.php?title=Allemand%2FVocabulaire%2FFormes_et_couleurs&diff=354352&oldid=354343)
            '''PageTemp = PageEnd
            PageEnd = u''
            while PageEnd.find(u'{{CfExo') != -1 or PageEnd.find(u'{{cfExo') != -1:
                PageTemp = PageEnd[
                if 
                |exercice=[[
                /Exercices/
                /quiz/
            PageEnd = PageEnd + PageTemp'''

    PageEnd = PageEnd + PageTemp
    PageTemp = u''

    # Test des URL
    if debugLevel > 0: print u'Test des URL'
    PageEnd = hyperlynx(PageEnd)
    if debugLevel > 1: raw_input (u'--------------------------------------------------------------------------------------------')

    if PageBegin != PageEnd: sauvegarde(page, PageEnd, summary)


def getWiki(language = 'fr', family = 'wiktionary'):
    if debugLevel > 1: print u'get ' + language + u'.' + family
    return pywikibot.Site(language, family)

def Valeur(Mot,Page):
    #raw_input(u'Bug http://fr.wikiversity.org/w/index.php?title=Initiation_%C3%A0_l%27arithm%C3%A9tique/PGCD&diff=prev&oldid=386685')
    if re.search(u'\n *' + Mot + u' *=', Page):
        niveau = re.sub(u'\n *' + Mot + u' *=()[\n|\||}|{]', ur'$1', Page)
        if debugLevel > 0: raw_input(niveau)
        #return
    '''
    if Page.find(u' ' + Mot) != Page.find(Mot)-1 and Page.find(u'|' + Mot) != Page.find(Mot)-1: # Pb du titre_leçon
        PageTemp2 = Page[Page.find(Mot)+len(Mot):len(Page)]
    else:
        PageTemp2 = Page
    if PageTemp2.find(Mot) == -1:
        return u''
    else:
        PageTemp2 = PageTemp2[PageTemp2.find(Mot)+len(Mot):len(PageTemp2)]
        PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
        if PageTemp2.find (u'{{C|') != -1:        
            PageTemp2 = PageTemp2[PageTemp2.find (u'{{C|')+4:len(PageTemp2)]
            PageTemp2 = u'[[../' + PageTemp2[0:PageTemp2.find (u'|')] + u'/]]'
        while PageTemp2[0:1] == u' ' or PageTemp2[0:1] == u'\t' or PageTemp2[0:1] == u'=':
            PageTemp2 = PageTemp2[1:len(PageTemp2)]
        if PageTemp2[0:3] == u'[[/':        
            PageTemp2 = u'[[..' + PageTemp2[2:len(PageTemp2)]
        return PageTemp2
    '''            

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

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    if source:
        PagesHS = open(source, 'r')
        while 1:
            PageHS = PagesHS.readline()
            fin = PageHS.find("\t")
            PageHS = PageHS[0:fin]
            if PageHS == '': break
            if PageHS.find(u'[[') != -1:
                PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
            if PageHS.find(u']]') != -1:
                PageHS = PageHS[0:PageHS.find(u']]')]
            modification(PageHS)
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
                if debugLevel > 1: print u' balises HTML désuètes'
                for deprecatedTag in deprecatedTags.keys():
                    if PageTemp.find(u'<' + deprecatedTag) != -1:
                        outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

        outPutFile.close()
 
# Traitement d'une catégorie
def crawlerCat(category, recursif, apres, doc = False):
    modifier = u'False'
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    #gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) HS sur Commons
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title())
            if doc: modification(Page.title() + u'/Documentation')
        elif Page.title() == apres:
            modifier = u'True'
    if recursif == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            if subcategory.title().find(u'.ogg') == -1 and subcategory.title().find(u'spoken') == -1 and subcategory.title().find(u'Wikipedia') == -1 and subcategory.title().find(u'Wikinews') == -1:
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
    if recursif == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            if subcategory.title().find(u'.ogg') == -1 and subcategory.title().find(u'spoken') == -1 and subcategory.title().find(u'Wikipedia') == -1 and subcategory.title().find(u'Wikinews') == -1:
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                    modification(Page.title())

# Traitement des pages liées
def crawlerLink(pagename, apres, doc = False):
    modifier = u'False'
    page = pywikibot.Page(site, pagename)
    gen = pagegenerators.ReferringPageGenerator(page)
    #gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if debugLevel > 1: print(Page.title().encode(config.console_encoding, 'replace'))
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title())
            if doc: modification(Page.title() + u'/Documentation')
        elif Page.title() == apres:
            modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
    modifier = u'False'
    cat = catlib.Category(site, pagename)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        page = pywikibot.Page(site, Page.title())
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
            #print(Page.title().encode(config.console_encoding, 'replace'))
            if not apres or apres == u'' or modifier == u'True':
                modification(PageLiee.title()) #crawlerLink(Page.title())
            elif PageLiee.title() == apres:
                modifier = u'True'
                
# Traitement d'une recherche
def crawlerSearch(pagename):
    gen = pagegenerators.SearchPageGenerator(pagename, site=site, namespaces=6)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
    gen = pagegenerators.RecentchangesPageGenerator()
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
    gen = pagegenerators.UserContributionsGenerator(username)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Toutes les redirections
def crawlerRedirects():
    for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
        modification(Page.title())    
                                        
# Traitement de toutes les pages du site
def crawlerAll(start):
    gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print (Page.title().encode(config.console_encoding, 'replace'))
        modification(Page.title())

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
    page = Page(site,u'User talk:' + username)
    if page.exists():
        PageTemp = u''
        try:
            PageTemp = page.get()
        except pywikibot.exceptions.NoPage: return
        except pywikibot.exceptions.IsRedirectPage: return
        except pywikibot.exceptions.LockedPage: return
        except pywikibot.exceptions.ServerError: return
        except pywikibot.exceptions.BadTitle: return
        except pywikibot.EditConflict: return
        if PageTemp != u"{{/Stop}}":
            pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
            exit(0)

def sauvegarde(PageCourante, Contenu, summary):
    result = "ok"
    if debugLevel > 0:
        if len(Contenu) < 6000:
            print(Contenu.encode(config.console_encoding, 'replace'))
        else:
            taille = 3000
            print(Contenu[:taille].encode(config.console_encoding, 'replace'))
            print u'\n[...]\n'
            print(Contenu[len(Contenu)-taille:].encode(config.console_encoding, 'replace'))
        result = raw_input((u'Sauvegarder [['+PageCourante.title()+u']] ? (o/n) ').encode('utf-8'))
    if result != "n" and result != "no" and result != "non":
        if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
        if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            PageCourante.put(Contenu, summary)
        except pywikibot.exceptions.NoPage: 
            print "NoPage en sauvegarde"
            return
        except pywikibot.exceptions.IsRedirectPage: 
            print "IsRedirectPage en sauvegarde"
            return
        except pywikibot.exceptions.LockedPage: 
            print "LockedPage en sauvegarde"
            return
        except pywikibot.EditConflict: 
            print "EditConflict en sauvegarde"
            return
        except pywikibot.exceptions.ServerError: 
            print "ServerError en sauvegarde"
            return
        except pywikibot.exceptions.BadTitle: 
            print "BadTitle en sauvegarde"
            return
        except AttributeError:
            print "AttributeError en sauvegarde"
            return


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
            crawlerXML(u'dumps/frwikiversity-20170720-pages-meta-current.xml', regex)
        elif sys.argv[1] == u'link' or sys.argv[1] == u'm':
            crawlerLink(site, u'Modèle:ex',u'')
        elif sys.argv[1] == u'cat':
            crawlerCat(u'Caractères en braille', True, u'')
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
        while 1:
            crawlerRC()

if __name__ == "__main__":
    main(sys.argv)

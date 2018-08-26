#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

debugLevel = 0

#*** General functions ***
def setGlobals(myDebugLevel, mySite, myUsername):
    global debugLevel
    global site
    global username
    debugLevel  = myDebugLevel
    site        = mySite
    username    = myUsername 

def globalOperations(pageContent):
    # Dmoz a fermé et bug https://fr.wikipedia.org/w/index.php?title=Flup,_N%C3%A9nesse,_Poussette_et_Cochonnet&diff=150799141&oldid=150798957
    #pageContent = replaceDMOZ(pageContent)
    #pageContent = replaceISBN(pageContent)
    #pageContent = replaceRFC(pageContent)

    # Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
    pageContent = re.sub(ur'{{ *(formatnum|Formatnum|FORMATNUM)\:([0-9]*) *([0-9]*)}}', ur'{{\1:\2\3}}', pageContent)
    return pageContent

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
    if page.exists():
        version = page.getLatestEditors(1)
        dateNow = datetime.datetime.utcnow()
        maxDate = dateNow - datetime.timedelta(minutes=timeAfterLastEdition)
        if debugLevel > 1:
            print maxDate.strftime('%Y-%m-%dT%H:%M:%SZ')
            print version[0]['timestamp']
            print version[0]['timestamp'] < maxDate.strftime('%Y-%m-%dT%H:%M:%SZ')   
        if version[0]['timestamp'] < maxDate.strftime('%Y-%m-%dT%H:%M:%SZ') or username in page.title() or page.contributors(total=1).keys()[0] == 'JackPotte':
            return True
        if debugLevel > 0: pywikibot.output(u' \03{red}the last edition is too recent to edit: \03{default}' + version[0]['timestamp'])
    return False

def isTrustedVersion(page, site = site):
    firstEditor = page.oldest_revision['user']
    lastEditor = page.contributors(total=1).keys()[0]
    if firstEditor == lastEditor:
        if debugLevel > 0: pywikibot.output(u' \03{green} the page belongs to its last edition user: \03{default}' + lastEditor)
        return True
    userPage = u' user: ' + lastEditor
    page = Page(site, userPage)
    user = User(page)
    if u'autoconfirmed' in user.groups():
        if debugLevel > 0: pywikibot.output(u' \03{green} the last edition user can be trusted: \03{default}' + lastEditor)
        return True
    if user.isAnonymous():
        if debugLevel > 0: pywikibot.output(u' \03{red}the last edition user cannot be trusted: \03{default}' + lastEditor)
        pywikibot.output(u' \03{red}to check manually\03{default}')
        return False
    if debugLevel > 0: pywikibot.output(u' \03{green} the last edition user could be trusted: \03{default}' + lastEditor)
    return True

def getContentFromPageName(pageName, allowedNamespaces = None, site = site):
    page = Page(site, pageName)
    return getContentFromPage(page, allowedNamespaces)

def getContentFromPage(page, allowedNamespaces = None, username = username):
    if debugLevel > 0: pywikibot.output(u' \03{blue}getContentFromPage : \03{default}' + page.title())
    PageBegin = u''
    try:
        get = page.exists()
    except:
        pywikibot.exceptions.InvalidTitle
        return PageBegin
    if get:
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
                if debugLevel > 0: print u' IsRedirect l 676'
                return 'KO'
            except pywikibot.exceptions.IsRedirectPage:
                if debugLevel > 0: print u' IsRedirect l 679'
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
                if debugLevel > 0: print u' NoPage l 694'
                return 'KO'
            except pywikibot.exceptions.ServerError:
                if debugLevel > 0: print u' NoPage l 697'
                return 'KO'
        else:
            if debugLevel > 0: print u' Forbidden namespace l 700'
            return 'KO'
    else:
        if debugLevel > 0: print u' No page l 703'
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

def getParameter(pageContent, p):
	if pageContent.find(p + u'=') == -1 or pageContent.find(u'}}') == -1 or pageContent.find(p + u'=') > pageContent.find(u'}}'): return u''
	pageContent = pageContent[pageContent.find(p + u'=')+len(p + u'='):]
	if pageContent.find(u'|') != -1 and pageContent.find(u'|') < pageContent.find(u'}}'):
		return trim(pageContent[:pageContent.find(u'|')])
	else:
		return trim(pageContent[:pageContent.find(u'}')])

def addParameter(pageContent, parameter, content = None):
    finalPageContent = u''
    if parameter == u'titre' and content is None:
        # Détermination du titre d'un site web
        URL = getParameter(u'url')
        finalPageContent = pageContent

    else:
        print 'en travaux'
    return finalPageContent

def replaceParameterValue(pageContent, template, parameterKey, oldValue, newValue):
    regex = ur'({{ *(' + template[:1].lower() + ur'|' + template[:1].upper() + ur')' + template[1:] + ur' *\n* *\|[^}]*' + parameterKey + ur' *= *)' + oldValue
    if debugLevel > 0: print regex
    pageContent = re.sub(regex, ur'\1' + newValue, pageContent)

    return pageContent

def replaceTemplate(pageContent, oldTemplate, newTemplate = ''):
    if debugLevel > 0: print u'\nreplaceTemplate : ' + oldTemplate
    regex = ur'({{[ \n]*)' + oldTemplate + ur'([ \n]*[{}\|][^{}]*}}?)'
    if re.search(regex, pageContent):
        if debugLevel > 0: print u' trouvé'
        result = ur''
        if newTemplate != '': result = ur'\1' + newTemplate + ur'\2'
        pageContent = re.sub(regex, result, pageContent)
    return pageContent

def replaceDepretacedTags(pageContent):
    if debugLevel > 0: print u'Remplacements des balises HTML'

    deprecatedTags = {}
    deprecatedTags['big'] = 'strong'
    deprecatedTags['center'] = 'div style="text-align: center;"'
    deprecatedTags['font *color *= *"?'] = 'span style="color:'
    deprecatedTags['font *face *= *"?'] = 'span style="font-family:'
    deprecatedTags['font *\-?size *= *"?\+?\-?'] = 'span style="font-size:'
    deprecatedTags['font *style *= *"?\+?\-?'] = 'span style="'
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

    pageContent = pageContent.replace(u'</br>', u'<br/>')
    pageContent = pageContent.replace(u'<source lang="html4strict">', u'<source lang="html">')

    #TODO: {{citation}} https://fr.wikiversity.org/w/index.php?title=Matrice%2FD%C3%A9terminant&action=historysubmit&type=revision&diff=669911&oldid=664849
    #TODO: multiparamètre
    pageContent = pageContent.replace('<font size="+1" color="red">', ur'<span style="font-size:0.63em; color:red;>')
    regex = ur'<font color="?([^>"]*)"?>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(pageContent):
        if debugLevel > 1: print u'Remplacement de ' + match.group(0) + u' par <span style="color:' + match.group(1) + u'">'
        pageContent = pageContent.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
        pageContent = pageContent.replace('</font>', u'</span>')

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
        #regex = ur'<' + oldTag + ur'([^>]*)>([^\n]*)</' + closingOldTag + '>'
        # bug https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:-flex-nom-fam-/Documentation&diff=prev&oldid=24027702
        regex = ur'< *' + oldTag + ur'([^>]*) *>'
        if re.search(regex, pageContent):
            #summary = summary + u', ajout de ' + newTag
            #pageContent = re.sub(regex, ur'<' + newTag + ur'\1>', pageContent)
            pattern = re.compile(regex, re.UNICODE)
            for match in pattern.finditer(pageContent):
                if debugLevel > 1: print str(match.group(1))
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
                pageContent = pageContent.replace(match.group(0), ur'<' + openingTag + ur'>')

        regex = ur'</ *' + closingOldTag + ' *>'
        pageContent = re.sub(regex, ur'</' + closingNewTag + '>', pageContent)
    pageContent = pageContent.replace('<strong">', ur'<strong>')
    pageContent = pageContent.replace('<s">', ur'<s>')
    pageContent = pageContent.replace('<code">', ur'<code>')
    pageContent = pageContent.replace(';"">', ur';">')

    # Fix
    regex = ur'<span style="font\-size:([a-z]+)>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(pageContent):
        #summary = summary + u', correction de color'
        pageContent = pageContent.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
    pageContent = pageContent.replace('</font>', u'</span>')
    pageContent = pageContent.replace('</font>'.upper(), u'</span>')

    regex = ur'<span style="font\-size:(#[0-9]+)"?>'
    s = re.search(regex, pageContent)
    if s:
        #summary = summary + u', correction de color'
        pageContent = re.sub(regex, ur'<span style="color:' + s.group(1) + ur'">', pageContent)

    regex = ur'<span style="text\-size:([0-9]+)"?>'
    s = re.search(regex, pageContent)
    if s:
        #summary = summary + u', correction de font-size'
        pageContent = re.sub(regex, ur'<span style="font-size:' + str(fontSize[int(s.group(1))]) + ur'em">', pageContent)

    # Fix :
    regex = ur'(<span style="font\-size:[0-9]+px;">)[0-9]+px</span>([^<]*)</strong></strong>'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\1 \2</span>', pageContent)

    pageContent = pageContent.replace(u'<strong><strong><strong><strong><strong><strong>', u'<span style="font-size:75px;">')
    pageContent = pageContent.replace(u'<strong><strong><strong><strong><strong>', u'<span style="font-size:50px;">')
    pageContent = pageContent.replace(u'<strong><strong><strong><strong>', u'<span style="font-size:40px;">')
    pageContent = pageContent.replace(u'<strong><strong><strong>', u'<span style="font-size:25px;">')
    pageContent = pageContent.replace(u'<strong><strong>', u'<span style="font-size:20px;">')
    pageContent = re.sub(ur'</strong></strong></strong></strong></strong></strong>', ur'</span>', pageContent)
    pageContent = re.sub(ur'</strong></strong></strong></strong></strong>', ur'</span>', pageContent)
    pageContent = re.sub(ur'</strong></strong></strong></strong>', ur'</span>', pageContent)
    pageContent = re.sub(ur'</strong></strong></strong>', ur'</span>', pageContent)
    pageContent = re.sub(ur'</strong></strong>', ur'</span>', pageContent)
    regex = ur'<strong>([^<]*)</span>'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'<strong>\1</strong>', pageContent)
    regex = ur'<strong><span ([^<]*)</span></span>'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'<strong><span \1</span></strong>', pageContent)
    #pageContent = re.sub(ur'</span></span>', ur'</span>', pageContent)

    return pageContent

def replaceFilesErrors(pageContent):
    #https://fr.wiktionary.org/wiki/Sp%C3%A9cial:LintErrors/bogus-image-options
    badFileParameters = []
    badFileParameters.append(u'')
    #badFileParameters.append(u'cadre')
    for badFileParameter in badFileParameters:
        regex = ur'(\[\[(Image|Fichier|File) *: *[^\]{]+)\| *' + badFileParameter + ur' *(\||\])'
        if debugLevel > 1: print regex
        pageContent = re.sub(regex, ur'\1\3', pageContent)
    # Doublons
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *thumb *[\|\]])'
    pageContent = re.sub(regex, ur'\1\3', pageContent)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *vignette *[\|\]])'
    pageContent = re.sub(regex, ur'\1\3', pageContent)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *vignette *[\|\]])'
    pageContent = re.sub(regex, ur'\1\3', pageContent)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *thumb *[\|\]])'
    pageContent = re.sub(regex, ur'\1\3', pageContent)
    return pageContent

def replaceDMOZ(pageContent):
    # http://www.dmoz.org => http://dmoztools.net
    URLend = ' \\n\[\]}{<>\|\^`\\"\''
    if pageContent.find('dmoz.org/search?') == -1 and pageContent.find('dmoz.org/license.html') == -1:
        if debugLevel > 1: print regex
        regex = ur'\[http://(www\.)?dmoz\.org/([^' + URLend + ur']*)([^\]]*)\]'
        pageContent = re.sub(regex, ur'[[dmoz:\2|\3]]', pageContent)
        regex =   ur'http://(www\.)?dmoz\.org/([^' + URLend + ur']*)'
        pageContent = re.sub(regex, ur'[[dmoz:\2]]', pageContent)
    return pageContent

def replaceISBN(pageContent):
    #TODO: out of <source> <nowiki> <pre>
    pageContent = pageContent.replace('ISBN&#160;', 'ISBN ')
    regex = ur'\(*ISBN +([0-9Xx\- ]+)\)*( [^0-9Xx\- ])'
    if debugLevel > 1: print regex
    if re.search(regex, pageContent):
        if debugLevel > 0: u'ISBN'
        pageContent = re.sub(regex, ur'{{ISBN|\1}}\2', pageContent)
    regex = ur'\(*ISBN +([0-9Xx\- ]+)\)*'
    if debugLevel > 1: print regex
    if re.search(regex, pageContent):
        if debugLevel > 0: u'ISBN'
        pageContent = re.sub(regex, ur'{{ISBN|\1}}', pageContent)

    #TODO: no hardfix anymore
    regex = ur'{{ISBN *\|([0-9X\- ]+)}}([Xx]?)'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'{{ISBN|\1\2}}', pageContent)
    regex = ur'{{ISBN *\| *(1[03]) *}}'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'ISBN \1', pageContent)

    regex = ur'({{ISBN *\|.*)\-\-}}>'
    if re.search(regex, pageContent):
        pageContent = re.sub(regex, ur'\1}}-->', pageContent)

    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))
    return pageContent

def replaceRFC(pageContent):
    #TODO?
    return pageContent

def searchDoubles(pageContent, parameter):
    if debugLevel > 0: u' Recherche de doublons dans le modèle : ' + parameter[1]
    finalPageContent = u''
    regex = ur'{{' + parameter[1] + ur'[^\n]*{{' + parameter[1]
    while re.search(regex, pageContent):
        #TODO: finalPageContent = pageContent[:], pageContent = pageContent[:]
        print(pageContent[re.search(regex, pageContent).start():re.search(regex, pageContent).end()].encode(config.console_encoding, 'replace'))
    return finalPageContent + pageContent

def log(source):        
    txtfile = codecs.open(u'JackBot.log', 'a', 'utf-8')
    txtfile.write(u'\n' + source + u'\n')
    txtfile.close()

def stopRequired(username = username):
    pageContent = getContentFromPageName(u'User talk:' + username)
    if pageContent == 'KO': return
    if pageContent != u"{{/Stop}}":
        pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
        exit(0)

def savePage(currentPage, pageContent, summary, minorEdit = False):
    result = "ok"
    if debugLevel > 0:
        pywikibot.output(u"\n\03{blue}" + summary + u"\03{default}")
        pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
        if len(pageContent) < 6000:
            print(pageContent.encode(config.console_encoding, 'replace'))
        else:
            taille = 3000
            print(pageContent[:taille].encode(config.console_encoding, 'replace'))
            print u'\n[...]\n'
            print(pageContent[len(pageContent)-taille:].encode(config.console_encoding, 'replace'))
        result = raw_input((u'\nSauvegarder [[' + currentPage.title() + u']] ? (o/n) ').encode('utf-8'))
    if result != "n" and result != "no" and result != "non":
        if currentPage.title().find(u'JackBot/') == -1: stopRequired()
        if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            currentPage.put(pageContent, summary, minorEdit = minorEdit)
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
            time.sleep(100)
            savePage(currentPage, pageContent, summary)
            return
        except pywikibot.exceptions.BadTitle:
            print "BadTitle in savePage"
            return
        except pywikibot.exceptions.OtherPageSaveError:
            # Ex : [[SIMP J013656.5+093347]]
            print "OtherPageSaveError"
            return
        except AttributeError:
            print "AttributeError in savePage"
            return


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

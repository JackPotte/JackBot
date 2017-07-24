#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles de Wikilivres

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators
from pywikibot.data import api

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

checkURL = False # TODO: translate hyperlynx.py by adding content{} at the top
fixTags = False
addCategory = False

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

bookCatTemplates = []
bookCatTemplates.append(u'{{Auto category}}')
bookCatTemplates.append(u'{{Book category}}')
bookCatTemplates.append(u'{{AutoCat}}')
bookCatTemplates.append(u'{{BOOKCAT}}')
bookCatTemplates.append(u'[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
bookCatTemplates.append(u'[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')


def modification(pageName):
    if debugLevel > -1: print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatting'
    page = Page(site, pageName)
    PageBegin = getContentFromPage(page, 'All')
    if PageBegin == 'KO' or pageName.find(u'/Print version') != -1: return
    PageTemp = PageBegin
    PageEnd = u''

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
                summary = summary + u', ajout de ' + newTag
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
        # Templates treatment
        for bookCatTemplate in bookCatTemplates:
            PageTemp = PageTemp.replace(bookCatTemplate, u'{{BookCat}}')
        if addCategory and isPatrolled(page):
            if PageTemp.find(u'{{BookCat}}') == -1 and trim(PageTemp) != '':
                PageTemp = PageTemp + u'\n\n{{BookCat}}'

        regex = ur'\(*ISBN +([0-9\-]+)\)*'
        if re.search(regex, PageTemp):
            if debugLevel > 0: u'ISBN'
            PageTemp = re.sub(regex, ur'{{ISBN|\1}}', PageTemp)
            summary += ', ajout de {{ISBN}}'

    if checkURL: PageTemp = hyperlynx(PageTemp)

    PageEnd = PageEnd + PageTemp
    if PageEnd != PageBegin: sauvegarde(page,PageEnd,summary)


def trim(s):
    return s.strip(" \t\n\r\0\x0B")

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

def isPatrolled(page):
    versions = page.getLatestEditors(1)
    print versions
    #if version['timestamp'] < x and version['user'].patroller:
    #print versions[len(versions)-1]
    #raw_input('Fin')

    return False

def getWiki(language = 'fr', family = 'wiktionary'):
  if debugLevel > 1: print u'get ' + language + u'.' + family
  return pywikibot.Site(language, family)

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

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    if source:
        PagesHS = open(source, 'r')
        while 1:
            pageName = PagesHS.readline()
            fin = pageName.find("\t")
            pageName = pageName[0:fin]
            if pageName == '': break
            if pageName.find(u'[[') != -1:
                pageName = pageName[pageName.find(u'[[')+2:len(pageName)]
            if pageName.find(u']]') != -1:
                pageName = pageName[0:pageName.find(u']]')]
            modification(pageName)
        PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
    modifier = u'False'
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'
    if recursif == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            pages = subcategory.articlesList(False)
            for Page in pagegenerators.PreloadingGenerator(pages,100):
                modification(Page.title())

# Traitement des pages liées
def crawlerLink(pagename,apres):
    modifier = u'False'
    #pagename = unicode(arg[len('-links:'):], 'utf-8')
    page = wikipedia.Page(site, pagename)
    gen = pagegenerators.ReferringPageGenerator(page)
    gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print(Page.title().encode(config.console_encoding, 'replace'))
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
    modifier = u'False'
    cat = catlib.Category(site, pagename)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        page = wikipedia.Page(site, Page.title())
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
    gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
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

def crawlerSpecialNotCategorized():
    global addCategory
    addCategory = True
    for Page in site.uncategorizedpages():
        #print (Page.title().encode(config.console_encoding, 'replace'))
        modification(Page.title())

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
        page = Page(site,u'User talk:' + username)
        if page.exists():
            PageTemp = u''
            try:
                PageTemp = page.get()
            except wikipedia.NoPage: return
            except wikipedia.IsRedirectPage: return
            except wikipedia.LockedPage: return
            except wikipedia.ServerError: return
            except wikipedia.BadTitle: return
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
        result = raw_input("Sauvegarder ? (o/n) ")
    if result != "n" and result != "no" and result != "non":
        if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
        if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            PageCourante.put(Contenu, summary)
        except wikipedia.NoPage: 
            print "NoPage en sauvegarde"
            return
        except wikipedia.IsRedirectPage: 
            print "IsRedirectPage en sauvegarde"
            return
        except wikipedia.LockedPage: 
            print "LockedPage en sauvegarde"
            return
        except pywikibot.EditConflict: 
            print "EditConflict en sauvegarde"
            return
        except wikipedia.ServerError: 
            print "ServerError en sauvegarde"
            return
        except wikipedia.BadTitle: 
            print "BadTitle en sauvegarde"
            return
        except AttributeError:
            print "AttributeError en sauvegarde"
            return

# Lancement
if len(sys.argv) > 1:
    DebutScan = u''
    if len(sys.argv) > 2:
        if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
            debugLevel = 1
        else:
            DebutScan = sys.argv[2]
    if sys.argv[1] == u'test':
        modification(u'Utilisateur:' + username + u'/test')
    elif sys.argv[1] == u'test2':
        modification(u'Utilisateur:' + username + u'/test2')
    elif sys.argv[1] == u'p':
        modification(u'Catégorie:Python')
    elif sys.argv[1] == u'file' or sys.argv[1] == u'txt' or sys.argv[1] == u't':
        crawlerFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
    elif sys.argv[1] == u'u':
        crawlerUser(u'Utilisateur:JackBot')
    elif sys.argv[1] == u'r':
        if len(sys.argv) > 2:
            crawlerSearch(sys.argv[2])
        else:
            crawlerSearch(u'chinois')
    elif sys.argv[1] == u'l':
        crawlerLink(u'Apprendre à programmer avec Python',u'')
    elif sys.argv[1] == u'm':
        crawlerLink(u'Modèle:autres projets',u'')
    elif sys.argv[1] == u'cat':
        crawlerCat(u'Catégorie:Python', False, u'')
    elif sys.argv[1] == u'page':
        modification(u'Utilisateur:JackBot/test unitaire')
    elif sys.argv[1] == u'nocat':
        crawlerSpecialNotCategorized()
    else:
        modification(sys.argv[1])    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
    while 1:
        crawlerRC()

#TODO : getSubPages()
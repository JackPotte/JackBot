#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles de Wikilivres

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

checkURL = False # TODO: translate hyperlynx.py by adding content{} at the top


# Modification du wiki
def modification(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatting'
    page = Page(site, pageName)
    if page.namespace() != 0 or pageName.find(u'/Print version') != -1: return
    try:
        PageBegin = page.get()
    except pywikibot.exception.NoPage:
        print "NoPage"
        return
    except pywikibot.exception.IsRedirectPage:
        print "Redirect page"
        return
    PageTemp = PageBegin
    PageEnd = u''

    # Templates
    bookCatTemplates = []
    bookCatTemplates.append(u'{{Auto category}}')
    bookCatTemplates.append(u'{{Book category}}')
    bookCatTemplates.append(u'{{AutoCat}}')
    bookCatTemplates.append(u'{{BOOKCAT}}')
    bookCatTemplates.append(u'[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
    bookCatTemplates.append(u'[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')
    for bookCatTemplate in bookCatTemplates:
        PageTemp = PageTemp.replace(bookCatTemplate, u'{{BookCat}}')
    if PageTemp.find(u'{{BookCat}}') == -1:
        PageTemp = PageTemp + u'\n\n{{BookCat}}'

    # URLs
    if checkURL:
        PageTemp = hyperlynx(PageTemp)

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

def getWiki(language = 'fr', family = 'wiktionary'):
  if debugLevel > 1: print u'get ' + language + u'.' + family
  return pywikibot.Site(language, family)

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

# Traitement des entrées d'une page spéciale
def crawlerSpecial(pagename):
    gen = pagegenerators.LinksearchPageGenerator(pagename, namespaces=0, total=None, site=site, protocol='http')
    for Page in pagegenerators.PreloadingGenerator(gen, 100):   # pywikibot.data.api.APIError: badquery: Invalid query.
        modification(Page.title())

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
    elif sys.argv[1] == u'special':
        crawlerSpecial(u'Special:UncategorizedPages')
    else:
        modification(sys.argv[1])    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
    while 1:
        crawlerRC()

#TODO : getSubPages()
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

checkURL = False


def modification(PageHS):
    summary = u'Formatage'
    page = Page(site, PageHS)
    print(PageHS.encode(config.console_encoding, 'replace'))
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
    if PageBegin.find(u'{{en travaux') != -1 or PageBegin.find(u'{{En travaux') != -1:
        print u'Page en travaux'
        return
    PageTemp = PageBegin
    PageEnd = u''

    PageTemp = PageTemp.replace(u'<source lang="html4strict">', u'<source lang="html">')
    PageTemp = PageTemp.replace(u'{{Oracle}}\n', u'<noinclude>{{Oracle}}</noinclude>\n')

    # Templates
    oldTemplates = []
    oldTemplates.append(u'lienDePage') # TODO

    regex = ur'({{[a|A]utres projets[^}]*)\|noclear *= *1'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1', PageTemp)
    if debugLevel > 1: raw_input(PageTemp.encode(config.console_encoding, 'replace'))

    if page.namespace() == 0:
        # Traitement des modèles
        regex = ur'\{\{[P|p]ortail([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des portails'
            PageTemp = re.sub(regex, ur'', PageTemp)
        regex = ur'\{\{[P|p]alette([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des palettes'
            PageTemp = re.sub(regex, ur'', PageTemp)
        PageTemp = PageTemp.replace(u'{{PDC}}', u'profondeur de champ')
        PageTemp = PageTemp.replace(u'[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'{{BookCat}}', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'{{reflist}}', u'{{Références}}')
        PageTemp = PageTemp.replace(u'{{Reflist}}', u'{{Références}}')
        
        regex = ur'\(*ISBN +([0-9\-]+)\)*'
        if re.search(regex, PageTemp):
            if debugLevel > 0: u'ISBN'
            PageTemp = re.sub(regex, ur'{{ISBN|\1}}', PageTemp)
            summary += ', ajout de {{ISBN}}'

        # Traitement des hyperliens
        if checkURL: PageTemp = hyperlynx(PageTemp)

        # Clés de tri pour les noms propres
        if PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
            PageTemp = PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie')] + PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
        '''ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
        regex = ur'()\n{{DEFAULTSORT[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'()\n{{defaultsort[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        '''

    PageEnd = PageEnd + PageTemp
    if PageEnd != PageBegin:
        PageTemp = PageTemp.replace(u'<references/>', u'{{Références}}')
        PageTemp = PageTemp.replace(u'<references />', u'{{Références}}')
        sauvegarde(page, PageEnd, summary)


def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def getWiki(language = 'fr', family = 'wiktionary'):
    if debugLevel > 1: print u'get ' + language + u'.' + family
    return pywikibot.Site(language, family)

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

# Traitement d'une catégorie
def crawlerCat(category, recursif, apres):
    modifier = u'False'
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    #gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) HS sur Commons
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
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
def crawlerLink(pagename, apres):
    modifier = u'False'
    #pagename = unicode(arg[len('-links:'):], 'utf-8')
    page = pywikibot.Page(site, pagename)
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
    page = Page(site,u'User talk:' + mynick)
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


# Lancement
if len(sys.argv) > 1:
    DebutScan = u''
    if len(sys.argv) > 2:
        if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
            debugLevel = 1
        else:
            DebutScan = sys.argv[2]
    if sys.argv[1] == u'test':
        modification(u'Utilisateur:' + mynick + u'/test')
    elif sys.argv[1] == u'test2':
        modification(u'Utilisateur:' + mynick + u'/test2')
    elif sys.argv[1] == u'txt':
        crawlerFile(u'scripts/JackBot/articles_' + language + u'_' + family + u'.txt')
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
        crawlerCat(u'Catégorie:Oracle Database (livre)', False, u'')
    elif sys.argv[1] == u'page':
        modification(u'Utilisateur:JackBot/test unitaire')
    elif sys.argv[1] == u'p':
        modification(u'Catégorie:Python')
    else:
        modification(sys.argv[1])    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
    while 1:
        crawlerRC()

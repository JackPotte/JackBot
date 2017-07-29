#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

class PageProvider:
    debugLevel = None
    site = None

    def __init__(self, treatPage, site, debugLevel):
        self.treatPage = treatPage
        self.site = site
        self.debugLevel = debugLevel

    # Lecture du fichier articles_list.txt (au même format que pour replace.py)
    def pagesByFile(self, source, site = None):
        from lib import html2Unicode
        if site is None: site = self.site
        if source:
            pagesList = open(source, 'r')
            while 1:
                pageName = pagesList.readline().decode(config.console_encoding, 'replace')
                fin = pageName.find("\t")
                pageName = pageName[:fin]
                if pageName == '': break
                if pageName.find(u'[[') != -1:
                    pageName = pageName[pageName.find(u'[[')+2:]
                if pageName.find(u']]') != -1:
                    pageName = pageName[:pageName.find(u']]')]
                # Conversion ASCII => Unicode (pour les .txt)
                self.treatPage(html2Unicode(pageName))
            pagesList.close()

    # Lecture du dump
    def pagesByXML(self, source, regex = u'', site = None):
        if site is None: site = self.site
        if self.debugLevel > 1: print u'pagesByXML'
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
                    '''
                    if self.debugLevel > 1: print u' Pluriels non flexion'
                    if entry.title[-2:] == u'es':
                        if self.debugLevel > 1: print entry.title
                        regex = ur"=== {{S\|adjectif\|fr[^}]+}} ===\n[^\n]*\n*{{fr\-rég\|[^\n]+\n*'''" + re.escape(entry.title) + ur"'''[^\n]*\n# *'*'*(Masculin|Féminin)+ *[P|p]luriel de *'*'* *\[\["
                        if re.search(regex, PageTemp):
                            if self.debugLevel > 0: print entry.title
                            #PageTemp = re.sub(regex, ur'\1|flexion\2', PageTemp)
                            #self.treatPage(html2Unicode(entry.title))

                    if self.debugLevel > 1: print u' Ajout de la boite de flexion'
                    if entry.title[-1:] == u's':
                        if (PageTemp.find(u'{{S|adjectif|fr|flexion}}') != -1 or PageTemp.find(u'{{S|nom|fr|flexion}}') != -1) and PageTemp.find(u'{{fr-') == -1:
                            #print entry.title # limite de 8191 lignes dans le terminal.
                            #self.treatPage(entry.title)
                            outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                    '''
                    if self.debugLevel > 1: print u' balises HTML désuètes'
                    for deprecatedTag in deprecatedTags.keys():
                        if PageTemp.find(u'<' + deprecatedTag) != -1:
                            outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

            outPutFile.close()


    # Traitement d'une catégorie
    def pagesByCat(self, category, recursif, afterPage, ns = 0, site = None):
        if site is None: site = self.site
        modifier = u'False'
        print category.encode(config.console_encoding, 'replace')
        cat = catlib.Category(self.site, category)
        pages = cat.articlesList(False)
        gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) # HS sur Commons
        #gen =  pagegenerators.CategorizedPageGenerator(cat)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not afterPage or afterPage == u'' or modifier == u'True':
                self.treatPage(Page.title()) #pagesByLink(Page.title())
            elif Page.title() == afterPage:
                modifier = u'True'
        if recursif:
            subcat = cat.subcategories(recurse = True)
            for subcategory in subcat:
                print subcategory.title().encode(config.console_encoding, 'replace')
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                    self.treatPage(Page.title())

    def pagesByCat2(self, category, recursif, afterPage, site = None):
        if site is None: site = self.site
        modifier = u'False'
        cat = pywikibot.Category(site, category)    # 'module' object has no attribute 'Category'
        gen =  pagegenerators.CategorizedPageGenerator(cat)
        for Page in gen:
            self.treatPage(Page.title())

    # Traitement des pages liées
    def pagesByLink(self, pageName, afterPage, site = None):
        if site is None: site = self.site
        modifier = u'False'
        #pageName = unicode(arg[len('-links:'):], 'utf-8')
        page = pywikibot.Page(site, pageName)
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            print(Page.title().encode(config.console_encoding, 'replace'))
            if not afterPage or afterPage == u'' or modifier == u'True':
                self.treatPage(Page.title()) #pagesByLink(Page.title())
            elif Page.title() == afterPage:
                modifier = u'True'

    # Traitement des pages liées des entrées d'une catégorie
    def pagesByCatLink(self, pageName, afterPage, site = None):
        if site is None: site = self.site
        modifier = u'False'
        cat = catlib.Category(site, pageName)
        pages = cat.articlesList(False)
        for Page in pagegenerators.PreloadingGenerator(pages,100):
            print Page.title().encode(config.console_encoding, 'replace')
            page = pywikibot.Page(site, Page.title())
            gen = pagegenerators.ReferringPageGenerator(page)
            gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
            for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
                if not afterPage or afterPage == u'' or modifier == u'True':
                    self.treatPage(PageLiee.title()) #pagesByLink(Page.title())
                elif PageLiee.title() == afterPage:
                    modifier = u'True'

    def pagesByCatPMID(self, category, site = None):
        if site is None: site = self.site
        cat = catlib.Category(site, category)
        pages = cat.articlesList(False)
        for Page in pagegenerators.PreloadingGenerator(pages,100):
            main = Page.title()
            #main = main[11:len(main)]
            if main.find(u'pmid') != -1:
                self.treatPage(main)

    # Traitement d'une recherche
    def pagesBySearch(self, pageName, ns = None, site = None):
        if site is None: site = self.site
        gen = pagegenerators.SearchPageGenerator(pageName, site = site, namespaces = ns)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            self.treatPage(Page.title())

    # Traitement des self.treatPages récentes
    def pagesByRCLastDay(self, nobots = True, namespace = '0', site = None):
        if site is None: site = self.site
        # Génère les self.treatPages récentes de la dernière journée
        timeAfterLastEdition = 30 # minutes

        date_now = datetime.datetime.utcnow()
        # Date de la plus récente self.treatPage à récupérer
        date_start = date_now - datetime.timedelta(minutes=timeAfterLastEdition)
        # Date d'un jour plus tôt
        date_end = date_start - datetime.timedelta(1)

        start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
        end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

        for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
                        rcdir='older', rctype='edit|new', namespace=namespace,
                        includeredirects=True, repeat=False, user=None,
                        returndict=False, nobots=nobots):
            yield item[0]

    def pagesByRC(self, site = None):
        from lib import timeAfterLastEdition
        if site is None: site = self.site
        gen = pagegenerators.RecentchangesPageGenerator(site = site)
        ecart_minimal_requis = 30 # min
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            #print str(timeAfterLastEdition(Page)) + ' =? ' + str(ecart_minimal_requis)
            if timeAfterLastEdition(Page) > ecart_minimal_requis:
                self.treatPage(Page.title())

    # Traitement des self.treatPages d'un compte
    def pagesByUser(self, username, untilPage, afterPage, regex = None, site = None):
        if site is None: site = self.site
        modifier = u'False'
        compteur = 0
        gen = pagegenerators.UserContributionsGenerator(username, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            if not afterPage or afterPage == u'' or modifier == u'True':
                if regex is None:
                    self.treatPage(Page.title())
                else:
                    PageTemp = getContentFromPageName(Page.title(), allowedNamespaces = 'All')
                    if re.search(regex, PageTemp):
                        print Page.title()
                compteur = compteur + 1
                if compteur > untilPage: break
            elif Page.title() == afterPage:
                modifier = u'True'

    # Toutes les redirections
    def pagesByRedirects(self, site = None):
        if site is None: site = self.site
        for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
            self.treatPage(Page.title())

    # Traitement de toutes les pages du site
    def pagesByAll(self, start, site = None):
        if site is None: site = self.site
        gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            self.treatPage(Page.title())

    def pagesBySpecialNotCategorized(self, site = None):
        if site is None: site = self.site
        global addCategory
        addCategory = True
        for Page in site.uncategorizedpages():
            self.treatPage(Page.title())


    #*** Test methods ***
    def pagesBySpecialLint(self, site = None):
        if site is None: site = self.site
        #TODO
        page = pywikibot.Page(site, u'Spécial:ApiSandbox')
        raw_input(page._get_parsed_page())  # WARNING: API error pagecannotexist: Namespace doesn't allow actual pages.
        #self.treatPage(Page.title())

    def pagesBySpecialLint2(self, site = None):
        if site is None: site = self.site
        predata = { # https://fr.wiktionary.org/wiki/Sp%C3%A9cial:ApiSandbox#action=query&format=rawfm&prop=info&list=linterrors&inprop=url&lntcategories=obsolete-tag&lntlimit=5000&lntnamespace=10
           'action': 'query',
           'format': 'json',
           'prop': 'info',
           'list': 'linterrors',
           'inprop': 'url',
           'lntcategories': 'obsolete-tag',
           'lntlimit': '5000',
           'lntnamespace': '10'
        }
        data = site.postForm(site.apipath(), predata) # WARNING: Http response status 405
        if self.debugLevel > 0: raw_input(data)
        text = simplejson.loads(data)['parse']['text']['*'] # ValueError: No JSON object could be decode
        if self.debugLevel > 0: raw_input(text)
        #self.treatPage(Page.title())

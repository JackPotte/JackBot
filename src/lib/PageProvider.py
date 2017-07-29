#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

class PageProvider:
    site = None
    debugLevel = None
    addCategory = None

    def __init__(self, treatPage, site, debugLevel):
        self.treatPage = treatPage
        self.site = site
        self.debugLevel = debugLevel

    # Lecture du fichier articles_list.txt (au même format que pour replace.py)
    def pagesByFile(self, source):
        if source:
            PagesHS = open(source, 'r')
            while 1:
                pageName = PagesHS.readline().decode(config.console_encoding, 'replace')
                fin = pageName.find("\t")
                pageName = pageName[:fin]
                if pageName == '': break
                if pageName.find(u'[[') != -1:
                    pageName = pageName[pageName.find(u'[[')+2:]
                if pageName.find(u']]') != -1:
                    pageName = pageName[:pageName.find(u']]')]
                # Conversion ASCII => Unicode (pour les .txt)
                self.treatPage(html2Unicode(pageName))
            PagesHS.close()

    # Lecture du dump
    def pagesByXML(self, source, regex = u''):
        if debugLevel > 1: print u'pagesByXML'
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
                    if debugLevel > 1: print u' Pluriels non flexion'
                    if entry.title[-2:] == u'es':
                        if debugLevel > 1: print entry.title
                        regex = ur"=== {{S\|adjectif\|fr[^}]+}} ===\n[^\n]*\n*{{fr\-rég\|[^\n]+\n*'''" + re.escape(entry.title) + ur"'''[^\n]*\n# *'*'*(Masculin|Féminin)+ *[P|p]luriel de *'*'* *\[\["
                        if re.search(regex, PageTemp):
                            if debugLevel > 0: print entry.title
                            #PageTemp = re.sub(regex, ur'\1|flexion\2', PageTemp)
                            #self.treatPage(html2Unicode(entry.title))

                    if debugLevel > 1: print u' Ajout de la boite de flexion'
                    if entry.title[-1:] == u's':
                        if (PageTemp.find(u'{{S|adjectif|fr|flexion}}') != -1 or PageTemp.find(u'{{S|nom|fr|flexion}}') != -1) and PageTemp.find(u'{{fr-') == -1:
                            #print entry.title # limite de 8191 lignes dans le terminal.
                            #self.treatPage(entry.title)
                            outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                    '''
                    if debugLevel > 1: print u' balises HTML désuètes'
                    for deprecatedTag in deprecatedTags.keys():
                        if PageTemp.find(u'<' + deprecatedTag) != -1:
                            outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

            outPutFile.close()


    # Traitement d'une catégorie
    def pagesByCat(self, category, recursif, apres, ns = 0):
        modifier = u'False'
        print category.encode(config.console_encoding, 'replace')
        cat = catlib.Category(self.site, category)
        pages = cat.articlesList(False)
        gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) # HS sur Commons
        #gen =  pagegenerators.CategorizedPageGenerator(cat)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not apres or apres == u'' or modifier == u'True':
                self.treatPage(Page.title()) #pagesByLink(Page.title())
            elif Page.title() == apres:
                modifier = u'True'
        if recursif:
            subcat = cat.subcategories(recurse = True)
            for subcategory in subcat:
                print subcategory.title().encode(config.console_encoding, 'replace')
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                    self.treatPage(Page.title())

    def pagesByCat2(self, category, recursif, apres):
        import pywikibot
        from pywikibot import pagegenerators
        modifier = u'False'
        cat = pywikibot.Category(site, category)    # 'module' object has no attribute 'Category'
        gen =  pagegenerators.CategorizedPageGenerator(cat)
        for Page in gen:
            self.treatPage(Page.title())

    # Traitement des pages liées
    def pagesByLink(self, pageName, apres):
        modifier = u'False'
        #pageName = unicode(arg[len('-links:'):], 'utf-8')
        page = pywikibot.Page(site, pageName)
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            print(Page.title().encode(config.console_encoding, 'replace'))
            if not apres or apres == u'' or modifier == u'True':
                self.treatPage(Page.title()) #pagesByLink(Page.title())
            elif Page.title() == apres:
                modifier = u'True'

    # Traitement des pages liées des entrées d'une catégorie
    def pagesByCatLink(self, pageName, apres):
        modifier = u'False'
        cat = catlib.Category(site, pageName)
        pages = cat.articlesList(False)
        for Page in pagegenerators.PreloadingGenerator(pages,100):
            print Page.title().encode(config.console_encoding, 'replace')
            page = pywikibot.Page(site, Page.title())
            gen = pagegenerators.ReferringPageGenerator(page)
            gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
            for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
                if not apres or apres == u'' or modifier == u'True':
                    self.treatPage(PageLiee.title()) #pagesByLink(Page.title())
                elif PageLiee.title() == apres:
                    modifier = u'True'

    def pagesByCatPMID(self, category):
        cat = catlib.Category(site, category)
        pages = cat.articlesList(False)
        for Page in pagegenerators.PreloadingGenerator(pages,100):
            main = Page.title()
            #main = main[11:len(main)]
            if main.find(u'pmid') != -1:
                self.treatPage(main)

    # Traitement d'une recherche
    def pagesBySearch(self, pageName, ns = None):
        gen = pagegenerators.SearchPageGenerator(pageName, site = site, namespaces = ns)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            self.treatPage(Page.title())

    # Traitement des self.treatPages récentes
    def pagesByRCLastDay(self, site = site, nobots = True, namespace = '0'):
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

    def pagesByRC(self):
        gen = pagegenerators.RecentchangesPageGenerator(site = site)
        ecart_minimal_requis = 30 # min
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            #print str(timeAfterLastEdition(Page)) + ' =? ' + str(ecart_minimal_requis)
            if timeAfterLastEdition(Page) > ecart_minimal_requis:
                self.treatPage(Page.title())

    def timeAfterLastEdition(self, page):
        # Timestamp au format MediaWiki de la dernière version
        time_last_edit = page.getVersionHistory()[0][1]
        match_time = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', time_last_edit)
        # Mise au format "datetime" du timestamp de la dernière version
        datetime_last_edit = datetime.datetime(int(match_time.group(1)), int(match_time.group(2)), int(match_time.group(3)),
            int(match_time.group(4)), int(match_time.group(5)), int(match_time.group(6)))
        datetime_now = datetime.datetime.utcnow()
        diff_last_edit_time = datetime_now - datetime_last_edit

        # Ecart en minutes entre l'horodotage actuelle et l'horodotage de la dernière version
        return diff_last_edit_time.seconds/60 + diff_last_edit_time.days*24*60

    # Traitement des self.treatPages d'un compte
    def pagesByUser(self, username, jusqua, apres, regex = None):
        modifier = u'False'
        compteur = 0
        gen = pagegenerators.UserContributionsGenerator(username, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            if not apres or apres == u'' or modifier == u'True':
                if regex is None:
                    self.treatPage(Page.title())
                else:
                    PageTemp = getContentFromPageName(Page.title(), allowedNamespaces = 'All')
                    if re.search(regex, PageTemp):
                        print Page.title()
                compteur = compteur + 1
                if compteur > jusqua: break
            elif Page.title() == apres:
                modifier = u'True'

    # Toutes les redirections
    def pagesByRedirects(self):
        for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
            self.treatPage(Page.title())

    # Traitement de toutes les pages du site
    def pagesByAll(self, start):
        gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            self.treatPage(Page.title())


    #*** Test methods ***
    def pagesBySpecialLint(self, treatPage):
        #TODO
        page = pywikibot.Page(site, u'Spécial:ApiSandbox')
        raw_input(page._get_parsed_page())  # WARNING: API error pagecannotexist: Namespace doesn't allow actual pages.
        #self.treatPage(Page.title())

    def pagesBySpecialLint2(self, treatPage):
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
        if debugLevel > 0: raw_input(data)
        text = simplejson.loads(data)['parse']['text']['*'] # ValueError: No JSON object could be decode
        if debugLevel > 0: raw_input(text)
        #self.treatPage(Page.title())

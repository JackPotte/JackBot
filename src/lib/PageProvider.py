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
        self.outputFile = open(u'src/lists/articles_' + str(site.lang) + u'_' + str(site.family) + u'.txt', 'a')

    # articles_list.txt may need to be formatted with format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
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

    def pagesByXML(self, source, regex = None, site = None, folder = 'dumps', include = None, exclude = None, titleInclude = None, titleExclude = None, namespaces = None):
        if site is None: site = self.site
        if self.debugLevel > 1: print u'pagesByXML'
        if not source:
            print ' Dump non précisé'
            return
        source = source.replace('wikipedia', 'wiki')
        if source.find('*') != -1:
            fileName = [f for f in os.listdir(folder) if re.match(source, f)]
        if len(fileName) == 0:
            print ' Dump introubable : ' + source
            return
        fileName = fileName[0]
        if self.debugLevel > 0:
            print ' Dump trouvé : ' + fileName
        from pywikibot import xmlreader
        dump = xmlreader.XmlDump(folder + '/' + fileName)
        parser = dump.parse()
        for entry in parser:
            if not namespaces and entry.title.find(u':') == -1:
                pageContent = entry.text
                if titleInclude:
                    if re.search(titleInclude, entry.title):
                        if regex:
                            if re.search(regex, pageContent, re.DOTALL):
                                self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                        elif include and exclude and include in pageContent and not exclude in pageContent:
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                        elif include and include in pageContent:
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                        elif exclude and not exclude in pageContent:
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                        elif not include and not exclude:
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                else:
                    if regex:
                        if re.search(regex, pageContent, re.DOTALL):
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                    elif include and exclude:
                        if include in pageContent and not exclude in pageContent:
                            self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                    else:
                        pass
                        '''
                        if self.debugLevel > 1: print u' Pluriels non flexion'
                        if entry.title[-2:] == u'es':
                            if self.debugLevel > 1: print entry.title
                            regex = ur"=== {{S\|adjectif\|fr[^}]+}} ===\n[^\n]*\n*{{fr\-rég\|[^\n]+\n*'''" + re.escape(entry.title) + ur"'''[^\n]*\n# *'*'*(Masculin|Féminin)+ *[P|p]luriel de *'*'* *\[\["
                            if re.search(regex, pageContent):
                                if self.debugLevel > 0: print entry.title
                                #pageContent = re.sub(regex, ur'\1|flexion\2', pageContent)
                                #self.treatPage(html2Unicode(entry.title))

                        if self.debugLevel > 1: print u' Ajout de la boite de flexion'
                        if entry.title[-1:] == u's':
                            if (pageContent.find(u'{{S|adjectif|fr|flexion}}') != -1 or pageContent.find(u'{{S|nom|fr|flexion}}') != -1) and pageContent.find(u'{{fr-') == -1:
                                #print entry.title # limite de 8191 lignes dans le terminal.
                                #self.treatPage(entry.title)
                                self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

                        if self.debugLevel > 1: print u' balises HTML désuètes'
                        from lib import *
                        for deprecatedTag in deprecatedTags.keys():
                            if pageContent.find(u'<' + deprecatedTag) != -1:
                                self.outputFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))
                        '''
        self.outputFile.close()

    # Traitement des pages d'une catégorie
    def pagesByCat(self, category, recursive = False, afterPage = None, namespaces = [0], names = None, notNames = None,
        notCatNames = None, site = None, pagesList = False, linked = False
    ):
        if site is None: site = self.site
        if self.debugLevel > 0:
            print category.encode(config.console_encoding, 'replace')
        cat = catlib.Category(self.site, category)
        pages = cat.articlesList(False)
        if namespaces == [0]:
            # Filtre bien 0, 2, 12, mais pas 10 ni 100 ni 114, Namespace identifier(s) not recognised
            gen =  pagegenerators.NamespaceFilterPageGenerator(pages, namespaces)
        else:
            gen =  pagegenerators.CategorizedPageGenerator(cat)
        modify = False
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if Page.title() == afterPage:
                modify = True
            elif afterPage is None or afterPage == u'' or modify:
                if linked:
                    gen2 = pagegenerators.ReferringPageGenerator(Page)
                    gen2 =  pagegenerators.NamespaceFilterPageGenerator(gen2, namespaces)
                    for LinkedPage in pagegenerators.PreloadingGenerator(gen2, 100):
                        if pagesList:
                            self.outputFile.write((LinkedPage.title() + '\n').encode(config.console_encoding, 'replace'))
                        else:
                            self.treatPage(LinkedPage.title())
                elif pagesList:
                    self.outputFile.write((Page.title() + '\n').encode(config.console_encoding, 'replace'))
                else:
                    self.treatPageIfName(Page.title(), names, notNames)
        subcat = cat.subcategories(recurse = recursive == True)
        for subcategory in subcat:
            if self.debugLevel > 0: print u' ' + subcategory.title()
            if not namespaces is None and 14 in namespaces:
                self.treatPageIfName(subcategory.title(), names, notNames)
            if recursive:
                modify = True
                if notCatNames is not None:
                    for notCatName in notCatNames:
                        if subcategory.title().find(notCatName) != -1:
                            if self.debugLevel > 0: print u' ' + notCatName + u' ignoré'
                            modify = False
                if modify:
                    pages = subcategory.articlesList(False)
                    for Page in pagegenerators.PreloadingGenerator(pages,100):
                        self.treatPageIfName(Page.title(), names, notNames)

    def treatPageIfName(self, pageName, names = None, notNames = None):
        if names is None and notNames is None:
            self.treatPage(pageName)
        elif names is not None:
            for name in names:
                if self.debugLevel > 1: print u' ' + name + u' trouvé'
                if pageName.find(name) != -1:
                    self.treatPage(pageName)
                    return
        elif notNames is not None:
            for notName in notNames:
                if self.debugLevel > 1: print u' ' + notName + u' ignoré'
                if pageName.find(notName) == -1:
                    self.treatPage(pageName)
                    return
        else:
            for name in names:
                for notName in notNames:
                    if pageName.find(name) != -1 and pageName.find(notName) == -1:
                        self.treatPage(pageName)
                        return

    # [[Special:WhatLinksHere]]
    def pagesByLink(self, pageName, afterPage = None, site = None, namespaces = [0, 10], linked = False, onlyTemplateInclusion = True):
        if site is None: site = self.site
        modify = False
        page = pywikibot.Page(site, pageName)
        gen =  pagegenerators.ReferringPageGenerator(page, onlyTemplateInclusion=True)
        gen = pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not afterPage or afterPage == u'' or modify:
                if linked:
                    gen2 = pagegenerators.ReferringPageGenerator(Page.title(), onlyTemplateInclusion = onlyTemplateInclusion)
                    gen2 =  pagegenerators.NamespaceFilterPageGenerator(gen2, namespaces)
                    for LinkedPage in pagegenerators.PreloadingGenerator(gen2, 100):
                        self.treatPage(LinkedPage.title())
                else:
                    self.treatPage(Page.title())
            elif Page.title() == afterPage:
                modify = True

    # [[Special:Search]]
    def pagesBySearch(self, pageName, namespaces = None, site = None, afterPage = None):
        if site is None: site = self.site
        modify = False
        gen = pagegenerators.SearchPageGenerator(pageName, site = site, namespaces = namespaces)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            if not afterPage or afterPage == u'' or modify:
                self.treatPage(Page.title())
            elif Page.title() == afterPage:
                modify = True

    # [[Special:RecentChanges]]
    def pagesByRC(self, site = None):
        if site is None: site = self.site
        from lib import timeAfterLastEdition
        minimumTime = 30 # min
        gen = pagegenerators.RecentchangesPageGenerator(site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            if self.debugLevel > 1: print str(timeAfterLastEdition(Page)) + ' =? ' + str(minimumTime)
            if timeAfterLastEdition(Page) > minimumTime:
                self.treatPage(Page.title())

    # [[Special:RecentChanges]]
    def pagesByRCLastDay(self, nobots = True, ns = '0', site = None):
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
                        rcdir='older', rctype='edit|new', namespace = ns,
                        includeredirects=True, repeat=False, user=None,
                        returndict=False, nobots=nobots):
            yield item[0]

    # [[Special:Contributions]]: the last pages touched by a user
    def pagesByUser(self, username, numberOfPagesToTreat = None, afterPage = None, regex = None, notRegex = None, site = None):
        if site is None: site = self.site
        modify = False
        numberOfPagesTreated = 0
        gen = pagegenerators.UserContributionsGenerator(username, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
            if not afterPage or afterPage == u'' or modify:
                found = False
                if regex is not None and notRegex is None:
                    if re.search(regex, Page.title()): found = True
                elif regex is None and notRegex is not None:
                    if not re.search(notRegex, Page.title()): found = True
                elif regex is not None and notRegex is not None:
                    if re.search(regex, Page.title()) or not re.search(notRegex, Page.title()): found = True  
                else:
                    found = True

                if found:
                    self.treatPage(Page.title())
                    #self.outputFile.write((Page.title() + '\n').encode(config.console_encoding, 'replace'))
                numberOfPagesTreated += 1
                if numberOfPagesToTreat is not None and numberOfPagesTreated > numberOfPagesToTreat: break
            elif Page.title() == afterPage:
                modify = True

    # [[Special:AllPages]]
    def pagesByAll(self, start = u'', ns = 0, site = None):
        if site is None: site = self.site
        gen = pagegenerators.AllpagesPageGenerator(start, namespace = ns, includeredirects = False, site = site)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            self.treatPage(Page.title())

    # [[Special:ListRedirects]]
    def pagesByRedirects(self, start = u'', site = None):
        if site is None: site = self.site
        for Page in site.allpages(start, namespace = 0, includeredirects = 'only'):
            self.treatPage(Page.title())

    # [[Special:UncategorizedPages]]
    def pagesBySpecialNotCategorized(self, site = None):
        if site is None: site = self.site
        global addCategory
        addCategory = True
        for Page in site.uncategorizedpages():
            self.treatPage(Page.title())

    # [[Special:WantedCategories]]
    def pagesBySpecialWantedCategories(self, site = None):
        if site is None: site = self.site
        for Page in site.wantedcategories():
            self.treatPage(Page.title())

    # [[Special:WantedPages]]
    def pagesBySpecialWantedPages(self, site = None):
        if site is None: site = self.site
        for Page in site.wantedpages():
            self.treatPage(Page.title())

    # [[Special:LinkSearch]]
    def pagesBySpecialLinkSearch(self, url, namespaces = [0], site = None):
        if site is None: site = self.site
        for Page in site.exturlusage(url = url, namespaces = namespaces):
            self.treatPage(Page.title())


    #*** Tested methods ***
    # [[Special:LintErrors]]
    def pagesBySpecialLint(self, site = None):
        #TODO: impossible de parser une page spéciale ainsi (et pywikibot.site.BaseSite.postForm is deprecated)
        if site is None: site = self.site
        page = pywikibot.Page(site, u'Special:ApiSandbox')
        raw_input(page._get_parsed_page())  # WARNING: API error pagecannotexist: Namespace doesn't allow actual pages.
        #self.treatPage(Page.title())

#!/usr/bin/env python
# coding: utf-8

import pywikibot
from pywikibot import *
import creation as c
import html2Unicode
debugLevel= 1


def getFromFile(list, template = None):
    if list:
        fileContent = open(list, 'r')
        while 1:
            fileLine = fileContent.readline()
            fin = fileLine.find("\t")
            fileLine = fileLine[0:fin]
            if fileLine == '': break
            if fileLine.find(u'[[') != -1:
                fileLine = fileLine[fileLine.find(u'[[')+2:]
            if fileLine.find(u']]') != -1:
                fileLine = fileLine[0:PageHS.find(u']]')]
            if template:
                templateFile = open(template, 'r')
                c.creationByTemplate(
                    html2Unicode.html2Unicode(fileLine), 
                    html2Unicode.html2Unicode("".join(templateFile.readlines()))
                )
            else:
                c.creation(html2Unicode.html2Unicode(fileLine))
        fileContent.close()


def getFromCategory(category, recursive, after):
    modifier = u'False'
    cat = catlib.Category(self.site, category)
    pages = cat.articlesList(False)
    gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if not after or after == u'' or modifier == u'True':
            c.creation(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == after:
            modifier = u'True'
    if recursive == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            pages = subcategory.articlesList(False)
            for Page in pagegenerators.PreloadingGenerator(pages,100):
                c.creation(Page.title())


def getLinkedPages(pageName, after):
    modifier = u'False'
    #pagename = unicode(arg[len('-links:'):], 'utf-8')
    page = pywikibot.Page(self.site, pageName)
    gen = pagegenerators.ReferringPageGenerator(page)
    gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if debugLevel > 0: print(Page.title().encode(config.console_encoding, 'replace'))
        if not after or after == u'' or modifier == u'True':
            c.creation(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == after:
            modifier = u'True'


def getFromCategoryPagesLinkedPages(pageName, after):
    modifier = u'False'
    cat = catlib.Category(self.site, pageName)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        page = Page(self.site, Page.title())
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for linkedPage in pagegenerators.PreloadingGenerator(gen,100):
            if debugLevel > 0: print(Page.title().encode(config.console_encoding, 'replace'))
            if not after or after == u'' or modifier == u'True':
                c.creation(linkedPage.title()) #crawlerLink(Page.title())
            elif linkedPage.title() == after:
                modifier = u'True'


def getFromSearchEngine(pageName):
    gen = pagegenerators.SearchPageGenerator(pageName, site = self.site, namespaces = '0')
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        c.creation(Page.title())


def lastEditTime(page):
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


def getFromRecentChanges():
    gen = pagegenerators.RecentchangesPageGenerator(site = self.site)
    ecart_minimal_requis = 30 # min
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if debugLevel > 0: print str(lastEditTime(Page)) + ' =? ' + str(ecart_minimal_requis)
        if lastEditTime(Page) > ecart_minimal_requis:
            c.creation(Page.title())


def getFromLastDayRecentChanges(site, nobots=True, namespace='0'):
    # Génère les modifications récentes de la dernière journée
    lastEditTime = 30 # minutes

    date_now = datetime.datetime.utcnow()
    # Date de la plus récente modification à récupérer
    date_start = date_now - datetime.timedelta(minutes=lastEditTime)
    # Date d'un jour plus tôt
    date_end = date_start - datetime.timedelta(1)

    start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
    end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

    for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
                    rcdir='older', rctype='edit|new', namespace=namespace,
                    includeredirects=True, repeat=False, user=None,
                    returndict=False, nobots=nobots):
        yield item[0]


def getFromUserLastEditions(userName = u'JackBot', until = 0):
    compteur = 0
    gen = pagegenerators.UserContributionsGenerator(userName)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        c.creation(Page.title())
        compteur = compteur + 1
        if compteur > until: break


def getFromAllRedirects(self):
    for Page in self.site.allpages(start=u'', namespace=0, includeredirects='only'):
        if debugLevel > 0: print Page.title()
        c.creation(Page.title())


def getAll(start):
    gen = pagegenerators.AllpagesPageGenerator(start, namespace=0, includeredirects=False)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        if debugLevel > 0: print (Page.title().encode(config.console_encoding, 'replace'))
        c.creation(Page.title())


def getFlexionsFromSite(site):
    if debugLevel > 0: print 'todo'
    return


def getFlexionsFromCategory(category):
    if debugLevel > 0: print 'todo'
    return

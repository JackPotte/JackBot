#!/usr/bin/env python
# coding: utf-8
# This script formats the Wikibooks pages

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators
from pywikibot.data import api

# Global variables
debugLevel = 0
debugAliases = ['-debug', '-d']
for debugAlias in debugAliases:
    if debugAlias in sys.argv:
        debugLevel= 1
        sys.argv.remove(debugAlias)

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
fixFiles = True
addCategory = False

bookCatTemplates = []
bookCatTemplates.append(u'{{Auto category}}')
bookCatTemplates.append(u'{{Book category}}')
bookCatTemplates.append(u'{{AutoCat}}')
bookCatTemplates.append(u'{{Bookcat}}')
bookCatTemplates.append(u'{{BOOKCAT}}')
bookCatTemplates.append(u'[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
bookCatTemplates.append(u'[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')
bookCatTemplates.append(u'[[Category:{{FULLBOOKNAME}}|{{FULLCHAPTERNAME}}]]')
bookCatTemplates.append(u'[[Category:{{PAGENAME}}]]')
bookCatTemplates.append(u'[[Category:{{BASEPAGENAME}}]]')
bookCatTemplates.append(u'[[Category:{{FULLBOOKNAME}}]]')


def treatPageByName(pageName):
    if debugLevel > -1: print(pageName.encode(config.console_encoding, 'replace'))
    page = Page(site, pageName)
    PageBegin = getContentFromPage(page, 'All')
    if not username in pageName and (PageBegin == 'KO' or pageName.find(u'/Print version') != -1): return
    summary = u'Formatting'
    PageTemp = PageBegin
    PageEnd = u''

    PageTemp = globalOperations(PageTemp)
    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
    if checkURL: PageTemp = hyperlynx(PageTemp)

    if debugLevel > 1: print 'Templates treatment'
    regex = ur'{{[Tt]alk *archive([^}]*)}}='
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'{{Talk archive\1}}\n=', PageTemp)
    regex = ur'{{[Tt]alk *header([^}]*)}}='
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'{{Talk header\1}}\n=', PageTemp)

    if username in pageName or page.namespace() == 0:
        for bookCatTemplate in bookCatTemplates:
            PageTemp = PageTemp.replace(bookCatTemplate, u'{{BookCat}}')
            PageTemp = PageTemp.replace(bookCatTemplate[:2] + bookCatTemplate[2:3].lower() + bookCatTemplate[3:], u'{{BookCat}}')
        if addCategory and hasMoreThanTime(page) and isTrustedVersion(page):
            # The untrusted can have blanked a relevant content including {{BookCat}}
            if trim(PageTemp) != '' and PageTemp.find(u'[[Category:') == -1 and PageTemp.find(u'{{BookCat}}') == -1 and PageTemp.find(u'{{printable') == -1:
                PageTemp = PageTemp + u'\n\n{{BookCat}}'
                summary = summary + u', {{BookCat}}'
        # Fix
        regex = ur'\[\[{{BookCat}}(\n|$)'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'{{BookCat}}\1', PageTemp)
            summary = summary + u', {{BookCat}} correction'

    PageEnd = PageEnd + PageTemp
    if PageEnd != PageBegin: savePage(page, PageEnd, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'-test2':
            treatPageByName(u'User:' + username + u'/test2')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            treatPageByName(u'Python')
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.pagesByXML(siteLanguage + siteFamily + '.*xml', regex)
        elif sys.argv[1] == u'-u':
            user = username
            if len(sys.argv) > 2: user = sys.argv[2]
            p.pagesByUser(u'User:' + user, numberOfPagesToTreat = 10000)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            research = u'insource:"Quantum theory of observation/ "'
            if len(sys.argv) > 2: research = sys.argv[2]
            p.pagesBySearch(research)
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Category:Side Dish recipes', namespaces = None)
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat':
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Rebol programming')
            #p.pagesByCat(u'Category:Pages using ISBN magic links', namespaces = None, afterPage = afterPage)
            #p.pagesByCat(u'Category:Pages with ISBN errors', namespaces = None, afterPage = afterPage)
        elif sys.argv[1] == u'-redirects':
            p.pagesByRedirects()
        elif sys.argv[1] == u'-all':
           p.pagesByAll()
        elif sys.argv[1] == u'-RC':
            while 1:
                p.pagesByRCLastDay()
        elif sys.argv[1] == u'-nocat':
            global addCategory
            addCategory = True
            p.pagesBySpecialNotCategorized()
        elif sys.argv[1] == u'-lint':
            p.pagesBySpecialLint()
        elif sys.argv[1] == u'-extlinks':
            p. pagesBySpecialLinkSearch('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        while 1:
            p.pagesByRC()

if __name__ == "__main__":
    main(sys.argv)

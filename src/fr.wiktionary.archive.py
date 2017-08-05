#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script archive des pages de discussion
 
# Importation des modules
from __future__ import absolute_import, unicode_literals
import catlib, datetime, locale, os, re, sys, time
from lib import *
import pywikibot
from pywikibot import *

# Global variables
debugLevel = 0
debugAliases = ['debug', 'd', '-d']
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

summary = u'Autoarchivage de [[Wiktionnaire:Bot/Requêtes]]'

# Modification du wiki
def treatPageByName(pageName):
	page = Page(site, pageName)
	if page.exists():
		if page.namespace() != 4 and page.title() != u'User:JackBot/test': 
			return
		else:
			try:
				PageTemp = page.get()
			except pywikibot.exceptions.NoPage:
				print "NoPage"
				return
			except pywikibot.exceptions.IsRedirectPage:
				print "Redirect page l 42"
				PageTemp = page.get(get_redirect=True)
				page2 = Page(site, PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')])
				try:
					PageEnd2 = page2.get()
				except pywikibot.exceptions.NoPage:
					print "NoPage"
					return
				except pywikibot.exceptions.IsRedirectPage:
					print "Redirect page l 51"
					return
				except pywikibot.exceptions.LockedPage:
					print "Locked/protected page"
					return
				if PageEnd2.find(u'{{NavigBOT') == -1:
					PageEnd2 = u'{{NavigBOT|' + page2.title()[len(page2.title())-4:len(page2.title())] + u'}}\n' + PageEnd2
					savePage(page2,PageEnd2,summary)
				return
			except pywikibot.exceptions.LockedPage:
				print "Locked/protected page"
				return
	else:
		return
	
	PageEnd = ''
	annee = time.strftime('%Y')
	regex = u'\n==[ ]*{{[rR]equête [fait|refus|refusée|sans suite]+}}.*==[ \t]*\n'
	while re.compile(regex).search(PageTemp):
		DebutParagraphe = re.search(regex,PageTemp).end()
		if re.search(ur'\n==[^=]',PageTemp[DebutParagraphe:]):
			FinParagraphe = re.search(ur'\n==[^=]',PageTemp[DebutParagraphe:]).start()
		else:
			FinParagraphe = len(PageTemp[DebutParagraphe:])
		if debugLevel > 0:
			raw_input(PageTemp[DebutParagraphe:][:FinParagraphe].encode(config.console_encoding, 'replace'))
			print u'-------------------------------------'
		if PageTemp[DebutParagraphe:].find('\n==') == -1:
			# Dernier paragraphe
			PageEnd = PageEnd + PageTemp[:DebutParagraphe][PageTemp[:DebutParagraphe].rfind('\n=='):] + PageTemp[DebutParagraphe:]
			PageTemp = PageTemp[:DebutParagraphe][:PageTemp[:DebutParagraphe].rfind('\n==')]
		else:
			PageEnd = PageEnd + PageTemp[:DebutParagraphe][PageTemp[:DebutParagraphe].rfind('\n=='):] + PageTemp[DebutParagraphe:][:FinParagraphe]
			PageTemp = PageTemp[:DebutParagraphe][:PageTemp[:DebutParagraphe].rfind('\n==')] + PageTemp[DebutParagraphe:][FinParagraphe:]
			
			
	# Sauvegardes
	if PageTemp != page.get():
		page2 = Page(site,pageName + u'/Archives/' + annee)
		PageEnd2 = u''
		if page2.exists():
			try:
				PageEnd2 = page2.get()
			except pywikibot.exceptions.NoPage:
				print "NoPage"
				return
			except pywikibot.exceptions.IsRedirectPage:
				print "Redirect page"
				return
			except pywikibot.exceptions.LockedPage:
				print "Locked/protected page"
				return		
		if PageEnd2.find(u'{{NavigBOT') == -1: PageEnd2 = u'{{NavigBOT|' + page2.title()[len(page2.title())-4:len(page2.title())] + u'}}\n' + PageEnd2
		savePage(page2,PageEnd2 + PageEnd,summary)
		savePage(page,PageTemp,summary)

treatPageByName(u'Wiktionnaire:Bots/Requêtes')

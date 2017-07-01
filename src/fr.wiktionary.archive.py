#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script archive des pages de discussion
 
# Importation des modules
from __future__ import absolute_import, unicode_literals
import catlib, datetime, locale, os, re, sys, time
import pywikibot
from pywikibot import *

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

summary = u'Autoarchivage de [[Wiktionnaire:Bot/Requêtes]]'

# Modification du wiki
def modification(PageHS):
	page = Page(site, PageHS)
	if page.exists():
		if page.namespace()!=4 and page.title() != u'Utilisateur:JackBot/test': 
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
				page2 = Page(site,PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')])
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
					sauvegarde(page2,PageEnd2,summary)
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
		page2 = Page(site,PageHS + u'/Archives/' + annee)
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
		sauvegarde(page2,PageEnd2 + PageEnd,summary)
		sauvegarde(page,PageTemp,summary)
	
				
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		modification(Page.title()) #crawlerLink(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())
	'''
	subcat = cat.subcategories() #recurse = True)
	for subcategory in subcat:
		
		# HS
		if subcategory == u'[[Catégorie:Mammifère disparu]]':
			raw_input("oui")
		else:
			raw_input("non")
		
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			#if not crawlerFile(Page.title()):
			modification(Page.title())'''

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = pywikibot.exceptions.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Blacklist (en cours de test)
def crawlerFile(PageCourante):
    PagesHS = open(u'BL.txt', 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': 
			break
		elif PageHS == PageCourante: 
			return "False"
    PagesHS.close()
	
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,10000):
		modification(Page.title())
		
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		modification(PageHS)
    PagesHS.close()
	
def DatePlusMois(months):
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

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
	page = Page(site,u'User talk:' + username)
	if page.exists():
		PageTemp = u''
		try:
			PageTemp = page.get()
		except pywikibot.exceptions.NoPage: return
		except pywikibot.exceptions.IsRedirectPage: return
		except pywikibot.exceptions.ServerError: return
		except pywikibot.exceptions.BadTitle: return
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

modification(u'Wiktionnaire:Bots/Requêtes')


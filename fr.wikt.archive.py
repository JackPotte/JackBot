#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script archive des pages de discussion
 
# Importation des modules
from wikipedia import *
import os, sys, catlib, pagegenerators, time, datetime, locale, re

# Déclaration
debogage = True
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Autoarchivage de [[Wiktionnaire:Bot/Requêtes]]'
#locale.setlocale(locale.LC_ALL,'fr')

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!=4 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				PageTemp = page.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				PageTemp = page.get(get_redirect=True)
				page2 = Page(site,PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')])
				try:
					PageEnd2 = page2.get()
				except wikipedia.NoPage:
					print "NoPage"
					return
				except wikipedia.IsRedirectPage:
					print "Redirect page"
					return
				except wikipedia.LockedPage:
					print "Locked/protected page"
					return
				if PageEnd2.find(u'{{NavigBOT') == -1:
					PageEnd2 = u'{{NavigBOT|' + page2.title()[len(page2.title())-4:len(page2.title())] + u'}}\n' + PageEnd2
					sauvegarde(page2,PageEnd2,summary)
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return
	else:
		return
	
	PageEnd = ""
	annee = time.strftime('%Y')
	regex = u'\n==[ ]*{{[rR]equête [fait|refus|refusée|sans suite]+}}.*==[ \t]*\n'
	while re.compile(regex).search(PageTemp):
		i1 = re.search(regex,PageTemp).end()
		#raw_input (PageTemp[:i1].encode(config.console_encoding, 'replace'))	# Début avec titre inclu
		#raw_input (PageTemp[i1:].encode(config.console_encoding, 'replace'))	# Fin avec titre exclu
		# Si c'est le dernier paragraphe
		if PageTemp[i1:].find('\n==') == -1:
			PageEnd = PageEnd + PageTemp[:i1][PageTemp[:i1].rfind('\n=='):len(PageTemp[:i1])] + PageTemp[i1:]
			PageTemp = PageTemp[:i1][:PageTemp[:i1].rfind('\n==')]
		else:
			PageEnd = PageEnd + PageTemp[:i1][PageTemp[:i1].rfind('\n=='):len(PageTemp[:i1])] + PageTemp[i1:][:PageTemp[i1:].find('\n==')]
			PageTemp = PageTemp[:i1][:PageTemp[:i1].rfind('\n==')] + PageTemp[i1:][PageTemp[i1:].find('\n=='):len(PageTemp[i1:])]
			
	# Sauvegardes
	if PageTemp != page.get():
		page2 = Page(site,PageHS + u'/Archives/' + annee)
		PageEnd2 = u''
		if page2.exists():
			try:
				PageEnd2 = page2.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
			except wikipedia.LockedPage:
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
	page = wikipedia.Page(site, pagename)
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
	page = Page(site,u'User talk:' + mynick)
	if page.exists():
		PageTemp = u''
		try:
			PageTemp = page.get()
		except wikipedia.NoPage: return
		except wikipedia.IsRedirectPage: return
		except wikipedia.ServerError: return
		except wikipedia.BadTitle: return
		if PageTemp != u"{{/Stop}}":
			pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
			exit(0)
	
def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage:
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
modification(u'Wiktionnaire:Bot/Requêtes')
'''
TraitementFile = crawlerFile('articles_list.txt')
TraitementPage = modification(u'Wikipédia:Bot/Requêtes/' + time.strftime(u'%Y/%m'))
TraitementLiens = crawlerLink(u'Modèle:mois')
TraitementSearch = crawlerSearch(u'reference')
TraitementCategory = crawlerCat(u'')

à faire : prévoir les autres paragraphes que ==
'''

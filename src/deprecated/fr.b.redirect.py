#!/usr/bin/env python
# coding: utf-8
# Ce script important masse

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wikibooks"
site = getSite(language,family)
summary = u'[[Wikilivres:Le Bistro/Messages actuels]] : redirection des ingrédients'

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.namespace() != 0: return
	try:
		PageTemp = page.get()
	except wikipedia.NoPage:
		print "NoPage"
		return
	except wikipedia.IsRedirectPage:
		print "Redirect page"
		return
	while PageTemp.find(u'[[Livre de cuisine/Ingrédients/') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'[[Livre de cuisine/Ingrédients/')+2] + u'w:' + PageTemp[PageTemp.find(u'[[Livre de cuisine/Ingrédients/')+len(u'[[Livre de cuisine/Ingrédients/'):len(PageTemp)]
	if PageTemp != page.get():
		try:
			#print (PageEnd.encode(config.console_encoding, 'replace'))
			#raw_input("fin")
			page.put(PageTemp, summary)
		except pywikibot.EditConflict:
			print "Conflict"
			return
		except wikipedia.NoPage:
			print "NoPage"
			return
		except wikipedia.IsRedirectPage:
			print "Redirect page"
			return
		except wikipedia.LockedPage:
			print "Locked/protected page"
			return	
		
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		modification(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lancement
TraitementCategory = crawlerCat(u'Catégorie:Cuisine')
'''
TraitementRedirections = crawlerRedirects()
while 1:
	TraitementRC = crawlerRC()
'''

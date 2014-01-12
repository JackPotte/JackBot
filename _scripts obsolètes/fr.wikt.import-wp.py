#!/usr/bin/env python
# coding: utf-8
# Ce script crée les pages des comtés d’Angleterre depuis la liste de Wikipédia mise préalablement dans un fichier texte (voire directement de la catégorie s’il n’y a rien à filtrer)
# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = u'JackBot'
language1 = u'fr'
family = u'wiktionary'
site1 = getSite(language1,family)
family2 = u'wikipedia'
site2 = getSite(language1,family2)
pays = u'Angleterre'
toponyme = u'Comté'
PageEnd = u'== {{=fr=}} ==\n{{-étym-}}\n{{ébauche-étym|fr}}\n\n{{-nom-pr-|fr}}\n{{fr-inv|}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||fr}} {{genre|fr}} {{invar}}\n# ' + toponyme + u' d\'[[' + pays + u']].\n\n{{-holo-}}\n* [[' + pays + u']]\n\n{{-trad-}}\n{{ébauche-trad}}\n\n[[Catégorie:' + toponyme + u's d’' + pays + u' en français]]\n'

# Modification du wiki
def modification(Page1):
	page1 = Page(site1,Page1)
	if not page1.exists():
		summary = u'Création depuis [[w:' + Page1 + u']]'	
		page1.put(PageEnd, summary)

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			modification(PageHS)
		PagesHS.close()
		
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

def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site2, u'Template:' + pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
	'''
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site2, u'Template:' + pagename)
	links = page.linkedPages()
	print links
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in links:
		print(Page.title())	
		modification(Page.title())
	'''
	
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lancement
TraitementFile = crawlerFile('articles_list.txt')
'''
TraitementCategory = crawlerCat(u'')
TraitementLiens = crawlerLink(template)
while 1:
	TraitementRC = crawlerRC()
'''

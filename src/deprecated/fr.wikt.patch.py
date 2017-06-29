#!/usr/bin/env python
# coding: utf-8
# Ce script important masse

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
summary = u'Remplacement de -prov- par -loc-phr-'

# Modification du wiki
def modification(PageHS):
	if PageHS.find(u' ') == -1: return
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() !=0 and page.title() != u'Utilisateur:JackBot/test': return
	else: return
	try: PageTemp = page.get()
	except wikipedia.NoPage: return
	except wikipedia.InvalidPage: return
	except wikipedia.ServerError: return
	while PageTemp.find(u'-prov-') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'-prov-')] + u'-loc-phr-' + PageTemp[PageTemp.find(u'-prov-')+len(u'-prov-'):len(PageTemp)]
	if PageTemp != page.get():
		arretdurgence()
		try:
			#print (PageTemp.encode(config.console_encoding, 'replace'))
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

# Permet à tout le monde de stopper le bot en lui écrivant
def arretdurgence():
        arrettitle = ''.join(u"Discussion utilisateur:JackBot")
        arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
        gen = iter([arretpage])
        arret = arretpage.get()
        if arret != u"{{/Stop}}":
                pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
                exit(0)

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

# Traitement des sous-catégories
def crawlerCatCat(category):
	modification(category.title())
	cat = catlib.Category(site, category)
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		modification(subcategory.title())

# Traitement des pages liées
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
	
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lancement
TraitementLiens = crawlerLink(u'Modèle:-prov-')
'''
TraitementCategory = crawlerCat(u'Villes')
TraitementFile = crawlerFile('articles_list.txt')
while 1:
	TraitementRC = crawlerRC()
'''

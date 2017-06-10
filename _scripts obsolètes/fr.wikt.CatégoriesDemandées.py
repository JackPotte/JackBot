#!/usr/bin/env python
# coding: utf-8
# Ce script créé certaines catégories les plus demandées depuis un fichier

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
output = u'articles_listed.txt'

# Traitement d'une catégorie
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists(): return
	langue1 = PageHS[len(u'Cat&#233;gorie:Mots en '):PageHS.find(u' issus')]
	langue2 = PageHS[PageHS.rfind(u'mot en ')+len(u'mot en '):len(PageHS)]
	page2 = Page(site,u'Catégorie:Mots ' + langue1 + u'issus d’un mot ' + langue2)
	if not page2.exists(): page2 = Page(site,u'Catégorie:Mots ' + langue1 + u's issus d’un mot ' + langue2)
	if not page2.exists(): page2 = Page(site,u'Catégorie:Mots ' + langue1 + u'x issus d’un mot ' + langue2)
	if not page2.exists():
		PageEnd = u'{{CatégorieTDM}}\n[[Catégorie:Origines étymologiques des mots en '+ langue1 + u'|' + langue2 + u']]\n[[Catégorie:Mots issus d’un mot en ' + langue2 + u'|' + langue1 +u']]\n'
		page.put(PageEnd, u'[[Wiktionnaire:Prise de décision/Modèles de codes de langue]]')
		return
	try:
		PageTemp = page2.get()
	except wikipedia.NoPage:
		print "NoPage"
		return
	except wikipedia.IsRedirectPage:
		print "Redirect page"
		print PageHS
		return
	except wikipedia.LockedPage:
		print "Locked/protected page"
		return
	#while PageTemp.find(u'|type=cat') != 0:
	#	PageTemp = PageTemp[0:PageTemp.find(u'|type=cat')] + PageTemp[PageTemp.find(u'|type=cat')+len(u'|type=cat'):len(PageTemp)]
	#while PageTemp.find(u'|type=fs') != 0:
	#	PageTemp = PageTemp[0:PageTemp.find(u'|type=fs')] + PageTemp[PageTemp.find(u'|type=fs')+len(u'|type=fs'):len(PageTemp)]
	page.put(PageTemp, u'[[Wiktionnaire:Prise de décision/Modèles de codes de langue]]')

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
		modification(Page.title()) #crawlerLink(Page.title())
	subcat = cat.subcategories(recurse = True)
	#modification(subcat.title())
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())
		
# Traitement des pages liées
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())


# Lancement
TraitementFile = crawlerFile('articles_list.txt')
'''
TraitementCategory = crawlerCat(u'Catégorie:Origines étymologiques des mots')

TraitementLiens = crawlerLink(u'Modèle:fr-rég')
TraitementWord = modification(u'Utilisateur:JackBot/test')
TraitementCategory = crawlerCat(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementRecherche = crawlerSearch(u'chinois')
while 1:
	TraitementRC = crawlerRC()

python movepages.py -pairs:"articles_listed.txt" -noredirect -lang:fr -family:wiktionary
'''

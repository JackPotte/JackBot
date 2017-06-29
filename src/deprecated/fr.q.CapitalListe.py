#!/usr/bin/env python
# coding: utf-8
# Ce script calcule le nombre d'article et de citation de Wikiquote, en tenant compte des doublons

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re
from wikipedia import *

# Déclaration
language = "fr"
family = "wikiquote"
mynick = "JackBot"
site = getSite(language,family)
output = u'Wikiquote.txt'
template = u'Citation'
template2 = u'citation'

def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists() and page.namespace() ==0:
		try:
			PageTemp = page.get()
		except wikipedia.NoPage:
			print "NoPage"
			return
		except wikipedia.IsRedirectPage:
			print "Redirect page"
			return
		except wikipedia.LockedPage:
			print "Locked/protected page"
			return
	else:
		return
	# On resense toutes les citations une par une pour chaque page
	txtfile = codecs.open(output, 'a', 'utf-8')
	while PageTemp.find(u'{{' + template + u'|') != -1 or PageTemp.find(u'{{' + template2 + u'|') != -1:
		if PageTemp.find(u'{{' + template + u'|') < PageTemp.find(u'{{' + template2 + u'|') and PageTemp.find(u'{{' + template + u'|') != -1:
			PageTemp = PageTemp[PageTemp.find(u'{{' + template + u'|')+len(u'{{' + template + u'|'):len(PageTemp)]
		else:
			PageTemp = PageTemp[PageTemp.find(u'{{' + template2 + u'|')+len(u'{{' + template2 + u'|'):len(PageTemp)]
		
		if PageTemp.find(u'|') < PageTemp.find(u'}}') and PageTemp.find(u'|') != -1:
			if PageTemp.find(u'citation=') < PageTemp.find(u'|') and PageTemp.find(u'citation=') != -1:
				txtfile.write(PageTemp[PageTemp.find(u'citation=')+len(u'citation='):PageTemp.find(u'|')] + u'\n')
			else:
				txtfile.write(PageTemp[0:PageTemp.find(u'|')] + u'\n')
		else:
			txtfile.write(PageTemp[0:PageTemp.find(u'}}')] + u'\n')
	txtfile.close()


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
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "1")
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
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

# Lancement
TraitementLiens = crawlerLink(u'Modèle:Citation')
'''
TraitementUtilisateur = crawlerUser(u'Utilisateur:BeBot')
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementFile = crawlerFile('articles_list.txt')
TraitementCategorie = crawlerCat(u'Écosse')
TraitementRecherche = crawlerSearch(u'Écosse')
while 1:
     TraitementRC = crawlerRC()
'''

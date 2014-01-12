#!/usr/bin/env python
# coding: utf-8

# Ce script liste des pages dans un fichier (avant éventuel renommage avec movingpages.py)

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wikiversity"
mynick = "JackBot"
site = getSite(language,family)
outputFile = u'articles_listed.txt'
outputPage = u'Utilisateur:JackBot/Page sans modèle de titre'
summary = u'Mise à jour des pages à formater'

# Traitement d'une catégorie
def modification(PageHS):
	page = Page(site,PageHS)
	PageTemp = u''
	if page.namespace() != 0: 
		return
	elif page.exists():
		try: PageTemp = page.get()
		except wikipedia.NoPage: return
		except wikipedia.IsRedirectPage: return
		except wikipedia.ServerError: return
		if PageTemp.find(u'{{faculté') == -1 and PageTemp.find(u'{{département') == -1 and PageTemp.find(u'{{leçon') == -1 and PageTemp.find(u'{{chapitre') == -1 and PageTemp.find(u'{{exercice') == -1 and PageTemp.find(u'{{annexe') == -1 and PageTemp.find(u'{{cours') == -1 and PageTemp.find(u'{{entête de fiche') == -1 and PageTemp.find(u'{{travail pratique') == -1 and (
		PageTemp.find(u'{{Faculté') == -1) and PageTemp.find(u'{{Département') == -1 and PageTemp.find(u'{{Leçon') == -1 and PageTemp.find(u'{{Chapitre') == -1 and PageTemp.find(u'{{Exercice') == -1 and PageTemp.find(u'{{Annexe') == -1 and PageTemp.find(u'{{Cours') == -1 and PageTemp.find(u'{{Entête de fiche') == -1 and PageTemp.find(u'{{Travail pratique') == -1  and (
		PageTemp.find(u'{{Transféré sur Wikibooks') == -1) and PageTemp.find(u'{{Redirect Wikilivres') == -1 and PageTemp.find(u'{{Projets collaboratifs') == -1 and PageTemp.find(u'{{Ressources') == -1 and (
		PageHS[len(PageHS)-len(u'Présentation de la leçon'):len(PageHS)] != u'Présentation de la leçon') and PageHS[len(PageHS)-len(u'Objectifs'):len(PageHS)] != u'Objectifs' and PageHS[len(PageHS)-len(u'Prérequis conseillés'):len(PageHS)] != u'Prérequis conseillés' and PageHS[len(PageHS)-len(u'Référents'):len(PageHS)] != u'Référents':
			# {{à wikifier}}
			txtfile = codecs.open(outputFile, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']]\n')
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

# Traitement d'une moyenne des tailles de page d'une catégorie
def crawlerSCat(category):
	somme = 0
	nbpage = 0
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		PageTemp = Page.title()
		print PageTemp.encode(config.console_encoding, 'replace')
		somme = somme + long(str(modification(PageTemp[PageTemp.find(u':')+1:len(PageTemp)]))) # ValueError: invalid literal for long() with base 10: 'None'
		nbpage = nbpage + 1
	#subcat = cat.subcategories(recurse = True)
	#for subcategory in subcat:
	#	pages = subcategory.articlesList(False)
	#	for Page in pagegenerators.PreloadingGenerator(pages,100):
	#		somme = somme + int(str(modification(Page.title())))
	#		nbpage = nbpage + 1
	return (somme / nbpage)

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

# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())
		
# Lancement 
TraitementAll = crawlerAll(u'')
page = Page(site,outputPage)
page.put(txtfile.read(), summary)									
'''
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementLiens = crawlerLink(u'Modèle:Wikiprojet Athlétisme')
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementFile = crawlerFile('articles_list.txt')
TraitementCategorie = crawlerCat(u'Écosse')
TraitementRecherche = crawlerSearch(u'Écosse')
while 1:
     TraitementRC = crawlerRC()

python movepages.py -pairs:"articles_listed.txt" -noredirect -lang:fr -family:wikipedia
python interwiki.py -lang:fr -family:wikiversity -cat:anglais
'''

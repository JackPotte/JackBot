#!/usr/bin/env python
# coding: utf-8

# Ce script liste des pages dans un fichier (avant éventuel renommage avec movingpages.py)

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
input = u'articles_WPin.txt'
output = u'articles_WPout.txt'
summary = u'Interwikis francophones'

# Traitement d'une catégorie
def modification(PageHS):
	PageTemp = u''
	page = Page(site,PageHS)
	if page.exists():
		try:
			PageTemp = page.get()
		except wikipedia.NoPage:
			print "NoPage"
			return
		except wikipedia.IsRedirectPage:
			print "Redirect page"
			print PageHS
		if re.search(u'langue *= *pdf',PageTemp):
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : pdf\n')
			txtfile.close()	
		if re.search(u'{{[de|es|it|pt|ja|zh|ru]}} langue *= *en',PageTemp):
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : langues\n')
			txtfile.close()	
		'''
		if re.search(u'{{[l|L]ien brisé\|[^}]*url *=[^}\|]*[\[|\]|<|>|\^|`|"][\n|}|)]',PageTemp):
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : faux lien brisé\n')
			txtfile.close()
		if PageTemp.find('{{DEFAULTSORT') != -1 and PageTemp.find('{{CLEDETRI') != -1:
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : clé de tri\n')
			txtfile.close()
		if PageTemp.count('[[') - PageTemp.count(']]') != 0:
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : lien interne\n')
			txtfile.close()
		if PageTemp.count('{{') - PageTemp.count('}}') != 0:
			txtfile = codecs.open(output, 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']] : lien externe\n')
			txtfile.close()
		'''
		
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

# Lancement 
TraitementFile = crawlerFile(input)
'''
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementLiens = crawlerLink(u'Modèle:Wikiprojet Athlétisme')
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementCategorie = crawlerCat(u'Écosse')
TraitementRecherche = crawlerSearch(u'Écosse')
while 1:
     TraitementRC = crawlerRC()

python movepages.py -pairs:"articles_listed.txt" -noredirect -lang:fr -family:wikipedia
python delete.py -lang:fr -family:wiktionary -cat:"Pages à supprimer rapidement"
python delete.py -lang:fr -family:wikibooks -links:"Delete"
A vérifier dans le dump WP :
	[^<]/ref>
	{{[^}]*langue *= *[^}]*langue *= *[^}]*}}
	{{[l|L]ien web\|[^}]*{{[l|L]ien brisé
	{{[l|L]ien brisé\|[^}]*url *=[^}\|]*[\[|\]|<|>|\^|`|"][\n|}]
'''
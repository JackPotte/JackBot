#!/usr/bin/env python
# coding: utf-8
# Ce script liste remplace des modèles dans leurs pages liées, avant de les supprimer si elles sont des sous-pages

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wikibooks"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Page liée à une suppression'

# Traitement d'une catégorie
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() != 0 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				PageEnd = page.getRedirectTarget()
			except wikipedia.NoPage:
				print "NoPage"
				return
			gen2 = pagegenerators.ReferringPageGenerator(page)
			for PageCourante in pagegenerators.PreloadingGenerator(gen2,100):
				print(PageCourante.title().encode(config.console_encoding, 'replace'))
				try:
					PageBegin = PageCourante.get()
				except wikipedia.NoPage:
					print "NoPage"
					return
				except wikipedia.IsRedirectPage:
					print "Redirect page"
					return
				except wikipedia.LockedPage:
					print "Locked/protected page"
					return
				except wikipedia.ServerError:
					print "ServerError"
					return
				except wikipedia.NoSuchSite:
					print "NoSuchSite"
					return
				except wikipedia.InvalidTitle:
					print "InvalidTitle"
					return			
				PageTemp = PageBegin
				while PageTemp.find(u'[[' + PageHS + u']]') != -1:
					PageTemp = PageTemp[0:PageTemp.find(u'[[' + PageHS + u']]')+2] + PageEnd.title() + u'|' + PageHS + PageTemp[PageTemp.find(u'[[' + PageHS + u']]')+len(u'[[' + PageHS + u']]')-2:len(PageTemp)]
				while PageTemp.find(u'[[' + PageHS + u'|') != -1:
					PageTemp = PageTemp[0:PageTemp.find(u'[[' + PageHS + u'|')+2] + PageEnd.title() + PageTemp[PageTemp.find(u'[[' + PageHS + u'|')+len(u'[[' + PageHS + u'|')-1:len(PageTemp)]
				if PageTemp != PageBegin: sauvegarde(PageCourante,PageTemp)
			if PageHS.find(u'/') != -1 or PageHS.find(u' - ') != -1: page.delete(u'Suppression après gestion des pages liées', u'', throttle = True)	

				
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
	'''subcat = cat.subcategories(recurse = true)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())'''

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
			
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "10")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,200):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
		page = Page(site,u'User talk:' + mynick)
		if page.exists():
			PageTemp = u''
			try:
				PageTemp = page.get()
			except wikipedia.NoPage: return
			except wikipedia.IsRedirectPage: return
			except wikipedia.LockedPage: return
			except wikipedia.ServerError: return
			except wikipedia.BadTitle: return
			except pywikibot.EditConflict: return
			if PageTemp != u"{{/Stop}}":
				pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
				exit(0)
				
def sauvegarde(PageCourante, Contenu):
	ArretDUrgence()
	result = "ok"
	#print(Contenu.encode(config.console_encoding, 'replace')[0:4000])	#[len(Contenu)-2000:len(Contenu)]) #
	#result = raw_input("Sauvegarder ? (o/n)")
	if result != "n" and result != "no" and result != "non":
		try:
			PageCourante.put(Contenu, summary)
		except wikipedia.NoPage: return
		except wikipedia.IsRedirectPage: return
		except wikipedia.LockedPage: return
		except pywikibot.EditConflict: return
		except wikipedia.ServerError: return
		except wikipedia.BadTitle: return
		
# Lancement
TraitementRedirections = crawlerRedirects()

'''
TraitementUtilisateur = crawlerUser(u'')
TraitementFile = crawlerFile('articles_list.txt')
TraitementLiens = crawlerLink(u'Modèle:Autres projets',u'')
TraitementCategory = crawlerCat(u'Catégorie:Modèles de base de code langue')
TraitementRecherche = crawlerSearch(u'/Aide')
python protect.py -lang:fr -family:wikibooks -file:"articles_list.txt" -edit:sysop -move:sysop -summary:"Protection des modèles > 10 000"
python delete.py -lang:fr -family:wikibooks -file:"articles_WLin.txt" -undelete -summary:"Licence trouvée"
python movepages.py -lang:fr -family:wikibooks -pairs:"articles_listed.txt" -noredirect
python interwiki.py -lang:fr -family:wikibooks -page:"Utilisateur:JackBot"
python imagecopy.py -lang:fr -family:wikibooks -cat:
python revertbot.py -lang:fr -family:wikibooks
python redirect.py broken -lang:fr -family:wikibooks -always

python imagecopy.py -lang:en -family:wikibooks -transcludes:GFDL -always
python delete.py -lang:fr -family:wikibooks -cat:"Image présente sur Commons" -summary:"Transféré sur Commons"
python replace.py -lang:commons -family:commons -cat:"Étude sur l'enseignement et l'apprentissage" "{{No license since|month=August|day=2|year=2014}}" "{{PD-self}}"
'''
#à faire : suppression auto si plus de page liée
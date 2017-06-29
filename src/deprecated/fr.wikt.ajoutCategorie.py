#!/usr/bin/env python
# coding: utf-8
# Ce script patch les catégories

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re, collections, socket, langues
import hyperlynx, CleDeTri, html2Unicode		# Faits maison
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
summary = u'Ajout de catégorie'
cat = u'[[Catégorie:Machines en $langue]]'
ns = 14
debogage = False

# Modification du wiki
def modification(PageHS):
	if debogage == True: print PageHS.encode(config.console_encoding, 'replace')
	
	# Détermination de la langue
	if PageHS.find(u' en ') != -1:
		Langue = PageHS[PageHS.find(u' en ')+len(u' en '):]
		if debogage == True: print Langue.encode(config.console_encoding, 'replace')
		Categorie = cat.replace(u'$langue', Langue)
		if debogage == True: print Categorie.encode(config.console_encoding, 'replace')
	else:
		if debogage == True: print u'Pas de langue trouvée'
		return
		
	page = Page(site,PageHS)
	if not page.exists(): return
	if page.namespace() != ns: return
	try: PageBegin = page.get()
	except wikipedia.NoPage: return
	except wikipedia.IsRedirectPage: return
	except wikipedia.ServerError: return
	if PageBegin.find(Categorie) == -1:
		if debogage == True: print 'Catégorie absente'
		if PageBegin.find(u'[[Catégorie:') == -1:
			PageEnd = PageBegin + u'\n' + Categorie
		else:
			PageEnd = PageBegin[:PageBegin.find(u'[[Catégorie:')] + Categorie + u'\n' + PageBegin[PageBegin.find(u'[[Catégorie:'):]
		PageEnd = html2Unicode.html2Unicode(PageEnd)
		if PageEnd != PageBegin: sauvegarde(page, PageEnd, summary)
	else:
		if debogage == True: print 'Catégorie présente'

def trim(s):
    return s.strip(" \t\n\r\0\x0B")
	
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
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print Page.title()
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
		for subcategory in subcat:
			pages = subcategory.articlesList(False)
			for Page in pagegenerators.PreloadingGenerator(pages,100):
				modification(Page.title())

# Traitement des sous-catégories
def crawlerCatCat(category,recursif):
	#modification(category.title())
	cat = catlib.Category(site, category)
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
	else:
		subcat = cat.subcategories(recurse = False)
	for subcategory in subcat:
		modification(subcategory.title())

# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [14])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
	modifier = u'False'
	cat = catlib.Category(site, pagename)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [14])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,1000):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,1000):
		modification(Page.title())
		
def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage == True:
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
TraitementCatCat = crawlerCatCat(u'Catégorie:Véhicules', u'False')
'''
TraitementCatCat = crawlerCatCat(u'Catégorie:Origines étymologiques des mots')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementLiens = crawlerLink(u'Modèle:fr')
TraitementFile = crawlerFile('articles_listed.txt')
TraitementPage = modification(u'Modèle:aab')
while 1:
	TraitementRC = crawlerRC()
'''

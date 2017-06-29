#!/usr/bin/env python
# coding: utf-8
# Ce script crée des localités

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
import CleDeTri, html2Unicode		# Faits maison
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
site = getSite(language,u'wiktionary')
summary = u'[[Wiktionnaire:Bot/Requêtes#Création_d.27articles_sur_les_communes_de_France|Importation depuis Wikipédia]]'
debogage = False

# Modification du wiki
def modification(PageHS):
	print (PageHS.encode(config.console_encoding, 'replace'))
	codelangue = u'fr'
	nature = u'-nom-pr-'
	pays = u'France'
	articleWT = PageHS[:PageHS.find(u',')]
	PageHS = PageHS[PageHS.find(u',')+1:]
	articleWP = PageHS[:PageHS.find(u',')]
	PageHS = PageHS[PageHS.find(u',')+1:]
	departement = PageHS[PageHS.find(u',')+1:]
	if articleWP == articleWT:
		projetfrere = u'{{WP}}'
	else:
		projetfrere = u'{{WP|' + articleWP + u'}}'
		
	page = Page(site, articleWT)
	if not page.exists() and page.namespace() == 0:
		CleTri = CleDeTri.CleDeTri(articleWT)
		if CleTri.lower() == articleWT.lower():
			CleTri = u''
		else:
			CleTri = u'{{clé de tri|' + CleTri + u'}}'
		PageEnd = u'=={{langue|' + codelangue + u'}}==\n{{-étym-}}\n{{ébauche-étym|fr}}\n\n{{' + nature + u'|' + codelangue + u'}}\n\'\'\'' + articleWT + u'\'\'\' {{pron||' + codelangue + u'}}\n# Localité du département : [[' + departement + u']], pays : [[' + pays + u']].\n\n{{-voir-}}\n* ' + projetfrere + u'\n\n[[Catégorie:Localités de France en français]]\n\n' + CleTri
		sauvegarde(page, PageEnd, summary)
	else:	
		if debogage == True: print 'Page existante'
		try:
			PageBegin = page.get()
		except wikipedia.NoPage:return
		except wikipedia.IsRedirectPage: return
		if PageBegin.find(u' ' + departement) == -1 and PageBegin.find(u'[[' + departement) == -1:
			if debogage == True: print 'Ajout d\'une ligne de définition'
			PageTemp = PageBegin[PageBegin.find(u'#'):]
			PageEnd = PageBegin[:PageBegin.find(u'#')+PageTemp.find(u'\n')+1] + u'# Localité du département : [[' + departement + u']], pays : [[' + pays + u']].\n' + PageBegin[PageBegin.find(u'#')+PageTemp.find(u'\n')+1:]
			if PageTemp.find(u'{{-voir') != -1:
				if debogage == True: print 'Ajout d\'une ligne vers le projet frère'
				PageTemp = PageEnd[PageEnd.find(u'{{-voir'):]
				PageEnd = PageEnd[:PageEnd.find(u'{{-voir')+PageTemp.find(u'\n')+1] + u'* {{WP|' + articleWT + u'}}\n' + PageEnd[PageEnd.find(u'{{-voir')+PageTemp.find(u'\n')+1:]
			sauvegarde(page, PageEnd, summary)

		
def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def rec_anagram(counter):
	# Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1
def anagram(word):
    return rec_anagram(collections.Counter(word))
	
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			if PageHS.find(u'[[') != -1:
				PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
			if PageHS.find(u']]') != -1:
				PageHS = PageHS[0:PageHS.find(u']]')]
			# Conversion ASCII => Unicode (pour les .txt)
			modification(html2Unicode.html2Unicode(PageHS))
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
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

# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
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
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
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

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
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

# Modèles
TraitementFile = crawlerFile('articles_WTin.txt')
'''
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementLiens = crawlerLink(u'Modèle:terme',u'')
TraitementLiens = crawlerLink(u'Modèle:R:DAF8',u'')
TraitementLiens = crawlerLink(u'Modèle:Import:DAF8',u'')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True)
TraitementRecherche = crawlerSearch(u'clé de tri')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')
while 1:
	TraitementRC = crawlerRC()
'''
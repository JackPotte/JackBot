#!/usr/bin/env python
# coding: utf-8
# Ce script identifie les palindrome depuis un dump TXT (List of page titles in main namespace)

# Importation des modules
import catlib, pagegenerators, os, langues
from wikipedia import *

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
debogage = False

# Modification du wiki
def modification(PageHS):
	summary = u'[[Catégorie:Palindromes]]'
	#if debogage == True: print u'------------------------------------'
	#print(PageHS.encode(config.console_encoding, 'replace'))
	if len(PageHS) > 1 and PageHS == PageHS[::-1]:
		try:
			page = Page(site,PageHS)
		except UnicodeDecodeError: 
			print "UnicodeDecodeError l 26"
			return
			
		if page.exists() and page.namespace() == 0:
			try:
				PageBegin = page.get()
			except wikipedia.NoPage:
				print "NoPage l 28"
				return
			except wikipedia.LockedPage: 
				print "Locked l 31"
				return
			except wikipedia.IsRedirectPage: 
				print "IsRedirect l 34"
				return
		else:
			print "NoPage l 37"
			return
		PageTemp = PageBegin
		PageEnd = u''
		
		# Pour chaque langue, recherche de la catégorie des palindromes
		while PageTemp.find('{{langue|') != -1:
			PageEnd = PageEnd + PageTemp[:PageTemp.find('{{langue|')+len('{{langue|')]
			PageTemp = PageTemp[PageTemp.find('{{langue|')+len('{{langue|'):]
			codelangue = PageTemp[:PageTemp.find('}}')]
			NomLangue = langues.langues[codelangue].decode("utf8")
			if NomLangue != u'':
				#if debogage == True: print NomLangue.encode(config.console_encoding, 'replace')
				if PageTemp.find(u'[[Catégorie:Palindromes en ' + NomLangue) == -1:
					# Modification de la page
					if PageTemp.find('{{langue|') != -1:
						PageTemp2 = PageTemp[:PageTemp.find('{{langue|')]
						PageTemp = PageTemp[:PageTemp2.rfind(u'\n')] + u'\n[[Catégorie:Palindromes en '+NomLangue+']]\n\n' + PageTemp[PageTemp2.rfind(u'\n'):]
					else:
						PageTemp = PageTemp + u'\n\n[[Catégorie:Palindromes en '+NomLangue+']]'
		
		PageEnd = PageEnd + PageTemp		
		#if debogage == True: print (u'--------------------------------------------------------------------------------------------')
		if PageEnd != PageBegin:
			sauvegarde(page,PageEnd, summary)
		elif debogage == True:
			print "Aucun changement"
		
		
def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def crawlerXML(source):
	pages = [r for r in xmlreader.XmlDump(source, allrevisions=False).parse()]
	for Page in pages:
		modification(Page.title())
	
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		#PagesHS = codecs.open(source,"r","utf-8")
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			'''if PageHS.find(u'[[') != -1:
				PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
			if PageHS.find(u']]') != -1:
				PageHS = PageHS[0:PageHS.find(u']]')]'''
			# Conversion ASCII => Unicode (pour les .txt)
			#modification(HTMLUnicode.HTMLUnicode(PageHS))
			modification(PageHS)
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
def crawlerUser(username,jusqua):
	compteur = 0
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
		compteur = compteur + 1
		if compteur > jusqua: break

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
			
# Lancement
TraitementFichier = crawlerFile(u'frwiktionary-20140314-all-titles-in-ns0.txt')


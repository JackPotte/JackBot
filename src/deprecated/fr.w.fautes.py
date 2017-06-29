#!/usr/bin/env python
# Ce script corrige les fautes d'orthographe sans casser d'image ou d'hyperlien

# Importation des modules
import os, catlib, pagegenerators, codecs
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
size = 3
old = range(1, size)
new = range(1, size)
old[1] = u'Alfredo di Stéfano'
new[1] = u'Alfredo Di Stéfano'
ChangerLiens = 'oui'
summary = u'[[Wikipédia:Bot/Requêtes/2011/11]] : Alfredo Di Stéfano'

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!=0 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
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
	PageEnd = ""
	position = 0
	while position < len(PageTemp):	# On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première	
		for p in range(1,size-1):
			position = PageTemp.find(old[p])
			if position < 0: break
			PageEnd = PageEnd + PageTemp[0:position]
			PageTemp = PageTemp[position:len(PageTemp)]
			if ChangerLiens == u'oui' or ChangerLiens == u'ok':
				# Lien interwiki ou image à éviter
				if PageEnd.rfind(u'[') > PageEnd.rfind(u'\n') and PageEnd.rfind(u'[') > PageEnd.rfind(u']') and PageEnd.rfind(u':') > PageEnd.rfind(u'['):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break
				else:
					PageEnd = PageEnd + new[p]
					PageTemp = PageTemp[len(old[p]):len(PageTemp)]
					break
			else:
				# Lien interne à éviter
				if PageEnd.rfind(u'[') > PageEnd.rfind(u'\n') and PageEnd.rfind(u'[') > PageEnd.rfind(u']'):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break
				if PageEnd.rfind(u'{') > PageEnd.rfind(u'}'):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break
				# Lien externe à éviter
				elif PageEnd.rfind(u'http://') > PageEnd.rfind(u' ') and PageEnd.rfind(u'http://') > PageEnd.rfind(u'\n') and PageEnd.rfind(u'http://') > PageEnd.rfind(u'|'):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break
				# Modèle à éviter
				elif PageEnd.rfind(u'<ref') > PageEnd.rfind(u'</ref>') or PageEnd.rfind(u'{{langue|') > PageEnd.rfind(u'}}') or PageEnd.rfind(u'{{Traduction/') > PageEnd.rfind(u'}}') or PageEnd.rfind(u'{{Traduit de') > PageEnd.rfind(u'}}'):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break	
				if PageEnd.rfind(u'<') > PageEnd.rfind(u'>'):
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
					break			
				# Fautes à remplacer
				else:
					PageEnd = PageEnd + new[p]
					PageTemp = PageTemp[len(old[p]):len(PageTemp)]
					break

		if position < 0: break
	PageEnd = PageEnd + PageTemp[0:len(PageTemp)]
	if PageEnd != page.get():
		arretdurgence()
		try:
			result = "ok"
			#print (PageEnd[PageEnd.find(new[1])-100:PageEnd.find(new[1])+100].encode(config.console_encoding, 'replace'))
			#result = raw_input(u'\033[94m' + u'Sauvegarder ? (o/n)' + '\033[0m ')
			if result == u'n' or result == u'no' or result == u'non': 
				return
			else:
				page.put(PageEnd, summary)
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
def lecture(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		#if not crawlerFile(PageHS):
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
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,10000):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Lancement
TraitementSearch = crawlerSearch(u'Alfredo di Stéfano')
TraitementLiens = crawlerLink(u'Alfredo Di Stéfano')
'''
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementFichier = lecture('articles_list.txt')
TraitementCategorie = crawlerCat('')
TraitementLiens = crawlerLink(u'')
TraitementRecherche = crawlerSearch(u'')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
     TraitementRC = crawlerRC()
'''

#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles de Wikilivres

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re, collections, socket
import hyperlynx, CleDeTri, HTMLUnicode		# Faits maison
from wikipedia import *
mynick = "JackBot"
language = "fr"
family = "wikibooks"
site = getSite(language,family)
debogage = False
debogageLent = False

# Modification du wiki
def modification(PageHS):
	summary = u'Formatage'
	page = Page(site,PageHS)
	if page.namespace() != 0: return
	try:
		PageBegin = page.get()
	except wikipedia.NoPage:
		print "NoPage"
		return
	except wikipedia.IsRedirectPage:
		print "Redirect page"
		return
	PageTemp = PageBegin
	PageEnd = u''
	
	# Traitement des modèles
	regex = ur'\{\{[P|p]ortail([^\}]*)\}\}'
	if re.search(regex, PageTemp):
		summary += ', retrait des portails'
		PageTemp = re.sub(regex, ur'', PageTemp)
	regex = ur'\{\{[P|p]alette([^\}]*)\}\}'
	if re.search(regex, PageTemp):
		summary += ', retrait des palettes'
		PageTemp = re.sub(regex, ur'', PageTemp)
	PageTemp = PageTemp.replace(u'{{PDC}}', u'profondeur de champ')
	PageTemp = PageTemp.replace(u'[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
	PageTemp = PageTemp.replace(u'[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
	PageTemp = PageTemp.replace(u'{{BookCat}}', u'{{AutoCat}}')
	PageTemp = PageTemp.replace(u'{{reflist}}', u'{{Références}}')
	PageTemp = PageTemp.replace(u'{{Reflist}}', u'{{Références}}')
	PageTemp = PageTemp.replace(u'<references/>', u'{{Références}}')
	PageTemp = PageTemp.replace(u'<references />', u'{{Références}}')
	
	# Traitement des hyperliens
	PageTemp = hyperlynx.hyperlynx(PageTemp)
	
	# Clés de tri pour les noms propres
	if PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
		PageTemp = PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie')] + PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
	
	''' Ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
	regex = ur'()\n{{DEFAULTSORT[^}]*}}'
	if re.search(regex, PageTemp):
		PageTemp = re.sub(regex, ur'\1', PageTemp)
	regex = ur'()\n{{defaultsort[^}]*}}'
	if re.search(regex, PageTemp):
		PageTemp = re.sub(regex, ur'\1', PageTemp)
	'''
	PageEnd = PageEnd + PageTemp
	if PageEnd != PageBegin: sauvegarde(page,PageEnd,summary)


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
	gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
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
			
# Lancement
if len(sys.argv) > 1:
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'txt':
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Pages using duplicate arguments in template calls',False,u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:Reflist',u'')
		TraitementLiens = crawlerLink(u'Modèle:BookCat',u'')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	TraitementPage = modification(u'Diaspora : Le guide du parfait débutant/Icônes des réseaux sociaux sur le profil')

'''
TraitementLiens = crawlerLink(u'Modèle:Palette',u'')
TraitementCategory = crawlerCat(u'Catégorie:Personnalités de la photographie')
while 1:
	TraitementRC = crawlerRC()
'''

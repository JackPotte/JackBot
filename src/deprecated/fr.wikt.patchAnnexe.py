#!/usr/bin/env python
# coding: utf-8
# Ce script patch les annexes
## Ajout de {{voir}}
## Ajout des interwikis en allemand et italien 

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re
import CleDeTri, html2Unicode		# Faits maison
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
summary = u'[[Wiktionnaire:Bot/Requêtes]]'
debogage = False
limite = 10
prefixe = range(1, limite+1)
prefixe[0] = 'auto'
prefixe[1] = 'contre'
prefixe[2] = 'co'
prefixe[3] = 'entre'
prefixe[4] = 'entr'
prefixe[5] = 'sous'
prefixe[6] = 'sur'
prefixe[7] = 're'
prefixe[8] = 'pseudo'
prefixe[9] = 'extra'

# Modification du wiki
def modification(PageHS):
	if debogage == True: print PageHS.encode(config.console_encoding, 'replace')
	page = Page(site,PageHS)
	if not page.exists(): return
	if page.namespace() != 100: return
	try: PageBegin = page.get()
	except wikipedia.NoPage: return
	except wikipedia.IsRedirectPage: return
	except wikipedia.ServerError: return
	PageEnd = PageBegin
	
	if PageHS[:len(u'Annexe:Conjugaison en français/')] == u'Annexe:Conjugaison en français/' or PageHS[:len(u'Annexe:Conjugaison en fran&#231;ais')] == u'Annexe:Conjugaison en fran&#231;ais':
		if PageEnd.find(u'{{voir|') == -1:
			if debogage == True: print u'Recherche des homonymes d\'annexe en français...'
			PageHomo = u''
			for p in range(0,limite):
				if PageHS[PageHS.find(u'/')+1:PageHS.find(u'/')+1+len(prefixe[p])+1] == prefixe[p] + u'-':
					PageHomo = PageHS[:PageHS.find(u'/')+1+len(prefixe[p])] + PageHS[PageHS.find(u'/')+len(prefixe[p])+2:]
				elif PageHS[PageHS.find(u'/')+1:PageHS.find(u'/')+1+len(prefixe[p])+1] == prefixe[p] + u'’':
					PageHomo = PageHS[:PageHS.find(u'/')+1+len(prefixe[p])] + PageHS[PageHS.find(u'/')+len(prefixe[p])+2:]
				elif PageHS[PageHS.find(u'/')+1:PageHS.find(u'/')+1+len(prefixe[p])] == prefixe[p]:
					PageHomo = PageHS[:PageHS.find(u'/')+1+len(prefixe[p])] + u'-' + PageHS[PageHS.find(u'/')+1+len(prefixe[p]):]
			if PageHomo != u'':
				if debogage == True: print u'Préfixe : ' + PageHomo
				pageHomo = Page(site,PageHomo)
				if not pageHomo.exists():
					PageHomo = PageHomo + u'’'
					pageHomo = Page(site,PageHomo)
				if pageHomo.exists():
					if debogage == True: print 'Ajout de {{voir}}'
					PageEnd = u'<noinclude>{{voir|' + PageHomo + u'}}</noinclude>\n' + PageEnd
					PageEnd = html2Unicode.html2Unicode(PageEnd)
		
		verbe = PageHS[PageHS.find(u'/')+1:]
		if debogage == True: print u'Recherche d\'interwikis pour : ' + verbe + u'...'
		interwikis = u''
		if PageEnd.find(u'[[de:') == -1:
			if debogage == True: print u' en allemand'
			site2 = getSite('de',family)
			page2 = Page(site2,verbe + u' (Konjugation)')
			if page2.exists():
				try: Page2 = page2.get()
				except wikipedia.NoPage: return
				except wikipedia.IsRedirectPage: return
				except wikipedia.ServerError: return
				if Page2.find(u'Französisch') != -1:
					interwikis = interwikis + u'\n[[de:' + verbe + u' (Konjugation)]]'
		if PageEnd.find(u'[[it:') == -1:
			if debogage == True: print u' en italien'
			site2 = getSite('it',family)
			page2 = Page(site2,u'Appendice:Coniugazioni/Francese/' + verbe)
			if page2.exists(): interwikis = interwikis + u'\n[[it:Appendice:Coniugazioni/Francese/' + verbe + u']]'
		if interwikis != u'': PageEnd = PageEnd + '\n' + interwikis
		
		# Sauvegarde
		if PageEnd != PageBegin: sauvegarde(page, PageEnd, summary)

		
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [100])
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [100])
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
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [100])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "100")
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
	for Page in site.allpages(start=u'', namespace=100, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=100,includeredirects=False)
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
TraitementCategory = crawlerCat(u'Catégorie:Conjugaison en français', False, u'Annexe:Conjugaison en français/caillasser')
'''
TraitementCatCat = crawlerCatCat(u'Catégorie:Origines étymologiques des mots')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementLiens = crawlerLink(u'Modèle:voir')
TraitementFile = crawlerFile('articles_WTin.txt')
while 1:
	TraitementRC = crawlerRC()
'''

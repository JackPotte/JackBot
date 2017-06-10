#!/usr/bin/env python
# Ce script crée les sous-pages de {{Traduction}}.
 
# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *
 
# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
summary = u'[[Wikipédia:Bot/Requêtes/2011/10#Listage des traductions]]'

# Modification du wiki à partir du nom de la page
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() != 0 and PageHS != u'Utilisateur:JackBot/test': # On évite les sous-pages  or PageHS.find(u'/') == -1
			return
		else:
			Traduction = Page(site,u'Discussion:' + PageHS + u'/Traduction')
			if not Traduction.exists():
				try:
					PageTemp = page.get()
				except wikipedia.NoPage:
					print "NoPage"
					return
				except wikipedia.LockedPage:
					print "Locked/protected page"
					return
				except wikipedia.IsRedirectPage:
					print "Redirect page"
					return
				# Recherche des liens interwikis par traductions fréquentes
				if PageTemp.find('[[en:') != -1:
					codelangue = u'en'
					PageTemp2 = PageTemp[PageTemp.find('[[en:')+len('[[en:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[es:') != -1:
					codelangue = u'es'
					PageTemp2 = PageTemp[PageTemp.find('[[es:')+len('[[es:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[es:') != -1:
					codelangue = u'de'
					PageTemp2 = PageTemp[PageTemp.find('[[de:')+len('[[de:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[it:') != -1:
					codelangue = u'it'
					PageTemp2 = PageTemp[PageTemp.find('[[it:')+len('[[it:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[pt:') != -1:
					codelangue = u'pt'
					PageTemp2 = PageTemp[PageTemp.find('[[pt:')+len('[[pt:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[ca:') != -1:
					codelangue = u'ca'
					PageTemp2 = PageTemp[PageTemp.find('[[ca:')+len('[[ca:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[nl:') != -1:
					codelangue = u'nl'
					PageTemp2 = PageTemp[PageTemp.find('[[nl:')+len('[[nl:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[sv:') != -1:
					codelangue = u'sv'
					PageTemp2 = PageTemp[PageTemp.find('[[sv:')+len('[[sv:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[pl:') != -1:
					codelangue = u'pl'
					PageTemp2 = PageTemp[PageTemp.find('[[pl:')+len('[[pl:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[ru:') != -1:
					codelangue = u'ru'
					PageTemp2 = PageTemp[PageTemp.find('[[ru:')+len('[[ru:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[zh:') != -1:
					codelangue = u'zh'
					PageTemp2 = PageTemp[PageTemp.find('[[zh:')+len('[[zh:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				elif PageTemp.find('[[ja:') != -1:
					codelangue = u'ja'
					PageTemp2 = PageTemp[PageTemp.find('[[ja:')+len('[[ja:'):len(PageTemp)]
					interwiki = PageTemp2[0:PageTemp2.find(u']]')]
				else:
					codelangue = u'en'
					interwiki = PageHS
				PageEnd = u'{{subst:Initialiser la page de traduction|{{subst:BASEPAGENAME}}|[[Utilisateur:JackBot|JackBot]]||' + codelangue + u'||' + interwiki + u'||Article demandé par un tiers||Création de sous-page automatique}}'
				# Sauvegarde semie-automatique
				result = "ok"
				#print (PageEnd.encode(config.console_encoding, 'replace')[0:900])
				#result = raw_input(u'\033[94m' + u'Sauvegarder ? (o/n)' + '\033[0m ')
				if result == u'n' or result == u'no' or result == u'non': 
					return
				else:
					try:
							arretdurgence()
							Traduction.put(PageEnd, summary)
					except pywikibot.EditConflict:
							print "Conflict"
							return
					except wikipedia.NoPage:
							print "NoPage"
							return
					except wikipedia.IsRedirectPage:
							print "Redirect page"
							return
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
		modification(Page.title())

# Traitement des pages liées des entrées d'une catégorie
def crawlerLinkCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		if Page.title() != u'Modèle:Wikiprojet':
			crawlerLink(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			if Page.title() != u'Modèle:Wikiprojet':
				crawlerLink(Page.title())

# Lancement
TraitementLien = crawlerLink(u'Modèle:Traduction')
TraitementLien = crawlerLink(u'Modèle:Demande de traduction')
'''
TraitementCategorie = crawlerCat(u'Catégorie:Article à traduire')
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementLien = crawlerLink(u'Modèle:Wikiprojet')
TraitementFile = crawlerFile('articles_list.txt')
TraitementCategorie = crawlerCat(u'Écosse')
TraitementRecherche = crawlerSearch(u'Écosse')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
     TraitementRC = crawlerRC()


Exceptions :
http://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial%3APages+li%C3%A9es&target=Mod%C3%A8le%3AImportance&namespace=1
=maximale => maximum
=élevé => élevée
=moyen => moyenne
'''

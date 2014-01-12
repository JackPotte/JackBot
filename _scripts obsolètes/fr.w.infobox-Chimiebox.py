#!/usr/bin/env python
# coding: utf-8
# Ce script modifie le contenu d'une infobox données

# Importation des modules
import os
from wikipedia import *
import catlib
import pagegenerators

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
infobox = u'Chimiebox'
summary = u'[[Wikipédia:Bot/Requêtes/2012/11#Classe_thérapeutique_du_Modèle:Chimiebox]]'

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!=0 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				PageBegin = page.get()
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
	PageTemp = PageBegin
	if PageTemp.find(infobox) == -1:
		return
	elif PageTemp.find(u'\n<!-- Classe thérapeutique -->\n') == -1:
		return
	else:
		PageEnd = PageTemp[0:PageTemp.find(u'<!-- Classe thérapeutique -->\n')]
		PageTemp = PageTemp[PageTemp.find(u'<!-- Classe thérapeutique -->\n')+len(u'<!-- Classe thérapeutique -->\n'):len(PageTemp)]
		if PageTemp.find(u'classeTherapeutique') < PageTemp.find(u'\n'):
			if PageTemp.find(u'<!-- Considérations thérapeutiques -->\n') != -1:
				PageTemp = PageTemp[PageTemp.find(u'\n')+1:PageTemp.find(u'<!-- Considérations thérapeutiques -->\n')+len(u'<!-- Considérations thérapeutiques -->\n')] + PageTemp[0:PageTemp.find(u'\n')+1] + PageTemp[PageTemp.find(u'<!-- Considérations thérapeutiques -->\n')+len(u'<!-- Considérations thérapeutiques -->\n'):len(PageTemp)]
		else:
			print(PageHS.encode(config.console_encoding, 'replace'))
			return
			
	PageTemp = re.sub(r'{{formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{Formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{FORMATNUM:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageEnd = PageEnd + PageTemp
	if PageEnd != PageBegin: sauvegarde(page, PageEnd, summary)
	
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def lecture(source):
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
		modification(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		'''
		if subcategory == u'[[Catégorie:Mammifère disparu]]':
			raw_input("oui")
		else:
			raw_input("non")
		'''
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			#if not crawlerFile(Page.title()):
			modification(Page.title())

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Blacklist
def crawlerFile(PageCourante):
    PagesHS = open(u'BL.txt', 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': 
			break
		elif PageHS == PageCourante: 
			return "False"
    PagesHS.close()
	
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def lecture(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		if not crawlerFile(PageHS):
			modification(PageHS)
    PagesHS.close()

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
	ArretDUrgence()
	result = "ok"
	#print(Contenu.encode(config.console_encoding, 'replace')[0:4000])	#[len(Contenu)-2000:len(Contenu)]) #
	#result = raw_input("Sauvegarder ? (o/n)")
	if result != "n" and result != "no" and result != "non":
		if not summary: summary = u'[[Aide:Comment rédiger un bon article|Autoformatage]]'
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
			
# Lancement
TraitementLiens = crawlerLink(u'Modèle:' + infobox)
#TraitementFile = lecture('articles_test.txt')
#TraitementCategory = crawlerCat(u'')

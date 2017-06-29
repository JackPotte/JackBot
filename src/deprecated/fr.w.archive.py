#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script archive des pages de discussion
 
# Importation des modules
from wikipedia import *
import os, sys, catlib, pagegenerators, time, datetime, locale, re

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Autoarchivage de [[Wikipédia:Bot/Requêtes]]'
#locale.setlocale(locale.LC_ALL,'fr')

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!=4 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				PageTemp = page.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				PageTemp = page.get(get_redirect=True)
				page2 = Page(site,PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')])
				try:
					PageEnd2 = page2.get()
				except wikipedia.NoPage:
					print "NoPage"
					return
				except wikipedia.IsRedirectPage:
					print "Redirect page"
					return
				except wikipedia.LockedPage:
					print "Locked/protected page"
					return
				if PageEnd2.find(u'<noinclude>{{Wikipédia:Bot/Navig}}</noinclude>'):
					PageEnd2 = u'<noinclude>{{Wikipédia:Bot/Navig}}</noinclude>\n' + PageEnd2
					#print (PageEnd2.encode(config.console_encoding, 'replace')[0:500])
					#raw_input("archivé")
					page2.put(PageEnd2, summary, force=True)
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return
	else:
		return
	PageEnd = u''
	date = time.strftime('%d %B %Y')
	if date [0:1] == u'0': date = date[1:len(date)]
	# Erreurs : UnicodeDecodeError: 'ascii' codec can't decode byte 0xe9 in position 4: ordinal not in range(128)
	#print sys.getdefaultencoding()
	titre = "|ici]] à partir du \'\'\'" + date
	#titre = "|ici]] &#224; partir du \'\'\'" + date
	#titre = "|ici]] &#224; partir du \'\'\'" + date.decode('utf8')
	#titre = "|ici]] &#224; partir du \'\'\'" + date.encode('utf8')
	#titre = "|ici]] &#224; partir du \'\'\'" + date.replace("é", "&#233;")
	#raw_input(titre)
	#m = re.search('0-9a-z àéè+', titre)
	#raw_input (m.group(0))
	
	if PageTemp.find(date) == -1: return	# pb ASCII au mois d'août
	# Filtre de la page en retirant les paragraphes à archiver le jour même
	while PageTemp.find(titre) > 0:	
		PageTemp2 = PageTemp[0:PageTemp.find(titre)]
		PageTemp3 = PageTemp[PageTemp.find(titre):len(PageTemp)]
		if PageTemp3.find(u'\n==') > 0:
			PageEnd = PageEnd + PageTemp[PageTemp2.rfind(u'\n=='):PageTemp.find(titre)+PageTemp3.find(u'\n==')]
			PageTemp = PageTemp[0:PageTemp2.rfind(u'\n==')] + PageTemp[PageTemp.find(titre)+PageTemp3.find(u'\n=='):len(PageTemp)]
		else: # Cas du dernier paragraphe
			PageEnd = PageEnd + PageTemp[PageTemp2.rfind(u'\n=='):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp2.rfind(u'\n==')]
	# Sauvegardes
	archive = PageTemp2[PageTemp2.rfind(u'[[')+2:len(PageTemp2)]
	print archive
	if PageTemp != page.get():
		page2 = Page(site,archive)
	if page2.exists():
		if page2.namespace()!=4: 
			return
		else:
			try:
				PageEnd2 = page2.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return		
			print (PageTemp.encode(config.console_encoding, 'replace'))
			raw_input("non touché")
			#print ((PageEnd2 + PageEnd).encode(config.console_encoding, 'replace'))
			#raw_input("archivé")
			if PageEnd2.find(u'<noinclude>{{Wikipédia:Bot/Navig}}</noinclude>') == -1: PageEnd2 = u'<noinclude>{{Wikipédia:Bot/Navig}}</noinclude>\n' + PageEnd2
			page2.put(PageEnd2 + PageEnd, summary, force=True)
			page.put(PageTemp, summary, force=True)
				
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
	'''
	subcat = cat.subcategories() #recurse = True)
	for subcategory in subcat:
		
		# HS
		if subcategory == u'[[Catégorie:Mammifère disparu]]':
			raw_input("oui")
		else:
			raw_input("non")
		
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			#if not crawlerFile(Page.title()):
			modification(Page.title())'''

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Blacklist (en cours de test)
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
	
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,10000):
		modification(Page.title())
		
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		modification(PageHS)
    PagesHS.close()
	
def DatePlusMois(months):
	year, month, day = datetime.date.today().timetuple()[:3]
	new_month = month + months
	if new_month == 0:
		new_month = 12
		year = year - 1
	elif new_month == -1:
		new_month = 11
		year = year - 1
	elif new_month == -2:
		new_month = 10
		year = year - 1
	elif new_month == -3:
		new_month = 9
		year = year - 1
	elif new_month == -4:
		new_month = 8
		year = year - 1
	elif new_month == -5:
		new_month = 7
		year = year - 1
	if new_month == 2 and day > 28: day = 28
	return datetime.date(year, new_month, day)

# Lancement	
m = 0
while m > -6:
	date = str(DatePlusMois(m))
	date = date[0:date.find(u'-')] + u'/' + date[date.find(u'-')+1:len(date)]
	date = date[0:date.find(u'-')]
	#print(u'Wikipédia:Bot/Requêtes/' + date[0:7])
	#raw_input("1")
	modification(u'Wikipédia:Bot/Requêtes/' + date[0:7])
	m = m -1
'''
TraitementFile = crawlerFile('articles_list.txt')
TraitementPage = modification(u'Wikipédia:Bot/Requêtes/' + time.strftime(u'%Y/%m'))
TraitementLiens = crawlerLink(u'Modèle:mois')
TraitementSearch = crawlerSearch(u'reference')
TraitementCategory = crawlerCat(u'Catégorie:Wikipédia:ébauche géologie')
'''

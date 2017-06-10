#!/usr/bin/env python
# Ce script ajoute les portails manquants, en en remplaçant le cas échéant
 
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
size = 7
newportail = range(1, size)
notportail = range(1, size)
newportail[1] = u'Culture russe'
newportail[2] = u''
newportail[3] = u''
newportail[4] = u''
newportail[5] = u''
notportail[1] = u'culture russe'	# [[Wikipédia:Règle_sur_l'apposition_de_liens_vers_les_portails]]
notportail[2] = u'Russie'
notportail[3] = u'russie'
notportail[4] = u'Culture'
notportail[5] = u'culture'
if newportail[1] != "":
	summary = u'[[Wikipédia:Bot/Requêtes/2010/12]] : ajout du portail ' + newportail[1]
else:
	summary = u'[[Wikipédia:Bot/Requêtes/2010/12]] : retrait du portail ' + notportail[1]
	
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
	if PageTemp.find(u'{{portail') != -1:
		position = PageTemp.find(u'{{portail')
	else:
		position = PageTemp.find(u'{{Portail')
	if position == -1: # S'il n'y a pas de portail
		position = PageTemp.find(u'[[Catégorie')
		if position == -1: # S'il n'y a pas de catégorie
			PageEnd = PageTemp
			PageTemp = ""
		else:
			PageEnd = PageTemp[0:position]
			PageTemp = PageTemp[position:(len(PageTemp))]
	else:
		# Formatage
		while PageTemp[position+len(u'{{Portail'):position+len(u'{{Portail')+1] == u' ': # On corrige les {{Portail ...}}
			PageTemp = PageTemp[0:position+len(u'{{Portail')] + PageTemp[position+len(u'{{Portail')+1:len(PageTemp)]
		while PageTemp[position+len(u'{{portail'):position+len(u'{{portail')+1] == u' ': # On corrige les {{Portail ...}}
			PageTemp = PageTemp[0:position+len(u'{{portail')] + PageTemp[position+len(u'{{portail')+1:len(PageTemp)]
		if PageTemp[position+len(u'{{Portail'):position+len(u'{{Portail')+1] != u'|' or PageTemp[position+len(u'{{Portail'):position+len(u'{{Portail')+1] != u'}':
			PageTemp = PageTemp[0:position+len(u'{{Portail')] + u'|' + PageTemp[position+len(u'{{Portail'):len(PageTemp)] # PageTemp = ...{{Portail|...
		PageEnd = PageEnd + PageTemp[0:position+len(u'{{Portail')] # PageEnd = ...{{Portail
		PageTemp = PageTemp[position+len(u'{{Portail'):len(PageTemp)]
		# On scanne tous les portails à retirer
		for p in range(1,size-1):
			if (PageTemp.find(notportail[p]) != -1) and (PageTemp.find(notportail[p]) < PageTemp.find(u'}}')
			) and (PageTemp[PageTemp.find(notportail[p])-1:PageTemp.find(notportail[p])] == u'|' or PageTemp[PageTemp.find(notportail[p])-1:PageTemp.find(notportail[p])] == u' '
			) and (PageTemp[PageTemp.find(notportail[p])+len(notportail[p]):PageTemp.find(notportail[p])+len(notportail[p])+1] == u'|' or PageTemp[PageTemp.find(notportail[p])+len(notportail[p]):PageTemp.find(notportail[p])+len(notportail[p])+1] == u'}'):
				PageTemp = PageTemp[0:PageTemp.find(notportail[p])-1] + PageTemp[PageTemp.find(notportail[p])+len(notportail[p]):len(PageTemp)]
	# On scanne tous les portails à ajouter
	for p in range(1,size-1):
		if newportail[p] == "": break
		else:
			if (PageEnd.rfind(newportail[p]) > position and position != -1) or (PageTemp.find(newportail[p]) < PageTemp.find(u'}}') and PageTemp.find(newportail[p]) != -1): break
			else:
				if PageEnd.find(u'{{Portail') == -1 and PageEnd.find(u'{{portail') == -1:
					PageEnd = PageEnd + u'\n{{Portail'
					PageTemp = u'}}\n' + PageTemp
				PageEnd = PageEnd + u'|' + newportail[p]
	# Formatage 2
	if PageTemp.find("||") < PageTemp.find("}}") and PageTemp.find("||") != -1: # On corrige les {{Portail...||...}}
		PageTemp = PageTemp[0:PageTemp.find("||")] + PageTemp[PageTemp.find("||")+1:len(PageTemp)]
	if PageTemp.find("|}") < PageTemp.find("}}") and PageTemp.find("|}") != -1: # On corrige les {{Portail...||...}}
		PageTemp = PageTemp[0:PageTemp.find("|}")] + PageTemp[PageTemp.find("|}")+1:len(PageTemp)]
	PageEnd = PageEnd + PageTemp
	while PageEnd.find(u'{{Portail}}') != -1: # On nettoie les portails vides
		PageEnd = PageEnd[0:PageEnd.find(u'{{Portail}}')] + PageEnd[PageEnd.find(u'{{Portail}}')+len(u'{{Portail}}'):len(PageEnd)]
	while PageEnd.find(u'{{portail}}') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{portail}}')] + PageEnd[PageEnd.find(u'{{portail}}')+len(u'{{portail}}'):len(PageEnd)]
	#print (PageEnd.encode(config.console_encoding, 'replace'))
	#raw_input("fin")
	if PageEnd != page.get():
		try:
			page.put(PageEnd, summary)
		except wikipedia.LockedPage:
			print "Locked/protected page"
			return
 
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
	
# Lancement
#TraitementFile = lecture('articles_list.txt')
#TraitementLiens = crawlerLink(u'Modèle:mois')
#TraitementSearch = crawlerSearch(u'reference')
TraitementCategory = crawlerCat(u'Catégorie:Créature du folklore russe')
TraitementCategory = crawlerCat(u'Gastronomie russe')
TraitementCategory = crawlerCat(u'Littérature russe')
TraitementCategory = crawlerCat(u'Musée russe')
TraitementCategory = crawlerCat(u'Musique russe')
TraitementCategory = crawlerCat(u'Art en Russie')
TraitementCategory = crawlerCat(u'Télévision russe')
TraitementCategory = crawlerCat(u'Théâtre russe')
TraitementCategory = crawlerCat(u'Danse en Russie')
TraitementCategory = crawlerCat(u'Mythologie russe')
raw_input("Jackpot")

'''
Catégorie:Chevalier de l'Ordre de Saint-Vladimir
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.w.portails.py
#469 l 98
'''
#!/usr/bin/env python
# Ce script ajoute les ébauches manquants, en en remplaçant le cas échéant
 
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
size = 3
newebauche = range(1, size)
notebauche = range(1, size)
newebauche[1] = u'culture russe'
notebauche[1] = u'Culture russe'
if newebauche[1] != "":
	summary = u'[[Wikipédia:Bot/Requêtes/2010/11]] : ajout de l\'ébauche ' + newebauche[1]
else:
	summary = u'[[Wikipédia:Bot/Requêtes/2010/11]] : retrait de l\'ébauche ' + notebauche[1]
	
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
	if PageTemp.find(u'{{Ébauche') != -1:
		position = PageTemp.find(u'{{Ébauche')
	else:
		position = PageTemp.find(u'{{ébauche')
	if position == -1: # S'il n'y a pas d'ébauche
		PageEnd = PageTemp
		PageTemp = ""
	else:
		PageEnd = PageTemp[0:position+len(u'{{ébauche')]
		PageTemp = PageTemp[position+len(u'{{ébauche'):(len(PageTemp))]	
	# On scanne les ébauches à retirer
	for p in range(1,size-1):
		if notebauche[p] == "": break
		if (PageTemp.find(notebauche[p]) != -1) and (PageTemp.find(notebauche[p]) < PageTemp.find(u'}}')
		) and (PageTemp[PageTemp.find(notebauche[p])-1:PageTemp.find(notebauche[p])] == u'|' or PageTemp[PageTemp.find(notebauche[p])-1:PageTemp.find(notebauche[p])] == u' '
		) and (PageTemp[PageTemp.find(notebauche[p])+len(notebauche[p]):PageTemp.find(notebauche[p])+len(notebauche[p])+1] == u'|' or PageTemp[PageTemp.find(notebauche[p])+len(notebauche[p]):PageTemp.find(notebauche[p])+len(notebauche[p])+1] == u'}'):
			PageTemp = PageTemp[0:PageTemp.find(notebauche[p])-1] + PageTemp[PageTemp.find(notebauche[p])+len(notebauche[p]):len(PageTemp)]
	# On scanne les ébauches à ajouter
	for p in range(1,size-1):
		if newebauche[p] == "": break
		else:
			if (PageEnd.rfind(newebauche[p]) > position and position != -1) or (PageTemp.find(newebauche[p]) < PageTemp.find(u'}}') and PageTemp.find(newebauche[p]) != -1): break
			else:
				if PageEnd.find(u'{{ébauche') == -1 and PageEnd.find(u'{{Ébauche') == -1:
					PageEnd = u'\n{{ébauche' + u'|' + newebauche[p] + u'}}\n' + PageEnd
				else:
					PageEnd = PageEnd + u'|' + newebauche[p]
	PageEnd = PageEnd + PageTemp
	# Formatage 2
	while PageEnd.find(u'||') != -1 and PageEnd.find(u'||') < PageEnd.find(u'}}'): # On nettoie les ébauches vides
		PageEnd = PageEnd[0:PageEnd.find(u'||')] + PageEnd[PageEnd.find(u'||')+1:len(PageEnd)]
	while PageEnd.find(u'|}') != -1 and PageEnd.find(u'|}') < PageEnd.find(u'}}'): # On nettoie les ébauches vides
		PageEnd = PageEnd[0:PageEnd.find(u'|}')] + PageEnd[PageEnd.find(u'|}')+1:len(PageEnd)]
	while PageEnd.find(u'{{ébauche}}') != -1: # On nettoie les ébauches vides
		PageEnd = PageEnd[0:PageEnd.find(u'{{ébauche}}')] + PageEnd[PageEnd.find(u'{{ébauche}}')+len(u'{{ébauche}}'):len(PageEnd)]
	while PageEnd.find(u'{{Ébauche}}') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Ébauche}}')] + PageEnd[PageEnd.find(u'{{Ébauche}}')+len(u'{{Ébauche}}'):len(PageEnd)]
	if PageEnd != page.get():
		#print (PageEnd.encode(config.console_encoding, 'replace'))
		#raw_input("fin")
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
		main = Page.title()
		main = main[11:len(main)]
		modification(main)
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
			main = Page.title()
			main = main[11:len(main)]
			modification(main)

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if Page.namespace() == 1: modification(Page.title())
		elif Page.namespace() == 0: modification(u'Discussion:' + Page.title())

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
	
# Lancement
#TraitementFile = lecture('articles_test.txt')
#TraitementLiens = crawlerLink(u'Modèle:mois')
TraitementCategory = crawlerCat(u'Article sur la culture russe d\'avancement ébauche')
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.w.ébauche.py
'''
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
infobox = u'Infobox Unité militaire'
size = 4
line = range(1, size)
line[1] = u'taille'
line[2] = u'Taille'
OldParameter = range(1, size)
OldParameter[1] = u'taille'
OldParameter[2] = u'Taille'
NewParameter = range(1, size)
NewParameter[1] = u'effectif' # Bug http://fr.wikipedia.org/w/index.php?title=Crash_Boom_Bang!&diff=prev&oldid=58662566
NewParameter[2] = u'Effectif' # Si redondance mettre le plus long en premier
summary = u'[[Wikipédia:Bot/Requêtes/2010/11]] : paramètre des infobox ' + line[1]

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
	if PageTemp.find(infobox) == -1:
		return
	else:
		position = PageTemp.find(u'{{' + infobox)
		PageEnd = PageEnd + PageTemp[0:position+len(u'{{' + infobox)] # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première	
		PageTemp = PageTemp[position+len(u'{{' + infobox):len(PageTemp)]
		for l in range(1,size-1): # Pour chaque ligne à changer
			if line[l] != -1 and PageTemp.find(line[l]) != -1:
				PageTemp2 = PageTemp[PageTemp.find(line[l]):len(PageTemp)]
				PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')+1]
				longueur = len(PageTemp2)
				for p in range(1,size-1): # On cherche chaque paramètre à modifier
					if (PageTemp2.find(u'|' + OldParameter[p]) != -1 or PageTemp2.find(u'| ' + OldParameter[p]) != -1) and PageTemp2.find(OldParameter[p]) < u'}}\n': # Il y certains modèles dans les box mais sans retour chariot
						if PageTemp2.find(NewParameter[p]) != -1: # Elimination des doublons
							PageTemp3 = PageTemp2[0:PageTemp2.find(OldParameter[p])] # Détermination si le paramètre à remplacer est dans un hyperlien
							if PageTemp3.rfind(u'[') != -1:
								if PageTemp3.rfind(u'[') > PageTemp3.rfind(u']'):
									while PageTemp3[len(PageTemp3)-1:len(PageTemp3)] != u'[':
										PageTemp3 = PageTemp3[0:len(PageTemp3)-1]
									while PageTemp3[len(PageTemp3)-1:len(PageTemp3)] == u'[':
										PageTemp3 = PageTemp3[0:len(PageTemp3)-1]
							while PageTemp3[len(PageTemp3)-1:len(PageTemp3)] == u' ' or PageTemp3[len(PageTemp3)-1:len(PageTemp3)] == u',' or PageTemp3[len(PageTemp3)-1:len(PageTemp3)] == u';':
								PageTemp3 = PageTemp3[0:len(PageTemp3)-1]
							PageTemp2 = PageTemp3 + PageTemp2[PageTemp2.find(OldParameter[p]):len(PageTemp2)]
							PageTemp3 = PageTemp2[PageTemp2.find(OldParameter[p])+len(OldParameter[p]):len(PageTemp2)]
							while PageTemp3[0:1] == u']':
								PageTemp3 = PageTemp3[1:len(PageTemp3)]
							PageTemp2 = PageTemp2[0:PageTemp2.find(OldParameter[p])] + PageTemp2[PageTemp2.find(OldParameter[p])+len(OldParameter[p])+len(PageTemp2[PageTemp2.find(OldParameter[p])+len(OldParameter[p]):len(PageTemp2)])-len(PageTemp3):len(PageTemp2)]
							PageTemp = PageTemp[0:PageTemp.find(line[l])] + PageTemp2[0:len(PageTemp2)] + PageTemp[PageTemp.find(line[l])+longueur:len(PageTemp)]
						else:
							PageTemp = PageTemp[0:PageTemp.find(line[l])+PageTemp2.find(OldParameter[p])] + NewParameter[p] + PageTemp[PageTemp.find(line[l])+PageTemp2.find(OldParameter[p])+len(OldParameter[p]):len(PageTemp)]
					p=p+1
			l=l+1
	PageEnd = PageEnd + PageTemp[0:len(PageTemp)]
	#print (PageEnd.encode(config.console_encoding, 'replace'))
	#raw_input("fin")
	if PageEnd != page.get(): page.put(PageEnd, summary)	

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
	
# Lancement
#TraitementFile = lecture('articles_test.txt')
TraitementLiens = crawlerLink(u'Modèle:' + infobox)
#TraitementCategory = crawlerCat(u'')
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.w.Infobox.py
'''
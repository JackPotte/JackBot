#!/usr/bin/env python
# Ce script retire un nombre déterminé d'articles connexes

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
size = 5
article = range(1, size)
article[1] = u'Réseau de bus L\'Aile Bleue'
article[2] = u'Réseau routier de l\'Indre'
article[3] = u'Réseau des transports en commun de l\'Indre'
summary = "[[Wikip&#233;dia:Bot/Requ&#234;tes/2010/10]] : communes de l'Indre"

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
	position = PageTemp.find(u'Articles connexes')
	while position < len(PageTemp):		# On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première	
		if position < 0: return
		PageEnd = PageEnd + PageTemp[0:position]
		PageTemp = PageTemp[position:len(PageTemp)]
		for p in range(1,size-1): # On cherche chaque article connexe à retirer
			if PageTemp.find(article[p]) != -1:
				while PageTemp.find(article[p]) != 0 and len(PageTemp) > 0:
					if PageTemp.find(u'|') < PageTemp.find(u'[[') and PageTemp.find(u'|') != -1:
						position = PageTemp.find(u'|')+1
					else:
						position = PageTemp.find(u'[[')+2
					PageEnd = PageEnd + PageTemp[0:position]
					PageTemp = PageTemp[position:len(PageTemp)]
				PageTemp = PageTemp[PageTemp.find(u']]')+2:len(PageTemp)]	# PageTemp = [[Article à retirer
				if PageEnd[len(PageEnd)-1:len(PageEnd)] == u'|':
					PageEnd = PageEnd[0:PageEnd.rfind(u'[[')]
				else:
					PageEnd = PageEnd[0:len(PageEnd)-2]
	if PageEnd.find('\n* \n* \n') != -1:
		PageEnd = PageEnd[0:PageEnd.find('\n* \n* \n')] + PageEnd[PageEnd.find('\n* \n* \n')+len('\n* \n* \n')-1:len(PageEnd)]
	if PageEnd.find('\n*\t\n*\t\n') != -1:
		PageEnd = PageEnd[0:PageEnd.find('\n*\t\n*\t\n')] + PageEnd[PageEnd.find('\n*\t\n*\t\n')+len('\n*\t\n*\t\n')-1:len(PageEnd)]
	PageEnd = PageEnd + PageTemp[0:len(PageTemp)]
	page.put(PageEnd, summary)	

# Lancement
HS = lecture('articles_list.txt')
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\pywikipedia-fr.w"
python _connexes.py
'''
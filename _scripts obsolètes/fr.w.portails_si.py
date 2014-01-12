#!/usr/bin/env python
# Ce script ajoute des portails manquants, si et seulement si il en remplace

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
size = 4
newportail = range(1, size-1)
notportail = range(1, size)
newportail[1] = u'politique québécoise'
notportail[1] = u'politique'	# Wikipédia:Règle_sur_l'apposition_de_liens_vers_les_portails
notportail[2] = u'Québec'
summary = u'[[Wikipédia:Bot/Requêtes/2010/10]] : ajout du portail ' + newportail[1]

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
	position = 0
	while position < len(PageTemp) and position >= 0: # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première
		if PageTemp.find(u'{{portail') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{portail')] + u'{{Portail' + PageTemp[PageTemp.find(u'{{portail')+len(u'{{portail'):len(PageTemp)]
		position = PageTemp.find(u'{{Portail')
		if position == -1: # S'il n'y a pas de portail
			position = PageTemp.find(u'[[Catégorie')
			if position < 0: # S'il n'y a pas de catégorie
				PageEnd = PageTemp + "\n{{Portail " + newportail[1] + "}}\n"
				break
			else:
				PageEnd = PageTemp[0:position] + "\n{{Portail " + newportail[1] + "}}\n" + PageTemp[position:(len(PageTemp))]
				break
		PageEnd = PageTemp[0:position]
		PageTemp = PageTemp[position:len(PageTemp)]     # PageTemp = {{Portail...
		# Si les deux portails n'y sont pas on enchaine sur une autre page
		if not (PageTemp.find(notportail[1]) != -1 and (PageTemp.find(notportail[1]) < PageTemp.find(u'}}')
			) and (PageTemp.find(u'Portail '+notportail[1]) != -1 or PageTemp.find(u'|'+notportail[1]) != -1
			) and (PageTemp.find(notportail[1]+u'|') != -1 or PageTemp.find(notportail[1]+u'}') != -1
			) and PageTemp.find(notportail[2]) != -1 and (PageTemp.find(notportail[2]) < PageTemp.find(u'}}')
			) and (PageTemp.find(u'Portail '+notportail[2]) != -1 or PageTemp.find(u'|'+notportail[2]) != -1
			) and (PageTemp.find(notportail[2]+u'|') != -1 or PageTemp.find(notportail[2]+u'}') != -1)):
			return
		if PageTemp.find("||") < PageTemp.find("}}") and PageTemp.find("||") != -1: # On corrige les {{Portail...||...}}
			PageTemp = PageTemp[0:PageTemp.find("||")] + PageTemp[PageTemp.find("||")+1:len(PageTemp)]
		if PageTemp.find("Portail |") < PageTemp.find("}}") and PageTemp.find("Portail |") != -1: # On corrige les {{Portail |...}}
			PageTemp = PageTemp[0:PageTemp.find("Portail |")] + u'Portail|' + PageTemp[PageTemp.find("Portail |")+1:len(PageTemp)]			
		for p in range(1,size-1): # On scanne tous les vieux portails et on supprime s'il y a un vieux portail à remplacer dont le nom n'est pas inclu dans un autre
			if PageTemp.find(notportail[p]) != -1 and (PageTemp.find(notportail[p]) < PageTemp.find(u'}}')
			) and (PageTemp.find(u'Portail '+notportail[p]) != -1 or PageTemp.find(u'|'+notportail[p]) != -1
			) and (PageTemp.find(notportail[p]+u'|') != -1 or PageTemp.find(notportail[p]+u'}') != -1):
				if PageTemp.find(u'Portail '+notportail[p]) != -1:
					PageTemp = PageTemp[0:PageTemp.find(u'Portail '+notportail[p])+len(u'Portail ')] + PageTemp[PageTemp.find(u'Portail '+notportail[p])+len(u'Portail ')+len(notportail[p]):len(PageTemp)]
				else:
					if PageTemp.find(u'|'+notportail[p]+u'|') != -1:
						PageTemp = PageTemp[0:PageTemp.find(u'|'+notportail[p]+u'|')] + PageTemp[PageTemp.find(u'|'+notportail[p]+u'|')+len(notportail[p])+1:len(PageTemp)]
					elif PageTemp.find(u'|'+notportail[p]+u'}') != -1:
						PageTemp = PageTemp[0:PageTemp.find(u'|'+notportail[p]+u'}')] + PageTemp[PageTemp.find(u'|'+notportail[p]+u'}')+len(notportail[p])+1:len(PageTemp)]
			p=p+1
		for p in range(1,size-2): # On scanne tous les nouveaux portails et on ne fait rien s'il y a un nouveau portail à ajouter dont le nom n'est pas inclu dans un autre
			if PageTemp.find(newportail[p]) != -1 and (PageTemp.find(newportail[p]) < PageTemp.find(u'}}')
			) and (PageTemp[PageTemp.find(newportail[p])-1:PageTemp.find(newportail[p])] == u'|' or PageTemp[PageTemp.find(newportail[p])-1:PageTemp.find(newportail[p])] == u' '
			) and (PageTemp[PageTemp.find(newportail[p])+len(newportail[p]):PageTemp.find(newportail[p])+len(newportail[p])+1] == u'|' or PageTemp[PageTemp.find(newportail[p])+len(newportail[p]):PageTemp.find(newportail[p])+len(newportail[p])+1] == u'}'):
				print "déjà posé"
			elif PageTemp[PageTemp.find(u'Portail')+len(u'Portail'):PageTemp.find(u'Portail')+len(u'Portail')+1] == " ": # S'il faut ajouter
				if PageTemp[PageTemp.find(u'Portail')+len(u'Portail')-1:PageTemp.find(u'Portail')+len(u'Portail')+2] == u'}':
					PageTemp = PageTemp[0:PageTemp.find(u'Portail')+len(u'Portail')+1] + newportail[p] + PageTemp[PageTemp.find(u'Portail')+len(u'Portail')+1:len(PageTemp)]
				else:
					PageTemp = PageTemp[0:PageTemp.find(u'Portail')+len(u'Portail')] + u'|' + newportail[p] + PageTemp[PageTemp.find(u'Portail')+len(u'Portail')+1:len(PageTemp)]
			else:
				PageTemp = PageTemp[0:PageTemp.find(u'Portail')+len(u'Portail')] + u'|' + newportail[p] + PageTemp[PageTemp.find(u'Portail')+len(u'Portail'):len(PageTemp)]
			p=p+1
		PageEnd = PageEnd + PageTemp[0:len(PageTemp)]
		PageTemp = ""
	if PageEnd != page.get():
		page.put(PageEnd, summary)

# Lancement
HS = lecture('articles_list.txt')
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\pywikipedia-fr.w"
python _portails.py
'''
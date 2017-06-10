#!/usr/bin/env python
# Ce script crée les pages de Wiktionnaire:Collaboration_de_la_semaine.

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Création des [[Wiktionnaire:Collaboration_de_la_semaine|collaborations de la semaine]] par défaut'

# Calcul des dates
def date(j,m,a):
	if j > 31 and m == u'janvier':
		j = j - 31
		m = u'février'
	elif j > 28 and m == u'février':
		j = j - 28 # A changer les années bisextiles
		m = u'mars'
	elif j > 31 and m == u'mars':
		j = j - 31
		m = u'avril'
	elif j > 30 and m == u'avril':
		j = j - 30
		m = u'mai'
	elif j > 31 and m == u'mai':
		j = j - 31
		m = u'juin'
	elif j > 30 and m == u'juin':
		j = j - 30
		m = u'juillet'
	elif j > 31 and m == u'juillet':
		j = j - 31
		m = u'août'
	elif j > 31 and m == u'août':
		j = j - 31
		m = u'septembre'
	elif j > 30 and m == u'septembre':
		j = j - 30
		m = u'octobre'
	elif j > 31 and m == u'octobre':
		j = j - 31
		m = u'novembre'
	elif j > 30 and m == u'novembre':
		j = j - 30
		m = u'décembre'
	elif j > 31 and m == u'décembre':
		j = j - 31
		m = u'janvier'
		a = a + 1
	return str(j) + u' ' + m + u' ' + str(a)

def date2(jj,mm):
	if mm == u'janvier':
		if jj > 59: # 31 + 28 : à changer les années bisextiles
			jj = jj - 59
			mm = u'03'
		elif jj > 31:
			jj = jj - 31
			mm = u'02'
		else:
			mm = u'01'
	elif mm == u'février':
		if jj > 59:
			jj = jj - 59
			mm = u'04'		
		elif jj > 28: 
			jj = jj - 28
			mm = u'03'
		else:
			mm = u'02'
	elif mm == u'mars':
		if jj > 61:
			jj = jj - 61
			mm = u'05'		
		elif jj > 31: 
			jj = jj - 31
			mm = u'04'
		else:
			mm = u'03'
	elif mm == u'avril':
		if jj > 61:
			jj = jj - 61
			mm = u'06'		
		elif jj > 30: 
			jj = jj - 30
			mm = u'05'
		else:
			mm = u'04'
	elif mm == u'mai':
		if jj > 61:
			jj = jj - 61
			mm = u'07'		
		elif jj > 31: 
			jj = jj - 31
			mm = u'06'
		else:
			mm = u'05'
	elif mm == u'juin':
		if jj > 61:
			jj = jj - 61
			mm = u'08'	
		elif jj > 30: 
			jj = jj - 30
			mm = u'07'
		else:
			mm = u'06'
	elif mm == u'juillet':
		if jj > 62:
			jj = jj - 62
			mm = u'09'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'08'
		else:
			mm = u'07'
	elif mm == u'août':
		if jj > 61:
			jj = jj - 61
			mm = u'10'
		elif jj > 31: 
			jj = jj - 31
			mm = u'09'
		else:
			mm = u'08'
	elif mm == u'septembre':
		if jj > 61:
			jj = jj - 61
			mm = u'11'
		elif jj > 30: 
			jj = jj - 30
			mm = u'10'
		else:
			mm = u'09'
	elif mm == u'octobre':
		if jj > 61:
			jj = jj - 61
			mm = u'12'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'11'
		else:
			mm = u'10'
	elif mm == u'novembre':
		if jj > 61:
			jj = jj - 61
			mm = u'01'
		elif jj > 30: 
			jj = jj - 30
			mm = u'12'
		else:
			mm = u'11'
	elif mm == u'décembre':
		if jj > 62:
			jj = jj - 62
			mm = u'02'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'01'
		else:
			mm = u'12'
	return str(jj) + u'/' + mm
	
def zero(n):
	if n < 10:
		return u'0' + str(n)
	else:
		return str(n)

# Modification du wiki
def modification():
	j = 3 # 1e lundi de l'année
	m = u'janvier'
	a = 2011
	for s in range(4, 52):
		PageHS = u'Modèle:Projet de la semaine/' + zero(s) + u' ' + str(a)
		#print (PageHS.encode(config.console_encoding, 'replace'))
		#raw_input("1")
		page = Page(site,PageHS)
		if not page.exists():
			PageEnd = u'\'\'Les travaux à accomplir sont listés dans [[Wiktionnaire:Que faire sur le Wiktionnaire ?]]\n<noinclude>\n\'\'Ce message a été généré par un robot, n’hésitez pas à le remplacer par vos propositions\'\'\n{{-voir-}}\n* [[Modèle:Projet de la semaine/' + zero(s - 1) + u' ' + str(a) + u'|Semaine précédente]]\n* [[Modèle:Projet de la semaine/' + zero(s + 1) + u' ' + str(a) + u'|Semaine suivante]]\n[[Catégorie:Projet de la semaine|' + str(a) + u' ' + zero(s)+ u']] </noinclude>'
			print (PageEnd.encode(config.console_encoding, 'replace'))
			raw_input("Sauvegarder ?")
			page.put(PageEnd, summary)

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
		if Page.namespace() == 0: modification(u'Discussion:' + Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			if Page.namespace() == 0: modification(u'Discussion:' + Page.title())

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if Page.namespace() == 1: modification(Page.title())
		elif Page.namespace() == 0: modification(u'Discussion:' + Page.title())
		
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		if Page.namespace() == 1: modification(Page.title())

# Lancement
Traitment = modification()
#TraitementFile = lecture('articles_list.txt')
#TraitementLiens = crawlerLink(u'')
#TraitementCategory = crawlerCat(u'')
raw_input("Jackpot")

'''
Tâches annueles : 
	créer les pages comme la Wikidémie...
	archiver RBOT
Vérifier manuellement les {{trad|
python" fr.wikt.collaboration.py
'''

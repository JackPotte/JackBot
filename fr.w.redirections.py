#!/usr/bin/env python
# Ce script :
# 	Ajoute les {{DEFAULTSORT:}} dans les articles (attente de consensus pour les évaluations)
# 	Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
# 	Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
#	Vérifie les hyperliens
# A terme peut-être :
# 	Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...)
# 	Mettra à jour les évaluations à partir du bandeau ébauche
# 	Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto)

# Importation des modules
import os, catlib, pagegenerators, re
import HTMLUnicode		# Faits maison
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
debogage = False
debogageLent = False
input = u'articles_WPin.txt'
output = u'articles_WPout.txt'
ns = 0

# Modification du wiki
def modification(PageHS):
	print(PageHS.encode(config.console_encoding, 'replace'))
	summary = u'[[Aide:Redirection#Usages|Redirection pour apostrophe]]'
	page = Page(site,PageHS)
	if PageHS.find(u'’') != -1:
		Page2 = PageHS.replace(u'’', u'\'')
	elif PageHS.find(u'\'') != -1:
		Page2 = PageHS.replace(u'\'', u'’')
	else:
		return
	page2 = Page(site,Page2)
	if not page.exists() and page2.exists():
		if debogage == True: print u'Création d\'une redirection apostrophe'
		sauvegarde(page, u'#REDIRECT[[' + Page2.replace(u'\n', u'') + u']]', summary)
	elif page.exists() and not page2.exists():
		if debogage == True: print u'Création d\'une redirection apostrophe'
		sauvegarde(page2, u'#REDIRECT[[' + PageHS.replace(u'\n', u'') + u']]', summary)
 
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
'''def crawlerFile(PageCourante):
    PagesHS = open(u'BL.txt', 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': 
			break
		elif PageHS == PageCourante: 
			return "False"
    PagesHS.close()'''
	
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
			modification(HTMLUnicode.HTMLUnicode(PageHS.replace(u'\n',u'')))
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns])
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [ns])
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = ns)
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
	for Page in site.allpages(start=u'', namespace=ns, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=ns,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def log(source):		
	txtfile = codecs.open(output, 'a', 'utf-8')
	txtfile.write(source + u'\n')
	txtfile.close()
	
def filtre(projets,langue,PageHS):
	projets2 = projets[projets.find(langue + u'='):len(projets)]
	if projets2.find(u'\n') == -1:
		return projets[0:projets.find(langue + u'=')] + u'w=' + PageHS
	else:
		return projets[0:projets.find(langue + u'=')] + u'w=' + PageHS + projets[projets.find(langue + u'=')+projets2.find(u'\n'):len(projets)]			

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
TraitementFile = crawlerFile(input)
'''
#Modeles :
TraitementFile = crawlerFile(input)
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementPage = modification(u'Utilisateur:JackBot/test/À faire')
TraitementLiens = crawlerLink(u'Modèle:ko-hanja')
TraitementRecherche = crawlerSearch(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
	TraitementRC = crawlerRC()
'''
#ajouter : python cosmetic_changes.py -lang:"fr" -recentchanges
#défaultsort : http://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial%3AToutes+les+pages&from=%C3%A9&to=&namespace=14
# traiter les liens vers WP ([[ ]] + {{lien|lang=}}) + mai 27, 2010 -> 27 mai 2010 ou 2010-05-27
#(¤|₳|฿|¢|₡|₵|₢|₫|€|ƒ|₣|₲|G€|₭|k€|£|₤|₥|₦|₱|₧|₨|\$|₮|₩|¥|Ƶ|₯|₴|₪|₠|₰)[0-9]+
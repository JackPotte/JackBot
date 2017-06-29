#!/usr/bin/env python
# coding: utf-8
# Ce script patch les catégories

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re
import CleDeTri, html2Unicode		# Faits maison
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
summary = u'[[Wiktionnaire:Prise de décision/Modèles de codes de langue]]'
cat = range(1, 8)
cat[1] = u'[[Catégorie:Wiktionnaire:Étymologies manquantes]]'
cat[2] = u'[[Catégorie:Wiktionnaire:Ébauches à compléter]]'
cat[3] = u'[[Catégorie:Wiktionnaire:Définitions manquantes]]'
cat[4] = u'[[Catégorie:Wiktionnaire:Exemples manquants]]'
cat[5] = u'[[Catégorie:Wiktionnaire:Prononciations manquantes]]'
cat[6] = u'[[Catégorie:Traductions]]'
debogage = False

# Modification du wiki
def modification(PageHS):
	if debogage == True: print PageHS.encode(config.console_encoding, 'replace')
	page = Page(site,PageHS)
	PageEnd = u''
	PageTemp = u''
	if not page.exists(): return
	if page.namespace() != 14: return
	# Remplacement des modèles de langue par leurs noms dans les catégories
	try: PageBegin = page.get()
	except wikipedia.NoPage: return
	except wikipedia.IsRedirectPage: return
	except wikipedia.ServerError: return
	PageTemp = PageBegin
	
	while PageTemp.find(u'{{#ifeq:onom|') != -1:
		if PageTemp.find(u'dun mot en ') > PageTemp.find(u'{{#ifeq:onom|'):
			# [[Catégorie:Mots issus {{#ifeq:onom|es|dune onomatopee|dun mot en {{es}}}}|allemand bas]]
			if PageTemp.find(u'}}}}|') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{#ifeq:onom|')] + u'd’un mot en ' + PageTemp[PageTemp.find(u'dun mot en ')+len(u'dun mot en '):PageTemp.find(u'}}}}|')+2] + PageTemp[PageTemp.find(u'}}}}|')+4:len(PageTemp)]
			else:
				PageTemp = PageTemp[0:PageTemp.find(u'{{#ifeq:onom|')] + u'd’un mot en ' + PageTemp[PageTemp.find(u'dun mot en ')+len(u'dun mot en '):PageTemp.find(u'}}|')] + PageTemp[PageTemp.find(u'}}|')+2:len(PageTemp)]
		elif PageTemp.find(u'd’un mot en ') > PageTemp.find(u'{{#ifeq:onom|'):
			# [[Catégorie:Mots issus {{#ifeq:onom|es|d’une onomatopée|d’un mot en {{es}}}}|{{nds|type=cat}}]]
			if PageTemp.find(u'}}}}|') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{#ifeq:onom|')] + PageTemp[PageTemp.find(u'd’un mot en '):PageTemp.find(u'}}}}|')+2] + PageTemp[PageTemp.find(u'}}}}|')+4:len(PageTemp)]
			else:
				PageTemp = PageTemp[0:PageTemp.find(u'{{#ifeq:onom|')] + PageTemp[PageTemp.find(u'd’un mot en '):PageTemp.find(u'}}|')] + PageTemp[PageTemp.find(u'}}|')+2:len(PageTemp)]
		else:
			break
	while PageTemp.find(u'|type=cat') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|type=cat')] + PageTemp[PageTemp.find(u'|type=cat')+len(u'|type=cat'):len(PageTemp)]
	while PageTemp.find(u'|type=ms') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=ms')]
		PageTemp = PageTemp[0:PageTemp.find(u'|type=ms')] + PageTemp[PageTemp.find(u'|type=ms')+len(u'|type=ms'):len(PageTemp)]
	while PageTemp.find(u'|type=mp') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=mp')]
		PageTemp = PageTemp[0:PageTemp2.rfind(u'{{')] + u'en ' + PageTemp[PageTemp2.rfind(u'{{'):PageTemp.find(u'|type=mp')] + PageTemp[PageTemp.find(u'|type=mp')+len(u'|type=mp'):len(PageTemp)]
	while PageTemp.find(u'|type=fs') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=fs')]
		PageTemp = PageTemp[0:PageTemp2.rfind(u'{{')] + u'en ' + PageTemp[PageTemp2.rfind(u'{{'):PageTemp.find(u'|type=fs')] + PageTemp[PageTemp.find(u'|type=fs')+len(u'|type=fs'):len(PageTemp)]
	while PageTemp.find(u'|type=fp') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=fp')]
		PageTemp = PageTemp[0:PageTemp2.rfind(u'{{')] + u'en ' + PageTemp[PageTemp2.rfind(u'{{'):PageTemp.find(u'|type=fp')] + PageTemp[PageTemp.find(u'|type=fp')+len(u'|type=fp'):len(PageTemp)]	
	while PageTemp.find(u'|type=en nom') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=en nom')]
		PageTemp = PageTemp[0:PageTemp2.rfind(u'{{')] + u'en ' + PageTemp[PageTemp2.rfind(u'{{'):PageTemp.find(u'|type=en nom')] + PageTemp[PageTemp.find(u'|type=en nom')+len(u'|type=en nom'):len(PageTemp)]
	while PageTemp.find(u'|type=du nom') != -1:
		PageTemp2 = PageTemp[0:PageTemp.find(u'|type=du nom')]
		PageTemp = PageTemp[0:PageTemp2.rfind(u'{{')] + u'en ' + PageTemp[PageTemp2.rfind(u'{{'):PageTemp.find(u'|type=du nom')] + PageTemp[PageTemp.find(u'|type=du nom')+len(u'|type=du nom'):len(PageTemp)]
	
	if debogage == True:
		print u'----------------------'
		print u'Recherche des modèles'
	while PageTemp.find(u'{{') != -1:
		PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{')]
		PageTemp = PageTemp[PageTemp.find(u'{{')+2:len(PageTemp)]
		Codelangue = PageTemp[:PageTemp.find(u'}}')]
		if debogage == True: print Codelangue.encode(config.console_encoding, 'replace')
		if len(Codelangue) < 4 or Codelangue[:4] == u'fra-':
			Langue = Page(site, u'Modèle:' + Codelangue)
			if not Langue.exists():
				if debogage == True: print u' Modèle absent'
				return
			if Langue.namespace() != 10:
				if debogage == True: print u' Modèle incorrect'
				return
			try: PageTemp2 = Langue.get()
			except wikipedia.NoPage: return
			except wikipedia.IsRedirectPage: return
			except wikipedia.ServerError: return
			if PageTemp2.find(u'<noinclude>') != -1:
				if debogage == True: print u'  Modèle langue trouvé'
				langue = PageTemp2[0:PageTemp2.find(u'<noinclude>')]
				if PageEnd.rfind(u'|') > PageEnd.rfind(u']]') and PageEnd.rfind(u'|') > PageEnd.rfind(u'}}'):
					PageEnd = PageEnd + CleDeTri.CleDeTri(langue)
				else:
					PageEnd = PageEnd + langue					
			else:
				if debogage == True: print u'  Modèle langue absent'
				PageEnd = PageEnd + u'{{' + PageTemp[0:PageTemp.find(u'}}')+2]
		else:
			PageEnd = PageEnd + u'{{' + PageTemp[0:PageTemp.find(u'}}')+2]
		PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
	PageEnd = PageEnd + PageTemp
	if debogage == True: print u'----------------------'
	
	# Traitement applicable aux modèles et catégories
	PageTemp = PageEnd
	PageEnd = u''
	if PageTemp.find(u'Autres projets') != -1:
		PageEnd = PageTemp[0:PageTemp.find(u'}}')+2]
		PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]	
	if PageTemp.find(u'[[Catégorie:{{MediaWiki:Hidden-category-category}}') != -1:
		PageTemp2 = PageTemp[PageTemp.find(u'[[Catégorie:{{MediaWiki:Hidden-category-category}}'):len(PageTemp)]
		PageTemp = PageTemp[0:PageTemp.find(u'[[Catégorie:{{MediaWiki:Hidden-category-category}}')] + PageTemp[PageTemp.find(u'[[Catégorie:{{MediaWiki:Hidden-category-category}}')+PageTemp2.find(u']]')+2:len(PageTemp)]		
	if PageTemp.find(u'{{clé de tri') != -1:
		PageTemp2 = PageTemp[PageTemp.find(u'{{clé de tri'):len(PageTemp)]
		PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri')] + PageTemp[PageTemp.find(u'{{clé de tri')+PageTemp2.find(u'}}')+2:len(PageTemp)]		
		if PageTemp.find(u'\n}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n}}')+1] + PageTemp[PageTemp.find(u'\n}}')+3:len(PageTemp)]
	if PageTemp.find(u'{{DEFAULTSORT') != -1:
		PageTemp2 = PageTemp[PageTemp.find(u'{{DEFAULTSORT'):len(PageTemp)]
		PageTemp = PageTemp[0:PageTemp.find(u'{{DEFAULTSORT')] + PageTemp[PageTemp.find(u'{{DEFAULTSORT')+PageTemp2.find(u'}}')+2:len(PageTemp)]		
		if PageTemp.find(u'\n}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n}}')+1] + PageTemp[PageTemp.find(u'\n}}')+3:len(PageTemp)]
	if PageTemp.find(u'\n Pron}}') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'\n Pron}}')] + PageTemp[PageTemp.find(u'\n Pron}}')+len(u'\n Pron}}'):len(PageTemp)]
	if PageTemp.find(u'\n Etym}}') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'\n Etym}}')] + PageTemp[PageTemp.find(u'\n Etym}}')+len(u'\n Etym}}'):len(PageTemp)]
	if PageTemp.find(u'\n Defi}}') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'\n Defi}}')] + PageTemp[PageTemp.find(u'\n Defi}}')+len(u'\n Defi}}'):len(PageTemp)]
	while PageTemp.find(u'[[Catégorie:') != -1:
		PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'[[Catégorie:')+len(u'[[Catégorie:')]
		PageTemp = PageTemp[PageTemp.find(u'[[Catégorie:')+len(u'[[Catégorie:'):len(PageTemp)]
		if PageTemp.find(u'|') < PageTemp.find(u']]') and PageTemp.find(u'|') != -1:
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'|')+1] + CleDeTri.CleDeTri(PageTemp[PageTemp.find(u'|')+1:PageTemp.find(u']]')])
			PageTemp = PageTemp[PageTemp.find(u']]'):len(PageTemp)]
	PageEnd = PageEnd + PageTemp
	for p in range(1,7):
		if PageEnd.find(cat[p]) != -1:
			if PageHS.find(u' en '):
				PageEnd = PageEnd[0:PageEnd.find(cat[p])+len(cat[p])-2] + u'|' + CleDeTri.CleDeTri(PageHS[PageHS.find(u' en ')+4:len(PageHS)]) + PageEnd[PageEnd.find(cat[p])+len(cat[p])-2:len(PageEnd)]
			
	PageEnd = html2Unicode.html2Unicode(PageEnd)
	regex = ur'\(code \<tt\>\{\{modl\|([a-z\-]+)\}\}\<\/tt\>\)'
	PageEnd = re.sub(regex, ur'(code <tt>[[\1]]</tt>)', PageEnd)
	if PageEnd != PageBegin: sauvegarde(page, PageEnd, summary)


	'''
	# Clé de catégorie Wiktionnaire
	Adjectifs = range(1, 8)
	Adjectifs[1] = u'moyen'
	Adjectifs[2] = u'vieux'
	Adjectifs[3] = u'ancien'
	Adjectifs[4] = u'haut'
	Adjectifs[5] = u'bas'
	Adjectifs[6] = u'langues'
	for a in range (1,7):
		if PageTitre.find(Adjectifs[a] + u' ') != -1: PageTitre = PageTitre[0:PageTitre.find(Adjectifs[a] + u' ')] + PageTitre[PageTitre.find(Adjectifs[a] + u' ')+len(Adjectifs[a] + u' '):len(PageTitre)] + u' ' + Adjectifs[a]
	return PageTitre
	'''			

def trim(s):
    return s.strip(" \t\n\r\0\x0B")
	
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
	for Page in pagegenerators.PreloadingGenerator(pages,1000):
		modification(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,1000):
			modification(Page.title())

# Traitement des sous-catégories
def crawlerCatCat(category):
	#modification(category.title())
	cat = catlib.Category(site, category)
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		modification(subcategory.title())

# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [14])
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
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [14])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,1000):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,1000):
		modification(Page.title())
		
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
TraitementCatLink = crawlerCatLink(u'Catégorie:Modèles de base de code langue', u'')
#TraitementCategory = crawlerCatCat(u'Catégorie:Espace principal') maximum recursive python depth exceeded
'''
TraitementCatCat = crawlerCatCat(u'Catégorie:Origines étymologiques des mots')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementCatCat = crawlerCatCat(u'Principale')
TraitementLiens = crawlerLink(u'Modèle:fr')
TraitementPage = modification(u'Modèle:aab')
TraitementCategory = crawlerCatCat(u'Catégorie:Lexique en gününa yajich de la zoologie')
TraitementFile = crawlerFile('articles_listed.txt')
while 1:
	TraitementRC = crawlerRC()
'''

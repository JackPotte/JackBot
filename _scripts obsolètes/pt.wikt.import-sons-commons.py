#!/usr/bin/env python
# coding: utf-8
# Ce script importe les sons de Commons

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
siteDest = getSite(u'pt',u'wiktionary')
site = getSite(u'',u'commons')
summary = u'Adição de som, desde [[commons:Category:Pronunciation]]'
debogage = False
ns = 0

# Modification du wiki
def modification(PageHS):
	print(PageHS.encode(config.console_encoding, 'replace'))
	if PageHS[len(PageHS)-len(u'.ogg'):] != u'.ogg': return
	'''page2 = Page(site2,PageHS)
	try:
		PageBegin = page2.get()
	except wikipedia.NoPage: return
	except wikipedia.IsRedirectPage: PageBegin = page2.get(get_redirect=True)'''
	
	mot = PageHS[len(u'File:'):len(PageHS)-len(u'.ogg')]
	if mot.find(u'-') == -1:
		if debogage == True: print u'Son sans langue'
		return
	codelangue = mot[:mot.find(u'-')].lower()
	if debogage == True: u'Mot de code langue : ' + codelangue
	mot = mot[mot.find(u'-')+1:]
	mot = mot.replace(u'-',' ')
	mot = mot.replace(u'_',' ')
	mot = mot.replace(u'\'',u'’')
	if debogage == True: print u'Mot de Commons : ' + mot.encode(config.console_encoding, 'replace')
	region = u''
	
	page1 = Page(siteDest,mot)
	try:
		PageBegin = page1.get()
	except wikipedia.NoPage:
		# Retrait d'un éventuel article ou une région dans le nom du fichier
		mot1 = mot
		if codelangue == u'fr':
			if mot[0:3] == u'le ' or mot[0:3] == u'la ' or mot[0:4] == u'les ' or mot[0:3] == u'un ' or mot[0:3] == u'une ' or mot[0:4] == u'des ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'ca ' or mot[0:3] == u'be ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'en':
			if mot[0:4] == u'the ' or mot[0:2] == u'a ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'us ' or mot[0:3] == u'uk ' or mot[0:3] == u'ca ' or mot[0:3] == u'au ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'de':
			if mot[0:4] == u'der ' or mot[0:4] == u'die ' or mot[0:4] == u'das ' or mot[0:4] == u'den ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'at ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'es':
			if mot[0:3] == u'el ' or mot[0:3] == u'lo ' or mot[0:3] == u'la ' or mot[0:3] == u'un ' or mot[0:4] == u'uno ' or mot[0:4] == u'una ' or mot[0:5] == u'unos ' or mot[0:5] == u'unas ' or mot[0:4] == u'los ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'mx ' or mot[0:3] == u'ar ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
			if mot[0:7] == u'am lat ':
				region = u'{{AM|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'it':
			if mot[0:3] == u'lo ' or mot[0:3] == u'la ' or mot[0:3] == u'le ' or mot[0:4] == u'gli ' or mot[0:3] == u'un ' or mot[0:4] == u'uno ' or mot[0:4] == u'una ':
				mot = mot[mot.find(u' ')+1:]
			
		elif codelangue == u'pt':
			if mot[0:2] == u'a ' or mot[0:2] == u'o ' or mot[0:3] == u'as ' or mot[0:3] == u'os ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'br ' or mot[0:3] == u'pt ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
		
		elif codelangue == u'nl':
			if mot[0:3] == u'de ' or mot[0:4] == u'een ' or mot[0:4] == u'het ':
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'sv':
			if mot[0:3] == u'en ' or mot[0:4] == u'ett ':
				mot = mot[mot.find(u' ')+1:]				
	
		if debogage == True: print u'Mot potentiel : ' + mot.encode(config.console_encoding, 'replace')
		
		# Deuxième tentative de recherche sur le Wiktionnaire	
		if mot != mot1:
			page1 = Page(siteDest,mot)
			try:
				PageBegin = page1.get()
			except wikipedia.NoPage:
				if debogage == True: print u'Page introuvable 1'
				return
			except wikipedia.IsRedirectPage:
				PageBegin = page1.get(get_redirect=True)
		else:
			if debogage == True: print u'Page introuvable 2'
			return
	except wikipedia.IsRedirectPage:
		PageBegin = page1.get(get_redirect=True)
		
	if debogage == True: print u'Mot du Wiktionnaire : ' + mot.encode(config.console_encoding, 'replace')
	if PageBegin.find(PageHS[len(u'File:'):]) != -1 or PageBegin.find(PageHS[len(u'File:'):][:1].lower() + PageHS[len(u'File:'):][1:]) != -1 or PageBegin.find(PageHS[len(u'File:'):].replace(u' ', u'_')) != -1 or PageBegin.find((PageHS[len(u'File:'):][:1].lower() + PageHS[len(u'File:'):][1:]).replace(u' ', u'_')) != -1:
		if debogage == True: print u'Son existant'
		return
	if PageBegin.find(u'{{langue|' + codelangue) == -1:
		if debogage == True: print u'Paragraphe absent'
		return
	
	PageTemp = PageBegin
	PageEnd = PageTemp[:PageTemp.find(u'{{langue|' + codelangue)+len(u'{{langue|' + codelangue)]
	PageTemp = PageTemp[PageTemp.find(u'{{langue|' + codelangue)+len(u'{{langue|' + codelangue):len(PageTemp)]
	if debogage == True: print u'Ajout du son...'
	if PageTemp.find(u'{{pronúncia') != -1 and ((PageTemp.find(u'{{pronúncia') < PageTemp.find(u'\n={{-') or PageTemp.find(u'\n={{-') == -1)):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-pron-}}')+len(u'{{-pron-}}')]
		PageTemp = u'\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n' + PageTemp[PageTemp.find(u'{{-pron-}}')+len(u'{{-pron-}}'):]
	elif PageTemp.find(u'{{-homo-}}') != -1 and (PageTemp.find(u'{{-homo-}}') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-homo-}}')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n' + PageTemp[PageTemp.find(u'{{-homo-}}'):]
	elif PageTemp.find(u'{{-anagr-}}') != -1 and (PageTemp.find(u'{{-anagr-}}') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-anagr-}}')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n' + PageTemp[PageTemp.find(u'{{-anagr-}}'):]
	elif PageTemp.find(u'{{-voir-}}') != -1 and (PageTemp.find(u'{{-voir-}}') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-voir-}}')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n' + PageTemp[PageTemp.find(u'{{-voir-}}'):]
	elif PageTemp.find(u'{{-réf-}}') != -1 and (PageTemp.find(u'{{-réf-}}') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-réf-}}')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n' + PageTemp[PageTemp.find(u'{{-réf-}}'):]
	elif PageTemp.find(u'{{-ref-}}') != -1 and (PageTemp.find(u'{{-ref-}}') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{-ref-}}')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n' + PageTemp[PageTemp.find(u'{{-ref-}}'):]
	elif PageTemp.find(u'[[Catégorie:') != -1 and (PageTemp.find(u'[[Catégorie:') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[Catégorie:')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n\n' + PageTemp[PageTemp.find(u'[[Catégorie:'):]
	elif PageTemp.find(u'{{clé de tri') != -1 and (PageTemp.find(u'{{clé de tri') < PageTemp.find(u'{{langue') or PageTemp.find(u'{{langue') == -1):
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{clé de tri')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n\n' + PageTemp[PageTemp.find(u'{{clé de tri'):]
	elif PageTemp.find(u'{{langue|') != -1:
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{langue|')]
		PageTemp = u'{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}\n\n\n' + PageEnd[PageEnd.rfind(u'\n'):] + PageTemp[PageTemp.find(u'{{langue|'):]
		PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
	elif PageTemp.find(u'[[en:') != -1:
		if debogage == True: print u' avant interwikis'
		PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[en:')]
		PageTemp = PageTemp[PageTemp.find(u'[[en:'):]
		PageEnd = PageEnd[:PageEnd.rfind(u'\n\n')] + u'\n\n{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}' + PageEnd[PageEnd.rfind(u'\n\n'):]
		PageTemp = PageEnd[PageEnd.rfind(u'{{pron-rég'):] + PageTemp
		PageEnd = PageEnd[:PageEnd.rfind(u'{{pron-rég')]
	else:
		if debogage == True: print u' en fin de page'
		PageTemp = PageTemp + u'\n\n{{-pron-}}\n* {{pron-rég|' + region + u'|audio=' + PageHS[5:] + u'}}'
	#if debogage == True: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
	
	# Suppression de la ligne blanche éventuelle dans le paragraphe du modèle
	PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{pron-rég|')]
	PageTemp = PageTemp[PageTemp.find(u'{{pron-rég|'):]
	if PageTemp.find(u'\n\n') != -1 and (PageTemp.find(u'\n') == PageTemp.find(u'\n\n*{{pron') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n* {{pron') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n{{ébauche-pron') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n*{{CA|') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n*{{US') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n*{{UK') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n* {{CA|') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n* {{US') or PageTemp.find(u'\n') == PageTemp.find(u'\n\n* {{UK')):
		PageTemp = PageTemp[:PageTemp.find(u'\n\n')] + PageTemp[PageTemp.find(u'\n\n')+1:]
	
	PageEnd = PageEnd + PageTemp
	# Sauvegarde
	if PageEnd != PageBegin: sauvegarde(page1, PageEnd, summary)
		

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
			modification(PageHS)
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category, recursif, apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) HS sur Commons
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
		for subcategory in subcat:
			if subcategory.title().find(u'.ogg') == -1 and subcategory.title().find(u'spoken') == -1 and subcategory.title().find(u'Wikipedia') == -1 and subcategory.title().find(u'Wikinews') == -1:
				pages = subcategory.articlesList(False)
				for Page in pagegenerators.PreloadingGenerator(pages,100):
					modification(Page.title())
						
# Traitement des pages liées
def crawlerLink(pagename, apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
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
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
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
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

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
	#print(Contenu.encode(config.console_encoding, 'replace'))	#[len(Contenu)-2000:len(Contenu)]) #
	#result = raw_input("Sauvegarder ? (o/n) ")
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
TraitementCategory = crawlerCat(u'Category:Pronunciation‎', True, u'')
'''
TraitementPage = modification(u'File:En-us-Boolean.ogg')
TraitementFile = crawlerFile('articles_list.txt')
TraitementLiens = crawlerLink(u'Modèle:ko-hanja')
TraitementRecherche = crawlerSearch(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
	TraitementRC = crawlerRC()
'''
# pb avec crawlercat non récursif Commons + ignorer [[Category:Ogg sound files of spoken French]] ou Wikinews, Wikipedia
# dump : rechercher les erreurs de paragraphes
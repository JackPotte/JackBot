#!/usr/bin/env python
# coding: utf-8
# Ce script importe les sons de Commons

# Importation des modules
from __future__ import absolute_import, unicode_literals
import pywikibot
from pywikibot import *
import re, sys

# Déclaration
mynick = u'JackBot'
siteDest = pywikibot.Site(u'fr',u'wiktionary')
site = pywikibot.Site(u'commons',u'commons')
summary = u'Ajout du son depuis [[commons:Category:Pronunciation]]'
debug = 0

Sections = []
Niveau = []
Sections.append(u'étymologie')
Niveau.append(u'===')
Sections.append(u'nom')
Niveau.append(u'===')
Sections.append(u'variantes orthographiques')
Niveau.append(u'====')
Sections.append(u'synonymes')
Niveau.append(u'====')
Sections.append(u'antonymes')
Niveau.append(u'====')
Sections.append(u'dérivés')
Niveau.append(u'====')
Sections.append(u'apparentés')
Niveau.append(u'====')
Sections.append(u'vocabulaire')
Niveau.append(u'====')
Sections.append(u'hyperonymes')
Niveau.append(u'====')
Sections.append(u'hyponymes')
Niveau.append(u'====')
Sections.append(u'méronymes')
Niveau.append(u'====')
Sections.append(u'holonymes')
Niveau.append(u'====')
Sections.append(u'traductions')
Niveau.append(u'====')
Sections.append(u'prononciation')
Niveau.append(u'===')
Sections.append(u'homophones')
Niveau.append(u'====')
Sections.append(u'paronymes')
Niveau.append(u'====')
Sections.append(u'anagrammes')
Niveau.append(u'===')
Sections.append(u'voir aussi')
Niveau.append(u'===')
Sections.append(u'références')
Niveau.append(u'===')
Sections.append(u'catégorie')
Niveau.append(u'')
Sections.append(u'clé de tri')
Niveau.append(u'')

# Modification du wiki
def modification(PageHS):
	print(PageHS.encode(config.console_encoding, 'replace'))
	if PageHS[-4:] != u'.ogg' and PageHS[-4:] != u'.oga' and PageHS[-4:] != u'.wav': return

	mot = PageHS[len(u'File:'):len(PageHS)-4]
	if mot.find(u'-') == -1:
		if debug > 0: print u'Son sans langue'
		return
	codelangue = mot[:mot.find(u'-')].lower()
	if debug > 0: u'Mot de code langue : ' + codelangue
	mot = mot[mot.find(u'-')+1:]
	mot = mot.replace(u'-',' ')
	mot = mot.replace(u'_',' ')
	mot = mot.replace(u'\'',u'’')
	if debug > 1: print u'Mot de Commons : ' + mot.encode(config.console_encoding, 'replace')
	region = u''
	
	page1 = Page(siteDest,mot)
	try:
		PageBegin = page1.get()
	except pywikibot.exceptions.NoPage:
		# Retrait d'un éventuel article ou une région dans le nom du fichier
		mot1 = mot
				
		if codelangue == u'de':
			if mot[0:4] == u'der ' or mot[0:4] == u'die ' or mot[0:4] == u'das ' or mot[0:4] == u'den ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'at ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'en':
			if mot[0:4] == u'the ' or mot[0:2] == u'a ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'au ' or mot[0:3] == u'gb ' or mot[0:3] == u'ca ' or mot[0:3] == u'uk ' or mot[0:3] == u'us ':
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
				
		elif codelangue == u'fr':
			if mot[:3] == u'le ' or mot[:3] == u'la ' or mot[:4] == u'les ' or mot[:3] == u'un ' or mot[:3] == u'une ' or mot[:4] == u'des ':
				mot = mot[mot.find(u' ')+1:]
			if mot[:3] == u'ca ' or mot[:3] == u'be ':
				region = u'{{' + mot[:2].upper() + u'|nocat=1}}'
				mot = mot[mot.find(u' ')+1:]
			if mot[:6] == u'Paris ':
				region = u'Paris (France)'
				mot = mot[mot.find(u' ')+1:]
				
		elif codelangue == u'it':
			if mot[0:3] == u"l'" or mot[0:3] == u'la ' or mot[0:3] == u'le ' or mot[0:3] == u'lo ' or mot[0:4] == u'gli ' or mot[0:3] == u'un ' or mot[0:4] == u'uno ' or mot[0:4] == u'una ':
				mot = mot[mot.find(u' ')+1:]
		
		elif codelangue == u'nl':
			if mot[0:3] == u'de ' or mot[0:4] == u'een ' or mot[0:4] == u'het ':
				mot = mot[mot.find(u' ')+1:]
							
		elif codelangue == u'pt':
			if mot[0:2] == u'a ' or mot[0:2] == u'o ' or mot[0:3] == u'as ' or mot[0:3] == u'os ':
				mot = mot[mot.find(u' ')+1:]
			if mot[0:3] == u'br ' or mot[0:3] == u'pt ':
				region = u'{{' + mot[0:2].upper() + u'|nocat=1}}'

		elif codelangue == u'sv':
			if mot[0:3] == u'en ' or mot[0:4] == u'ett ':
				mot = mot[mot.find(u' ')+1:]				
		
		if debug > 1: print u'Mot potentiel : ' + mot.encode(config.console_encoding, 'replace')
		# Deuxième tentative de recherche sur le Wiktionnaire	
		if mot != mot1:
			page1 = Page(siteDest,mot)
			try:
				PageBegin = page1.get()
			except pywikibot.exceptions.NoPage:
				if debug > 0: print u'Page introuvable 1'
				return
			except pywikibot.exceptions.IsRedirectPage:
				PageBegin = page1.get(get_redirect=True)
		else:
			if debug > 0: print u'Page introuvable 2'
			return
	except pywikibot.exceptions.IsRedirectPage:
		PageBegin = page1.get(get_redirect=True)
	# à faire : 3e tentative en retirant les suffixes numériques (ex : File:De-aber2.ogg)

	regex = ur'{{pron\|[^\}|]*\|' + codelangue + u'}}'
	if re.compile(regex).search(PageBegin):
		prononciation = PageBegin[re.search(regex,PageBegin).start()+len(u'{{pron|'):re.search(regex,PageBegin).end()-len(u'|'+codelangue+u'}}')]
	else:
		prononciation = u''
	if debug > 1: print prononciation.encode(config.console_encoding, 'replace')
	
	if debug > 1: print u'Mot du Wiktionnaire : ' + mot.encode(config.console_encoding, 'replace')
	Son = PageHS[len(u'File:'):]
	if PageBegin.find(Son) != -1 or PageBegin.find(Son[:1].lower() + Son[1:]) != -1 or PageBegin.find(Son.replace(u' ', u'_')) != -1 or PageBegin.find((Son[:1].lower() + Son[1:]).replace(u' ', u'_')) != -1:
		if debug > 0: print u'Son déjà présent'
		return
	if PageBegin.find(u'{{langue|' + codelangue) == -1:
		if debug > 0: print u'Paragraphe absent'
		return
	PageTemp = PageBegin

	PageEnd = addLine(PageTemp, codelangue, u'prononciation', u'* {{écouter|' + region + u'|' + prononciation + u'|lang=' + codelangue + u'|audio=' + Son + u'}}')

	# Sauvegarde
	if PageEnd != PageBegin: sauvegarde(page1, PageEnd, summary)


def addLine(Page, CodeLangue, Section, Contenu):
	if debug > 0:
		print u'addLine()'
	if debug > 1:
		print CodeLangue
		print Section
		print Contenu
	if Page != '' and CodeLangue != '' and Section != '' and Contenu != '':
		if Page.find(Contenu) == -1 and Page.find(u'{{langue|' + CodeLangue + u'}}') != -1:
			if Section == u'catégorie' and Contenu.find(u'[[Catégorie:') == -1: Contenu = u'[[Catégorie:' + Contenu + u']]'
			if Section == u'clé de tri' and Contenu.find(u'{{clé de tri|') == -1: Contenu = u'{{clé de tri|' + Contenu + u'}}'
			
			# Recherche de l'ordre théorique de la section à ajouter
			NumSection = numeroSection(Section)
			if NumSection == len(Sections):
				if debug > 0:
					print u''
					print u' ajout de '
					print Section.encode(config.console_encoding, 'replace')
					print u' dans une section inconnue'
					print u' (car ' + len(Sections) + u' = ' + str(NumSection) + u')'
					print u''
				return Page
			if debug > 1: print u' position S : ' + s
			
			# Recherche de l'ordre réel de la section à ajouter
			PageTemp2 = Page[Page.find(u'{{langue|' + CodeLangue + u'}}')+len(u'{{langue|' + CodeLangue + u'}}'):]
			#SectionPage = re.findall("{{S\|([^}]+)}}", PageTemp2) # Mais il faut trouver le {{langue}} de la limite de fin
			SectionPage = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", PageTemp2)
			if debug > 1:
				o = 0
				while o < len(SectionPage):
					 print str(SectionPage[o]).encode(config.console_encoding, 'replace')
					 o = o + 1
				if o == len(SectionPage): o = o - 1
				raw_input()

			o = 0
			if len(SectionPage[o]) > 0:
				# pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
				#while o < len(SectionPage) and str(SectionPage[o][0].encode(config.console_encoding, 'replace')) != 'langue' and numeroSection(SectionPage[o][0]) <= NumSection:

				if debug > 0: print u' sections de la page :'
				while o < len(SectionPage) and SectionPage[o][0] != u'langue' and numeroSection(SectionPage[o][0]) <= NumSection:
					if debug > 0: print u'  ' + SectionPage[o][0] + u'  ' + str(numeroSection(SectionPage[o][0]))
					o = o + 1
				o = o - 1
				if debug > 1: print u' position O : ' + o

				if debug > 0:
					print u'Ajout de : ' + Section.encode(config.console_encoding, 'replace')
					if o == len(SectionPage) -1:
						print u' après '
						print SectionPage[o][0]
						print u' (car ' + str(numeroSection(SectionPage[o][0])) + u' < ' + str(NumSection) + u')'
					else:
						print u' avant '
						print SectionPage[o][0]
						print u' (car ' + str(numeroSection(SectionPage[o][0])) + u' > ' + str(NumSection) + u')'
					print u''

				# Ajout après la section trouvée
				if PageTemp2.find(u'{{S|' + SectionPage[o][0]) == -1:
					print 'Erreur d\'encodage'
					return

				PageTemp3 = PageTemp2[PageTemp2.find(u'{{S|' + SectionPage[o][0]):]
				if SectionPage[o][0] != Section and Section != u'catégorie' and Section != u'clé de tri':
					if debug > 1: print u' ajout de la section'
					Contenu = u'\n' + Niveau[NumSection] + u' {{S|' + Section + u'}} ' + Niveau[NumSection] + u'\n' + Contenu

				# Ajout à la ligne
				if PageTemp3.find(u'\n==') == -1:
					categories = Page.find(u'\n[[Catégorie:')
					defaultSort = Page.find(u'\n{{clé de tri|')
					if categories != -1 and (categories < defaultSort or defaultSort == -1):
						if debug > 0: print u' ajout avant les catégories'
						Page = Page[:Page.find(u'\n[[Catégorie:')] + Contenu + u'\n' + Page[Page.find(u'\n[[Catégorie:'):]
					elif defaultSort != -1:
						if debug > 0: print u' ajout avant la clé de tri'
						Page = Page[:Page.find(u'\n{{clé de tri|')] + Contenu + Page[Page.find(u'\n{{clé de tri|'):]
					else:
						if debug > 0: print u' ajout en fin de page'
						Page = Page + Contenu
				else:
					if debug > 0: print u' ajout avant pochaine langue'
					Page = Page[:-len(PageTemp2)] + PageTemp2[:-len(PageTemp3)] + PageTemp3[:PageTemp3.find(u'\n==')] + Contenu + u'\n\n' + PageTemp3[PageTemp3.find(u'\n=='):]
				Page = Page.replace(u'\n\n\n', u'\n\n')
	return Page
	
def numeroSection(Section):
	if debug > 0: print u'numeroSection()'
	if debug > 1:
		print u''
		print Section
		print Sections[0]
		raw_input(Section == Sections[0])
	#UnicodeDecodeError: 'ascii' codec can't decode byte 0x82 in position 1: ordinal not in range(128)
	#if isinstance(Section, str): Section = Section
	#if isinstance(Section, str): Section = Section.encode(config.console_encoding, 'replace')
	#if isinstance(Section, str): Section = Section.encode('utf-8')
	#if isinstance(Section, str): Section = Section.decode('ascii')
	#if isinstance(Section, str): Section = Section.decode('ascii').encode(config.console_encoding, 'replace')
	#if isinstance(Section, str): Section = Section.decode('ascii').encode('utf-8')
	#if isinstance(Section, str): Section = unicode(Section)
	#if isinstance(Section, unicode): Section = Section.decode("utf-8")
	
	s = 0
	while s < len(Sections) and Section != Sections[s]:
		s = s + 1
	if s >= len(Sections):
		if debug > 0: print u' ' + Section + u' non trouvé'
		s = 1	# pour éviter de lister les natures grammaticales
	if debug > 1:
		print u''
		print Section
		print u' = ' + str(s)
		print u''
	return s
		
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

def crawlerCat2(category, recursif, apres):
	import pywikibot
	from pywikibot import pagegenerators
	modifier = u'False'
	cat = pywikibot.Category(site, category)	# 'module' object has no attribute 'Category'
	gen =  pagegenerators.CategorizedPageGenerator(cat)
	for Page in gen:
		modification(Page.title())
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
	page = pywikibot.Page(site, pagename)
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
		page = pywikibot.Page(site, Page.title())
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
	gen = pagegenerators.SearchPageGenerator(pagename, site=site, namespaces=6)
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
		except pywikibot.exceptions.NoPage: return
		except pywikibot.exceptions.IsRedirectPage: return
		except pywikibot.exceptions.LockedPage: return
		except pywikibot.exceptions.ServerError: return
		except pywikibot.exceptions.BadTitle: return
		except pywikibot.EditConflict: return
		if PageTemp != u"{{/Stop}}":
			pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
			exit(0)

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debug > 0:
		if len(Contenu) < 6000:
			print(Contenu.encode(config.console_encoding, 'replace'))
		else:
			taille = 3000
			print(Contenu[:taille].encode(config.console_encoding, 'replace'))
			print u'\n[...]\n'
			print(Contenu[len(Contenu)-taille:].encode(config.console_encoding, 'replace'))
		result = raw_input((u'Sauvegarder [['+PageCourante.title()+u']] ? (o/n) ').encode('utf-8'))
	if result != "n" and result != "no" and result != "non":
		if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
		if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
		try:
			PageCourante.put(Contenu, summary)
		except pywikibot.exceptions.NoPage: 
			print "NoPage en sauvegarde"
			return
		except pywikibot.exceptions.IsRedirectPage: 
			print "IsRedirectPage en sauvegarde"
			return
		except pywikibot.exceptions.LockedPage: 
			print "LockedPage en sauvegarde"
			return
		except pywikibot.EditConflict: 
			print "EditConflict en sauvegarde"
			return
		except pywikibot.exceptions.ServerError: 
			print "ServerError en sauvegarde"
			return
		except pywikibot.exceptions.BadTitle: 
			print "BadTitle en sauvegarde"
			return
		except AttributeError:
			print "AttributeError en sauvegarde"
			return
			
def testAdd(PageHS):
	page1 = Page(siteDest,PageHS)
	try:
		PageBegin = page1.get()
	except pywikibot.exceptions.NoPage:
		print 'NoPage'
	PageEnd = PageBegin
	codelangue = u'fr'
	
	PageEnd = addLine(PageEnd, codelangue, u'prononciation', u'* {{écouter|||lang=fr|audio=test.ogg}}')
	PageEnd = addLine(PageEnd, codelangue, u'prononciation', u'* {{écouter|||lang=fr|audio=test2.ogg}}')
	PageEnd = addLine(PageEnd, codelangue, u'catégorie', u'Tests en français')
	PageEnd = addLine(PageEnd, codelangue, u'catégorie', u'[[Catégorie:Tests en français]]')
	PageEnd = addLine(PageEnd, codelangue, u'clé de tri', u'test')
	PageEnd = addLine(PageEnd, codelangue, u'étymologie', u':{{étyl|test|fr}}')
	if debug > 1: raw_input(u'Fin')
	if PageEnd != PageBegin: sauvegarde(page1, PageEnd, summary)


debug = 0
# Lancement
if len(sys.argv) > 1:
	DebutScan = u''
	if len(sys.argv) > 2:
		if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
			debug = 1
		else:
			DebutScan = sys.argv[2]
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'ta':
		TraitementPage = testAdd(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'p':
		TraitementPage = modification(u'File:De-Dominikanische Republik.ogg')
	elif sys.argv[1] == u'cat':
		TraitementCategory = crawlerCat2(u'Category:Pronunciation‎', True, u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:vx',u'')
	elif sys.argv[1] == u'page':
		TraitementPage = modification(u'Utilisateur:JackPotte/test2')
	elif sys.argv[1] == u'trad':
		TraitementLiens = crawlerLink(u'Modèle:trad-',u'')
	elif sys.argv[1] == u's':
		TraitementRecherche = crawlerSearch(u'File:fr-Paris--')	# à faire : renommer les "File:Fr-œsophagienne-fr FR-Paris.ogg" avec "{{rename|Fr-Paris--œsophagienne.ogg|4|Pronunciation norm for Wiktionaries sync}}"
	elif sys.argv[1] == u'u':
		crawlerUser(u'Utilisateur:JackPotte', 1000,u'')
else:
	TraitementCategory = crawlerCat2(u'Category:Pronunciation', True, u'')

'''
	TraitementCategory = crawlerCat2(u'Category:U.S. English pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:German pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Arabic pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Armenian pronunciation‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Belarusian pronunciation‎‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Chinese pronunciation‎‎‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Czech pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Hungarian pronunciation‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Swedish pronunciation‎‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Ukrainian pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Russian pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Polish pronunciation‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Dutch pronunciation‎‎‎‎‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:French pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:Spanish pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:English pronunciation‎', True, u'')
	TraitementCategory = crawlerCat2(u'Category:British English pronunciation‎', True, u'')

 à faire :
	Insérer avant les clés de tri : https://fr.wiktionary.org/w/index.php?title=Orthop%C3%A4de&diff=prev&oldid=21702612
	pb avec crawlercat non récursif Commons (test l 333). Ex : ne traite que les "a*" de [[Catégorie:French pronunciations]]
	try save except service unavailable, wait
	niveau de récursivité limite
	ignorer [[Category:Ogg sound files of spoken French]] ou Wikinews, Wikipedia

python pwb.py JackBot/fr.wikt.import-sons-commons
'''

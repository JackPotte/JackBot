#!/usr/bin/env python
# coding: utf-8
'''
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le labs Wikimedia :
1) Retire certains doublons de modèles et d'espaces.
2) Ajoute les clés de tris, prononciations vides, et certains liens vers les conjugaisons.
3) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
4) Ajoute les codes langues appropriés dans les modèles du Wiktionnaire du namespace 0 et paragraphes appropriés (dont "nocat=1" si une catégorie le justifie).
5) Complète les flexions de verbes en français à vérifier.
6) Gère des modèles {{voir}} en début de page.
7) Ajoute les anagrammes (pour les petits mots)
8) Teste les URL et indique si elles sont brisées avec {{lien brisé}}, et les transforme en modèle s'il existe pour leur site
9) Remplace les modèles catégorisés comme obsolètes
10) Créer des liens absents : http://fr.wiktionary.org/w/index.php?title=radiateur&diff=prev&oldid=14443668
11) Détecte les modèles à ajouter : http://fr.wiktionary.org/w/index.php?title=cl%C3%A9&diff=prev&oldid=14443625
12) Crée les redirection d'apostrophe dactylographique vers apostrophe typographique
Testé ici : http://fr.wiktionary.org/w/index.php?title=Utilisateur%3AJackBot%2Ftest&diff=14533806&oldid=14533695
'''

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re, collections, socket, langues
import hyperlynx, CleDeTri, html2Unicode		# Faits maison
from wikipedia import *
''' Bug des n° de lignes auto
from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print str(frameinfo.lineno)
'''

# Déclaration
language = "en"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
debogage = False
debogageLent = False

# Modification du wiki
def modification(PageHS):
	#PageHS = u'Catégorie:'+PageHS[:1].upper()+PageHS[1:]
	summary = u'[[User_talk:Chuck_Entz#Category:Java_programming_language_and_Category:en:Java_programming_language|Category Java without {{context}}]]'
	if debogage: print u'------------------------------------'
	print(PageHS.encode(config.console_encoding, 'replace'))
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() !=0 and page.namespace() != 100 and page.namespace() != 12 and page.namespace() != 14 and PageHS.find(u'Utilisateur:JackBot/') == -1:
			print u'Page non traitée l 47'
			return
		else:
			try:
				PageBegin = page.get()
			except wikipedia.NoPage:
				print u'NoPage l 53'
				return
			except wikipedia.IsRedirectPage: 
				print u'IsRedirect l 56'
				return
	else:
		print u'NoPage l 59'
		return
	PageTemp = PageBegin
	
	if page.namespace() == 0 or PageHS.find(u'Utilisateur:JackBot/') != -1:
		PageTemp = addCat(PageTemp, u'English', u'en:Java programming language')
	if debogage: print (u'--------------------------------------------------------------------------------------------')
	PageEnd = PageTemp
	
	if PageEnd != PageBegin:
		# Modifications mineures, ne justifiant pas une édition à elles seules
		PageEnd = PageEnd.replace(u'  ', u' ')
		PageEnd = PageEnd.replace(u'\n\n\n\n', u'\n\n\n')
		PageEnd = PageEnd.replace(u'.\n=', u'.\n\n=')
		sauvegarde(page,PageEnd, summary)
	elif debogage:
		print "Aucun changement"
		

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def addCat(PageTemp, lang, cat):
	if lang != u'':
		if PageTemp.find(cat) == -1 and PageTemp.find(u'==' + lang + u'==\n') != -1:
			if cat.find(u'[[Category:') == -1: cat = u'[[Category:' + cat + u']]'
			DebutSection = PageTemp.find(u'==' + lang + u'==\n')+len(u'==' + lang + u'==\n')
			PageTemp2 = PageTemp[DebutSection:]
			regex = ur'\n----'
			if re.compile(regex).search(PageTemp2):
				if debogage: print u' catégorie ajoutée avant la section langue suivante'	
				try:
					PageTemp = PageTemp[:DebutSection+re.search(regex,PageTemp2).start()] + cat + u'\n' + PageTemp[DebutSection+re.search(regex,PageTemp2).start():]
				except:
					print u'pb regex interwiki'
			else:
				regex = ur'\n==[A-Z]'
				if re.compile(regex).search(PageTemp2):
					if debogage: print u' catégorie ajoutée avant la section langue suivante'	
					try:
						PageTemp = PageTemp[:DebutSection+re.search(regex,PageTemp2).start()] + cat + u'\n' + PageTemp[DebutSection+re.search(regex,PageTemp2).start():]
					except:
						print u'pb regex interwiki'
				else:
					if debogage: print u' catégorie ajoutée avant les interwikis'
					regex = ur'\n\[\[\w?\w?\w?:'
					if re.compile(regex).search(PageTemp):
						try:
							PageTemp = PageTemp[:re.search(regex,PageTemp).start()] + u'\n' + cat + u'\n' + PageTemp[re.search(regex,PageTemp).start():]
						except:
							print u'pb regex interwiki'
					else:
						if debogage: print u' catégorie ajoutée en fin de page'
						PageTemp = PageTemp + u'\n' + cat
		elif debogage:
			print u'Aucune section dans la langue de la catégorie'
	elif debogage:
		print u'Aucune langue précisée'
	return PageTemp

def rec_anagram(counter):
	# Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1
def anagram(word):
    return rec_anagram(collections.Counter(word))
	
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
			# Conversion ASCII => Unicode (pour les .txt)
			modification(html2Unicode.html2Unicode(PageHS))
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
	#for Page in pagegenerators.PreloadingGenerator(gen,100):
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
	gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC_last_day(site=site, nobots=True, namespace='0'):
    # Génère les modifications récentes de la dernière journée
	ecart_last_edit = 30 # minutes
	
	date_now = datetime.datetime.utcnow()
	# Date de la plus récente modification à récupérer
	date_start = date_now - datetime.timedelta(minutes=ecart_last_edit)
	# Date d'un jour plus tôt
	date_end = date_start - datetime.timedelta(1)
	
	start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
	end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

	for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
					rcdir='older', rctype='edit|new', namespace=namespace,
					includeredirects=True, repeat=False, user=None,
					returndict=False, nobots=nobots):
		yield item[0]
		
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator(site = site)
	ecart_minimal_requis = 30 # min
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print str(ecart_last_edit(Page)) + ' =? ' + str(ecart_minimal_requis)
		if ecart_last_edit(Page) > ecart_minimal_requis:
			modification(Page.title())

def ecart_last_edit(page):
	# Timestamp au format MediaWiki de la dernière version
	time_last_edit = page.getVersionHistory()[0][1]
	match_time = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', time_last_edit)
	# Mise au format "datetime" du timestamp de la dernière version
	datetime_last_edit = datetime.datetime(int(match_time.group(1)), int(match_time.group(2)), int(match_time.group(3)),
		int(match_time.group(4)), int(match_time.group(5)), int(match_time.group(6)))
	datetime_now = datetime.datetime.utcnow()
	diff_last_edit_time = datetime_now - datetime_last_edit
 
	# Ecart en minutes entre l'horodotage actuelle et l'horodotage de la dernière version
	return diff_last_edit_time.seconds/60 + diff_last_edit_time.days*24*60
	
# Traitement des modifications d'un compte
def crawlerUser(username,jusqua):
	compteur = 0
	gen = pagegenerators.UserContributionsGenerator(username, site = site)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
		compteur = compteur + 1
		if compteur > jusqua: break

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False, site = site)
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
			except wikipedia.ServerError: return
			except wikipedia.BadTitle: return
			if PageTemp != u"{{/Stop}}":
				pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
				exit(0)

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage:
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
if len(sys.argv) > 1:
	if len(sys.argv) > 2:
		DebutScan = sys.argv[2]
	else:
		DebutScan = u''
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'txt': 
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
	elif sys.argv[1] == u'txt2':
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'2.txt')
	elif sys.argv[1] == u'm':
		TraitementLiens = crawlerLink(u'Modèle:localités',u'')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Lexique en français de la géographie',False,DebutScan)
		#TraitementCategorie = crawlerCat(u'Catégorie:Genres manquants en français',False,u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:conj-pl',u'')
	elif sys.argv[1] == u'page':
		TraitementPage = modification(u'écran brillant')
		TraitementPage = modification(u'écran de veille')
		TraitementPage = modification(u'écran mat')
	elif sys.argv[1] == u's':
		TraitementRecherche = crawlerSearch(u'"source à préciser"')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	# Quotidiennement :
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Terminologie sans langue précisée',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Flexions à vérifier',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Ébauches à compléter',False,u'')
	TraitementLiens = crawlerLink(u'Modèle:trad',u'')
	TraitementLiens = crawlerLink(u'Modèle:1ergroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:2egroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:3egroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:-',u'')
	TraitementLiens = crawlerLink(u'Modèle:-ortho-alt-',u'')
	TraitementLiens = crawlerLink(u'Modèle:mascul',u'')
	TraitementLiens = crawlerLink(u'Modèle:fémin',u'')
	TraitementLiens = crawlerLink(u'Modèle:femin',u'')
	TraitementLiens = crawlerLink(u'Modèle:sing',u'')
	TraitementLiens = crawlerLink(u'Modèle:plur',u'')
	TraitementLiens = crawlerLink(u'Modèle:pluri',u'')
	TraitementLiens = crawlerLink(u'Modèle:=langue=',u'')
	TraitementLiens = crawlerLink(u'Modèle:-déf-',u'')
	TraitementLiens = crawlerLink(u'Modèle:pron-rég',u'')
	TraitementLiens = crawlerLink(u'Modèle:mp',u'')
	TraitementLiens = crawlerLink(u'Modèle:fp',u'')
	TraitementLiens = crawlerLink(u'Modèle:pron-rég',u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Traduction en français demandée d’exemple(s) écrits en français',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section',False,u'')
'''	
	while 1:
		TraitementRC = crawlerRC_last_day()

TraitementLiensCategorie = crawlerCatLink(u'Catégorie:Modèles désuets',u'')
TraitementLiens = crawlerLink(u'Modèle:SAMPA',u'') : remplacer les tableaux de prononciations ?
TraitementLiens = crawlerLink(u'Modèle:trad-',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Conjugaisons manquantes en français',True,u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects:pron conv',True,u'')

# Modèles
TraitementPage = modification(u'Modèle:terme')
TraitementLiens = crawlerLink(u'Modèle:terme',u'')
TraitementFichier = crawlerFile(u'articles_WTin.txt')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True,u'')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot', 800)
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')

python replace.py -lang:commons -family:commons -file:articles_commons.txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
python delete.py -lang:fr -family:wiktionary -file:articles_WTin.txt
python movepages.py -lang:fr -family:wiktionary -pairs:"articles_WTin.txt" -noredirect -pairs
python interwiki.py -lang:fr -family:wiktionary -page:"Wiktionnaire:Accueil communautaire"
python interwiki.py -lang:fr -family:wiktionary -wiktionary -autonomous -force -usercontribs:Otourly
python protect.py -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop
'''

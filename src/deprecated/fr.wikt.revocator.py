#!/usr/bin/env python
# coding: utf-8
# Révocateur

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
#language = "commons"
#family = "commons"
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
debogage = False
debogageLent = False
Action = u'révocation'
Bloquer = False

# Modification du wiki
def modification(PageHS, Username):
	if debogage: print u'------------------------------------'
	print(PageHS.encode(config.console_encoding, 'replace'))
	page = Page(site,PageHS)
	if (page.namespace() != 1 and page.namespace() != 3 and page.namespace() != 5) or PageHS == u'User:JackBot/test':	#page.namespace() == 0 
		if page.exists():
			PageBegin = u''
			if Action == u'annulation':
				summary = u'Annulation de ' + Username
				if page.userName() == Username and page.getCreator() != Username:
					if debogage: print Username + u' trouvé'
					try:
						PageBegin = page.getOldVersion(page.previousRevision())
					except wikipedia.NoPage:
						print u'NoPage l 42'
						return
					except wikipedia.IsRedirectPage: 
						print u'IsRedirect l 45'
						return
				else:
					if debogage: print page.userName() + u' trouvé'
			else:
				summary = u'Révocation de ' + Username
				Found = False
				cpt = 0
				try:
					while page.getVersionHistory()[cpt][2] == Username and page.getCreator() != Username:
						Found = True
						cpt = cpt + 1
						if debogage: print Username + u' trouvé'
					if Found: 
						PageBegin = page.getOldVersion(page.getVersionHistory()[cpt][0])
				except wikipedia.NoPage:
					print u'NoPage l 56'
					return
				except wikipedia.IsRedirectPage: 
					print u'IsRedirect l 59'
					return
				except IndexError: 
					print u'IndexError Out Of Range l 67'
					return
			if PageBegin != u'': 
				page = Page(site,PageHS)	# Reset de page pour éditer la dernière version
				sauvegarde(page, PageBegin, summary)
			
		else:
			if debogage: print u'page inexistante'
	else:
		if debogage: print u'page non ciblée'

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source, Username):
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
			modification(html2Unicode.html2Unicode(PageHS), Username)
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres, Username):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title(), Username) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
		for subcategory in subcat:
			pages = subcategory.articlesList(False)
			for Page in pagegenerators.PreloadingGenerator(pages,100):
				modification(Page.title(), Username)

# Traitement des pages liées
def crawlerLink(pagename,apres, Username):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title(), Username) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres, Username):
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
				modification(PageLiee.title(), Username) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename, Username):
	gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title(), Username)

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
		
def crawlerRC(Username):
	gen = pagegenerators.RecentchangesPageGenerator(site = site)
	ecart_minimal_requis = 30 # min
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print str(ecart_last_edit(Page)) + ' =? ' + str(ecart_minimal_requis)
		if ecart_last_edit(Page) > ecart_minimal_requis:
			modification(Page.title(), Username)

def ecart_last_edit(page, Username):
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
def crawlerUser(username, jusqua, Username):
	compteur = 0
	gen = pagegenerators.UserContributionsGenerator(username, site = site)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title(), Username)
		compteur = compteur + 1
		if compteur > jusqua: break

# Toutes les redirections
def crawlerRedirects(Username):
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title(), Username)	
										
# Traitement de toutes les pages du site
def crawlerAll(start, Username):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title(), Username)
	
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
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test', sys.argv[2])
	elif sys.argv[1] == u'page':
		TraitementPage = modification(u'négriat littéraire', sys.argv[2])
	elif sys.argv[1] == u'txt': 
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'.txt', sys.argv[2])
	elif sys.argv[1] == u'm':
		TraitementLiens = crawlerLink(u'Modèle:mp',u'', sys.argv[2])
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée',False,u'', sys.argv[2])
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:fs',u'', sys.argv[2])
	elif sys.argv[1] == u'user':	
		TraitementUtilisateur = crawlerUser(sys.argv[3], 1000, sys.argv[2])
	else:
		TraitementPage = modification(sys.argv[1], sys.argv[2])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	print 'Please enter a username'
'''	
# Modèles
TraitementPage = modification(u'Modèle:terme', '78.217.232.147')
TraitementLiens = crawlerLink(u'Modèle:terme',u'')
TraitementFichier = crawlerFile(u'articles_WTin.txt')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True,u'')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot', 800)
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')
while 1:
	TraitementRC = crawlerRC_last_day()
	
python delete.py -lang:fr -family:wiktionary -file:articles_WTin.txt
python movepages.py -lang:fr -family:wiktionary -pairs:"articles_WTin.txt" -noredirect -pairs
python interwiki.py -lang:fr -family:wiktionary -page:"Wiktionnaire:Accueil communautaire"
python interwiki.py -lang:fr -family:wiktionary -wiktionary -autonomous -force -usercontribs:Otourly
python protect.py -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop

python commons.revocator.py user 78.217.232.147 78.217.232.147
'''

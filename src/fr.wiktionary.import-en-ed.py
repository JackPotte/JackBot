#!/usr/bin/env python
# coding: utf-8
# Ce script importe les flexions d'un Wiktionary dans un autre où le lemme se trouve

# Environment modules
from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, os, re, socket, sys, urllib
import hyperlynx, defaultSort, html2Unicode, langues

debugLevel= 0
fileName = __file__
if debugLevel > 0: print fileName
if fileName.rfind('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
siteLanguage = fileName[0:2]
if debugLevel > 1: print siteLanguage
siteFamily = fileName[3:]
siteFamily = siteFamily[:siteFamily.find('.')]
if debugLevel > 1: print siteFamily
PWB = os.getcwd().find(u'Pywikibot') != -1
if PWB:
	import pywikibot
	from pywikibot import *
	from pywikibot import pagegenerators
	username = u'JackBot'	#KeyError: 'fr'
else:
	from wikipedia import *
	username = config.usernames[site.family.name][site.lang]

def getWiki(language, family):
	if PWB:
		return pywikibot.Site(language, family)
	else:
		return getSite(language, family)

site = getWiki(siteLanguage, siteFamily)
siteSource = getWiki('en', siteFamily)
templateSource = u'en-past of'
textTranslated = u'Passé de'
DebutScan = u'interspersed'

# Modification du wiki
def modification(Page2):
	page2 = Page(siteSource,Page2)
	page1 = Page(site,Page2)
	if debugLevel > 0: print Page2.encode(config.console_encoding, 'replace')
	if page2.exists() and page2.namespace() == 0 and not page1.exists():
		PageTemp = getPage(page2)
		if PageTemp == u'': return
		# Nature grammaticale
		PageTemp2 = PageTemp[:PageTemp.find(templateSource)]
		# Code langue
		PageTemp = PageTemp[PageTemp.find(templateSource)+len(templateSource)+1:len(PageTemp)]
		if PageTemp.find("lang=") != -1 and PageTemp.find("lang=") < PageTemp.find(u'}}'):
			PageTemp2 = PageTemp[PageTemp.find("lang=")+5:len(PageTemp)]
			if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
				codelangue = PageTemp2[:PageTemp2.find("|")]
				PageTemp = PageTemp[:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("|"):len(PageTemp)]
			else:
				codelangue = PageTemp2[:PageTemp2.find("}}")]
				PageTemp = PageTemp[:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("}"):len(PageTemp)]
			if codelangue == u'': codelangue = u'en'
			elif codelangue == u'Italian': codelangue = u'it'
			elif codelangue == u'Irish': codelangue = u'ga'
			elif codelangue == u'German': codelangue = u'de'
			elif codelangue == u'Middle English': codelangue = u'enm'
			elif codelangue == u'Old English': codelangue = u'ang'
			elif codelangue == u'Dutch': codelangue = u'nl'
			elif codelangue == u'Romanian': codelangue = u'ro'
			elif codelangue == u'Spanish': codelangue = u'es'
			elif codelangue == u'Catalan': codelangue = u'ca'
			elif codelangue == u'Portuguese': codelangue = u'pt'
			elif codelangue == u'Russian': codelangue = u'ru'
			elif codelangue == u'French': codelangue = u'fr'
			elif codelangue == u'Scots': codelangue = u'sco'
			elif codelangue == u'Chinese': codelangue = u'zh'
			elif codelangue == u'Mandarin': codelangue = u'zh'
			elif codelangue == u'Japanese': codelangue = u'ja'
		else:
			codelangue = u'en'
		#if debugLevel > 0: print u' ' + codelangue
		
		while PageTemp[:1] == u' ' or PageTemp[:1] == u'|':
			PageTemp = PageTemp[1:len(PageTemp)]
		# Lemme
		if PageTemp.find(u']]') != -1 and PageTemp.find(u']]') < PageTemp.find(u'}}'): # Si on est dans un lien
			mot = PageTemp[:PageTemp.find(u']]')+2]
		elif PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find(u'}}'):
			mot = PageTemp[:PageTemp.find(u'|')] # A faire : si dièse on remplace en même temps que les codelangue ci-dessous, à patir d'un tableau des langues
		else:
			mot = PageTemp[:PageTemp.find(u'}}')]
		if mot[:2] != u'[[': mot = u'[[' + mot + u']]'
		
		# Demande de Lmaltier : on ne crée que les flexions des lemmes existant
		page3 = Page(site,mot[2:len(mot)-2])
		if page3.exists() == u'False':
			print 'Page du lemme absente du Wiktionnaire'
			return
		PageLemme = getPage(page3)
		if PageLemme == u'': return
		if PageLemme.find(u'{{langue|' + codelangue + u'}}') == -1:
			print ' Paragraphe du lemme absent du Wiktionnaire'
			return
		else:
			# Prononciation
			pron = u''
			PageLemme = PageLemme[PageLemme.find(u'{{langue|' + codelangue + u'}}'):]
			if debugLevel > 1: raw_input(PageLemme.encode(config.console_encoding, 'replace'))

			p = re.compile(ur'{{pron\|([^}]+)\|en}}')
			result = p.findall(PageLemme)
			if len(result) > 0:
				if debugLevel > 0: print u' à partir de {{pron}}'
				r = 0
				while result[r] == u'' and r < len(result):
					r += 1
				pron = result[r]

			elif PageLemme.find(u'{{en-conj-rég') != -1:
				if debugLevel > 0: print u' à partir de {{en-conj-rég'
				pron = PageLemme[PageLemme.find(u'{{en-conj-rég')+len(u'{{en-conj-rég'):]
				if pron.find(u'|inf.pron=') != -1 and pron.find(u'|inf.pron=') < pron.find(u'}}'):
					pron = pron[pron.find(u'|inf.pron=')+len(u'|inf.pron='):]
					if pron.find(u'}}') < pron.find(u'|') or pron.find(u'|') == -1:
						pron = pron[:pron.find(u'}}')]
					else:
						pron = pron[:pron.find(u'|')]
				else:
					pron = u''

			if pron != '':
				# Suffixe du -ed
				l = pron[-1:]
				if l in (u'f', u'k', u'p', u'θ', u's', u'ʃ'):
					pron = pron + u't'
				elif l in (u't', u'd'):
					pron = pron + u'ɪd' 
				else:
					pron = pron + u'd'
			if debugLevel > 0: print u' prononciation : ' + pron #.encode(config.console_encoding, 'replace')
		
		if PageTemp2.rfind(u'===') == -1:
			return
		else:
			PageTemp3 = PageTemp2[:PageTemp2.rfind(u'===')]
			nature = PageTemp3[PageTemp3.rfind(u'===')+3:]
			if debugLevel > 1: raw_input(nature.encode(config.console_encoding, 'replace'))
		if nature == 'Noun':
			nature = u'S|nom'
		elif nature == 'Adjective':
			nature = u'S|adjectif'
		elif nature == 'Pronoun':
			nature = u'S|pronom'
		elif nature == 'Verb':
			nature = u'S|verbe'
		else:
			if debugLevel > 0: print ' Nature inconnue'
			return
		if debugLevel > 0: print u' nature : ' + nature

		# Interwikis
		interwikiInside = pywikibot.getLanguageLinks(PageTemp, siteSource)
		interwiki = replaceLanguageLinks(u'', interwikiInside, siteSource)
		while interwiki.find(u'[[wiktionary:') != -1:
			interwiki = interwiki[:interwiki.find(u'[[wiktionary:')+2] + interwiki[interwiki.find(u'[[wiktionary:')+len(u'[[wiktionary:'):len(interwiki)]

		Page1 = u'=={{langue|' + codelangue + u'}}==\n=== {{' + nature + u'|' + codelangue + u'|flexion}} ===\n\'\'\'' + page2.title() + u'\'\'\' {{pron|'+pron+'|' + codelangue + u'}}\n# \'\'Prétérit de\'\' ' + mot + u'.\n# \'\'Participe passé de\'\' ' + mot + u'.\n\n[[en:' + page2.title() + u']]\n' + trim(interwiki)
		summary = u'Importation depuis [[en:' + page2.title() + u']]'
		sauvegarde(page1, Page1, summary)


def trim(s):
    return s.strip(" \t\n\r\0\x0B")
	
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
	cat = catlib.Category(siteSource, category)
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
	page = pywikibot.Page(siteSource, pagename)
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
	cat = catlib.Category(siteSource, pagename)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		page = Page(siteSource, Page.title())
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
	gen = pagegenerators.SearchPageGenerator(pagename, site = siteSource, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC_last_day(site = siteSource, nobots=True, namespace='0'):
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
	gen = pagegenerators.RecentchangesPageGenerator(site = siteSource)
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
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
		compteur = compteur + 1
		if compteur > jusqua: break

# Toutes les redirections
def crawlerRedirects():
	for Page in siteSource.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())
	
# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
		page = pywikibot.Page(site,u'User talk:' + username)
		if page.exists():
			PageTemp = u''
			try:
				PageTemp = page.get()
			except pywikibot.exceptions.NoPage: return
			except pywikibot.exceptions.IsRedirectPage: return
			except pywikibot.exceptions.ServerError: return
			except pywikibot.exceptions.BadTitle: return
			if PageTemp != u"{{/Stop}}":
				pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
				exit(0)

def getPage(page):
	if page.exists():
		try:
			PageBegin = page.get()
		except pywikibot.exceptions.NoPage:
			#if debugLevel > 0: print u' no page ' + page.title()
			return u''
		except pywikibot.exceptions.InvalidPage:
			#if debugLevel > 0: print u' invalid page ' + page.title()
			return u''
		except pywikibot.exceptions.ServerError:
			#if debugLevel > 0: print u' server error ' + page.title()
			return u''
		except pywikibot.exceptions.IsRedirectPage:
			try:
				PageBegin = page.get(get_redirect=True)
			except:
				#if debugLevel > 0: print u' redirect error ' + page.title()
				return u''
	else:
		#if debugLevel > 0: print u' NoPage l 345 ' + page.title()
		return u''
	return PageBegin

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debugLevel > 0:
		if len(Contenu) < 6000:
			print(Contenu.encode(config.console_encoding, 'replace'))
		else:
			taille = 6000
			print(Contenu[:taille].encode(config.console_encoding, 'replace'))
			print u'\n[...]\n'
			print(Contenu[len(Contenu)-taille:].encode(config.console_encoding, 'replace'))
		result = raw_input("Sauvegarder ? (o/n) ")
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

def debug(chaine):
	try:
		print chaine
	except UnicodeError:
		print "UnicodeError"
	return

# Lancement
debugLevel = 0
if len(sys.argv) > 1:
	if len(sys.argv) > 2:
		if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
			debugLevel = 1
		else:
			DebutScan = sys.argv[2]
	if sys.argv[1] == u'test':
		modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'txt':
		# Au format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
		crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
	elif sys.argv[1] == u'm':
		crawlerLink(u'Modèle:pl-cour',u'')
	elif sys.argv[1] == u'cat':
		crawlerCat(u'Catégorie:Pages using duplicate arguments in template calls',False,u'')
	elif sys.argv[1] == u'lien':
		crawlerLink(u'Template:' + templateSource, DebutScan)
	else:
		modification(sys.argv[1])
else:
	crawlerLink(u'Template:' + templateSource, DebutScan)

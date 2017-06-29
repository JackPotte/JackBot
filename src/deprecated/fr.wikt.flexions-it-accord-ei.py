#!/usr/bin/env python
# coding: utf-8
# Ce script crée des flexions depuis le modèle d'un lemme

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *
import CleDeTri, html2Unicode

# Déclaration
mynick = "JackBot"
language1 = "fr"
family = "wiktionary"
site = getSite(language1,family)
template = u'it-accord-ei'
langue = template[0:2]
debogage = False

# Modification du wiki
def modification(Page1):
	summary = u'Création des flexions en italien depuis [[' + Page1 + u']]'
	print (Page1.encode(config.console_encoding, 'replace'))
	page0 = Page(site,Page1)
	if page0.namespace() != 0: return
	PageTitre = page0.title()
	PageTemp = page0.get()
	PageTemp2 = PageTemp[PageTemp.find(template)+len(template)+1:len(PageTemp)]
	PageTemp = PageTemp[0:PageTemp.find(template)]
	
	nature = PageTemp[PageTemp.rfind(u'{{S|')+4:PageTemp.rfind(u'}}')]
	if nature.find(u'|'): nature = nature[:nature.find(u'|')]
	if debogage: print ' nature : ' + nature.encode(config.console_encoding, 'replace')
	#if nature != u'nom': return
	
	if PageTemp2.find(u'|') < PageTemp2.find(u'}}') and PageTemp2.find(u'|') != -1:
		radical = PageTemp2[:PageTemp2.find(u'|')]
		if radical.find(u'=') != -1:
			radical = PageTemp2[PageTemp2.find(u'|')+1:PageTemp2.find(u'}}')]
			if radical.find(u'|') != -1: radical = radical[:radical.find(u'|')]
			if radical.find(u'=') != -1: radical = u''
	else:
		radical = PageTemp2[:PageTemp2.find(u'}}')]
	if debogage: print ' radical : ' + radical.encode(config.console_encoding, 'replace')
	if radical != -1:
		radical = radical + u'i'
	else:
		return
	
	if PageTemp2.find(u'{{pron|') != -1:
		prononciation = PageTemp2[PageTemp2.find(u'{{pron|')+len(u'{{pron|'):]
		prononciation = prononciation[:prononciation.find(u'|')]
		if prononciation != u'': prononciation = prononciation[:-1]+u'i'
	else:
		prononciation = u''
	if debogage: print ' pron : ' + prononciation.encode(config.console_encoding, 'replace')
	
	page1 = Page(site,radical)
	if not page1.exists():
		if debogage: print ' pluriel absent : ' + radical.encode(config.console_encoding, 'replace')
		PageTemp = u'== {{langue|'+langue+u'}} ==\n=== {{S|' + nature + u'|'+langue+u'|flexion}} ===\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron|'+prononciation+u'|'+langue+u'}}\n# \'\'Pluriel de\'\' [[' + Page1 + u'#'+langue+u'-nom|' + Page1 + u']].'
		sauvegarde(page1, PageTemp, summary)

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def addCat(PageTemp, lang, cat):
	if lang != u'':
		if PageTemp.find(cat) == -1 and PageTemp.find(u'{{langue|' + lang + u'}}') != -1:
			if cat.find(u'[[Catégorie:') == -1: cat = u'[[Catégorie:' + cat + u']]'
			PageTemp2 = PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}'):]
			if PageTemp2.find(u'{{langue|') != -1:
				if debogage: print u' catégorie ajoutée avant la section suivante'
				if PageTemp2.find(u'== {{langue|') != -1:
					PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'== {{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'== {{langue|'):]
				elif PageTemp2.find(u'=={{langue|') != -1:
					PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'=={{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'=={{langue|'):]
				else:
					 print u'Modèle {{langue| mal positionné'
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
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'txt': 
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
	elif sys.argv[1] == u'txt2':
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'2.txt')
	elif sys.argv[1] == u'm':
		TraitementLiens = crawlerLink(u'Modèle:mplur',u'')
		TraitementLiens = crawlerLink(u'Modèle:fplur',u'')
		TraitementLiens = crawlerLink(u'Modèle:pron-rég',u'')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Théorie des graphes en français',False,u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:fs',u'')
	elif sys.argv[1] == u'page':
		#TraitementPage = modification(u'C++')
		TraitementPage = modification(u'négriat littéraire')
	elif sys.argv[1] == u's':
		TraitementRecherche = crawlerSearch(u'"source à préciser"')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	TraitementLiens = crawlerLink(u'Modèle:'+template,u'')
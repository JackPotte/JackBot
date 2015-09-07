#!/usr/bin/env python
# coding: utf-8
# Ce script crée les pluriels en français à partir des singuliers

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
import CleDeTri, HTMLUnicode
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
Langue = u'fr'
debogage = False
debogageLent = False

# Modification du wiki
def modification(PageHS):
	if debogage: print u'------------------------------------'
	print(PageHS.encode(config.console_encoding, 'replace'))
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() != 0 and page.title() != u'Utilisateur:JackBot/test':
			print u' Autre namespace l 26'
			return
	else:
		print u' Page inexistante'
		return
	Modele = [] # Liste des modèles du site à traiter
	Param = [] # Paramètre du lemme associé
	Modele.append(u'fr-rég')
	Param.append(u's')
	limiteMF = 2
	# Pb car boucle quand-même
	Modele.append(u'fr-accord-cons')
	Param.append(u'ms')
	# à faire : ajouter Catégorie:Modèles d’accord en français

	try:
		PageSing = page.get()
	except wikipedia.NoPage:
		print u' NoPage l 40'
		return
	except wikipedia.IsRedirectPage:
		print u' IsRedirectPage l 43'
		return
	except wikipedia.BadTitle:
		print u' BadTitle l 46'
		return
	except wikipedia.InvalidPage:
		print u' InvalidPage l 49'
		return
	except wikipedia.ServerError:
		print u' ServerError l 52'
		return

	for m in range(0,len(Modele)):
		# Parcours de la page pour chaque modèle
		if debogageLent: print ' début du for'
		if PageSing.find(Modele[m]) == -1:
			print u' Modèle ' + Modele[m] + u' absent l 58'
			return
		else:
			PageTemp = PageSing
		
		while PageTemp.find(Modele[m]) != -1:
			if len(Modele[m]) < 3:
				print u' bug'
				return
			if debogageLent: 
				print Modele[m].encode(config.console_encoding, 'replace')
				print PageTemp.find(Modele[m])
				
			# Parcours de la page pour chaque occurence du modèle
			nature = PageTemp[:PageTemp.find(Modele[m])]
			nature = nature[nature.rfind(u'{{S|')+len(u'{{S|'):]
			nature = nature[:nature.find(u'|')]
			if debogage:
				try:
					print u' Nature : ' + nature.encode(config.console_encoding, 'replace')
				except UnicodeDecodeError:
					print u' Nature à décoder'
				except UnicodeEncodeError:
					print u' Nature à encoder'
			if nature == u'erreur' or nature == u'faute':
				print u' section erreur'
				return
				
			PageTemp = PageTemp[PageTemp.find(Modele[m])+len(Modele[m]):]
			if PageTemp.find(u'inv=') != -1 and PageTemp.find(u'inv=') < PageTemp.find(u'}}'):
				print u' inv='
				return
			if PageTemp.find(u's=') != -1 and (PageTemp.find(u's=') < PageTemp.find(u'}}') or PageTemp.find(u's=') < PageTemp.find(u'\n')):
				print u' s='
				# à traiter
				return
			# Prononciation
			if PageTemp.find(u'|pp=') != -1 and PageTemp.find(u'|pp=') < PageTemp.find(u'}}'):
				if debogage: print ' pp='
				PageTemp2 = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
				if PageTemp2.find(u'|') != -1:
					pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'|pp=')+4+PageTemp2.find(u'|')]
				else:
					pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
			else:
				if debogageLent: print ' prononciation identique au singulier'
				pron = PageTemp[:PageTemp.find(u'}}')]
				if debogageLent: print u'  pron avant while : ' + pron.encode(config.console_encoding, 'replace')
				if pron.find(u'|pron=') != -1:
					pron = u'|' + pron[pron.find(u'|pron=')+len(u'|pron='):]
				
				'''
				print pron.encode(config.console_encoding, 'replace')
				pattern = ur'.*\|([^}\|]*)}|\|'
				regex = re.search(pattern, pron)
				print regex.start()
				print regex.end()
				raw_input(pron[regex.start():regex.end()])
				'''
				
				TabPron = pron.split(u'|')
				# {{fr-rég|a.kʁɔ.sɑ̃.tʁik|mf=oui}}
				n = 0
				while n < len(TabPron) and (TabPron[n] == '' or TabPron[n].find(u'=') != -1):
					if debogageLent: print TabPron[n].find(u'=')
					n += 1
				if n == len(TabPron):
					pron = u'|'
				else:
					pron = u'|' + TabPron[n]
				'''
				while pron.find(u'=') != -1:
					pron2 = pron[:pron.find(u'=')]
					pron3 = pron[pron.find(u'='):]
					if debogage: print u'  pron2 : ' + pron2.encode(config.console_encoding, 'replace')
					if pron2.find(u'|') == -1:
						pron = pron[pron.find(u'|')+1:]
						if debogageLent: print u'  pron dans while1 : ' + pron.encode(config.console_encoding, 'replace')
					else:
						if debogage: print u'  pron3 : ' + pron3.encode(config.console_encoding, 'replace')
						if pron3.rfind(u'|') == -1:
							limitPron = len(pron3)
						else:
							limitPron = pron3.rfind(u'|')
						if debogage: print u'  limitPron : ' + str(limitPron)
						pron = pron[pron.find(u'=')+limitPron:]
						if debogage: print u'  pron dans while2 : ' + pron.encode(config.console_encoding, 'replace')
				'''
				if debogage: print u'  pron après while : ' + pron.encode(config.console_encoding, 'replace')
			while pron[:1] == u' ': pron = pron[1:len(pron)]
			if pron.rfind(u'|') > 0:
				pronM = pron[:pron.rfind(u'|')]
				while pronM.rfind(u'|') > 0:
					pronM = pronM[:pronM.rfind(u'|')]
			else:
				pronM = pron
			if debogage:
				try:
					print u' Prononciation : ' + pronM.encode(config.console_encoding, 'replace')
				except UnicodeDecodeError:
					print u' Prononciation à décoder'
				except UnicodeEncodeError:
					print u' Prononciation à encoder'
			
			# h aspiré
			H = u''
			if PageTemp.find(u'|prefpron={{h aspiré') != -1 and PageTemp.find(u'|prefpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|prefpron={{h aspiré}}'
			if PageTemp.find(u'|préfpron={{h aspiré') != -1 and PageTemp.find(u'|préfpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|préfpron={{h aspiré}}'
			# genre
			genre = u''
			PageTemp2 = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
			while PageTemp2[:1] == u'[' or PageTemp2[:1] == u'\n' and len(PageTemp2) > 1: PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
			if PageTemp2.find(u'{{m}}') != -1 and PageTemp2.find(u'{{m}}') < PageTemp2.find(u'\n'): genre = u' {{m}}'	
			if PageTemp2.find(u'{{f}}') != -1 and PageTemp2.find(u'{{f}}') < PageTemp2.find(u'\n'): genre = u' {{f}}'
			MF = u''
			if PageTemp2.find(u'{{mf}}') != -1 and PageTemp2.find(u'{{mf}}') < PageTemp2.find(u'\n'):
				genre = u' {{mf}}'
				MF = u'|mf=oui'
				if PageSing.find(u'|mf=') == -1 and m < limiteMF:
					PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|mf=oui' + PageSing[PageSing.find(Modele[m])+len(Modele[m]):len(PageSing)]
					sauvegarde(page, PageSing, u'|mf=oui')
			if PageTemp.find(u'|mf=') != -1 and PageTemp.find(u'|mf=') < PageTemp.find(u'}}'): MF = u'|mf=oui' 
			# Pluriel
			summary = u'Création du pluriel de [[' + PageHS + u']]'
			pluriel = u''
			if (PageTemp.find(u'|p=') != -1 and PageTemp.find(u'|p=') < PageTemp.find(u'}}')):
				pluriel = PageTemp[PageTemp.find(u'|p=')+3:PageTemp.find(u'}}')]
				if pluriel.find(u'|') != -1: pluriel = pluriel[:pluriel.find(u'|')]
			if not pluriel: pluriel = PageHS + u's'
			if pluriel[-2:] == u'ss' or pluriel.find(u'{') != -1:
				print pluriel[-2:]
				return
			if debogageLent:
				print ' Paramètre du modèle du lemme : ' + PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
			
			page2 = Page(site,pluriel)
			if page2.exists():
				try:
					PagePluriel = page2.get()
				except wikipedia.NoPage:
					print u' NoPage l 120'
					return
				except wikipedia.IsRedirectPage:
					print u' IsRedirectPage l 123'
					return
				except wikipedia.BadTitle:
					print u' BadTitle l 126'
					return
				except wikipedia.InvalidPage:
					print u' InvalidPage l 129'
					return
				except wikipedia.ServerError:
					print u' ServerError l 132'
					return
				if PagePluriel.find(u'{{langue|' + Langue + u'}}') != -1:
					print u' Pluriel existant l 135'
					return
			else:
				if debogage: print u' Pluriel introuvable l 138'
				PagePluriel = u''
			
			# **************** Pluriel 1 ****************
			if debogage: print u' Pluriel 1'
			Modele = u'{{' + Modele[m] + pronM + H + MF + '|' + Param[m] + u'=' + PageHS
			if pluriel.find(u' ') != -1:
				Modele += u'|p={{subst:PAGENAME}}'
			Modele += u'}}'
			PageEnd = u'== {{langue|fr}} ==\n=== {{S|' + nature + u'|fr|flexion}} ===\n' + Modele + u'\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pronM + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + PageHS +']].\n'
			while PageEnd.find(u'{{pron|fr}}') != -1:
				PageEnd = PageEnd[:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]

			if pluriel[len(pluriel)-2:len(pluriel)] == u'ss':
				PageSing = PageSing[:PageSing.find(Modele[m])+len(Modele[m])] + u'|' + Param[m] + u'=' + pluriel[:len(pluriel)-2] + PageSing[PageSing.find(Modele[m])+len(Modele[m]):len(PageSing)]
				sauvegarde(page, PageSing, u'{{' + Modele[m] + u'|s=...}}')
			elif pluriel[len(pluriel)-2:len(pluriel)] == u'xs':
				print u' Pluriel en xs'
				return
			else:
				PageEnd = HTMLUnicode.HTMLUnicode(PageEnd)
				sauvegarde(page2, PageEnd + u'\n' + PagePluriel, summary)
			#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
			if debogage: print u'Fin du while'

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

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
			PageHS = PageHS[:fin]
			if PageHS == '': break
			if PageHS.find(u'[[') != -1:
				PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
			if PageHS.find(u']]') != -1:
				PageHS = PageHS[:PageHS.find(u']]')]
			# Conversion ASCII => Unicode (pour les .txt)
			modification(HTMLUnicode.HTMLUnicode(PageHS))
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
	gen = pagegenerators.UserContributionsGenerator(username)
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
	elif sys.argv[1] == u'm':
		TraitementLiens = crawlerLink(u'Modèle:pl-cour',u'')
	elif sys.argv[1] == u'p':
		TraitementLiens = modification(u'acide hydrothionique')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Pluriels manquants en français',False,u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:sports de combat',u'')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	#TraitementLiens = crawlerLink(u'Modèle:fr-accord-cons',u'')
	TraitementLiens = crawlerLink(u'Modèle:fr-accord-al',u'')
# python touch.py -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"
# python fr.wikt.pluriel.py cat

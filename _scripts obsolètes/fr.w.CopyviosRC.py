#!/usr/bin/env python
# Ce script cherche les copyvios sur Google et les signale à qui de droit.
 
# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, urllib2, json, pprint, urlparse, datetime
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
summary = u'[[Wikipédia:Bot/Requêtes/2011/07#Traitement_des_copyvios|Probable copyvio détecté dans Google]]'

# Modification du wiki à partir du nom de la page
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		try:
			PageTemp = page.get()
		except wikipedia.NoPage:
			print "NoPage"
			return
		except wikipedia.IsRedirectPage:
			print "Redirect page"
			return
		except wikipedia.LockedPage:
			print "Locked/protected page"
			return
		if len(PageTemp) > 100:
			url = u'http://ajax.googleapis.com/ajax/services/search/web?hl=fr&v=1.0&q="' + PageTemp[0:100] + u'"'
		else:
			url = u'http://ajax.googleapis.com/ajax/services/search/web?hl=fr&v=1.0&q="' + PageTemp + u'"'
		url = url.replace("\n","+")
		url = url.replace("|","+")
		url = url.replace("{","+")
		url = url.replace("}","+")
		url = url.replace("<","+")
		url = url.replace(">","+")
		url = url.replace("-","+")
		url = url.replace("!","+")
		while url.find("++") != -1:
			url = url.replace("++","+")
		url = url.replace(" ","%20")
		#url = urllib.quote(url) # UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
		data = urllib2.urlopen(url.encode("latin-1","ignore")).read()
		results = json.loads(data)
		#pprint.pprint(results)
		#print (str(results['responseDetails'])[results['responseDetails'].find("u'responseDetails': ")+len("u'responseDetails': "):results['responseDetails'].find("u'responseDetails': ")+len("u'responseDetails': ")+4])
		if str(results['responseDetails']) != u'None':
			# Récupération de la page à modifier
			page = Page(site,u'Utilisateur:JackBot/Copyvios RC')
			if page.exists():
				try:
					PageTemp = page.get()
				except wikipedia.NoPage:
					print "NoPage"
					return
				except wikipedia.IsRedirectPage:
					print "Redirect page"
					return
				except wikipedia.LockedPage:
					print "Locked/protected page"
					return
			PageEnd = PageTemp + u'\n* ' + unicode(datetime.datetime.now()) + u' Copyvio probable de [[' + PageHS + u']] depuis ' + str(results['responseDetails'])
			# Sauvegarde semie-automatique
			result = "ok"
			#print (PageEnd.encode(config.console_encoding, 'replace')[0:900])
			#result = raw_input(u'\033[94m' + u'Sauvegarder ? (o/n)' + '\033[0m ')
			if result == u'n' or result == u'no' or result == u'non': 
				return
			else:
				try:
						arretdurgence()
						page.put(PageEnd, summary)
				except pywikibot.EditConflict:
						print "Conflict"
						return
				except wikipedia.NoPage:
						print "NoPage"
						return
				except wikipedia.IsRedirectPage:
						print "Redirect page"
						return
				except wikipedia.LockedPage:
						print "Locked/protected page"
						return 

# Permet à tout le monde de stopper le bot en lui écrivant
def arretdurgence():
	arrettitle = ''.join(u"Discussion utilisateur:JackBot")
	arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
	gen = iter([arretpage])
	arret = arretpage.get()
	if arret != u"{{/Stop}}":
		pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
		exit(0)

# Traitement des modifications récentes
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator(site=site)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		print Page.title()
		modification(Page.title())

#TraitementPage = modification(u'Utilisateur:JackBot/test')
while 1:
     TraitementRC = crawlerRC()

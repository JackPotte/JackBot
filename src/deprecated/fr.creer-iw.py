#!/usr/bin/env python
# coding: utf-8
# Ce script crée des pages sur tous les wikis de la fondation (ex : PU)

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
family = range(1, 9)
family[1] = u'wikipedia'
family[2] = u'wiktionary'
family[3] = u'wikibooks'
family[4] = u'wikiversity'
family[5] = u'wikisource'
family[6] = u'wikiquote'
family[7] = u'wikinews'
PageEnd = u'{{Bot|JackPotte}}\n[[fr:Utilisateur:JackBot]]'
summary = u''

def sauvegarde(PageCourante, Contenu, Resume):
	try:
		result = "ok"
		#print(Contenu.encode(config.console_encoding, 'replace')[len(Contenu)-1000:len(Contenu)])
		#result = raw_input("Sauvegarder ? (o/n)")
		if not Resume: Resume = summary
		if result != "n" and result != "no" and result != "non": PageCourante.put(Contenu, Resume)
	except wikipedia.NoPage:
		print "No page"
		return
	except wikipedia.IsRedirectPage:
		print "Redirect page"
		return
	except wikipedia.LockedPage:
		print "Protected page"
		return
	except pywikibot.EditConflict:
		print "Edit conflict"
		return
		
for famille in range(1, 8):
	PagesHS = open(u'Languages from names.php.txt', 'r')
	while 1:
		language = PagesHS.readline()
		fin = language.find("\t")
		language = language[0:fin]
		if language == '':
			break
		#elif language != u'dz' and language != u'ast' and language != u'mn' and language != u'my' and language != u'tk' and language != u'vo' and language != u'co' and language != u'lb' and language != u'sd':
		else:
			print language + "." + family[famille]
			try:
				site = getSite(language,family[famille])
				page = Page(site,u'User:JackBot')
				if not page.exists(): sauvegarde(page,PageEnd,summary)
			except wikipedia.ServerError: print "erreur"
			except wikipedia.NoSuchSite: print "pas de site"
			except wikipedia.UserBlocked: print u'bloqué'
			except wikipedia.IsRedirectPage: print u'pb'
			except wikipedia.LockedPage: print u'pb'
			except wikipedia.BadTitle: print u'pb'
			except pywikibot.EditConflict: print u'pb'
	PagesHS.close()
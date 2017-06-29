#/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Importation des modules
import catlib, pagegenerators, os #, codecs, urllib, re, collections, socket
from wikipedia import *

# Déclaration
language = "fr"
family = "wikinews"
mynick = "JackBot"
site = getSite(language,family)
debogage = False

# Modification du wiki
def modification(PageHS):
	summary = u'Ratissage'
	page = Page(site,PageHS)
	if page.exists():
		try:
			PageBegin = page.get()
		except wikipedia.NoPage:
			print "NoPage l 1113"
			return
		except wikipedia.LockedPage: 
			print "Locked l 1116"
			return
	else:
		return
	
	page2 = Page(site,u'Utilisateur:JackBot/Template du bac à sable')
	if page2.exists():
		try:
			PageTemplate = page2.get()
		except wikipedia.NoPage:
			print "NoPage l 1113"
			return
		except wikipedia.LockedPage: 
			print "Locked l 1116"
			return
	else:
		return
	
	if PageBegin != u'{{Sandbox heading}}\n' + PageTemplate:
		sauvegarde(page, u'{{Sandbox heading}}\n' + PageTemplate, summary)
	
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
			
TraitementPage = modification(u'Wikinews:Bac à sable')
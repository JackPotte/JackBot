#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *
from pageimport import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wikibooks"
site = getSite(language,family)
site2 = getSite(u'en',family)
summary = u'Importation de projet frère'

# Traitement des importations
def crawlerImport(source):
	importerbot = Importer(site)
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			#page = Page(site2,PageHS)
			importerbot.Import(target=PageHS, crono=1, namespace = '0', project='en', prompt=False)
		PagesHS.close()
		
# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
        arrettitle = ''.join(u'Discussion utilisateur:' + mynick)
        arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
        gen = iter([arretpage])
        arret = arretpage.get()
        if arret != u"{{/Stop}}":
			pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
			exit(0)

def sauvegarde(PageCourante, Contenu, Resume):
	ArretDUrgence()
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
		
# Lancement
TraitementImport = crawlerImport('articles_list.txt')
#TraitementCategory = crawlerCat(u'Catégorie:Personnalités de la photographie')
#TraitementFile = crawlerFile('articles_listed.txt')
#while 1:
#	TraitementRC = crawlerRC()


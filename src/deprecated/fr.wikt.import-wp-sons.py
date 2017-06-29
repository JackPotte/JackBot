#!/usr/bin/env python
# coding: utf-8
# Ce script importe les localités du Portugal

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
site = getSite(u'fr',u'wiktionary')
site1 = getSite(u'pt',u'wikipedia')
summary = u'Création depuis [[w:pt:Anexo:Lista de concelhos por NUTS]]'

# Modification du wiki
def modification(Page1):
	page1 = Page(site1,Page1)
	try:
		PageTemp = page1.get()
	except wikipedia.NoPage: return
	except wikipedia.IsRedirectPage: return
	except wikipedia.LockedPage: return
	PageTemp = PageTemp[PageTemp.find(u'{|'):len(PageTemp)]
	while PageTemp.find(u'{{IPA-pt|') != -1:
		# Récupération depuis une annexe
		PageTemp = PageTemp[PageTemp.find(u'{{IPA-pt|')+9:len(PageTemp)]
		prononciation = PageTemp[0:PageTemp.find(u'|')]
		PageTemp = PageTemp[PageTemp.find(u'|pron|')+6:len(PageTemp)]
		son = PageTemp[0:PageTemp.find(u'}}')]
		Page2 = PageTemp[PageTemp.find(u'Pt-pt ')+6:PageTemp.find(u' FF.ogg')] 
		PageEnd = u'== {{langue|pt}} ==\n{{-étym-}}\n{{ébauche-étym|pt}}\n\n{{-nom-pr-|pt}}\n{{fr-inv|' + prononciation + u'}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron|' + prononciation + u'|pt}} {{genre|pt}} {{invar}}\n# Localité du [[Portugal]].\n\n{{-pron-}}\n{{pron-rég|Portugal|' + prononciation + u'|audio=' + son + u'}}\n\n{{-voir-}}\n*{{WP|Anexo:Lista de concelhos por NUTS|lang=pt}}\n\n[[Catégorie:Localités du Portugal en portugais]]\n'
		
		# Sauvegarde
		page2 = Page(site,Page2)
		if page2.exists():
			try:
				PageTemp2 = page2.get()
			except wikipedia.NoPage: return
			except wikipedia.IsRedirectPage: return
			except wikipedia.LockedPage: return
			if PageTemp2.find(u'{{langue|pt}}') == -1 and PageTemp2.find(u'{{=pt=}}') == -1:
				sauvegarde(page2,PageTemp2 + PageEnd)
			#else:
				#sauvegarde(page2,PageEnd)
		else:
			sauvegarde(page2,PageEnd)
		
def sauvegarde(PageCourante, Contenu):
	ArretDUrgence()
	result = "ok"
	#print(Contenu.encode(config.console_encoding, 'replace')[0:4000])	#[len(Contenu)-2000:len(Contenu)]) #
	#result = raw_input("Sauvegarder ? (o/n)")
	if result != "n" and result != "no" and result != "non":
		try:
			PageCourante.put(Contenu, summary)
		except wikipedia.NoPage: return
		except wikipedia.IsRedirectPage: return
		except wikipedia.LockedPage: return
		except pywikibot.EditConflict: return
		except wikipedia.ServerError: return
		except wikipedia.BadTitle: return

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
				
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def lecture(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			modification(PageHS)
		PagesHS.close()
		
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		modification(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())

def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, u'Template:' + pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
	'''
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, u'Template:' + pagename)
	links = page.linkedPages()
	print links
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in links:
		print(Page.title())	
		modification(Page.title())
	'''
	
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Lancement
TraitementPage = modification(u'Anexo:Lista_de_concelhos_por_NUTS')
'''
TraitementFile = lecture('articles_list.txt')
TraitementCategory = crawlerCat(u'')
TraitementLiens = crawlerLink(template)
while 1:
	TraitementRC = crawlerRC()
'''

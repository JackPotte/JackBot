#!/usr/bin/env python
# coding: utf-8
# Ce script importe les localités du Portugal

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
site = getSite(u'pt',u'wiktionary')
site1 = getSite(u'pt',u'wikipedia')
summary = u'criação desde [[w:Anexo:Lista de concelhos por NUTS]]'

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
		PageEnd = u'= {{-pt-}} =\n{{Wikipédia}}\n==Substantivo==\n\'\'\'{{subst:PAGENAME}}\'\'\' {{AFI|/' + prononciation + u'/|pt}} {{pr}}\n# [[cidade]] [[português|portuguesa]].\n\n===Tradução===\n{{tradini}}\n{{tradfim}}\n\n=={{pronúncia|pt}}==\n{{áudio|' + son + u'|Português (BR)|/' + prononciation + u'/}}\n\n==Ver também==\n*[[w:Anexo:Lista de concelhos por NUTS]]\n\n[[Categoria:Concelho de Portugal (Português)]]\n\n[[fr:' + Page2 + u']]'

		# Sauvegarde
		page2 = Page(site,Page2)
		if page2.exists():
			try:
				PageTemp2 = page2.get()
			except wikipedia.NoPage: return
			except wikipedia.IsRedirectPage: return
			except wikipedia.LockedPage: return
			if PageTemp2.find(u'{{-pt-}}') == -1:
				sauvegarde(page2,PageEnd + PageTemp2)
			#else:
				#sauvegarde(page2,PageEnd)
		else:
			sauvegarde(page2,PageEnd)
		
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
		
# Lancement
TraitementPage = modification(u'Anexo:Lista_de_concelhos_por_NUTS')
'''
TraitementFile = lecture('articles_list.txt')
TraitementCategory = crawlerCat(u'')
TraitementLiens = crawlerLink(template)
while 1:
	TraitementRC = crawlerRC()
'''

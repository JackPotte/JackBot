#!/usr/bin/env python
# coding: utf-8
# Ce script important masse

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language1 = "fr"
family = "wiktionary"
site1 = getSite(language1,family)
language2 = "en"
site2 = getSite(language2,family)
template = u'plural of'
texte = u'Pluriel de'

# Modification du wiki
def modification(Page2):
	page2 = Page(site2,Page2)
	page1 = Page(site1,Page2)
	print (Page2.encode(config.console_encoding, 'replace'))
	if page2.exists() and page2.namespace() ==0 and not page1.exists():
		try: PageTemp = page2.get()
		except wikipedia.NoPage: return
		except wikipedia.InvalidPage: return
		except wikipedia.ServerError: return
		# Nature grammaticale
		PageTemp2 = PageTemp[0:PageTemp.find(template)]
		# Code langue
		PageTemp = PageTemp[PageTemp.find(template)+len(template)+1:len(PageTemp)]
		if PageTemp.find("lang=") != -1 and PageTemp.find("lang=") < PageTemp.find(u'}}'):
			PageTemp2 = PageTemp[PageTemp.find("lang=")+5:len(PageTemp)]
			if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
				codelangue = PageTemp2[0:PageTemp2.find("|")]
				PageTemp = PageTemp[0:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("|"):len(PageTemp)]
			else:
				codelangue = PageTemp2[0:PageTemp2.find("}}")]
				PageTemp = PageTemp[0:PageTemp.find("lang=")] + PageTemp[PageTemp.find("lang=")+5+PageTemp2.find("}"):len(PageTemp)]
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
		while PageTemp[0:1] == u' ' or PageTemp[0:1] == u'|':
			PageTemp = PageTemp[1:len(PageTemp)]
		# Lemme
		if PageTemp.find(u']]') != -1 and PageTemp.find(u']]') < PageTemp.find(u'}}'): # Si on est dans un lien
			mot = PageTemp[0:PageTemp.find(u']]')+2]
		elif PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find(u'}}'):
			mot = PageTemp[0:PageTemp.find(u'|')] # A faire : si dièse on remplace en même temps que les codelangue ci-dessous, à patir d'un tableau des langues
		else:
			mot = PageTemp[0:PageTemp.find(u'}}')]
		if mot[0:2] != u'[[': mot = u'[[' + mot + u']]'
		
		# Demande de Lmaltier : on ne crée que les flexions des lemmes existant
		page3 = Page(site1,mot[2:len(mot)-2])
		if page3.exists() == u'False': return
		try: Test = page3.get()
		except wikipedia.NoPage: return
		except wikipedia.SectionError: return
		except wikipedia.IsRedirectPage: return
		if Test.find(u'{{=' + codelangue + u'=}}') == -1: return
		
		if PageTemp2.rfind(u'===') == -1: return
		else:
			PageTemp3 = PageTemp2[0:PageTemp2.rfind(u'===')]
			nature = PageTemp3[PageTemp3.rfind(u'===')+3:len(PageTemp3)]
		if nature == 'Noun':
			if mot.find(u' ') == -1:
				nature = u'-flex-nom-'
			else:
				nature = u'-flex-loc-nom-'
		elif nature == 'Adjective':
			if mot.find(u' ') == -1:
				nature = u'-flex-adj-'
			else:
				nature = u'-flex-loc-adj-'
		elif nature == 'Pronoun':
			if mot.find(u' ') == -1:
				nature = u'-flex-pronom-'
			else:
				nature = u'-flex-loc-pronom-'
		elif nature == 'Verb':
			if mot.find(u' ') == -1:
				nature = u'-flex-verb-'
			else:
				nature = u'-flex-loc-verb-'
		else: return
		# Interwikis
		interwikiInside = pywikibot.getLanguageLinks(PageTemp, site2)
		interwiki = wikipedia.replaceLanguageLinks(u'', interwikiInside, site2)
		while interwiki.find(u'[[wiktionary:') != -1:
			interwiki = interwiki[0:interwiki.find(u'[[wiktionary:')+2] + interwiki[interwiki.find(u'[[wiktionary:')+len(u'[[wiktionary:'):len(interwiki)]
		Page1 = u'=={{=' + codelangue + u'=}}==\n{{' + nature + u'|' + codelangue + u'}}\n\'\'\'' + page2.title() + u'\'\'\' {{pron||' + codelangue + u'}}\n# \'\'' + texte + u'\'\' ' + mot + u'.\n\n[[en:' + page2.title() + u']]' + interwiki
		summary = u'Importation depuis [[en:' + page2.title() + u']]'
		#print (Page1.encode(config.console_encoding, 'replace'))
		#raw_input("fin")
		page1.put(Page1, summary)

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
	page = wikipedia.Page(site2, u'Template:' + pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
	'''
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site2, u'Template:' + pagename)
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
#TraitementFile = lecture('articles_test.txt')
#TraitementCategory = crawlerCat(u'')
TraitementLiens = crawlerLink(template)
#while 1:
#	TraitementRC = crawlerRC()
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.wikt.import.py
trouver le bon encodage pour les lettres à accent
Choisir flex-nom ou adj selon
pb avec bates, Englishes
'''

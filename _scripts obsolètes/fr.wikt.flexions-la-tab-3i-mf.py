#!/usr/bin/env python
# coding: utf-8
# Ce script crée des flexions depuis le modèle d'un lemme

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language1 = "fr"
family = "wiktionary"
site1 = getSite(language1,family)
template = u'la-tab-3i-mf'

# Modification du wiki
def modification(Page1):
	summary = u'Création des flexions latines depuis [[' + Page1 + u']]'
	#print (Page1.encode(config.console_encoding, 'replace'))
	page0 = Page(site1,Page1)
	if page0.namespace() != 0: return
	PageTitre = page0.title()
	PageTemp = page0.get()
	PageTemp2 = PageTemp[PageTemp.find(template)+len(template)+1:len(PageTemp)]
	PageTemp = PageTemp[0:PageTemp.find(template)]
	nature = PageTemp[PageTemp.rfind(u'{{-')+3:PageTemp.rfind(u'-|')]
	if nature != u'nom' and nature != u'flex-nom': return
	if PageTemp2.find(u'|sing=') < PageTemp2.find(u'}}') and PageTemp2.find(u'|sing=') > 0:
		radical = PageTemp2[PageTemp2.find(u'|')+1:PageTemp2.find(u'|sing=')]
	elif PageTemp2.find(u'|plur=') < PageTemp2.find(u'}}') and PageTemp2.find(u'|plur=') > 0:
		radical = PageTemp2[PageTemp2.find(u'|')+1:PageTemp2.find(u'|plur=')]
	else:
		radical = PageTemp2[PageTemp2.find(u'|')+1:PageTemp2.find(u'}}')]

	#print (radical.encode(config.console_encoding, 'replace'))
	#raw_input("1")	
	
	page1 = Page(site1,radical + u'em')
	if not page1.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Accusatif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Accusatif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page1.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)

	page2 = Page(site1,radical + u'is')
	if not page2.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Génitif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Génitif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page2.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)
		
	page3 = Page(site1,radical + u'i')
	if not page3.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# ''Datif singulier de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# ''Datif singulier de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page3.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)

	page4 = Page(site1,radical + u'e')
	if not page4.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Ablatif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Ablatif singulier de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page4.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)
		
	page5 = Page(site1,radical + u'es')
	if not page5.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Nominatif pluriel de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Vocatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Accusatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Nominatif pluriel de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Vocatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Accusatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page5.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)
		
	page6 = Page(site1,radical + u'um')
	if not page6.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Génitif pluriel de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# \'\'Génitif pluriel de\'\' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page6.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)
		
	page7 = Page(site1,radical + u'ibus')
	if not page7.exists():
		if nature[0:4] == u'flex':
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# ''Datif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Ablatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		else:
			PageTemp = u'== {{=la=}} ==\n{{-flex-' + nature + u'-|la}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||la}}\n# ''Datif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].\n# ''Ablatif pluriel de'' [[' + Page1 + u'#la-nom|' + Page1 + u']].'
		page7.put(PageTemp + u'\n' + CleDeTri(PageTitre), summary)
		
def CleDeTri(PageTitre):
	# Clés de tri
		PageT = ""
		key = "false"
		key2 = "false"
		for lettre in range(0,len(PageTitre)):	
			if PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä':
				PageT = PageT + "a"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'ë':
				PageT = PageT + "e"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'í' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ï':
				PageT = PageT + "i"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ó'  or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'ö':
				PageT = PageT + "o"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'ù' or PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ü':
				PageT = PageT + "u"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'æ':
				PageT = PageT + "ae"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'œ':
				PageT = PageT + "oe"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ñ':
				PageT = PageT + "n"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ÿ':
				PageT = PageT + "y"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ç':
				PageT = PageT + "c"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'-':
				PageT = PageT + " "
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'/':
				PageT = PageT + " "
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'\\':
				PageT = PageT + ""
				key = "yes"
			elif PageTitre[lettre:lettre+1].lower() == PageTitre[lettre:lettre+1]:
				PageT = PageT + PageTitre[lettre:lettre+1]
			else:
				PageT = PageT + PageTitre[lettre:lettre+1].lower()
				key2 = "yes"
		if key == "yes":
			return (u'\n{{clé de tri|' + PageT + u'}}\n')
		elif key2 == "yes":
			return (u'\n{{clé de tri}}\n')
		else:
			return u''

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
	page = wikipedia.Page(site1, u'Modèle:' + pagename)
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
#TraitementWord = modification(u'maciatus')
#TraitementFile = lecture('articles_test.txt')
#TraitementCategory = crawlerCat(u'')
TraitementLiens = crawlerLink(template)
#while 1:
#	TraitementRC = crawlerRC()
raw_input("Jackpot")

'''
cd "C:\Users\hbossot\Documents\Site\Personnel\mybot\pywikipedia"
python fr.wikt.flexions.py
'''

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
template = u'pl-décl-nom-cja' #pl-décl-adj-y
output = u'articles_listed_pl.txt'

# Modification du wiki
def modification(PageHS):
	summary = u'Création des flexions du polonais depuis [[' + PageHS + u']]'
	page = Page(site1,PageHS)
	if page.exists():
		if page.namespace() !=0 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				radical = page.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
	else:
		return
	if radical.find(u'{{-nom-|pl}}') == -1: return
	radical = radical[radical.find(template)+len(template)+1:len(radical)]
	radical = radical[0:radical.find(u'}}')]
	while radical[0:1] == u' ' or radical[0:1] == u'|':
		radical = radical[1:len(radical)]
	while radical[len(radical)-1:len(radical)] == u' ' or radical[len(radical)-1:len(radical)] == u'|':
		radical = radical[0:len(radical)-1]
	if radical != PageHS[0:len(PageHS)-2]:
		txtfile = codecs.open(output, 'a', 'utf-8')
		txtfile.write(u'* [[' + PageHS + u']]\n')
		txtfile.close()
		return
	# Flexions
	page1 = Page(site1,radical + u'je')
	if not page1.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Nominatif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].\n# \'\'Accusatif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].\n# \'\'Vocatif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page1.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
	page2 = Page(site1,radical + u'ji')
	if not page2.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Génitif singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].\n# \'\'Génitif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].\n# \'\'Datif singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].\n# \'\'Locatif singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page2.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
	page3 = Page(site1,radical + u'jom')
	if not page3.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Datif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page3.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)

	page4 = Page(site1,radical + u'ję')
	if not page4.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Accusatif singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page4.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
	page5 = Page(site1,radical + u'ją')
	if not page5.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Instrumental singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page5.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
	page6 = Page(site1,radical + u'jami')
	if not page6.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Instrumental pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page6.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
	page7 = Page(site1,radical + u'jach')
	if not page7.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Locatif pluriel de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page7.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)

	page8 = Page(site1,radical + u'jo')
	if not page8.exists():
		PageTemp = u'== {{=pl=}} ==\n{{-flex-nom-|pl}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||pl}}\n# \'\'Vocatif singulier de\'\' [[' + PageHS + u'#pl-nom|' + PageHS + u']].'
		page8.put(PageTemp + u'\n' + CleDeTri(PageHS), summary)
		
def CleDeTri(PageHS):
	# Clés de tri
		PageT = ""
		key = "false"
		for lettre in range(0,len(PageHS)):	
			if PageHS[lettre:lettre+1] == u'á' or PageHS[lettre:lettre+1] == u'à' or PageHS[lettre:lettre+1] == u'â' or PageHS[lettre:lettre+1] == u'ä' or PageHS[lettre:lettre+1] == u'ą':
				PageT = PageT + "a"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'æ':
				PageT = PageT + "ae"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ç' or PageHS[lettre:lettre+1] == u'ć':
				PageT = PageT + "c"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'é' or PageHS[lettre:lettre+1] == u'è' or PageHS[lettre:lettre+1] == u'ê' or PageHS[lettre:lettre+1] == u'ë' or PageHS[lettre:lettre+1] == u'ę':
				PageT = PageT + "e"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'í' or PageHS[lettre:lettre+1] == u'ì' or PageHS[lettre:lettre+1] == u'î' or PageHS[lettre:lettre+1] == u'ï':
				PageT = PageT + "i"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ñ' or PageHS[lettre:lettre+1] == u'ń':
				PageT = PageT + "n"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ó'  or PageHS[lettre:lettre+1] == u'ò' or PageHS[lettre:lettre+1] == u'ô' or PageHS[lettre:lettre+1] == u'ö':
				PageT = PageT + "o"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'œ':
				PageT = PageT + "oe"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ś':
				PageT = PageT + "s"
				key = "yes"	
			elif PageHS[lettre:lettre+1] == u'ú' or PageHS[lettre:lettre+1] == u'ù' or PageHS[lettre:lettre+1] == u'û' or PageHS[lettre:lettre+1] == u'ü':
				PageT = PageT + "u"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ÿ':
				PageT = PageT + "y"
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'ż':
				PageT = PageT + "z"
				key = "yes"				
			elif PageHS[lettre:lettre+1] == u'-':
				PageT = PageT + " "
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'/':
				PageT = PageT + " "
				key = "yes"
			elif PageHS[lettre:lettre+1] == u'\\':
				PageT = PageT + ""
				key = "yes"
			else:
				PageT = PageT + PageHS[lettre:lettre+1].lower()
		if key == "yes":
			return (u'\n{{clé de tri|' + PageT + u'}}\n')
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
TraitementLiens = crawlerLink(template)
'''
TraitementWord = modification(u'maciatus')
TraitementFile = lecture('articles_test.txt')
TraitementCategory = crawlerCat(u'')
while 1:
	TraitementRC = crawlerRC()
python fr.wikt.flexions-pl.py
'''
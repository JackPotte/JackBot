#!/usr/bin/env python
# Ce script signe les commentaires des pages de discussions.

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re
from wikipedia import *

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
	
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def lecture(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		modification(PageHS)
    PagesHS.close()
	
# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!= 1 and page.namespace()!= 3 and page.namespace()!= 5 and page.namespace()!= 7 and page.namespace()!= 9 and page.namespace()!= 11 and page.namespace()!= 13 and page.namespace()!= 15 and page.namespace()!= 103 and page.namespace()!= 109 and page.namespace()!= 111 and page.namespace()!= 113: 
			return
		else:
			url = u'http://' + language + u'.' + family + u'.org/w/api.php?action=query&prop=info|revisions&titles=%s&format=xml' % PageHS
			PageTemp = urllib.urlopen(url)		
			try:			
				infos = PageTemp.read()
				print (infos)
				raw_input("1")	
				reviseur = re.findall(' user="(.*?)" ',infos)
				PageTemp.close()			
				PageEnd = page.get()
				if PageEnd.find(u'{{supp') != -1 or PageEnd.find(u'{{nobots') != -1 or PageEnd.find(u'{{bots|deny=all') != -1: return
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return
		if not reviseur: return
		if PageEnd[len(PageEnd)-8:len(PageEnd)].rfind(u'(UTC)') != -1: return	
		#for chacun in reviseur:
		reviseur = str(reviseur)
		reviseur = reviseur[reviseur.find("'")+1:reviseur.rfind("'")]
		summary = u'Autosignature de ' + u'[[User:' + reviseur + u'|' + reviseur + u']]'
			
		date = re.findall(' timestamp="(.*?)" ',infos)
		date = str(date)
		date = date[date.find("'")+1:date.rfind("'")]
		date = date[0:date.find("T")] + u' ' + date[date.find("T")+1:date.find("Z")]
			
		PageEnd = PageEnd + u' {{non signé|' + reviseur + u'|' + date + u'}}'
		print (PageEnd.encode(config.console_encoding, 'replace'))
		raw_input("fin")
		page.put(PageEnd, summary)

# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		if Page.namespace() == 0: modification(u'Discussion:' + Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			if Page.namespace() == 0: modification(u'Discussion:' + Page.title())

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if Page.namespace() == 1: modification(Page.title())
		elif Page.namespace() == 0: modification(u'Discussion:' + Page.title())
		
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		if Page.namespace() == 1: modification(Page.title())

# Lancement
#TraitementFile = lecture('articles_list.txt')
#TraitementLink = crawlerLink(u'')
#TraitementCategory = crawlerCat(u'')
while 1:
	TraitementRC = crawlerRC()
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.wikt.signe.py
'''
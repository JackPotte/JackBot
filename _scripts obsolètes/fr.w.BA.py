#!/usr/bin/env python
# Ce script ajoute si besoin, les étoiles ADQ dans les liens interwikis des Wikis contenant les pages données dans articles_list.txt.
# Tous ces wikis doivent au préalable être mentionnés dans user-config.py

# Importation des modules
import os
from wikipedia import *
import catlib
import pagegenerators

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
langue = u'fr' # Langue de l'ADQ {{Link GA|fr}}
summary = u'{{Link GA|' + langue + u'}}'

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
	position = 0
	PageEnd = ""
	projet = "False"
	if page.exists():
		if page.title() != u'Utilisateur:JackBot/test' and page.namespace() != 0:
			return
		else:
			try:
				Page1 = page.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
		# Recherche des liens interwikis
		while Page1.rfind(u']]') != -1 and Page1.rfind(u':') != -1 and Page1.rfind(u'[[') != -1 and Page1.rfind(u'[[') > Page1.rfind(u'}}'):
			Lien = Page1[Page1.rfind(u'[['):len(Page1)]
			Mot = Lien[Lien.find(u':')+1:len(Lien)-2]
			codelangue = Lien[2:Lien.find(u':')]
			if codelangue != u'en': 
				break
			try:
				site2 = getSite(codelangue,family)
			except wikipedia.NoSuchSite:
				print (u'Pas de wiki : ' + codelangue)
				return
			try:
				page2 = Page(site2,Mot)
			except wikipedia.NoPage:
				print (u'Pas de mot : ' + Lien.encode(config.console_encoding, 'replace'))
			except wikipedia.BadTitle:
				print (u'Pas de mot : ' + Lien.encode(config.console_encoding, 'replace'))
			except wikipedia.IsRedirectPage:
				print (u'Pas de mot : ' + Lien.encode(config.console_encoding, 'replace'))
			except wikipedia.LockedPage:
				print (u'Page protégée : ' + Lien.encode(config.console_encoding, 'replace'))
			except wikipedia.UserBlocked:
				print u'Blocage sur ' + codelangue
			if page2.exists():
				try:
					Page2 = page2.get()
				except wikipedia.IsRedirectPage:
					print u'Redirection sur ' + codelangue
					return
				except wikipedia.InvalidTitle:
					print u'Titre incorrect sur ' + codelangue
					return							
				if Page2.find(u'{{Link GA|fr}}') != -1 and Page2.find(u'{{link FA|fr}}') != -1: # Nettoyage des doublons
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				#else voir http://en.wikipedia.org/wiki/Template:Link_FA
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Link AdQ|fr}}') != -1 or Page2.find(u'{{link AdQ|fr}}') != -1):  #it
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Destacato|fr}}') != -1 or Page2.find(u'{{destacato|fr}}') != -1): #an
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Destacado|fr}}') != -1 or Page2.find(u'{{destacado|fr}}') != -1): #es
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Enllaç AD|fr}}') != -1 or Page2.find(u'{{enllaç AD|fr}}') != -1): #ca
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Link UA|fr}}') != -1 or Page2.find(u'{{link UA|fr}}') != -1): #no
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and Page2.find(u'{{???? ????? ??????|fr}}') != -1: #ar
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and Page2.find(u'{{NA lotura|fr}}') != -1: #eu
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Legatura AF|fr}}') != -1 or Page2.find(u'{{legatura AF|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{LigoElstara|fr}}') != -1 or Page2.find(u'{{ligoElstara|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Tengill ÚG|fr}}') != -1 or Page2.find(u'{{tengill ÚG|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Nasc AR|fr}}') != -1 or Page2.find(u'{{nasc AR|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Cyswllt erthygl ddethol|fr}}') != -1 or Page2.find(u'{{cyswllt erthygl ddethol|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') != -1 and (Page2.find(u'{{Liên k?t ch?n l?c|fr}}') != -1 or Page2.find(u'{{liên k?t ch?n l?c|fr}}') != -1):
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link SM|fr}}') != -1 and (Page2.find(u'{{Link SM|fr}}') != -1 or Page2.find(u'{{Link SM|fr}}') != -1): #turc
					Page2 = Page2[0:Page2.find(u'{{Link GA|fr}}')] + Page2[Page2.find(u'{{Link GA|fr}}')+len(u'{{Link GA|fr}}')+1:len(Page2)]
					try:
						page2.put(Page2, summary)
					except wikipedia.LockedPage:
						print (u'Page protégée sur ' + codelangue)
					except wikipedia.UserBlocked:
						print u'Blocage sur ' + codelangue
				elif Page2.find(u'{{Link GA|fr}}') == -1 and Page2.find(u'{{link FA|fr}}') == -1 and Page2.find(u'{{Link AdQ|fr}}') == -1 and Page2.find(u'{{link AdQ|fr}}') == -1 and Page2.find(u'{{Destacato|fr}}') == -1 and Page2.find(u'{{destacato|fr}}') == -1 and Page2.find(u'{{Destacado|fr}}') == -1 and Page2.find(u'{{destacado|fr}}') == -1 and Page2.find(u'{{Enllaç AD|fr}}') == -1 and Page2.find(u'{{enllaç AD|fr}}') == -1 and Page2.find(u'{{Link UA|fr}}') == -1 and Page2.find(u'{{link UA|fr}}') == -1 and Page2.find(u'{{وصلة مقالة مختارة|fr}}') == -1 and Page2.find(u'{{NA lotura|fr}}') == -1 and Page2.find(u'{{Legătură AF|fr}}') == -1 and Page2.find(u'{{legătură AF|fr}}') == -1 and Page2.find(u'{{LigoElstara|fr}}') == -1 and Page2.find(u'{{ligoElstara|fr}}') == -1 and Page2.find(u'{{Tengill ÚG|fr}}') == -1 and Page2.find(u'{{tengill ÚG|fr}}') == -1 and Page2.find(u'{{Nasc AR|fr}}') == -1 and Page2.find(u'{{nasc AR|fr}}') == -1 and Page2.find(u'{{Cyswllt erthygl ddethol|fr}}') == -1 and Page2.find(u'{{cyswllt erthygl ddethol|fr}}') == -1 and Page2.find(u'{{Liên kết chọn lọc|fr}}') == -1 and Page2.find(u'{{liên kết chọn lọc|fr}}') == -1: # Certains wikis imposent leurs propres modèles ADQ
					if Page2.find(u'{{Link GA|' + langue + u'}}') != -1: # On remplace le modèle "Good Article" correspondant
						Page2 = Page2[0:Page2.find(u'{{Link FA|' + langue + u'}}')] + Page2[Page2.find(u'{{Link FA|' + langue + u'}}')+len(u'{{Link FA|' + langue + u'}}')+1:len(Page2)]
					if Page2.find(u'{{Link FL|' + langue + u'}}') != -1: # On remplace le modèle "Featured List" correspondant
						Page2 = Page2[0:Page2.find(u'{{Link FL|' + langue + u'}}')] + Page2[Page2.find(u'{{Link FL|' + langue + u'}}')+len(u'{{Link FL|' + langue + u'}}')+1:len(Page2)]					
					if Page2.find(u'{{Link GA|') != -1: 	# Si le paragraphe du modèle existe					
						PageTemp = Page2[Page2.find(u'{{Link GA|'):len(Page2)]
						longueur = len(PageTemp[0:PageTemp.rfind(u'}}')+3]) # Longueur des liens "Featured Article"
						PageTemp = PageTemp[0:PageTemp.rfind(u'}}')+3] + summary + u'\n'
						# Bug du classement alphabétique : PageTemp.sort(lambda x,y: cmp(x[4],y[4])) : 'unicode' object has no attribute 'sort'
						Page2 = Page2[0:Page2.find(u'{{Link GA|')] + PageTemp + Page2[Page2.find(u'{{Link GA|')+longueur:len(Page2)] 
						'''# Test dans un fichier
						txtfile = codecs.open("_test.txt", 'a', 'utf-8')
						txtfile.write(codelangue + u'\n' + page.title() + u' => ' + page2.title() + u'\n\n')
						txtfile.close()'''
					else:
						PageTemp = Page2[0:len(Page2)-2]
						while PageTemp[len(PageTemp)-2:len(PageTemp)] != u'\n\n' and len(PageTemp) > 0: 	# Sinon on remonte les interwikis
							PageTemp = PageTemp[0:len(PageTemp)-1]
						Page2 = Page2[0:len(PageTemp)] + summary + u'\n\n' + Page2[len(PageTemp):len(Page2)]
						'''# Test dans un fichier
						txtfile = codecs.open("_test.txt", 'a', 'utf-8')
						txtfile.write(codelangue + u'\n' + page.title() + u' => ' + page2.title() + u'\n\n')
						txtfile.close()'''
					if Page2 != page2.get():
						try:
							print (Page2.encode(config.console_encoding, 'replace'))
							raw_input("fin")
							page2.put(Page2, summary)
						except wikipedia.LockedPage:
							print (u'Page protégée sur ' + codelangue)
						except wikipedia.UserBlocked:
							print u'Blocage sur ' + codelangue
					else:
						print (u'Pas d\'action sur ' + codelangue)
				else:
					print (u'Déjà présent sur ' + codelangue)				
			Page1 = Page1[0:Page1.rfind(u'\n[[')]
			
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		modification(Page.title()) #crawlerLink(Page.title())
	'''subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())'''
			
# Traitement des pages liées
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
		
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,1000):
		modification(Page.title())

# Lancement
#TraitementFile = lecture('articles_list.txt')
#TraitementLiens = crawlerLink(u'')
#TraitementCategory = crawlerCat(u'Portail de qualité')
TraitementCategory = crawlerCat(u'Bon article')
'''
while 1:
	TraitementRC = crawlerRC()
raw_input("Jackpot")


cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.w.BA.py
cron avec redirect
'''
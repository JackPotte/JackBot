#!/usr/bin/env python
# coding: utf-8
# Ce script formate les pages de la Wikiversité :
# 1) Il retire les clés de tri devenues inutiles.
# 2) Il complète les modèles {{Chapitre}} à partir des {{Leçon}}.
# 3) Ajoute {{Bas de page}}.
# Reste à faire :
# 4) Remplir les {{Département}} à remplir à partir des {{Leçon}}.
# 5) Compléter les {{Bas de page}} existants.

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re, hyperlynx
from wikipedia import *

# Déclaration
language = "fr"
family = "wikiversity"
mynick = "JackBot"
site = getSite(language,family)
debogage = False
CorrigerModeles = False
sizeT = 3
sizeP = 12

temp = range(1, sizeT)
Ttemp = range(1, sizeT)
temp[1] = u'numero'
Ttemp[1] = u'numéro'

# Modèle:Chapitre
param = range(1, sizeP)
param[1] = u'titre ' # espace pour disambiguiser
param[2] = u'idfaculté'
param[3] = u' leçon'
param[4] = u'page'
param[5] = u'numero'
param[6] = u'précédent'
param[7] = u'suivant'
param[8] = u'align'
param[9] = u'niveau'
param[10] = u'titre_leçon'

# Modification du wiki
def modification(PageHS):
	summary = u'[[Aide:Syntaxe|Autoformatage]]'
	PageEnd = "" # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première
	page = Page(site,PageHS)
	print(PageHS.encode(config.console_encoding, 'replace'))
	if page.exists():
		try:
			PageBegin = page.get()
		except wikipedia.NoPage:
			print "NoPage"
			return
		except wikipedia.IsRedirectPage:
			print "Redirect page"
			return
		except wikipedia.LockedPage:
			print "Locked/protected page"
			return
	else:
		print u'Page inexistante'
		return
	PageTemp = PageBegin
	PageTemp = u'{{bleu|abattement [abatmɑ̃] (fr \nom masculin\ fatigue, diminution)}} {{rouge|abatement [əbeɪtmənt] (en \nom\ réduction)}}'
	# Différence des noeuds entre manuels en JSON et auto via dump XML
'''
	{
		"faux-amis": {
			{
				"langue": "fr",
				"mot": "abattement",
				"prononciation": "abatmɑ̃",
				"sens": "fatigue, diminution"
			}
			{
				"langue": "en",
				"mot": "abatement",
				"prononciation": "əbeɪtmənt",
				"sens": "réduction"
			}
		}
	}
'''
	PageEnd = PageEnd + PageTemp
	PageTemp = u''
	
	# Test des URL
	if debogage == True: print u'Test des URL'
	PageEnd = hyperlynx.hyperlynx(PageEnd)
	if debogage == True: raw_input (u'--------------------------------------------------------------------------------------------')
	
	if PageBegin != PageEnd: sauvegarde(page, PageEnd, summary)

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
        arrettitle = ''.join(u'Discussion utilisateur:JackBot')
        arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
        gen = iter([arretpage])
        arret = arretpage.get()
        if arret != u"{{/Stop}}":
                pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
                exit(0)

def Valeur(Mot,Page):
	#raw_input(u'Bug http://fr.wikiversity.org/w/index.php?title=Initiation_%C3%A0_l%27arithm%C3%A9tique/PGCD&diff=prev&oldid=386685')
	if re.search(u'\n *' + Mot + u' *=', Page):
		niveau = re.sub(u'\n *' + Mot + u' *=()[\n|\||}|{]', ur'$1', Page)
		if debogage == True: raw_input(niveau)
		#return
	'''
	if Page.find(u' ' + Mot) != Page.find(Mot)-1 and Page.find(u'|' + Mot) != Page.find(Mot)-1: # Pb du titre_leçon
		PageTemp2 = Page[Page.find(Mot)+len(Mot):len(Page)]
	else:
		PageTemp2 = Page
	if PageTemp2.find(Mot) == -1:
		return u''
	else:
		PageTemp2 = PageTemp2[PageTemp2.find(Mot)+len(Mot):len(PageTemp2)]
		PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
		if PageTemp2.find (u'{{C|') != -1:		
			PageTemp2 = PageTemp2[PageTemp2.find (u'{{C|')+4:len(PageTemp2)]
			PageTemp2 = u'[[../' + PageTemp2[0:PageTemp2.find (u'|')] + u'/]]'
		while PageTemp2[0:1] == u' ' or PageTemp2[0:1] == u'\t' or PageTemp2[0:1] == u'=':
			PageTemp2 = PageTemp2[1:len(PageTemp2)]
		if PageTemp2[0:3] == u'[[/':		
			PageTemp2 = u'[[..' + PageTemp2[2:len(PageTemp2)]
		return PageTemp2
	'''			
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			if PageHS.find(u'[[') != -1:
				PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
			if PageHS.find(u']]') != -1:
				PageHS = PageHS[0:PageHS.find(u']]')]
			modification(PageHS)
		PagesHS.close()
		
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		modification(Page.title()) #crawlerLink(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())
		
# Traitement des pages liées
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage:
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
			
# Lancement
TraitementFile = crawlerFile('articles_WVin.txt')
#TraitementLiens = crawlerLink(u'Modèle:Clé de tri')
#TraitementLiens = crawlerLink(u'Modèle:cite book')
'''
TraitementPage = modification(u'Initiation_à_l\'arithmétique/PGCD')
TraitementFile = crawlerFile('articles_list.txt')
TraitementCategory = crawlerCat(u'Modèle mal utilisé')
TraitementLiens = crawlerLink(u'Modèle:Chapitre')
TraitementLiens = crawlerLink(u'Modèle:CfExo')
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementRecherche = crawlerSearch(u'chinois')
while 1:
	TraitementRC = crawlerRC()
'''

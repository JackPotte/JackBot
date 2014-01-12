#!/usr/bin/env python
# Ce script :
# 	Ajoute les {{DEFAULTSORT:}} dans les articles (attente de consensus pour les évaluations)
# 	Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
# 	Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
#	Vérifie les hyperliens
# A terme peut-être :
# 	Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...)
# 	Mettra à jour les évaluations à partir du bandeau ébauche
# 	Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto)
# {{Date|3|M->mai|2012}}

# Importation des modules
import os, catlib, pagegenerators, re
import hyperlynx, CleDeTri, HTMLUnicode		# Faits maison
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
debogage = True
debogageLent = False
input = u'articles_WPin.txt'
output = u'articles_WPout.txt'
ns = 0

# Modification du wiki
def modification(PageHS):
	summary = u'Formatage'
	page = Page(site,PageHS)
	print(PageHS.encode(config.console_encoding, 'replace'))
	if not page.exists(): return
	if page.namespace() != ns and page.title().find(u'Utilisateur:JackBot/test') == -1:
		return
	else:
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
	PageTemp = PageBegin
	PageEnd = u''
	
	# Traitements des URL et leurs modèles
	if debogage == True: print u'Test des URL'
	PageTemp = hyperlynx.hyperlynx(PageTemp)
	if debogage == True: raw_input (u'--------------------------------------------------------------------------------------------')
	if PageTemp != PageBegin:
		summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/11#Identifier les liens brisés (le retour ;-))|Vérification des liens externes]]'
		summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer_les_.7B.7BCite_web.7D.7D_par_.7B.7BLien_web.7D.7D|traduction de leurs modèles]]'

	# Nombres
	PageTemp = re.sub(ur'{{ *(formatnum|Formatnum|FORMATNUM)\:([0-9]*) *([0-9]*)}}', ur'{{\1:\2\3}}', PageTemp)
	'''Semi-auto
	if re.search(ur'(¤|₳|฿|¢|₡|₵|₢|₫|€|ƒ|₣|₲|₭|£|₤|₥|₦|₱|\$|₮|₩|¥|Ƶ|₯|₴|₪|₠|₰)([0-9]+)(&nbsp;| )*([0-9]+)?[.,]([0-9]+)(&nbsp;| +)?', PageTemp):
		summary = summary + u', [[Wikipédia:Bot/Requêtes/2013/03#.7B.7BRequ.C3.AAte_en_cours.7D.7D_Mille_millions_de_mille_sabords_.28et_pas_Sabords_mille_millions_de_mille_sabords.29|symbole monétaire]]'
		PageTemp = re.sub(ur'(¤|₳|฿|¢|₡|₵|₢|₫|€|ƒ|₣|₲|₭|£|₤|₥|₦|₱|\$|₮|₩|¥|Ƶ|₯|₴|₪|₠|₰)([0-9]+)(&nbsp;| )*([0-9]+)?[.,]([0-9]+)(&nbsp;| +)?', ur'{{unité|$2$4.$5|$1}}', PageTemp)
	'''
	# Analyse des crochets et accolades (à faire : hors LaTex)
	if PageTemp.count('{') - PageTemp.count('}') != 0:
		if PageHS.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + PageHS + u']] : accolade cassée')
		#if debogageLent == True: raise Exception(u'Accolade cassée')
	if PageTemp.count('[') - PageTemp.count(']') != 0:
		if PageHS.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + PageHS + u']] : crochet cassé')
		#if debogageLent == True: raise Exception(u'Crochet cassé')
	if PageBegin.count('[[') - PageBegin.count(']]') != PageTemp.count('[[') - PageTemp.count(']]'):
		txtfile = codecs.open(output, 'a', 'utf-8')
		txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
		txtfile.close()	
		if debogage == False: raise Exception(u'Crochets cassés')
	if PageBegin.count('{{') - PageBegin.count('}}') != PageTemp.count('{{') - PageTemp.count('}}'):
		txtfile = codecs.open(output, 'a', 'utf-8')
		txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
		txtfile.close()	
		if debogage == False: raise Exception(u'Accolades cassées')
		
	# En travaux : déplacement par étapes de PageTemp vers PageEnd en s'arrêtant sur chaque point à modifier
	'''positionW = -1
	if PageTemp.find(u'{{Sigle') != -1:
		PageTemp2 = PageTemp[PageTemp.find(u'{{Sigle'):len(PageTemp)]
		positionW = PageTemp.find(u'{{Sigle')+PageTemp2.find(u'\n')+1
	elif PageTemp.find(u'{{sigle') != -1:
		PageTemp2 = PageTemp[PageTemp.find(u'{{sigle'):len(PageTemp)]
		positionW = PageTemp.find(u'{{sigle')+PageTemp2.find(u'\n')+1
	elif PageTemp.find(u'{{Homonymie}}\n') != -1:
		positionW = PageTemp.find(u'{{Homonymie}}\n')+len(u'{{Homonymie}}\n')
	elif PageTemp.find(u'{{homonymie}}\n') != -1:
		positionW = PageTemp.find(u'{{homonymie}}\n')+len(u'{{homonymie}}\n')
	elif PageTemp.find(u'{{Titres homonymes}}\n') != -1:
		positionW = PageTemp.find(u'{{Titres homonymes}}\n')+len(u'{{Titres homonymes}}\n')
	elif PageTemp.find(u'{{titres homonymes}}\n') != -1:
		positionW = PageTemp.find(u'{{titres homonymes}}\n')+len(u'{{titres homonymes}}\n')		
	elif PageTemp.find(u'{{Communes') != -1:
		positionW = PageTemp.find(u'{{Communes')
	elif PageTemp.find(u'{{communes') != -1:
		positionW = PageTemp.find(u'{{communes')
	elif PageTemp.find(u'{{Patronyme') != -1:
		positionW = PageTemp.find(u'{{Patronyme')
	elif PageTemp.find(u'{{patronyme') != -1:
		positionW = PageTemp.find(u'{{patronyme')		
	elif PageTemp.find(u'=== Liens externes ===\n') != -1:
		positionW = PageTemp.find(u'=== Liens externes ===\n')+len(u'=== Liens externes ===\n')
	elif PageTemp.find(u'== Voir aussi ==\n') != -1:
		positionW = PageTemp.find(u'== Voir aussi ==\n')+len(u'== Voir aussi ==\n')
	elif PageTemp.find(u'{{Palette') != -1:
		positionW = PageTemp.find(u'{{Palette')
	elif PageTemp.find(u'{{palette') != -1:
		positionW = PageTemp.find(u'{{palette')
	elif PageTemp.find(u'{{Portail') != -1:
		positionW = PageTemp.find(u'{{Portail')
	elif PageTemp.find(u'{{portail') != -1:
		positionW = PageTemp.find(u'{{portail')
	elif PageTemp.find(u'[[Catégorie:') != -1:
		positionW = PageTemp.find(u'[[Catégorie:')
	elif re.compile('\[\[[a-z][^wikts]+:[^\[\]\n]+\]\]').search(PageTemp):
		try:
			i1 = re.search('\[\[[a-z][^wikts]+:[^\[\]\n]+\]\]',PageTemp).start()
			positionW = len(PageTemp[:i1])
		except:
			print u'pb regex interwiki'
	else:
		positionW = 0'''

	if PageTemp.find(u'{{DEFAULTSORT:') == -1 and PageTemp.find(u'{{CLEDETRI:') == -1 and ns == 0:
		ClePage = CleDeTri.CleDeTri(PageHS)
		if ClePage != u'' and ClePage != None and ClePage != PageHS:
			''' if PageTemp.find(u'né en ...')
				if PageHS.rfind(u' ') != -1:
					Nom = PageHS[PageHS.rfind(u' ')+1:len(PageHS)]
					PageHS2 = PageHS[PageHS.find(u'/')+1:len(PageHS)]
					PageHS2 = PageHS2[PageHS2.find(u'/')+1:len(PageHS2)]
					Prenom = PageHS2[PageHS2.find(u'/')+1:len(PageHS2)]
					Prenom = Prenom[Prenom.find(u'/')+1:len(Prenom)]
					Prenom = Prenom[0:Prenom.find(u' ')]
					print PageHS2
					print Nom
					print Prenom
					if Nom[0:1] == PageHS2[0:1]:
						PageEnd = PageEnd + u'{{DEFAULTSORT:' + CleDeTri.CleDeTri(Nom) + u', ' + CleDeTri.CleDeTri(Prenom) + u'}}\n\n'
					else:
						print PageHS.encode(config.console_encoding, 'replace')
				else:
					print PageHS.encode(config.console_encoding, 'replace')
			else:'''	
			if PageTemp.find(u'[[Catégorie:') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'[[Catégorie:')] + u'\n{{DEFAULTSORT:' + ClePage + u'}}\n' + PageTemp[PageTemp.find(u'[[Catégorie:'):len(PageTemp)]
			elif PageTemp.find(u'[[Category:') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'[[Category:')] + u'\n{{DEFAULTSORT:' + ClePage + u'}}\n' + PageTemp[PageTemp.find(u'[[Category:'):len(PageTemp)]
			else:	# Avant interwikis
				if re.compile('\[\[[a-z][^wsq]+:[^\[\]\n]+\]\]').search(PageTemp):
					try:
						i1 = re.search('\[\[[a-z][^wsq]+:[^\[\]\n]+\]\]',PageTemp).start()
						PageTemp = PageTemp[:i1] + u'\n{{DEFAULTSORT:' + ClePage + u'}}\n\n' + PageTemp[i1:]
					except:
						print u'pb regex interwiki'
				else:
					PageTemp = PageTemp + u'\n\n{{DEFAULTSORT:' + ClePage + u'}}\n'			
	else:
		PageTemp2 = PageTemp[PageTemp.find(u'{{DEFAULTSORT'):len(PageTemp)]
		ClePage = PageTemp2[PageTemp2.find(u'|')+1:PageTemp2.find(u'}}')]
		if CleDeTri.CleDeTri(PageHS) != ClePage and debogage == True:
			print (u'Fausse clé de tri dans :')
			print (PageHS.encode(config.console_encoding, 'replace'))
			print (ClePage.encode(config.console_encoding, 'replace'))
	
	#raw_input(PageEnd.encode(config.console_encoding, 'replace'))	
	PageEnd = PageEnd + PageTemp
	if PageEnd != PageBegin:
		PageEnd = re.sub(ur'<br>', ur'<br/>', PageEnd)
		sauvegarde(page,PageEnd,summary)
 
# Traitement d'une catégorie
def crawlerCat(category):
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		main = Page.title()
		main = main[11:len(main)]
		modification(main)
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			#if not crawlerFile(Page.title()):
			main = Page.title()
			main = main[11:len(main)]
			modification(main)

# Traitement des pages liées			
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if Page.namespace() == 1: modification(Page.title())
		elif Page.namespace() == 0: modification(u'Discussion:' + Page.title())

# Blacklist
def crawlerFile(PageCourante):
    PagesHS = open(u'BL.txt', 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': 
			break
		elif PageHS == PageCourante: 
			return "False"
    PagesHS.close()
	
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
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
		for subcategory in subcat:
			pages = subcategory.articlesList(False)
			for Page in pagegenerators.PreloadingGenerator(pages,100):
				modification(Page.title())

# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [ns])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
	modifier = u'False'
	cat = catlib.Category(site, pagename)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = ns)
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

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=ns, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=ns,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def log(source):		
	txtfile = codecs.open(output, 'a', 'utf-8')
	txtfile.write(source + u'\n')
	txtfile.close()
	
def filtre(projets,langue,PageHS):
	projets2 = projets[projets.find(langue + u'='):len(projets)]
	if projets2.find(u'\n') == -1:
		return projets[0:projets.find(langue + u'=')] + u'w=' + PageHS
	else:
		return projets[0:projets.find(langue + u'=')] + u'w=' + PageHS + projets[projets.find(langue + u'=')+projets2.find(u'\n'):len(projets)]			

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

def sauvegarde(PageCourante, Contenu, Resume):
	try:
		result = "ok"
		#print(Contenu.encode(config.console_encoding, 'replace'))
		#result = raw_input("Sauvegarder ? (o/n)")
		if result != "n" and result != "no" and result != "non":
			# if len(Contenu) > 90000: log(Contenu)	# HTTPError: 504 Gateway Time-out
			if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
			if not Resume: Resume = summary
			PageCourante.put(Contenu, Resume)
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

# Lancement quotidient :
#TraitementPage = modification(u'Poncke Princen') 
#TraitementLiens = crawlerLink(u'Modèle:Cite book',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite web',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite journal',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite news',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite press release',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite episode',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite video',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite conference',u'')
TraitementLiens = crawlerLink(u'Modèle:Cite arXiv',u'')
TraitementLiens = crawlerLink(u'Modèle:Lien news',u'')
TraitementLiens = crawlerLink(u'Modèle:Lien mort',u'')
TraitementLiens = crawlerLink(u'Modèle:Docu',u'')
TraitementLiens = crawlerLink(u'Modèle:Cita web',u'')
TraitementLiens = crawlerLink(u'Modèle:Cita noticia',u'')
'''
TraitementRecherche = crawlerSearch(u'Finnish')
TraitementRecherche = crawlerSearch(u'Indonesian')
TraitementRecherche = crawlerSearch(u'Hindi')
TraitementRecherche = crawlerSearch(u'Arabic')

TraitementRecherche = crawlerSearch(u'French')
TraitementRecherche = crawlerSearch(u'English')
TraitementRecherche = crawlerSearch(u'German')
TraitementRecherche = crawlerSearch(u'Spanish')
TraitementRecherche = crawlerSearch(u'Italian')
TraitementRecherche = crawlerSearch(u'Portuguese')
TraitementRecherche = crawlerSearch(u'Dutch')
TraitementRecherche = crawlerSearch(u'Russian')
TraitementRecherche = crawlerSearch(u'Chinese')
TraitementRecherche = crawlerSearch(u'Japanese')
TraitementRecherche = crawlerSearch(u'Polish')
TraitementRecherche = crawlerSearch(u'Norwegian')
TraitementRecherche = crawlerSearch(u'Swedish')

TraitementRecherche = crawlerSearch(u'January')
TraitementRecherche = crawlerSearch(u'February')
TraitementRecherche = crawlerSearch(u'March')
TraitementRecherche = crawlerSearch(u'April')
TraitementRecherche = crawlerSearch(u'May')
TraitementRecherche = crawlerSearch(u'June')
TraitementRecherche = crawlerSearch(u'July')
TraitementRecherche = crawlerSearch(u'August')
TraitementRecherche = crawlerSearch(u'September')
TraitementRecherche = crawlerSearch(u'October')
TraitementRecherche = crawlerSearch(u'November')
TraitementRecherche = crawlerSearch(u'December')
#TraitementCategory = crawlerCat(u'Page du modèle Article comportant une erreur',False,u'')

#Modeles :
TraitementFile = crawlerFile(input)
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementPage = modification(u'Utilisateur:JackBot/test/À faire')
TraitementLiens = crawlerLink(u'Modèle:ko-hanja')
TraitementRecherche = crawlerSearch(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
	TraitementRC = crawlerRC()
'''
#ajouter : python cosmetic_changes.py -lang:"fr" -recentchanges
#défaultsort : http://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial%3AToutes+les+pages&from=%C3%A9&to=&namespace=14
# traiter les liens vers WP ([[ ]] + {{lien|lang=}}) + mai 27, 2010 -> 27 mai 2010 ou 2010-05-27
#(¤|₳|฿|¢|₡|₵|₢|₫|€|ƒ|₣|₲|G€|₭|k€|£|₤|₥|₦|₱|₧|₨|\$|₮|₩|¥|Ƶ|₯|₴|₪|₠|₰)[0-9]+
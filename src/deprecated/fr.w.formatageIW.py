#!/usr/bin/env python
# Ce script :
# 	Ajoute les {{DEFAULTSORT:}} dans les articles (attente de consensus pour les évaluations)
# 	Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
# 	Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
# A terme peut-être :
# 	Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...)
# 	Mettra à jour les évaluations à partir du bandeau ébauche
# 	Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto)

# Importation des modules
import os, catlib, pagegenerators, re
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
NomSites = range(1,8)
NomSites[1] = u'wiktionary'	 # à faire : utiliser {{WP}} au lieu de {{Autres projets
NomSites[2] = u'wikibooks'	 # à faire : lier les recettes de cuisine avec WP et WT
NomSites[3] = u'wikiversity'
NomSites[4] = u'wikinews'
NomSites[5] = u'wikisource'
NomSites[6] = u'wikiquote'
sites = range(1,8)
sites[1] = getSite(language,u'wiktionary')
sites[2] = getSite(language,u'wikibooks')
sites[3] = getSite(language,u'wikiversity')
sites[4] = getSite(language,u'wikinews')
sites[5] = getSite(language,u'wikisource')
sites[6] = getSite(language,u'wikiquote')
codes = range(1,8)
codes[1] = u'wikt'
codes[2] = u'b'
codes[3] = u'v'
codes[4] = u'n'
codes[5] = u's'
codes[6] = u'q'
pages = range(1,8)
PageTempSites = range(1,8)

# Modification du wiki
def modification(PageHS):
	summary = u'[[Aide:Comment rédiger un bon article|Autoformatage]]'
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace()!=0 and page.namespace()!=14 and page.title() != u'Utilisateur:JackBot/test': 
			return	# if page.namespace()!=cat
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
	else:
		return
	PageTemp = PageBegin
	PageEnd = u''
	projets = u''
	# Déplacement par étapes de PageTemp vers PageEnd en s'arrêtant sur chaque point à modifier
	positionW = -1
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
		positionW = 0
	if positionW != -1:
		if PageHS.find(u' (homonymie)') != -1:
			NomPageHS = PageHS[0:PageHS.find(u' (homonymie)')]
			homonymie = u'True'
		else:
			NomPageHS = PageHS
			homonymie = u'False'
		# Premier balayage des projets frères pour lecture
		for s in range(1,7):
			pages[s] = Page(sites[s],NomPageHS)
			if pages[s].exists():
				try:
					PageTempSites[s] = pages[s].get()
					projets = projets + u'\n|' + codes[s] + u'=' + NomPageHS
				except wikipedia.NoPage:
					PageTempSites[s] = -1
					break
				except wikipedia.IsRedirectPage:
					PageTempSites[s] = -1
					break
			else: 
				pages[s] = Page(sites[s],NomPageHS[0:1].lower() + NomPageHS[1:len(NomPageHS)])
				if pages[s].exists():
					try:
						PageTempSites[s] = pages[s].get()
						projets = projets + u'\n|' + codes[s] + u'=' + NomPageHS[0:1].lower() + NomPageHS[1:len(NomPageHS)]
					except wikipedia.NoPage:
						PageTempSites[s] = -1
						break
					except wikipedia.IsRedirectPage:
						PageTempSites[s] = -1
						break
				else:
					pages[s] = Page(sites[s],NomPageHS.lower())
					if pages[s].exists():
						try:
							PageTempSites[s] = pages[s].get()
							projets = projets + u'\n|' + codes[s] + u'=' + NomPageHS.lower()
						except wikipedia.NoPage:
							PageTempSites[s] = -1
							break
						except wikipedia.IsRedirectPage:
							PageTempSites[s] = -1
							break
					else: 
						pages[s] = Page(sites[s],NomPageHS + u's')
						if pages[s].exists():
							try:
								PageTempSites[s] = pages[s].get()
								projets = projets + u'\n|' + codes[s] + u'=' + NomPageHS + u's'
							except wikipedia.NoPage:
								PageTempSites[s] = -1
								break
							except wikipedia.IsRedirectPage:
								PageTempSites[s] = -1
								break
						else:
							pages[s] = Page(sites[s],u'Catégorie:' + NomPageHS)
							if pages[s].exists():
								try:
									PageTempSites[s] = pages[s].get()
									projets = projets + u'\n|' + codes[s] + u'=Catégorie:' + NomPageHS
								except wikipedia.NoPage:
									PageTempSites[s] = -1
									break
								except wikipedia.IsRedirectPage:
									PageTempSites[s] = -1
									break					
							else:
								PageTempSites[s] = -1
		#raw_input(projets.encode(config.console_encoding, 'replace'))
		if projets != u'':
			if PageTemp.find(u'{{Autres projets') != -1:
				print (u'MAJ en travaux')
				#PageTemp2 = PageTemp[PageTemp.find(u'{{Autres projets|')+len(u'{{Autres projets|'):len(PageTemp)]
				#PageTemp = PageTemp[0:PageTemp.find(u'{{Autres projets|')] + u'{{Autres projets' + projets + u'}}\n' + PageTemp[PageTemp.find(u'{{Autres projets|')+len(u'{{Autres projets|')+PageTemp2.find(u'}}')+2:len(PageTemp)]
			elif PageTemp.find(u'{{autres projets') != -1:
				print (u'MAJ en travaux')
				#PageTemp2 = PageTemp[PageTemp.find(u'{{autres projets|')+len(u'{{autres projets|'):len(PageTemp)]
				#PageTemp = PageTemp[0:PageTemp.find(u'{{autres projets|')] + u'{{autres projets' + projets + u'}}\n' + PageTemp[PageTemp.find(u'{{autres projets|')+len(u'{{autres projets|')+PageTemp2.find(u'}}')+2:len(PageTemp)]
			elif PageTemp.find(u'{{Commonscat') != -1:
				print (u'MAJ en travaux')
				#PageTemp2 = PageTemp[PageTemp.find(u'{{Commonscat|')+len(u'{{Commonscat|'):len(PageTemp)]
			elif PageTemp.find(u'{{commonscat') != -1:
				print (u'MAJ en travaux')
				#PageTemp2 = PageTemp[PageTemp.find(u'{{commonscat|')+len(u'{{commonscat|'):len(PageTemp)]
			elif PageTemp.find(u'{{Projets Wikimedia') != -1:
				print "Accueil"	# pb
			else:
				if homonymie == u'True':
					# Ajout des paramètres |titre= dans {{autres projets}} pour la cosmétique
					projets2 = projets
					projetsWP = u''
					for s in range(1,7):
						if projets2.find(codes[s] + u'=') != -1:
							projetsWP = projetsWP + projets2[0:projets2.find(codes[s] + u'=')+len(codes[s] + u'=')]
							projets2 = projets2[projets2.find(codes[s] + u'=')+len(codes[s] + u'='):len(projets2)]
							if projets2.find(u'\n') != -1:
								projetsWP = projetsWP + projets2[0:projets2.find(u'\n')] + u'|' + NomSites[s] + u' titre=' + NomPageHS
								projets2 = projets2[projets2.find(u'\n'):len(projets2)]							
							else:	# Dernière ligne du modèle
								projetsWP = projetsWP + projets2 + u'|' + NomSites[s] + u' titre=' + NomPageHS
					PageTemp = PageTemp[0:positionW] + u'{{Autres projets' + projetsWP + u'}}\n' + PageTemp[positionW:len(PageTemp)]
				else:
					# {{autres projets}} sans aucun |titre=
					PageTemp = PageTemp[0:positionW] + u'{{Autres projets' + projets + u'}}\n' + PageTemp[positionW:len(PageTemp)]
				summary = u'Interwikis francophones'
		#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		# Deuxième balayage des projets frères pour écriture
		for s in range(1,7):
			#print PageTempSites[s].encode(config.console_encoding, 'replace')
			if PageTempSites[s] != -1 and PageTempSites[s].find(u'{{Autres projets') == -1 and PageTempSites[s].find(u'{{Projets Wikimedia') == -1:
				if s == 1:	# wikt
					projetsW = filtre(projets,u'wikt',PageHS)
					PageTemp2 = u''
					if PageTempSites[s].find(u'{{=fr=}}') != -1:
						position = PageTempSites[s].find(u'{{=fr=}}')+len(u'{{=fr=}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					elif PageTempSites[s].find(u'{{=conv=}}') != -1:
						position = PageTempSites[s].find(u'{{=conv=}}')+len(u'{{=conv=}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					elif PageTempSites[s].find(u'{{-car-}}') != -1:
						position = PageTempSites[s].find(u'{{-car-}}')+len(u'{{-car-}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					elif PageTempSites[s].find(u'{{langue|fr}}') != -1:
						position = PageTempSites[s].find(u'{{langue|fr}}')+len(u'{{langue|fr}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					elif PageTempSites[s].find(u'{{langue|conv}}') != -1:
						position = PageTempSites[s].find(u'{{langue|conv}}')+len(u'{{langue|conv}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					elif PageTempSites[s].find(u'{{caractère}}') != -1:
						position = PageTempSites[s].find(u'{{caractère}}')+len(u'{{caractère}}')
						PageTemp2 = PageTempSites[s][position:len(PageTempSites[s])]
					if PageTemp2 != u'':
						if PageTempSites[s].find(u'{{Autres projets') == -1:
							if PageTempSites[s].find(u'{{WP') == -1:
								if PageTemp2.find(u'{{-voir-}}\n') != -1 and ((PageTemp2.find(u'{{=') != -1 and PageTemp2.find(u'{{-voir-}}\n') < PageTemp2.find(u'{{=')) or PageTemp2.find(u'{{=') == -1) and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'{{-voir-}}\n') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
									PageTempSites[s] = PageTempSites[s][0:position+PageTemp2.find(u'{{-voir-}}\n')+len(u'{{-voir-}}\n')] + u'{{Autres projets' + projetsW + u'}}\n' + PageTempSites[s][position+PageTemp2.find(u'{{-voir-}}\n')+len(u'{{-voir-}}\n'):len(PageTempSites[s])]
								elif PageTemp2.find(u'{{-réf-}}') != -1 and ((PageTemp2.find(u'{{=') != -1 and PageTemp2.find(u'{{-réf-}}') < PageTemp2.find(u'{{=')) or PageTemp2.find(u'{{=') == -1) and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'{{-réf-}}') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
									PageTempSites[s] = PageTempSites[s][0:position+PageTemp2.find(u'{{-réf-}}')] + u'{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n' + PageTempSites[s][position+PageTemp2.find(u'{{-réf-}}'):len(PageTempSites[s])]
								elif PageTemp2.find(u'\n==') != -1 and ((PageTemp2.find(u'[[Catégorie:') != -1 and PageTemp2.find(u'\n==') < PageTemp2.find(u'[[Catégorie:')) or PageTemp2.find(u'[[Catégorie:') == -1):
									PageTempSites[s] = PageTempSites[s][0:position+PageTemp2.find(u'\n==')] + u'\n{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n\n' + PageTempSites[s][position+PageTemp2.find(u'\n=='):len(PageTempSites[s])]						
								elif PageTemp2.find(u'{{clé de tri') != -1:
									PageTempSites[s] = PageTempSites[s][0:position+PageTemp2.find(u'{{clé de tri')] + u'\n{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n' + PageTempSites[s][position+PageTemp2.find(u'{{clé de tri'):len(PageTempSites[s])]
								elif PageTemp2.find(u'[[Catégorie:') != -1:
									PageTempSites[s] = PageTempSites[s][0:position+PageTemp2.find(u'[[Catégorie:')] + u'\n{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n\n' + PageTempSites[s][position+PageTemp2.find(u'[[Catégorie:'):len(PageTempSites[s])]
								else:
									regex = ur'\[\[(.+?)(?:\]\]\n)'	# Avant interwikis ^w^wikt^b^n^s^q
									if re.compile(regex).search(PageTempSites[s]):
										try:
											PageTempSites[s] = PageTempSites[s][0:re.search(regex,PageTempSites[s]).end()] + u'\n{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n' + PageTempSites[s][re.search(regex,PageTempSites[s]).end():len(PageTempSites[s])]
										except:
											print u'pb regex interwiki'
									else:
										PageTempSites[s] = PageTempSites[s] + u'\n\n{{-voir-}}\n{{Autres projets' + projetsW + u'}}\n'
							else: 
								PageTempSites[s] = -1
						else: 
							PageTempSites[s] = -1	
					else: 
						PageTempSites[s] = -1
				elif s == 3:	# v
					projetsV = filtre(projets,u'v',PageHS)
					if PageTempSites[s].find(u'Autres projets') == -1 and PageTempSites[s].find(u'autres projets') == -1:
						if PageTempSites[s].find(u'{{Leçon\n') != -1:
							PageTempSites[s] = PageTempSites[s][0:PageTempSites[s].find(u'{{Leçon\n')+len(u'{{Leçon\n')] + u'|autres projets=oui' + projetsV + u'\n' + PageTempSites[s][PageTempSites[s].find(u'{{Leçon\n')+len(u'{{Leçon\n'):len(PageTempSites[s])]
						elif PageTempSites[s].find(u'{{leçon') != -1:
							PageTempSites[s] = PageTempSites[s][0:PageTempSites[s].find(u'{{leçon\n')+len(u'{{leçon\n')] + u'|autres projets=oui' + projetsV + u'\n' + PageTempSites[s][PageTempSites[s].find(u'{{leçon\n')+len(u'{{leçon\n'):len(PageTempSites[s])]
						else:
							PageTempSites[s] = u'{{Autres projets' + projetsV + u'}}\n' + PageTempSites[s]
					else: 
						PageTempSites[s] = -1							
				elif s == 5:	# s
					print "s"
					projetsS = filtre(projets,u's',PageHS)
					if PageTempSites[s].find(u'{{Interprojet') == -1 and PageTempSites[s].find(u'{{interprojet') == -1:
						PageTempSites[s] = u'{{Interprojet' + projetsS + u'}}\n' + PageTempSites[s]
					else: 
						PageTempSites[s] = -1							
				elif s == 2:	# b
					projetsB = filtre(projets,u'b',PageHS)
					if PageTempSites[s].find(u'{{Autres projets') == -1 and PageTempSites[s].find(u'{{autres projets') == -1:
						PageTempSites[s] = u'{{Autres projets' + projetsB + u'}}\n' + PageTempSites[s]
					else: 
						PageTempSites[s] = -1
				elif s == 4:	# n
					projetsS = filtre(projets,u'n',PageHS)
					if PageTempSites[s].find(u'{{Autres projets') == -1 and PageTempSites[s].find(u'{{autres projets') == -1:
						PageTempSites[s] = u'{{Autres projets' + projetsS + u'}}\n' + PageTempSites[s]
					else: 
						PageTempSites[s] = -1
				elif s == 6:	# q
					projetsQ = filtre(projets,u'q',PageHS)
					if PageTempSites[s].find(u'{{Autres projets') == -1 and PageTempSites[s].find(u'{{autres projets') == -1 and PageTempSites[s].find(u'{{Interprojet') == -1 and PageTempSites[s].find(u'{{interprojet') == -1:
						PageTempSites[s] = u'{{Interprojet' + projetsQ + u'}}\n' + PageTempSites[s]
					else: 
						PageTempSites[s] = -1
				if PageTempSites[s] != -1: sauvegarde(pages[s],PageTempSites[s],u'Interwikis francophones')

	#raw_input(PageTemp.encode(config.console_encoding, 'replace'))						
	PageTemp = re.sub(r'{{formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{Formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{FORMATNUM:([0-9]*) ', r'{{formatnum:\1', PageTemp)

	if PageTemp.find(u'{{DEFAULTSORT:') == -1:
		ClePage = CleDeTri(PageHS)
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
						PageEnd = PageEnd + u'{{DEFAULTSORT:' + CleDeTri(Nom) + u', ' + CleDeTri(Prenom) + u'}}\n\n'
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
		if CleDeTri(PageHS) != ClePage:
			print (u'Fausse clé de tri dans :')
			print (PageHS.encode(config.console_encoding, 'replace'))
			print (ClePage.encode(config.console_encoding, 'replace'))
	
	#raw_input(PageEnd.encode(config.console_encoding, 'replace'))	
	PageEnd = PageEnd + PageTemp
	if PageEnd != PageBegin: sauvegarde(page,PageEnd,summary)
 
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
	
def CleDeTri(PageTitre):
	PageT = u''
	key = "false"
	for lettre in range(0,len(PageTitre)):
		# Latin
		if PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'Á' or PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä' or PageTitre[lettre:lettre+1] == u'ā' or PageTitre[lettre:lettre+1] == u'ă' or PageTitre[lettre:lettre+1] == u'ą' or PageTitre[lettre:lettre+1] == u'ǎ' or PageTitre[lettre:lettre+1] == u'ǻ' or PageTitre[lettre:lettre+1] == u'ȁ' or PageTitre[lettre:lettre+1] == u'ȃ' or PageTitre[lettre:lettre+1] == u'ȧ' or PageTitre[lettre:lettre+1] == u'ɑ' or PageTitre[lettre:lettre+1] == u'ạ' or PageTitre[lettre:lettre+1] == u'ả' or PageTitre[lettre:lettre+1] == u'ấ' or PageTitre[lettre:lettre+1] == u'Ấ' or PageTitre[lettre:lettre+1] == u'ⱥ' or PageTitre[lettre:lettre+1] == u'À' or PageTitre[lettre:lettre+1] == u'Â' or PageTitre[lettre:lettre+1] == u'Ä' or PageTitre[lettre:lettre+1] == u'Å' or PageTitre[lettre:lettre+1] == u'Ā' or PageTitre[lettre:lettre+1] == u'Ă' or PageTitre[lettre:lettre+1] == u'Ą' or PageTitre[lettre:lettre+1] == u'Ǎ' or PageTitre[lettre:lettre+1] == u'Ǻ' or PageTitre[lettre:lettre+1] == u'Ȁ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'Ȧ' or PageTitre[lettre:lettre+1] == u'Ⱥ' or PageTitre[lettre:lettre+1] == u'æ' or PageTitre[lettre:lettre+1] == u'ǣ' or PageTitre[lettre:lettre+1] == u'ǽ' or PageTitre[lettre:lettre+1] == u'Æ' or PageTitre[lettre:lettre+1] == u'Ǣ' or PageTitre[lettre:lettre+1] == u'Ǽ' or PageTitre[lettre:lettre+1] == u'Ɑ' or PageTitre[lettre:lettre+1] == u'Ǟ' or PageTitre[lettre:lettre+1] == u'Ǡ' or PageTitre[lettre:lettre+1] == u'ắ' or PageTitre[lettre:lettre+1] == u'Ắ' or PageTitre[lettre:lettre+1] == u'å' or PageTitre[lettre:lettre+1] == u'Å':
			PageT = PageT + "a"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ƀ' or PageTitre[lettre:lettre+1] == u'ƃ' or PageTitre[lettre:lettre+1] == u'Ɓ' or PageTitre[lettre:lettre+1] == u'Ƃ' or PageTitre[lettre:lettre+1] == u'Ƀ':
			PageT = PageT + "b"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ç' or PageTitre[lettre:lettre+1] == u'ć' or PageTitre[lettre:lettre+1] == u'ĉ' or PageTitre[lettre:lettre+1] == u'ċ' or PageTitre[lettre:lettre+1] == u'č' or PageTitre[lettre:lettre+1] == u'ƈ' or PageTitre[lettre:lettre+1] == u'ȼ' or PageTitre[lettre:lettre+1] == u'Ç' or PageTitre[lettre:lettre+1] == u'Ć' or PageTitre[lettre:lettre+1] == u'Ĉ' or PageTitre[lettre:lettre+1] == u'Ċ' or PageTitre[lettre:lettre+1] == u'Č' or PageTitre[lettre:lettre+1] == u'Ƈ' or PageTitre[lettre:lettre+1] == u'Ȼ':
			PageT = PageT + "c"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ď' or PageTitre[lettre:lettre+1] == u'đ' or PageTitre[lettre:lettre+1] == u'ƌ' or PageTitre[lettre:lettre+1] == u'ȡ' or PageTitre[lettre:lettre+1] == u'Ď' or PageTitre[lettre:lettre+1] == u'Đ' or PageTitre[lettre:lettre+1] == u'Ɖ' or PageTitre[lettre:lettre+1] == u'Ɗ' or PageTitre[lettre:lettre+1] == u'Ƌ' or PageTitre[lettre:lettre+1] == u'ȸ' or PageTitre[lettre:lettre+1] == u'ǆ' or PageTitre[lettre:lettre+1] == u'ǳ' or PageTitre[lettre:lettre+1] == u'Ǆ' or PageTitre[lettre:lettre+1] == u'ǅ' or PageTitre[lettre:lettre+1] == u'Ǳ' or PageTitre[lettre:lettre+1] == u'ǲ':
			PageT = PageT + "d"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'È' or PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'É' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'Ê' or PageTitre[lettre:lettre+1] == u'ë' or PageTitre[lettre:lettre+1] == u'Ë' or PageTitre[lettre:lettre+1] == u'ē' or PageTitre[lettre:lettre+1] == u'ĕ' or PageTitre[lettre:lettre+1] == u'ė' or PageTitre[lettre:lettre+1] == u'ę' or PageTitre[lettre:lettre+1] == u'ě' or PageTitre[lettre:lettre+1] == u'ǝ' or PageTitre[lettre:lettre+1] == u'ɛ' or PageTitre[lettre:lettre+1] == u'ȅ' or PageTitre[lettre:lettre+1] == u'ȇ' or PageTitre[lettre:lettre+1] == u'ȩ' or PageTitre[lettre:lettre+1] == u'ɇ' or PageTitre[lettre:lettre+1] == u'ế' or PageTitre[lettre:lettre+1] == u'Ế' or PageTitre[lettre:lettre+1] == u'Ē' or PageTitre[lettre:lettre+1] == u'Ĕ' or PageTitre[lettre:lettre+1] == u'Ė' or PageTitre[lettre:lettre+1] == u'Ę' or PageTitre[lettre:lettre+1] == u'Ě' or PageTitre[lettre:lettre+1] == u'Ǝ' or PageTitre[lettre:lettre+1] == u'Ɛ' or PageTitre[lettre:lettre+1] == u'Ȅ' or PageTitre[lettre:lettre+1] == u'Ȇ' or PageTitre[lettre:lettre+1] == u'Ȩ' or PageTitre[lettre:lettre+1] == u'Ɇ' or PageTitre[lettre:lettre+1] == u'ệ' or PageTitre[lettre:lettre+1] == u'Ệ':
			PageT = PageT + "e"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ƒ' or PageTitre[lettre:lettre+1] == u'Ƒ':
			PageT = PageT + "f"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĝ' or PageTitre[lettre:lettre+1] == u'ğ' or PageTitre[lettre:lettre+1] == u'ġ' or PageTitre[lettre:lettre+1] == u'ģ' or PageTitre[lettre:lettre+1] == u'ǥ' or PageTitre[lettre:lettre+1] == u'ǧ' or PageTitre[lettre:lettre+1] == u'ǵ' or PageTitre[lettre:lettre+1] == u'Ĝ' or PageTitre[lettre:lettre+1] == u'Ğ' or PageTitre[lettre:lettre+1] == u'Ġ' or PageTitre[lettre:lettre+1] == u'Ģ' or PageTitre[lettre:lettre+1] == u'Ɠ' or PageTitre[lettre:lettre+1] == u'Ǥ' or PageTitre[lettre:lettre+1] == u'Ǧ' or PageTitre[lettre:lettre+1] == u'Ǵ':
			PageT = PageT + "g"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĥ' or PageTitre[lettre:lettre+1] == u'ħ' or PageTitre[lettre:lettre+1] == u'ȟ' or PageTitre[lettre:lettre+1] == u'Ĥ' or PageTitre[lettre:lettre+1] == u'Ħ' or PageTitre[lettre:lettre+1] == u'Ȟ':
			PageT = PageT + "h"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ı' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ĩ' or PageTitre[lettre:lettre+1] == u'ī' or PageTitre[lettre:lettre+1] == u'ĭ' or PageTitre[lettre:lettre+1] == u'į' or PageTitre[lettre:lettre+1] == u'ǐ' or PageTitre[lettre:lettre+1] == u'ȉ' or PageTitre[lettre:lettre+1] == u'ȋ' or PageTitre[lettre:lettre+1] == u'Î' or PageTitre[lettre:lettre+1] == u'Ĩ' or PageTitre[lettre:lettre+1] == u'Ī' or PageTitre[lettre:lettre+1] == u'Ĭ' or PageTitre[lettre:lettre+1] == u'Į' or PageTitre[lettre:lettre+1] == u'İ' or PageTitre[lettre:lettre+1] == u'Ɨ' or PageTitre[lettre:lettre+1] == u'Ǐ' or PageTitre[lettre:lettre+1] == u'Ȉ' or PageTitre[lettre:lettre+1] == u'Ȋ' or PageTitre[lettre:lettre+1] == u'ĳ' or PageTitre[lettre:lettre+1] == u'Ĳ' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'Ì' or PageTitre[lettre:lettre+1] == u'ï' or PageTitre[lettre:lettre+1] == u'Ï':
			PageT = PageT + "i"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĵ' or PageTitre[lettre:lettre+1] == u'ǰ' or PageTitre[lettre:lettre+1] == u'ȷ' or PageTitre[lettre:lettre+1] == u'ɉ' or PageTitre[lettre:lettre+1] == u'Ĵ' or PageTitre[lettre:lettre+1] == u'Ɉ':
			PageT = PageT + "j"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ķ' or PageTitre[lettre:lettre+1] == u'ƙ' or PageTitre[lettre:lettre+1] == u'ǩ' or PageTitre[lettre:lettre+1] == u'Ķ' or PageTitre[lettre:lettre+1] == u'Ƙ' or PageTitre[lettre:lettre+1] == u'Ǩ':
			PageT = PageT + "k"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĺ' or PageTitre[lettre:lettre+1] == u'ļ' or PageTitre[lettre:lettre+1] == u'ľ' or PageTitre[lettre:lettre+1] == u'ŀ' or PageTitre[lettre:lettre+1] == u'ł' or PageTitre[lettre:lettre+1] == u'ƚ' or PageTitre[lettre:lettre+1] == u'ȴ' or PageTitre[lettre:lettre+1] == u'ɫ' or PageTitre[lettre:lettre+1] == u'Ɫ' or PageTitre[lettre:lettre+1] == u'Ĺ' or PageTitre[lettre:lettre+1] == u'Ļ' or PageTitre[lettre:lettre+1] == u'Ľ' or PageTitre[lettre:lettre+1] == u'Ŀ' or PageTitre[lettre:lettre+1] == u'Ł' or PageTitre[lettre:lettre+1] == u'Ƚ' or PageTitre[lettre:lettre+1] == u'ǉ' or PageTitre[lettre:lettre+1] == u'Ǉ' or PageTitre[lettre:lettre+1] == u'ǈ' or PageTitre[lettre:lettre+1] == u'ị' or PageTitre[lettre:lettre+1] == u'Ị':
			PageT = PageT + "i"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ɯ':
			PageT = PageT + "m"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ń' or PageTitre[lettre:lettre+1] == u'ņ' or PageTitre[lettre:lettre+1] == u'ň' or PageTitre[lettre:lettre+1] == u'ŋ' or PageTitre[lettre:lettre+1] == u'ǹ' or PageTitre[lettre:lettre+1] == u'ƞ' or PageTitre[lettre:lettre+1] == u'ȵ' or PageTitre[lettre:lettre+1] == u'Ń' or PageTitre[lettre:lettre+1] == u'Ņ' or PageTitre[lettre:lettre+1] == u'Ň' or PageTitre[lettre:lettre+1] == u'Ŋ' or PageTitre[lettre:lettre+1] == u'Ɲ' or PageTitre[lettre:lettre+1] == u'Ǹ' or PageTitre[lettre:lettre+1] == u'Ƞ' or PageTitre[lettre:lettre+1] == u'ǌ' or PageTitre[lettre:lettre+1] == u'Ǌ' or PageTitre[lettre:lettre+1] == u'ǋ' or PageTitre[lettre:lettre+1] == u'ɲ' or PageTitre[lettre:lettre+1] == u'ṉ' or PageTitre[lettre:lettre+1] == u'Ṉ':
			PageT = PageT + "n"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'Ô' or PageTitre[lettre:lettre+1] == u'ø' or PageTitre[lettre:lettre+1] == u'ō' or PageTitre[lettre:lettre+1] == u'ŏ' or PageTitre[lettre:lettre+1] == u'ő' or PageTitre[lettre:lettre+1] == u'ơ' or PageTitre[lettre:lettre+1] == u'ǒ' or PageTitre[lettre:lettre+1] == u'ǫ' or PageTitre[lettre:lettre+1] == u'ǭ' or PageTitre[lettre:lettre+1] == u'ǿ' or PageTitre[lettre:lettre+1] == u'ȍ' or PageTitre[lettre:lettre+1] == u'ȏ' or PageTitre[lettre:lettre+1] == u'ȫ' or PageTitre[lettre:lettre+1] == u'ȭ' or PageTitre[lettre:lettre+1] == u'ȯ' or PageTitre[lettre:lettre+1] == u'ȱ' or PageTitre[lettre:lettre+1] == u'Ø' or PageTitre[lettre:lettre+1] == u'Ō' or PageTitre[lettre:lettre+1] == u'Ŏ' or PageTitre[lettre:lettre+1] == u'Ő' or PageTitre[lettre:lettre+1] == u'Ɔ' or PageTitre[lettre:lettre+1] == u'Ɵ' or PageTitre[lettre:lettre+1] == u'ɵ' or PageTitre[lettre:lettre+1] == u'Ơ' or PageTitre[lettre:lettre+1] == u'Ǒ' or PageTitre[lettre:lettre+1] == u'Ǫ' or PageTitre[lettre:lettre+1] == u'Ǭ' or PageTitre[lettre:lettre+1] == u'Ǿ' or PageTitre[lettre:lettre+1] == u'Ȍ' or PageTitre[lettre:lettre+1] == u'Ȏ' or PageTitre[lettre:lettre+1] == u'Ȫ' or PageTitre[lettre:lettre+1] == u'Ȭ' or PageTitre[lettre:lettre+1] == u'Ȯ' or PageTitre[lettre:lettre+1] == u'Ȱ' or PageTitre[lettre:lettre+1] == u'ɔ' or PageTitre[lettre:lettre+1] == u'ở' or PageTitre[lettre:lettre+1] == u'Ở' or PageTitre[lettre:lettre+1] == u'ợ' or PageTitre[lettre:lettre+1] == u'Ợ':
			PageT = PageT + "o"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'œ' or PageTitre[lettre:lettre+1] == u'Œ':
			PageT = PageT + "oe"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ƥ' or PageTitre[lettre:lettre+1] == u'Ƥ':
			PageT = PageT + "p"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ɋ' or PageTitre[lettre:lettre+1] == u'Ɋ' or PageTitre[lettre:lettre+1] == u'ȹ':
			PageT = PageT + "q"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ŕ' or PageTitre[lettre:lettre+1] == u'ŗ' or PageTitre[lettre:lettre+1] == u'ř' or PageTitre[lettre:lettre+1] == u'ȑ' or PageTitre[lettre:lettre+1] == u'ȓ' or PageTitre[lettre:lettre+1] == u'ɍ' or PageTitre[lettre:lettre+1] == u'Ŕ' or PageTitre[lettre:lettre+1] == u'Ŗ' or PageTitre[lettre:lettre+1] == u'Ř' or PageTitre[lettre:lettre+1] == u'Ȑ' or PageTitre[lettre:lettre+1] == u'Ȓ' or PageTitre[lettre:lettre+1] == u'Ɍ':
			PageT = PageT + "r"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ſ' or PageTitre[lettre:lettre+1] == u'ś' or PageTitre[lettre:lettre+1] == u'ŝ' or PageTitre[lettre:lettre+1] == u'ş' or PageTitre[lettre:lettre+1] == u'š' or PageTitre[lettre:lettre+1] == u'ƪ' or PageTitre[lettre:lettre+1] == u'ș' or PageTitre[lettre:lettre+1] == u'ȿ' or PageTitre[lettre:lettre+1] == u'Ś' or PageTitre[lettre:lettre+1] == u'Ŝ' or PageTitre[lettre:lettre+1] == u'Ş' or PageTitre[lettre:lettre+1] == u'Š' or PageTitre[lettre:lettre+1] == u'Ʃ' or PageTitre[lettre:lettre+1] == u'Ș' or PageTitre[lettre:lettre+1] == u'ß':
			PageT = PageT + "s"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ţ' or PageTitre[lettre:lettre+1] == u'ť' or PageTitre[lettre:lettre+1] == u'ŧ' or PageTitre[lettre:lettre+1] == u'ƫ' or PageTitre[lettre:lettre+1] == u'ƭ' or PageTitre[lettre:lettre+1] == u'ț' or PageTitre[lettre:lettre+1] == u'ȶ' or PageTitre[lettre:lettre+1] == u'Ţ' or PageTitre[lettre:lettre+1] == u'Ť' or PageTitre[lettre:lettre+1] == u'Ŧ' or PageTitre[lettre:lettre+1] == u'Ƭ' or PageTitre[lettre:lettre+1] == u'Ʈ' or PageTitre[lettre:lettre+1] == u'Ț' or PageTitre[lettre:lettre+1] == u'Ⱦ' or PageTitre[lettre:lettre+1] == u'ⱦ':
			PageT = PageT + "t"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ũ' or PageTitre[lettre:lettre+1] == u'ū' or PageTitre[lettre:lettre+1] == u'ŭ' or PageTitre[lettre:lettre+1] == u'ů' or PageTitre[lettre:lettre+1] == u'ű' or PageTitre[lettre:lettre+1] == u'ų' or PageTitre[lettre:lettre+1] == u'ư' or PageTitre[lettre:lettre+1] == u'ǔ' or PageTitre[lettre:lettre+1] == u'ǖ' or PageTitre[lettre:lettre+1] == u'ǘ' or PageTitre[lettre:lettre+1] == u'ǚ' or PageTitre[lettre:lettre+1] == u'ǜ' or PageTitre[lettre:lettre+1] == u'ǟ' or PageTitre[lettre:lettre+1] == u'ǡ' or PageTitre[lettre:lettre+1] == u'ȕ' or PageTitre[lettre:lettre+1] == u'ȗ' or PageTitre[lettre:lettre+1] == u'ʉ' or PageTitre[lettre:lettre+1] == u'Û' or PageTitre[lettre:lettre+1] == u'Ũ' or PageTitre[lettre:lettre+1] == u'Ū' or PageTitre[lettre:lettre+1] == u'Ŭ' or PageTitre[lettre:lettre+1] == u'Ů' or PageTitre[lettre:lettre+1] == u'Ű' or PageTitre[lettre:lettre+1] == u'Ų' or PageTitre[lettre:lettre+1] == u'Ư' or PageTitre[lettre:lettre+1] == u'Ǔ' or PageTitre[lettre:lettre+1] == u'Ǖ' or PageTitre[lettre:lettre+1] == u'Ǘ' or PageTitre[lettre:lettre+1] == u'Ǚ' or PageTitre[lettre:lettre+1] == u'Ǜ' or PageTitre[lettre:lettre+1] == u'Ȕ' or PageTitre[lettre:lettre+1] == u'Ȗ' or PageTitre[lettre:lettre+1] == u'Ʉ' or PageTitre[lettre:lettre+1] == u'ủ' or PageTitre[lettre:lettre+1] == u'Ủ' or PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'Ú':
			PageT = PageT + "u"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ʋ' or PageTitre[lettre:lettre+1] == u'Ʋ' or PageTitre[lettre:lettre+1] == u'Ʌ' or PageTitre[lettre:lettre+1] == u'ʌ':
			PageT = PageT + "v"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ŵ' or PageTitre[lettre:lettre+1] == u'Ŵ':
			PageT = PageT + "w"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ŷ' or PageTitre[lettre:lettre+1] == u'ƴ' or PageTitre[lettre:lettre+1] == u'ȳ' or PageTitre[lettre:lettre+1] == u'ɏ' or PageTitre[lettre:lettre+1] == u'Ŷ' or PageTitre[lettre:lettre+1] == u'Ÿ' or PageTitre[lettre:lettre+1] == u'Ƴ' or PageTitre[lettre:lettre+1] == u'Ȳ' or PageTitre[lettre:lettre+1] == u'Ɏ':
			PageT = PageT + "y"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ź' or PageTitre[lettre:lettre+1] == u'ż' or PageTitre[lettre:lettre+1] == u'ž' or PageTitre[lettre:lettre+1] == u'ƶ' or PageTitre[lettre:lettre+1] == u'ƹ' or PageTitre[lettre:lettre+1] == u'ƺ' or PageTitre[lettre:lettre+1] == u'ǯ' or PageTitre[lettre:lettre+1] == u'ȥ' or PageTitre[lettre:lettre+1] == u'ɀ' or PageTitre[lettre:lettre+1] == u'Ź' or PageTitre[lettre:lettre+1] == u'Ż' or PageTitre[lettre:lettre+1] == u'Ž' or PageTitre[lettre:lettre+1] == u'Ƶ' or PageTitre[lettre:lettre+1] == u'Ʒ' or PageTitre[lettre:lettre+1] == u'Ƹ' or PageTitre[lettre:lettre+1] == u'Ǯ' or PageTitre[lettre:lettre+1] == u'Ȥ':
			PageT = PageT + "z"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'\'' or PageTitre[lettre:lettre+1] == u'’' or PageTitre[lettre:lettre+1] == u'ʼ':
			PageT = PageT + ""
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'-':
			PageT = PageT + " "
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'/':
			PageT = PageT + " "
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'\\':
			PageT = PageT + ""
			key = "yes"'''
		# Grec
		elif PageTitre[lettre:lettre+1] == u'α' or PageTitre[lettre:lettre+1] == u'Ἀ' or PageTitre[lettre:lettre+1] == u'ἀ' or PageTitre[lettre:lettre+1] == u'Ἁ' or PageTitre[lettre:lettre+1] == u'ἁ' or PageTitre[lettre:lettre+1] == u'Ἂ' or PageTitre[lettre:lettre+1] == u'ἂ' or PageTitre[lettre:lettre+1] == u'Ἃ' or PageTitre[lettre:lettre+1] == u'ἃ' or PageTitre[lettre:lettre+1] == u'Ἄ' or PageTitre[lettre:lettre+1] == u'ἄ' or PageTitre[lettre:lettre+1] == u'Ἅ' or PageTitre[lettre:lettre+1] == u'ἅ' or PageTitre[lettre:lettre+1] == u'Ἆ' or PageTitre[lettre:lettre+1] == u'ἆ' or PageTitre[lettre:lettre+1] == u'Ἇ' or PageTitre[lettre:lettre+1] == u'ἇ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ὰ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ά' or PageTitre[lettre:lettre+1] == u'ᾈ' or PageTitre[lettre:lettre+1] == u'ᾀ' or PageTitre[lettre:lettre+1] == u'ᾉ' or PageTitre[lettre:lettre+1] == u'ᾁ' or PageTitre[lettre:lettre+1] == u'ᾊ' or PageTitre[lettre:lettre+1] == u'ᾂ' or PageTitre[lettre:lettre+1] == u'ᾋ' or PageTitre[lettre:lettre+1] == u'ᾃ' or PageTitre[lettre:lettre+1] == u'ᾌ' or PageTitre[lettre:lettre+1] == u'ᾄ' or PageTitre[lettre:lettre+1] == u'ᾍ' or PageTitre[lettre:lettre+1] == u'ᾅ' or PageTitre[lettre:lettre+1] == u'ᾎ' or PageTitre[lettre:lettre+1] == u'ᾆ' or PageTitre[lettre:lettre+1] == u'ᾏ' or PageTitre[lettre:lettre+1] == u'ᾇ' or PageTitre[lettre:lettre+1] == u'Ᾰ' or PageTitre[lettre:lettre+1] == u'ᾰ' or PageTitre[lettre:lettre+1] == u'Ᾱ' or PageTitre[lettre:lettre+1] == u'ᾱ' or PageTitre[lettre:lettre+1] == u'ᾼ' or PageTitre[lettre:lettre+1] == u'ᾳ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ᾲ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ᾴ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾶ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾷ':
			PageT = PageT + "α"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ἐ' or PageTitre[lettre:lettre+1] == u'ἐ' or PageTitre[lettre:lettre+1] == u'Ἑ' or PageTitre[lettre:lettre+1] == u'ἑ' or PageTitre[lettre:lettre+1] == u'Ἒ' or PageTitre[lettre:lettre+1] == u'ἒ' or PageTitre[lettre:lettre+1] == u'Ἓ' or PageTitre[lettre:lettre+1] == u'ἓ' or PageTitre[lettre:lettre+1] == u'Ἔ' or PageTitre[lettre:lettre+1] == u'ἔ' or PageTitre[lettre:lettre+1] == u'Ἕ' or PageTitre[lettre:lettre+1] == u'ἕ' or PageTitre[lettre:lettre+1] == u'Ὲ' or PageTitre[lettre:lettre+1] == u'ὲ' or PageTitre[lettre:lettre+1] == u'Έ' or PageTitre[lettre:lettre+1] == u'έ':
			PageT = PageT + "ε"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ἠ' or PageTitre[lettre:lettre+1] == u'ἠ' or PageTitre[lettre:lettre+1] == u'Ἡ' or PageTitre[lettre:lettre+1] == u'ἡ' or PageTitre[lettre:lettre+1] == u'Ἢ' or PageTitre[lettre:lettre+1] == u'ἢ' or PageTitre[lettre:lettre+1] == u'Ἣ' or PageTitre[lettre:lettre+1] == u'ἣ' or PageTitre[lettre:lettre+1] == u'Ἤ' or PageTitre[lettre:lettre+1] == u'ἤ' or PageTitre[lettre:lettre+1] == u'Ἥ' or PageTitre[lettre:lettre+1] == u'ἥ' or PageTitre[lettre:lettre+1] == u'Ἦ' or PageTitre[lettre:lettre+1] == u'ἦ' or PageTitre[lettre:lettre+1] == u'Ἧ' or PageTitre[lettre:lettre+1] == u'ἧ' or PageTitre[lettre:lettre+1] == u'ᾘ' or PageTitre[lettre:lettre+1] == u'ᾐ' or PageTitre[lettre:lettre+1] == u'ᾙ' or PageTitre[lettre:lettre+1] == u'ᾑ' or PageTitre[lettre:lettre+1] == u'ᾚ' or PageTitre[lettre:lettre+1] == u'ᾒ' or PageTitre[lettre:lettre+1] == u'ᾛ' or PageTitre[lettre:lettre+1] == u'ᾓ' or PageTitre[lettre:lettre+1] == u'ᾜ' or PageTitre[lettre:lettre+1] == u'ᾔ' or PageTitre[lettre:lettre+1] == u'ᾝ' or PageTitre[lettre:lettre+1] == u'ᾕ' or PageTitre[lettre:lettre+1] == u'ᾞ' or PageTitre[lettre:lettre+1] == u'ᾖ' or PageTitre[lettre:lettre+1] == u'ᾟ' or PageTitre[lettre:lettre+1] == u'ᾗ' or PageTitre[lettre:lettre+1] == u'Ὴ' or PageTitre[lettre:lettre+1] == u'ὴ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ή' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῂ' or PageTitre[lettre:lettre+1] == u'Η' or PageTitre[lettre:lettre+1] == u'ῃ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ῄ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῆ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῇ':
			PageT = PageT + "η"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ὶ' or PageTitre[lettre:lettre+1] == u'ὶ' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ῐ' or PageTitre[lettre:lettre+1] == u'ῐ' or PageTitre[lettre:lettre+1] == u'Ῑ' or PageTitre[lettre:lettre+1] == u'ῑ' or PageTitre[lettre:lettre+1] == u'Ἰ' or PageTitre[lettre:lettre+1] == u'ἰ' or PageTitre[lettre:lettre+1] == u'Ἱ' or PageTitre[lettre:lettre+1] == u'ἱ' or PageTitre[lettre:lettre+1] == u'Ἲ' or PageTitre[lettre:lettre+1] == u'ἲ' or PageTitre[lettre:lettre+1] == u'Ἳ' or PageTitre[lettre:lettre+1] == u'ἳ' or PageTitre[lettre:lettre+1] == u'Ἴ' or PageTitre[lettre:lettre+1] == u'ἴ' or PageTitre[lettre:lettre+1] == u'Ἵ' or PageTitre[lettre:lettre+1] == u'ἵ' or PageTitre[lettre:lettre+1] == u'Ἶ' or PageTitre[lettre:lettre+1] == u'ἶ' or PageTitre[lettre:lettre+1] == u'Ἷ' or PageTitre[lettre:lettre+1] == u'ἷ' or PageTitre[lettre:lettre+1] == u'ΐ' or PageTitre[lettre:lettre+1] == u'ῖ' or PageTitre[lettre:lettre+1] == u'ῗ' or PageTitre[lettre:lettre+1] == u'ῒ':
			PageT = PageT + "ι"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ὀ' or PageTitre[lettre:lettre+1] == u'ὀ' or PageTitre[lettre:lettre+1] == u'Ὁ' or PageTitre[lettre:lettre+1] == u'ὁ' or PageTitre[lettre:lettre+1] == u'Ὂ' or PageTitre[lettre:lettre+1] == u'ὂ' or PageTitre[lettre:lettre+1] == u'Ὃ' or PageTitre[lettre:lettre+1] == u'ὃ' or PageTitre[lettre:lettre+1] == u'Ὄ' or PageTitre[lettre:lettre+1] == u'ὄ' or PageTitre[lettre:lettre+1] == u'Ὅ' or PageTitre[lettre:lettre+1] == u'ὅ' or PageTitre[lettre:lettre+1] == u'Ὸ' or PageTitre[lettre:lettre+1] == u'ὸ' or PageTitre[lettre:lettre+1] == u'Ό' or PageTitre[lettre:lettre+1] == u'ό':
			PageT = PageT + "ο"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ὠ' or PageTitre[lettre:lettre+1] == u'ὠ' or PageTitre[lettre:lettre+1] == u'Ὡ' or PageTitre[lettre:lettre+1] == u'ὡ' or PageTitre[lettre:lettre+1] == u'Ὢ' or PageTitre[lettre:lettre+1] == u'ὢ' or PageTitre[lettre:lettre+1] == u'Ὣ' or PageTitre[lettre:lettre+1] == u'ὣ' or PageTitre[lettre:lettre+1] == u'Ὤ' or PageTitre[lettre:lettre+1] == u'ὤ' or PageTitre[lettre:lettre+1] == u'Ὥ' or PageTitre[lettre:lettre+1] == u'ὥ' or PageTitre[lettre:lettre+1] == u'Ὦ' or PageTitre[lettre:lettre+1] == u'ὦ' or PageTitre[lettre:lettre+1] == u'Ὧ' or PageTitre[lettre:lettre+1] == u'ὧ' or PageTitre[lettre:lettre+1] == u'Ὼ' or PageTitre[lettre:lettre+1] == u'ὼ' or PageTitre[lettre:lettre+1] == u'Ώ' or PageTitre[lettre:lettre+1] == u'ώ' or PageTitre[lettre:lettre+1] == u'ᾨ' or PageTitre[lettre:lettre+1] == u'ᾠ' or PageTitre[lettre:lettre+1] == u'ᾩ' or PageTitre[lettre:lettre+1] == u'ᾡ' or PageTitre[lettre:lettre+1] == u'ᾪ' or PageTitre[lettre:lettre+1] == u'ᾢ' or PageTitre[lettre:lettre+1] == u'ᾫ' or PageTitre[lettre:lettre+1] == u'ᾣ' or PageTitre[lettre:lettre+1] == u'ᾬ' or PageTitre[lettre:lettre+1] == u'ᾤ' or PageTitre[lettre:lettre+1] == u'ᾭ' or PageTitre[lettre:lettre+1] == u'ᾥ' or PageTitre[lettre:lettre+1] == u'ᾮ' or PageTitre[lettre:lettre+1] == u'ᾦ' or PageTitre[lettre:lettre+1] == u'ᾯ' or PageTitre[lettre:lettre+1] == u'ᾧ' or PageTitre[lettre:lettre+1] == u'ῼ' or PageTitre[lettre:lettre+1] == u'ῳ' or PageTitre[lettre:lettre+1] == u'ῲ' or PageTitre[lettre:lettre+1] == u'ῴ' or PageTitre[lettre:lettre+1] == u'ῶ' or PageTitre[lettre:lettre+1] == u'ῷ':
			PageT = PageT + "ω"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ὓ' or PageTitre[lettre:lettre+1] == u'ὓ' or PageTitre[lettre:lettre+1] == u'Υ' or PageTitre[lettre:lettre+1] == u'ὔ' or PageTitre[lettre:lettre+1] == u'Ὕ' or PageTitre[lettre:lettre+1] == u'ὕ' or PageTitre[lettre:lettre+1] == u'Ὗ' or PageTitre[lettre:lettre+1] == u'ὗ' or PageTitre[lettre:lettre+1] == u'Ὺ' or PageTitre[lettre:lettre+1] == u'ὺ' or PageTitre[lettre:lettre+1] == u'Ύ' or PageTitre[lettre:lettre+1] == u'ύ' or PageTitre[lettre:lettre+1] == u'Ῠ' or PageTitre[lettre:lettre+1] == u'ῠ' or PageTitre[lettre:lettre+1] == u'Ῡ' or PageTitre[lettre:lettre+1] == u'ῡ' or PageTitre[lettre:lettre+1] == u'ῢ' or PageTitre[lettre:lettre+1] == u'ΰ' or PageTitre[lettre:lettre+1] == u'ῦ' or PageTitre[lettre:lettre+1] == u'ῧ' or PageTitre[lettre:lettre+1] == u'ὐ' or PageTitre[lettre:lettre+1] == u'ὑ' or PageTitre[lettre:lettre+1] == u'ὒ' or PageTitre[lettre:lettre+1] == u'ὖ':
			PageT = PageT + "υ"
			key = "yes"
		# Cyrillique
		elif PageTitre[lettre:lettre+1] == u'ѐ' or PageTitre[lettre:lettre+1] == u'Ѐ' or PageTitre[lettre:lettre+1] == u'ё' or PageTitre[lettre:lettre+1] == u'Ё':
			PageT = PageT + u'е'
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ѝ' or PageTitre[lettre:lettre+1] == u'й' or PageTitre[lettre:lettre+1] == u'И' or PageTitre[lettre:lettre+1] == u'Ѝ' or PageTitre[lettre:lettre+1] == u'Й':
			PageT = PageT + "и"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ў' or PageTitre[lettre:lettre+1] == u'У' or PageTitre[lettre:lettre+1] == u'Ў':
			PageT = PageT + "у"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ѓ' or PageTitre[lettre:lettre+1] == u'ґ' or PageTitre[lettre:lettre+1] == u'Г' or PageTitre[lettre:lettre+1] == u'Ѓ' or PageTitre[lettre:lettre+1] == u'Ґ':
			PageT = PageT + "г"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ќ' or PageTitre[lettre:lettre+1] == u'К' or PageTitre[lettre:lettre+1] == u'Ќ':
			PageT = PageT + "к"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ї' or PageTitre[lettre:lettre+1] == u'І' or PageTitre[lettre:lettre+1] == u'Ї':
			PageT = PageT + "і"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ѿ':
			PageT = PageT + "Ѡ"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'Ѵ' or PageTitre[lettre:lettre+1] == u'ѷ' or PageTitre[lettre:lettre+1] == u'Ѷ':
			PageT = PageT + "ѵ"
			key = "yes"
		# Arabe
		elif PageTitre[lettre:lettre+1] == u'أ' or PageTitre[lettre:lettre+1] == u'إ' or PageTitre[lettre:lettre+1] == u'آ' or PageTitre[lettre:lettre+1] == u'ٱ':
			PageT = PageT + "ا"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'دَ' or PageTitre[lettre:lettre+1] == u'دِ' or PageTitre[lettre:lettre+1] == u'دُ':
			PageT = PageT + "ﺩ"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ذٰ':
			PageT = PageT + "ﺫ"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'لٰ':
			PageT = PageT + "ﻝ"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'مٰ':
			PageT = PageT + "ﻡ"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'هٰ':
			PageT = PageT + "ﻩ"
			key = "yes"'''
		elif PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'B' or PageTitre[lettre:lettre+1] == u'C' or PageTitre[lettre:lettre+1] == u'D' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'F' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'H' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'J' or PageTitre[lettre:lettre+1] == u'K' or PageTitre[lettre:lettre+1] == u'L' or PageTitre[lettre:lettre+1] == u'M' or PageTitre[lettre:lettre+1] == u'N' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'P' or PageTitre[lettre:lettre+1] == u'Q' or PageTitre[lettre:lettre+1] == u'R' or PageTitre[lettre:lettre+1] == u'S' or PageTitre[lettre:lettre+1] == u'T' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'V' or PageTitre[lettre:lettre+1] == u'W' or PageTitre[lettre:lettre+1] == u'X' or PageTitre[lettre:lettre+1] == u'Y' or PageTitre[lettre:lettre+1] == u'Z':
			PageT = PageT + PageTitre[lettre:lettre+1].lower()
		else:
			PageT = PageT + PageTitre[lettre:lettre+1]
		#print (PageT.encode(config.console_encoding, 'replace'))
		#raw_input("lettre")
		if key != "yes": return # 1ère lettre uniquement pour l'instant
	if key == "yes":
		while PageT[0:1] == u' ': PageT = PageT[1:len(PageT)]
		return PageT
	else:
		#raw_input(PageTitre.encode(config.console_encoding, 'replace'))
		return PageTitre

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			print PageHS
			modification(PageHS)
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
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
def crawlerLink(pagename):
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())

# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
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

def trim(s):
    return s.strip(" \t\n\r\0\x0B")
	
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
	ArretDUrgence()
	try:
		result = "ok"
		#print(Contenu.encode(config.console_encoding, 'replace')[0:10000])
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
TraitementCategory = crawlerCat(u'Catégorie:Homonymie',False,u'Masreliez')
'''
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementLiens = crawlerLink(u'Modèle:ko-hanja')
TraitementFile = crawlerFile('articles_list.txt')
TraitementRecherche = crawlerSearch(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
	TraitementRC = crawlerRC()
'''
#python cosmetic_changes.py -lang:"fr" -recentchanges
#http://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial%3AToutes+les+pages&from=%C3%A9&to=&namespace=14
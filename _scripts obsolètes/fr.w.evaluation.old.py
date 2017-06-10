#!/usr/bin/env python
# Ce script fusion les évaluations existantes, et éventuellement en ajoute une au début.

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
eval = u'Écosse' # Nom à ajouter
uation = u'|?' # Noter l'importance, éventuellement l'avancement (ex : "|avancement=ébauche") sinon le bot ajoute seul "|avancement=?"
if eval != "":
	summary = u'[[Wikipédia:Bot/Requêtes/2010/11]] : ajout de l\'évaluation : ' + eval
else:
	summary = u'Fusion des évaluations'
	
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
	PageTemp2 = ""
	projet = "False"
	if page.exists():
		if page.namespace()!= 1 and page.title() != u'Utilisateur:JackBot/test': 
			return
		else:
			try:
				PageTemp = page.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return
		if PageTemp[len(PageTemp)-1:len(PageTemp)] == u'}': PageTemp = PageTemp + u'\n'
		if PageTemp.find(u'{{Évaluation multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{Évaluation multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{Évaluation multiprojet')+len(u'{{Évaluation multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{Évaluation_multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{Évaluation_multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{Évaluation_multiprojet')+len(u'{{Évaluation_multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{évaluation multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{évaluation multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{évaluation multiprojet')+len(u'{{évaluation multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{évaluation_multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{évaluation_multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{évaluation_multiprojet')+len(u'{{évaluation_multiprojet'):len(PageTemp)]
		while position != -1 and position < len(PageTemp): # On déplace les données d'une page provisoire dans une page finale jusqu'à disparition de la première
			position = PageTemp.find(u'{{Wikiprojet')
			if position == -1: position = PageTemp.find(u'{{wikiprojet')
			if position == -1 and projet == "True": break 	# S'il n'y a plus d'évaluation à traiter
			elif position == -1 and projet == "False":    	# S'il n'y a aucune évaluation
				if eval:
					PageEnd = PageEnd + "{{Wikiprojet|\n" + eval + uation
			else:											# S'il y a un modèle évaluation à traiter
				if position == PageTemp.find(u'{{wikiprojet'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{wikiprojet')+2] + u'W' + PageTemp[PageTemp.find(u'{{wikiprojet')+3:len(PageTemp)]
				if PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet'):PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1] == u' ' and PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+2] != u'\n' and PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+2] != u'|': # Normalisation du modèle
					PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')] + u'|' + PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:len(PageTemp)]
				if projet == "False": # Premier modèle Wikiprojet
					PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')]
					PageTemp = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)] # PageTemp = paramètres}}...

					if PageTemp.find(u'importance=') != -1 and PageTemp.find(u'importance=') < PageTemp.find("}}"): # Aucune importance= par Wikiprojet
						PageTemp = PageTemp[0:PageTemp.find(u'importance=')] + PageTemp[PageTemp.find(u'importance=')+len(u'importance='):len(PageTemp)]					
					
					if PageTemp.find(u'avancement') != -1 and PageTemp.find(u'avancement') < PageTemp.find(u'}}'):
						PageTemp3 = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
						if PageTemp3.find(u'avancement') != -1 and PageTemp3.find(u'avancement') < PageTemp3.find(u'}}') or PageTemp.find(eval) == -1: # S'il y a plusieurs avancements
							while PageTemp.find(u' avancement=') != -1 and PageTemp.find(u' avancement=') < PageTemp.find(u'}}'):
								PageTemp = PageTemp[0:PageTemp.find(u' avancement=')] + PageTemp[PageTemp.find(u' avancement=')+1:len(PageTemp)]
							if PageTemp.find(u'|avancement=') != -1: # Récupération de l'état d'avancement du Wikiprojet
								PageTemp3 = PageTemp[PageTemp.find(u'|avancement=')+1:len(PageTemp)]
								if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
									if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1] == u'|avancement=?':
										PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
										if PageTemp4.find(u'|avancement=') != -1:
											PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
											if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
											elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
											else:
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
									else:
										PageEnd = PageEnd + PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1]						
								elif PageTemp3.find(u'\n') != -1 and PageTemp3.find(u'\n') < PageTemp3.find(u'}'):
									if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1] == u'|avancement=?':
										PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
										if PageTemp4.find(u'|avancement=') != -1:
											PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
											if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
											elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
											else:
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
									else:
										PageEnd = PageEnd + PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1]	
								else:
									if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1] == u'|avancement=?':
										PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
										if PageTemp4.find(u'|avancement=') != -1:
											PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
											if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
											elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
											else:
												PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
									else:
										PageEnd = PageEnd + PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1]	
								while PageTemp.find(u'|avancement=') != -1: # Un seul avancement par Wikiprojet
									PageTemp3 = PageTemp[PageTemp.find(u'|avancement=')+1:len(PageTemp)]
									if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
										PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1:len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1:len(PageTemp)]
					if PageTemp.find(u'avancement ') != -1 and PageTemp.find(u'avancement ') < PageTemp.find(u'}}'):
						PageTemp3 = PageTemp[max(PageTemp.find(u'|avancement '),PageTemp.find(u'| avancement '))+1:len(PageTemp)]
						if PageEnd.find(u'|avancement=') == -1:
							if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}') and PageTemp3.find(u'|') < PageTemp3.find(u'['):
								PageEnd = PageEnd + PageTemp[max(PageTemp.find(u'|avancement '),PageTemp.find(u'| avancement ')):max(PageTemp.find(u'|avancement '),PageTemp.find(u'| avancement '))+1+PageTemp3.find(u'|')+1]
							else:
								PageEnd = PageEnd + u'|avancement=' + PageTemp[PageTemp.find(u'|avancement ')+PageTemp3.find(u'=')+2:PageTemp.find(u'|avancement ')+PageTemp3.find(u'}')+1]
						while PageTemp.find(u'|avancement ') != -1: # Un seul avancement par Wikiprojet
							PageTemp3 = PageTemp[PageTemp.find(u'|avancement ')+1:len(PageTemp)]
							if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement ')] + PageTemp[PageTemp.find(u'|avancement ')+PageTemp3.find(u'|')+1:len(PageTemp)]
							else:
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement ')] + PageTemp[PageTemp.find(u'|avancement ')+PageTemp3.find(u'}')+1:len(PageTemp)]
					if PageEnd.find(u'|avancement=') == -1 and PageEnd.find(u'| avancement=') == -1 and PageEnd.find(u'| avancement =') == -1 and PageTemp.find(u'avancement=') == -1: # On ajoute un avancement indéfini s'il n'y en a pas
						PageEnd = PageEnd + u'\n|avancement=?\n'
					PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")]
					PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
					projet = "True"				
				else: # Modèle Wikiprojet superfétatoire trouvé
					PageTemp2 = PageTemp2 + PageTemp[0:PageTemp.find(u'{{Wikiprojet')] # Retient les éléments entre les Wikiprojets
					PageTemp = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)]					
					PageTemp3 = PageTemp[1:PageTemp.find("}}")]
					if PageEnd.find(u'|' + PageTemp3[0:PageTemp3.find(u'|')+1]) != -1: # Si elle existe déjà
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
					else:
						if PageTemp.find(u'importance=') != -1 and PageTemp.find(u'importance=') < PageTemp.find("}}"): # Aucune importance= par Wikiprojet
							PageTemp = PageTemp[0:PageTemp.find(u'importance=')] + PageTemp[PageTemp.find(u'importance=')+len(u'importance='):len(PageTemp)]
						PageEnd = PageEnd + u'\n' + PageTemp[0:PageTemp.find("}}")]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						
		if PageTemp.find("}}") > PageTemp.find("{{") or PageTemp.find("}}") == -1:
			if PageEnd.find("{{") != -1:
				PageEnd = PageEnd + u'}}' + PageTemp2 + PageTemp[0:len(PageTemp)]
			else:
				PageEnd = PageEnd + PageTemp2 + PageTemp[0:len(PageTemp)]
		else:
			PageEnd = PageEnd + PageTemp2 + PageTemp[0:len(PageTemp)]
	else: # Si la page n'existe pas
		if eval != "":
			PageEnd = "{{Wikiprojet\n|" + eval + uation + "\n|avancement=?}}\n"
			page.put(PageEnd, summary)
			return
		else:
			return
	# Gestion des 1% d'imprévus par le modèle
	if PageEnd.find(u'{{Wikiprojet|') != -1 and PageEnd.find(u'|avancement=') == -1 and PageEnd.find(u'| avancement=') == -1 and PageEnd.find(u'|avancement =') == -1 and PageEnd.find(u'| avancement =') == -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet|')] + u'avancement=?|' + PageEnd[PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet|'):len(PageEnd)]
	if PageEnd.find(u'avancement=|') != -1 and PageEnd.find(u'avancement=|') < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find(u'avancement=|')+len(u'avancement=|')-1] + u'?' + PageEnd[PageEnd.find(u'avancement=|')+len(u'avancement=|')-1:len(PageEnd)]
	if PageEnd.find(u'avancement=\n') != -1 and PageEnd.find(u'avancement=\n') < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find(u'avancement=\n')+len(u'avancement=\n')-1] + u'?' + PageEnd[PageEnd.find(u'avancement=\n')+len(u'avancement=\n')-1:len(PageEnd)]
	if PageEnd.find(u'{{évaluations WP1') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{évaluations WP1')+2] + u'É' + PageEnd[PageEnd.find(u'{{évaluations WP1')+3:len(PageEnd)]
	if (PageEnd.find(u'{{Évaluations WP1') != -1 and PageEnd.find(u'{{Évaluations WP1') < PageEnd.find("}}")) or (PageEnd.find(u'{{Évaluations_WP1') != -1 and PageEnd.find(u'{{Évaluations_WP1') < PageEnd.find("}}")):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Évaluations WP1')] + PageEnd[PageEnd.find(u'{{Évaluations WP1')+len(u'{{Évaluations WP1'):len(PageEnd)]
		if PageEnd.find(u'\n}}\n}}') != -1:
			PageEnd = PageEnd[0:PageEnd.find(u'\n}}\n}}')+len(u'\n}}\n}}')-2] + PageEnd[PageEnd.find(u'\n}}\n}}')+len(u'\n}}\n}}'):len(PageEnd)]
		if PageEnd.find(u'\n}} \n}}') != -1:
			PageEnd = PageEnd[0:PageEnd.find(u'\n}} \n}}')+len(u'\n}} \n}}')-2] + PageEnd[PageEnd.find(u'\n}} \n}}')+len(u'\n}} \n}}'):len(PageEnd)]
		if PageEnd.find(u'}}\n{{Wikiprojet') != -1:
			PageEnd = PageEnd[0:PageEnd.find(u'}}\n{{Wikiprojet')] + PageEnd[PageEnd.find(u'}}\n{{Wikiprojet')+len(u'}}\n'):len(PageEnd)]
		if PageEnd.find(u'\n}}\t\n}}') != -1:
			PageEnd = PageEnd[0:PageEnd.find(u'\n}}\t\n}}')+len(u'\n}}\t\n}}')-2] + PageEnd[PageEnd.find(u'\n}}\t\n}}')+len(u'\n}}\t\n}}'):len(PageEnd)]	
	if PageEnd.find(u'|1=') != -1 and PageEnd.find(u'|1=') < PageEnd.find(u'{{Wikiprojet'):
		PageEnd = PageEnd[0:PageEnd.find(u'|1=')] + PageEnd[PageEnd.find(u'|1=')+len(u'|1='):len(PageEnd)]
	if PageEnd.find(u'{{Wikiprojet}}') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet}}')+len(u'{{Wikiprojet')] + PageEnd[PageEnd.find(u'{{Wikiprojet}}')+len(u'{{Wikiprojet}}'):len(PageEnd)]	
	while PageEnd.find("gare|") != -1 and PageEnd.find("gare|") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("gare|")] + PageEnd[PageEnd.find("gare|")+len("gare|"):len(PageEnd)]
	while PageEnd.find("|boite=oui") != -1 and PageEnd.find("|boite=oui") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("|boite=oui")] + PageEnd[PageEnd.find("|boite=oui")+len("|boite=oui"):len(PageEnd)]
	while PageEnd.find(u'vérifié=oui') != -1 and PageEnd.find(u'vérifié=oui') < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find(u'vérifié=oui')] + PageEnd[PageEnd.find(u'vérifié=oui')+len(u'vérifié=oui'):len(PageEnd)]
	while PageEnd.find("||") != -1 and PageEnd.find("||") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("||")] + PageEnd[PageEnd.find("||")+1:len(PageEnd)]
	while PageEnd.find("\n|\n|") != -1 and PageEnd.find("\n|\n|") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("\n|\n|")] + PageEnd[PageEnd.find("\n|\n|")+2:len(PageEnd)]
	while PageEnd.find("\n\n|") != -1 and PageEnd.find("\n\n|") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("\n\n|")] + PageEnd[PageEnd.find("\n\n|")+1:len(PageEnd)]
	while PageEnd.find("\net ") != -1 and PageEnd.find("\net ") < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find("\net ")] + u'|' + PageEnd[PageEnd.find("\net ")+3:len(PageEnd)]
	while PageEnd.find(u'}}==') != -1:	
		PageEnd = PageEnd[0:PageEnd.find(u'}}==')+2] + u'\n' + PageEnd[PageEnd.find(u'}}==')+2:len(PageEnd)]
	if eval and PageEnd.find(eval) == -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')] + u'\n|' + eval + uation + u'\n' + PageEnd[PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageEnd)]

	# Choix si plusieurs avancements
	if PageEnd.find(u'|avancement=') != -1:
		PageTemp = PageEnd[PageEnd.find(u'|avancement=')+len(u'|avancement='):len(PageEnd)]
		while PageTemp.find(u'|avancement=') != -1:
			PageTemp2 = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):len(PageTemp)]
			if PageTemp2.find(u'\n') != -1 and PageTemp2.find(u'\n') < PageTemp2.find(u'|') and PageTemp2.find(u'\n') < PageTemp2.find(u'}}'):
				PageEnd = PageEnd[0:PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')] + PageEnd[PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')+len(u'|avancement=')+PageTemp2.find(u'\n')+1:len(PageEnd)]
			elif PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'\n') and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
				PageEnd = PageEnd[0:PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')] + PageEnd[PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')+len(u'|avancement=')+PageTemp2.find(u'|'):len(PageEnd)]
			else:
				PageEnd = PageEnd[0:PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')] + PageEnd[PageEnd.find(u'|avancement=')+len(u'|avancement=')+PageTemp.find(u'|avancement=')+len(u'|avancement=')+PageTemp2.find(u'}}'):len(PageEnd)]	
			PageTemp = PageEnd[PageEnd.find(u'|avancement=')+len(u'|avancement='):len(PageEnd)]
	if page.get() != PageEnd: 
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
			if Page.namespace() == 0 and Page.title() != u'Arthur Conan Doyle' and Page.title() != u'Currach': modification(u'Discussion:' + Page.title())

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
TraitementFile = lecture('articles_test.txt')
#TraitementLiens = crawlerLink(u'Modèle:Wikiprojet')
#TraitementCategory = crawlerCat(u'Catégorie:Écosse')
raw_input("Jackpot")

'''
cd "C:\Program Files\Apache Software Foundation\Apache2.2\htdocs\Personnel\mybot\pywikipedia\"
python fr.w.evaluation.py
http://fr.wikipedia.org/wiki/Sp%C3%A9cial:Pages_li%C3%A9es/Mod%C3%A8le:Importance
http://fr.wikipedia.org/wiki/Sp%C3%A9cial:Pages_li%C3%A9es/Mod%C3%A8le:Wikiproje
effacer |boite=|oldid=
# N'ajoute pas "musique" quand "musique classique"
'''

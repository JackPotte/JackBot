#!/usr/bin/env python
# Ce script fusionne les évaluations existantes, et éventuellement en ajoute une au début (voir [[Modèle:Wikiprojet]]).
 
# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re
from wikipedia import *
 
# Déclaration
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
eval = u'industrie' # Nom à ajouter
uation = u'|?' # Noter l'importance et éventuellement l'avancement (ex : "|avancement=ébauche") sinon le bot ajoute seul "|avancement=?"
if eval != "":
	summary = u'Ajout de l\'évaluation à partir du portail : ' + eval
else:
	summary = u'[[Wikipédia:Prise de décision/Wikiprojet|Fusion des évaluations]]'
debogage = True

# Eléments obsolètes à remplacer (en minuscule), consensus http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Prise_de_d%C3%A9cision/Wikiprojet
Msize = 2 + 2
Mobsolete = range(1, Msize)
Mobsolete[1] = u'todo'
Mobsolete[2] = u'à faire'
 
Psize = 2 + 9
Pobsolete = range(1, Psize)
Pobsolete[1] = u'oldid'
Pobsolete[2] = u'boite'
Pobsolete[3] = u'boîte'
Pobsolete[4] = u'vérifié'
Pobsolete[5] = u'homonymie'
Pobsolete[6] = u'chronologie'
Pobsolete[7] = u'gare'
Pobsolete[8] = u'TGV'
Pobsolete[9] = u'GV'
''' Mange les importance=élevée
Pobsolete[10] = u'impotance='
Pobsolete[11] = u'importnace='
Pobsolete[12] = u'important'
'''

# Modification du wiki à partir du nom de la page
def modification(PageHS):
	if PageHS.find(u'/') != -1 and PageHS != u'Utilisateur:JackBot/test': return	 # On évite les sous-pages
	page = Page(site,PageHS)
	print(PageHS.encode(config.console_encoding, 'replace'))
	PageEnd = ""
	PageTemp2 = ""
	avancement = ""
	projet = "False"
	if page.exists():
		if page.namespace() != 1 and PageHS != u'Utilisateur:JackBot/test':		    
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
		if PageTemp[len(PageTemp)-1:len(PageTemp)] == u'}': PageTemp = PageTemp + u'\n'
		if PageTemp.find(u'{{Évaluation multiprojet|\n') != -1: 
			PageTemp = PageTemp[0:PageTemp.find(u'{{Évaluation multiprojet|\n')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{Évaluation multiprojet|\n')+len(u'{{Évaluation multiprojet'):len(PageTemp)]
			PageTemp2 = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')]
			while PageTemp2.find(u'|\n') != -1 and PageTemp2.find(u'|\n') < PageTemp2.find(u'}}'):
				PageTemp = PageTemp + PageTemp2[0:PageTemp2.find(u'|\n')] + u'\n|'
				PageTemp2 = PageTemp2[PageTemp2.find(u'|\n')+2:len(PageTemp2)]
			PageTemp = PageTemp + PageTemp2
		if PageTemp.find(u'{{évaluation multiprojet|\n') != -1: 
			PageTemp = PageTemp[0:PageTemp.find(u'{{évaluation multiprojet|\n')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{évaluation multiprojet|\n')+len(u'{{évaluation multiprojet'):len(PageTemp)]
			PageTemp2 = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')]
			while PageTemp2.find(u'|\n') != -1 and PageTemp2.find(u'|\n') < PageTemp2.find(u'}}'):
				PageTemp = PageTemp + PageTemp2[0:PageTemp2.find(u'|\n')] + u'\n|'
				PageTemp2 = PageTemp2[PageTemp2.find(u'|\n')+2:len(PageTemp2)]
			PageTemp = PageTemp + PageTemp2
		if PageTemp.find(u'{{Évaluation multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{Évaluation multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{Évaluation multiprojet')+len(u'{{Évaluation multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{Évaluation_multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{Évaluation_multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{Évaluation_multiprojet')+len(u'{{Évaluation_multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{évaluation multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{évaluation multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{évaluation multiprojet')+len(u'{{évaluation multiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{évaluation_multiprojet') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{évaluation_multiprojet')] + u'{{Wikiprojet' + PageTemp[PageTemp.find(u'{{évaluation_multiprojet')+len(u'{{évaluation_multiprojet'):len(PageTemp)]
		while PageTemp.find(u'Avancement=') != -1: PageTemp = PageTemp[0:PageTemp.find(u'Avancement=')] + u'a' + PageTemp[PageTemp.find(u'Avancement=')+1:len(PageTemp)]
		while PageTemp.find(u'{{projet ') != -1 and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Éphéméride}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet éphéméride}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Bar}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet bar}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Café}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet café}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Combat libre}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet combat libre}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet FGS}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet France du Grand Siècle}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Littérature pour enfants}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet littérature pour enfants}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet Psychotrope}}') and PageTemp.find(u'{{projet ') != PageTemp.find(u'{{projet psychotrope}}'):
			PageTemp = PageTemp[0:PageTemp.find(u'{{projet ')] + u'{{Wikiprojet ' + PageTemp[PageTemp.find(u'{{projet ')+len(u'{{projet '):len(PageTemp)]
		while PageTemp.find(u'{{Projet ') != -1 and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Éphéméride}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet éphéméride}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Bar}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet bar}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Café}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet café}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Combat libre}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet combat libre}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet FGS}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet France du Grand Siècle}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Littérature pour enfants}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet littérature pour enfants}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet Psychotrope}}') and PageTemp.find(u'{{Projet ') != PageTemp.find(u'{{Projet psychotrope}}'):
			PageTemp = PageTemp[0:PageTemp.find(u'{{Projet ')] + u'{{Wikiprojet ' + PageTemp[PageTemp.find(u'{{Projet ')+len(u'{{Projet '):len(PageTemp)]
		while PageTemp.find(u'}\n{{Wikiprojet') < PageTemp.find(u'}}') and PageTemp.find(u'}\n{{Wikiprojet') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'}\n{{Wikiprojet')] + u'}' + PageTemp[PageTemp.find(u'}\n{{Wikiprojet'):len(PageTemp)]
		if PageTemp.find(u'{{Wikiprojet') != -1 and PageTemp.find(u'}}') == -1:
			if PageTemp.find("\n") == -1:
				PageTemp = PageTemp + u'}}'
			else:
				PageTemp2 = PageTemp[PageTemp.find(u'{{Wikiprojet'):len(PageTemp)]
				PageTemp3 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
			    	if PageTemp3.find(u'\n') < PageTemp3.find(u'|'):
			    		PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+PageTemp2.find(u'\n')] + u'}}' + PageTemp[PageTemp.find(u'{{Wikiprojet')+PageTemp2.find(u'\n'):len(PageTemp)]
			    	elif PageTemp3.find(u'\n') != -1:
							PageTemp4 = PageTemp3[PageTemp3.find(u'\n')+1:len(PageTemp3)]
							if PageTemp4.find(u'\n') < PageTemp4.find(u'|'):
								PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+PageTemp2.find(u'\n')+1+PageTemp3.find(u'\n')] + u'}}' + PageTemp[PageTemp.find(u'{{Wikiprojet')+PageTemp2.find(u'\n')+1+PageTemp3.find(u'\n'):len(PageTemp)]
							else:
								return  # Modèle à traiter manuellement
			    	else:
			    		return	# Modèle à traiter manuellement
		if PageTemp.find(u'<nowiki>') < PageTemp.find(u'{{wikiprojet') and PageTemp.find(u'<nowiki>') != -1 and PageTemp.find(u'</nowiki>') > PageTemp.find(u'{{wikiprojet'): return # Quand on discute des modèles le bot n'y touche pas
		elif PageTemp.find(u'<pre>') < PageTemp.find(u'{{wikiprojet') and PageTemp.find(u'<pre>') != -1 and PageTemp.find(u'</pre>') > PageTemp.find(u'{{wikiprojet'): return
		elif PageTemp.find(u'<source>') < PageTemp.find(u'{{wikiprojet') and PageTemp.find(u'<source>') != -1 and PageTemp.find(u'</source>') > PageTemp.find(u'{{wikiprojet'): return
		PageTemp2 = PageTemp3 = PageTemp4 = ""
		position = -2
		while position != -1 and position < len(PageTemp): # On déplace les données d'une page provisoire dans une page finale jusqu'à disparition de la première
			#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
			#if position == -1: position = PageTemp.find(u'{{wikiprojet')					# pb si modèle absent : détecté présent
			#position = PageTemp.find(u'{{wikiprojet')										# pb de boucle infinie
			if position == -1 or position == -2: position = PageTemp.find(u'{{wikiprojet')	# pb d'absence de fusion des modèles
			if position == -1 and projet == "True": break  # S'il n'y a plus d'évaluation à traiter
			elif position == -1 and projet == "False":      # S'il n'y a aucune évaluation
				if eval:
					if debogage == True: print u'Ajout de {{Wikiprojet'
					PageEnd = PageEnd + "{{Wikiprojet|\n" + eval + uation + u'}}'
				else: return
			else: # S'il y a un modèle évaluation à traiter
				if debogage == True: print u'Modèle {{Wikiprojet existant'
				if position == PageTemp.find(u'{{wikiprojet'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{wikiprojet')+2] + u'W' + PageTemp[PageTemp.find(u'{{wikiprojet')+3:len(PageTemp)]
				if PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet'):PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1] == u' ' and PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+2] != u'\n' and PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+2] != u'|': # Normalisation du modèle
					PageTemp = PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')] + u'|' + PageTemp[PageTemp.find(u'{{Wikiprojet')+len('{{Wikiprojet')+1:len(PageTemp)]
				# Premier modèle Wikiprojet
				if projet == "False":
					PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')]
					PageTemp = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)] # PageTemp = paramètres}}...
					# Eviter les modifications cosmétiques
					if eval: 
						if PageTemp.find(eval) != -1 and PageTemp.find(eval) < PageTemp.find(u'}}'): return
					# Bug des évaluations sans jugement : http://fr.wikipedia.org/w/index.php?title=Discussion:000&diff=prev&oldid=63627129
					while PageTemp.find(u'|avancement=|importance=|') != -1:
						PageTemp = PageTemp[0:PageTemp.find(u'|avancement=|importance=|')] + u'|avancement=?|importance=?|' + PageTemp[PageTemp.find(u'|avancement=|importance=|')+len(u'|avancement=|importance=|'):len(PageTemp)]
					# Aucun paramètre importance= dans Wikiprojet
					if PageTemp.find(u'importance=') != -1 and PageTemp.find(u'importance=') < PageTemp.find(u'}}'):
						PageTemp = PageTemp[0:PageTemp.find(u'importance=')] + PageTemp[PageTemp.find(u'importance=')+len(u'importance='):len(PageTemp)]				   
					# Récupération de l'état d'avancement du Wikiprojet
					while PageTemp.find(u'|}}') != -1: PageTemp = PageTemp[0:PageTemp.find(u'|}}')] + PageTemp[PageTemp.find(u'|}}')+1:len(PageTemp)]
					while PageTemp.find(u'| avancement    =') != -1: PageTemp = PageTemp[0:PageTemp.find(u'| avancement    =')] + u'|avancement=' + PageTemp[PageTemp.find(u'| avancement    =')+len(u'| avancement    ='):len(PageTemp)]
					while PageTemp.find(u'| avancement = ') != -1: PageTemp = PageTemp[0:PageTemp.find(u'| avancement = ')] + u'|avancement=' + PageTemp[PageTemp.find(u'| avancement = ')+len(u'| avancement = '):len(PageTemp)]
					while PageTemp.find(u'| avancement =') != -1: PageTemp = PageTemp[0:PageTemp.find(u'| avancement =')] + u'|avancement=' + PageTemp[PageTemp.find(u'| avancement =')+len(u'| avancement ='):len(PageTemp)]
					while PageTemp.find(u'| avancement=') != -1: PageTemp = PageTemp[0:PageTemp.find(u'| avancement=')] + u'|avancement=' + PageTemp[PageTemp.find(u'| avancement=')+len(u'| avancement='):len(PageTemp)]
					while PageTemp.find(u'| avancement ') != -1 and PageTemp.find(u'| avancement ') < 1000: PageTemp = PageTemp[0:PageTemp.find(u'| avancement ')] + u'|avancement ' + PageTemp[PageTemp.find(u'| avancement ')+len(u'| avancement '):len(PageTemp)]
					while PageTemp.find(u'|avancement ') != -1 and PageTemp.find(u'|avancement ') < 1000:
						PageTemp3 = PageTemp[PageTemp.find(u'|avancement ')+len(u'|avancement '):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'|avancement ')+len(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement ')+len(u'|avancement ')+PageTemp3.find(u'='):len(PageTemp)]
					PageTemp3 = PageTemp[PageTemp.find(u'|avancement=')+1:len(PageTemp)]
					if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
						if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1] == u'|avancement=?':
							PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
							if PageTemp4.find(u'|avancement=') != -1:
								PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
								if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
								elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
								else:
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
						else:
							avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1]
					elif PageTemp3.find(u'\n') != -1 and PageTemp3.find(u'\n') < PageTemp3.find(u'}'):
						if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1] == u'|avancement=?':
							PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
							if PageTemp4.find(u'|avancement=') != -1:
								PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
								if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
								elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
								else:
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
						else:
							avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1]
					else:
						if PageTemp[PageTemp.find(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1] == u'|avancement=?':
							PageTemp4 = PageTemp3[PageTemp3.find(u'|avancement=')+1:len(PageTemp3)]
							if PageTemp4.find(u'|avancement=') != -1:
								PageTemp5 = PageTemp4[PageTemp4.find(u'|avancement=')+1:len(PageTemp4)]
								if PageTemp5.find(u'|') != -1 and PageTemp5.find(u'|') < PageTemp5.find(u'}'):
									PageEnd = PageEnd + PageTemp4[PageTemp4.find(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'|')+1]
								elif PageTemp5.find(u'\n') != -1 and PageTemp5.find(u'\n') < PageTemp5.find(u'}'):
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'\n')+1]
								else:
									avancement = PageTemp4[PageTemp4.find(u'|avancement=')+len(u'|avancement='):PageTemp4.find(u'|avancement=')+PageTemp5.find(u'}')+1]
						else:
							avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1]    
					# Un seul avancement par Wikiprojet, de préférence différent de ?
					while PageTemp.find(u'|avancement=') != -1:
						PageTemp3 = PageTemp[PageTemp.find(u'|avancement=')+1:len(PageTemp)]
						if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'\n') and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
							if not avancement or avancement == u'?':
								avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+1+PageTemp3.find(u'|')]
							PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1:len(PageTemp)]
						elif PageTemp3.find(u'\n') != -1 and PageTemp3.find(u'\n') < PageTemp3.find(u'}'):
							if not avancement or avancement == u'?':
								avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+1+PageTemp3.find(u'\n')]
							PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1:len(PageTemp)]
						elif PageTemp3.find(u'}') != -1:
							if not avancement or avancement == u'?':
								avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+1+PageTemp3.find(u'}')]
							PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1:len(PageTemp)]
						else: # Modèle à réparer sur une seule ligne
							if not avancement or avancement == u'?':
								avancement = PageTemp[PageTemp.find(u'|avancement=')+len(u'|avancement='):PageTemp.find(u'|avancement=')+1+PageTemp3.find(u'}')]
							PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1:len(PageTemp)] + u'}}'
					# Suppression des avancements supplémentaires
					while PageTemp.find(u'|avancement=') != -1:
						PageTemp3 = PageTemp[PageTemp.find(u'|avancement=')+1:len(PageTemp)]
						if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'\n'):
							if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'|')+1:len(PageTemp)]
							else:
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1:len(PageTemp)]
						elif PageTemp3.find(u'\n') != -1 and PageTemp3.find(u'\n') < PageTemp3.find(u'}'):
							if PageTemp3.find(u'\n') != -1 and PageTemp3.find(u'\n') < PageTemp3.find(u'}'):
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'\n')+1:len(PageTemp)]
							else:
								PageTemp = PageTemp[0:PageTemp.find(u'|avancement=')] + PageTemp[PageTemp.find(u'|avancement=')+PageTemp3.find(u'}')+1:len(PageTemp)]
					PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')]
					PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
					projet = "True"
				else: # Modèle Wikiprojet superfétatoire trouvé
					PageTemp2 = PageTemp2 + PageTemp[0:PageTemp.find(u'{{Wikiprojet')] # Retient les éléments entre les Wikiprojets
					PageTemp = PageTemp[PageTemp.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageTemp)]				    
					PageTemp3 = PageTemp[1:PageTemp.find(u'}}')]
					if PageTemp3.find(u'|') != -1:
						if PageEnd.find(u'|' + PageTemp3[0:PageTemp3.find(u'|')+1]) != -1: # Si elle existe déjà
							PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
						else:
							if PageTemp.find(u'importance=') != -1 and PageTemp.find(u'importance=') < PageTemp.find(u'}}'): # Aucune importance= par Wikiprojet
								PageTemp = PageTemp[0:PageTemp.find(u'importance=')] + PageTemp[PageTemp.find(u'importance=')+len(u'importance='):len(PageTemp)]
							PageEnd = PageEnd + u'\n' + PageTemp[0:PageTemp.find(u'}}')]
							PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
					else:
						PageEnd = PageEnd + u'\n' + PageTemp[0:PageTemp.find(u'}}')]
						PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]						
			position = PageTemp.find(u'{{Wikiprojet')
		#print (PageEnd.encode(config.console_encoding, 'replace'))
		#raw_input(len(PageEnd))
		#print (PageTemp.encode(config.console_encoding, 'replace'))
		#raw_input(len(PageTemp))
		if PageTemp.find(u'}}') == -1 or PageTemp.find(u'}}') > PageTemp.find(u'{{') or PageTemp.find(u'}}') > PageTemp.find(u'<math>'): # Fin des évaluations
			if PageEnd.find("{{") != -1:
				PageEnd = PageEnd + u'}}' + PageTemp2 + PageTemp[0:len(PageTemp)]
			else:
				PageEnd = PageEnd + PageTemp2 + PageTemp[0:len(PageTemp)]
		else:
			PageEnd = PageEnd + PageTemp2 + PageTemp[0:len(PageTemp)]
	else:
		if debogage == True: print u'La page n\'existe pas'
		if eval != "":
			PageEnd = "{{Wikiprojet\n|" + eval + uation + u'\n|avancement=?}}\n'
			arretdurgence()
			# Si ébauche
			if PageEnd.find(u'avancement=?') > 0 and PageEnd.find(u'avancement=?') < 1000:
				Recto = Page(site,PageHS[len(u'Discussion:'):len(PageHS)])
				recto = Recto.get()
				if recto.find(u'{{ébauche') != -1:
					recto = recto[recto.find(u'{{ébauche'):len(recto)]
					if recto.find(eval) > 0 and recto.find(eval) < recto.find(u'}}'): PageEnd = PageEnd[0:PageEnd.find(u'avancement=?')+len(u'avancement=')] + u'ébauche' + PageEnd[PageEnd.find(u'avancement=?')+len(u'avancement=?'):len(PageEnd)]
				elif recto.find(u'{{Ébauche') != -1: 
					recto = recto[recto.find(u'{{Ébauche'):len(recto)]
					if recto.find(eval) > 0 and recto.find(eval) < recto.find(u'}}'): PageEnd = PageEnd[0:PageEnd.find(u'avancement=?')+len(u'avancement=')] + u'ébauche' + PageEnd[PageEnd.find(u'avancement=?')+len(u'avancement=?'):len(PageEnd)]
			page.put(PageEnd, summary)
			return
		else:
			return
	# Certains paramètres sont sous la forme "avancement eval=" dans Wikiprojet
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(u'|avancement') != -1 and PageTemp.find(u'|avancement') < PageTemp.find(u'}}'):
		PageTemp2 = PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement'):len(PageTemp)]
		if PageTemp2.find(u'|') > 0 and PageTemp2.find(u'|') < PageTemp2.find(u'\n'):
			if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
				if not avancement or avancement == u'?':
					avancement = PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'=')+1:PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'|')]
				PageTemp = PageTemp[0:PageTemp.find(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'|'):len(PageTemp)]
			elif PageTemp2.find(u'}}') != -1 and PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
				if not avancement or avancement == u'?':
					avancement = PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'=')+1:PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'}}')]
				PageTemp = PageTemp[0:PageTemp.find(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'}}'):len(PageTemp)]
			else:
				return # Modèle à traiter manuellement
		elif PageTemp2.find(u'\n') != -1 and PageTemp2.find(u'\n') < PageTemp2.find(u'}}'):
			if PageTemp2.find(u'\n') != -1 and PageTemp2.find(u'\n') < PageTemp2.find(u'}}'):
				if not avancement or avancement == u'?':
					avancement = PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'=')+1:PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'\n')]
				PageTemp = PageTemp[0:PageTemp.find(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'\n'):len(PageTemp)]
			elif PageTemp2.find(u'}}') != -1 and PageTemp2.find(u'\n') > PageTemp2.find(u'}}'):
				if not avancement or avancement == u'?':
					avancement = PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'=')+1:PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'}}')]
				PageTemp = PageTemp[0:PageTemp.find(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'}}'):len(PageTemp)]
			else:
				return # Modèle à traiter manuellement
		else:
			PageTemp = PageTemp[0:PageTemp.find(u'|avancement')] + PageTemp[PageTemp.find(u'|avancement')+len(u'|avancement')+PageTemp2.find(u'}}'):len(PageTemp)]
	PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')] + PageTemp
	# Ajout de l'avancement à la fin du modèle
	if not avancement or avancement == u'?':	   
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')] + u'\n|avancement=?' + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}'):len(PageEnd)]
	else:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')] + u'\n|avancement=' + avancement + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}'):len(PageEnd)]
	# Effacement des modèles "à faire"
	todo = ""
	for p in range(1,Msize-1):
		if PageEnd.find(u'<nowiki>') < Mobsolete[p] and PageEnd.find(u'<nowiki>') != -1 and PageEnd.find(u'</nowiki>') > Mobsolete[p]:
			break # Quand on discute des modèles le bot n'y touche pas
		elif PageEnd.find(u'<pre>') < Mobsolete[p] and PageEnd.find(u'<pre>') != -1 and PageEnd.find(u'</pre>') > Mobsolete[p]:
			break
		elif PageEnd.find(u'<source>') < Mobsolete[p] and PageEnd.find(u'<source>') != -1 and PageEnd.find(u'</source>') > Mobsolete[p]:
			break
		else:
			# Corrections des erreurs avant retrait du modèle obsolète
			while PageEnd.find(u'{{' + Mobsolete[p] + u'}\n') != -1:
				PageEnd = PageEnd[0:PageEnd.find(u'{{' + Mobsolete[p] + u'}\n')+len(u'{{' + Mobsolete[p] + u'}')] + u'}' + PageEnd[PageEnd.find(u'{{' + Mobsolete[p] + u'}\n')+len(u'{{' + Mobsolete[p] + u'}'):len(PageEnd)]
			while PageEnd.find(u'\n{' + Mobsolete[p] + u'}}') != -1:
			 	PageEnd = PageEnd[0:PageEnd.find(u'\n{' + Mobsolete[p] + u'}}')] + u'{' + PageEnd[PageEnd.find(u'{' + Mobsolete[p] + u'}}\n'):len(PageEnd)]
			while PageEnd.find(u'\n{' + Mobsolete[p] + u'}\n') != -1:
				PageEnd = PageEnd[0:PageEnd.find(u'\n{' + Mobsolete[p] + u'}\n')] + u'{' + PageEnd[PageEnd.find(u'\n{' + Mobsolete[p] + u'}\n'):PageEnd.find(u'\n{' + Mobsolete[p] + u'}\n')+len(u'\n{' + Mobsolete[p] + u'}')] + u'}' + PageEnd[PageEnd.find(u'\n{' + Mobsolete[p] + u'}\n')+len(u'\n{' + Mobsolete[p] + u'}'):len(PageEnd)]
			while PageEnd.find(u'{{' + Mobsolete[p]) != -1:
				PageTemp = PageEnd[PageEnd.find(u'{{' + Mobsolete[p])+len(u'{{' + Mobsolete[p]):len(PageEnd)]
				if PageTemp.find(u'|') < PageTemp.find(u'}}') and PageTemp.find(u'|') != -1:
					# On déplace le contenu du modèle
					PageTemp2 = PageTemp[0:PageTemp.find(u'|')+1]
					PageTemp = PageTemp[PageTemp.find(u'|')+1:len(PageTemp)]
					while PageTemp.find(u'{{') < PageTemp.find(u'}}') and PageTemp.find(u'{{') != -1:
						todo = todo + PageTemp[0:PageTemp.find(u'}}')+2]
						PageTemp2 = PageTemp2 + PageTemp[0:PageTemp.find(u'}}')+2]
						PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
					todo = todo + PageTemp[0:PageTemp.find(u'}}')]
				PageEnd = PageEnd[0:PageEnd.find(u'{{' + Mobsolete[p])] + PageEnd[PageEnd.find(u'{{' + Mobsolete[p]) + len(u'{{' + Mobsolete[p]) + len(PageTemp2) + PageTemp.find(u'}}')+2:len(PageEnd)]	 
			Mobsolete2 = Mobsolete[p][0:1].upper() + Mobsolete[p][1:len(Mobsolete[p])]
			while PageEnd.find(u'{{' + Mobsolete2) != -1:
				PageTemp = PageEnd[PageEnd.find(u'{{' + Mobsolete2)+len(u'{{' + Mobsolete2):len(PageEnd)]
				if PageTemp.find(u'|') < PageTemp.find(u'}}') and PageTemp.find(u'|') != -1:
					# On déplace le contenu du modèle
					PageTemp2 = PageTemp[0:PageTemp.find(u'|')+1]
					PageTemp = PageTemp[PageTemp.find(u'|')+1:len(PageTemp)]
					while PageTemp.find(u'{{') < PageTemp.find(u'}}') and PageTemp.find(u'{{') != -1:
						todo = todo + PageTemp[0:PageTemp.find(u'}}')+2]
						PageTemp2 = PageTemp2 + PageTemp[0:PageTemp.find(u'|')+1]
						PageTemp = PageTemp[PageTemp.find(u'|')+1:len(PageTemp)]
					todo = todo + PageTemp[0:PageTemp.find(u'}}')]
				PageEnd = PageEnd[0:PageEnd.find(u'{{' + Mobsolete2)] + PageEnd[PageEnd.find(u'{{' + Mobsolete2) + len(u'{{' + Mobsolete2) + len(PageTemp2) + PageTemp.find(u'}}')+2:len(PageEnd)]	 
		p = p + 1
	while todo[0:1] == u'\n' or todo[0:1] == u'\r' or todo[0:1] == u' ':
		todo = todo[1:len(todo)]
	if len(todo) > 1 and todo <> u'à faire':
		page2 = Page(site,PageHS + u'/À faire')
		if page2.exists():
			try:
				PageTemp = page2.get()
			except wikipedia.NoPage:
				print "NoPage"
				return
			except wikipedia.IsRedirectPage:
				print "Redirect page"
				return
			except wikipedia.LockedPage:
				print "Locked/protected page"
				return
			todo = PageTemp + u'\n' + todo
 
		# Sauvegarde de la sous-page "à faire"
		sauvegarde(page2,todo,summary)

	# Cosmétique normalisant pour la suite
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(u'<br>') != -1 and PageTemp.find(u'<br>') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'<br>')] + PageEnd[PageEnd.find(u'<br>')+len(u'<br>'):len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(u'| ') != -1 and PageTemp.find(u'| ') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'| ')+1] + PageEnd[PageEnd.find(u'| ')+len(u'| '):len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(u'|\n') != -1 and PageTemp.find(u'|\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'|\n')+1] + PageEnd[PageEnd.find(u'|\n')+len(u'|\n'):len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
 
	# Effacement des paramètres Wikiprojet désuets
	for p in range(1,Psize-1):
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
		Pobsolete1 = '|' + Pobsolete[p]
		Pobsolete2 = '|' + Pobsolete[p][0:1].upper() + Pobsolete[p][1:len(Pobsolete[p])]
		while PageTemp.find(Pobsolete1) != -1 and PageTemp.find(Pobsolete1) < PageTemp.find(u'}}'):
			PageTemp2 = PageTemp[PageTemp.find(Pobsolete1) + len(Pobsolete1):len(PageTemp)]
			if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'\n') and PageTemp2.find(u'|') < PageTemp2.find(u'}'):
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1) + len(Pobsolete1) + PageTemp2.find(u'|'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
			elif PageTemp2.find(u'\n') < PageTemp2.find(u'}'):
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1) + len(Pobsolete1) + PageTemp2.find(u'\n'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
			else:
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete1) + len(Pobsolete1) + PageTemp2.find(u'}'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
		while PageTemp.find(Pobsolete2) != -1 and PageTemp.find(Pobsolete2) < PageTemp.find(u'}}'):
			PageTemp2 = PageTemp[PageTemp.find(Pobsolete2) + len(Pobsolete2):len(PageTemp)]
			if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'\n') and PageTemp2.find(u'|') < PageTemp2.find(u'}'):
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2) + len(Pobsolete2) + PageTemp2.find(u'|'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
			elif PageTemp2.find(u'\n') < PageTemp2.find(u'}'):
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2) + len(Pobsolete2) + PageTemp2.find(u'\n'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
			else:
				PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2)] + PageEnd[PageEnd.find(u'{{Wikiprojet') + PageTemp.find(Pobsolete2) + len(Pobsolete2) + PageTemp2.find(u'}'):len(PageEnd)]
				PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
		p = p + 1

	# Gestion des exceptions
	if PageEnd.find(u'{{Wikiprojet}}') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet}}')+len(u'{{Wikiprojet')] + PageEnd[PageEnd.find(u'{{Wikiprojet}}')+len(u'{{Wikiprojet}}'):len(PageEnd)]  
	if PageEnd.find(u'|à faire=non') != -1 and PageEnd.find(u'|à faire=non') < PageEnd.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'|à faire=non')] + PageEnd[PageEnd.find(u'|à faire=non')+len(u'|à faire=non'):len(PageEnd)]
	if PageEnd.find(u'|à faire =non') != -1 and PageEnd.find(u'|à faire =non') < PageEnd.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'|à faire =non')] + PageEnd[PageEnd.find(u'|à faire =non')+len(u'|à faire =non'):len(PageEnd)]
	if PageEnd.find(u'|à faire = non') != -1 and PageEnd.find(u'|à faire = non') < PageEnd.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'|à faire = non')] + PageEnd[PageEnd.find(u'|à faire = non')+len(u'|à faire = non'):len(PageEnd)]
	if PageEnd.find(u'{{Évaluations WP1|1=') != -1 and PageEnd.find(u'{{Évaluations WP1|1=') < PageEnd.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Évaluations WP1|1=')] + PageEnd[PageEnd.find(u'{{Évaluations WP1|1=')+len(u'{{Évaluations WP1|1='):len(PageEnd)]
	if PageEnd[PageEnd.find(u'|avancement=' + avancement)-1:PageEnd.find(u'|avancement=' + avancement)] != u'\n' and PageEnd[PageEnd.find(u'|avancement=' + avancement)-1:PageEnd.find(u'|avancement=' + avancement)] != u'\r':
		PageEnd = PageEnd[0:PageEnd.find(u'|avancement=' + avancement)] + u'\n' + PageEnd[PageEnd.find(u'|avancement=' + avancement):len(PageEnd)]
	if PageEnd.find(u'{{Wikiprojet|') != -1 and PageEnd.find(u'|avancement=') == -1 and PageEnd.find(u'| avancement=') == -1 and PageEnd.find(u'|avancement =') == -1 and PageEnd.find(u'| avancement =') == -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet|')] + u'avancement=?|' + PageEnd[PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet|'):len(PageEnd)]
	if PageEnd.find(u'avancement=|') != -1 and PageEnd.find(u'avancement=|') < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find(u'avancement=|')+len(u'avancement=|')-1] + u'?' + PageEnd[PageEnd.find(u'avancement=|')+len(u'avancement=|')-1:len(PageEnd)]
	if PageEnd.find(u'avancement=\n') != -1 and PageEnd.find(u'avancement=\n') < PageEnd.find("}}"):
		PageEnd = PageEnd[0:PageEnd.find(u'avancement=\n')+len(u'avancement=\n')-1] + u'?' + PageEnd[PageEnd.find(u'avancement=\n')+len(u'avancement=\n')-1:len(PageEnd)]
	while PageEnd[PageEnd.find(u'\n|avancement=')-1:PageEnd.find(u'\n|avancement=')] == u'\n' or PageEnd[PageEnd.find(u'\n|avancement=')-1:PageEnd.find(u'\n|avancement=')] == u' ':  
		PageEnd = PageEnd[0:PageEnd.find(u'\n|avancement=')-1] + PageEnd[PageEnd.find(u'\n|avancement='):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'}}') == PageTemp.find(u'}}}}'): # Pas d'imbrication du Wikiprojet
		PageEnd = PageEnd[0:PageEnd.find(u'}}}}')] + PageEnd[PageEnd.find(u'}}}}')+2:len(PageEnd)]
	while PageTemp.find(u'}|') != -1 and PageTemp.find(u'}|') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find('}|')] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find('}|')+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')+2:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')+3] != u'\n':
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')+2] + u'\n' + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(u'}}')+2:len(PageEnd)]  
	while PageTemp.find("||") != -1 and PageTemp.find("||") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find("||")] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find("||")+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find("\n|\n|") != -1 and PageTemp.find("\n|\n|") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find("\n|\n|")] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find("\n|\n|")+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(" |") != -1 and PageTemp.find(" |") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(" |")] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(" |")+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find("| ") != -1 and PageTemp.find("| ") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find("| ")+1] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find("| ")+2:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(" }}") != -1 and PageTemp.find(" }}") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find(" }}")] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find(" }}")+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find("\net ") != -1 and PageTemp.find("\net ") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find("\net ")] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find("\net ")+1:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find("|Importance=") != -1 and PageTemp.find("|Importance=") < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find("|Importance=")+1] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find("|Importance=")+len(u'|Importance='):len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageEnd.find(u'\n|1=\n') != -1 and PageEnd.find(u'\n|1=\n') < (PageEnd.find(u'{{Wikiprojet') + PageTemp.find(u'}}')):
		PageEnd = PageEnd[0:PageEnd.find(u'\n|1=\n')] + PageEnd[PageEnd.find(u'\n|1=\n')+4:len(PageEnd)]
	while PageEnd.find(u'}}==') != -1 and PageEnd.find(u'}}==') < (PageEnd.find(u'{{Wikiprojet') + PageTemp.find(u'}}')):
		PageEnd = PageEnd[0:PageEnd.find(u'}}==')+2] + u'\n' + PageEnd[PageEnd.find(u'}}==')+2:len(PageEnd)]
	while PageEnd.find(u'\n\n') != -1 and PageEnd.find(u'\n\n') < (PageEnd.find(u'{{Wikiprojet') + PageTemp.find(u'}}')):     
		PageEnd = PageEnd[0:PageEnd.find(u'\n\n')] + PageEnd[PageEnd.find(u'\n\n')+1:len(PageEnd)]
	# Bug du pipe au début
	PageTemp2 = PageEnd[0:PageEnd.find(u'{{Wikiprojet')]
	if (PageTemp2.rfind(u'}}') > PageTemp2.rfind(u'{{') or PageTemp2.find(u'{{') == -1) and PageEnd.find(u'|\n{{Wikiprojet') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'|\n{{Wikiprojet')] + PageEnd[PageEnd.find(u'|\n{{Wikiprojet')+2:len(PageEnd)]
	if (PageTemp2.rfind(u'}}') > PageTemp2.rfind(u'{{') or PageTemp2.find(u'{{') == -1) and PageEnd.find(u'| \n{{Wikiprojet') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'| \n{{Wikiprojet')] + PageEnd[PageEnd.find(u'| \n{{Wikiprojet')+3:len(PageEnd)]
	# Bug de l'espace http://fr.wikipedia.org/w/index.php?title=Discussion:Saint-Barth%C3%A9lemy_%28Antilles_fran%C3%A7aises%29&diff=63402900&oldid=57421892
	if (PageTemp2.rfind(u'}}') > PageTemp2.rfind(u'{{') or PageTemp2.find(u'{{') == -1) and PageEnd[0:14] == u'|\n{{Wikiprojet' != -1:
		PageEnd = PageEnd[2:len(PageEnd)]
	if (PageTemp2.rfind(u'}}') > PageTemp2.rfind(u'{{') or PageTemp2.find(u'{{') == -1) and PageEnd[0:15] == u'| \n{{Wikiprojet' != -1:
		PageEnd = PageEnd[3:len(PageEnd)]
	if eval and PageEnd.find(eval) == -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')] + u'\n|' + eval + uation + u'\n' + PageEnd[PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageEnd)]
	if PageEnd.find(u'{{Wikiprojet|') != -1:
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet')] + u'\n' + PageEnd[PageEnd.find(u'{{Wikiprojet|')+len(u'{{Wikiprojet'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	while PageTemp.find(u'?|?') != -1 and PageTemp.find(u'?|?') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+PageTemp.find('?|?')] + PageEnd[PageEnd.find(u'{{Wikiprojet')+PageTemp.find('?|?')+2:len(PageEnd)]
		PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	# Paramètres à corriger
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'avancement=ebauche') != -1 and PageTemp.find(u'avancement=ebauche') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'avancement=ebauche')+len(u'avancement=')] + u'ébauche' + PageEnd[PageEnd.find(u'avancement=ebauche')+len(u'avancement=ebauche'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'moyen\n') != -1 and PageTemp.find(u'moyen\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'moyen\n')+len(u'moyen')] + u'ne' + PageEnd[PageEnd.find(u'moyen\n')+len(u'moyen'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'Moyen\n') != -1 and PageTemp.find(u'Moyen\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'Moyen\n')+len(u'Moyen')] + u'ne' + PageEnd[PageEnd.find(u'Moyen\n')+len(u'Moyen'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'élevé\n') != -1 and PageTemp.find(u'élevé\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'élevé\n')+len(u'élevé')] + u'e' + PageEnd[PageEnd.find(u'élevé\n')+len(u'élevé'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'max\n') != -1 and PageTemp.find(u'max\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'max\n')+len(u'max')] + u'imum' + PageEnd[PageEnd.find(u'max\n')+len(u'max'):len(PageEnd)]
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet'):len(PageEnd)]
	if PageTemp.find(u'important\n') != -1 and PageTemp.find(u'important\n') < PageTemp.find(u'}}'):
		PageEnd = PageEnd[0:PageEnd.find(u'important\n')] + u'élevée' + PageEnd[PageEnd.find(u'important\n')+len(u'important'):len(PageEnd)]
	# On reprendre l'évaluation ligne par ligne pour voir s'il manque des importances
	PageTemp = PageEnd[PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet'):len(PageEnd)]
	PageEnd = PageEnd[0:PageEnd.find(u'{{Wikiprojet')+len(u'{{Wikiprojet')] + PageTemp[0:PageTemp.find(u'\n')+1]
	PageTemp = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
	while PageTemp.find(u'\n') != -1 and PageTemp.find(u'\n') < PageTemp.find(u'}}'):
		if (PageTemp[1:len(PageTemp)].find(u'|') == -1 or PageTemp[1:len(PageTemp)].find(u'|') > PageTemp[1:len(PageTemp)].find(u'\n')) and (PageTemp[1:len(PageTemp)].find(u'=') > PageTemp[1:len(PageTemp)].find(u'\n') or PageTemp[1:len(PageTemp)].find(u'=') == -1):
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'\n')] + u'|?\n'
		else:
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'\n')+1]
		PageTemp = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
	PageEnd = PageEnd + PageTemp
	while PageEnd[0:1] == u' ': PageEnd = PageEnd[1:len(PageEnd)]

	PageEnd = re.sub(ur'{{Wikiprojet([^}]*)\n\n([^}]*)}}', ur'{{Wikiprojet\1\n\2}}', PageEnd)
	#.replace(u'\n\n',u'\n')
	
	# Sauvegarde semie-automatique
	if PageEnd != PageBegin: sauvegarde(page,PageEnd,summary)

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
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
	gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "1")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

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
		print(Contenu[:1000].encode(config.console_encoding, 'replace'))
		result = raw_input("Sauvegarder ? (o/n)")
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
		
# Lancement
TraitementFile = crawlerFile('articles_list.txt')
'''
TraitementLiens = crawlerLink(u'Modèle:Évaluation multiprojet')
TraitementLiens = crawlerLink(u'Modèle:todo')
TraitementLiens = crawlerLink(u'Modèle:Todo')
TraitementLiens = crawlerLink(u'Modèle:à faire')
TraitementLiens = crawlerLink(u'Modèle:À faire')
TraitementLiens = crawlerLink(u'Modèle:Wikiprojet Finance')
TraitementLiens = crawlerLink(u'Modèle:Wikiprojet Blues')
TraitementLiens = crawlerLink(u'Modèle:Wikiprojet Athlétisme')

TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementCategorie = crawlerCat(u'Écosse')
TraitementRecherche = crawlerSearch(u'Écosse')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
while 1:
     TraitementRC = crawlerRC()


Exceptions :
http://fr.wikipedia.org/wiki/Sp%C3%A9cial:Pages_li%C3%A9es/Mod%C3%A8le:Importance
http://fr.wikipedia.org/wiki/Sp%C3%A9cial:Pages_li%C3%A9es/Mod%C3%A8le:Wikiproje
{{Wikirojet droit}} (qui n'a pas toujours d'importance)
|wikiconcours mars 2011=24
=maximale => maximum
=élevé => élevée
=moyen => moyenne
'''

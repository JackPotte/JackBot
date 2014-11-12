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
	
	# Clés de tri
	sizeR = 7
	regex = range(1, sizeR+1)
	regex[1] = ur'()\n{{[Cc]lé de tri[^}]*}}'
	regex[2] = ur'({{[Cc]hapitre[^}]*)\| *clé *=[^}\|]*'
	regex[3] = ur'({{[Ll]eçon[^}]*)\| *clé *=[^}\|]*'
	regex[4] = ur'({{[Cc]ours[^}]*)\| *clé *=[^}\|]*'
	regex[5] = ur'({{[Dd]épartement[^}]*)\| *clé *=[^}\|]*'
	regex[6] = ur'({{[Ff]aculté[^}]*)\| *clé *=[^}\|]*'
	
	for p in range(1,sizeR-1):
		if re.search(regex[p], PageTemp):
			PageTemp = re.sub(regex[p], ur'\1', PageTemp)
			if summary.find(u'clé de tri') == -1: summary = summary + u', retrait de la clé de tri'

	# Remplacements consensuels
	#if page.namespace() != 0 and page.namespace() != 106 and page.namespace() != 108 and page.title() != u'Utilisateur:JackBot/test' and page.title() != u'Utilisateur:JackBot/test/test2': 
	#	return
	
	for p in range(1,sizeT-1):
		if PageTemp.find(u'{{' + temp[p] + u'|') != -1 or PageTemp.find(u'{{' + temp[p] + u'}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(temp[p])] + Ttemp[p] + PageTemp[PageTemp.find(temp[p])+len(temp[p]):len(PageTemp)]
		#p=p+1
		
	# http://fr.wikiversity.org/wiki/Catégorie:Modèle_mal_utilisé
	if CorrigerModeles == True:
		if PageTemp.find('{Chapitre') != -1 or PageTemp.find('{chapitre') != -1:
			''' Bug du modèle tronqué :
			if re.compile('{Chapitre').search(PageTemp):
				if re.compile('{Chapitre[.\n]*(\n.*align.*=.*\n)').search(PageTemp):
					i1 = re.search(u'{{Chapitre[.\n]*(\n.*align.*=.*\n)',PageTemp).end()
					i2 = re.search(u'(\n.*align.*=.*\n)',PageTemp[:i1]).start()
					PageTemp = PageTemp[:i2] + u'\n' + PageTemp[i1:]
				PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
				PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
			elif re.compile('{chapitre').search(PageTemp):
				if re.compile('{chapitre[.\n]*(\n.*align.*=.*\n)').search(PageTemp):
					i1 = re.search(u'{{chapitre[.\n]*(\n.*align.*=.*\n)',PageTemp).end()
					i2 = re.search(u'(\n.*align.*=.*\n)',PageTemp[:i1]).start()
					PageTemp = PageTemp[:i2] + u'\n' + PageTemp[i1:]
				PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
				PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
				
				if re.compile('{{Chapitre[\n.]*(\n.*leçon.*=.*\n)').search(PageTemp):
					print "leçon1"
				if re.compile('{{Chapitre.*\n.*\n.*(\n.*leçon.*=.*\n)').search(PageTemp):
					print "leçon2"
				if re.compile('{{Chapitre.*\n.*\n.*\n.*(\n.*leçon.*=.*\n)').search(PageTemp):
					print "leçon3"
				if re.compile('{{Chapitre[.\n]*(\n.*niveau.*=.*\n)').search(PageTemp):
					print "niveau"
					print re.compile('{{Chapitre[.\n]*(\n.*niveau.*=.*\n)').search(PageTemp)
				if re.compile('{{Chapitre[.\n]*(\n.*précédent.*=.*\n)').search(PageTemp):
					print "précédent"
				if re.compile('{{Chapitre[.\n]*(\n.*suivant.*=.*\n)').search(PageTemp):
					print "suivant"
			else: # Pas de modèle chapitre
				print u'Pas de chapitre dans :'
				print (PageHS.encode(config.console_encoding, 'replace'))
				return
			raw_input (PageTemp.encode(config.console_encoding, 'replace'))'''

			Lecon = u''
			# Majuscule
			if PageTemp.find(u'Leçon') != -1 and PageTemp.find(u'Leçon') < 100:
				PageTemp2 = PageTemp[PageTemp.find(u'Leçon'):len(PageTemp)]
				Lecon = Valeur(u'Leçon',PageTemp)
			# Minuscule
			elif PageTemp.find(u'leçon') != -1 and PageTemp.find(u'leçon') < 100:
				PageTemp2 = PageTemp[PageTemp.find(u'leçon'):len(PageTemp)]
				Lecon = Valeur(u'leçon',PageTemp)
			#raw_input (Lecon.encode(config.console_encoding, 'replace'))
			
			if Lecon.find(u'|') != -1:
				Lecon = Lecon[0:Lecon.find(u'|')]
			while Lecon[0:1] == u'[':
				Lecon = Lecon[1:len(Lecon)]
			while Lecon[len(Lecon)-1:len(Lecon)] == u']':
				Lecon = Lecon[0:len(Lecon)-1]
			if (Lecon == u'../' or Lecon == u'') and PageHS.find(u'/') != -1:
				Lecon = PageHS[0:PageHS.rfind(u'/')]
			#raw_input (Lecon.encode(config.console_encoding, 'replace'))
			
			if Lecon != u'' and Lecon.find(u'.') == -1: 
				page2 = Page(site,Lecon)
				if page2.exists():
					if page2.namespace() != 0 and page2.title() != u'Utilisateur:JackBot/test': 
						return
					else:
						try:
							PageLecon = page2.get()
						except wikipedia.NoPage:
							print "NoPage"
							return
						except wikipedia.IsRedirectPage:
							PageLecon = page2.getRedirectTarget().get()
						except wikipedia.LockedPage:
							print "Locked/protected page"
							return
					#raw_input (PageLecon.encode(config.console_encoding, 'replace'))
					
					# Majuscule
					if PageLecon.find(u'{{Leçon') != -1:
						if Valeur(u'Leçon',PageTemp) == u'':
							if PageTemp.find(u'Leçon') < PageTemp.find(u'}}') or PageTemp.find(u'Leçon') < PageTemp.find(u'}}'):
								if Valeur(u'Leçon',PageTemp) == u'':
									PageTemp2 = PageTemp[PageTemp.find(u'Leçon')+len(u'Leçon'):len(PageTemp)]
									PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
									while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u' ' or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'\t':
										PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
									if PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'=':
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'Leçon')+len(u'Leçon')+PageTemp2.find(u'=')+1] + page2.title()
										PageTemp = PageTemp[PageTemp.find(u'Leçon')+len(u'Leçon')+PageTemp2.find(u'=')+1:len(PageTemp)]
									else:
										print u'Signe égal manquant dans :'
										print PageTemp2[len(PageTemp2)-1:len(PageTemp2)]
							else:
								PageEnd = PageEnd + u'\n|Leçon=' + page2.title()
						PageEnd = PageEnd + PageTemp
						if PageLecon.find(u'niveau') != -1:
							PageTemp = PageLecon[PageLecon.find(u'niveau'):len(PageLecon)]
							if PageTemp.find(u'=') < PageTemp.find(u'\n') and PageTemp.find(u'=') != -1:
								if Valeur(u'niveau',PageLecon) != -1:
									PageTemp = PageEnd
									if PageTemp.find(u'{{Chapitre') != -1:
										PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
										PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
									elif PageTemp.find(u'{{chapitre') != -1:
										PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
										PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
									else: return
									if PageTemp.find(u'niveau') < PageTemp.find(u'}}') and PageTemp.find(u'niveau') != -1:
										PageTemp2 = PageTemp[PageTemp.find(u'niveau')+len(u'niveau'):len(PageTemp)]
										while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
											PageTemp2 = PageTemp2[1:len(PageTemp2)]
										if PageTemp2[0:PageTemp2.find(u'\n')] == u'':
											PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'niveau')+len(u'niveau')] + "=" + Valeur(u'niveau',PageLecon)
											PageTemp = PageTemp2
										elif Valeur(u'niveau',PageLecon) != PageTemp2[0:PageTemp2.find(u'\n')]:
											if debogage == True: 
												print u'Différence de niveau dans ' + PageHS.encode(config.console_encoding, 'replace') + u' : '
												print Valeur(u'niveau',PageLecon)
												print PageTemp2[0:PageTemp2.find(u'\n')].encode(config.console_encoding, 'replace')
									else:
										PageEnd = PageEnd + u'\n  | niveau      = ' + Valeur(u'niveau',PageLecon)
									#print (PageEnd.encode(config.console_encoding, 'replace'))
									#raw_input (PageTemp.encode(config.console_encoding, 'replace'))
					# Minuscule
					elif PageLecon.find(u'{{leçon') != -1:
						if Valeur(u'leçon',PageTemp) == u'':
							if PageTemp.find(u'leçon') < PageTemp.find(u'}}') or PageTemp.find(u'leçon') < PageTemp.find(u'}}'):
								if Valeur(u'leçon',PageTemp) == u'':
									PageTemp2 = PageTemp[PageTemp.find(u'leçon')+len(u'leçon'):len(PageTemp)]
									PageTemp2 = PageTemp2[0:PageTemp2.find(u'\n')]
									while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u' ' or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'\t':
										PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
									if PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'=':
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'leçon')+len(u'leçon')+PageTemp2.find(u'=')+1] + page2.title()
										PageTemp = PageTemp[PageTemp.find(u'leçon')+len(u'leçon')+PageTemp2.find(u'=')+1:len(PageTemp)]
									else:
										print u'Signe égal manquant dans :'
										print PageTemp2[len(PageTemp2)-1:len(PageTemp2)]
							else:
								PageEnd = PageEnd + u'\n|leçon=' + page2.title()
						PageEnd = PageEnd + PageTemp
						PageTemp = u''
						if PageLecon.find(u'niveau') != -1:
							niveauLecon = Valeur(u'niveau',PageLecon)
							print niveauLecon
							PageTemp = PageLecon[PageLecon.find(u'niveau'):len(PageLecon)]
							if PageTemp.find(u'=') < PageTemp.find(u'\n') and PageTemp.find(u'=') != -1:
								if niveauLecon != -1:
									PageTemp = PageEnd
									if PageTemp.find(u'{{Chapitre') != -1:
										PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
										PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
									elif PageTemp.find(u'{{chapitre') != -1:
										PageEnd = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')]
										PageTemp = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
									else: return
									if PageTemp.find(u'niveau') < PageTemp.find(u'}}') and PageTemp.find(u'niveau') != -1:
										PageTemp2 = PageTemp[PageTemp.find(u'niveau')+len(u'niveau'):len(PageTemp)]
										while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
											PageTemp2 = PageTemp2[1:len(PageTemp2)]
										niveauChapitre = PageTemp2[0:PageTemp2.find(u'\n')]
										if niveauChapitre == u'':
											PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'niveau')+len(u'niveau')] + "=" + niveauLecon
											PageTemp = PageTemp2
										elif niveauChapitre != niveauLecon:
											print u'Niveau du chapitre différent de celui de la leçon dans ' + PageHS.encode(config.console_encoding, 'replace')
									else:
										PageEnd = PageEnd + u'\n|niveau=' + niveauLecon
										
					PageEnd = PageEnd + PageTemp
					PageTemp = u''
					#raw_input (PageEnd.encode(config.console_encoding, 'replace'))
					
					'''print Valeur(u'niveau',PageEnd)
					print u'********************************************'
					print Valeur(u'numéro',PageEnd)
					print u'********************************************'
					print Valeur(u'précédent',PageEnd)
					print u'********************************************'
					print Valeur(u'suivant',PageEnd)
					raw_input(u'Fin de paramètres')'''
					NumLecon = u''
					PageTemp2 = u''
					if Valeur(u'numéro',PageEnd) == u'' or Valeur(u'précédent',PageEnd) == u'' or Valeur(u'suivant',PageEnd) == u'':
						if PageLecon.find(PageHS) != -1:
							PageTemp2 = PageLecon[0:PageLecon.find(PageHS)]	# Nécessite que le département ait un nom déifférent et que les leçons soient bien nommées différemment
						elif PageLecon.find(PageHS[PageHS.rfind(u'/')+1:len(PageHS)]) != -1:
							PageTemp2 = PageLecon[0:PageLecon.find(PageHS[PageHS.rfind(u'/')+1:len(PageHS)])]
						if PageTemp2 != u'':
							while PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == " " or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "=" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "[" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "{" or PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == "|" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{C" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{c" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{L" or PageTemp2[len(PageTemp2)-2:len(PageTemp2)] == "{l":
								PageTemp2 = PageTemp2[0:len(PageTemp2)-1]
							if PageTemp2.rfind(u' ') > PageTemp2.rfind(u'|'):
								NumLecon = PageTemp2[PageTemp2.rfind(u' ')+1:len(PageTemp2)]
							else:
								NumLecon = PageTemp2[PageTemp2.rfind(u'|')+1:len(PageTemp2)]
							#print (PageTemp2.encode(config.console_encoding, 'replace'))				
							if NumLecon != u'' and NumLecon != u'département':
								# Le numéro de la leçon permet de remplir les champs : |numéro=, |précédent=, |suivant=
								if Valeur(u'numéro',PageEnd) == u'':
									if PageEnd.find(u'numéro') == -1:
										PageTemp = PageEnd
										PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
										PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
										if PageTemp.find(u'numéro') < PageTemp.find(u'}}') and PageTemp.find(u'numéro') != -1:
											PageTemp2 = PageTemp[PageTemp.find(u'numéro')+len(u'numéro'):len(PageTemp)]
											while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
												PageTemp2 = PageTemp2[1:len(PageTemp2)]
											PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'numéro')+len(u'numéro')] + "=" + NumLecon
											PageTemp = PageTemp2
										else:
											PageEnd = PageEnd + u'\n|numéro=' + NumLecon
										PageEnd = PageEnd + PageTemp
										PageTemp = u''
								if Valeur(u'précédent',PageEnd) == u'' and NumLecon	== 1:
									PageTemp = PageEnd
									PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
									PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
									if PageTemp.find(u'précédent') < PageTemp.find(u'}}') and PageTemp.find(u'précédent') != -1:
										PageTemp2 = PageTemp[PageTemp.find(u'précédent')+len(u'précédent'):len(PageTemp)]
										while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
											PageTemp2 = PageTemp2[1:len(PageTemp2)]
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+len(u'précédent')] + "=" + NumLecon
										PageTemp = PageTemp2
									else:
										PageEnd = PageEnd + u'\n|précédent=' + NumLecon
									PageEnd = PageEnd + PageTemp
									PageTemp = u''								
								elif Valeur(u'précédent',PageEnd) == u'' and Valeur(str(int(NumLecon)-1),PageLecon) != u'':
									PageTemp = PageEnd
									PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
									PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
									if PageTemp.find(u'précédent') < PageTemp.find(u'}}') and PageTemp.find(u'précédent') != -1:
										PageTemp2 = PageTemp[PageTemp.find(u'précédent')+len(u'précédent'):len(PageTemp)]
										while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
											PageTemp2 = PageTemp2[1:len(PageTemp2)]
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+len(u'précédent')] + "=" + Valeur(str(int(NumLecon)-1),PageLecon)
										PageTemp = PageTemp2
									else:
										PageEnd = PageEnd + u'\n|précédent=' + Valeur(str(int(NumLecon)-1),PageLecon)
									PageEnd = PageEnd + PageTemp
									PageTemp = u''
								if Valeur(u'suivant',PageEnd) == u'' and Valeur(str(int(NumLecon)+1),PageLecon) != u'':					
									PageTemp = PageEnd
									PageEnd = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')]
									PageTemp = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
									if PageTemp.find(u'suivant') < PageTemp.find(u'}}') and PageTemp.find(u'suivant') != -1:
										PageTemp2 = PageTemp[PageTemp.find(u'suivant')+len(u'suivant'):len(PageTemp)]
										while PageTemp2[0:1] == " " or PageTemp2[0:1] == "=":
											PageTemp2 = PageTemp2[1:len(PageTemp2)]
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'suivant')+len(u'suivant')] + "=" + Valeur(str(int(NumLecon)+1),PageLecon)
										PageTemp = PageTemp2
									else:
										if PageTemp.find(u'précédent') != -1:
											PageTemp2 = PageTemp[PageTemp.find(u'précédent'):len(PageTemp)]
											PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'précédent')+PageTemp2.find(u'\n')] + u'\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
											PageTemp = PageTemp[PageTemp.find(u'précédent')+PageTemp2.find(u'\n'):len(PageTemp)]
										else:
											PageEnd = PageEnd + u'\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
									PageEnd = PageEnd + PageTemp
									PageTemp = u''
				else: # Pas de leçon
					print u'Pas de leçon : '
					print (Lecon.encode(config.console_encoding, 'replace'))
					print u'dans : '
					print (PageHS.encode(config.console_encoding, 'replace'))
					#raw_input ('Attente')
				PageEnd = PageEnd + PageTemp
				PageTemp = u''
		elif PageTemp.find(u'{Leçon') != -1 or PageTemp.find(u'{leçon') != -1:
			# Evaluations
			page2 = Page(site,u'Discussion:' + PageHS)
			if page2.exists():
				try:
					PageDisc = page2.get()
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
				PageDisc = u''
			if PageDisc.find(u'{{Évaluation') == -1 and PageDisc.find(u'{{évaluation') == -1: sauvegarde(page2, u'{{Évaluation|idfaculté=' + Valeur(u'idfaculté',PageTemp) + u'|avancement=?}}\n' + PageDisc, u'Ajout d\'évaluation inconnue')	
							
			# Synchronisations avec les niveaux des départements, et les évaluations des onglets Discussion:
			#...
		PageEnd = PageEnd + PageTemp
		
		# Bas de page
		if (PageEnd.find(u'{{Chapitre') != -1 or PageEnd.find(u'{{chapitre') != -1) and PageEnd.find(u'{{Bas de page') == -1 and PageEnd.find(u'{{bas de page') == -1:
			idfaculte = u''
			precedent = u''
			suivant = u''
			if PageEnd.find(u'idfaculté') != -1:
				PageTemp = PageEnd[PageEnd.find(u'idfaculté'):len(PageEnd)]
				idfaculte = PageTemp[0:PageTemp.find(u'\n')]	# pb si tout sur la même ligne, faire max(0,min(PageTemp.find(u'\n'),?))
				if PageEnd.find(u'précédent') != -1:
					PageTemp = PageEnd[PageEnd.find(u'précédent'):len(PageEnd)]
					precedent = PageTemp[0:PageTemp.find(u'\n')]
				if PageEnd.find(u'suivant') != -1:
					PageTemp = PageEnd[PageEnd.find(u'suivant'):len(PageEnd)]
					suivant = PageTemp[0:PageTemp.find(u'\n')]
				PageEnd = PageEnd + u'\n\n{{Bas de page|' + idfaculte + u'\n|' + precedent + u'\n|' + suivant + u'}}'
		
		# Exercices (pb http://fr.wikiversity.org/w/index.php?title=Allemand%2FVocabulaire%2FFormes_et_couleurs&diff=354352&oldid=354343)
		'''PageTemp = PageEnd
		PageEnd = u''
		while PageEnd.find(u'{{CfExo') != -1 or PageEnd.find(u'{{cfExo') != -1:
			PageTemp = PageEnd[
			if 
			|exercice=[[
			/Exercices/
			/quiz/
		PageEnd = PageEnd + PageTemp'''
	
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

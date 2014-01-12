#!/usr/bin/env python
# coding: utf-8
# Ce script formate les pages de la Wikiversité :
# 1) Il ajoute les clés de tri pour palier au classement des catégories Mediawiki.
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
summary = u'[[Aide:Syntaxe|Autoformatage]]'
debogage = False
sizeT = 3
sizeP = 12

temp = range(1, sizeT)
Ttemp = range(1, sizeT)
temp[1] = u'numero'
Ttemp[1] = u'numéro'

# Modèle:Chapitre
param = range(1, sizeP)
param[1] = u'titre '
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
	PageEnd = "" # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première
	page = Page(site,PageHS)
	print(PageHS.encode(config.console_encoding, 'replace'))
	if page.exists():
		if page.namespace() != 0 and page.namespace() != 106 and page.namespace() != 108 and page.title() != u'Utilisateur:JackBot/test' and page.title() != u'Utilisateur:JackBot/test/test2': 
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
	else:
		print u'Page inexistante'
		return
	
	PageTemp = PageBegin
	# Clés de tri
	if PageTemp.find(u'{{clé de tri') == -1 and (PageTemp.find(u'clé') == -1 or PageTemp.find(u'clé') > PageTemp.find(u'}}')):
		PageTitre = page.title()
		if page.namespace() == 0 or page.title() != u'Utilisateur:JackBot/test' or page.title() != u'Utilisateur:JackBot/test/test2':
			if PageTitre.find(u'/') != -1:
				PageTitre = PageTitre[PageTitre.rfind(u'/')+1:len(PageTitre)]
			'''if PageTitre[len(PageTitre)-len(u'/Présentation de la leçon'):len(PageTitre)] == u'/Présentation de la leçon':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Présentation de la leçon')]
			elif PageTitre[len(PageTitre)-len(u'/Objectifs'):len(PageTitre)] == u'/Objectifs':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Objectifs')]
			elif PageTitre[len(PageTitre)-len(u'/Prérequis conseillés'):len(PageTitre)] == u'/Prérequis conseillés':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Prérequis conseillés')]
			elif PageTitre[len(PageTitre)-len(u'/Référents'):len(PageTitre)] == u'/Référents':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Référents')]'''		
		elif page.namespace() == 106 or page.title() != u'Utilisateur:JackBot/test' or page.title() != u'Utilisateur:JackBot/test/test2':
			PageTitre = PageTitre[len(u'Faculté:'):len(PageTitre)]
			if PageTitre[len(PageTitre)-len(u'/Présentation de la faculté'):len(PageTitre)] == u'/Présentation de la faculté':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Présentation de la faculté')]
			elif PageTitre[len(PageTitre)-len(u'/Départements'):len(PageTitre)] == u'/Départements':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Départements')]
			elif PageTitre[len(PageTitre)-len(u'/Transverse'):len(PageTitre)] == u'/Transverse':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Transverse')]
			elif PageTitre[len(PageTitre)-len(u'/Voir aussi'):len(PageTitre)] == u'/Voir aussi':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Voir aussi')]		   
		elif page.namespace() == 108 or page.title() != u'Utilisateur:JackBot/test' or page.title() != u'Utilisateur:JackBot/test/test2':
			PageTitre = PageTitre[len(u'Département:'):len(PageTitre)]
			if PageTitre[len(PageTitre)-len(u'/Présentation du département'):len(PageTitre)] == u'/Présentation du département':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Présentation du département')]
			elif PageTitre[len(PageTitre)-len(u'/Leçons par thèmes'):len(PageTitre)] == u'/Leçons par thèmes':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Leçons par thèmes')]
			elif PageTitre[len(PageTitre)-len(u'/Leçons par niveaux'):len(PageTitre)] == u'/Leçons par niveaux':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Leçons par niveaux')]
			elif PageTitre[len(PageTitre)-len(u'/Contributeurs'):len(PageTitre)] == u'/Contributeurs':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Contributeurs')]
			elif PageTitre[len(PageTitre)-len(u'/Voir aussi'):len(PageTitre)] == u'/Voir aussi':
				PageTitre = PageTitre[0:len(PageTitre)-len(u'/Voir aussi')]
		PageT = ""
		key = "false"
		for lettre in range(0,len(PageTitre)):
			# Latin
			if PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä' or PageTitre[lettre:lettre+1] == u'Á' or PageTitre[lettre:lettre+1] == u'À' or PageTitre[lettre:lettre+1] == u'Â' or PageTitre[lettre:lettre+1] == u'Ä':
				PageT = PageT + "a"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'ë' or PageTitre[lettre:lettre+1] == u'É' or PageTitre[lettre:lettre+1] == u'È' or PageTitre[lettre:lettre+1] == u'Ê' or PageTitre[lettre:lettre+1] == u'Ë' or PageTitre[lettre:lettre+1] == u'ě' or PageTitre[lettre:lettre+1] == u'Ě':
				PageT = PageT + "e"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'í' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ï' or PageTitre[lettre:lettre+1] == u'Í' or PageTitre[lettre:lettre+1] == u'Ì' or PageTitre[lettre:lettre+1] == u'Î' or PageTitre[lettre:lettre+1] == u'Ï':
				PageT = PageT + "i"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ó'  or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'ö' or PageTitre[lettre:lettre+1] == u'Ó'  or PageTitre[lettre:lettre+1] == u'Ò' or PageTitre[lettre:lettre+1] == u'Ô' or PageTitre[lettre:lettre+1] == u'Ö':
				PageT = PageT + "o"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'ù' or PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ü' or PageTitre[lettre:lettre+1] == u'Ú' or PageTitre[lettre:lettre+1] == u'Ù' or PageTitre[lettre:lettre+1] == u'Û' or PageTitre[lettre:lettre+1] == u'Ü':
				PageT = PageT + "u"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ç' or PageTitre[lettre:lettre+1] == u'Ç':
				PageT = PageT + "c"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'š' or PageTitre[lettre:lettre+1] == u'Š':
				PageT = PageT + "c"
				key = "yes"		
			elif PageTitre[lettre:lettre+1] == u'æ' or PageTitre[lettre:lettre+1] == u'Æ':
				PageT = PageT + "ae"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'œ' or PageTitre[lettre:lettre+1] == u'Œ':
				PageT = PageT + "oe"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ñ' or PageTitre[lettre:lettre+1] == u'Ñ':
				PageT = PageT + "n"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'ÿ' or PageTitre[lettre:lettre+1] == u'Ÿ':
				PageT = PageT + "y"
				key = "yes"
			elif PageTitre[lettre:lettre+1] == u'-':
				PageT = PageT + " "
				key = "yes"'''
			elif PageTitre[lettre:lettre+1] == u'/':
				PageT = PageT + " "
				key = "yes"'''
			elif PageTitre[lettre:lettre+1] == u'\\':
				PageT = PageT + ""
				key = "yes"
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
				PageT = PageT + "е"
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
				key = "yes"
			else:
				PageT = PageT + PageTitre[lettre:lettre+1].lower()
			#print (PageT.encode(config.console_encoding, 'replace'))
			#raw_input("lettre")
		if key == "yes":
			if PageTemp.find(u'{{chapitre') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')] + u'\n|clé=' + PageT + PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
			if PageTemp.find(u'{{Chapitre') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')] + u'\n|clé=' + PageT + PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
			elif PageTemp.find(u'[[Catégorie:') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'[[Catégorie:')] + u'\n{{clé de tri|' + PageT + u'}}\n' + PageTemp[PageTemp.find(u'[[Catégorie:'):len(PageTemp)]
			elif PageTemp.find(u'[[Category:') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'[[Category:')] + u'\n{{clé de tri|' + PageT + u'}}\n' + PageTemp[PageTemp.find(u'[[Category:'):len(PageTemp)]
			else:
				PageTemp = PageTemp + u'\n\n{{clé de tri|' + PageT + u'}}\n'
	#raw_input (PageTemp.encode(config.console_encoding, 'replace'))
	
	# Remplacements consensuels
	for p in range(1,sizeT-1):
		if PageTemp.find(u'{{' + temp[p] + u'|') != -1 or PageTemp.find(u'{{' + temp[p] + u'}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(temp[p])] + Ttemp[p] + PageTemp[PageTemp.find(temp[p])+len(temp[p]):len(PageTemp)]
		p=p+1
		
	# http://fr.wikiversity.org/wiki/Catégorie:Modèle_mal_utilisé
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
	raw_input(u'Bug http://fr.wikiversity.org/w/index.php?title=Initiation_%C3%A0_l%27arithm%C3%A9tique/PGCD&diff=prev&oldid=386685')
	if re.search(u'\n *' + Mot + u' *=', Page):
		niveau = re.sub(u'\n *' + Mot + u' *=()[\n|\||}|{]', ur'$1', Page)
		raw_input(niveau)
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

def sauvegarde(PageCourante, Contenu, summary):
	ArretDUrgence()
	result = "ok"
	print(Contenu.encode(config.console_encoding, 'replace')[0:4000])	#[len(Contenu)-2000:len(Contenu)]) #
	result = raw_input("Sauvegarder ? (o/n)")
	if result != "n" and result != "no" and result != "non":
		if not summary: summary = u'[[Aide:Syntaxe|Autoformatage]]'
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
			
# Lancement
TraitementPage = modification(u'Initiation_à_l\'arithmétique/PGCD')
'''
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

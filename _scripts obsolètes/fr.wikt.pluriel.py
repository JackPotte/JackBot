#!/usr/bin/env python
# coding: utf-8
# Ce script crée les pluriels en français à partir des singuliers

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wiktionary"
site = getSite(language,family)
template = u'fr-rég'
debogage = True

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() !=0 and page.title() != u'Utilisateur:JackBot/test': return
	else: return
	try: PageSing = page.get()
	except wikipedia.NoPage: return
	except wikipedia.InvalidPage: return
	except wikipedia.ServerError: return
	if PageSing.find(template) == -1: return
	PageTemp = PageSing[0:PageSing.find(template)]
	nature = PageSing[PageTemp.rfind(u'{{-')+3:PageTemp.rfind(u'-|')]
	if nature == u'erreur': return
	PageTemp = PageSing[PageSing.find(template)+len(template):len(PageSing)]
	if PageTemp.find(u'inv=') != -1 and PageTemp.find(u'inv=') < PageTemp.find(u'}}'): return
	if PageTemp.find(u's=') != -1 and (PageTemp.find(u's=') < PageTemp.find(u'}}') or PageTemp.find(u's=') < PageTemp.find(u'\n')): return
	# Prononciation
	if PageTemp.find(u'|pp=') != -1 and PageTemp.find(u'|pp=') < PageTemp.find(u'}}'):
		PageTemp2 = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
		if PageTemp2.find(u'|') != -1:
			pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'|pp=')+4+PageTemp2.find(u'|')]
		else:
			pron = PageTemp[PageTemp.find(u'|pp=')+4:PageTemp.find(u'}}')]
	else:
		pron = PageTemp[0:PageTemp.find(u'}}')]
		while pron.find(u'=') != -1:
			pron2 = pron[0:pron.find(u'=')]
			pron3 = pron[pron.find(u'='):len(pron)]
			if pron2.find(u'|') == -1:
				pron = pron[pron.find(u'|')+1:len(pron)]
			else:
				if pron3.find(u'|') == -1:
					pron = pron[0:pron2.rfind(u'|')]
				else:
					pron = pron[0:pron2.rfind(u'|')]
			if pron3.find(u'|') == -1:
				pron = pron[0:pron2.rfind(u'|')]
			else:
				pron = pron[0:pron2.rfind(u'|')] + pron[pron2.rfind(u'|')+pron3.find(u'|'):len(pron)]
	while pron[0:1] == u' ': pron = pron[1:len(pron)]
	#print (pron.encode(config.console_encoding, 'replace'))
	#raw_input("pron\n")
	# h aspiré
	H = u''
	if PageTemp.find(u'|prefpron={{h aspiré') != -1 and PageTemp.find(u'|prefpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|prefpron={{h aspiré}}'
	if PageTemp.find(u'|préfpron={{h aspiré') != -1 and PageTemp.find(u'|préfpron={{h aspiré') < PageTemp.find(u'}}'): H = u'|préfpron={{h aspiré}}'
	# genre
	genre = u''
	PageTemp2 = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
	while PageTemp2[0:1] == u'[' or PageTemp2[0:1] == u'\n': PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
	if PageTemp2.find(u'{{m}}') != -1 and PageTemp2.find(u'{{m}}') < PageTemp2.find(u'\n'): genre = u' {{m}}'	
	if PageTemp2.find(u'{{f}}') != -1 and PageTemp2.find(u'{{f}}') < PageTemp2.find(u'\n'): genre = u' {{f}}'
	MF = u''
	if PageTemp2.find(u'{{mf}}') != -1 and PageTemp2.find(u'{{mf}}') < PageTemp2.find(u'\n'):
		genre = u' {{mf}}'
		MF = u'|mf=oui'
		if PageSing.find(u'|mf=') == -1:
			PageSing = PageSing[0:PageSing.find(template)+len(template)] + u'|mf=oui' + PageSing[PageSing.find(template)+len(template):len(PageSing)]
			sauvegarde(page, PageSing, u'|mf=oui')
	if PageTemp.find(u'|mf=') != -1 and PageTemp.find(u'|mf=') < PageTemp.find(u'}}'): MF = u'|mf=oui' 
	# Pluriel
	summary = u'Création du pluriel de [[' + PageHS + u']]'
	pluriel = u''
	if (PageTemp.find(u'|p=') != -1 and PageTemp.find(u'|p=') < PageTemp.find(u'}}')):
		pluriel = PageTemp[PageTemp.find(u'|p=')+3:PageTemp.find(u'}}')]
		if pluriel.find(u'|') != -1: pluriel = pluriel[0:pluriel.find(u'|')]
	if not pluriel: pluriel = PageHS + u's'
	if pluriel[-2:] == u'ss' or pluriel.find(u'{') != -1:
		return
	
	page2 = Page(site,pluriel)
	if page2.exists(): 
		return
	else:
		PageEnd = u'== {{langue|fr}} ==\n{{-flex-' + nature + u'-|fr}}\n{{fr-rég' + pron + H + MF + '|s=' + PageHS + u'}}\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pron + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + PageHS +']].\n'
		while PageEnd.find(u'{{pron|fr}}') != -1:
			PageEnd = PageEnd[0:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]
		# Autres paragraphes
		if PageTemp.find(template) != -1:
			PageTemp2 = PageTemp[0:PageTemp.find(template)]
			nature2 = PageTemp[PageTemp2.rfind(u'{{-')+3:PageTemp2.rfind(u'-|')]
			PageTemp2 = PageTemp[PageTemp.find(template)+1:len(PageTemp)]
			PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
			while PageTemp2[0:1] == u'[' or PageTemp2[0:1] == u'\n': PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:len(PageTemp2)]
			genre2 = u''
			if PageTemp2.find(u'{{m}}') != -1 and PageTemp2.find(u'{{m}}') < PageTemp2.find(u'\n'): genre2 = u' {{m}}'	
			if PageTemp2.find(u'{{f}}') != -1 and PageTemp2.find(u'{{f}}') < PageTemp2.find(u'\n'): genre2 = u' {{f}}'
			MF2 = u''
			if PageTemp2.find(u'{{mf}}') != -1 and PageTemp2.find(u'{{mf}}') < PageTemp2.find(u'\n'):
				genre2 = u' {{mf}}'
				MF2 = u'|mf=oui'
				if PageSing.find(u'|mf=') == -1:
					PageSing = PageSing[0:PageSing.find(template)+PageTemp.find(template)+2*len(template)] + u'|mf=oui' + PageSing[PageSing.find(template)+PageTemp.find(template)+2*len(template):len(PageSing)]
					sauvegarde(page, PageSing, u'|mf=oui')
			if PageTemp2.find(u'|mf=') != -1 and PageTemp2.find(u'|mf=') < PageTemp2.find(u'}}'): MF2 = u'|mf=oui'				
			PageEnd = PageEnd + u'\n{{-flex-' + nature2 + u'-|fr}}\n{{fr-rég' + pron + H + MF2 + '|s=' + PageHS + u'}}\n\'\'\'' + pluriel + u'\'\'\' {{pron' + pron + '|fr}}' + genre2 + u'\n# \'\'Pluriel de\'\' [[' + PageHS +']].\n'
			while PageEnd.find(u'{{pron|fr}}') != -1:
				PageEnd = PageEnd[0:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]		
		# cas des locutions
		if pluriel.find(u' ') != -1: PageEnd = PageEnd[0:PageEnd.find(u'{{fr-rég')+len(u'{{fr-rég')] + u'|p=' + pluriel + PageEnd[PageEnd.find(u'{{fr-rég')+len(u'{{fr-rég'):len(PageEnd)]
		# Clés de tri
		if PageEnd.find(u'{{clé de tri') == -1:
			PageTitre = page2.title()
			PageT = ""
			key = "false"
			key2 = "false"
			for lettre in range(0,len(PageTitre)):
				# Latin
				if PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä':
					PageT = PageT + "a"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'ë':
					PageT = PageT + "e"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'í' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ï':
					PageT = PageT + "i"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ó'  or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'ö':
					PageT = PageT + "o"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'ù' or PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ü':
					PageT = PageT + "u"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ç':
					PageT = PageT + "c"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'æ':
					PageT = PageT + "ae"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'œ':
					PageT = PageT + "oe"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ñ':
					PageT = PageT + "n"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ÿ':
					PageT = PageT + "y"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'-':
					PageT = PageT + " "
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'/':
					PageT = PageT + " "
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'\\':
					PageT = PageT + ""
					key = "yes"
				# Grec
				elif PageTitre[lettre:lettre+1] == u'Α' or PageTitre[lettre:lettre+1] == u'Ἀ' or PageTitre[lettre:lettre+1] == u'ἀ' or PageTitre[lettre:lettre+1] == u'Ἁ' or PageTitre[lettre:lettre+1] == u'ἁ' or PageTitre[lettre:lettre+1] == u'Ἂ' or PageTitre[lettre:lettre+1] == u'ἂ' or PageTitre[lettre:lettre+1] == u'Ἃ' or PageTitre[lettre:lettre+1] == u'ἃ' or PageTitre[lettre:lettre+1] == u'Ἄ' or PageTitre[lettre:lettre+1] == u'ἄ' or PageTitre[lettre:lettre+1] == u'Ἅ' or PageTitre[lettre:lettre+1] == u'ἅ' or PageTitre[lettre:lettre+1] == u'Ἆ' or PageTitre[lettre:lettre+1] == u'ἆ' or PageTitre[lettre:lettre+1] == u'Ἇ' or PageTitre[lettre:lettre+1] == u'ἇ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ὰ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ά' or PageTitre[lettre:lettre+1] == u'ᾈ' or PageTitre[lettre:lettre+1] == u'ᾀ' or PageTitre[lettre:lettre+1] == u'ᾉ' or PageTitre[lettre:lettre+1] == u'ᾁ' or PageTitre[lettre:lettre+1] == u'ᾊ' or PageTitre[lettre:lettre+1] == u'ᾂ' or PageTitre[lettre:lettre+1] == u'ᾋ' or PageTitre[lettre:lettre+1] == u'ᾃ' or PageTitre[lettre:lettre+1] == u'ᾌ' or PageTitre[lettre:lettre+1] == u'ᾄ' or PageTitre[lettre:lettre+1] == u'ᾍ' or PageTitre[lettre:lettre+1] == u'ᾅ' or PageTitre[lettre:lettre+1] == u'ᾎ' or PageTitre[lettre:lettre+1] == u'ᾆ' or PageTitre[lettre:lettre+1] == u'ᾏ' or PageTitre[lettre:lettre+1] == u'ᾇ' or PageTitre[lettre:lettre+1] == u'Ᾰ' or PageTitre[lettre:lettre+1] == u'ᾰ' or PageTitre[lettre:lettre+1] == u'Ᾱ' or PageTitre[lettre:lettre+1] == u'ᾱ' or PageTitre[lettre:lettre+1] == u'ᾼ' or PageTitre[lettre:lettre+1] == u'ᾳ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ᾲ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ᾴ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾶ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾷ':
					PageT = PageT + "α"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ε' or PageTitre[lettre:lettre+1] == u'Ἐ' or PageTitre[lettre:lettre+1] == u'ἐ' or PageTitre[lettre:lettre+1] == u'Ἑ' or PageTitre[lettre:lettre+1] == u'ἑ' or PageTitre[lettre:lettre+1] == u'Ἒ' or PageTitre[lettre:lettre+1] == u'ἒ' or PageTitre[lettre:lettre+1] == u'Ἓ' or PageTitre[lettre:lettre+1] == u'ἓ' or PageTitre[lettre:lettre+1] == u'Ἔ' or PageTitre[lettre:lettre+1] == u'ἔ' or PageTitre[lettre:lettre+1] == u'Ἕ' or PageTitre[lettre:lettre+1] == u'ἕ' or PageTitre[lettre:lettre+1] == u'Ὲ' or PageTitre[lettre:lettre+1] == u'ὲ' or PageTitre[lettre:lettre+1] == u'Έ' or PageTitre[lettre:lettre+1] == u'έ':
					PageT = PageT + "ε"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Η' or PageTitre[lettre:lettre+1] == u'Ἠ' or PageTitre[lettre:lettre+1] == u'ἠ' or PageTitre[lettre:lettre+1] == u'Ἡ' or PageTitre[lettre:lettre+1] == u'ἡ' or PageTitre[lettre:lettre+1] == u'Ἢ' or PageTitre[lettre:lettre+1] == u'ἢ' or PageTitre[lettre:lettre+1] == u'Ἣ' or PageTitre[lettre:lettre+1] == u'ἣ' or PageTitre[lettre:lettre+1] == u'Ἤ' or PageTitre[lettre:lettre+1] == u'ἤ' or PageTitre[lettre:lettre+1] == u'Ἥ' or PageTitre[lettre:lettre+1] == u'ἥ' or PageTitre[lettre:lettre+1] == u'Ἦ' or PageTitre[lettre:lettre+1] == u'ἦ' or PageTitre[lettre:lettre+1] == u'Ἧ' or PageTitre[lettre:lettre+1] == u'ἧ' or PageTitre[lettre:lettre+1] == u'ᾘ' or PageTitre[lettre:lettre+1] == u'ᾐ' or PageTitre[lettre:lettre+1] == u'ᾙ' or PageTitre[lettre:lettre+1] == u'ᾑ' or PageTitre[lettre:lettre+1] == u'ᾚ' or PageTitre[lettre:lettre+1] == u'ᾒ' or PageTitre[lettre:lettre+1] == u'ᾛ' or PageTitre[lettre:lettre+1] == u'ᾓ' or PageTitre[lettre:lettre+1] == u'ᾜ' or PageTitre[lettre:lettre+1] == u'ᾔ' or PageTitre[lettre:lettre+1] == u'ᾝ' or PageTitre[lettre:lettre+1] == u'ᾕ' or PageTitre[lettre:lettre+1] == u'ᾞ' or PageTitre[lettre:lettre+1] == u'ᾖ' or PageTitre[lettre:lettre+1] == u'ᾟ' or PageTitre[lettre:lettre+1] == u'ᾗ' or PageTitre[lettre:lettre+1] == u'Ὴ' or PageTitre[lettre:lettre+1] == u'ὴ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ή' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῂ' or PageTitre[lettre:lettre+1] == u'Η' or PageTitre[lettre:lettre+1] == u'ῃ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ῄ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῆ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῇ':
					PageT = PageT + "η"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ι' or PageTitre[lettre:lettre+1] == u'Ὶ' or PageTitre[lettre:lettre+1] == u'ὶ' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ῐ' or PageTitre[lettre:lettre+1] == u'ῐ' or PageTitre[lettre:lettre+1] == u'Ῑ' or PageTitre[lettre:lettre+1] == u'ῑ' or PageTitre[lettre:lettre+1] == u'Ἰ' or PageTitre[lettre:lettre+1] == u'ἰ' or PageTitre[lettre:lettre+1] == u'Ἱ' or PageTitre[lettre:lettre+1] == u'ἱ' or PageTitre[lettre:lettre+1] == u'Ἲ' or PageTitre[lettre:lettre+1] == u'ἲ' or PageTitre[lettre:lettre+1] == u'Ἳ' or PageTitre[lettre:lettre+1] == u'ἳ' or PageTitre[lettre:lettre+1] == u'Ἴ' or PageTitre[lettre:lettre+1] == u'ἴ' or PageTitre[lettre:lettre+1] == u'Ἵ' or PageTitre[lettre:lettre+1] == u'ἵ' or PageTitre[lettre:lettre+1] == u'Ἶ' or PageTitre[lettre:lettre+1] == u'ἶ' or PageTitre[lettre:lettre+1] == u'Ἷ' or PageTitre[lettre:lettre+1] == u'ἷ' or PageTitre[lettre:lettre+1] == u'ΐ' or PageTitre[lettre:lettre+1] == u'ῖ' or PageTitre[lettre:lettre+1] == u'ῗ' or PageTitre[lettre:lettre+1] == u'ῒ':
					PageT = PageT + "ι" 
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ο' or PageTitre[lettre:lettre+1] == u'Ὀ' or PageTitre[lettre:lettre+1] == u'ὀ' or PageTitre[lettre:lettre+1] == u'Ὁ' or PageTitre[lettre:lettre+1] == u'ὁ' or PageTitre[lettre:lettre+1] == u'Ὂ' or PageTitre[lettre:lettre+1] == u'ὂ' or PageTitre[lettre:lettre+1] == u'Ὃ' or PageTitre[lettre:lettre+1] == u'ὃ' or PageTitre[lettre:lettre+1] == u'Ὄ' or PageTitre[lettre:lettre+1] == u'ὄ' or PageTitre[lettre:lettre+1] == u'Ὅ' or PageTitre[lettre:lettre+1] == u'ὅ' or PageTitre[lettre:lettre+1] == u'Ὸ' or PageTitre[lettre:lettre+1] == u'ὸ' or PageTitre[lettre:lettre+1] == u'Ό' or PageTitre[lettre:lettre+1] == u'ό':
					PageT = PageT + "ο"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ω' or PageTitre[lettre:lettre+1] == u'Ὠ' or PageTitre[lettre:lettre+1] == u'ὠ' or PageTitre[lettre:lettre+1] == u'Ὡ' or PageTitre[lettre:lettre+1] == u'ὡ' or PageTitre[lettre:lettre+1] == u'Ὢ' or PageTitre[lettre:lettre+1] == u'ὢ' or PageTitre[lettre:lettre+1] == u'Ὣ' or PageTitre[lettre:lettre+1] == u'ὣ' or PageTitre[lettre:lettre+1] == u'Ὤ' or PageTitre[lettre:lettre+1] == u'ὤ' or PageTitre[lettre:lettre+1] == u'Ὥ' or PageTitre[lettre:lettre+1] == u'ὥ' or PageTitre[lettre:lettre+1] == u'Ὦ' or PageTitre[lettre:lettre+1] == u'ὦ' or PageTitre[lettre:lettre+1] == u'Ὧ' or PageTitre[lettre:lettre+1] == u'ὧ' or PageTitre[lettre:lettre+1] == u'Ὼ' or PageTitre[lettre:lettre+1] == u'ὼ' or PageTitre[lettre:lettre+1] == u'Ώ' or PageTitre[lettre:lettre+1] == u'ώ' or PageTitre[lettre:lettre+1] == u'ᾨ' or PageTitre[lettre:lettre+1] == u'ᾠ' or PageTitre[lettre:lettre+1] == u'ᾩ' or PageTitre[lettre:lettre+1] == u'ᾡ' or PageTitre[lettre:lettre+1] == u'ᾪ' or PageTitre[lettre:lettre+1] == u'ᾢ' or PageTitre[lettre:lettre+1] == u'ᾫ' or PageTitre[lettre:lettre+1] == u'ᾣ' or PageTitre[lettre:lettre+1] == u'ᾬ' or PageTitre[lettre:lettre+1] == u'ᾤ' or PageTitre[lettre:lettre+1] == u'ᾭ' or PageTitre[lettre:lettre+1] == u'ᾥ' or PageTitre[lettre:lettre+1] == u'ᾮ' or PageTitre[lettre:lettre+1] == u'ᾦ' or PageTitre[lettre:lettre+1] == u'ᾯ' or PageTitre[lettre:lettre+1] == u'ᾧ' or PageTitre[lettre:lettre+1] == u'ῼ' or PageTitre[lettre:lettre+1] == u'ῳ' or PageTitre[lettre:lettre+1] == u'ῲ' or PageTitre[lettre:lettre+1] == u'ῴ' or PageTitre[lettre:lettre+1] == u'ῶ' or PageTitre[lettre:lettre+1] == u'ῷ':
					PageT = PageT + "ω"
					key = "yes"
				# Cyrillique
				elif PageTitre[lettre:lettre+1] == u'Е' or PageTitre[lettre:lettre+1] == u'ѐ' or PageTitre[lettre:lettre+1] == u'Ѐ' or PageTitre[lettre:lettre+1] == u'ё' or PageTitre[lettre:lettre+1] == u'Ё':
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
				elif PageTitre[lettre:lettre+1].lower() == PageTitre[lettre:lettre+1]:
					PageT = PageT + PageTitre[lettre:lettre+1]
				else:
					PageT = PageT + PageTitre[lettre:lettre+1].lower()
					key2 = "yes"
			if key == "yes":
				PageEnd = PageEnd + u'\n{{clé de tri|' + PageT + u'}}\n'
		while PageTemp.find(u'&#32;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#32;')] + u' ' + PageTemp[PageTemp.find(u'&#32;')+len(u'&#32;'):len(PageTemp)]
		while PageTemp.find(u'&#224;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#224;')] + u'à' + PageTemp[PageTemp.find(u'&#224;')+len(u'&#224;'):len(PageTemp)]
		while PageTemp.find(u'&#226;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#226;')] + u'â' + PageTemp[PageTemp.find(u'&#226;')+len(u'&#226;'):len(PageTemp)]
		while PageTemp.find(u'&#228;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#228;')] + u'ä' + PageTemp[PageTemp.find(u'&#228;')+len(u'&#228;'):len(PageTemp)]
		while PageTemp.find(u'&#233;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#233;')] + u'é' + PageTemp[PageTemp.find(u'&#233;')+len(u'&#233;'):len(PageTemp)]
		while PageTemp.find(u'&#232;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#232;')] + u'è' + PageTemp[PageTemp.find(u'&#232;')+len(u'&#232;'):len(PageTemp)]
		while PageTemp.find(u'&#234;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#234;')] + u'ê' + PageTemp[PageTemp.find(u'&#234;')+len(u'&#234;'):len(PageTemp)]
		while PageTemp.find(u'&#235;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#235;')] + u'ë' + PageTemp[PageTemp.find(u'&#235;')+len(u'&#235;'):len(PageTemp)]
		while PageTemp.find(u'&#238;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#238;')] + u'î' + PageTemp[PageTemp.find(u'&#238;')+len(u'&#238;'):len(PageTemp)]
		while PageTemp.find(u'&#239;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#239;')] + u'ï' + PageTemp[PageTemp.find(u'&#239;')+len(u'&#239;'):len(PageTemp)]
		while PageTemp.find(u'&#244;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#244;')] + u'ô' + PageTemp[PageTemp.find(u'&#244;')+len(u'&#244;'):len(PageTemp)]
		while PageTemp.find(u'&#246;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#246;')] + u'ö' + PageTemp[PageTemp.find(u'&#246;')+len(u'&#246;'):len(PageTemp)]
		while PageTemp.find(u'&#249;') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#249;')] + u'ù' + PageTemp[PageTemp.find(u'&#249;')+len(u'&#249;'):len(PageTemp)]
		while PageTemp.find(u'&#251;') != -1: 
			PageTemp = PageTemp[0:PageTemp.find(u'&#251;')] + u'û' + PageTemp[PageTemp.find(u'&#251;')+len(u'&#251;'):len(PageTemp)]
		while PageTemp.find(u'&#252') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'&#252;')] + u'ü' + PageTemp[PageTemp.find(u'&#252;')+len(u'&#252;'):len(PageTemp)]
		while PageTemp.find(u'&#231;') != -1: 
			PageTemp = PageTemp[0:PageTemp.find(u'&#231;')] + u'ç' + PageTemp[PageTemp.find(u'&#231;')+len(u'&#231;'):len(PageTemp)]
		if pluriel[len(pluriel)-2:len(pluriel)] == u'ss':
			PageSing = PageSing[0:PageSing.find(template)+len(template)] + u'|s=' + pluriel[0:len(pluriel)-2] + PageSing[PageSing.find(template)+len(template):len(PageSing)]
			sauvegarde(page, PageSing, u'{{fr-rég|s=...}}')
		elif pluriel[len(pluriel)-2:len(pluriel)] == u'xs':
			return
		else:
			sauvegarde(page2, PageEnd, summary)
	# Pluriel 2
	if PageTemp.find(u'|p2=') != -1 and PageTemp.find(u'|p2=') < PageTemp.find(u'}}'):
		pluriel2 = PageTemp[PageTemp.find(u'|p2=')+4:PageTemp.find(u'}}')]
		if pluriel2.find(u'|') != -1: pluriel2 = pluriel2[0:pluriel2.find(u'|')]
		page2 = Page(site,pluriel2)
		if page2.exists(): 
			return
		else:
			PageEnd = u'== {{langue|fr}} ==\n{{-flex-' + nature + u'-|fr}}\n{{fr-rég' + pron + H + MF + '|s=' + PageHS + u'}}\n\'\'\'' + pluriel2 + u'\'\'\' {{pron' + pron + '|fr}}' + genre + u'\n# \'\'Pluriel de\'\' [[' + PageHS +']].\n'
			while PageEnd.find(u'{{pron|fr}}') != -1:
				PageEnd = PageEnd[0:PageEnd.find(u'{{pron|fr}}')+7] + u'|' + PageEnd[PageEnd.find(u'{{pron|fr}}')+7:len(PageEnd)]
		# Clés de tri
		if PageEnd.find(u'{{clé de tri') == -1:
			PageTitre = page2.title()
			PageT = ""
			key = "false"
			key2 = "false"
			for lettre in range(0,len(PageTitre)):
				# Latin
				if PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä':
					PageT = PageT + "a"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'ë':
					PageT = PageT + "e"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'í' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ï':
					PageT = PageT + "i"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ó'  or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'ö':
					PageT = PageT + "o"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'ù' or PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ü':
					PageT = PageT + "u"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ç':
					PageT = PageT + "c"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'æ':
					PageT = PageT + "ae"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'œ':
					PageT = PageT + "oe"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ñ':
					PageT = PageT + "n"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'ÿ':
					PageT = PageT + "y"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'-':
					PageT = PageT + " "
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'/':
					PageT = PageT + " "
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'\\':
					PageT = PageT + ""
					key = "yes"
				# Grec
				elif PageTitre[lettre:lettre+1] == u'Α' or PageTitre[lettre:lettre+1] == u'Ἀ' or PageTitre[lettre:lettre+1] == u'ἀ' or PageTitre[lettre:lettre+1] == u'Ἁ' or PageTitre[lettre:lettre+1] == u'ἁ' or PageTitre[lettre:lettre+1] == u'Ἂ' or PageTitre[lettre:lettre+1] == u'ἂ' or PageTitre[lettre:lettre+1] == u'Ἃ' or PageTitre[lettre:lettre+1] == u'ἃ' or PageTitre[lettre:lettre+1] == u'Ἄ' or PageTitre[lettre:lettre+1] == u'ἄ' or PageTitre[lettre:lettre+1] == u'Ἅ' or PageTitre[lettre:lettre+1] == u'ἅ' or PageTitre[lettre:lettre+1] == u'Ἆ' or PageTitre[lettre:lettre+1] == u'ἆ' or PageTitre[lettre:lettre+1] == u'Ἇ' or PageTitre[lettre:lettre+1] == u'ἇ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ὰ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ά' or PageTitre[lettre:lettre+1] == u'ᾈ' or PageTitre[lettre:lettre+1] == u'ᾀ' or PageTitre[lettre:lettre+1] == u'ᾉ' or PageTitre[lettre:lettre+1] == u'ᾁ' or PageTitre[lettre:lettre+1] == u'ᾊ' or PageTitre[lettre:lettre+1] == u'ᾂ' or PageTitre[lettre:lettre+1] == u'ᾋ' or PageTitre[lettre:lettre+1] == u'ᾃ' or PageTitre[lettre:lettre+1] == u'ᾌ' or PageTitre[lettre:lettre+1] == u'ᾄ' or PageTitre[lettre:lettre+1] == u'ᾍ' or PageTitre[lettre:lettre+1] == u'ᾅ' or PageTitre[lettre:lettre+1] == u'ᾎ' or PageTitre[lettre:lettre+1] == u'ᾆ' or PageTitre[lettre:lettre+1] == u'ᾏ' or PageTitre[lettre:lettre+1] == u'ᾇ' or PageTitre[lettre:lettre+1] == u'Ᾰ' or PageTitre[lettre:lettre+1] == u'ᾰ' or PageTitre[lettre:lettre+1] == u'Ᾱ' or PageTitre[lettre:lettre+1] == u'ᾱ' or PageTitre[lettre:lettre+1] == u'ᾼ' or PageTitre[lettre:lettre+1] == u'ᾳ' or PageTitre[lettre:lettre+1] == u'Ὰ' or PageTitre[lettre:lettre+1] == u'ᾲ' or PageTitre[lettre:lettre+1] == u'Ά' or PageTitre[lettre:lettre+1] == u'ᾴ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾶ' or PageTitre[lettre:lettre+1] == u'Ȃ' or PageTitre[lettre:lettre+1] == u'ᾷ':
					PageT = PageT + "α"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ε' or PageTitre[lettre:lettre+1] == u'Ἐ' or PageTitre[lettre:lettre+1] == u'ἐ' or PageTitre[lettre:lettre+1] == u'Ἑ' or PageTitre[lettre:lettre+1] == u'ἑ' or PageTitre[lettre:lettre+1] == u'Ἒ' or PageTitre[lettre:lettre+1] == u'ἒ' or PageTitre[lettre:lettre+1] == u'Ἓ' or PageTitre[lettre:lettre+1] == u'ἓ' or PageTitre[lettre:lettre+1] == u'Ἔ' or PageTitre[lettre:lettre+1] == u'ἔ' or PageTitre[lettre:lettre+1] == u'Ἕ' or PageTitre[lettre:lettre+1] == u'ἕ' or PageTitre[lettre:lettre+1] == u'Ὲ' or PageTitre[lettre:lettre+1] == u'ὲ' or PageTitre[lettre:lettre+1] == u'Έ' or PageTitre[lettre:lettre+1] == u'έ':
					PageT = PageT + "ε"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Η' or PageTitre[lettre:lettre+1] == u'Ἠ' or PageTitre[lettre:lettre+1] == u'ἠ' or PageTitre[lettre:lettre+1] == u'Ἡ' or PageTitre[lettre:lettre+1] == u'ἡ' or PageTitre[lettre:lettre+1] == u'Ἢ' or PageTitre[lettre:lettre+1] == u'ἢ' or PageTitre[lettre:lettre+1] == u'Ἣ' or PageTitre[lettre:lettre+1] == u'ἣ' or PageTitre[lettre:lettre+1] == u'Ἤ' or PageTitre[lettre:lettre+1] == u'ἤ' or PageTitre[lettre:lettre+1] == u'Ἥ' or PageTitre[lettre:lettre+1] == u'ἥ' or PageTitre[lettre:lettre+1] == u'Ἦ' or PageTitre[lettre:lettre+1] == u'ἦ' or PageTitre[lettre:lettre+1] == u'Ἧ' or PageTitre[lettre:lettre+1] == u'ἧ' or PageTitre[lettre:lettre+1] == u'ᾘ' or PageTitre[lettre:lettre+1] == u'ᾐ' or PageTitre[lettre:lettre+1] == u'ᾙ' or PageTitre[lettre:lettre+1] == u'ᾑ' or PageTitre[lettre:lettre+1] == u'ᾚ' or PageTitre[lettre:lettre+1] == u'ᾒ' or PageTitre[lettre:lettre+1] == u'ᾛ' or PageTitre[lettre:lettre+1] == u'ᾓ' or PageTitre[lettre:lettre+1] == u'ᾜ' or PageTitre[lettre:lettre+1] == u'ᾔ' or PageTitre[lettre:lettre+1] == u'ᾝ' or PageTitre[lettre:lettre+1] == u'ᾕ' or PageTitre[lettre:lettre+1] == u'ᾞ' or PageTitre[lettre:lettre+1] == u'ᾖ' or PageTitre[lettre:lettre+1] == u'ᾟ' or PageTitre[lettre:lettre+1] == u'ᾗ' or PageTitre[lettre:lettre+1] == u'Ὴ' or PageTitre[lettre:lettre+1] == u'ὴ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ή' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῂ' or PageTitre[lettre:lettre+1] == u'Η' or PageTitre[lettre:lettre+1] == u'ῃ' or PageTitre[lettre:lettre+1] == u'Ή' or PageTitre[lettre:lettre+1] == u'ῄ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῆ' or PageTitre[lettre:lettre+1] == u'ῌ' or PageTitre[lettre:lettre+1] == u'ῇ':
					PageT = PageT + "η"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ι' or PageTitre[lettre:lettre+1] == u'Ὶ' or PageTitre[lettre:lettre+1] == u'ὶ' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ί' or PageTitre[lettre:lettre+1] == u'ί' or PageTitre[lettre:lettre+1] == u'Ῐ' or PageTitre[lettre:lettre+1] == u'ῐ' or PageTitre[lettre:lettre+1] == u'Ῑ' or PageTitre[lettre:lettre+1] == u'ῑ' or PageTitre[lettre:lettre+1] == u'Ἰ' or PageTitre[lettre:lettre+1] == u'ἰ' or PageTitre[lettre:lettre+1] == u'Ἱ' or PageTitre[lettre:lettre+1] == u'ἱ' or PageTitre[lettre:lettre+1] == u'Ἲ' or PageTitre[lettre:lettre+1] == u'ἲ' or PageTitre[lettre:lettre+1] == u'Ἳ' or PageTitre[lettre:lettre+1] == u'ἳ' or PageTitre[lettre:lettre+1] == u'Ἴ' or PageTitre[lettre:lettre+1] == u'ἴ' or PageTitre[lettre:lettre+1] == u'Ἵ' or PageTitre[lettre:lettre+1] == u'ἵ' or PageTitre[lettre:lettre+1] == u'Ἶ' or PageTitre[lettre:lettre+1] == u'ἶ' or PageTitre[lettre:lettre+1] == u'Ἷ' or PageTitre[lettre:lettre+1] == u'ἷ' or PageTitre[lettre:lettre+1] == u'ΐ' or PageTitre[lettre:lettre+1] == u'ῖ' or PageTitre[lettre:lettre+1] == u'ῗ' or PageTitre[lettre:lettre+1] == u'ῒ':
					PageT = PageT + "ι" 
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ο' or PageTitre[lettre:lettre+1] == u'Ὀ' or PageTitre[lettre:lettre+1] == u'ὀ' or PageTitre[lettre:lettre+1] == u'Ὁ' or PageTitre[lettre:lettre+1] == u'ὁ' or PageTitre[lettre:lettre+1] == u'Ὂ' or PageTitre[lettre:lettre+1] == u'ὂ' or PageTitre[lettre:lettre+1] == u'Ὃ' or PageTitre[lettre:lettre+1] == u'ὃ' or PageTitre[lettre:lettre+1] == u'Ὄ' or PageTitre[lettre:lettre+1] == u'ὄ' or PageTitre[lettre:lettre+1] == u'Ὅ' or PageTitre[lettre:lettre+1] == u'ὅ' or PageTitre[lettre:lettre+1] == u'Ὸ' or PageTitre[lettre:lettre+1] == u'ὸ' or PageTitre[lettre:lettre+1] == u'Ό' or PageTitre[lettre:lettre+1] == u'ό':
					PageT = PageT + "ο"
					key = "yes"
				elif PageTitre[lettre:lettre+1] == u'Ω' or PageTitre[lettre:lettre+1] == u'Ὠ' or PageTitre[lettre:lettre+1] == u'ὠ' or PageTitre[lettre:lettre+1] == u'Ὡ' or PageTitre[lettre:lettre+1] == u'ὡ' or PageTitre[lettre:lettre+1] == u'Ὢ' or PageTitre[lettre:lettre+1] == u'ὢ' or PageTitre[lettre:lettre+1] == u'Ὣ' or PageTitre[lettre:lettre+1] == u'ὣ' or PageTitre[lettre:lettre+1] == u'Ὤ' or PageTitre[lettre:lettre+1] == u'ὤ' or PageTitre[lettre:lettre+1] == u'Ὥ' or PageTitre[lettre:lettre+1] == u'ὥ' or PageTitre[lettre:lettre+1] == u'Ὦ' or PageTitre[lettre:lettre+1] == u'ὦ' or PageTitre[lettre:lettre+1] == u'Ὧ' or PageTitre[lettre:lettre+1] == u'ὧ' or PageTitre[lettre:lettre+1] == u'Ὼ' or PageTitre[lettre:lettre+1] == u'ὼ' or PageTitre[lettre:lettre+1] == u'Ώ' or PageTitre[lettre:lettre+1] == u'ώ' or PageTitre[lettre:lettre+1] == u'ᾨ' or PageTitre[lettre:lettre+1] == u'ᾠ' or PageTitre[lettre:lettre+1] == u'ᾩ' or PageTitre[lettre:lettre+1] == u'ᾡ' or PageTitre[lettre:lettre+1] == u'ᾪ' or PageTitre[lettre:lettre+1] == u'ᾢ' or PageTitre[lettre:lettre+1] == u'ᾫ' or PageTitre[lettre:lettre+1] == u'ᾣ' or PageTitre[lettre:lettre+1] == u'ᾬ' or PageTitre[lettre:lettre+1] == u'ᾤ' or PageTitre[lettre:lettre+1] == u'ᾭ' or PageTitre[lettre:lettre+1] == u'ᾥ' or PageTitre[lettre:lettre+1] == u'ᾮ' or PageTitre[lettre:lettre+1] == u'ᾦ' or PageTitre[lettre:lettre+1] == u'ᾯ' or PageTitre[lettre:lettre+1] == u'ᾧ' or PageTitre[lettre:lettre+1] == u'ῼ' or PageTitre[lettre:lettre+1] == u'ῳ' or PageTitre[lettre:lettre+1] == u'ῲ' or PageTitre[lettre:lettre+1] == u'ῴ' or PageTitre[lettre:lettre+1] == u'ῶ' or PageTitre[lettre:lettre+1] == u'ῷ':
					PageT = PageT + "ω"
					key = "yes"
				# Cyrillique
				elif PageTitre[lettre:lettre+1] == u'Е' or PageTitre[lettre:lettre+1] == u'ѐ' or PageTitre[lettre:lettre+1] == u'Ѐ' or PageTitre[lettre:lettre+1] == u'ё' or PageTitre[lettre:lettre+1] == u'Ё':
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
				elif PageTitre[lettre:lettre+1].lower() == PageTitre[lettre:lettre+1]:
					PageT = PageT + PageTitre[lettre:lettre+1]
				else:
					PageT = PageT + PageTitre[lettre:lettre+1].lower()
					key2 = "yes"
			if key == "yes":
				PageEnd = PageEnd + u'\n{{clé de tri|' + PageT + u'}}\n'
			while PageTemp.find(u'&#32;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#32;')] + u' ' + PageTemp[PageTemp.find(u'&#32;')+len(u'&#32;'):len(PageTemp)]
			while PageTemp.find(u'&#224;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#224;')] + u'à' + PageTemp[PageTemp.find(u'&#224;')+len(u'&#224;'):len(PageTemp)]
			while PageTemp.find(u'&#226;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#226;')] + u'â' + PageTemp[PageTemp.find(u'&#226;')+len(u'&#226;'):len(PageTemp)]
			while PageTemp.find(u'&#228;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#228;')] + u'ä' + PageTemp[PageTemp.find(u'&#228;')+len(u'&#228;'):len(PageTemp)]
			while PageTemp.find(u'&#233;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#233;')] + u'é' + PageTemp[PageTemp.find(u'&#233;')+len(u'&#233;'):len(PageTemp)]
			while PageTemp.find(u'&#232;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#232;')] + u'è' + PageTemp[PageTemp.find(u'&#232;')+len(u'&#232;'):len(PageTemp)]
			while PageTemp.find(u'&#234;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#234;')] + u'ê' + PageTemp[PageTemp.find(u'&#234;')+len(u'&#234;'):len(PageTemp)]
			while PageTemp.find(u'&#235;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#235;')] + u'ë' + PageTemp[PageTemp.find(u'&#235;')+len(u'&#235;'):len(PageTemp)]
			while PageTemp.find(u'&#238;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#238;')] + u'î' + PageTemp[PageTemp.find(u'&#238;')+len(u'&#238;'):len(PageTemp)]
			while PageTemp.find(u'&#239;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#239;')] + u'ï' + PageTemp[PageTemp.find(u'&#239;')+len(u'&#239;'):len(PageTemp)]
			while PageTemp.find(u'&#244;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#244;')] + u'ô' + PageTemp[PageTemp.find(u'&#244;')+len(u'&#244;'):len(PageTemp)]
			while PageTemp.find(u'&#246;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#246;')] + u'ö' + PageTemp[PageTemp.find(u'&#246;')+len(u'&#246;'):len(PageTemp)]
			while PageTemp.find(u'&#249;') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#249;')] + u'ù' + PageTemp[PageTemp.find(u'&#249;')+len(u'&#249;'):len(PageTemp)]
			while PageTemp.find(u'&#251;') != -1: 
				PageTemp = PageTemp[0:PageTemp.find(u'&#251;')] + u'û' + PageTemp[PageTemp.find(u'&#251;')+len(u'&#251;'):len(PageTemp)]
			while PageTemp.find(u'&#252') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'&#252;')] + u'ü' + PageTemp[PageTemp.find(u'&#252;')+len(u'&#252;'):len(PageTemp)]
			while PageTemp.find(u'&#231;') != -1: 
				PageTemp = PageTemp[0:PageTemp.find(u'&#231;')] + u'ç' + PageTemp[PageTemp.find(u'&#231;')+len(u'&#231;'):len(PageTemp)]
			sauvegarde(page2,PageEnd, summary)

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def rec_anagram(counter):
	# Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1
def anagram(word):
    return rec_anagram(collections.Counter(word))
	
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
			# Conversion ASCII => Unicode (pour les .txt)
			modification(HTMLUnicode.HTMLUnicode(PageHS))
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
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
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
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
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
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

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
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

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage == True:
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
TraitementPage = modification(u'Puvirniturmiuq')
TraitementPage = modification(u'Ivujivimmiuq')
TraitementPage = modification(u'cache-flamme')
TraitementPage = modification(u'agent de maîtrise')
#TraitementCategory = crawlerCat(u'Catégorie:Pluriels manquants en français',False,u'')
'''
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementFile = crawlerFile('articles_list.txt')
TraitementLiens = crawlerLink(u'Modèle:' + template)
while 1:
	TraitementRC = crawlerRC()
'''

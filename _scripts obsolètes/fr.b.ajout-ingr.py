#!/usr/bin/env python
# coding: utf-8
# Ce script crée les redirections d'ingrédient

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
mynick = "JackBot"
language = "fr"
family = "wikibooks"
site = getSite(language,family)

# Modification du wiki
def modification(PageHS):
	page = Page(site,PageHS)
	if not page.exists():
		# Remplacements consensuels
		while PageHS.find(u'&#32;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#32;')] + u'&nbsp;' + PageHS[PageHS.find(u'&#32;')+len(u'&#32;'):len(PageHS)]
		while PageHS.find(u'&#224;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#224;')] + u'à' + PageHS[PageHS.find(u'&#224;')+len(u'&#224;'):len(PageHS)]
		while PageHS.find(u'&#226;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#226;')] + u'â' + PageHS[PageHS.find(u'&#226;')+len(u'&#226;'):len(PageHS)]
		while PageHS.find(u'&#228;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#228;')] + u'ä' + PageHS[PageHS.find(u'&#228;')+len(u'&#228;'):len(PageHS)]
		while PageHS.find(u'&#233;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#233;')] + u'é' + PageHS[PageHS.find(u'&#233;')+len(u'&#233;'):len(PageHS)]
		while PageHS.find(u'&#232;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#232;')] + u'è' + PageHS[PageHS.find(u'&#232;')+len(u'&#232;'):len(PageHS)]
		while PageHS.find(u'&#234;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#234;')] + u'ê' + PageHS[PageHS.find(u'&#234;')+len(u'&#234;'):len(PageHS)]
		while PageHS.find(u'&#235;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#235;')] + u'ë' + PageHS[PageHS.find(u'&#235;')+len(u'&#235;'):len(PageHS)]
		while PageHS.find(u'&#238;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#238;')] + u'î' + PageHS[PageHS.find(u'&#238;')+len(u'&#238;'):len(PageHS)]
		while PageHS.find(u'&#239;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#239;')] + u'ï' + PageHS[PageHS.find(u'&#239;')+len(u'&#239;'):len(PageHS)]
		while PageHS.find(u'&#244;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#244;')] + u'ô' + PageHS[PageHS.find(u'&#244;')+len(u'&#244;'):len(PageHS)]
		while PageHS.find(u'&#246;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#246;')] + u'ö' + PageHS[PageHS.find(u'&#246;')+len(u'&#246;'):len(PageHS)]
		while PageHS.find(u'&#249;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#249;')] + u'ù' + PageHS[PageHS.find(u'&#249;')+len(u'&#249;'):len(PageHS)]
		while PageHS.find(u'&#251;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#251;')] + u'û' + PageHS[PageHS.find(u'&#251;')+len(u'&#251;'):len(PageHS)]
		while PageHS.find(u'&#252') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#252;')] + u'ü' + PageHS[PageHS.find(u'&#252;')+len(u'&#252;'):len(PageHS)]
		while PageHS.find(u'&#231;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#231;')] + u'ç' + PageHS[PageHS.find(u'&#231;')+len(u'&#231;'):len(PageHS)]
		while PageHS.find(u'&#700;') != -1:
			PageHS = PageHS[0:PageHS.find(u'&#700;')] + u'\'' + PageHS[PageHS.find(u'&#700;')+len(u'&#700;'):len(PageHS)]
		summary = u'Redirection d\'ingrédient'
		if PageHS[0:1] == u'a' or PageHS[0:1] == u'e' or PageHS[0:1] == u'é' or PageHS[0:1] == u'è' or PageHS[0:1] == u'ê' or PageHS[0:1] == u'i' or PageHS[0:1] == u'o' or PageHS[0:1] == u'u' or PageHS[0:1] == u'y' or PageHS[0:1] == u'A' or PageHS[0:1] == u'E' or PageHS[0:1] == u'É' or PageHS[0:1] == u'È' or PageHS[0:1] == u'Ê' or PageHS[0:1] == u'I' or PageHS[0:1] == u'O' or PageHS[0:1] == u'U' or PageHS[0:1] == u'Y': 
			PageEnd = u'#REDIRECT[[:Catégorie:Recettes de cuisine à base d\'' + PageHS.lower() + u']]'
		else:
			PageEnd = u'#REDIRECT[[:Catégorie:Recettes de cuisine à base de ' + PageHS.lower() + u']]'
		sauvegarde(page,PageEnd,summary)

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
			# ĉ -> cx en espéranto
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
	if key == "yes":
		while PageT[0:1] == u' ': PageT = PageT[1:len(PageT)]
		return PageT
	else:
		#raw_input(PageTitre.encode(config.console_encoding, 'replace'))
		return PageTitre
		
# Traitement d'un fichier
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
		modification(Page.title())
	subcat = cat.subcategories(recurse = True)
	for subcategory in subcat:
		pages = subcategory.articlesList(False)
		for Page in pagegenerators.PreloadingGenerator(pages,100):
			modification(Page.title())
	
# Traitement des modifications récentes
def crawlerRC():
	RC = pagegenerators.RecentchangesPageGenerator()
	for Page in pagegenerators.PreloadingGenerator(RC,100):
		modification(Page.title())

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
        arrettitle = ''.join(u'Discussion utilisateur:' + mynick)
        arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
        gen = iter([arretpage])
        arret = arretpage.get()
        if arret != u"{{/Stop}}":
			pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
			exit(0)

def sauvegarde(PageCourante, Contenu, Resume):
	ArretDUrgence()
	try:
		result = "ok"
		#print(Contenu.encode(config.console_encoding, 'replace')[len(Contenu)-1000:len(Contenu)])
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
TraitementFile = crawlerFile('articles_list.txt')
'''
TraitementPage = modification(u'Cigale de mer')
TraitementCategory = crawlerCat(u'Catégorie:Personnalités de la photographie')
while 1:
	TraitementRC = crawlerRC()
'''

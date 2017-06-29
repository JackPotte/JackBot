#!/usr/bin/env python
# coding: utf-8
# Crée des pages à partir d'un tableau

# Importing modules
from wikipedia import *
import urllib, config, re, sys, codecs

# Declaring all global values
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)

# Modification du wiki
def modification(PageHS):
	summary = u'[[Utilisateur:Christian COGNEAUX/Préparation des temps géologiques|Création des temps géologiques]]'
	print(PageHS.encode(config.console_encoding, 'replace'))
	page = Page(site,PageHS)
	if page.exists():
		try:
			PageBegin = page.get()
		except wikipedia.NoPage:
			print "NoPage l 24"
			return
		except wikipedia.IsRedirectPage: 
			PageBegin = page.get(get_redirect=True)
			TxtTmp = u'<!--\n  Redirection créée par le robot User:DaftBot.\n  La création automatique de la page ciblée est prévue prochainement.\n-->'
			if PageBegin.find(TxtTmp) != -1:
				summary = u'[[Catégorie:Redirections à remplacer]]'
				PageBegin = PageBegin[0:PageBegin.find(TxtTmp)] + summary + PageBegin[PageBegin.find(TxtTmp)+len(TxtTmp):len(PageBegin)]
				sauvegarde(page,PageBegin, summary)
			else:
				print "IsRedirect 34"
			return
	else:
		print "NoPage l 37"
		return
	
	# Lecture du tableau
	PageTemp = PageBegin[PageBegin.find(u'Hongrois'):]
	while PageTemp.find(u'|-\n|') != -1:
		# Ligne suivante
		if PageTemp.find(u'|-\n|') != -1:
			PageTemp = PageTemp[PageTemp.find(u'|-\n|')+len(u'|-\n|'):]
			NewPage = trim(PageTemp[0:PageTemp.find(u'||')])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Etymologie1 = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Etymologie2 = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Etymologie3 = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Definition = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Prononciation = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Catalan = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Allemand = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Anglais = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Espagnol = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Italien = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Neerlandais = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Polonais = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		if PageTemp.find(u'||') != -1 and PageTemp.find(u'||') < PageTemp.find(u'\n'):
			PageTemp = PageTemp[PageTemp.find(u'||')+2:]
			Hongrois = trim(PageTemp[0:min(PageTemp.find(u'||'),PageTemp.find(u'\n'))])
		PageEnd = u"\n=={{langue|fr}}==\n{{-étym-}}\n"
		if Etymologie1 != "": PageEnd = PageEnd + u":\'\'(" + Etymologie1 + u")'' "
		if Etymologie2 != "" or Etymologie3 != "":
			PageEnd = PageEnd + Etymologie2 + u' ' + Etymologie3
		else:
			PageEnd = PageEnd + u"{{ébauche-étym|fr}}"
		PageEnd = PageEnd + u"\n\n{{-nom-|fr}}\n\'''{{subst:PAGENAME}}\''' {{pron|" + Prononciation.replace("/","") + u"|fr}}\n# " + Definition + u"\n\n{{-trad-}}\n{{trad-début}}" 
		if Allemand != "": PageEnd = PageEnd + u'\n* {{T|de}} : {{trad|de|' + Allemand.replace("[","").replace("]","") + u'}}'
		if Anglais != "": PageEnd = PageEnd + u'\n* {{T|en}} : {{trad|en|' + Anglais.replace("[","").replace("]","") + u'}}'
		if Catalan != "": PageEnd = PageEnd + u'\n* {{T|ca}} : {{trad|ca|' + Catalan.replace("[","").replace("]","") + u'}}'
		if Espagnol != "": PageEnd = PageEnd + u'\n* {{T|es}} : {{trad|es|' + Espagnol.replace("[","").replace("]","") + u'}}'
		if Hongrois != "": PageEnd = PageEnd + u'\n* {{T|hu}} : {{trad|hu|' + Hongrois.replace("[","").replace("]","") + u'}}'
		if Italien != "": PageEnd = PageEnd + u'\n* {{T|it}} : {{trad|it|' + Italien.replace("[","").replace("]","") + u'}}'
		if Neerlandais != "": PageEnd = PageEnd + u'\n* {{T|nl}} : {{trad|nl|' + Neerlandais.replace("[","").replace("]","") + u'}}'
		if Polonais != "": PageEnd = PageEnd + u'\n* {{T|p}} : {{trad|pl|' + Polonais.replace("[","").replace("]","") + u'}}'
		PageEnd = PageEnd + u'\n{{trad-fin}}'
		ClePage = CleDeTri(NewPage)
		if ClePage != u'' and ClePage != PageHS and ClePage.lower() != PageHS.lower(): PageEnd = PageEnd + u'\n\n{{clé de tri|' + ClePage + u'}}'
		newpage = Page(site,NewPage)
		if not newpage.exists(): sauvegarde(newpage, PageEnd, summary)		

def CleDeTri(PageTitre):
	PageT = u''
	key = "false"
	for lettre in range(0,len(PageTitre)):
		# Latin
		if PageTitre[lettre:lettre+1] == u'à' or PageTitre[lettre:lettre+1] == u'Á' or PageTitre[lettre:lettre+1] == u'á' or PageTitre[lettre:lettre+1] == u'â' or PageTitre[lettre:lettre+1] == u'ä' or PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'À' or PageTitre[lettre:lettre+1] == u'Â' or PageTitre[lettre:lettre+1] == u'Ä' or PageTitre[lettre:lettre+1] == u'Å' or PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'A' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'å' or PageTitre[lettre:lettre+1] == u'Å':
			PageT = PageT + "a"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'æ' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Æ' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "ae"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'b' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "b"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ç' or PageTitre[lettre:lettre+1] == u'c' or PageTitre[lettre:lettre+1] == u'c' or PageTitre[lettre:lettre+1] == u'c' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Ç' or PageTitre[lettre:lettre+1] == u'C' or PageTitre[lettre:lettre+1] == u'C' or PageTitre[lettre:lettre+1] == u'C' or PageTitre[lettre:lettre+1] == u'C' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "c"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'c':
			PageT = PageT + "cx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'd' or PageTitre[lettre:lettre+1] == u'd' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'D' or PageTitre[lettre:lettre+1] == u'Ð' or PageTitre[lettre:lettre+1] == u'Ð' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "d"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'è' or PageTitre[lettre:lettre+1] == u'È' or PageTitre[lettre:lettre+1] == u'é' or PageTitre[lettre:lettre+1] == u'É' or PageTitre[lettre:lettre+1] == u'ê' or PageTitre[lettre:lettre+1] == u'Ê' or PageTitre[lettre:lettre+1] == u'ë' or PageTitre[lettre:lettre+1] == u'Ë' or PageTitre[lettre:lettre+1] == u'e' or PageTitre[lettre:lettre+1] == u'e' or PageTitre[lettre:lettre+1] == u'e' or PageTitre[lettre:lettre+1] == u'e' or PageTitre[lettre:lettre+1] == u'e' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'E' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "e"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ƒ' or PageTitre[lettre:lettre+1] == u'ƒ':
			PageT = PageT + "f"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'g':
			PageT = PageT + "gx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'g' or PageTitre[lettre:lettre+1] == u'g' or PageTitre[lettre:lettre+1] == u'g' or PageTitre[lettre:lettre+1] == u'g' or PageTitre[lettre:lettre+1] == u'g' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'G' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "g"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'h':
			PageT = PageT + "hx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'h' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'H' or PageTitre[lettre:lettre+1] == u'H' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "h"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'i' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Î' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'I' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'Ì' or PageTitre[lettre:lettre+1] == u'ï' or PageTitre[lettre:lettre+1] == u'Ï':
			PageT = PageT + "i"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'j':
			PageT = PageT + "jx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'j' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'J' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "j"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'k' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'k' or PageTitre[lettre:lettre+1] == u'K' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'K':
			PageT = PageT + "k"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'l' or PageTitre[lettre:lettre+1] == u'l' or PageTitre[lettre:lettre+1] == u'l' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'l' or PageTitre[lettre:lettre+1] == u'l' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'L' or PageTitre[lettre:lettre+1] == u'L' or PageTitre[lettre:lettre+1] == u'L' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'L' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'í' or PageTitre[lettre:lettre+1] == u'Í':
			PageT = PageT + "i"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "m"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'n' or PageTitre[lettre:lettre+1] == u'n' or PageTitre[lettre:lettre+1] == u'n' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'N' or PageTitre[lettre:lettre+1] == u'N' or PageTitre[lettre:lettre+1] == u'N' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'ñ' or PageTitre[lettre:lettre+1] == u'Ñ':
			PageT = PageT + "n"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'Ô' or PageTitre[lettre:lettre+1] == u'ø' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'o' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Ø' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'O' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ó':
			PageT = PageT + "o"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'œ' or PageTitre[lettre:lettre+1] == u'Œ':
			PageT = PageT + "oe"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "p"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "q"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'r' or PageTitre[lettre:lettre+1] == u'r' or PageTitre[lettre:lettre+1] == u'r' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'R' or PageTitre[lettre:lettre+1] == u'R' or PageTitre[lettre:lettre+1] == u'R' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "r"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u's':
			PageT = PageT + "sx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u's' or PageTitre[lettre:lettre+1] == u's' or PageTitre[lettre:lettre+1] == u'š' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'S' or PageTitre[lettre:lettre+1] == u'S' or PageTitre[lettre:lettre+1] == u'S' or PageTitre[lettre:lettre+1] == u'Š' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'ß':
			PageT = PageT + "s"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u't' or PageTitre[lettre:lettre+1] == u't' or PageTitre[lettre:lettre+1] == u't' or PageTitre[lettre:lettre+1] == u't' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'T' or PageTitre[lettre:lettre+1] == u'T' or PageTitre[lettre:lettre+1] == u'T' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'T' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "t"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'u':
			PageT = PageT + "ux"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'u' or PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Û' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'U' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'Ú' or PageTitre[lettre:lettre+1] == u'ù' or PageTitre[lettre:lettre+1] == u'Ù' or PageTitre[lettre:lettre+1] == u'ü' or PageTitre[lettre:lettre+1] == u'Ü':
			PageT = PageT + "u"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "v"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'w' or PageTitre[lettre:lettre+1] == u'W':
			PageT = PageT + "w"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'y' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Y' or PageTitre[lettre:lettre+1] == u'Ÿ' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "y"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'z' or PageTitre[lettre:lettre+1] == u'z' or PageTitre[lettre:lettre+1] == u'ž' or PageTitre[lettre:lettre+1] == u'z' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'Z' or PageTitre[lettre:lettre+1] == u'Z' or PageTitre[lettre:lettre+1] == u'Ž' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "z"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'\'' or PageTitre[lettre:lettre+1] == u'’' or PageTitre[lettre:lettre+1] == u'\'':
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
		elif PageTitre[lettre:lettre+1] == u'a' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "a"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "e"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		# Cyrillique
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + u'?'
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		# Arabe
		elif PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?' or PageTitre[lettre:lettre+1] == u'?':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'??' or PageTitre[lettre:lettre+1] == u'??' or PageTitre[lettre:lettre+1] == u'??':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'??':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'??':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'??':
			PageT = PageT + "?"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'??':
			PageT = PageT + "?"
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
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
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
		#gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
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
	ArretDUrgence()
	result = "ok"
	#print(Contenu.encode(config.console_encoding, 'replace'))	#[len(Contenu)-2000:len(Contenu)]) #
	#result = raw_input("Sauvegarder ? (o/n) ")
	if result != "n" and result != "no" and result != "non":
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
PageHS = u'Utilisateur:Christian COGNEAUX/Préparation des temps géologiques'
TraitementPage = modification(PageHS)
'''
# Modèles
TraitementPage = modification(u'Utilisateur:JackBot/test')
TraitementLiens = crawlerLink(u'Modèle:R:DAF8',u'homme')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True)
TraitementRecherche = crawlerSearch(u'clé de tri')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')
while 1:
	TraitementRC = crawlerRC()
'''
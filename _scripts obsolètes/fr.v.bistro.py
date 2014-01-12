#!/usr/bin/env python
# Ce script crée les pages de la salle café.

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *

# Déclaration
language = "fr"
family = "wikiversity"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Création du café de la semaine'
bisextile = 28
debogage = True

# Calcul des dates
def date(j,m,a):
	if j > 31 and m == u'janvier':
		j = j - 31
		m = u'février'
	elif j > bisextile and m == u'février':
		j = j - bisextile
		m = u'mars'
	elif j > 31 and m == u'mars':
		j = j - 31
		m = u'avril'
	elif j > 30 and m == u'avril':
		j = j - 30
		m = u'mai'
	elif j > 31 and m == u'mai':
		j = j - 31
		m = u'juin'
	elif j > 30 and m == u'juin':
		j = j - 30
		m = u'juillet'
	elif j > 31 and m == u'juillet':
		j = j - 31
		m = u'août'
	elif j > 31 and m == u'août':
		j = j - 31
		m = u'septembre'
	elif j > 30 and m == u'septembre':
		j = j - 30
		m = u'octobre'
	elif j > 31 and m == u'octobre':
		j = j - 31
		m = u'novembre'
	elif j > 30 and m == u'novembre':
		j = j - 30
		m = u'décembre'
	elif j > 31 and m == u'décembre':
		j = j - 31
		m = u'janvier'
		a = a + 1
	return str(j) + u' ' + m + u' ' + str(a)

def date2(jj,mm):
	if mm == u'janvier':
		if jj > (31 + bisextile):
			jj = jj - (31 + bisextile)
			mm = u'03'
		elif jj > 31:
			jj = jj - 31
			mm = u'02'
		else:
			mm = u'01'
	elif mm == u'février':
		if jj > (31 + bisextile):
			jj = jj - (31 + bisextile)
			mm = u'04'		
		elif jj > bisextile: 
			jj = jj - bisextile
			mm = u'03'
		else:
			mm = u'02'
	elif mm == u'mars':
		if jj > 61:
			jj = jj - 61
			mm = u'05'		
		elif jj > 31: 
			jj = jj - 31
			mm = u'04'
		else:
			mm = u'03'
	elif mm == u'avril':
		if jj > 61:
			jj = jj - 61
			mm = u'06'		
		elif jj > 30: 
			jj = jj - 30
			mm = u'05'
		else:
			mm = u'04'
	elif mm == u'mai':
		if jj > 61:
			jj = jj - 61
			mm = u'07'		
		elif jj > 31: 
			jj = jj - 31
			mm = u'06'
		else:
			mm = u'05'
	elif mm == u'juin':
		if jj > 61:
			jj = jj - 61
			mm = u'08'	
		elif jj > 30: 
			jj = jj - 30
			mm = u'07'
		else:
			mm = u'06'
	elif mm == u'juillet':
		if jj > 62:
			jj = jj - 62
			mm = u'09'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'08'
		else:
			mm = u'07'
	elif mm == u'août':
		if jj > 61:
			jj = jj - 61
			mm = u'10'
		elif jj > 31: 
			jj = jj - 31
			mm = u'09'
		else:
			mm = u'08'
	elif mm == u'septembre':
		if jj > 61:
			jj = jj - 61
			mm = u'11'
		elif jj > 30: 
			jj = jj - 30
			mm = u'10'
		else:
			mm = u'09'
	elif mm == u'octobre':
		if jj > 61:
			jj = jj - 61
			mm = u'12'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'11'
		else:
			mm = u'10'
	elif mm == u'novembre':
		if jj > 61:
			jj = jj - 61
			mm = u'01'
		elif jj > 30: 
			jj = jj - 30
			mm = u'12'
		else:
			mm = u'11'
	elif mm == u'décembre':
		if jj > 62:
			jj = jj - 62
			mm = u'02'	
		elif jj > 31: 
			jj = jj - 31
			mm = u'01'
		else:
			mm = u'12'
	return str(jj) + u'/' + mm
	
def zero(n):
	if n < 10 and n > 0:
		return u'0' + str(n)
	else:
		return str(n)

# Modification du wiki
def modification():
	#j = 7 # 1e lundi de l'année
	j = 23 # avant-avant dernier lundi de décembre
	m = u'décembre'
	a = 2013
	for s in range(1, 53): # on commence semaine 4 pour coller au sommaire
		PageHS = u'Wikiversité:La salle café/' + zero(s) + u' ' + str(a)
		page = Page(site,PageHS)
		if not page.exists():
			PageEnd = u'= La salle café du ' + date(j+21,m,int(a)) + u' au ' + date(j+27,m,int(a)) + u' =\n<noinclude>\n{| align="right" rules="all" width="100px" cellpadding="0" cellspacing="0" style="margin: 0 0 1em 1em; border: 1px solid #999; border-right-width: 2px; border-bottom-width: 2px; font-size:90%; text-align:center; background-color: #FFFFFF;"\n! bgcolor="#bfbfff" | <font color="gray">Sous-pages</font>''''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s - 3) + u' ' + str(a) + u'|Du ' + date2(j,m) + u' au ' + date2(j+6,m) + u']]''''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s - 2) + u' ' + str(a) + u'|Du ' + date2(j+7,m) + u' au ' + date2(j+13,m) + u']]''''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s - 1) + u' ' + str(a) + u'|Du ' + date2(j+14,m) + u' au ' + date2(j+20,m) + u']]''''
			'''u'|-\n|bgcolor="#ccccff"| Semaine du ' + date2(j+21,m) + u' au ' + date2(j+27,m) + '''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s + 1) + u' ' + str(a) + u'|Du ' + date2(j+28,m) + u' au ' + date2(j+34,m) + u']]''''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s + 2) + u' ' + str(a) + u'|Du ' + date2(j+35,m) + u' au ' + date2(j+41,m) + u']]''''
			'''u'|-\n|[[Wikiversité:La salle café/' + zero(s + 3) + u' ' + str(a) + u'|Du ' + date2(j+42,m) + u' au ' + date2(j+48,m) + u']]''''
			'''u'|-\n|<!-- choisissez une image et remplacez ce commentaire par [[Image:Nom_de_l\'image.jpg|150px]] <small>description de l\'image</small> -->''''
			'''u'|}\n[http://fr.wikiversity.org/w/index.php?title=Wikiversité:La_salle_café&action=purge <small>Café rafraîchi</small>][{{SERVER}}{{localurl:Wikiversité:La salle café/{{#time:W Y}}|action=edit&section=new}} <small>Ajouter un message</small>]__TOC__</noinclude>'
			if PageEnd.find(u'Wikiversité:La salle café/0 ' + str(a)) > 1: PageEnd = PageEnd[0:PageEnd.find(u'Wikiversité:La salle café/0 ' + str(a))] + u'Wikiversité:La salle café/53 ' + str(int(a)-1) + PageEnd[PageEnd.find(u'Wikiversité:La salle café/0 ' + str(a))+len(u'Wikiversité:La salle café/0 ' + str(a)):len(PageEnd)]
			if PageEnd.find(u'Wikiversité:La salle café/-1 ' + str(a)) > 1: PageEnd = PageEnd[0:PageEnd.find(u'Wikiversité:La salle café/-1 ' + str(a))] + u'Wikiversité:La salle café/52 ' + str(int(a)-1) + PageEnd[PageEnd.find(u'Wikiversité:La salle café/-1 ' + str(a))+len(u'Wikiversité:La salle café/-1 ' + str(a)):len(PageEnd)]
			if PageEnd.find(u'Wikiversité:La salle café/-2 ' + str(a)) > 1: PageEnd = PageEnd[0:PageEnd.find(u'Wikiversité:La salle café/-2 ' + str(a))] + u'Wikiversité:La salle café/51 ' + str(int(a)-1) + PageEnd[PageEnd.find(u'Wikiversité:La salle café/-2 ' + str(a))+len(u'Wikiversité:La salle café/-2 ' + str(a)):len(PageEnd)]
			if PageEnd.find(u'Wikiversité:La salle café/-3 ' + str(a)) > 1: PageEnd = PageEnd[0:PageEnd.find(u'Wikiversité:La salle café/-3 ' + str(a))] + u'Wikiversité:La salle café/50 ' + str(int(a)-1) + PageEnd[PageEnd.find(u'Wikiversité:La salle café/-3 ' + str(a))+len(u'Wikiversité:La salle café/-3 ' + str(a)):len(PageEnd)]
			#print (PageEnd.encode(config.console_encoding, 'replace'))
			#raw_input(PageHS.encode(config.console_encoding, 'replace'))
			sauvegarde(page, PageEnd, summary)
		DateCourante = date(j+7,m,int(a))
		j = int(DateCourante[0:DateCourante.find(u' ')])
		m = DateCourante[DateCourante.find(u' ')+1:DateCourante.rfind(u' ')]
		a = DateCourante[DateCourante.rfind(u' ')+1:len(DateCourante)]


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
			if Page.namespace() == 0: modification(u'Discussion:' + Page.title())

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
Traitement = modification()
'''
#TraitementFile = lecture('articles_list.txt')
#TraitementLiens = crawlerLink(u'')
#TraitementCategory = crawlerCat(u'')
'''

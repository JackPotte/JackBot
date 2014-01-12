#!/usr/bin/env python
# coding: utf-8
# Ce script ajoute ou retire {{lien brisé}}, et remplace :
#	{{cite web}} par {{lien web}}
#	{{cite news}} par {{article}}
# avec leurs paramètres
'''
Reste à faire :
1 conserver param lien web dans lien brise
2 maj date lien web via categ sup 1 an
3 cgi
4 erreur si plusieurs &
pas de {{lien brisé}} dans {{ouvrage}}
'''
# Déclaration
import os, catlib, pagegenerators, codecs, urllib, urllib2, json, pprint, urlparse, datetime, webbrowser, re
from wikipedia import *
semiauto = False
language = "fr"
family = "wikipedia"
mynick = "JackBot"
site = getSite(language,family)
# Modèles à remplacer
limiteM = 3
ModeleEN = range(1, limiteM +1)
ModeleFR = range(1, limiteM +1)
ModeleEN[1] = u'cite web'
ModeleFR[1] = u'lien web'
ModeleEN[2] = u'cite news'
ModeleFR[2] = u'article'
ModeleEN[3] = u'lien arXiv'
ModeleFR[3] = u'lien arXiv'
#ModeleEN[4] = u'ouvrage'
#ModeleFR[4] = u'ouvrage'
# Paramètres à remplacer
limiteP = 17
ParamEN = range(1, limiteP +1)
ParamFR = range(1, limiteP +1)
ParamEN[1] = u'author'
ParamFR[1] = u'auteur'
ParamEN[2] = u'authorlink1'
ParamFR[2] = u'lien auteur'
ParamEN[3] = u'title'
ParamFR[3] = u'titre'
ParamEN[4] = u'publisher'
ParamFR[4] = u'éditeur'
ParamEN[5] = u'work'
ParamFR[5] = u'série'
ParamEN[6] = u'month'
ParamFR[6] = u'mois'
ParamEN[7] = u'year'
ParamFR[7] = u'année'
ParamEN[8] = u'accessdate'
ParamFR[8] = u'consulté le'
ParamEN[9] = u'quote'
ParamFR[9] = u'extrait'
ParamEN[10] = u'language'
ParamFR[10] = u'langue'
ParamEN[11] = u'first'
ParamFR[11] = u'prénom1'
ParamEN[12] = u'last'
ParamFR[12] = u'nom1'
ParamEN[13] = u'authorlink'
ParamFR[13] = u'lien auteur1'
ParamEN[14] = u'coauthors'
ParamFR[14] = u'nom2'
ParamEN[15] = u'newspaper'
ParamFR[15] = u'périodique'
ParamEN[16] = u'location'
ParamFR[16] = u'lieu'
ParamEN[17] = u'id'
ParamFR[17] = u'issn'

# Modification du wiki
def modification(PageHS):
	summary = u'[[Wikipédia:Bot/Requêtes/2012/11#Identifier les liens brisés (le retour ;-))]]'
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() !=0 and PageHS != u'Utilisateur:JackBot/test':
			return
		else:
			try:
				PageBegin = page.get()
			except wikipedia.NoPage:
				print "NoPage l 54"
				return
			except wikipedia.LockedPage: 
				print "Locked l 57"
				return
			except wikipedia.IsRedirectPage: 
				print "IsRedirect l 60"
				return
	else:
		print "NoPage l 41"
		return
	PageTemp = PageBegin
	PageEnd = u''
	'''while PageTemp.find(u'[http://') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'[http://')+1] + PageTemp[PageTemp.find(u'[http://')+len(u'[http:'):len(PageTemp)]
	while PageTemp.find(u'[https://') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'[https://')+1] + PageTemp[PageTemp.find(u'[https://')+len(u'[https:'):len(PageTemp)]
	while PageTemp.find(u'| url =') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'| url =')] + u'|url=' + PageTemp[PageTemp.find(u'| url =')+len(u'| url ='):len(PageTemp)]
	while PageTemp.find(u'| titre =') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'| titre =')] + u'|titre=' + PageTemp[PageTemp.find(u'| titre =')+len(u'| titre ='):len(PageTemp)]
	while PageTemp.find(u'|url =') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|url =')] + u'|url=' + PageTemp[PageTemp.find(u'|url =')+len(u'|url ='):len(PageTemp)]
	while PageTemp.find(u'|titre =') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|titre =')] + u'|titre=' + PageTemp[PageTemp.find(u'|titre =')+len(u'|titre ='):len(PageTemp)]
	while PageTemp.find(u'| url=') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'| url=')] + u'|url=' + PageTemp[PageTemp.find(u'| url=')+len(u'| url='):len(PageTemp)]
	while PageTemp.find(u'| titre=') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'| titre=')] + u'|titre=' + PageTemp[PageTemp.find(u'| titre=')+len(u'| titre='):len(PageTemp)]
	while PageTemp.find(u'|url= ') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|url= ')] + u'|url=' + PageTemp[PageTemp.find(u'|url= ')+len(u'|url= '):len(PageTemp)]
	while PageTemp.find(u'|titre= ') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|titre= ')] + u'|titre=' + PageTemp[PageTemp.find(u'|titre= ')+len(u'|titre= '):len(PageTemp)]'''
	while PageTemp.find(u'{{ cite web') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{ cite web')] + u'{{cite web' + PageTemp[PageTemp.find(u'{{ cite web')+len(u'{{ cite web'):len(PageTemp)]
	while PageTemp.find(u'{{cite  web') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{cite  web')] + u'{{cite web' + PageTemp[PageTemp.find(u'{{cite  web')+len(u'{{cite  web'):len(PageTemp)]
	while PageTemp.find(u'{{cite web |') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{cite web |')] + u'{{cite web|' + PageTemp[PageTemp.find(u'{{cite web |')+len(u'{{cite web |'):len(PageTemp)]
	while PageTemp.find(u'{{ Cite web') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{ Cite web')] + u'{{cite web' + PageTemp[PageTemp.find(u'{{ Cite web')+len(u'{{ Cite web'):len(PageTemp)]
	while PageTemp.find(u'{{Cite  web') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{Cite  web')] + u'{{cite web' + PageTemp[PageTemp.find(u'{{Cite  web')+len(u'{{Cite  web'):len(PageTemp)]
	while PageTemp.find(u'{{Cite web |') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{Cite web |')] + u'{{cite web|' + PageTemp[PageTemp.find(u'{{Cite web |')+len(u'{{Cite web |'):len(PageTemp)]
	while PageTemp.find(u'{{ cite news') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{ cite news')] + u'{{cite news' + PageTemp[PageTemp.find(u'{{ cite news')+len(u'{{ cite news'):len(PageTemp)]
	while PageTemp.find(u'{{cite  news') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{cite  news')] + u'{{cite news' + PageTemp[PageTemp.find(u'{{cite  news')+len(u'{{cite  news'):len(PageTemp)]
	while PageTemp.find(u'{{cite news |') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{cite news |')] + u'{{cite news|' + PageTemp[PageTemp.find(u'{{cite news |')+len(u'{{cite news |'):len(PageTemp)]
	while PageTemp.find(u'{{ Cite news') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{ Cite news')] + u'{{cite news' + PageTemp[PageTemp.find(u'{{ Cite news')+len(u'{{ Cite news'):len(PageTemp)]
	while PageTemp.find(u'{{Cite  news') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{Cite  news')] + u'{{cite news' + PageTemp[PageTemp.find(u'{{Cite  news')+len(u'{{Cite  news'):len(PageTemp)]
	while PageTemp.find(u'{{Cite news |') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'{{Cite news |')] + u'{{cite news|' + PageTemp[PageTemp.find(u'{{Cite news |')+len(u'{{Cite news |'):len(PageTemp)]
	# Si dans {{ouvrage}} "lire en ligne" est vide, cela bloque le paramètre "url"
	while PageTemp.find(u'|lire en ligne=|') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|lire en ligne=|')+1] + PageTemp[PageTemp.find(u'|lire en ligne=|')+len(u'|lire en ligne=|'):len(PageTemp)]
	# Remplacement des modèles et paramètres
	regex = ur'\{\{' + (.+?)(?:\]\]\n)'
	if re.compile(regex).search(PageTemp):
		try:
			PageTemp = PageTemp[0:re.search(regex,PageTemp).end()] + u'\n{{clé de tri|' + ClePage + u'}}\n' + PageTemp[re.search(regex,PageTemp).end():len(PageTemp)]
		except:
			print u'pb regex interwiki'
	else:
				
	
	while PageTemp.find(u'//') != -1:
		# 1) Recherche de chaque hyperlien
		url = u''
		LimiteDebURL = u''
		LimiteFinURL = u''
		titre = u''
		htmlSource = u''
		
		PageTemp2 = PageTemp[0:PageTemp.find(u'//')]
		# titre=
		if PageTemp2.rfind(u'titre=') > PageTemp2.rfind(u'{{') and (PageTemp2.rfind(u'titre=') > PageTemp2.rfind(u'}}') or PageTemp2.rfind(u'}}') < PageTemp2.rfind(u'{{')):
			PageTemp3 = PageTemp2[PageTemp2.rfind(u'titre=')+len(u'titre='):len(PageTemp2)]
			if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.rfind(u'}}') == -1):
				titre = PageTemp3[0:PageTemp3.find(u'|')]
			else:
				titre = PageTemp3[0:len(PageTemp3)]
			#print(PageTemp3.encode(config.console_encoding, 'replace'))
			#raw_input(titre.encode(config.console_encoding, 'replace'))
		# url=
		if PageTemp2[len(PageTemp2)-1:len(PageTemp2)] == u'[':
			LimiteDebURL = 1
		elif PageTemp2[len(PageTemp2)-5:len(PageTemp2)] == u'http:':
			LimiteDebURL = 5
		elif PageTemp2[len(PageTemp2)-6:len(PageTemp2)] == u'https:':
			LimiteDebURL = 6
		else:
			LimiteDebURL = 0
		if LimiteDebURL != 0:
			PageTemp2 = PageTemp[PageTemp.find(u'//'):len(PageTemp)]
			# titre=
			if titre == u'' and PageTemp2.find(u'titre=') != -1 and PageTemp2.find(u'titre=') < PageTemp2.find(u'\n') and PageTemp2.find(u'titre=') < PageTemp2.find(u'}}'):
				PageTemp3 = PageTemp2[PageTemp2.find(u'titre=')+len(u'titre='):len(PageTemp2)]
				if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.find(u'}}') == -1):
					titre = PageTemp3[0:PageTemp3.find(u'|')]
				else:
					titre = PageTemp3[0:PageTemp3.find(u'}}')]
			elif PageTemp2.find(u']') != -1 and (PageTemp.find(u'//') == PageTemp.find(u'[//')+1 or PageTemp.find(u'//') == PageTemp.find(u'[http://')+6 or PageTemp.find(u'//') == PageTemp.find(u'[https://')+7):
				titre = PageTemp2[PageTemp2.find(u' ')+1:PageTemp2.find(u']')]
			# url=	
			if PageTemp2.find(u' ') != -1 and ((PageTemp2.find(u' ') < PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u' ') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u' ') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u' ') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u' ') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u' ') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u' ') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u' '
			elif PageTemp2.find(u'\n') != -1 and ((PageTemp2.find(u'\n') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u'\n') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u'\n') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u'\n') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u'\n') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u'\n') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u'\n') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u'\n'
			elif PageTemp2.find(u']') != -1 and ((PageTemp2.find(u']') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u']') <  PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u']') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u']') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u']') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u']') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u']') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u']'
			elif PageTemp2.find(u'}') != -1 and ((PageTemp2.find(u'}') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u'}') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u'}') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u'}') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u'}') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u'}') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u'}') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u'}'
			elif PageTemp2.find(u'|') != -1 and ((PageTemp2.find(u'|') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u'|') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u'|') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u'|') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u'|') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u'|') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u'|') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u'|'
			elif PageTemp2.find(u'. ') != -1 and ((PageTemp2.find(u'. ') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u'. ') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u'. ') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u'. ') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u'. ') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u'. ') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1) and ((PageTemp2.find(u'. ') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u'. '
			elif PageTemp2.find(u', ') != -1 and ((PageTemp2.find(u', ') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u', ') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u', ') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u', ') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u', ') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u', ') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u', ') < PageTemp2.find(u'<') != -1) or PageTemp2.find(u'<') == -1):
				LimiteFinURL = u', '
			elif PageTemp2.find(u'<') != -1 and ((PageTemp2.find(u'<') <  PageTemp2.find(u'\n') != -1) or PageTemp2.find(u'\n') == -1) and ((PageTemp2.find(u'<') <  PageTemp2.find(u']') != -1) or PageTemp2.find(u']') == -1) and ((PageTemp2.find(u'<') < PageTemp2.find(u'}') != -1) or PageTemp2.find(u'}') == -1) and ((PageTemp2.find(u'<') < PageTemp2.find(u' ') != -1) or PageTemp2.find(u' ') == -1) and ((PageTemp2.find(u'<') < PageTemp2.find(u'. ') != -1) or PageTemp2.find(u'. ') == -1) and ((PageTemp2.find(u'<') < PageTemp2.find(u'|') != -1) or PageTemp2.find(u'|') == -1) and ((PageTemp2.find(u'<') < PageTemp2.find(u', ') != -1) or PageTemp2.find(u', ') == -1):
				LimiteFinURL = u'<'
			else:
				print 'Pas de limite dans ' + PageHS.encode(config.console_encoding, 'replace') + u' avec ' + url
				break
			if LimiteDebURL == 1:
				url = u'http:' + PageTemp[PageTemp.find(u'//'):PageTemp.find(u'//')+PageTemp2.find(LimiteFinURL)]
			else:
				url = PageTemp[PageTemp.find(u'//')-LimiteDebURL:PageTemp.find(u'//')+PageTemp2.find(LimiteFinURL)]
			try:
				user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
				headers = { 'User-Agent' : user_agent }
				req = urllib2.Request(url, "", headers)
				req.add_header('Accept','text/html')
				handle = urllib2.urlopen(req)
				htmlSource = handle.read()
				#s = unicode(htmlSource,'utf-8')
				#print s
				#print(handle.info())
				#print LienBrise
				
				# Bug IOError avec Google Books :
				'''sock = urllib.urlopen(url)
				htmlSource = sock.read()
				sock.close()'''
				
				# Bug dans addinfourl instance has no attribute 'find'
				'''req = urllib2.Request(url='http://stackoverflow.com/')
				htmlSource = urllib2.urlopen(req)'''
				
				# Bug IOError avec les wikis :
				'''req = urllib2.Request(url)
				handle = urllib2.urlopen(req)
				htmlSource = handle.read()'''
				
				LienBrise = False
			except UnicodeEncodeError:
				#print 'UnicodeEncodeError avec ' + url
				LienBrise = False
			except UnicodeDecodeError:
				#print 'UnicodeDecodeError avec ' + url
				LienBrise = False
			except IOError as e:
				#print "I/O error({0}): {1}".format(e.errno, e.strerror) + " avec " + url
				try:
					# Fonctionne pour britishbattles.com
					sock = urllib.urlopen(url)
					htmlSource = sock.read()
					#print url
					#print(sock.info())
					sock.close()
					LienBrise = False
				except UnicodeEncodeError:
					#print 'UnicodeEncodeError avec ' + url
					LienBrise = False
				except UnicodeDecodeError:
					#print 'UnicodeDecodeError avec ' + url
					LienBrise = False
				except IOError as e:
					#print "2e I/O error({0}): {1}".format(e.errno, e.strerror) + " avec " + url
					LienBrise = True
			except urllib2.HTTPError:
				#print 'HTTPError avec ' + url
				LienBrise = True
			except urllib2.URLError:
				#print 'URLError avec ' + url
				LienBrise = True
			except httplib.BadStatusLine:
				#print 'BadStatusLine avec ' + url
				LienBrise = True
			
			if htmlSource == "":
				# Fonctionne pour nytimes.com
				url = url + "?_r=4&"
				try:
					user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
					headers = { 'User-Agent' : user_agent }
					req = urllib2.Request(url, "", headers)
					req.add_header('Accept','text/html')
					handle = urllib2.urlopen(req)
					htmlSource = handle.read()
				except urllib2.HTTPError:
					#print 'HTTPError avec ' + url
					LienBrise = True
				except urllib2.URLError:
					#print 'URLError avec ' + url
					LienBrise = True
				except httplib.BadStatusLine:
					#print 'BadStatusLine avec ' + url
					LienBrise = True
				if url[len(url)-6:len(url)] == "?_r=4&": url = url[0:len(url)-6]
					
			# 2) Recherche si la page du lien existe encore (à faire : ouvrir un onglet pour vérifier en live)
			try:
				if htmlSource == "":
					LienBrise = True
				elif (htmlSource.find("404 error") != -1 and htmlSource.find("creating 404 error") == -1):
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " 404 error"
				elif htmlSource.find("404 Not Found") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " 404 Not Found"
				elif htmlSource.find("404 – File not found") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " 404 – File not found"
				elif htmlSource.find("Error 404 - Not found") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " Error 404 - Not found"
				elif htmlSource.find("Error 503 (Server Error)") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " 503 (Server Error)"
				elif htmlSource.find("Page not found") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " Page not found"
				elif htmlSource.find("The page you requested cannot be found") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " The page you requested cannot be found"
				elif htmlSource.find("The service you requested is not available at this time") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " The service you requested is not available at this time"
				elif htmlSource.find("<p>Soit vous avez mal &#233;crit le titre") != -1:
					LienBrise = True
					#print url.encode(config.console_encoding, 'replace') + " Soit vous avez mal"
				else:
					LienBrise = False
			except UnicodeEncodeError:
				#print 'UnicodeEncodeError avec ' + url
				LienBrise = False
			except UnicodeDecodeError:
				#print 'UnicodeDecodeError avec ' + url
				LienBrise = False
			except IOError:
				#print 'IOError avec ' + url
				LienBrise = True
			except httplib.BadStatusLine:
				#print 'BadStatusLine avec ' + url
				LienBrise = True
				
			if semiauto == True:
				# Confirmation manuelle à cause des sites comme http://www.kurosawa-drawings.com/page/27 (site parking, cloaking ?)
				webbrowser.open_new_tab(url)
				if LienBrise == True:
					result = raw_input("Lien brisé ? (o/n) ")
				else:
					result = raw_input("Lien fonctionnel ? (o/n) ")
				if result != "n" and result != "no" and result != "non":
					LienBrise = True
				else:
					LienBrise = False
			'''
			# Compte-rendu des URL détectées
			print u'-----------------------------------------------------------------'
			print url.encode(config.console_encoding, 'replace')
			print titre.encode(config.console_encoding, 'replace')
			print LienBrise
			print u'-----------------------------------------------------------------'
			'''
			
			# 3) Modification du wiki en conséquence	
			PageTemp3 = PageTemp[0:PageTemp.find(u'//')+2]
			debutURL = max(PageTemp3.find(u'http://'),PageTemp3.find(u'https://'),PageTemp3.find(u'[//'))
			PageTemp4 = PageTemp3
			# Filtre des modèles sans URL
			while PageTemp4.rfind(u'{{') != -1 and PageTemp4.rfind(u'{{') < PageTemp4.rfind(u'}}'):
				PageTemp4 = PageTemp4[0:PageTemp4.rfind(u'{{')]
			'''if PageTemp4.rfind(u'{{') == -1:
					print url.encode(config.console_encoding, 'replace')
					print u'Modèle ' + PageTemp4[0:10] + u' non ouvert par { dans ' #+ PageHS.encode(config.console_encoding, 'replace')
					log(PageHS)
					return
			if url.find('solarsystem.nasa.gov') != -1:
				print PageTemp4.encode(config.console_encoding, 'replace')
				print u'-----------------------'
			'''
			if PageTemp4.rfind(u'{{') != -1:	# and (PageTemp4.rfind(u'{{') < PageTemp4.rfind(u'url') or PageTemp4.rfind(u'{{') < PageTemp4.rfind(u'en ligne')):
				# 3.1) Lien dans un modèle connu
				positionDeb = PageTemp4.rfind(u'{{')
				PageTemp4 = PageTemp4[PageTemp4.rfind(u'{{')+2:len(PageTemp4)]
				if PageTemp4.find(u'|') == -1:
					print u'Modèle ' + AncienModele + u' non fermé par | dans ' + PageHS.encode(config.console_encoding, 'replace')
					log(PageHS)
					return
				elif PageTemp4.find(u'|') > PageTemp4.find(u'\n') and PageTemp4.find(u'\n') != -1:
					AncienModele = PageTemp4[0:PageTemp4.find(u'\n')]
				else:
					AncienModele = PageTemp4[0:PageTemp4.find(u'|')]	
				'''
				# Compte-rendu des URL détectées
				print url.encode(config.console_encoding, 'replace')
				#print PageTemp4.encode(config.console_encoding, 'replace')
				print AncienModele.encode(config.console_encoding, 'replace')
				print u'------------------'
				'''
				
				PageTemp4 = PageTemp[positionDeb+2:len(PageTemp)]	
				if PageTemp4.find(u'}}') == -1:
					print u'Modèle ' + AncienModele + u' non fermé par } dans ' + PageHS.encode(config.console_encoding, 'replace')
					log(PageHS)
					return
				
				if LienBrise == True and AncienModele != u'lien brisé' and AncienModele != u'Lien brisé':
					summary = summary + u', remplacement de ' + AncienModele + u' par {{lien brisé}}'
					if titre == u'':
						PageTemp = PageTemp[0:positionDeb+2] + u'lien brisé|url=' + url + u'}}' + PageTemp[positionDeb+2+PageTemp4.find(u'}}')+2+positionFin:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:positionDeb+2] + u'lien brisé|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[positionDeb+2+PageTemp4.find(u'}}')+2+positionFin:len(PageTemp)]
				elif AncienModele == u'cite web' or AncienModele == u'Cite web' or AncienModele == u'cite news' or AncienModele == u'Cite news' or AncienModele == u'lien web' or AncienModele == u'Lien web' or AncienModele == u'article' or AncienModele == u'Article' or AncienModele == u'lien arXiv' or AncienModele == u'Lien arXiv':
					summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer les {{Cite web}} par {{Lien web}}|{{Cite web}} -> {{Lien web}}]]'
					# Remplacement des paramètres en anglais
					for p in range(1,limiteP):
						#PageTemp5 = PageTemp[positionDeb:positionDeb+2+PageTemp4.find(u'}}')+2+positionFin]
						# Prise en compte des modèles imbriqués dans celui de l'URL, pour en déterminer la taille
						positionFin = 0
						re.compile model, template # double for dans un while
						
						PageTemp4 = PageTemp[positionDeb+2:len(PageTemp)]	
						ModeleDuLien = PageTemp4
						while ModeleDuLien.find(u'}}') > ModeleDuLien.find(u'{{') and ModeleDuLien.find(u'{{') != -1:
							positionFin = positionFin + ModeleDuLien.find(u'}}') + 2
							ModeleDuLien = ModeleDuLien[ModeleDuLien.find(u'}}')+2:len(ModeleDuLien)]
						ModeleDuLien = ModeleDuLien[0:ModeleDuLien.find(u'}}')+2]
						PageTemp5 = PageTemp[PageTemp.find(ModeleDuLien):PageTemp.find(ModeleDuLien)+len(ModeleDuLien)]

						if PageTemp5.find(ParamEN[p] + u'=') != -1:
							PageTemp = PageTemp[0:PageTemp.find(ModeleDuLien)+PageTemp5.find(ParamEN[p] + u'=')] + ParamFR[p] + PageTemp[PageTemp.find(ModeleDuLien)+PageTemp5.find(ParamEN[p] + u'=')+len(ParamEN[p]):len(PageTemp)]
						elif PageTemp5.find(ParamEN[p] + u' =') != -1:
							PageTemp = PageTemp[0:PageTemp.find(ModeleDuLien)+PageTemp5.find(ParamEN[p] + u' =')] + ParamFR[p] + PageTemp[PageTemp.find(ModeleDuLien)+PageTemp5.find(ParamEN[p] + u' =')+len(ParamEN[p]):len(PageTemp)]

					print url.encode(config.console_encoding, 'replace')
					raw_input(PageTemp5.encode(config.console_encoding, 'replace'))
					print u'--------------------------'
						
					# Remplacement des modèles en anglais	
					if AncienModele[1:len(AncienModele)] == u'ite web' or AncienModele == u'lien web':
						PageTemp = PageTemp[0:positionDeb+2] + u'lien web' + PageTemp[positionDeb+2+len(u'cite web'):len(PageTemp)]
					elif AncienModele == u'Lien web':
						PageTemp = PageTemp[0:positionDeb+2] + u'Lien web' + PageTemp[positionDeb+2+len(u'cite web'):len(PageTemp)]
					elif AncienModele[1:len(AncienModele)] == u'ite news':
						PageTemp = PageTemp[0:positionDeb+2] + u'article' + PageTemp[positionDeb+2+len(u'cite news'):len(PageTemp)]
					elif AncienModele == u'article':
						PageTemp = PageTemp[0:positionDeb+2] + u'article' + PageTemp[positionDeb+2+len(u'article'):len(PageTemp)]
					elif AncienModele == u'Article':
						PageTemp = PageTemp[0:positionDeb+2] + u'Article' + PageTemp[positionDeb+2+len(u'article'):len(PageTemp)]
					elif AncienModele == u'lien arXiv':
						PageTemp = PageTemp[0:positionDeb+2] + u'lien arXiv' + PageTemp[positionDeb+2+len(u'lien arXiv'):len(PageTemp)]
					elif AncienModele == u'Lien arXiv':
						PageTemp = PageTemp[0:positionDeb+2] + u'Lien arXiv' + PageTemp[positionDeb+2+len(u'lien arXiv'):len(PageTemp)]
				elif LienBrise == False and (AncienModele == u'lien brisé' or AncienModele == u'Lien brisé'):
					summary = summary + u', Retrait de {{lien brisé}}'
					PageTemp = PageTemp[0:positionDeb+2] + u'lien web' + PageTemp[positionDeb+2+len(u'lien brisé'):len(PageTemp)]
				#else: rien à faire (http://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Modèle_créant_un_lien_externe)
				
				
			elif LienBrise == True:
				if LimiteDebURL == 1:
					# 3.2) Lien entre crochets
					summary = summary + u', ajout de {{lien brisé}}'
					PageTemp = PageTemp[0:debutURL] + u'{{lien brisé|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[PageTemp.find(u'//')+PageTemp2.find(u']')+1:len(PageTemp)]
				else:
					# 3.3) Lien sans modèle ni crochet
					summary = summary + u', ajout de {{lien brisé}}'
					if PageTemp[debutURL-1:debutURL] == u'[' and PageTemp[debutURL-2:debutURL] != u'[[': debutURL = debutURL -1
					if LimiteFinURL == u' ' and PageTemp2.find(u']') != -1 and (PageTemp2.find(u'[') == -1 or PageTemp2.find(u']') < PageTemp2.find(u'[')): 
						# Présence d'un titre
						PageTemp = PageTemp[0:debutURL] + u'{{lien brisé|url=' + url + u'|titre=' + PageTemp[PageTemp.find(u'//')+PageTemp2.find(LimiteFinURL)+1:PageTemp.find(u'//')+PageTemp2.find(u']')]  + u'}}' + PageTemp[PageTemp.find(u'//')+PageTemp2.find(u']')+1:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:debutURL] + u'{{lien brisé|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+PageTemp2.find(LimiteFinURL):len(PageTemp)]		
				
					
		PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'//')+2]
		PageTemp = PageTemp[PageTemp.find(u'//')+2:len(PageTemp)]
		#print max(PageTemp2.find(u'http://'),PageTemp2.find(u'https://'),PageTemp2.find(u'[//'))
		#raw_input (PageTemp.encode(config.console_encoding, 'replace'))
		
	PageEnd = PageEnd + PageTemp
	PageTemp = PageEnd
	PageEnd = u''
	
	# Formatage fondamental
	PageTemp = re.sub(r'{{formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{Formatnum:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	PageTemp = re.sub(r'{{FORMATNUM:([0-9]*) ', r'{{formatnum:\1', PageTemp)
	while PageTemp.find(u' }}') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u' }}')] + PageTemp[PageTemp.find(u' }}')+1:len(PageTemp)]
		
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
			
	PageEnd = PageEnd + PageTemp		
	if PageEnd != PageBegin: sauvegarde(page,PageEnd, summary)

	
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
		elif PageTitre[lettre:lettre+1] == u'ç' or PageTitre[lettre:lettre+1] == u'ć' or PageTitre[lettre:lettre+1] == u'ċ' or PageTitre[lettre:lettre+1] == u'č' or PageTitre[lettre:lettre+1] == u'ƈ' or PageTitre[lettre:lettre+1] == u'ȼ' or PageTitre[lettre:lettre+1] == u'Ç' or PageTitre[lettre:lettre+1] == u'Ć' or PageTitre[lettre:lettre+1] == u'Ĉ' or PageTitre[lettre:lettre+1] == u'Ċ' or PageTitre[lettre:lettre+1] == u'Č' or PageTitre[lettre:lettre+1] == u'Ƈ' or PageTitre[lettre:lettre+1] == u'Ȼ':
			PageT = PageT + "c"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĉ':
			PageT = PageT + "cx"
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
		elif PageTitre[lettre:lettre+1] == u'ĝ':
			PageT = PageT + "gx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ğ' or PageTitre[lettre:lettre+1] == u'ġ' or PageTitre[lettre:lettre+1] == u'ģ' or PageTitre[lettre:lettre+1] == u'ǥ' or PageTitre[lettre:lettre+1] == u'ǧ' or PageTitre[lettre:lettre+1] == u'ǵ' or PageTitre[lettre:lettre+1] == u'Ĝ' or PageTitre[lettre:lettre+1] == u'Ğ' or PageTitre[lettre:lettre+1] == u'Ġ' or PageTitre[lettre:lettre+1] == u'Ģ' or PageTitre[lettre:lettre+1] == u'Ɠ' or PageTitre[lettre:lettre+1] == u'Ǥ' or PageTitre[lettre:lettre+1] == u'Ǧ' or PageTitre[lettre:lettre+1] == u'Ǵ':
			PageT = PageT + "g"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĥ':
			PageT = PageT + "hx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ħ' or PageTitre[lettre:lettre+1] == u'ȟ' or PageTitre[lettre:lettre+1] == u'Ĥ' or PageTitre[lettre:lettre+1] == u'Ħ' or PageTitre[lettre:lettre+1] == u'Ȟ':
			PageT = PageT + "h"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ı' or PageTitre[lettre:lettre+1] == u'î' or PageTitre[lettre:lettre+1] == u'ĩ' or PageTitre[lettre:lettre+1] == u'ī' or PageTitre[lettre:lettre+1] == u'ĭ' or PageTitre[lettre:lettre+1] == u'į' or PageTitre[lettre:lettre+1] == u'ǐ' or PageTitre[lettre:lettre+1] == u'ȉ' or PageTitre[lettre:lettre+1] == u'ȋ' or PageTitre[lettre:lettre+1] == u'Î' or PageTitre[lettre:lettre+1] == u'Ĩ' or PageTitre[lettre:lettre+1] == u'Ī' or PageTitre[lettre:lettre+1] == u'Ĭ' or PageTitre[lettre:lettre+1] == u'Į' or PageTitre[lettre:lettre+1] == u'İ' or PageTitre[lettre:lettre+1] == u'Ɨ' or PageTitre[lettre:lettre+1] == u'Ǐ' or PageTitre[lettre:lettre+1] == u'Ȉ' or PageTitre[lettre:lettre+1] == u'Ȋ' or PageTitre[lettre:lettre+1] == u'ĳ' or PageTitre[lettre:lettre+1] == u'Ĳ' or PageTitre[lettre:lettre+1] == u'ì' or PageTitre[lettre:lettre+1] == u'Ì' or PageTitre[lettre:lettre+1] == u'ï' or PageTitre[lettre:lettre+1] == u'Ï':
			PageT = PageT + "i"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ĵ':
			PageT = PageT + "jx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ǰ' or PageTitre[lettre:lettre+1] == u'ȷ' or PageTitre[lettre:lettre+1] == u'ɉ' or PageTitre[lettre:lettre+1] == u'Ĵ' or PageTitre[lettre:lettre+1] == u'Ɉ':
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
		elif PageTitre[lettre:lettre+1] == u'ô' or PageTitre[lettre:lettre+1] == u'Ô' or PageTitre[lettre:lettre+1] == u'ø' or PageTitre[lettre:lettre+1] == u'ō' or PageTitre[lettre:lettre+1] == u'ŏ' or PageTitre[lettre:lettre+1] == u'ő' or PageTitre[lettre:lettre+1] == u'ơ' or PageTitre[lettre:lettre+1] == u'ǒ' or PageTitre[lettre:lettre+1] == u'ǫ' or PageTitre[lettre:lettre+1] == u'ǭ' or PageTitre[lettre:lettre+1] == u'ǿ' or PageTitre[lettre:lettre+1] == u'ȍ' or PageTitre[lettre:lettre+1] == u'ȏ' or PageTitre[lettre:lettre+1] == u'ȫ' or PageTitre[lettre:lettre+1] == u'ȭ' or PageTitre[lettre:lettre+1] == u'ȯ' or PageTitre[lettre:lettre+1] == u'ȱ' or PageTitre[lettre:lettre+1] == u'Ø' or PageTitre[lettre:lettre+1] == u'Ō' or PageTitre[lettre:lettre+1] == u'Ŏ' or PageTitre[lettre:lettre+1] == u'Ő' or PageTitre[lettre:lettre+1] == u'Ɔ' or PageTitre[lettre:lettre+1] == u'Ɵ' or PageTitre[lettre:lettre+1] == u'ɵ' or PageTitre[lettre:lettre+1] == u'Ơ' or PageTitre[lettre:lettre+1] == u'Ǒ' or PageTitre[lettre:lettre+1] == u'Ǫ' or PageTitre[lettre:lettre+1] == u'Ǭ' or PageTitre[lettre:lettre+1] == u'Ǿ' or PageTitre[lettre:lettre+1] == u'Ȍ' or PageTitre[lettre:lettre+1] == u'Ȏ' or PageTitre[lettre:lettre+1] == u'Ȫ' or PageTitre[lettre:lettre+1] == u'Ȭ' or PageTitre[lettre:lettre+1] == u'Ȯ' or PageTitre[lettre:lettre+1] == u'Ȱ' or PageTitre[lettre:lettre+1] == u'ɔ' or PageTitre[lettre:lettre+1] == u'ở' or PageTitre[lettre:lettre+1] == u'Ở' or PageTitre[lettre:lettre+1] == u'ợ' or PageTitre[lettre:lettre+1] == u'Ợ' or PageTitre[lettre:lettre+1] == u'ò' or PageTitre[lettre:lettre+1] == u'ó':
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
		elif PageTitre[lettre:lettre+1] == u'ŝ':
			PageT = PageT + "sx"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ſ' or PageTitre[lettre:lettre+1] == u'ś' or PageTitre[lettre:lettre+1] == u'ş' or PageTitre[lettre:lettre+1] == u'š' or PageTitre[lettre:lettre+1] == u'ƪ' or PageTitre[lettre:lettre+1] == u'ș' or PageTitre[lettre:lettre+1] == u'ȿ' or PageTitre[lettre:lettre+1] == u'Ś' or PageTitre[lettre:lettre+1] == u'Ŝ' or PageTitre[lettre:lettre+1] == u'Ş' or PageTitre[lettre:lettre+1] == u'Š' or PageTitre[lettre:lettre+1] == u'Ʃ' or PageTitre[lettre:lettre+1] == u'Ș' or PageTitre[lettre:lettre+1] == u'ß':
			PageT = PageT + "s"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ţ' or PageTitre[lettre:lettre+1] == u'ť' or PageTitre[lettre:lettre+1] == u'ŧ' or PageTitre[lettre:lettre+1] == u'ƫ' or PageTitre[lettre:lettre+1] == u'ƭ' or PageTitre[lettre:lettre+1] == u'ț' or PageTitre[lettre:lettre+1] == u'ȶ' or PageTitre[lettre:lettre+1] == u'Ţ' or PageTitre[lettre:lettre+1] == u'Ť' or PageTitre[lettre:lettre+1] == u'Ŧ' or PageTitre[lettre:lettre+1] == u'Ƭ' or PageTitre[lettre:lettre+1] == u'Ʈ' or PageTitre[lettre:lettre+1] == u'Ț' or PageTitre[lettre:lettre+1] == u'Ⱦ' or PageTitre[lettre:lettre+1] == u'ⱦ':
			PageT = PageT + "t"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'ŭ':
			PageT = PageT + "ux"
			key = "yes"
		elif PageTitre[lettre:lettre+1] == u'û' or PageTitre[lettre:lettre+1] == u'ũ' or PageTitre[lettre:lettre+1] == u'ū' or PageTitre[lettre:lettre+1] == u'ů' or PageTitre[lettre:lettre+1] == u'ű' or PageTitre[lettre:lettre+1] == u'ų' or PageTitre[lettre:lettre+1] == u'ư' or PageTitre[lettre:lettre+1] == u'ǔ' or PageTitre[lettre:lettre+1] == u'ǖ' or PageTitre[lettre:lettre+1] == u'ǘ' or PageTitre[lettre:lettre+1] == u'ǚ' or PageTitre[lettre:lettre+1] == u'ǜ' or PageTitre[lettre:lettre+1] == u'ǟ' or PageTitre[lettre:lettre+1] == u'ǡ' or PageTitre[lettre:lettre+1] == u'ȕ' or PageTitre[lettre:lettre+1] == u'ȗ' or PageTitre[lettre:lettre+1] == u'ʉ' or PageTitre[lettre:lettre+1] == u'Û' or PageTitre[lettre:lettre+1] == u'Ũ' or PageTitre[lettre:lettre+1] == u'Ū' or PageTitre[lettre:lettre+1] == u'Ŭ' or PageTitre[lettre:lettre+1] == u'Ů' or PageTitre[lettre:lettre+1] == u'Ű' or PageTitre[lettre:lettre+1] == u'Ų' or PageTitre[lettre:lettre+1] == u'Ư' or PageTitre[lettre:lettre+1] == u'Ǔ' or PageTitre[lettre:lettre+1] == u'Ǖ' or PageTitre[lettre:lettre+1] == u'Ǘ' or PageTitre[lettre:lettre+1] == u'Ǚ' or PageTitre[lettre:lettre+1] == u'Ǜ' or PageTitre[lettre:lettre+1] == u'Ȕ' or PageTitre[lettre:lettre+1] == u'Ȗ' or PageTitre[lettre:lettre+1] == u'Ʉ' or PageTitre[lettre:lettre+1] == u'ủ' or PageTitre[lettre:lettre+1] == u'Ủ' or PageTitre[lettre:lettre+1] == u'ú' or PageTitre[lettre:lettre+1] == u'Ú':
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

def log(source):		
	txtfile = codecs.open(u'_hyperlinx.log', 'a', 'utf-8')
	txtfile.write(u'\n' + source + u'\n')
	txtfile.close()
			
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
	print(Contenu.encode(config.console_encoding, 'replace')[0:4000])	#[len(Contenu)-2000:len(Contenu)]) #
	result = raw_input("Sauvegarder ? (o/n) ")
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
		
# Lancement
TraitementPage = modification(u'Utilisateur:JackBot/test')
#TraitementLiens = crawlerLink(u'Modèle:Cite news',u'')
#TraitementLiens = crawlerLink(u'Modèle:Cite web',u'')
#TraitementLiens = crawlerLink(u'Modèle:Lien arXiv',u'')
'''
TraitementLiens = crawlerLink(u'Modèle:R:DAF8',u'homme')
TraitementFichier = crawlerFile('articles_list.txt')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True)
TraitementRecherche = crawlerSearch(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')
while 1:
	TraitementRC = crawlerRC()
'''

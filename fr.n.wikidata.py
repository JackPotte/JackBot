#!/usr/bin/env python
# coding: utf-8
import pywikibot
site = pywikibot.Site("fr", "wikinews")

def modification(PageHS):
	try:
		page = pywikibot.Page(site, PageHS)
	except NoPage:
		print "NoPage"
		return
	except IsRedirectPage:
		print "Redirect page"
		return
	except LockedPage:
		print "Locked/protected page"
		return
		
	# Données Wikidata
	try:
		item = pywikibot.ItemPage.fromPage(page) # AttributeError: 'module' object has no attribute 'ItemPage'
	except AttributeError:
		print "AttributeError"
		return
	dictionary = item.get()
	print dictionary
	print dictionary.keys()
	print item
	
	# Liens interwikis
	'''repo = site.data_repository()
	item = pywikibot.ItemPage(repo, u"Q42")
	item.get()
	print item.sitelinks'''
	
modification(u"Wikinews:Salle café/2014/septembre")
	
#!/usr/bin/env python
# coding: utf-8

# ébauche de factorisation de l'intro (pb : "crawler" appelle "modification")

# Environment modules
from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, os, re, socket, sys, urllib
import hyperlynx, defaultSort, html2Unicode, langues
# à faire : class PWB def __init__(self) def getWiki, save...

PWB = os.getcwd().find(u'Pywikibot') != -1
if PWB:
	import pywikibot
	from pywikibot import *
	from pywikibot import pagegenerators
	username = u'JackBot'	#KeyError: 'fr'
else:
	from wikipedia import *
	username = config.usernames[site.family.name][site.lang]

# crawlers...
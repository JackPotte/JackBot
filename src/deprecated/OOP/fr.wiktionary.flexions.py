#!/usr/bin/env python
# coding: utf-8
# This script calls the appropriate functions according to the parameters

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
import defaultSort, html2Unicode, hyperlynx, langues, creation as c, getPages as g
import pywikibot
from pywikibot import *

# Global variables
debugLevel = 0
if len(sys.argv) > 2:
    if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
        debugLevel= 1
fileName = __file__
if debugLevel > 0: print fileName
if fileName.rfind('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
siteLanguage = fileName[:2]
if debugLevel > 1: print siteLanguage
siteFamily = fileName[3:]
siteFamily = siteFamily[:siteFamily.find('.')]
if debugLevel > 1: print siteFamily
site = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

if len(sys.argv) > 1:
    DebutScan = u''
    if len(sys.argv) > 2:
        if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
            debugLevel= 1
        else:
            DebutScan = sys.argv[2]
    if sys.argv[1] == u'test':
        c.creation(u'User:' + username + u'/test')
    elif sys.argv[1] == u't':
        c.creation(u'User:' + username + u'/test court')
    elif sys.argv[1] == u'tu':
        # Test unitaire
        addText(u"== {{langue|fr}} ==\n=== {{S|étymologie}} ===\n{{ébauche-étym|fr}}\n=== {{S|nom|fr}} ===\n{{fr-rég|}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||fr}} {{genre ?}}\n#\n#* ''''\n==== {{S|variantes orthographiques}} ====\n==== {{S|synonymes}} ====\n==== {{S|antonymes}} ====\n==== {{S|dérivés}} ====\n==== {{S|apparentés}} ====\n==== {{S|vocabulaire}} ====\n==== {{S|hyperonymes}} ====\n==== {{S|hyponymes}} ====\n==== {{S|méronymes}} ====\n==== {{S|holonymes}} ====\n==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n=== {{S|prononciation}} ===\n* {{pron||fr}}\n* {{écouter|<!--  précisez svp la ville ou la région -->||audio=|lang=}}\n==== {{S|homophones}} ====\n==== {{S|paronymes}} ====\n=== {{S|anagrammes}} ===\n=== {{S|voir aussi}} ===\n* {{WP}}\n=== {{S|références}} ===\n{{clé de tri}}", u'fr', u'prononciation', u'* {{pron|boum|fr}}')
    elif sys.argv[1] == u'txt': 
        crawlerFile(u'articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
    elif sys.argv[1] == u'txt2':
        crawlerFile(u'articles_' + siteLanguage + u'_' + siteFamily + u'2.txt')
    elif sys.argv[1] == u'list':
        g.getFromFile(u'scripts/JackBot/articles_' + siteLanguage + u'_' + siteFamily + u'.txt', u'scripts/JackBot/fr.wiktionary.NomDeFamille-fr.txt')
    elif sys.argv[1] == u'm':
        crawlerLink(u'Modèle:ex',u'')
    elif sys.argv[1] == u'cat':
        crawlerCat(u'Catégorie:Wiktionnaire:Sections avec paramètres superflus',False,u'')
        crawlerCat(u'Catégorie:Wiktionnaire:Sections de type avec locution forcée',False,u'')
        crawlerCat(u'Catégorie:Termes peu attestés sans langue précisée',False,u'')
        crawlerCat(u'Catégorie:Genres manquants en français',False,u'')
    elif sys.argv[1] == u'lien':
        crawlerLink(u'Modèle:vx',u'')
    elif sys.argv[1] == u'page':
        c.creation(u'abréviatrice')
        c.creation(u'c**ksuckers')
    elif sys.argv[1] == u'trad':
        crawlerLink(u'Modèle:trad-',u'')
    elif sys.argv[1] == u's':
        crawlerSearch(u'"source à préciser"')
    elif sys.argv[1] == u'u':
        crawlerUser(u'Utilisateur:JackPotte', 1000,u'')
    else:
        # Au format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
        c.creation(sys.argv[1])
else:
    crawlerLink(u'Template:' + templateSource, DebutScan)

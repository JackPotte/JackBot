#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ce script archive des pages de discussion
"""
# Importation des modules
from __future__ import absolute_import, unicode_literals
import sys
import time
import pywikibot
from pywikibot import *
try:
    from src.lib import *
except ImportError:
    from lib import *

# Global variables
debug_level = 0
debug_aliases = ['debug', 'd', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level= 1
        sys.argv.remove(debugAlias)

file_name = __file__
if debug_level > 0: print(file_name)
if file_name.rfind('/') != -1: file_name = file_name[file_name.rfind('/')+1:]
site_language = file_name[:2]
if debug_level > 1: print(site_language)
site_family = file_name[3:]
site_family = site_family[:site_family.find('.')]
if debug_level > 1: print(site_family)
site = pywikibot.Site(site_language, site_family)
username = config.usernames[site_family][site_language]

summary = 'Autoarchivage de [[Wiktionnaire:Bot/Requêtes]]'

# Modification du wiki
'''
@param waitingTimeBeforeArchiving nombre de jours d'inactivité requis avant archivage
(utile pour permettre aux requêtes traitées d'être relues avant qu'elles soient enfouies
en page d'archive)
'''
def treat_page_by_name(page_name, waitingTimeBeforeArchiving=3):
    page = Page(site, page_name)

    # Ne pas archiver tout de suite si page très récemment modifiée
    # (Idéalement, la date des dernières interventions devrait être checkée...)
    latestRev = page.editTime()
    now = datetime.datetime.now()
    inactivityDuration = (now - latestRev).days
    if inactivityDuration < waitingTimeBeforeArchiving:
        return

    if page.exists():
        if page.namespace() != 4 and page.title() != 'User:JackBot/test':
            return
        else:
            try:
                PageTemp = page.get()
            except pywikibot.exceptions.NoPage:
                print("NoPage")
                return
            except pywikibot.exceptions.IsRedirectPage:
                print("Redirect page l 42")
                PageTemp = page.get(get_redirect=True)
                page2 = Page(site, PageTemp[PageTemp.find('[[')+2:PageTemp.find(']]')])
                try:
                    PageEnd2 = page2.get()
                except pywikibot.exceptions.NoPage:
                    print("NoPage")
                    return
                except pywikibot.exceptions.IsRedirectPage:
                    print("Redirect page l 51")
                    return
                except pywikibot.exceptions.LockedPage:
                    print("Locked/protected page")
                    return
                if PageEnd2.find('{{NavigBOT') == -1:
                    PageEnd2 = '{{NavigBOT|' + page2.title()[len(page2.title())-4:len(page2.title())] + '}}\n' + PageEnd2
                    save_page(page2, PageEnd2, summary)
                return
            except pywikibot.exceptions.LockedPage:
                print("Locked/protected page")
                return
    else:
        return

    PageEnd = ''
    annee = time.strftime('%Y')
    regex = '\n==[ ]*{{[rR]equête [fait|refus|refusée|sans suite]+}}.*==[ \t]*\n'
    while re.compile(regex).search(PageTemp):
        DebutParagraphe = re.search(regex,PageTemp).end()
        if re.search(r'\n==[^=]',PageTemp[DebutParagraphe:]):
            FinParagraphe = re.search(r'\n==[^=]',PageTemp[DebutParagraphe:]).start()
        else:
            FinParagraphe = len(PageTemp[DebutParagraphe:])
        if debug_level > 0:
            input(PageTemp[DebutParagraphe:][:FinParagraphe])
            print('-------------------------------------')
        if PageTemp[DebutParagraphe:].find('\n==') == -1:
            # Dernier paragraphe
            PageEnd = PageEnd + PageTemp[:DebutParagraphe][PageTemp[:DebutParagraphe].rfind('\n=='):] + PageTemp[DebutParagraphe:]
            PageTemp = PageTemp[:DebutParagraphe][:PageTemp[:DebutParagraphe].rfind('\n==')]
        else:
            PageEnd = PageEnd + PageTemp[:DebutParagraphe][PageTemp[:DebutParagraphe].rfind('\n=='):] + PageTemp[DebutParagraphe:][:FinParagraphe]
            PageTemp = PageTemp[:DebutParagraphe][:PageTemp[:DebutParagraphe].rfind('\n==')] + PageTemp[DebutParagraphe:][FinParagraphe:]


    # Sauvegardes
    if PageTemp != page.get():
        page2 = Page(site,page_name + '/Archives/' + annee)
        PageEnd2 = ''
        if page2.exists():
            try:
                PageEnd2 = page2.get()
            except pywikibot.exceptions.NoPage:
                print("NoPage")
                return
            except pywikibot.exceptions.IsRedirectPage:
                print("Redirect page")
                return
            except pywikibot.exceptions.LockedPage:
                print("Locked/protected page")
                return
        if PageEnd2.find('{{NavigBOT') == -1: PageEnd2 = '{{NavigBOT|' + page2.title()[len(page2.title())-4:len(page2.title())] + '}}\n' + PageEnd2
        save_page(page2, PageEnd2 + PageEnd, summary)
        save_page(page, PageTemp, summary)

treat_page_by_name('Wiktionnaire:Bots/Requêtes')

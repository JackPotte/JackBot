#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les articles de Wikilivres
"""
from __future__ import absolute_import, unicode_literals
import sys
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

checkURL = False
fix_tags = False
fixFiles = True
addCategory = False
oldTemplates = False

def treat_page_by_name(page_name):
    if debug_level > -1: print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    if current_page_content == 'KO' or current_page_content.find('{{en travaux') != -1 or current_page_content.find('{{En travaux') != -1: return
    PageTemp = current_page_content
    PageEnd = ''

    PageTemp = global_operations(PageTemp)
    if fixFiles: PageTemp = replace_files_errors(PageTemp)
    if fix_tags: PageTemp = replace_deprecated_tags(PageTemp)
    if checkURL: PageTemp = hyper_lynx(PageTemp)

    # Templates
    if PageTemp.find('{{AutoCat}}') == -1:
        # Présence de {{bas de page}} par inclusion
        oldTemplates = []
        oldTemplates.append('lienDePage')
        oldTemplates.append('NavTitre')
        oldTemplates.append('NavChapitre')
        for oldTemplate in oldTemplates:
            PageTemp = replace_template(PageTemp, oldTemplate)
        regex = r'<noinclude>[ \n\-]*</noinclude>\n?'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, '', PageTemp)

    regex = r'({{[a|A]utres projets[^}]*)\|noclear *= *1'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, r'\1', PageTemp)
    if debug_level > 1: input(PageTemp)

    if page.namespace() == 0:
        # Traitement des modèles
        regex = r'\{\{[P|p]ortail([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des portails'
            PageTemp = re.sub(regex, r'', PageTemp)
        regex = r'\{\{[P|p]alette([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des palettes'
            PageTemp = re.sub(regex, r'', PageTemp)
        PageTemp = PageTemp.replace('{{PDC}}', 'profondeur de champ')
        PageTemp = PageTemp.replace('{{reflist}}', '{{Références}}')
        PageTemp = PageTemp.replace('{{Reflist}}', '{{Références}}')

        PageTemp = PageTemp.replace('[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
        PageTemp = PageTemp.replace('[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
        PageTemp = PageTemp.replace('{{BookCat}}', '{{AutoCat}}')
        if addCategory:
            if trim(PageTemp) != '' and PageTemp.find('[[Catégorie:') == -1 and PageTemp.find('{{AutoCat}}') == -1 and PageTemp.find('{{imprimable') == -1:
                PageTemp = PageTemp + '\n\n{{AutoCat}}'
                summary = summary + ', [[Spécial:Pages non catégorisées]]'

        # Clés de tri pour les noms propres
        if PageTemp.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
            PageTemp = PageTemp[PageTemp.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):PageTemp.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len('[[Catégorie:Personnalités de la photographie')] + PageTemp[PageTemp.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
        '''ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
        regex = r'()\n{{DEFAULTSORT[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, r'\1', PageTemp)
        regex = r'()\n{{defaultsort[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, r'\1', PageTemp)
        '''

    PageEnd = PageEnd + PageTemp
    if PageEnd != current_page_content:
        PageTemp = PageTemp.replace('<references/>', '{{Références}}')
        PageTemp = PageTemp.replace('<references />', '{{Références}}')
        save_page(page, PageEnd, summary)


p = PageProvider(treat_page_by_name, site, debug_level)
set_globals(debug_level, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1: print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name('Catégorie:Python')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = '{{[Mm]éta-étiquette *\|[^}]*text-align: center'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            p.pages_by_user('User:' + username)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search('chinois')
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Template:autres projets')
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            afterPage = ''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pages_by_cat('Programmation Java (livre)')
            p.pages_by_cat('Programmation PHP (livre)')
            p.pages_by_cat('Programmation Python (livre)')
        elif sys.argv[1] == '-redirects':
            p.pages_by_redirects()
        elif sys.argv[1] == '-all':
           p.pages_by_all()
        elif sys.argv[1] == '-RC':
            while 1:
                p.pages_by_rc_last_day()
        elif sys.argv[1] == '-nocat':
            global addCategory
            addCategory = True
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(html2unicode(sys.argv[1]))
    else:
        while 1:
            p.pages_by_rc()

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les articles de Wikilivres
"""
from __future__ import absolute_import, unicode_literals
import os
import sys
import pywikibot
from pywikibot import *
# JackBot
dir_src = os.path.dirname(__file__)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
from lib import *

# Global variables
debug_level = 0
debug_aliases = ['debug', 'd', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

check_url = False
fix_tags = False
fix_files = True
do_add_category = False
treat_old_templates = False

old_templates = []
old_templates.append('lienDePage')
old_templates.append('NavTitre')
old_templates.append('NavChapitre')


def treat_page_by_name(page_name):
    if debug_level > -1:
        print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    if current_page_content == 'KO' or current_page_content.find('{{en travaux') != -1 \
            or current_page_content.find('{{En travaux') != -1:
        return
    page_content = current_page_content
    final_page_content = ''

    page_content = global_operations(page_content)
    if fix_files:
        page_content = replace_files_errors(page_content)
    if fix_tags:
        page_content = replace_deprecated_tags(page_content)
    if check_url:
        page_content = hyper_lynx(page_content)

    if page_content.find('{{AutoCat}}') == -1:
        # Présence de {{bas de page}} par inclusion
        for old_template in old_templates:
            page_content = replace_template(page_content, old_template)
        regex = r'<noinclude>[ \n\-]*</noinclude>\n?'
        if re.search(regex, page_content):
            page_content = re.sub(regex, '', page_content)

    regex = r'({{[a|A]utres projets[^}]*)\|noclear *= *1'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1', page_content)
    if debug_level > 1:
        input(page_content)

    if page.namespace() == 0:
        # Traitement des modèles
        regex = r'\{\{[P|p]ortail([^\}]*)\}\}'
        if re.search(regex, page_content):
            summary += ', retrait des portails'
            page_content = re.sub(regex, r'', page_content)
        regex = r'\{\{[P|p]alette([^\}]*)\}\}'
        if re.search(regex, page_content):
            summary += ', retrait des palettes'
            page_content = re.sub(regex, r'', page_content)
        page_content = page_content.replace('{{PDC}}', 'profondeur de champ')
        page_content = page_content.replace('{{reflist}}', '{{Références}}')
        page_content = page_content.replace('{{Reflist}}', '{{Références}}')

        page_content = page_content.replace('[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
        page_content = page_content.replace('[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
        page_content = page_content.replace('{{BookCat}}', '{{AutoCat}}')
        if do_add_category:
            if trim(page_content) != '' and page_content.find('[[Catégorie:') == -1 and page_content.find('{{AutoCat}}') == -1 and page_content.find('{{imprimable') == -1:
                page_content = page_content + '\n\n{{AutoCat}}'
                summary = summary + ', [[Spécial:Pages non catégorisées]]'

        # Clés de tri pour les noms propres
        if page_content.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
            final_page_content = final_page_content + page_content[:page_content.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
            page_content = page_content[page_content.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):page_content.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len('[[Catégorie:Personnalités de la photographie')] + page_content[page_content.find('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len('[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
        '''ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
        regex = r'()\n{{DEFAULTSORT[^}]*}}'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
        regex = r'()\n{{defaultsort[^}]*}}'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
        '''

    final_page_content = final_page_content + page_content
    if final_page_content != current_page_content:
        page_content = page_content.replace('<references/>', '{{Références}}')
        page_content = page_content.replace('<references />', '{{Références}}')
        save_page(page, final_page_content, summary)


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)


def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name('Catégorie:Python')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = r'{{[Mm]éta-étiquette *\|[^}]*text-align: center'
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
            after_page = ''
            if len(sys.argv) > 2: after_page = sys.argv[2]
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
            global do_add_category
            do_add_category = True
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(html2unicode(sys.argv[1]))
    else:
        while 1:
            p.pages_by_rc()


if __name__ == "__main__":
    main(sys.argv)

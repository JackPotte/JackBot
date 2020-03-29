#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les articles de Wikinews
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
debug_aliases = ['-debug', '-d']
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
fix_tags = True
fixFiles = True


def treat_page_by_name(page_name):
    print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    PageTemp = current_page_content
    PageEnd = ''

    PageTemp = global_operations(PageTemp)
    if fixFiles: PageTemp = replace_files_errors(PageTemp)
    if fix_tags: PageTemp = replace_deprecated_tags(PageTemp)
    if checkURL: PageTemp = hyper_lynx(PageTemp)

    #if page.namespace() == 0: TODO

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
            regex = ''
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
            p.pages_by_cat('Catégorie:Pages utilisant des liens magiques ISBN', namespaces = None, afterPage = afterPage)
            p.pages_by_cat('Catégorie:Pages avec ISBN invalide', namespaces = None, afterPage = afterPage)
        elif sys.argv[1] == '-redirects':
            p.pages_by_redirects()
        elif sys.argv[1] == '-all':
           p.pages_by_all()
        elif sys.argv[1] == '-RC':
            while 1:
                p.pages_by_rc_last_day()
        elif sys.argv[1] == '-nocat':
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

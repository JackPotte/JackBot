#!/usr/bin/env python
# coding: utf-8
"""
This script formats the Wikibooks pages
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

checkURL = False # TODO: translate hyperlynx.py by adding content{} at the top
fix_tags = False
fixFiles = True
addCategory = False

bookCatTemplates = []
bookCatTemplates.append('{{Auto category}}')
bookCatTemplates.append('{{Book category}}')
bookCatTemplates.append('{{AutoCat}}')
bookCatTemplates.append('{{Bookcat}}')
bookCatTemplates.append('{{BOOKCAT}}')
bookCatTemplates.append('[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
bookCatTemplates.append('[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')
bookCatTemplates.append('[[Category:{{FULLBOOKNAME}}|{{FULLCHAPTERNAME}}]]')
bookCatTemplates.append('[[Category:{{PAGENAME}}]]')
bookCatTemplates.append('[[Category:{{BASEPAGENAME}}]]')
bookCatTemplates.append('[[Category:{{FULLBOOKNAME}}]]')


def treat_page_by_name(page_name):
    if debug_level > 0:
        print('\n' + page_name)
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    if username not in page_name and (current_page_content == 'KO' or page_name.find('/print version') != -1):
        return
    summary = 'Formatting'
    PageTemp = current_page_content
    PageEnd = ''

    PageTemp = global_operations(PageTemp)
    if fixFiles: PageTemp = replace_files_errors(PageTemp)
    if fix_tags: PageTemp = replace_deprecated_tags(PageTemp)
    if checkURL: PageTemp = hyper_lynx(PageTemp)

    if debug_level > 1: print('Templates treatment')
    regex = r'{{[Tt]alk *archive([^}]*)}}='
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, r'{{Talk archive\1}}\n=', PageTemp)
    regex = r'{{[Tt]alk *header([^}]*)}}='
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, r'{{Talk header\1}}\n=', PageTemp)

    if username in page_name or page.namespace() in (0, 102, 110):
        regex = r'({{Programming/Navigation)\n?\|[^{}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, r'\1}}', PageTemp)
            PageTemp = PageTemp.replace('\n{{BookCat}}', '')
            summary = summary + ', {{Programming/Navigation}} automation'

        regex = r'^{{Programming/Navigation}}'
        if re.search(regex, PageTemp):
            PageTemp = '<noinclude>' + PageTemp[:len(r'{{Programming/Navigation}}')] + '</noinclude>' + PageTemp[len(r'{{Programming/Navigation}}'):]

        #TODO: {{BookCat|filing=deep}}
        for bookCatTemplate in bookCatTemplates:
            PageTemp = PageTemp.replace(bookCatTemplate, '{{BookCat}}')
            PageTemp = PageTemp.replace(bookCatTemplate[:2] + bookCatTemplate[2:3].lower() + bookCatTemplate[3:], '{{BookCat}}')
        if addCategory and has_more_than_time(page) and is_trusted_version(page):
            # The untrusted can have blanked a relevant content including {{BookCat}}
            if trim(PageTemp) != '' and PageTemp.find('{{BookCat}}') == -1 and \
              PageTemp.find('[[category:') == -1 and PageTemp.find('[[Category:') == -1 and \
              PageTemp.find('{{printable') == -1 and PageTemp.find('{{Printable') == -1 and \
              PageTemp.find('{{subjects') == -1 and PageTemp.find('{{Subjects') == -1:
                PageTemp = PageTemp + '\n\n{{BookCat}}'
                summary = summary + ', [[Special:UncategorizedPages]]'

    PageEnd = PageEnd + PageTemp
    if PageEnd != current_page_content:
        if current_page_content.count('{{') - current_page_content.count('}}') != PageEnd.count('{{') - PageEnd.count('}}'):
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
            treat_page_by_name('Python')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = ''
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            user = username
            if len(sys.argv) > 2: user = sys.argv[2]
            p.pages_by_user('User:' + user, numberOfPagesToTreat = 10000)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            research = 'insource:"Quantum theory of observation/ "'
            if len(sys.argv) > 2: research = sys.argv[2]
            p.pages_by_search(research)
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Category:Side Dish recipes', namespaces = None)
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            afterPage = ''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pages_by_cat('Pages using RFC magic links', afterPage = afterPage)
            #p.pagesByCat('Category:Pages using ISBN magic links', afterPage = afterPage)
            #p.pagesByCat('Category:Pages with ISBN errors', afterPage = afterPage)
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
            # TODO: https://en.wikibooks.org/wiki/Special:LintErrors/bogus-image-options
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

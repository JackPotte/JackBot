#!/usr/bin/env python
# coding: utf-8
"""
This script formats the Wikibooks pages
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
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

check_url = False  # TODO: translate hyperlynx.py by adding content{} at the top
fix_tags = False
fix_files = True
do_add_category = False

book_cat_templates = []
book_cat_templates.append('{{Auto category}}')
book_cat_templates.append('{{Book category}}')
book_cat_templates.append('{{AutoCat}}')
book_cat_templates.append('{{Bookcat}}')
book_cat_templates.append('{{BOOKCAT}}')
book_cat_templates.append('[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
book_cat_templates.append('[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')
book_cat_templates.append('[[Category:{{FULLBOOKNAME}}|{{FULLCHAPTERNAME}}]]')
book_cat_templates.append('[[Category:{{PAGENAME}}]]')
book_cat_templates.append('[[Category:{{BASEPAGENAME}}]]')
book_cat_templates.append('[[Category:{{FULLBOOKNAME}}]]')


def treat_page_by_name(page_name):
    print('\n' + page_name)
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    if username not in page_name and (current_page_content == 'KO' or page_name.find('/print version') != -1):
        return
    summary = 'Formatting'
    page_content = current_page_content
    final_page_content = ''

    page_content = global_operations(page_content)
    if fix_files:
        page_content = replace_files_errors(page_content)
    if fix_tags:
        page_content = replace_deprecated_tags(page_content)
    if check_url:
        page_content = hyper_lynx(page_content)

    if debug_level > 1:
        print('Templates treatment')
    regex = r'{{[Tt]alk *archive([^}]*)}}='
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{Talk archive\1}}\n=', page_content)
    regex = r'{{[Tt]alk *header([^}]*)}}='
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{Talk header\1}}\n=', page_content)

    if username in page_name or page.namespace() in (0, 102, 110):
        regex = r'({{Programming/Navigation)\n?\|[^{}]*}}'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1}}', page_content)
            page_content = page_content.replace('\n{{BookCat}}', '')
            summary = summary + ', {{Programming/Navigation}} automation'

        regex = r'^{{Programming/Navigation}}'
        if re.search(regex, page_content):
            page_content = '<noinclude>' + page_content[:len(r'{{Programming/Navigation}}')] + '</noinclude>' + page_content[len(r'{{Programming/Navigation}}'):]

        # TODO: {{BookCat|filing=deep}}
        for bookCatTemplate in book_cat_templates:
            page_content = page_content.replace(bookCatTemplate, '{{BookCat}}')
            page_content = page_content.replace(bookCatTemplate[:2] + bookCatTemplate[2:3].lower() + bookCatTemplate[3:], '{{BookCat}}')
        if do_add_category and has_more_than_time(page) and is_trusted_version(site, page):
            # The untrusted can have blanked a relevant content including {{BookCat}}
            if trim(page_content) != '' and page_content.find('{{BookCat}}') == -1 and \
              page_content.find('[[category:') == -1 and page_content.find('[[Category:') == -1 and \
              page_content.find('{{printable') == -1 and page_content.find('{{Printable') == -1 and \
              page_content.find('{{subjects') == -1 and page_content.find('{{Subjects') == -1:
                page_content = page_content + '\n\n{{BookCat}}'
                summary = summary + ', [[Special:UncategorizedPages]]'

    final_page_content = final_page_content + page_content
    if final_page_content != current_page_content:
        if current_page_content.count('{{') - current_page_content.count('}}') != final_page_content.count('{{') - final_page_content.count('}}'):
            save_page(page, final_page_content, summary)


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)


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
            p.pages_by_user('User:' + user, number_of_pages_to_treat=10000)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            research = 'insource:"Quantum theory of observation/ "'
            if len(sys.argv) > 2: research = sys.argv[2]
            p.pages_by_search(research)
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Category:Side Dish recipes', namespaces=None)
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            after_page = ''
            if len(sys.argv) > 2: after_page = sys.argv[2]
            p.pages_by_cat('Pages using RFC magic links', after_page=after_page)
            # p.pagesByCat('Category:Pages using ISBN magic links', after_page = after_page)
            # p.pagesByCat('Category:Pages with ISBN errors', after_page = after_page)
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
            # TODO: https://en.wikibooks.org/wiki/Special:LintErrors/bogus-image-options
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(update_html_to_unicode(sys.argv[1]))
    else:
        while 1:
            p.pages_by_rc()


if __name__ == "__main__":
    main(sys.argv)

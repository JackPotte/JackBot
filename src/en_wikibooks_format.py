#!/usr/bin/env python
# coding: utf-8
"""
This script formats the Wikibooks pages
"""
from __future__ import absolute_import, unicode_literals
import os
import sys
from pywikibot import config, Page, User
# JackBot
dir_src = os.path.dirname(__file__)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
from lib import *
from html2unicode import *
from default_sort import *
from hyperlynx import *
from languages import *
from page_functions import *
from PageProvider import *

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

do_check_url = False  # TODO: translate hyperlynx.py by adding content{} at the top
fix_tags = False
fix_files = True
do_add_category = False

book_cat_templates = []
book_cat_templates.append('{{Auto category}}')
book_cat_templates.append('{{Book category}}')
book_cat_templates.append('{{AutoCat}}')
book_cat_templates.append('{{Bookcat}}')
book_cat_templates.append('{{bookcat}}')
book_cat_templates.append('{{bookCat}}')
book_cat_templates.append('{{BOOKCAT}}')
book_cat_templates.append('[[Category:{{PAGENAME}}|{{SUBPAGENAME}}]]')
book_cat_templates.append('[[Category:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]')
book_cat_templates.append('[[Category:{{FULLBOOKNAME}}|{{FULLCHAPTERNAME}}]]')
book_cat_templates.append('[[Category:{{PAGENAME}}]]')
book_cat_templates.append('[[Category:{{BASEPAGENAME}}]]')
book_cat_templates.append('[[Category:{{FULLBOOKNAME}}]]')

book_categorizing_templates = []
book_categorizing_templates.append('header')
# TODO fill by templates category?


def treat_page_by_name(page_name):
    page = Page(site, page_name)
    return treat_page(page)


def treat_page(page):
    if debug_level > 0:
        print('------------------------------------')
    page_name = page.title()
    pywikibot.output("\n\03{blue}" + page_name + u"\03{default}")

    current_page_content = get_content_from_page(page, 'All')
    if username not in page_name and (
        current_page_content is None
        or page.namespace() != 0
        or page_name.find('/print version') != -1
    ):
        if debug_level > 0:
            print('  Page to avoid')
        return
    summary = 'Formatting'
    page_content = current_page_content
    final_page_content = ''

    page_content = global_operations(page_content)
    if fix_files:
        page_content = replace_files_errors(page_content)
    if fix_tags:
        page_content = replace_deprecated_tags(page_content)
    if do_check_url:
        page_content, summary = treat_broken_links(page_content, summary)

    if debug_level > 0:
        print('  Templates treatment')
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
            page_content = '<noinclude>' + page_content[:len(r'{{Programming/Navigation}}')] + '</noinclude>' \
                           + page_content[len(r'{{Programming/Navigation}}'):]

        for cat_tpl in book_categorizing_templates:
            regex = r'{{[ \n]*(' + cat_tpl[:1].upper() + '|' + cat_tpl[:1] + ')' + cat_tpl[1:] + '[ \n]*[|}]'
            if re.search(regex, page_content):
                if debug_level > 0:
                    print('  categorizing template: ' + cat_tpl)
                return
        for book_cat_template in book_cat_templates:
            page_content = page_content.replace(book_cat_template, '{{BookCat}}')
            page_content = page_content.replace(
                book_cat_template[:2] + book_cat_template[2:3].lower() + book_cat_template[3:],
                '{{BookCat}}'
            )
        if do_add_category and has_more_than_time(page) and ('/' in page.title() or is_trusted_version(site, page)):
            # The untrusted can have blanked a relevant content including {{BookCat}} or {{BookCat|filing=deep}}
            if trim(page_content) != '' and '{{BookCat' not in page_content \
              and '[[Category:' not in page_content and '[[category:' not in page_content \
              and '{{Printable' not in page_content and '{{printable' not in page_content \
              and '{{Subjects' not in page_content and '{{subjects' not in page_content \
              and '{{Shelves' not in page_content and '{{shelves' not in page_content:
                if '/' not in page_name:
                    if debug_level > 0:
                        print('  {{shelves}} addition')
                    page_content = page_content + '\n\n{{shelves}}'
                else:
                    if debug_level > 0:
                        print('  {{BookCat}} addition')
                    page_content = page_content + '\n\n{{BookCat}}'
                summary = summary + ', [[Special:UncategorizedPages]]'

    final_page_content = final_page_content + page_content
    if final_page_content != current_page_content:
        save_page(page, final_page_content, summary)


p = PageProvider(treat_page, site, debug_level)
set_functions_globals(debug_level, site, username)


def main(*args) -> int:
    global do_add_category
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            do_add_category = True
            treat_page_by_name('Python')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = r''
            if len(sys.argv) > 2:
                regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            user = username
            if len(sys.argv) > 2:
                user = sys.argv[2]
            p.pages_by_user('User:' + user, number_of_pages_to_treat=10000)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            research = 'insource:"Quantum theory of observation/ "'
            if len(sys.argv) > 2:
                research = sys.argv[2]
            p.pages_by_search(research)
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Category:Side Dish recipes', namespaces=None)
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            after_page = ''
            if len(sys.argv) > 2:
                after_page = sys.argv[2]
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
            do_add_category = True
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
            # TODO: https://en.wikibooks.org/wiki/Special:LintErrors/bogus-image-options
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            do_add_category = True
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(update_html_to_unicode(sys.argv[1]))
    else:
        while 1:
            p.pages_by_rc()
    return 0


if __name__ == "__main__":
    main(sys.argv)

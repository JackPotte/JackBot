#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import datetime
import inspect
import os
import sys
import re
import pywikibot
from pywikibot import config, Page, pagegenerators

# JackBot
dir_wt = os.path.dirname(__file__)
dir_src = os.path.dirname(dir_wt)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
from html2unicode import *


class PageProvider:
    """Pywikibot middleware"""
    debug_level = None
    site = None

    def __init__(self, treat_page, site, debug_level):
        self.treat_page = treat_page
        self.site = site
        self.debug_level = debug_level
        self.outputFile = open('lists/articles_' + str(site.lang) + '_' + str(site.family) + '.txt', 'a')

    # .txt may need to be formatted with format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
    def pages_by_file(self, source, site=None):
        if self.debug_level > 1:
            print(inspect.currentframe())
        if site is None:
            site = self.site
        if source:
            pages_list = open(source, 'r')
            while 1:
                page_name = pages_list.readline().decode(config.console_encoding, 'replace')
                fin = page_name.find("\t")
                page_name = page_name[:fin]
                if page_name == '':
                    break
                if page_name.find('[[') != -1:
                    page_name = page_name[page_name.find('[[') + 2:]
                if page_name.find(']]') != -1:
                    page_name = page_name[:page_name.find(']]')]
                # Conversion ASCII => Unicode (pour les .txt)
                page = Page(site, update_html_to_unicode(page_name))
                self.treat_page(page)
            pages_list.close()

    def page_by_xml(self, source, regex=None, site=None, folder='dumps', include=None, exclude=None,
                    title_include=None, title_exclude=None, namespaces=None, list_false_translations=False,
                    page_name_subst=None):
        if self.debug_level > 1:
            print(inspect.currentframe())
        if site is None:
            site = self.site
        if not source:
            print(' Dump non précisé')
            return
        source = source.replace('wikipedia', 'wiki')
        file_name = ''
        if source.find('*') != -1:
            file_name = [f for f in os.listdir(folder) if re.match(source, f)]
        if len(file_name) == 0:
            print(' Dump introubable : ' + source)
            return
        file_name = file_name[0]
        if self.debug_level > 0:
            print(' Dump trouvé : ' + file_name)
        from pywikibot import xmlreader
        dump = xmlreader.XmlDump(folder + '/' + file_name)
        parser = dump.parse()
        for entry in parser:
            if list_false_translations:
                for lang in ['frm', 'fro']:
                    section_position = entry.text.find('{{langue|' + lang + '}}')
                    if section_position != -1 and section_position < entry.text.find('{{S|traductions}}'):
                        self.outputFile.write((entry.title + '\n'))

            if not namespaces and entry.title.find(':') == -1:
                page_content = entry.text
                i = title_include is None or re.search(title_include, entry.title)
                e = title_exclude is None or not re.search(title_exclude, entry.title)
                if self.debug_level > 0:
                    print(i)
                    print(e)
                    print(title_exclude)
                    print(title_include)
                if (i and e) or (i and not title_exclude) or (not title_include and e):
                    if regex:
                        # print(re.escape(regex.replace('PAGENAME', entry.title[:page_nameSubst])))
                        if page_name_subst is None:
                            if re.search(regex, page_content, re.DOTALL):
                                self.outputFile.write((entry.title + '\n'))
                        elif re.search(re.escape(regex.replace('PAGENAME', entry.title[:page_name_subst])),
                                       page_content, re.DOTALL):
                            self.outputFile.write((entry.title + '\n'))
                    elif include and exclude and include in page_content and not exclude in page_content:
                        self.outputFile.write((entry.title + '\n'))
                    elif include and include in page_content and not exclude:
                        self.outputFile.write((entry.title + '\n'))
                    elif exclude and exclude not in page_content and not include:
                        self.outputFile.write((entry.title + '\n'))
                    elif not include and not exclude:
                        self.outputFile.write((entry.title + '\n'))
        self.outputFile.close()

    def pages_by_cat(self, category, recursive=False, after_page=None, namespaces=[0], names=None, not_names=None,
                     exclude=None, site=None, pages_list=False, linked=False):
        page_ids = 50
        if site is None:
            site = self.site
        if self.debug_level > 0:
            print(category)
        cat = pywikibot.Category(site, category)
        pages = list(cat.articles(recurse=False))
        if namespaces == [0]:
            if self.debug_level > 0:
                print('  NamespaceFilterPageGenerator')
            # TODO OK with 0, 2, 12, but with 10, 100, 114: Namespace identifier(s) not recognised
            gen = pagegenerators.NamespaceFilterPageGenerator(pages, namespaces)
        else:
            if self.debug_level > 0:
                print('  CategorizedPageGenerator')
            gen = pagegenerators.CategorizedPageGenerator(cat, recurse=recursive, namespaces=namespaces)
        modify = False
        for page in pagegenerators.PreloadingGenerator(gen, page_ids):
            if self.debug_level > 2:
                print('  ' + page.title())
            if page.title() == after_page:
                modify = True
            elif after_page is None or after_page == '' or modify:
                if linked:
                    gen2 = Page.linkedPages(namespaces=namespaces)
                    for linked_page in pagegenerators.PreloadingGenerator(gen2, page_ids):
                        if pages_list:
                            self.outputFile.write(
                                (linked_page.title() + '\n'))
                        else:
                            self.treat_page(linked_page)
                elif pages_list:
                    self.outputFile.write((page.title() + '\n'))
                else:
                    self.treat_page_if_name(page.title(), names, not_names)
        subcat = cat.subcategories(recurse=recursive != False)
        for subcategory in subcat:
            if self.debug_level > 0:
                print(' ' + subcategory.title())
            if namespaces is not None and 14 in namespaces:
                self.treat_page_if_name(subcategory.title(), names, not_names)
            if recursive:
                # TODO: recurse depth
                modify = True
                if exclude is not None:
                    for notCatName in exclude:
                        if subcategory.title().find(notCatName) != -1:
                            if self.debug_level > 0:
                                print(' ' + notCatName + ' ignoré')
                            modify = False
                if modify:
                    pages = subcategory.articles(False)
                    for page in pagegenerators.PreloadingGenerator(pages, page_ids):
                        if namespaces is None or page.namespace() in namespaces:
                            self.treat_page_if_name(page.title(), names, not_names)

    def treat_page_if_name(self, page_name, names=None, not_names=None):
        page = Page(self.site, page_name)
        if names is None and not_names is None:
            self.treat_page(page)
        elif names is not None:
            for name in names:
                if self.debug_level > 1:
                    print(' ' + name + ' trouvé')
                if page_name.find(name) != -1:
                    self.treat_page(page)
                    return
        elif not_names is not None:
            for notName in not_names:
                if self.debug_level > 1:
                    print(' ' + notName + ' ignoré')
                if page_name.find(notName) == -1:
                    self.treat_page(page)
                    return
        else:
            for name in names:
                for notName in not_names:
                    if page_name.find(name) != -1 and page_name.find(notName) == -1:
                        self.treat_page(page)
                        return

    # [[Special:WhatLinksHere]] with link
    def pages_by_untranscluded_link(self, page_name, after_page=None, site=None, namespaces=[0, 10], is_linked=False,
                      only_template_inclusion=True):
        if site is None:
            site = self.site
        is_after_page = False
        page = pywikibot.Page(site, page_name)
        linked_pages = page.linkedPages(namespaces=namespaces)
        for linked_page in linked_pages:
            if self.debug_level > 0:
                print(' Linked page: ' + linked_page.title())
            if not after_page or after_page == '' or is_after_page:
                if is_linked:
                    linked_linked_pages = linked_page.linkedPages(namespaces=namespaces)
                    for linked_linked_page in linked_linked_pages:
                        self.treat_page(linked_linked_page)
                else:
                    self.treat_page(linked_page)
            elif linked_page.title() == after_page:
                is_after_page = True

    # [[Special:WhatLinksHere]] with transclude
    def pages_by_link(self, page_name, after_page=None, site=None, namespaces=[0, 10], is_linked=False,
                      only_template_inclusion=True):
        if site is None:
            site = self.site
        is_after_page = False
        page = pywikibot.Page(site, page_name)
        linked_pages = page.embeddedin(namespaces=namespaces)
        for linked_page in linked_pages:
            if self.debug_level > 0:
                print(' Linked page: ' + linked_page.title())
            if not after_page or after_page == '' or is_after_page:
                if is_linked:
                    linked_linked_pages = linked_page.embeddedin(namespaces=namespaces)
                    for linked_linked_page in linked_linked_pages:
                        self.treat_page(linked_linked_page)
                else:
                    self.treat_page(linked_page)
            elif linked_page.title() == after_page:
                is_after_page = True

    # [[Special:Search]]
    def pages_by_search(self, search_string, namespaces=None, site=None, after_page=None):
        if site is None:
            site = self.site
        modify = False
        # search_string = search_string[:300] TODO: API error cirrussearch-backend-error
        gen = pagegenerators.SearchPageGenerator(search_string, site=site, namespaces=namespaces)
        for page in pagegenerators.PreloadingGenerator(gen, 100):
            if not after_page or after_page == '' or modify:
                self.treat_page(page)
            elif page.title() == after_page:
                modify = True

    # [[Special:RecentChanges]]
    def pages_by_rc(self, site=None):
        from lib import time_after_last_edition
        if site is None:
            site = self.site
        minimum_time = 30  # min
        gen = pagegenerators.RecentChangesPageGenerator(site=site)
        for page in pagegenerators.PreloadingGenerator(gen, 50):
            if self.debug_level > 1:
                print(str(time_after_last_edition(Page) + ' =? ' + str(minimum_time)))
            if time_after_last_edition(Page) > minimum_time:
                self.treat_page(page)

    # [[Special:RecentChanges]]
    def pages_by_rc_last_day(self, nobots=True, ns='0', site=None):
        if site is None:
            site = self.site
        # Génère les self.treatPages récentes de la dernière journée
        time_after_last_edition = 30  # minutes

        date_now = datetime.datetime.utcnow()
        # Date de la plus récente self.treat_page à récupérer
        date_start = date_now - datetime.timedelta(minutes=time_after_last_edition)
        # Date d'un jour plus tôt
        date_end = date_start - datetime.timedelta(1)

        start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
        end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

        for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
                                       rcdir='older', rctype='edit|new', namespace=ns,
                                       includeredirects=True, repeat=False, user=None,
                                       returndict=False, nobots=nobots):
            yield item[0]

    # [[Special:Contributions]]: the last pages touched by a user
    def pages_by_user(self, username, number_of_pages_to_treat=None, after_page=None, regex=None, not_regex=None,
                      site=None, namespaces=None):
        if site is None:
            site = self.site
        modify = False
        number_of_pages_treated = 0
        gen = pagegenerators.UserContributionsGenerator(username, namespaces=namespaces, site=site)
        for page in pagegenerators.PreloadingGenerator(gen, 100):
            if not after_page or after_page == '' or modify:
                found = False
                if regex is not None and not_regex is None:
                    if re.search(regex, page.title()):
                        found = True
                elif regex is None and not_regex is not None:
                    if not re.search(not_regex, page.title()):
                        found = True
                elif regex is not None and not_regex is not None:
                    if re.search(regex, page.title()) or not re.search(not_regex, page.title()): found = True
                else:
                    found = True

                if found:
                    self.treat_page(page)
                    # self.outputFile.write((page.title() + '\n'))
                number_of_pages_treated += 1
                if number_of_pages_to_treat is not None and number_of_pages_treated > number_of_pages_to_treat:
                    break
            elif page.title() == after_page:
                modify = True

    # [[Special:AllPages]]
    def pages_by_all(self, start='', ns=0, site=None):
        if site is None:
            site = self.site
        gen = pagegenerators.AllpagesPageGenerator(start, namespace=ns, includeredirects=False, site=site)
        for page in pagegenerators.PreloadingGenerator(gen, 100):
            self.treat_page(page)

    # [[Special:ListRedirects]]
    def pages_by_redirects(self, start='', site=None):
        if site is None:
            site = self.site
        for page in site.allpages(start, namespace=0, includeredirects='only'):
            self.treat_page(page)

    # [[Special:Index]]
    def pages_by_prefix(self, prefix='', site=None, namespace=None):
        if site is None:
            site = self.site
        for page in pagegenerators.PrefixingPageGenerator(prefix, site=site, namespace=namespace, includeredirects=False):
            self.treat_page(page)

    # [[Special:UncategorizedPages]]
    def pages_by_special_not_categorized(self, site=None):
        if site is None:
            site = self.site
        global do_add_category
        do_add_category = True
        for page in site.uncategorizedpages():
            self.treat_page(page)

    # [[Special:WantedCategories]]
    def pages_by_special_wanted_categories(self, site=None):
        if site is None:
            site = self.site
        for page in site.wantedcategories():
            self.treat_page(page)

    # [[Special:WantedPages]]
    def pages_by_special_wanted_pages(self, site=None):
        if site is None:
            site = self.site
        for page in site.wantedpages():
            self.treat_page(page)

    # [[Special:LinkSearch]]
    def pages_by_special_link_search(self, url, namespaces=[0], site=None):
        if site is None:
            site = self.site
        for page in site.exturlusage(url=url, namespaces=namespaces):
            self.treat_page(page)

    # [[Special:LintErrors]]
    def pages_by_special_lint(self, namespaces=None, site=None, lint_categories='multiple-unclosed-formatting-tags'):
        if site is None:
            site = self.site
        for page in site.linter_pages(lint_categories=lint_categories, namespaces=namespaces):
            self.treat_page(page)

    # *** Tested methods ***
    # TODO: impossible de parser une page spéciale ainsi (et pywikibot.site.BaseSite.postForm is deprecated)
    def pages_by_custom(self, site=None):
        if site is None:
            site = self.site
        page = pywikibot.Page(site, 'Special:ApiSandbox')
        # input(page._get_parsed_page())  # TODO API error pagecannotexist: Namespace doesn't allow actual pages.
        # self.treat_page(page)

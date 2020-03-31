#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import datetime
import inspect
import os
import re
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

try:
    from src.lib import html2Unicode
except ImportError:
    from lib import html2Unicode


class PageProvider:
    debug_level = None
    site = None

    def __init__(self, treatPage, site, debug_level):
        self.treatPage = treatPage
        self.site = site
        self.debug_level = debug_level
        self.outputFile = open('src/lists/articles_' + str(site.lang) + '_' + str(site.family) + '.txt', 'a')

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
                self.treatPage(html2unicode(page_name))
            pages_list.close()

    def page_by_xml(self, source, regex=None, site=None, folder='dumps', include=None, exclude=None,
                    title_include=None, title_exclude=None, namespaces=None, list_false_translations=False,
                    page_name_subst=None
                    ):
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
            print(' Dump introubable : ') + source
            return
        file_name = file_name[0]
        if self.debug_level > 0:
            print(' Dump trouvé : ') + file_name
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
                    elif exclude and not exclude in page_content and not include:
                        self.outputFile.write((entry.title + '\n'))
                    elif not include and not exclude:
                        self.outputFile.write((entry.title + '\n'))
                    '''else:
                    if self.debug_level > 1: print(' Pluriels non flexion')
                    if entry.title[-2:] == 'es':
                        if self.debug_level > 1: print(entry.title)
                        regex = r"=== {{S\|adjectif\|fr[^}]+}} ===\n[^\n]*\n*{{fr\-rég\|[^\n]+\n*'''" + re.escape(entry.title) + r"'''[^\n]*\n# *'*'*(Masculin|Féminin)+ *[P|p]luriel de *'*'* *\[\["
                        if re.search(regex, page_content):
                            if self.debug_level > 0: print(entry.title)
                            #page_content = re.sub(regex, r'\1|flexion\2', page_content)
                            #self.treatPage(html2Unicode(entry.title))

                    if self.debug_level > 1: print(' Ajout de la boite de flexion')
                    if entry.title[-1:] == 's':
                        if (page_content.find('{{S|adjectif|fr|flexion}}') != -1 or page_content.find('{{S|nom|fr|flexion}}') != -1) and page_content.find('{{fr-') == -1:
                            #print(entry.title) # limite de 8191 lignes dans le terminal.
                            #self.treatPage(entry.title)
                            self.outputFile.write((entry.title + '\n'))

                    if self.debug_level > 1: print(' balises HTML désuètes')
                    try:
    from src.lib import *
except ImportError:
    from lib import *
                    for deprecatedTag in deprecatedTags.keys():
                        if page_content.find('<' + deprecatedTag) != -1:
                            self.outputFile.write((entry.title + '\n'))
                    '''
        self.outputFile.close()

    def pages_by_cat(self, category, recursive=False, afterPage=None, namespaces=[0], names=None, not_names=None,
                     exclude=None, site=None, pagesList=False, linked=False
                     ):
        pageids = 50
        if site is None:
            site = self.site
        if self.debug_level > 0:
            print(category)
        cat = pywikibot.Category(self.site, category)
        pages = cat.articlesList(False)
        if namespaces == [0]:
            # TODO: filtre bien 0, 2, 12, mais pas 10 ni 100 ni 114, Namespace identifier(s) not recognised
            gen = pagegenerators.NamespaceFilterPageGenerator(pages, namespaces)
        else:
            gen = pagegenerators.CategorizedPageGenerator(cat)
        modify = False
        for Page in pagegenerators.PreloadingGenerator(gen, pageids):
            if Page.title() == afterPage:
                modify = True
            elif afterPage is None or afterPage == '' or modify:
                if linked:
                    gen2 = pagegenerators.ReferringPageGenerator(Page)
                    gen2 = pagegenerators.NamespaceFilterPageGenerator(gen2, namespaces)
                    for LinkedPage in pagegenerators.PreloadingGenerator(gen2, pageids):
                        if pagesList:
                            self.outputFile.write(
                                (LinkedPage.title() + '\n'))
                        else:
                            self.treatPage(LinkedPage.title())
                elif pagesList:
                    self.outputFile.write((Page.title() + '\n'))
                else:
                    self.treat_page_if_name(Page.title(), names, not_names)
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
                    pages = subcategory.articlesList(False)
                    for Page in pagegenerators.PreloadingGenerator(pages, pageids):
                        if namespaces is None or Page.namespace() in namespaces:
                            self.treat_page_if_name(Page.title(), names, not_names)

    def treat_page_if_name(self, page_name, names=None, not_names=None):
        if names is None and not_names is None:
            self.treatPage(page_name)
        elif names is not None:
            for name in names:
                if self.debug_level > 1:
                    print(' ' + name + ' trouvé')
                if page_name.find(name) != -1:
                    self.treatPage(page_name)
                    return
        elif not_names is not None:
            for notName in not_names:
                if self.debug_level > 1: print(' ' + notName + ' ignoré')
                if page_name.find(notName) == -1:
                    self.treatPage(page_name)
                    return
        else:
            for name in names:
                for notName in not_names:
                    if page_name.find(name) != -1 and page_name.find(notName) == -1:
                        self.treatPage(page_name)
                        return

    # [[Special:WhatLinksHere]]
    def pages_by_link(self, page_name, afterPage=None, site=None, namespaces=[0, 10], linked=False,
                      onlyTemplateInclusion=True):
        if site is None:
            site = self.site
        modify = False
        page = pywikibot.Page(site, page_name)
        gen = pagegenerators.ReferringPageGenerator(page, onlyTemplateInclusion=True)
        gen = pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not afterPage or afterPage == '' or modify:
                if linked:
                    gen2 = pagegenerators.ReferringPageGenerator(Page.title(),
                                                                 onlyTemplateInclusion=onlyTemplateInclusion)
                    gen2 = pagegenerators.NamespaceFilterPageGenerator(gen2, namespaces)
                    for LinkedPage in pagegenerators.PreloadingGenerator(gen2, 100):
                        self.treatPage(LinkedPage.title())
                else:
                    self.treatPage(Page.title())
            elif Page.title() == afterPage:
                modify = True

    # [[Special:Search]]
    def pages_by_search(self, searchString, namespaces=None, site=None, afterPage=None):
        if site is None:
            site = self.site
        modify = False
        # searchString = searchString[:300] TODO: API error cirrussearch-backend-error
        gen = pagegenerators.SearchPageGenerator(searchString, site=site, namespaces=namespaces)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not afterPage or afterPage == '' or modify:
                self.treatPage(Page.title())
            elif Page.title() == afterPage:
                modify = True

    # [[Special:RecentChanges]]
    def pages_by_rc(self, site=None):
        if site is None:
            site = self.site
        from lib import timeAfterLastEdition
        minimumTime = 30  # min
        gen = pagegenerators.RecentchangesPageGenerator(site=site)
        for Page in pagegenerators.PreloadingGenerator(gen, 50):
            if self.debug_level > 1:
                print(str(timeAfterLastEdition(Page) + ' =? ' + str(minimumTime)))
            if timeAfterLastEdition(Page) > minimumTime:
                self.treatPage(Page.title())

    # [[Special:RecentChanges]]
    def pages_by_rc_last_day(self, nobots=True, ns='0', site=None):
        if site is None:
            site = self.site
        # Génère les self.treatPages récentes de la dernière journée
        timeAfterLastEdition = 30  # minutes

        date_now = datetime.datetime.utcnow()
        # Date de la plus récente self.treatPage à récupérer
        date_start = date_now - datetime.timedelta(minutes=timeAfterLastEdition)
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
    def pages_by_user(self, username, numberOfPagesToTreat=None, afterPage=None, regex=None, notRegex=None, site=None,
                      namespaces=None):
        if site is None:
            site = self.site
        modify = False
        numberOfPagesTreated = 0
        gen = pagegenerators.UserContributionsGenerator(username, namespaces=namespaces, site=site)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            if not afterPage or afterPage == '' or modify:
                found = False
                if regex is not None and notRegex is None:
                    if re.search(regex, Page.title()): found = True
                elif regex is None and notRegex is not None:
                    if not re.search(notRegex, Page.title()): found = True
                elif regex is not None and notRegex is not None:
                    if re.search(regex, Page.title()) or not re.search(notRegex, Page.title()): found = True
                else:
                    found = True

                if found:
                    self.treatPage(Page.title())
                    # self.outputFile.write((Page.title() + '\n'))
                numberOfPagesTreated += 1
                if numberOfPagesToTreat is not None and numberOfPagesTreated > numberOfPagesToTreat: break
            elif Page.title() == afterPage:
                modify = True

    # [[Special:AllPages]]
    def pages_by_all(self, start=u'', ns=0, site=None):
        if site is None:
            site = self.site
        gen = pagegenerators.AllpagesPageGenerator(start, namespace=ns, includeredirects=False, site=site)
        for Page in pagegenerators.PreloadingGenerator(gen, 100):
            self.treatPage(Page.title())

    # [[Special:ListRedirects]]
    def pages_by_redirects(self, start=u'', site=None):
        if site is None:
            site = self.site
        for Page in site.allpages(start, namespace=0, includeredirects='only'):
            self.treatPage(Page.title())

    # [[Special:UncategorizedPages]]
    def pages_by_special_not_categorized(self, site=None):
        if site is None:
            site = self.site
        global addCategory
        addCategory = True
        for Page in site.uncategorizedpages():
            self.treatPage(Page.title())

    # [[Special:WantedCategories]]
    def pages_by_special_wanted_categories(self, site=None):
        if site is None:
            site = self.site
        for Page in site.wantedcategories():
            self.treatPage(Page.title())

    # [[Special:WantedPages]]
    def pages_by_special_wanted_pages(self, site=None):
        if site is None:
            site = self.site
        for Page in site.wantedpages():
            self.treatPage(Page.title())

    # [[Special:LinkSearch]]
    def pages_by_special_link_search(self, url, namespaces=[0], site=None):
        if site is None:
            site = self.site
        for Page in site.exturlusage(url=url, namespaces=namespaces):
            self.treatPage(Page.title())

    # [[Special:LintErrors]]
    def pages_by_special_lint(self, namespaces=None, site=None, lintCategories='multiple-unclosed-formatting-tags'):
        if site is None:
            site = self.site
        for Page in site.linter_pages(lint_categories=lintCategories, namespaces=namespaces):
            self.treatPage(Page.title())

    # *** Tested methods ***
    # TODO: impossible de parser une page spéciale ainsi (et pywikibot.site.BaseSite.postForm is deprecated)
    def pages_by_custom(self, site=None):
        if site is None:
            site = self.site
        page = pywikibot.Page(site, 'Special:ApiSandbox')
        # input(page._get_parsed_page())  # TODO WARNING: API error pagecannotexist: Namespace doesn't allow actual pages.
        # self.treatPage(Page.title())

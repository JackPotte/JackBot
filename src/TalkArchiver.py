#!/usr/bin/python
# coding: utf-8
"""
Ce script archive des pages de discussion
"""
from __future__ import absolute_import, unicode_literals
import datetime
import os
import re
import sys
import time
import pywikibot
from pywikibot import *
# JackBot
dir_src = os.path.dirname(__file__)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
from lib import *
from html2unicode import *
from default_sort import *
from languages import *
from page_functions import *
from PageProvider import *


class TalkArchiver:
    site = None
    user_name = None
    debug_level = None
    days_before_archiving = 3
    namespace = 4

    default_talk_pages = {
        'wikipedia': 'Wikipédia:Bot/Requêtes',
        'wikisource': 'Wikisource:Bots/Requêtes',
        'wiktionary': 'Wiktionnaire:Bots/Requêtes',
    }

    headers_templates = {
        'wikipedia': 'Wikipédia:Bot/Navig',
        'wikisource': 'NavigBOT',
        'wiktionary': 'NavigBOT',
    }

    headers = {
        'wikipedia': '<noinclude>{{Wikipédia:Bot/Navig}}</noinclude>',
        'wikisource': '{{NavigBOT|{{subst:CURRENTYEAR}}}}',
        'wiktionary': '{{NavigBOT|{{subst:CURRENTYEAR}}}}',
    }

    closed_status = {
        'wiktionary': [
            'fait',
            'refus',
            'refusée',
            'sans suite',
        ],
        'wikisource': [
            'fait',
            'refus',
            'refusée',
            'sans suite',
        ],
    }

    def __init__(self, args):
        self.site, self.user_name, self.debug_level, self.page_name = get_global_variables(args)

    def treat_page_by_name(self):
        if self.page_name is None:
            self.page_name = self.default_talk_pages[str(self.site.family)]
        if self.debug_level > 0:
            pywikibot.output("\n\03{red}" + self.page_name + u"\03{default}")

        page = Page(self.site, self.page_name)
        latest_rev = page.editTime()
        now = datetime.datetime.now()
        inactivity_duration = (now - latest_rev).days
        if inactivity_duration < self.days_before_archiving:
            if self.debug_level > 0:
                print(' The page has been modified in the last days: ' + str(inactivity_duration))
            return

        page_content = get_content_from_page(page, [self.namespace])
        final_page_content = ''
        summary = 'Autoarchivage de [[' + self.page_name + ']]'
        l = r'=='
        status_regex = r'|'.join(self.closed_status[str(self.site.family)])
        section_title_regex = r'\n' + l + r'[ \t]*{{[ \t]*[rR]equête (?:' + status_regex + r')[ \t]*}}[^\n=]*' + l + r'[ \t]*\n'
        sections_titles = get_sections_titles(page_content, section_title_regex)
        if self.debug_level > 1:
            print(sections_titles)

        for section_title in sections_titles:
            section, s_start, s_end = get_section_by_title(page_content, re.escape(section_title), len(l))
            if section is None:
                if self.debug_level > 0:
                    print(' section not found: ' + section_title)
                continue
            final_page_content += section
            page_content = page_content.replace(section, '')

        if page_content == page.get():
            return

        # TODO Wikipedia archives per month
        current_year = time.strftime('%Y')
        archive_page = Page(self.site, self.page_name + '/Archives/' + current_year)
        final_page_content2 = get_content_from_page(archive_page, [self.namespace])
        if final_page_content2 is None:
            final_page_content2 = ''
        if '{{' + self.headers_templates[str(self.site.family)] not in final_page_content2:
            final_page_content2 = self.headers[str(self.site.family)] + '\n' + final_page_content2
        save_page(archive_page, final_page_content2 + '\n' + final_page_content, summary)
        save_page(page, page_content, summary)


if __name__ == "__main__":
    t = TalkArchiver(sys.argv)
    t.treat_page_by_name()

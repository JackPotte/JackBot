#!/usr/bin/python
# coding: utf-8
"""
Ce script archive des pages de discussion
TODO merge into TalkArchiver when debugged
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
dir_wt = os.path.dirname(__file__)
dir_src = os.path.dirname(dir_wt)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
from lib import *
from html2unicode import *
from default_sort import *
from hyperlynx import *
from languages import *
from page_functions import *
from PageProvider import *
from wiktionary import *
from fr_wiktionary_functions import *
from fr_wiktionary_templates import *

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debug_alias in debug_aliases:
    if debug_alias in sys.argv:
        debug_level = 1
        sys.argv.remove(debug_alias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

closed_status = [
    'fait',
    'refus',
    'refusée',
    'sans suite',
]
wait_after_humans = True


def treat_page_by_name(page_name, waiting_time_before_archiving=3):
    global debug_level
    if debug_level > 0:
        print(page_name)
    page = Page(site, page_name)
    '''
    @param waiting_time_before_archiving nombre de jours d'inactivité requis avant archivage
    (utile pour permettre aux requêtes traitées d'être relues avant qu'elles soient enfouies
    en page d'archive)
    Ne pas archiver tout de suite si page très récemment modifiée
    TODO (Idéalement, la date des dernières interventions devrait être checkée...)
    '''
    latest_rev = page.latest_revision.timestamp
    now = datetime.datetime.now()
    inactivity_duration = (now - latest_rev).days
    if wait_after_humans and inactivity_duration < waiting_time_before_archiving:
        if debug_level > 0:
            print(f' The page has been modified in the last days: {str(inactivity_duration)}')
        return

    if not page.exists():
        if debug_level > 0:
            print(' The page does not exist')
        return
    if page.namespace() != 4 and 'JackBot' not in page.title():
        if debug_level > 0:
            print(' Untreated namespace')
        return

    summary = 'Autoarchivage de [[' + page_name + ']]'

    try:
        page_content = page.get()
    except pywikibot.exceptions.NoPageError as e:
        print(e)
        return
    except pywikibot.exceptions.IsRedirectPageError as e:
        print(e)
        page_content = page.get(get_redirect=True)
        page2 = Page(site, page_content[page_content.find('[[')+2:page_content.find(']]')])

        try:
            final_page_content2 = page2.get()
        except pywikibot.exceptions.NoPageError as e:
            print(e)
            return
        except pywikibot.exceptions.IsRedirectPageError as e:
            print(e)
            return
        except pywikibot.exceptions.LockedPageError as e:
            print(e)
            return

        if 'Bots' in page_name and '{{NavigBOT' not in final_page_content2:
            final_page_content2 = (
                '{{NavigBOT|'
                + page2.title()[len(page2.title()) - 4 :]
                + '}}\n'
                + final_page_content2
            )

            save_page(page2, final_page_content2, summary)
        return
    except pywikibot.exceptions.LockedPageError as e:
        print(e)
        return

    current_year = time.strftime('%Y')

    # TODO utiliser get_section() pour éviter les balises imbriquées : (ou juste pre, nowiki, et source qui peuvent contenir "==").
    # ex : https://fr.wiktionary.org/w/index.php?title=Wiktionnaire:Bots/Requ%C3%AAtes&diff=prev&oldid=29274173
    regex = r'\n===?[ ]*{{[rR]equête [fait|refus|refusée|sans suite]+}}.*===?[ \t]*\n'
    final_page_content = ''
    while re.compile(regex).search(page_content):
        paragraph_start = re.search(regex, page_content).end()
        if re.search(r'\n===?[^=]', page_content[paragraph_start:]):
            paragraph_end = re.search(r'\n===?[^=]', page_content[paragraph_start:]).start()
        else:
            paragraph_end = len(page_content[paragraph_start:])

        if debug_level > 0:
            input(page_content[paragraph_start:][:paragraph_end])
            print('-------------------------------------')

        if page_content[paragraph_start:].find('\n==') == -1:
            # Last paragraph
            final_page_content += (page_content[:paragraph_start][page_content[:paragraph_start].rfind('\n=='):]
                                   + page_content[paragraph_start:])
            page_content = page_content[:paragraph_start][:page_content[:paragraph_start].rfind('\n==')]
        else:
            final_page_content += (page_content[:paragraph_start][page_content[:paragraph_start].rfind('\n=='):]
                                   + page_content[paragraph_start:][:paragraph_end])
            page_content = (page_content[:paragraph_start][:page_content[:paragraph_start].rfind('\n==')]
                            + page_content[paragraph_start:][paragraph_end:])

    if page_content == page.get():
        if debug_level > 0:
            print(' No change')
        return

    page2 = Page(site, f'{page_name}/Archives/{current_year}')
    final_page_content2 = ''
    if page2.exists():
        try:
            final_page_content2 = page2.get()
        except pywikibot.exceptions.NoPageError as e:
            print(e)
            return
        except pywikibot.exceptions.IsRedirectPageError as e:
            print(e)
            return
        except pywikibot.exceptions.LockedPageError as e:
            print(e)
            return

    if 'Bots' in page_name and '{{NavigBOT' not in final_page_content2:
        final_page_content2 = (
            '{{NavigBOT|'
            + page2.title()[len(page2.title()) - 4 :]
            + '}}\n'
            + final_page_content2
        )
    save_page(page2, final_page_content2 + final_page_content, summary)
    save_page(page, page_content, summary)


def main(*args) -> int:
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-tu', '-t']:
            global wait_after_humans
            wait_after_humans = False
            treat_page_by_name(f'User:{username}/test unitaire')
    else:
        treat_page_by_name('Wiktionnaire:Boîte à idées')
        treat_page_by_name('Wiktionnaire:Bots/Requêtes')
    return 0


if __name__ == "__main__":
    main(sys.argv)

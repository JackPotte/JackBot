#!/usr/bin/env python
# coding: utf-8
"""
Ce script importe les flexions d'un Wiktionary dans un autre où le lemme se trouve
"""
from __future__ import absolute_import, unicode_literals
import os
import sys
from pywikibot import config, Page
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

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

addDefaultSort = False
foreign_language = 'en'
source_site = pywikibot.Site(foreign_language, site_family)
templateSource = 'en-past of'
textTranslated = 'Passé de'
DebutScan = 'interspersed'
# TODO pluriels fr + en


def treat_page_by_name(page_name):
    page = Page(source_site, page_name)
    return treat_page(page, False)


def treat_page(source_page, is_lemma=True):
    global debug_level
    if debug_level > 0:
        print('------------------------------------')

    if is_lemma:
        lemma_page_name = source_page.title()
        last_letter = lemma_page_name[-1:]
        # TODO check each inflexion (plural, present participle...)
        if last_letter == 'e':
            page_name = lemma_page_name + 'd'
        elif last_letter == 'y':
            page_name = lemma_page_name[:-1] + 'ied'
        else:
            page_name = lemma_page_name + 'ed'
        source_page = Page(source_site, page_name)
        if not source_page.exists():
            page_name = lemma_page_name + lemma_page_name[-1:] + 'ed'
            source_page = Page(source_site, page_name)
    else:
        page_name = source_page.title()
    pywikibot.output("\n\03{blue}" + page_name + "\03{default}")

    if not source_page.exists():
        if debug_level > 0:
            print(' missing page content')
        return
    if source_page.namespace() != 0 and source_page.title() != 'User:JackBot/test':
        if debug_level > 0:
            print(' untreated namespace')
        return

    target_page = Page(site, page_name)
    if target_page.exists():
        # TODO search for foreign_language
        return

    page_content = get_content_from_page(source_page, 'All')
    if page_content == '':
        return

    summary = 'Importation depuis [[' + foreign_language + ':' + source_page.title() + ']]'
    # Nature grammaticale
    page_content2 = page_content[:page_content.find(templateSource)]
    # Code langue
    page_content = page_content[page_content.find(templateSource)+len(templateSource)+1:]
    if page_content.find("lang=") != -1 and page_content.find("lang=") < page_content.find('}}'):
        page_content2 = page_content[page_content.find("lang=")+5:len(page_content)]
        if page_content2.find('|') != -1 and page_content2.find('|') < page_content2.find('}}'):
            language_code = page_content2[:page_content2.find("|")]
            page_content = page_content[:page_content.find("lang=")] + page_content[page_content.find("lang=") + 5
                                                                                    + page_content2.find("|"):]
        else:
            language_code = page_content2[:page_content2.find("}}")]
            page_content = page_content[:page_content.find("lang=")] + page_content[page_content.find("lang=") + 5
                                                                                    + page_content2.find("}"):]

        if language_code == '':
            language_code = foreign_language
        else:
            language_code = get_language_code_by_name(language_code)
    else:
        language_code = foreign_language

    while page_content[:1] == ' ' or page_content[:1] == '|':
        page_content = page_content[1:]
    # Lemme
    if page_content.find(']]') != -1 and page_content.find(']]') < page_content.find('}}'):  # Si on est dans un lien
        lemma_page_name = page_content[:page_content.find(']]')+2]
    elif page_content.find('|') != -1 and page_content.find('|') < page_content.find('}}'):
        lemma_page_name = page_content[:page_content.find('|')]
        # TODO si dièse remplacer en même temps que les language_code ci-dessous, à partir d'un tableau des langues
    else:
        lemma_page_name = page_content[:page_content.find('}}')]
    if lemma_page_name[:2] != '[[':
        lemma_page_name = '[[' + lemma_page_name + ']]'

    if '{' in lemma_page_name or '}' in lemma_page_name or '[' in lemma_page_name or ']' in lemma_page_name \
        or '=' in lemma_page_name:
        if debug_level > 0:
            print('Unsupported source page format')
        return

    # On ne crée que les flexions des lemmes existants
    lemma_page = Page(site, lemma_page_name[2:-2])
    if not lemma_page.exists():
        print('page_content du lemme absente du Wiktionnaire')
        return
    lemma_page_content = get_content_from_page(lemma_page, 'All')
    if lemma_page_content == '':
        return
    if lemma_page_content.find('{{langue|' + language_code + '}}') == -1:
        print(' Paragraphe du lemme absent du Wiktionnaire')
        return
    else:
        # Prononciation
        pron = ''
        lemma_page_content = lemma_page_content[lemma_page_content.find('{{langue|' + language_code + '}}'):]
        if debug_level > 1:
            input(lemma_page_content)

        p = re.compile(r'{{pron\|([^}]+)\|en}}')
        result = p.findall(lemma_page_content)
        if len(result) > 0:
            if debug_level > 0:
                print(' à partir de {{pron}}')
            r = 0
            while result[r] == '' and r < len(result):
                r += 1
            pron = result[r]

        elif lemma_page_content.find('{{en-conj-rég') != -1:
            if debug_level > 0:
                print(' à partir de {{en-conj-rég')
            pron = lemma_page_content[lemma_page_content.find('{{en-conj-rég')+len('{{en-conj-rég'):]
            if pron.find('|inf.pron=') != -1 and pron.find('|inf.pron=') < pron.find('}}'):
                pron = pron[pron.find('|inf.pron=')+len('|inf.pron='):]
                if pron.find('}}') < pron.find('|') or pron.find('|') == -1:
                    pron = pron[:pron.find('}}')]
                else:
                    pron = pron[:pron.find('|')]
            else:
                pron = ''

        if pron != '':
            # Suffixe du -ed
            letter = pron[-1:]
            if letter in ('f', 'k', 'p', 'θ', 's', 'ʃ'):
                pron = pron + 't'
            elif letter in ('t', 'd'):
                pron = pron + 'ɪd'
            else:
                pron = pron + 'd'
        if debug_level > 0:
            print(' prononciation : ' + pron)

    if page_content2.rfind('===') == -1:
        return
    else:
        page_content3 = page_content2[:page_content2.rfind('===')]
        nature = page_content3[page_content3.rfind('===')+3:]
        if debug_level > 1:
            input(nature)
    if nature == 'Noun':
        nature = 'S|nom'
    elif nature == 'Adjective':
        nature = 'S|adjectif'
    elif nature == 'Pronoun':
        nature = 'S|pronom'
    elif nature == 'Verb':
        nature = 'S|verbe'
    else:
        if debug_level > 0:
            print(' Nature inconnue')
        return
    if debug_level > 0:
        print(' nature : ' + nature)

    target_page_content = '== {{langue|' + language_code + '}} ==\n=== {{' + nature + '|' + language_code \
            + '|flexion}} ===\n\'\'\'' + page_name + '\'\'\' {{pron|'+pron+'|' + language_code \
            + '}}\n# \'\'Prétérit de\'\' ' + lemma_page_name + '.\n# \'\'Participe passé de\'\' ' + lemma_page_name + '.\n'
    save_page(target_page, target_page_content, summary)


p = PageProvider(treat_page, site, debug_level)
set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)


def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name('saisie de schéma')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = r''
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
            if len(sys.argv) > 2:
                after_page = sys.argv[2]
            p.pages_by_cat('Catégorie:Python', after_page=after_page)
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
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(update_html_to_unicode(sys.argv[1]))
    else:
        #p.pages_by_cat('Catégorie:Pluriels manquants en français', False, '')
        p.pages_by_cat('Catégorie:Prétérits et participes passés manquants en anglais', False, '')
        # TODO: python3 core/pwb.py touch -lang:fr -family:wiktionary -cat:"Prétérits et participes passés manquants en anglais"


if __name__ == "__main__":
    main(sys.argv)

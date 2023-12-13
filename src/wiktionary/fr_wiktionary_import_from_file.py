#!/usr/bin/env python
# coding: utf-8
"""
Ce script importe les définitions dans le Wiktionnaire depuis un fichier
"""

from __future__ import absolute_import, unicode_literals
import os
import sys
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

debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

language_code = 'fr'
domain = '{{cartographie|' + language_code + '}} '
etymology = ': {{cartographie|nocat=1}} {{sigle|fr}}'
if debug_level > 0:
    reference = '<ref>{{Import:CFC}}</ref>'
else:
    reference = '<ref>{{Import:CFC|relu=non}}</ref>'
summary = 'Importation de définition CFC'
separator = ','
i = {
    'Terme': 0,
    'Terme ancien': 1,
    'Sigle': 2,
    'Terme commercial': 3,
    'Catégorie grammaticale': 4,
    'Définition 1': 5,
    'Domaine 1': 6,
    'Section 1': 7,
    'Synonymes 1': 8,
    'Exemples 1': 9,
    'Termes associés 1': 10,
    'Illustration 1': 11,
    'Commentaires 1': 12,
    'Définition 2': 13,
    'Domaine 2': 14,
    'Section 2': 15,
    'Synonymes 2': 16,
    'Exemples 2': 17,
    'Termes associés 2': 18,
    'Illustration 2': 19,
    'Commentaires 2': 20,
    'Définition 3': 21,
    'Domaine 3': 22,
    'Section 3': 23,
    'Synonymes 3': 24,
    'Exemples 3': 25,
    'Termes associés 3': 26,
    'Illustration 3': 27,
    'Commentaires 3': 28,
}
natures = {'adj.': 'adjectif', 'n.m.': 'nom', 'n.f.': 'nom'}


def treatPage(line):
    regex = r' *(\([^\)]*\)) *'
    line = re.sub(regex, r'', line)
    l = line.split(separator)
    l = map(unicode.strip, l)
    page_name = l[i['Terme']]

    if page_name == '':
        if debug_level > 0:
            print('Ligne vide')
        return
    page_name = page_name.replace('\'', '’')
    print(page_name)

    if l[i['Définition 1']] == '':
        if debug_level > 0:
            print('Définition vide')
        return

    if l[i['Catégorie grammaticale']] == '':
        if debug_level > 0:
            print('Nature vide')
        return
    nature = natures[l[i['Catégorie grammaticale']]]
    natureTemplate = '{{S|' + nature + '|fr'

    if page_name.find('’') != -1:
        page = Page(site, page_name.replace('’', '\''))
        if not page.exists() and page.namespace() == 0:
            if debug_level > 0:
                print('Création d\'une redirection apostrophe')
            save_page(page, f'#REDIRECT[[{page_name}]]', 'Redirection pour apostrophe')
    page = Page(site, page_name)

    definition = f'# {domain}'
    if l[i['Terme ancien']] == 'O':
        definition += '{{vieilli|fr}} '
    if l[i['Section 1']] != '':
        definition += '{{term|' + l[i['Section 1']] + '}} '
    definition += l[i['Définition 1']]
    if definition.count('"') == 1:
        definition = definition.replace('"', '')
    if definition[-1:] == '.':
        definition = definition[:-1]
    definition += reference + '.\n'
    if l[i['Exemples 1']] != '':
        definition += u"#* ''" + l[i['Exemples 1']] + u"''\n"

    if l[i['Définition 2']] != '':
        definition += f'# {domain}'
        if l[i['Terme ancien']] == 'O':
            definition += '{{vieilli|fr}} '
        if l[i['Section 2']] != '':
            definition += '{{term|' + l[i['Section 2']] + '}} '
        definition += l[i['Définition 2']]
        if definition.count('"') == 1:
            definition = definition.replace('"', '')
        if definition[-1:] == '.':
            definition = definition[:-1]
        definition += reference + '.\n'
        if l[i['Exemples 2']] != '':
            definition += u"#* ''" + l[i['Exemples 2']] + u"''\n"

        if l[i['Définition 3']] != '':
            definition += f'# {domain}'
            if l[i['Terme ancien']] == 'O':
                definition += '{{vieilli|fr}} '
            if l[i['Section 3']] != '':
                definition += '{{term|' + l[i['Section 3']] + '}} '
            definition += l[i['Définition 3']]
            if definition.count('"') == 1:
                definition = definition.replace('"', '')
            if definition[-1:] == '.':
                definition = definition[:-1]
            definition += reference + '.\n'
            if l[i['Exemples 3']] != '':
                definition += u"#* ''" + l[i['Exemples 3']] + u"''\n"
    definition = definition.replace('  ', ', ')

    current_page_content = get_content_from_page(page, 'All')
    page_content = current_page_content
    final_page_content = ''

    if current_page_content is None:
        if debug_level > 0:
            print(' page_content vide : création')
        page_content = '== {{langue|fr}} ==\n' + '=== {{S|étymologie}} ===\n'
        page_content += '{{ébauche-étym|fr}}\n'
        if l[i['Sigle']] == 'O':
            page_content += etymology + '\n'
        page_content += '\n'
        page_content += f'=== {natureTemplate}' + '}} ===\n'
        page_content += u"'''{{subst:PAGENAME}}'''"
        if l[i['Catégorie grammaticale']][-2:] == 'm.':
            page_content += ' {{m}}'
        if l[i['Catégorie grammaticale']][-2:] == 'f.':
            page_content += ' {{f}}'
        page_content += ' {{pluriel ?|fr}}\n' + definition
        if l[i['Synonymes 1']] != '':
            page_content += '\n==== {{S|synonymes}} ====\n'
            synonyms = l[i['Synonymes 1']].split(';')
            for s in synonyms:
                page_content += f'* [[{trim(s)}' + ']]\n'
            if l[i['Synonymes 2']] != '':
                synonyms = l[i['Synonymes 2']].split(';')
                for s in synonyms:
                    page_content += f'* [[{trim(s)}' + ']] (2)\n'
        elif l[i['Synonymes 2']] != '':
            synonyms = l[i['Synonymes 2']].split(';')
            for s in synonyms:
                page_content += f'* [[{trim(s)}' + ']] (2)\n'
        if l[i['Termes associés 1']] != '':
            page_content += '\n==== {{S|vocabulaire}} ====\n'
            terms = l[i['Termes associés 1']].split(';')
            for t in terms:
                print(t)
                page_content = add_line(
                    page_content,
                    language_code,
                    'vocabulaire',
                    f'* [[{trim(t)}]]',
                )
        page_content += '\n==== {{S|traductions}} ====\n'
        page_content += '{{trad-début}}\n'
        page_content += '{{trad-fin}}\n'
        page_content += '\n=== {{S|références}} ===\n'
        page_content += '{{Références}}\n'

        save_page(page, page_content, summary)
        return

    if current_page_content.find(domain) != -1 or current_page_content.find('{{Import:CFC') != -1 or \
            page_name in ['cahier', 'couleurs complémentaires', 'demi-teintes', 'droits d’auteur']:
        if debug_level > 0:
            print(' Définition déjà présente')
        return

    if l[i['Sigle']] == 'O':
        page_content = add_line(
            page_content, language_code, 'étymologie', etymology)
    page_content = add_line(page_content, language_code, nature, definition)
    if l[i['Synonymes 1']] != '':
        synonyms = l[i['Synonymes 1']].split(';')
        for s in synonyms:
            page_content = add_line(
                page_content,
                language_code,
                'synonymes',
                (f'* [[{trim(s)}' + ']] {{cartographie|nocat=1}} (1)'),
            )
    if l[i['Synonymes 2']] != '':
        synonyms = l[i['Synonymes 2']].split(';')
        for s in synonyms:
            page_content = add_line(
                page_content,
                language_code,
                'synonymes',
                (f'* [[{trim(s)}' + ']] {{cartographie|nocat=1}} (2)'),
            )
    if l[i['Termes associés 1']] != '':
        terms = l[i['Termes associés 1']].split(';')
        for t in terms:
            page_content = add_line(
                page_content,
                language_code,
                'vocabulaire',
                (f'* [[{trim(t)}' + ']] {{cartographie|nocat=1}}'),
            )
    page_content = add_line(page_content, language_code,
                            'références', '{{Références}}')

    final_page_content = page_content.replace('\n\n\n', '\n\n')
    if final_page_content != current_page_content:
        save_page(page, final_page_content, summary)


set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)


def main(*args) -> int:
    from lib import html2unicode
    with open(f'lists/articles_{site_language}_{site_family}_CFC.csv', 'r') as pagesList:
        while 1:
            line = pagesList.readline().decode(config.console_encoding, 'replace')
            fin = line.find("\t")
            line = line[:fin]
            if line == '':
                break
            # Conversion ASCII => Unicode (pour les .txt)
            treatPage(update_html_to_unicode(line))
    return 0


if __name__ == "__main__":
    main(sys.argv)

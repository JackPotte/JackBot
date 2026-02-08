#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le serveur Toolforge de Wikimedia :
1) Crée les redirections d'apostrophe dactylographique vers apostrophe typographique.
2) Gère des modèles {{voir}} en début de page.
3) Retire certains doublons de modèles et d'espaces.
4) Remplace les modèles catégorisés comme désuets.
5) Ajoute les prononciations sur la ligne de forme, et certains liens vers les conjugaisons.
6) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
7) Détecte les modèles de contexte à ajouter, et ajoute leurs codes langues ou "nocat=1"
8) Complète la boite de flexions de verbes en français.
9) Demande les pluriels et genres manquants quand les lemmes les éludent.
10) Ajoute certaines sections traductions manquantes.
11) Ajoute les anagrammes (pour les petits mots faute de vitesse réseau).
etc.
Tests sur http://fr.wiktionary.org/w/index.php?title=Utilisateur%3AJackBot%2Ftest&diff=14533806&oldid=14533695
"""

from __future__ import absolute_import, unicode_literals
import os
import re
import sys
import pywikibot
from pywikibot import config, Page

# JackBot
dir_wt = os.path.dirname(__file__)
dir_src = os.path.dirname(dir_wt)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
#from src.lib import get_content_from_page_name, update_html_to_unicode, get_site_by_file_name
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

days_before_archiving = True
force_aliases = ['-force', '-f']
for force_alias in force_aliases:
    if force_alias in sys.argv:
        days_before_archiving = False
        sys.argv.remove(force_alias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

do_check_url = False
fix_tags = False  # TODO set it from an arg & add edition summary
fix_files = True
fix_old_templates = False
add_default_sort_key = False
treat_templates = False
treat_categories = True
treat_appendix = True
fix_genders = True
fix_false_inflexions = False
do_list_homophones = False
fix_translations = True
list_false_translations = False
test_import = False
output_file = 'dumps/wiktionary-fr.txt'
blacklisted_pages = ['t’kuni']
cancel_user = {} # TODO move to its own file


def treat_page_by_name(page_name):
    if page_name in blacklisted_pages:
        return

    page = Page(site, page_name)
    return treat_page(page)


def treat_page(page):
    global debug_level
    if debug_level > 0:
        print('------------------------------------')
    page_name = page.title()
    pywikibot.output(f"\n\03<<blue>>{page_name}\03<<default>>")

    summary = '[[Wiktionnaire:Structure des articles|Autoformatage]]'
    if page_name[-3:] == '.js' or page_name[-4:] == '.css':
        return
    if page_name.find('’') != -1:
        redir_page = Page(site, page_name.replace('’', '\''))
        if not redir_page.exists() and redir_page.namespace() == 0:
            if debug_level > 0:
                print('Création d\'une redirection apostrophe')
            save_page(redir_page, '#REDIRECT[[' + page_name + ']]',
                      'Redirection pour apostrophe', is_minor=True)

    if debug_level == 0 and days_before_archiving and (page_name.find('<') != -1 or not has_more_than_time(page)):
        return

    current_page_content = get_content_from_page(page, 'All')
    if current_page_content is None:
        if debug_level > 0:
            print(' page_content vide')
        return

    if cancel_user != {}:
        page_content, summary = cancel_edition(page, cancel_user)
        # a page reset is needed to edit the last version
        page = Page(site, page_name)
        if page_content not in ['', current_page_content]:
            save_page(page, page_content, summary)
        return

    page_content = current_page_content
    final_page_content = ''
    regex_page_name = re.escape(page_name)

    page_content = global_operations(page_content)
    if fix_files:
        page_content = replace_files_errors(page_content)
    if fix_tags:
        page_content = replace_deprecated_tags(page_content)
    if do_check_url:
        page_content, summary = treat_broken_links(page_content, summary)

    if treat_categories and page.namespace() == 14:
        if debug_level > 0:
            print(' category treatment')
        page_content = page_content.replace('[[Catégorie:Date manquante', '[[Catégorie:Dates manquantes')
        final_page_content = page_content

    elif treat_templates and page.namespace() == 10:
        if debug_level > 0:
            print(' template treatment')
        templates_to_treat = ['emploi', 'région',
                              'régional', 'registre', 'term']
        for template in templates_to_treat:
            if '{{{clé|' not in page_content and page_content[:len('{{' + template)] == '{{' + template \
                    and '\n}}<noinclude>' in page_content:
                summary = '[[Wiktionnaire:Wikidémie/juillet_2017#Pour_conclure_Wiktionnaire:Prise_de_d.C3.A9cision.2FCl.C3.A9s_de_tri_fran.C3.A7aises_par_d.C3.A9faut|Clé de tri]]'
                page_content = page_content[:page_content.find('\n}}<noinclude>')] + '\n|clé={{{clé|}}}' \
                    + page_content[page_content.find('\n}}<noinclude>'):]

        regex = r'<includeonly> *\n*{{\#if(eq)?: *{{NAMESPACE}}[^<]+\[\[Catégorie:Wiktionnaire:Utilisation d’anciens modèles de sections[^<]+</includeonly>'
        if re.search(regex, page_content):
            page_content = re.sub(regex, '{{anciens modèles de section}}', page_content, re.MULTILINE)
        if debug_level > 1:
            input(page_content)

        final_page_content = page_content

    elif treat_appendix and page.namespace() == 100:
        rime_page = r'Annexe:Rimes en français en '
        if rime_page in page_name \
                and not '{{-rimes-' in page_content \
                and not '[[Catégorie:Rimes en français' in page_content:
            rime = re.sub(rime_page, '', page_name)
            rime = re.sub(r'[/\\]', '', rime)
            if rime == '':
                print('rime vide')
                return
            page_content += '\n\n[[Catégorie:Rimes en français|' + rime + ']]'
            final_page_content = page_content
        else:
            return

    elif page.namespace() == 0 or username in page_name:
        regex = r'{{(formater|SI|supp|supprimer|PàS)[\|}]'
        if re.search(regex, page_content):
            if debug_level > 0:
                print('page_content en travaux : non traitée')
            return

        if do_list_homophones:
            language_section, homophones_start, homophones_end = get_language_section(page_content, 'fr')
            if language_section is not None:
                homophones, homophones_start, homophones_end = getSection(language_section, 'homophones')
                if debug_level > 1:
                    input(homophones)
                output_file.write((homophones.replace('==== {{S|homophones|fr}} ====\n', '').replace(
                    '=== {{S|homophones|fr}} ===\n', '')))
            return

        page_content, summary = add_banner_see(page_name, page_content, summary)
        page_content, summary = format_sections(page_content, summary)
        page_content = replace_title_templates(page_content)
        page_content, summary = format_titles(page_content, summary)
        page_content, summary = format_templates(page_content, summary)
        page_content, summary = format_wikicode(page_content, summary, page_name)
        page_content, summary = add_templates(page_content, summary)
        page_content, summary = move_templates(page_content, summary)
        page_content, summary = replace_templates(page_content, summary)
        page_content, summary = remove_double_category_when_template(page_content, summary)
        page_content, summary = format_categories(page_content, summary)
        page_content, summary = format_languages_templates(page_content, summary, page_name)

        if fix_translations:
            page_content, summary = format_translations(page_content, summary)
            page_content, summary = sort_translations(page_content, summary)
        if add_default_sort_key:
            # TODO: compare the Lua with ", empty = True"
            page_content = add_default_sort(page_name, page_content)
        page_content, summary = add_appendix_links(page_content, summary, page_name)

        singular_page_name = ''
        if '{{langue|fr}}' in page_content:
            page_content, summary, singular_page_name = format_fr_section(page_content, summary, page_name, regex_page_name)

        # Post pre-processing treatments
        final_page_content, summary, infinitive = add_languages_codes_to_each_template(
            page_content,
            summary,
            page_name,
            final_page_content,
            fix_translations,
            fix_old_templates,
            site_family,
            current_page_content,
        )

        final_page_content, summary = treat_genders_and_numbers(
            final_page_content,
            summary,
            fix_genders,
            fix_false_inflexions,
            singular_page_name,
            page_name,
        )

        final_page_content, summary = check_false_homophones(
            final_page_content,
            summary,
            page_name,
            infinitive,
            singular_page_name,
        )

        regex = r'\n\* *{{Annexe\|Proverbes en français}} *'
        if re.search(regex, final_page_content):
            final_page_content = re.sub(regex, r'', final_page_content)

        regex = r'([^\n=])(===?=? *{{S\|)'
        if re.search(regex, final_page_content):
            final_page_content = re.sub(regex, r'\1\n\n\2', final_page_content)

    else:
        # Unknown namespace
        final_page_content = page_content

    # Post-processing fix
    final_page_content = final_page_content.replace('|lanɡ=', '|lang=')
    regex = r'({{pron)(\|lang=[a-zA-Z]{2,3})(\|[a-zA-Z]{2,3}}})'
    if re.search(regex, final_page_content):
        final_page_content = re.sub(regex, r'\1|\3', final_page_content)

    if test_import and username in page_name:
        final_page_content = add_line_test(final_page_content)
    if debug_level > 0:
        pywikibot.output("\n\03<<red>>---------------------------------------------\03<<default>>")
    if final_page_content != current_page_content:
        if page.namespace() == 0 or username in page_name:
            # Modifications mineures, ne justifiant pas une édition à elles seules
            final_page_content = final_page_content.replace('  ', ' ')
            regex = r'\n+(\n\n=* {{S\|)'
            final_page_content = re.sub(regex, r'\1', final_page_content)
            final_page_content = final_page_content.replace('\n\n\n\n', '\n\n\n')
            final_page_content = final_page_content.replace('.\n=', '.\n\n=')
            regex = r'(\])(\n== {{langue\|)'
            final_page_content = re.sub(regex, r'\1\n\2', final_page_content)
        save_page(page, final_page_content, summary)
    elif debug_level > 0:
        print('Aucun changement après traitement')


def format_fr_section(page_content, summary, page_name, regex_page_name):
    if debug_level > 0:
        print('\nformat_fr_section()')
    language_code = 'fr'
    natures_with_plural = ['nom', 'adjectif', 'suffixe']

    regex = r'(=== {{S\|nom\|' + language_code + r')\|flexion(}} ===\n(?:{{' + language_code + r"[^\n]*\n)*'''" \
            + regex_page_name + r"''' [^\n]*{{fsing}})"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
        summary = summary + ', un nom féminin n\'est pas une flexion en français'
    regex = r'(=== {{S\|nom\|' + language_code + r')\|flexion(}} ===\n(?:{{' + language_code + r"[^\n]*\n)*'''" \
            + regex_page_name + \
        r"''' [^\n]*{{f}}\n# *'*[Ff]éminin (?:de|singulier))"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
        summary = summary + ', un nom féminin n\'est pas une flexion en français'

    singular_page_name = ''
    if page_name.find('*') == -1 and page_name[-1:] == 's':
        singular_page_name = get_lemma_from_plural(page_content, language_code, natures_with_plural)
        if singular_page_name != '':
            # TODO cannot move this recursive function in the dedicated used module (circular dependency)?
            # Formatage des boites de flexion à récupérer
            treat_page_by_name(singular_page_name)
        page_content, summary = treat_noun_inflexion(
            page_content,
            summary,
            page_name,
            regex_page_name,
            natures_with_plural,
            language_code,
            singular_page_name
        )

    if debug_level > 0:
        print(' Missing translations')
    # Si la définition du mot (dit "satellite") ne renvoie pas vers un autre, les centralisant
    # TODO: # Variante,
    regex = (
        f'({language_code}'
        + r'\|flexion|'
        + '|'.join(definition_sentences)
        + '|'.join(map(lambda x: x.capitalize(), definition_sentences))
    ) + r')'
    regex2 = r'{{(formater|SI|supp|supprimer|PàS|S\|erreur|S\|faute|S\|traductions|' + \
             '|'.join(etymology_templates) + r')[\|}]'
    fr_section, language_start, language_end = get_language_section(page_content, language_code)
    if fr_section is not None and re.search(regex, fr_section) is None and re.search(regex2, fr_section) is None and \
            count_first_definition_size(fr_section) > 3:
        summary = summary + ', ajout de {{S|traductions}}'
        page_content = add_line(page_content, 'fr', 'traductions', '{{trad-début}}\n{{trad-fin}}')
    # Cosmetic fix
    regex = r'(==== {{S\|traductions}} ====\n)\n* *\n*({{trad\-début)'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
    regex = r'({{trad\-fin}}\n)([^\n])'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\n\2', page_content)
    return page_content, summary, singular_page_name


p = PageProvider(treat_page, site, debug_level)
set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)


def main(*args) -> int:
    global days_before_archiving, fix_old_templates, output_file, site_language, site_family, fix_tags, \
        list_false_translations, test_import, cancel_user
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        after_page = sys.argv[2] if len(sys.argv) > 2 else ''
        if sys.argv[1] in ['-test', '-t']:
            treat_page_by_name(f'User:{username}/test')
        elif sys.argv[1] == ['-test-import', '-ti']:
            test_import = True
            treat_page_by_name(f'User:{username}/test')
        elif sys.argv[1] in ['-page', '-p']:
            wait_after_humans = False
            treat_page_by_name('Annexe:Rimes_en_français_en_/sɑ̃/')
        elif sys.argv[1] == '-start':
            if len(sys.argv) > 2:
                p.pages_by_prefix(sys.argv[2])
            else:
                p.pages_by_prefix('Annexe:Rimes en français en ', namespace=100)
        elif sys.argv[1] in ['-file', '-txt']:
            wait_after_humans = False
            file_name = f'lists/articles_{site_language}_{site_family}.txt'
            if debug_level > 0:
                print(file_name)
            p.pages_by_file(file_name)
        elif sys.argv[1] in ['-dump', '-xml', '-regex']:
            dump_file = site_language + site_family + r'\-.*xml'
            if len(sys.argv) > 2:
                regex = sys.argv[2]
            else:
                regex = r"/\{\{S\|prononciation\}\}(?!\{\{langue).*\{\{S\|prononciation\}\}/"
            test_page = sys.argv[3] if len(sys.argv) > 3 else None
            if test_page is not None:
                page_content = get_content_from_page_name(test_page, site)
                if page_content is not None and re.search(regex, page_content, re.DOTALL):
                    print('Traitement...')
                else:
                    print('Pas de traitement.')
            else:
                p.page_by_xml(dump_file, regex=regex, namespaces=0)
        elif sys.argv[1] == '-u':
            targeted_user = sys.argv[2] if len(sys.argv) > 2 else username
            if len(sys.argv) > 3:
                cancel_user['user'] = targeted_user
                cancel_user['action'] = sys.argv[3]
            number = sys.argv[4] if len(sys.argv) > 4 else 1000
            p.pages_by_user(
                f'User:{targeted_user}',
                number_of_pages_to_treat=number,
                namespaces=[0],
            )
        elif sys.argv[1] in ['-search', '-s', '-r']:
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search(r'insource:/\}==* \{\{S\|/', namespaces=[0])

        elif sys.argv[1] in ['-link', '-l', '-template', '-m']:
            if len(sys.argv) > 2:
                p.pages_by_link(sys.argv[2], namespaces=[0])
            else:
                p.pages_by_link('Annexe:Proverbes en français', namespaces=[0])
        elif sys.argv[1] in ['-category', '-cat', '-c']:
            if len(sys.argv) > 2:
                if sys.argv[2] == 'listFalseTranslations':
                    list_false_translations = True
                    p.pages_by_cat('Catégorie:Pages "info" si réforme 1895 de l’espéranto')
                elif sys.argv[2] == 'fixOldTemplates':
                    fix_old_templates = True
                    p.pages_by_cat(
                        'Appels de modèles incorrects:abréviation',
                        after_page=after_page,
                        recursive=False,
                        namespaces=[14]
                    )
                else:
                    p.pages_by_cat(sys.argv[2])
            else:
                p.pages_by_cat(
                    'Expressions en sicilien',
                    namespaces=None,
                    recursive=False
                )

        elif sys.argv[1] == '-redirects':
            p.pages_by_redirects()
        elif sys.argv[1] == '-all':
            p.pages_by_all()
        elif sys.argv[1] in ['-rc', '-RC']:
            while 1:
                # p.pages_by_rc() TODO error with self in context
                p.pages_by_rc_last_day()
        elif sys.argv[1] == '-nocat':
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == '-lint':
            fix_tags = True
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p.pages_by_special_link_search('www.dmoz.org')
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            try:
                treat_page_by_name(update_html_to_unicode(sys.argv[1]))
            except UnicodeDecodeError:
                print(' page à décoder')
                treat_page_by_name(sys.argv[1].decode(config.console_encoding, 'replace'))
            except UnicodeEncodeError:
                print(' page à encoder')
                treat_page_by_name(sys.argv[1])
    else:
        # Nightly treatment:
        p.pages_by_cat(
            'Catégorie:Wiktionnaire:Codes langue manquants',
            recursive=True,
            # TODO
            exclude=[
                'Catégorie:Wiktionnaire:Régionalismes sans langue précisée',
            ]
        )
        #p.pages_by_cat('Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet')

        p.pages_by_cat('Catégorie:Wiktionnaire:Flexions à vérifier', recursive=True)
        p.pages_by_cat('Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée')
        p.pages_by_cat('Catégorie:Appels de modèles incorrects:deet')

        for old_template in old_templates:
            p.pages_by_link(f'Template:{old_template}', namespaces=[0])

        p.pages_by_link('Template:liaison')
        p.pages_by_link('Template:ucf')
        p.pages_by_link('Template:msing')
        p.pages_by_link('Template:fsing')
        p.pages_by_link('Template:nsing')
        p.pages_by_link('Template:mplur')
        p.pages_by_link('Template:fplur')
        p.pages_by_link('Template:nplur')

        p.pages_by_link('Template:1ergroupe')
        p.pages_by_link('Template:2egroupe')
        p.pages_by_link('Template:3egroupe')

        p.pages_by_link('Template:=langue=')

        p.pages_by_cat('Catégorie:Traduction en français demandée d’exemple(s) écrits en français')
        p.pages_by_cat('Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section')
        p.pages_by_cat('Catégorie:Wiktionnaire:Sections avec paramètres superflus')
        p.pages_by_cat('Catégorie:Wiktionnaire:Sections utilisant un alias')

        p.pages_by_search(r'insource:/\}==== \{\{S\|/', namespaces=[0])
        p.pages_by_search(r'insource:/\}=== \{\{S\|/', namespaces=[0])

    return 0


if __name__ == "__main__":
    main(sys.argv)

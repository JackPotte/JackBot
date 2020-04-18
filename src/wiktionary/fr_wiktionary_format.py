#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le serveur Toolforge de Wikimedia :
1) Crée les redirection d'apostrophe dactylographique vers apostrophe typographique.
2) Gère des modèles {{voir}} en début de page.
3) Retire certains doublons de modèles et d'espaces.
4) Remplace les modèles catégorisés comme désuets.
5) Ajoute les prononciations sur la ligne de forme, et certains liens vers les conjugaisons.
6) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
7) Détecte les modèles de contexte à ajouter, et ajoute leurs codes langues  ou "nocat=1"
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
debug_aliases = [str('-debug'), str('-d')]
for debug_alias in debug_aliases:
    if debug_alias in sys.argv:
        debug_level = 1
        sys.argv.remove(debug_alias)

wait_after_humans = True
force_aliases = [str('-force'), str('-f')]
for force_alias in force_aliases:
    if force_alias in sys.argv:
        wait_after_humans = False
        sys.argv.remove(force_alias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

do_check_url = False
fix_tags = False  # TODO passage en arg + résumé d'édition
fix_files = True
fix_old_templates = False
add_default_sort_key = False
all_namespaces = False
treat_templates = False
treat_categories = True
fix_genders = True
fix_false_inflexions = False
do_list_homophons = False
do_fix_translations = True
list_false_translations = False
test_import = False
cancel_user = {}
output_file = ''
anagrams_max_length = 4  # TODO: from dump otherwise 5 chars > 5 min & 8 chars > 1 h per page)


def treat_page_by_name(page_name):
    global debug_level
    summary = '[[Wiktionnaire:Structure des articles|Autoformatage]]'
    if debug_level > 0:
        print('------------------------------------')
    pywikibot.output("\n\03{blue}" + page_name + u"\03{default}")
    if page_name[-3:] == '.js' or page_name[-4:] == '.css':
        return
    if page_name.find('’') != -1:
        page = Page(site, page_name.replace('’', '\''))
        if not page.exists() and page.namespace() == 0:
            if debug_level > 0:
                print('Création d\'une redirection apostrophe')
            save_page(page, '#REDIRECT[[' + page_name + ']]', 'Redirection pour apostrophe', minor_edit=True)

    page = Page(site, page_name)
    if debug_level == 0 and wait_after_humans and (page_name.find('<') != -1 or not has_more_than_time(page)):
        return

    current_page_content = get_content_from_page(page, 'All')
    if current_page_content is None:
        if debug_level > 0:
            print(' page_content vide')
        return

    if cancel_user != {}:
        page_content, summary = cancel_edition(page, cancel_user)
        page = Page(site, page_name)  # a page reset is needed to edit the last version
        if page_content != '' and page_content != current_page_content:
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
        templates_to_treat = ['emploi', 'région', 'registre', 'term']
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

    elif page.namespace() == 0 or username in page_name:
        regex = r'{{(formater|SI|supp|supprimer|PàS)[\|}]'
        if re.search(regex, page_content):
            if debug_level > 0:
                print('page_content en travaux : non traitée')
            return

        if do_list_homophons:
            language_section, homophons_start, homophons_end = get_language_section(page_content, 'fr')
            if language_section is not None:
                homophons, homophons_start, homophons_end = getSection(language_section, 'homophones')
                if debug_level > 1:
                    input(homophons)
                output_file.write((homophons.replace('==== {{S|homophones|fr}} ====\n', '').replace(
                    '=== {{S|homophones|fr}} ===\n', '')))
            return

        page_content, summary = add_banner_see(page_name, page_content, summary)
        page_content, summary = format_sections(page_content, summary)

        if debug_level > 0:
            print(' {{S}} conversion and formatting')
        equals_in_section = '==='
        for p in range(1, limit4):
            if debug_level > 1:
                print(templates[p] + r'|S\|' + sections[p])
            if p == limit2:
                equals_in_section = '===='
            if p == limit3:
                equals_in_section = '====='
            if debug_level > 1:
                print(p, templates[p], sections[p])
            regex = r'[= ]*{{[\-loc]*(' + templates[p] + r'|S\|' + sections[p] + r')([^}]*)}}[= ]*\n'
            if re.search(regex, page_content):
                if debug_level > 1:
                    print(' {{S| : check des niveaux de section 1 : ') + sections[p] + ' ' + equals_in_section
                page_content = re.sub(regex, equals_in_section + r' {{S|' + sections[p] + r'\2}} ' +
                                      equals_in_section + '\n', page_content)

            regex = r'[= ]*{{\-flex[\-loc]*(' + templates[p] + r'|S\|' + sections[p] + r')\|([^}]*)}}[= ]*\n'
            if re.search(regex, page_content):
                if debug_level > 1:
                    print(' {{S| : check des niveaux de section 2 : ') + sections[p]
                page_content = re.sub(regex, equals_in_section + r' {{S|' + sections[p] + r'|\2|flexion}} ' +
                                      equals_in_section + '\n', page_content)

            if limit1 < p < limit3 - 1:
                regex = r'({{S\|' + sections[p] + r')\|[a-z]+}}'
                if debug_level > 1:
                    print(' {{S| : retrait de code langue')
                page_content = re.sub(regex, r'\1}}', page_content)

        page_content, summary = format_templates(page_content, summary)
        page_content, summary = format_wikicode(page_content, summary, page_name)
        page_content, summary = add_templates(page_content, summary)
        page_content, summary = rename_templates(page_content, summary)
        page_content, summary = remove_double_category_when_template(page_content, summary)
        page_content, summary = format_categories(page_content, summary)
        page_content, summary = format_languages_templates(page_content, summary, page_name)
        if do_fix_translations:
            page_content, summary = format_translations(page_content, summary)
            page_content, summary = sort_translations(page_content, summary)
        if add_default_sort_key:
            page_content = add_default_sort(page_name, page_content)  # TODO: compare the Lua with ", empty = True"
        page_content, summary = add_appendix_links(page_content, summary, page_name)

        if '{{langue|fr}}' in page_content:
            page_content, summary = format_fr_section(page_content, summary, page_name, regex_page_name)

        if debug_level > 0:
            print(' Languages in templates checking')
        add_language_code = False  # Some sections can contain uncategorizing domain templates
        if debug_level > 1:
            print('  add_language_code = ') + str(add_language_code)
        has_translation_section = False
        go_backward = False  # Some templates need to be moved and retreated
        language_code = None
        if debug_level > 1:
            print('  language_code = None')
        start_position = 1
        singular_page_name = ''
        infinitive = ''
        # Loop to find each page template, filling final_page_content by emptying page_content
        while start_position > -1:
            if debug_level > 1:
                pywikibot.output("\n\03{red}---------------------------------------------------\03{default}")
                print(final_page_content[:1000])
                input(page_content[:1000])
                pywikibot.output("\n\03{red}---------------------------------------------------\03{default}")
                if language_code is None:
                    print(' loop start with no language')
                else:
                    print(' loop start with language: ' + language_code)

            start_position = page_content.find('{{')
            if start_position < 0:
                break
            final_page_content = final_page_content + page_content[:start_position + 2]
            page_content = page_content[start_position + 2:]
            if page_content.find("|") > page_content.find('}}'):
                end_position = page_content.find('}}')
            elif page_content.find("|") == -1:
                end_position = page_content.find('}}')
            else:
                end_position = page_content.find("|")
            current_template = page_content[:end_position]

            if not go_backward:
                if debug_level > 1:
                    message = ' Remplacement de \x1b[6;31;40m{{' + page_content[
                                                                   :page_content.find('}}') + 2] + '\x1b[0m'
                    print(message)
            else:
                if debug_level > 1:
                    print(' Retour en arrière')
                    pywikibot.output("\n\03{red}---------------------------------------------------\03{default}")
            go_backward = False

            if current_template in templates:
                p = templates.index(current_template)
                if debug_level > 0:
                    pywikibot.output(' \03{yellow}' + current_template + '\03{default} (' + str(p) + ')')

                # Missing language section
                if not language_code and (p < limit1 or p >= limit6) and current_template != 'ébauche':
                    if debug_level > 0:
                        print(' page_content to format manually')
                    final_page_content = '{{formater|Section de langue manquante, avant le modèle ' \
                                         + current_template + ' (au niveau du ' + str(len(final_page_content)) \
                                         + '-ème caractère)}}\n' + final_page_content + page_content
                    summary = 'page_content à formater manuellement'
                    save_page(page, final_page_content, summary)
                    return

                elif current_template == 'caractère':
                    language_code = 'conv'
                    add_language_code = False
                    if debug_level > 0:
                        print(' add_language_code = ') + str(add_language_code)
                    final_page_content, page_content = next_template(final_page_content, page_content)

                elif current_template == 'langue':
                    language_code = page_content[end_position + 1:page_content.find('}}')]
                    if language_code == '':
                        if debug_level > 0:
                            print('  empty language code')
                        return
                    if debug_level > 1:
                        print('  language found: ') + language_code
                    regex = r'[a-zA-Z\-]+'
                    if not re.search(regex, language_code):
                        final_page_content = '{{formater|Code langue incorrect : ' + language_code + '}}\n' \
                                             + final_page_content + page_content
                        summary = 'page_content à formater manuellement'
                        save_page(page, final_page_content, summary)
                        if debug_level > 0:
                            print(' page_content to format manually')
                        return
                    add_language_code = True

                    # Ajout des anagrammes pour cette nouvelle langue détectée
                    if language_code == 'conv':
                        regex = r'[= ]*{{S\|anagrammes}}[^}]+\|conv}}\n'
                        if re.compile(regex).search(page_content):
                            if debug_level > 0:
                                print(' No anagram for {{conv}}')
                            final_page_content2 = page_content[:re.compile(regex).search(page_content).start()]
                            page_content2 = page_content[re.compile(regex).search(page_content).end():]
                            delta = re.compile(regex).search(page_content).end()
                            regex = r'[^}]+\|conv}}\n'
                            while re.compile(regex).search(page_content2):
                                if debug_level > 0:
                                    print(' No anagram for {{conv}}')
                                delta = delta + re.compile(regex).search(page_content2).end()
                                page_content2 = page_content2[re.compile(regex).search(page_content2).end():]
                            page_content = final_page_content2 + page_content[delta:]

                    elif debug_level == 0 and page_content.find('S|erreur|' + language_code) == -1 and \
                            page_content.find('S|faute|' + language_code) == -1 and language_code != 'conv' and \
                            page_name[:1] != '-' and page_name[-1:] != '-' and ':' not in page_name:

                        if debug_level > 0:
                            print(' Anagrams for ') + language_code
                        if page_content.find('{{S|anagr') == -1 and page_name.find(' ') == -1 and len(
                                page_name) <= anagrams_max_length:
                            page_content, summary = add_anagrams(page_content, summary, page_name, language_code)
                    final_page_content, page_content = next_template(final_page_content, page_content)

                # Sections
                elif current_template == 'S':
                    section = trim(page_content[end_position + 1:page_content.find('}}')])
                    if section.find('|') != -1:
                        section = trim(section[:section.find('|')])
                    if section not in sections:
                        if debug_level > 0:
                            pywikibot.output("\03{yellow} S\03{default}: with unknown section " + section)
                        final_page_content, page_content = next_template(final_page_content, page_content)
                        break
                    if debug_level > 0:
                        pywikibot.output("\03{yellow} S\03{default}: with known section " + section)

                    if sections.index(section) < limit1:
                        if debug_level > 1:
                            print(' Definition paragraph')
                        add_language_code = True  # Paragraphe avec code langue dans les modèles lexicaux
                        has_translation_section = False

                        if language_code is None:
                            # TODO: gérer les {{S|étymologie}} en milieu d'article
                            language_code = page_content[
                                            end_position + 1 + len(section) + 1:page_content.find('}}')].replace(
                                '|flexion', '')  # TODO: num=, genre=...
                            summary = summary + ' ajout du {{langue|' + language_code + '}} manquant'
                            page_content = '== {{langue|' + language_code + '}} ==\n' + final_page_content[
                                                                                        final_page_content.find(
                                                                                            '==='):] + page_content
                            final_page_content = final_page_content[:final_page_content.find('===')]
                            go_backward = True
                            break

                        if page_content.find(language_code) == -1 or \
                                page_content.find(language_code) > page_content.find('}}'):
                            page_content = page_content[:end_position + 1 + len(section)] + '|' + language_code \
                                           + page_content[page_content.find('}}'):]

                        # Tous ces modèles peuvent facultativement contenir |clé= et |num=, et |genre= pour les prénoms, voire locution=
                        if page_content.find('|clé=') == -1 or page_content.find('|clé=') > page_content.find('}}'):
                            if debug_level > 1:
                                print('  ' + str(p))  # eg: 0 for {{S}}
                            if debug_level > 1:
                                print('  ' + str(sections.index(section)))  # eg: 40 for "nom"
                            if debug_level > 1:
                                print('  ' + page_content[:page_content.find('}}')])  # eg: S|nom|sv|flexion

                            temp_page_name = default_sort_by_language(page_name, language_code)
                            if temp_page_name != page_name:
                                if debug_level > 0:
                                    print(' "|clé="')
                                temp_page_name = sort_by_encoding(temp_page_name)
                                page_content = page_content[:page_content.find('}}')] + '|clé=' + temp_page_name + \
                                                page_content[page_content.find('}}'):]

                    else:
                        add_language_code = False  # Paragraphe sans code langue dans les modèles lexicaux et les titres
                        has_translation_section = False

                        if section == 'homophones':
                            if debug_level > 0:
                                print(' Homophons categorization')
                            section_title = page_content[:page_content.find('}}')]
                            if section_title.rfind('|') > len(section):
                                page_content = section_title[:section_title.rfind('|')] + '|' + \
                                               language_code + page_content[page_content.find('}}'):]
                            else:
                                page_content = page_content[:page_content.find('}}')] + '|' + \
                                               language_code + page_content[page_content.find('}}'):]

                        if section == 'traductions' and language_code == 'fr':
                            has_translation_section = True
                            regex = r'{{S\|traductions}} *=*\n(\n|\:?\*? *({{cf|[Vv]oir))'
                            if not re.search(regex, page_content):
                                # Ajout de {{trad-début}} si {{T| en français (mais pas {{L| car certains les trient par famille de langue)
                                for t in ['T', 'ébauche-trad']:
                                    if page_content.find('{{') == page_content.find('{{' + t + '|'):
                                        if debug_level > 0:
                                            print('  {{trad-début}} addition')
                                        if page_content.find('\n') == -1: page_content = page_content + '\n'
                                        page_content = page_content[:page_content.find('\n')] + '\n{{trad-début}}' + \
                                            page_content[page_content.find('\n'):]
                                        page_content2 = page_content[page_content.find('{{trad-début}}\n') + len(
                                            '{{trad-début}}\n'):]
                                        while page_content2.find('{{' + t + '|') < page_content2.find('\n') and \
                                                page_content2.find('{{' + t + '|') != -1:
                                            page_content2 = page_content2[page_content2.find('\n') + 1:]
                                        if debug_level > 0:
                                            print('  {{trad-fin}} addition')
                                        page_content = page_content[:len(page_content) - len(page_content2)] + \
                                            '{{trad-fin}}\n' + page_content[len(page_content) - len(page_content2):]
                            if debug_level > 2:
                                input(page_content)
                        elif section == 'traductions à trier':
                            has_translation_section = True

                    if debug_level > 0:
                        print('  add_language_code = ' + str(add_language_code))
                    final_page_content, page_content = next_template(final_page_content, page_content)

                elif current_template in ['term', 'région']:
                    raw_term = page_content[end_position + 1:page_content.find('}}')]
                    term = trim(raw_term.replace('[[', '').replace(']]', ''))
                    if term.find('|') != -1:
                        term = trim(term[:term.find('|')])
                    if debug_level > 0:
                        print(' terminologie ou régionalisme')
                    if term == '':
                        final_page_content, page_content = next_template(final_page_content, page_content)
                    else:
                        if debug_level > 0:
                            print('  1 = ' + term)
                        template_page = get_content_from_page_name('Template:' + term, site,
                                                                   allowed_namespaces=['Template:'])
                        if template_page is None:
                            if debug_level > 0:
                                print(' Empty template page: ' + term)
                            final_page_content, page_content = next_template(final_page_content, page_content)
                        else:
                            if template_page.find('Catégorie:Modèles de domaine') == -1 and \
                                    template_page.find('{{région|') == -1 and term[:1] != term[:1].lower():
                                term = term[:1].lower() + term[1:]
                                if debug_level > 0:
                                    print('  2 = ' + term)
                                template_page = get_content_from_page_name('Template:' + term, site,
                                                                           allowed_namespaces=['Template:'])
                            if template_page is not None and (template_page.find('Catégorie:Modèles de domaine') != -1 \
                                    or template_page.find('{{région|') != -1):
                                if debug_level > 0:
                                    print('  substitution par le modèle existant')
                                page_content = '{{' + term + page_content[end_position + 1 + len(raw_term):]
                                final_page_content = final_page_content[:-2]
                                go_backward = True
                            else:
                                final_page_content, page_content = next_template(final_page_content, page_content)

                # Templates with language code at second
                elif current_template in definition_templates + etymology_templates_with_language_at_second + ['pron',
                                                                                                         'phon']:
                    if language_code == 'conv':
                        final_page_content, page_content = next_template(final_page_content, page_content)
                    else:
                        if debug_level > 0:
                            pywikibot.output("  Template with language code at second: \03{green}" + current_template
                                             + u"\03{default}")
                        page_content, final_page_content, summary = treat_pronunciation(page_content,
                                                                                        final_page_content, summary,
                                                                                        end_position, current_template,
                                                                                        language_code)

                # Templates with "lang="
                elif current_template in [u'écouter', 'cf'] + etymology_templates_with_language_at_lang:
                    final_page_content, page_content = add_language_code_with_named_parameter_to_template(
                        final_page_content,
                        page_content,
                        current_template,
                        language_code,
                        end_position
                    )

                elif current_template in ('référence nécessaire', 'réf?', 'réf ?', 'refnec', 'réfnéc', 'source?',
                                          'réfnéc'):
                    page_content2 = page_content[end_position + 1:]
                    # TODO regex = r'lang *= *'
                    if page_content2.find('lang=') == -1 or page_content2.find('lang=') > page_content2.find('}}'):
                        final_page_content = final_page_content + current_template + '|lang=' + language_code + \
                                             page_content[end_position:page_content.find('}}') + 2]
                        page_content = page_content[page_content.find('}}') + 2:]
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content)

                # Wrong genders
                elif current_template in ('m', 'f'):
                    if has_translation_section or (language_code != 'en' and language_code != 'zh' and
                                                   language_code != 'ja' and language_code != 'ko'):
                        final_page_content = final_page_content + page_content[:page_content.find('}}') + 2]
                    else:
                        if debug_level > 0:
                            print('  removing missing gender in ' + language_code)
                        final_page_content = final_page_content[:-2]
                        go_backward = True
                    page_content = page_content[page_content.find('}}') + 2:]
                elif current_template in ('mf', 'mf?'):
                    if has_translation_section or (language_code != 'en' and language_code != 'zh' and
                                                   language_code != 'ja' and language_code != 'ko'):
                        final_page_content = final_page_content + page_content[:page_content.find('}}') + 2]
                    else:
                        if debug_level > 0:
                            print('  removing missing gender in ' + language_code)
                        final_page_content = final_page_content[:-2]
                        go_backward = True
                    page_content = page_content[page_content.find('}}') + 2:]
                elif current_template in ('n', 'c'):
                    if has_translation_section or (language_code != 'en' and language_code != 'zh' and
                                                   language_code != 'ja' and language_code != 'ko' and
                                                   language_code != 'fr'):
                        final_page_content = final_page_content + current_template + '}}'
                    else:
                        if debug_level > 0:
                            print('  removing missing gender in ' + language_code)
                        final_page_content = final_page_content[:-2]
                        go_backward = True
                    page_content = page_content[page_content.find('}}') + 2:]

                # Templates with language code at first
                elif current_template in ('perfectif', 'perf', 'imperfectif', 'imperf', 'déterminé', 'dét',
                                          'indéterminé', 'indét'):
                    if (not add_language_code) or final_page_content.rfind('(') > final_page_content.rfind(')'):
                        # Si on est dans des parenthèses
                        final_page_content, page_content = next_template(final_page_content, page_content,
                                                                        current_template, 'nocat=1')
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content,
                                                                        current_template, language_code)

                # Templates with two parameters
                elif current_template in ('conjugaison', 'conj', '1ergroupe', '2egroupe', '3egroupe'):
                    page_content, final_page_content, summary = treat_conjugation(page_content, final_page_content,
                                                                                  summary, current_template,
                                                                                  language_code, page_name)

                elif do_fix_translations and (current_template == 'trad' or current_template == 'trad+'
                                              or current_template == 'trad-' or current_template == 'trad--'):
                    page_content, final_page_content, summary = treat_translations(page_content, final_page_content,
                                                                                   summary, end_position, site_family)

                elif current_template == '(':
                    if has_translation_section:
                        final_page_content = final_page_content + 'trad-début'
                    else:
                        final_page_content = final_page_content + '('
                    page_content = page_content[len(current_template):]
                elif current_template == ')':
                    if has_translation_section:
                        final_page_content = final_page_content + 'trad-fin'
                    else:
                        final_page_content = final_page_content + ')'
                    page_content = page_content[len(current_template):]
                elif current_template == 'trad-début':
                    if has_translation_section:
                        final_page_content = final_page_content + 'trad-début'
                    else:
                        final_page_content = final_page_content + '('
                    page_content = page_content[len(current_template):]
                elif current_template == 'trad-fin':
                    if has_translation_section:
                        final_page_content = final_page_content + 'trad-fin'
                    else:
                        final_page_content = final_page_content + ')'
                    page_content = page_content[len(current_template):]

                elif current_template == 'fr-verbe-flexion':
                    page_content, final_page_content, summary = treat_verb_inflexion(page_content, final_page_content,
                                                                                     summary, current_page_content)

                elif p < limit5:
                    add_language_code = False
                    if debug_level > 1:
                        print(' limit5 : paragraphe sans code langue contenant un texte. add_language_code=' +
                              str(add_language_code))
                    # trad = False
                    if page_content.find('}}') > page_content.find('{{') != -1:
                        page_content2 = page_content[page_content.find('}}') + 2:]
                        final_page_content = final_page_content + page_content[:page_content.find('}}') + 2
                                                                                + page_content2.find('}}') + 2]
                        page_content = page_content[page_content.find('}}') + 2 + page_content2.find('}}') + 2:]
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content)

                elif p < limit6:
                    if debug_level > 0:
                        print(' limit6 : modèle sans paramètre')
                    final_page_content = final_page_content + current_template + '}}'
                    page_content = page_content[page_content.find('}}') + 2:]

                elif p < limit7:
                    if debug_level > 0:
                        print(' limit7 : paragraphe potentiellement avec code langue, voire |spéc=')
                    if current_template == page_content[:page_content.find('}}')]:
                        if add_language_code:
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, language_code)
                        else:
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, 'nocat=1')
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content)

                elif p < limit8:
                    if debug_level > 0:
                        print(' limit8 : modèle catégorisé quel que soit add_language_code (ex : ébauches)')
                    if current_template == 'ébauche' and not language_code and page_content.find('== {{langue') != -1:
                        if debug_level > 0:
                            print('  déplacement du 1e {{ébauche}} pour être traité après détermination de la langue')
                        next_section = '{{caractère}}'
                        if page_content.find(next_section) == -1:
                            next_section = '{{langue|'
                        page_content2 = page_content[page_content.find(next_section):]
                        page_content = page_content[page_content.find('}}') + 2:page_content.find(next_section)
                                                                                + page_content2.find(
                            '\n') + 1] + '{{ébauche}}\n' \
                                       + page_content[page_content.find(next_section)
                                                      + page_content2.find('\n') + 1:]
                        final_page_content = final_page_content[:-2]
                        go_backward = True
                    elif language_code:
                        final_page_content, page_content = next_template(final_page_content, page_content,
                                                                        current_template, language_code)
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content,
                                                                        current_template, 'nocat=1')

                elif p < limit9:
                    if debug_level > 0:
                        print(' limit9 : modèle catégorisé dans les étymologies')
                    if current_template == page_content[:page_content.find('}}')]:
                        if add_language_code or section == 'étymologie':
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, language_code)
                        else:
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, 'nocat=1')
                    else:
                        final_page_content, page_content = next_template(final_page_content, page_content)

                else:
                    if debug_level > 0:
                        print(' Modèle régional : non catégorisé dans la prononciation')
                    if final_page_content.rfind('{{') != -1:
                        final_page_content2 = final_page_content[:final_page_content.rfind('{{')]
                        if add_language_code and (
                                (final_page_content2.rfind('{{') != final_page_content2.rfind('{{pron|')
                                    and final_page_content2.rfind('{{') != final_page_content2.rfind('{{US|')
                                    and final_page_content2.rfind('{{') != final_page_content2.rfind('{{UK|'))
                                    or final_page_content.rfind('{{pron|') < final_page_content.rfind('\n')
                                    or final_page_content2.rfind('{{pron|') == -1) \
                                    and ((page_content.find('{{') != page_content.find('{{pron|')
                                    or page_content.find('{{pron|') > page_content.find('\n'))
                                    or page_content.find('{{pron|') == -1):
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, language_code)
                        else:
                            final_page_content, page_content = next_template(final_page_content, page_content,
                                                                            current_template, 'nocat=1')

                if debug_level > 1:
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
                    pywikibot.output("\n\03{blue}Modèle traité\03{default}")
                    print(final_page_content[:1000])
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
                    input(page_content)
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
            else:
                if fix_old_templates:
                    if debug_level > 0:
                        print(' Recherche des modèles de langue désuets')
                    template_page = get_content_from_page_name('Template:' + current_template, site,
                                                               allowed_namespaces=['Template:'])
                    if template_page is not None and template_page.find('{{modèle désuet de code langue}}') != -1:
                        if debug_level > 0:
                            print(' Remplacements de l\'ancien modèle de langue')
                        page_content = 'subst:nom langue|' + current_template + page_content[page_content.find('}}'):]
                        page_content = page_content.replace('{{' + current_template + '}}',
                                                            '{{subst:nom langue|' + current_template + '}}')
                        final_page_content = final_page_content.replace('{{' + current_template + '}}',
                                                                        '{{subst:nom langue|' + current_template + '}}')
                        final_page_content, page_content = next_template(final_page_content, page_content)
                else:
                    if debug_level > 0:
                        pywikibot.output("\03{yellow} " + current_template + "\03{default}: unknown template")
                    final_page_content, page_content = next_template(final_page_content, page_content)

            if not go_backward:
                if debug_level > 1:
                    message = ' Remplacement par \x1b[6;32;40m' + final_page_content[
                                                                  final_page_content.rfind('{{'):] + '\x1b[0m\n\n'
                    print(message)
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
                if debug_level > 1:
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
                    input(page_content)
                    pywikibot.output("\n\03{red}---------------------------------------------\03{default}")

            if language_code is not None and page_content.find('}}') != -1 and (
                    page_content.find('}}') < page_content.find('{{') or page_content.find('{{') == -1):
                if debug_level > 1:
                    print('    possible duplicated "lang=" in ' + current_template)
                final_page_content, page_content = next_template(final_page_content, page_content)
                # TODO bug with nested templates:
                # https://fr.wiktionary.org/w/index.php?title=Utilisateur:JackBot/test_unitaire&diff=prev&oldid=25811164
                # regex = r'({{' + re.escape(current_template) + r')\|lang=' + language_code + '(\|[^{}]*({{(.*?)}}|.)*[^{}]*\|lang=' + language_code + ')'
                regex = r'({{' + re.escape(
                    current_template) + r')\|lang=' + language_code + '(\|[^{}]*\|lang=' + language_code + ')'
                if re.search(regex, final_page_content):
                    if debug_level > 1:
                        print('    remove duplicated "lang="')
                        print(regex)  # ex: ({{refnec)\|lang=pt(\|[^{}]*({{(.*?)}}|.)*[^{}]*\|lang=pt)
                        input(final_page_content)
                    final_page_content = re.sub(regex, r'\1\2', final_page_content)

        final_page_content = final_page_content + page_content

        if debug_level > 0:
            ' Recherche du nombre'
        regex = r"{{(pluriel|nombre) *\?*\|fr}}( {{[m|f]}})(\n# *'* *([Mm]asculin |[Ff]éminin )*[Pp]luriel d)"
        if re.search(regex, final_page_content):
            summary = summary + ', précision du pluriel'
            final_page_content = re.sub(regex, r'{{p}}\2\3', final_page_content)

        regex = r"{{(pluriel|nombre) *\?*\|fr}} *(\n# *'* *([Mm]asculin |[Ff]éminin )*[Pp]luriel d)"
        if re.search(regex, final_page_content):
            summary = summary + ', précision du pluriel'
            final_page_content = re.sub(regex, r'{{p}}\2', final_page_content)

        if fix_genders:
            if debug_level > 0: ' Recherche du genre'
            regex = r"{{genre *\?*\|fr}}(\n# *'* *[Mm]asculin)"
            if re.search(regex, final_page_content):
                final_page_content = re.sub(regex, r'{{m}}\1', final_page_content)
                summary = summary + ', précision du genre m'
                if debug_level > 1:
                    print('  m1')

            regex = r"{{genre *\?*\|fr}}(\n# *'* *[Ff]éminin)"
            if re.search(regex, final_page_content):
                final_page_content = re.sub(regex, r'{{f}}\1', final_page_content)
                summary = summary + ', précision du genre f'
                if debug_level > 1:
                    print('  f1')

            if final_page_content.find('{{genre|fr}}') != -1 or final_page_content.find('{{genre ?|fr}}') != -1:
                mSuffixes = ['eur', 'eux', 'ant', 'age', 'ier', 'ien', 'ois', 'ais', 'isme', 'el', 'if', 'ment',
                             'ments']  # pas "é" : adaptabilité
                for mSuffix in mSuffixes:
                    if page_name[-len(mSuffix):] == mSuffix:
                        final_page_content = final_page_content.replace(u"{{genre|fr}}", u"{{m}}")
                        final_page_content = final_page_content.replace(u"{{genre ?|fr}}", u"{{m}}")
                        summary = summary + ', précision du genre m'
                        if debug_level > 1:
                            print('  m2')
                        break

                fSuffixes = ['euse', 'ante', 'ance', 'ette', 'ienne', 'rie', 'oise', 'aise', 'logie', 'tion', 'ité',
                             'elle', 'ive']
                for fSuffix in fSuffixes:
                    if page_name[-len(fSuffix):] == fSuffix:
                        final_page_content = final_page_content.replace(u"{{genre|fr}}", u"{{f}}")
                        final_page_content = final_page_content.replace(u"{{genre ?|fr}}", u"{{f}}")
                        summary = summary + ', précision du genre f'
                        if debug_level > 1:
                            print('  f2')
                        break

                mfSuffixes = ['iste']
                for mfSuffix in mfSuffixes:
                    if page_name[-len(mfSuffix):] == mfSuffix:
                        final_page_content = final_page_content.replace(u"{{genre|fr}}", u"{{mf}}")
                        final_page_content = final_page_content.replace(u"{{genre ?|fr}}", u"{{mf}}")
                        summary = summary + ', précision du genre mf'
                        if debug_level > 1:
                            print('  mf1')
                        break

                if singular_page_name != '':
                    lemma_gender = getGenderFromPage_name(singular_page_name)
                    if lemma_gender != '':
                        final_page_content = final_page_content.replace('{{genre|fr}}', lemma_gender)
                        final_page_content = final_page_content.replace('{{genre ?|fr}}', lemma_gender)
                        summary = summary + ', précision du genre ' + lemma_gender
                        if debug_level > 1:
                            print('  loc')

            if fix_false_inflexions and page_name[-2:] == 'es':
                if debug_level > 0:
                    ' Fix des flexions de noms féminins'
                old_suffix = []
                new_suffix = []
                old_suffix.append(r'eur')
                new_suffix.append(r'rice')
                old_suffix.append(r'eur')
                new_suffix.append(r'euse')
                old_suffix.append(r'eux')
                new_suffix.append(r'euse')
                old_suffix.append(r'er')
                new_suffix.append(r'ère')
                old_suffix.append(r'el')
                new_suffix.append(r'elle')
                old_suffix.append(r'et')
                new_suffix.append(r'ette')
                old_suffix.append(r'n')
                new_suffix.append(r'nne')
                section_content, start_position, end_position = getSection(final_page_content, 'nom')
                if section_content is not None:
                    new_section_content = section_content
                    i = 0
                    while i < len(new_suffix):
                        if page_name[-len(new_suffix[i] + 's'):] == new_suffix[i] + 's':
                            regex = r"({{fr\-rég\|s=[^\|}]+)" + old_suffix[i] + u"([\|}])"
                            if re.search(regex, new_section_content):
                                new_section_content = re.sub(regex, r'\1' + new_suffix[i] + r'\2', new_section_content)

                            regex = r"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + old_suffix[
                                i] + u"([\|#][^\]]+)" + old_suffix[i] + u"(\])"
                            if re.search(regex, new_section_content):
                                new_section_content = re.sub(regex,
                                                             r'\1' + new_suffix[i] + r'\2' + new_suffix[i] + r'\3',
                                                             new_section_content)

                            regex = r"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + old_suffix[
                                i] + u"([\|#])"
                            if re.search(regex, new_section_content):
                                new_section_content = re.sub(regex, r'\1' + new_suffix[i] + r'\2', new_section_content)

                            regex = r"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + old_suffix[
                                i] + u"(\])"
                            if re.search(regex, new_section_content):
                                new_section_content = re.sub(regex, r'\1' + new_suffix[i] + r'\2', new_section_content)
                        i = i + 1
                    regex = r"({{fr\-rég\|s=[^\|}]+[^e\]}])([\|}])"
                    if re.search(regex, new_section_content):
                        new_section_content = re.sub(regex, r'\1e\2', new_section_content)
                    regex = r"({{f}}\n# ''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+[^e\]])(\])"
                    if re.search(regex, new_section_content):
                        new_section_content = re.sub(regex, r'\1e\2', new_section_content)
                    regex = r"({{f}}\n# ''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+[^e])([\|#][^\]]+[^e\]])(\])"
                    if re.search(regex, new_section_content):
                        new_section_content = re.sub(regex, r'\1e\2e\3', new_section_content)
                    new_section_content = new_section_content.replace('|e}}', '|}}')

                    summary = summary + ', correction de flexion de nom féminin'
                    final_page_content = final_page_content.replace(section_content, new_section_content)

        language = 'fr'  # TODO: intl
        if final_page_content.find('{{langue|' + language + '}}') != -1:
            if debug_level > 0:
                print(' Fix false homophons (lemma and its inflexion)')
            # TODO : modèles des locutions
            # TODO : doublon systématique ? singular_page_name = getLemmaFromContent(final_page_content, language)
            flexion_page_name = ''
            if final_page_content.find('|' + language + '|flexion}}') == -1:
                # Recherche d'éventuelles flexions dans la page du lemme
                inflexion_template = get_inflexion_template(page_name, language)
                if inflexion_template.find('inv=') == -1 and \
                        (inflexion_template[:inflexion_template.find('|')] in inflexion_templates_fr_with_s
                         or inflexion_template[:inflexion_template.find('|')] in inflexion_templates_fr_with_ms):
                    flexion_page_name = get_parameter_value(inflexion_template, 'p')
                    if flexion_page_name == '':
                        flexion_page_name = page_name + 's'
                # TODO: inflexion_template = [conjugaisons]

            for i in range(0, 2):
                if infinitive is not None and infinitive != '':
                    final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                        infinitive, summary)
                if singular_page_name is not None and singular_page_name != '':
                    final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                        singular_page_name, summary)
                if flexion_page_name is not None and flexion_page_name != '':
                    final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                        flexion_page_name, summary)
                ms_page_name = get_lemma_from_feminine(final_page_content, language, ['adjectif'])
                if ms_page_name is not None and ms_page_name != '':
                    final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                        ms_page_name, summary)
            if debug_level > 2:
                input(final_page_content)

        regex = r'([^\n=])(===?=? *{{S\|)'
        if re.search(regex, final_page_content):
            final_page_content = re.sub(regex, r'\1\n\n\2', final_page_content)

    else:
        # Unknown namespace
        final_page_content = page_content

    # Fix
    final_page_content = final_page_content.replace('|lanɡ=', '|lang=')
    regex = r'({{pron)(\|lang=[a-zA-Z]{2,3})(\|[a-zA-Z]{2,3}}})'
    if re.search(regex, final_page_content):
        final_page_content = re.sub(regex, r'\1|\3', final_page_content)

    if test_import and username in page_name:
        final_page_content = add_line_test(final_page_content)
    if debug_level > 0:
        pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
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
        print(' format_fr_section()')
    language_code = 'fr'
    natures_with_plural = ['nom', 'adjectif', 'suffixe']

    regex = r'(=== {{S\|nom\|' + language_code + r')\|flexion(}} ===\n(?:{{' + language_code + r"[^\n]*\n)*'''" \
            + regex_page_name + r"''' [^\n]*{{fsing}})"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
        summary = summary + ', un nom féminin n\'est pas une flexion en français'
    regex = r'(=== {{S\|nom\|' + language_code + r')\|flexion(}} ===\n(?:{{' + language_code + r"[^\n]*\n)*'''" \
            + regex_page_name + r"''' [^\n]*{{f}}\n# *'*[Ff]éminin (?:de|singulier))"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
        summary = summary + ', un nom féminin n\'est pas une flexion en français'

    if page_name.find('*') == -1 and page_name[-1:] == 's':
        singular_page_name = get_lemma_from_plural(page_content, language_code, natures_with_plural)
        if singular_page_name != '':
            # TODO cannot move this recursive function in the dedicated used module (circular dependency)?
            treat_page_by_name(singular_page_name)  # Formatage des boites de flexion à récupérer
        page_content, summary = treat_noun_inflexion(page_content, summary, page_name, regex_page_name,
                                                     natures_with_plural, language_code, singular_page_name)

    if debug_level > 0:
        print(' Missing translations')
    # Si la définition du mot (dit "satellite") ne renvoie pas vers un autre, les centralisant
    # TODO: # Variante,
    regex = r'(' + language_code + r'\|flexion|' + '|'.join(definition_sentences) + '|'.join(
        map(lambda x: x.capitalize(), definition_sentences)) + r')'
    regex2 = r'{{(formater|SI|supp|supprimer|PàS|S\|erreur|S\|faute|S\|traductions|' + \
             '|'.join(etymology_templates_in_satellite_words) + r')[\|}]'
    fr_section, language_start, language_end = get_language_section(page_content, language_code)
    if fr_section is not None and re.search(regex, fr_section) is None and re.search(regex2, fr_section) is None and \
            count_first_definition_size(fr_section) > 3:
        summary = summary + ', ajout de {{S|traductions}}'
        page_content = add_line(page_content, 'fr', 'traductions', '{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}')
    # Cosmetic fix
    regex = r'(==== {{S\|traductions}} ====\n)\n* *\n*({{trad\-début)'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\2', page_content)
    regex = r'({{trad\-fin}}\n)([^\n])'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1\n\2', page_content)
    return page_content, summary


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)


def main(*args):
    global wait_after_humans, fix_old_templates, output_file, site_language, site_family, fix_tags, \
        list_false_translations, test_import, cancel_user
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        after_page = ''
        if len(sys.argv) > 2:
            after_page = sys.argv[2]
        if sys.argv[1] == str('-test'):
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == str('-test2'):
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == str('-tu') or sys.argv[1] == str('-t'):
            treat_page_by_name('User:' + username + '/test unitaire')
        elif sys.argv[1] == str('-ti'):
            test_import = True
            treat_page_by_name('User:' + username + '/test unitaire')
        elif sys.argv[1] == str('-page') or sys.argv[1] == str('-p'):
            wait_after_humans = False
            treat_page_by_name('Nguyễn')
        elif sys.argv[1] == str('-file') or sys.argv[1] == str('-txt'):
            wait_after_humans = False
            file_name = 'src/lists/articles_' + site_language + '_' + site_family + '.txt'
            if debug_level > 0:
                print(file_name)
            p.pages_by_file(file_name)
        elif sys.argv[1] == str('-dump') or sys.argv[1] == str('-xml') or sys.argv[1] == str('-regex'):
            dump_file = site_language + site_family + '\-.*xml'
            if len(sys.argv) > 2:
                regex = sys.argv[2]
            else:
                regex = r'{term[\n\|].*id *= *[^\n\|{}]+[\n\|]'
            if len(sys.argv) > 3:
                test_page = sys.argv[3]
            else:
                test_page = None
            if test_page is not None:
                page_content = get_content_from_page_name(test_page, site)
                if page_content is not None and re.search(regex, page_content, re.DOTALL):
                    print('Traitement...')
                else:
                    print('Pas de traitement.')
            else:
                p.page_by_xml(dump_file, regex=regex, namespaces=10)
        elif sys.argv[1] == str('-u'):
            if len(sys.argv) > 2:
                targeted_user = sys.argv[2]
            else:
                targeted_user = username
            if len(sys.argv) > 3:
                cancel_user['user'] = targeted_user
                cancel_user['action'] = sys.argv[3]
            if len(sys.argv) > 4:
                number = sys.argv[4]
            else:
                number = 1000
            p.pages_by_user('User:' + targeted_user, number_of_pages_to_treat=number, namespaces=[0])
        elif sys.argv[1] == str('-search') or sys.argv[1] == str('-s') or sys.argv[1] == str('-r'):
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search('insource:/\{\{pron\|lanɡ=/', namespaces=[0])

        elif sys.argv[1] == str('-link') or sys.argv[1] == str('-l') or sys.argv[1] == str('-template') or \
                sys.argv[1] == str('-m'):
            p.pages_by_link('Template:abréviation', namespaces=[0])
            p.pages_by_link('Template:acronyme', namespaces=[0])
            p.pages_by_link('Template:diminutif', namespaces=[0])
            p.pages_by_link('Template:sigle', namespaces=[0])
            p.pages_by_link('Template:verlan', namespaces=[0])
        elif sys.argv[1] == str('-category') or sys.argv[1] == str('-cat') or sys.argv[1] == str('-c'):
            if len(sys.argv) > 2:
                if sys.argv[2] == str('listFalseTranslations'):
                    list_false_translations = True
                    p.pages_by_cat('Catégorie:Pages "info" si réforme 1895 de l’espéranto')
                elif sys.argv[2] == str('fixOldTemplates'):
                    fix_old_templates = True
                    p.pages_by_cat('Appels de modèles incorrects:abréviation', after_page=after_page, recursive=False,
                                   namespaces=[14])
                else:
                    p.pages_by_cat(sys.argv[2].decode(config.console_encoding, 'replace'))
            else:
                p.pages_by_cat('Date manquante', namespaces=[0, 14], recursive=True)
                p.pages_by_cat('Dates manquantes', namespaces=None, recursive=False)

        elif sys.argv[1] == str('-redirects'):
            p.pages_by_redirects()
        elif sys.argv[1] == str('-all'):
            p.pages_by_all()
        elif sys.argv[1] in [str('-rc'), str('-RC')]:
            while 1:
                # p.pages_by_rc() TODO error with self in context
                p.pages_by_rc_last_day()
        elif sys.argv[1] == str('-nocat'):
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == str('-lint'):
            fix_tags = True
            p.pages_by_special_lint()
        elif sys.argv[1] == str('-extlinks'):
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
        p.pages_by_cat('Catégorie:Wiktionnaire:Codes langue manquants', recursive=True,
                       exclude=['Catégorie:Wiktionnaire:Traductions manquantes sans langue précisée'])
        p.pages_by_cat('Catégorie:Wiktionnaire:Flexions à vérifier', recursive=True)
        p.pages_by_cat('Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée')
        p.pages_by_cat('Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet')
        p.pages_by_cat('Catégorie:Appels de modèles incorrects:deet')
        p.pages_by_cat('Catégorie:Wiktionnaire:Ébauches à compléter')
        p.pages_by_link('Template:trad', namespaces=[0])
        p.pages_by_link('Template:clef de tri')
        p.pages_by_link('Template:1ergroupe')
        p.pages_by_link('Template:2egroupe')
        p.pages_by_link('Template:3egroupe')
        p.pages_by_link('Template:-')
        p.pages_by_link('Template:-ortho-alt-')
        p.pages_by_link('Template:mascul')
        p.pages_by_link('Template:fémin')
        p.pages_by_link('Template:femin')
        p.pages_by_link('Template:sing')
        p.pages_by_link('Template:plur')
        p.pages_by_link('Template:pluri')
        p.pages_by_link('Template:=langue=')
        p.pages_by_link('Template:-déf-')
        p.pages_by_link('Template:pron-rég')
        p.pages_by_link('Template:mp')
        p.pages_by_link('Template:fp')
        p.pages_by_link('Template:vx')
        p.pages_by_link('Template:contr')
        p.pages_by_link('Template:deet')
        # p.pages_by_link('Template:compos')
        p.pages_by_link('Template:ordin')
        p.pages_by_link('Template:cardin')
        p.pages_by_link('Template:comp')
        p.pages_by_link('Template:super')
        p.pages_by_link('Template:irrég')
        p.pages_by_link('Template:perf')
        p.pages_by_link('Template:imperf')
        p.pages_by_link('Template:nomin')
        p.pages_by_link('Template:acron')
        p.pages_by_link('Template:abrév')
        p.pages_by_cat('Catégorie:Traduction en français demandée d’exemple(s) écrits en français')
        p.pages_by_cat('Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section')
        p.pages_by_cat('Catégorie:Wiktionnaire:Sections avec titre inconnu')
        p.pages_by_cat('Catégorie:Wiktionnaire:Sections avec paramètres superflus')
        p.pages_by_cat('Catégorie:Wiktionnaire:Sections utilisant un alias')
        p.pages_by_search('insource:/\}==== \{\{S\|/', namespaces=[0])
        p.pages_by_search('insource:/\}=== \{\{S\|/', namespaces=[0])
        p.pages_by_search('insource:/solrésol *:/i', namespaces=[0])
        p.pages_by_search('insource:/tsolyáni}} *: *\[/i', namespaces=[0])
        p.pages_by_search(
            'insource:/[^=]=== \{\{S\|(variantes|synonymes|antonymes|dérivés|apparentés|hyperonymes|hyponymes|méronymes|holonymes|vocabulaire|traductions)/',
            namespaces=[0])


if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/env python
# coding: utf-8
"""
TODO: common Wiktionaries interfaces in OOP
"""

from __future__ import absolute_import, unicode_literals
import collections
import re
import pywikibot
# JackBot
from lib import *
from languages import *
from fr_wiktionary_templates import *


def set_fr_wiktionary_functions_globals(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


def get_first_lemma_from_locution(page_name):
    if debug_level > 1:
        print(inspect.currentframe())
    lemma_page_name = ''
    if page_name.find(' ') != -1:
        if debug_level > 0:
            print(' lemme de locution trouvé : ' + lemma_page_name)
        lemma_page_name = page_name[:page_name.find(' ')]
    return lemma_page_name


def get_gender_from_page_name(page_name, language_code='fr', nature=None):
    if debug_level > 1:
        print('\ngetGenderFromPage_name')
    gender = None
    page_content = get_content_from_page_name(page_name, site)
    if page_content is None:
        return gender
    if page_content.find('|' + language_code + '}} {{m}}') != -1:
        gender = '{{m}}'
    elif page_content.find('|' + language_code + '}} {{f}}') != -1:
        gender = '{{f}}'
    elif page_content.find(u"''' {{m}}") != -1:
        gender = '{{m}}'
    elif page_content.find(u"''' {{f}}") != -1:
        gender = '{{f}}'
    if debug_level > 1:
        input(gender)
    return gender


def get_lemma_from_content(page_content, language_code='fr'):
    if debug_level > 1:
        print('\ngetLemmaFromContent')
    lemma_page_name = get_lemma_from_plural(page_content, language_code)
    if lemma_page_name == '':
        lemma_page_name = get_lemma_from_conjugation(page_content, language_code)
    return lemma_page_name


def get_lemma_from_plural(page_content, language_code='fr', natures=['nom', 'adjectif', 'suffixe']):
    if debug_level > 1:
        print('\nget_lemma_from_plural')
    lemma_page_name = ''
    regex = r"(=== {{S\|(" + '|'.join(natures) + r")\|" + language_code + r"\|flexion}} ===\n({{" + language_code + \
     r"\-[^}]*}}\n)?'''[^\n]+\n# *'* *([Mm]asculin|[Ff]éminin)* *'* *'*[P|p]luriel *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            print(s.group(1))  # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            input(s.group(6))
        lemma_page_name = s.group(6)
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03{red}" + lemma_page_name + "\03{default}")
    if debug_level > 1:
        input(page_content)

    return lemma_page_name


def get_lemma_from_feminine(page_content, language_code='fr', natures=['nom', 'adjectif']):
    if debug_level > 1:
        print('\nget_lemma_from_feminine()')
    lemma_page_name = ''
    regex = r"(=== {{S\|(" + '|'.join(natures) + ")\|" + language_code + "\|flexion}} ===\n({{" + language_code + \
     "\-[^}]*}}\n)?'''[^\n]+\n# *'* *[Ff]éminin *'* *'*(singulier|pluriel)? *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            print(s.group(1))  # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            input(s.group(6))
        lemma_page_name = s.group(6)
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03{red}" + lemma_page_name + "\03{default}")
    if debug_level > 1:
        input(page_content)

    return lemma_page_name


def get_lemma_from_conjugation(page_content, language_code='fr'):
    if debug_level > 1:
        print('\ngetLemmaFromConjugation')
    lemma_page_name = ''
    regex = r"(=== {{S\|verbe\|fr\|flexion}} ===\n({{fr\-[^}]*}}\n)*'''[^\n]+\n#[^\n\[{]+(\[\[|{{li?e?n?\|))([^#\|\]}]+)}*\]*'*\."
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            print(s.group(1))  # 2 fr-verbe-flexion, 3 = {{lien|, 4 = lemme
            input(s.group(4))
        lemma_page_name = s.group(4)
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03{red}" + lemma_page_name + "\03{default}")

    return lemma_page_name


def get_inflexion_template(page_name, language, nature=None):
    if debug_level > 1:
        print('\nget_inflexion_template')
    inflexion_template = ''
    if nature is None:
        nature = 'nom|adjectif|suffixe'
    page_content = get_content_from_page_name(page_name, site)
    if page_content is None:
        return inflexion_template

    regex = r"=== {{S\|(" + nature + r")\|" + language + r"(\|flexion)?(\|num=[0-9])?}} ===\n{{(" \
            + language + r"\-[^}]+)}}"
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            if not s.group(1) is None:
                print(' ' + s.group(1))  # Nature
            if not s.group(2) is None:
                print(' ' + s.group(2))  # Flexion
            if not s.group(3) is None:
                print(' ' + s.group(3))  # Number
            if not s.group(4) is None:
                print(' ' + s.group(4))  # Template
        inflexion_template = s.group(4)
    if debug_level > 0:
        pywikibot.output(" inflexion_template found: \03{green}" + inflexion_template + "\03{default}")
    # TODO
    if inflexion_template.find('{{') != -1:
        inflexion_template = ''
    if inflexion_template.find('-inv') != -1:
        inflexion_template = ''

    return inflexion_template


def get_inflexion_template_from_lemma(page_name, language, nature):
    d = 0
    if debug_level > d:
        print('\nget_inflexion_template_from_lemma()')
    inflexion_template = ''
    page_content = get_content_from_page_name(page_name, site)
    if page_content is None:
        return None

    regex = r"=== {{S\|" + nature + r"\|" + language + r"(\|num=[0-9])?}} ===\n{{(" + language + r"\-[^}]+)}}"
    if debug_level > d:
        print(' ' + regex)
    s = re.search(regex, page_content)
    if s:
        if debug_level > d:
            if not s.group(1) is None:
                print(' ' + s.group(1))
            if not s.group(2) is None:
                print(' ' + s.group(2))
        inflexion_template = s.group(2)
    if debug_level > d:
        print(' inflexion_template found: ' + inflexion_template)
    # TODO
    if inflexion_template.find('{{') != -1:
        inflexion_template = ''
    if inflexion_template.find('-inv') != -1:
        inflexion_template = ''
    return inflexion_template


def get_page_languages(page_content):
    if debug_level > 1:
        print('\nget_page_languages()')
    regex = r'{{langue\|([^}]+)}}'
    s = re.findall(regex, page_content, re.DOTALL)
    if s:
        return s
    return []


def get_language_section(page_content, language_code='fr'):
    if debug_level > 1:
        print('\nget_language_section(' + language_code + ')')
    start_position = 0
    end_position = len(page_content)

    regex = r'=* *{{langue\|' + language_code + '}}'
    s = re.search(regex, page_content)
    if not s:
        if debug_level > 0:
            print(' missing language!')
        return None, start_position, end_position

    start_position = s.start()
    page_content = page_content[s.start():]
    regex = r'\n== *{{langue\|(?!' + language_code + r'}).*} *='
    s = re.search(regex, page_content)
    if s:
        end_position = s.start()
        page_content = page_content[:end_position]
        if debug_level > 1:
            print(end_position)
    if debug_level > 2:
        input(page_content)

    return page_content, start_position, end_position


def get_not_natures_sections(page_content):
    global natures
    if debug_level > 1:
        print('\nget_not_natures_sections()')
    sections = get_sections_titles(page_content)
    return [item for item in sections if item not in natures]


def get_natures_sections(page_content):
    if debug_level > 1:
        print('\nget_natures_sections()')
    sections = get_sections_titles(page_content)
    not_natures_sections = get_not_natures_sections(page_content)
    return [item for item in sections if item not in not_natures_sections]


def get_definitions(page_content):
    if debug_level > 1:
        print('\nget_definitions')
    if debug_level > 2:
        input(page_content)
    regex = r"\n'''[^\n]*\n(#.*?(\n\n|\n=|$))"
    s = re.search(regex, page_content, re.DOTALL)
    if s is None:
        if debug_level > 1:
            print('No definition')
        return None
    if debug_level > 1:
        print(s.group(1))
    return s.group(1)


def count_definitions(page_content):
    if debug_level > 1:
        print('\ncount_definitions')
    definitions = get_definitions(page_content)
    if definitions is None:
        return 0
    definitions = definitions.split('\n')
    total = 0
    for definition in definitions:
        if definition[:1] == '#' and definition[:2] not in [u'#:', '#*']:
            total += 1
    return total


def count_first_definition_size(page_content):
    if debug_level > 1:
        print('\ncount_first_definition_size')

    definition = get_definitions(page_content)
    if definition is None:
        return 0
    if definition.find('\n') != -1:
        definition = definition[:definition.find('\n')]
    if debug_level > 1:
        print(' First definition:')  # regex = r"\n'''[^\n]*(\n#(!:\*)?.*(\n|$))"
        input(definition)

    regex = r'^#( *{{[^}]*}})?( *{{[^}]*}})? *\[\[[^\]]+\]\]\.?$'
    if re.search(regex, definition):
        if debug_level > 0:
            print(' The definition is just one link to another article')
        return 1

    regex = r' *({{[^}]*}}|\([^\)]*\) *\.?)'
    definition = re.sub(regex, '', definition)
    if debug_level > 1:
        print(' Parsed definition:')
        input(definition)
    words = definition.split(' ')
    if debug_level > 0:
        print(' count_first_definition_size(): ' + str(len(words)))
    return len(words)


def get_pronunciation_from_content(page_content, language_code, nature=None):
    if debug_level > 1:
        print('\nget_pronunciation_from_content')
    regex = r".*'''([^']+)'''.*"
    s = re.search(regex, page_content, re.MULTILINE| re.DOTALL)
    if not s: return
    page_name = s.group(1)

    # Template {{pron}}
    regex = r"{{pron\|([^}]+)\|" + language_code + "}}"
    s = re.search(regex, page_content)
    pronunciation = ''
    if s:
        pronunciation = s.group(1)
        pronunciation = pronunciation[:pronunciation.find('=')]
        pronunciation = pronunciation[:pronunciation.rfind('|')]
        if debug_level > 0:
            input(' prononciation en ' + language_code + ' : ' + pronunciation)
        page_content = re.sub(r'{{pron\|\|' + language_code + '}}', \
            r'{{pron|' + pronunciation + r'|' + language_code + '}}', page_content)
        return pronunciation

    # Templates {{fr-xxx}}
    if language_code == 'fr':
        templates = '|'.join(flexion_templates_fr_with_s) + '|' + '|'.join(flexion_templates_fr_with_ms)
        templates2 = '|'.join(flexion_templates_fr)
    else:
        return

    # TODO: templateContent = getTemplateContent(page_content, template) ?
    regex = r'{{(' + re.escape(templates) + r")\|([^{}\|=]+)([^{}]*}}\n\'\'\'" \
        + re.escape(page_name).replace('User:', '') + r"'\'\')( *{*f?m?n?}* *)\n"
    s = re.search(regex, page_content)
    if s:
        pronunciation = s.group(1)
        if debug_level > 0:
            print(' prononciation trouvée en {{{1}}} dans une boite de flexion : ' + pronunciation)
        page_content = re.sub(regex, r'{{\1|\2\3 {{pron|\2|' + language_code + '}}\4\n', page_content)
        return pronunciation

    regex = r'{{(' + templates.replace('-', '\-') + u")\|([^{}]+)}}"
    s = re.search(regex, page_content)
    if s:
        template = s.group(1)
        if debug_level > 0:
            print(template)

    regex = r'{{(' + templates2 + u")\|([^{}]+)}}"
    s = re.search(regex, page_content)
    if s:
        template = s.group(1)
        parameters = s.group(2)
        if debug_level > 0:
            print(' template trouvé : ' + template)
        if debug_level > 0:
            print(' paramètres : ' + parameters)

        if template == 'fr-accord-comp':
            # pronunciation = get_parameter(template, 3)
            pass
        elif template == 'fr-accord-comp-mf':
            # pronunciation = get_parameter(template, 3)
            pass
        elif template == 'fr-accord-eur':
            # TODO pronunciation = get_parameter(template, 2)
            pronunciation = parameters[parameters.rfind('|')+1:]
            pronunciation = pronunciation + 'œʁ'
        elif template == 'fr-accord-eux':
            # pronunciation = get_parameter(template, 2)
            pronunciation = pronunciation + 'ø'
        elif template == 'fr-accord-f':
            # pronunciation = get_parameter(template, 2)
            pronunciation = pronunciation + 'f'
        elif template == 'fr-accord-ind':
            pronunciation = get_parameter(template, 'pm')
            pass
        elif template == 'fr-accord-mf':
            pronunciation = get_parameter(template, 'pron')
        elif template == 'fr-accord-mf-ail':
            # pronunciation = get_parameter(template, 2)
            pass
        elif template == 'fr-accord-mf-al':
            # pronunciation = get_parameter(template, 2)
            pass
        elif template == 'fr-accord-oux':
            # pronunciation = get_parameter(template, 2)
            pass
        elif template == 'fr-accord-personne':
            # pronunciation = get_parameter(template, 'p1ms')
            # pronunciation = get_parameter(template, 'p2s')
            pass
        elif template == 'fr-accord-t-avant1835':
            # pronunciation = get_parameter(template, 2)
            pass
        elif template == 'fr-inv':
            # pronunciation = get_parameter(template, 1)
            pass

        if pronunciation.find('.') != -1:
            if debug_level > 0:
                print(' prononciation trouvée dans une boite de flexion : ' + pronunciation)
    if debug_level > 1:
        input('Fin du test des flexions féminines')
    return pronunciation


def get_pronunciation(page_content, language_code, nature=None):
    if debug_level > 1:
        print('\nget_pronunciation')
    pronunciation = get_pronunciation_from_content(page_content, language_code, nature)
    # TODO: from other pages or wikis
    '''
    if pronunciation == '':
        if page_content.find('|' + language_code + '|flexion}}') != -1:
            pronunciation = getPronunciationFromFlexion(page_content, language_code, nature)
        else:
            pronunciation = getPronunciationFromLemma(page_content, language_code, nature)
    '''
    if debug_level > 0:
        print(' Pronunciation found: ' + pronunciation)
    return pronunciation


def add_pronunciation_from_content(page_content, language_code, nature=None):
    if debug_level > 1:
        print('\nadd_pronunciationFromContent')
    if page_content.find('{{pron||' + language_code + '}}') != -1:
        pronunciation = get_pronunciation(page_content, language_code, nature=None)
        if pronunciation != '':
            page_content = page_content.replace('{{pron||' + language_code + '}}', '{{pron|' + pronunciation + '|'
                                                + language_code + '}}')
    return page_content


def add_category(page_content, language_code, line_content):
    if debug_level > 1:
        print('\ndo_add_category')
    if line_content.find('[[Catégorie:') == -1: line_content = '[[Catégorie:' + line_content + ']]'

    return add_line(page_content, language_code, 'catégorie', line_content)


def remove_category(page_content, category, summary):
    if debug_level > 1:
        print('\nremoveCategory(' + category + ')')
    regex_category = r'(\n\[\[Catégorie:' + category + r'(\||\])[^\]]*\]\]?)'
    new_page_content = re.sub(regex_category, r'', page_content)
    if new_page_content != page_content:
        summary = summary + ', retrait de [[Catégorie:' + category + ']]'

    return new_page_content, summary


def format_categories(page_content, summary):
    if debug_level > 1:
        print('\nformat_category')

    regex = r'\[\[[Cc]ategory:'
    page_content = re.sub(regex, r'[[Catégorie:', page_content)

    regex = r'([^\n])\[\[[Cc]atégorie:'
    page_content = re.sub(regex, r'\1\n[[Catégorie:', page_content)

    regex = r'(\[\[[Cc]atégorie:[^\n]+\n)\n+(\[\[[Cc]atégorie:)'
    page_content = re.sub(regex, r'\1\2', page_content)

    return page_content, summary


def remove_template(page_content, template, summary, language=None, in_section=None):
    if debug_level > 1:
        print('\nremove_template(' + template + ')')
    # TODO: rattacher le bon template à la bonne ligne de l'étymologie, et s'il doit être déplacé plusieurs fois
    regex_template = r'(,?( et| ou)? *{{' + template + r'(\||})[^}]*}}?)'
    old_section = page_content
    if in_section is not None:
        if language is not None:
            old_section, l_start, l_end = get_language_section(old_section, language)
        if old_section is not None:
            for section in in_section:
                old_sub_section, s_start, s_end = get_section_by_name(old_section, section)
                if old_sub_section is not None:
                    new_sub_section = re.sub(regex_template, r'', old_sub_section)
                    if old_sub_section != new_sub_section:
                        page_content = page_content.replace(old_sub_section, new_sub_section)
                        summary = summary + ', retrait de {{' + template + '}} dans {{S|' + section + '}}'
    else:
        new_section = re.sub(regex_template, r'', old_section)
        if old_section != new_section:
            page_content = page_content.replace(old_section, new_section)
            summary = summary + ', retrait de {{' + template + '}}'
    return page_content, summary


def add_line(page_content, language_code, section_name, line_content):
    d = 0
    if debug_level > d:
        pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
        print('\nadd_line(' + language_code + ', ' + section_name + ')')
    if page_content != '' and language_code != '' and section_name != '' and line_content != '':
        if page_content.find(line_content) == -1 and page_content.find('{{langue|' + language_code + '}}') != -1:
            if section_name == 'catégorie' and line_content.find('[[Catégorie:') == -1:
                line_content = '[[Catégorie:' + line_content + ']]'
            if section_name == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
                line_content = '{{clé de tri|' + line_content + '}}'

            section_to_add_order = get_order_by_section_name(section_name)
            if section_to_add_order == len(sections):
                if debug_level > d:
                    print(' ajout de la sous-section : ' + section_name + ' dans une section inconnue (car '
                          + str(len(sections)) + ' = ' + str(section_to_add_order) + ')\n')
                return page_content

            # Recherche de l'ordre réel de la section à ajouter
            language_section, start_position, end_position = get_language_section(page_content, language_code)
            if language_section is None:
                # TODO add section language too in option
                return page_content

            sections_in_page = re.findall(r"\n=+ *{{S\|?([^}/|]+)([^}]*)}}", language_section)
            if debug_level > d + 1:
                input(str(sections_in_page))  # ex : [('nom', '|fr|num=1'), ('synonymes', '')]

            regex = r'\n=* *{{S\|' + section_name + r'[}\|]'
            if not re.search(regex, language_section):
                page_content, language_section, start_position, end_position = add_section(page_content,
                    sections_in_page, section_name, section_to_add_order, language_section, start_position,
                                                                           end_position, line_content, language_code)

            s = re.search(regex, language_section)
            if s:
                final_section = language_section[s.end():]
            else:
                regex = r'\n=* *{{S\|' + sections_in_page[len(sections_in_page)-1][0]
                s = re.search(regex, language_section)
                if s:
                    if debug_level > d:
                        print(' ajout après les sous-sections')
                    final_section = language_section[s.end():]
                else:
                    final_section = None
                    print(' bug de section')

            # TODO page_content = add_line_content_into_section(page_content, line_content, final_section)
            line_content = trim(line_content)
            regex = r'\n?\n==* *{{S\|'
            s = re.search(regex, final_section)
            if s:
                if debug_level > d:
                    print(' ajout avant la sous-section suivante')
                page_content = page_content[:start_position] + language_section[:-len(final_section)] \
                       + final_section[:s.start()] \
                       + '\n' + line_content + final_section[s.start():] + page_content[start_position + end_position:]
            else:
                categories = language_section.find('\n[[Catégorie:')
                default_sort = language_section.find('\n{{clé de tri|')
                if categories != -1 and (categories < default_sort or default_sort == -1):
                    if debug_level > d:
                        print(' ajout avant les catégories')
                    page_content = page_content[:start_position] \
                                   + language_section[:language_section.find('\n[[Catégorie:')] \
                                   + line_content + '\n' + language_section[language_section.find('\n[[Catégorie:'):] \
                                   + page_content[start_position + end_position:]
                elif default_sort != -1:
                    if debug_level > d:
                        print(' ajout avant la clé de tri')
                    page_content = page_content[:start_position] \
                                   + language_section[:language_section.find('\n{{clé de tri|')] \
                                   + line_content + '\n' + language_section[language_section.find('\n{{clé de tri|'):] \
                                   + page_content[start_position + end_position:]
                else:
                    if debug_level > d:
                        print(' ajout en fin de section langue (donc saut de ligne)')
                    if language_section[-1:] != '\n':
                        line_content = '\n\n' + line_content
                    elif language_section[-2:] != '\n\n':
                        line_content = '\n' + line_content

                    page_content = page_content[:start_position] + language_section + line_content + '\n' \
                                    + page_content[start_position + end_position:]

    # TODO remove fix
    page_content = page_content.replace('\n\n* {{écouter|', '\n* {{écouter|')
    if debug_level > d:
        pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
    return page_content


def add_section(page_content, sections_in_page, section_name, section_to_add_order, language_section,
                start_position, end_position, line_content, language_code):
    d = 0
    o = 0
    while o < len(sections_in_page) and get_order_by_section_name(sections_in_page[o][0]) <= section_to_add_order:
        if debug_level > d:
            print(' ' + sections_in_page[o][0] + ' ' + str(get_order_by_section_name(sections_in_page[o][0])))
        o = o + 1
    if o > 0:
        o = o - 1
    if debug_level > d:
        print(' while ' + str(get_order_by_section_name(sections_in_page[o][0])) + ' <= '
              + str(section_to_add_order)
              + ' and ' + str(o) + ' < ' + str(len(sections_in_page)) + ' and '
              + sections_in_page[o][0] + ' != langue')

    # section_limit = str(sections_in_page[o][0])
    section_limit = sections_in_page[o][0]
    # TODO pb encodage : "étymologie" non fusionnée + "catégorie" = 1 au lieu de 20
    if language_section.find('{{S|' + section_limit) == -1 and section_limit != 'langue':
        if debug_level > d:
            print(' sites_errors d\'encodage sur "' + section_limit + '"')
        if debug_level > d:
            input(language_section)
        return page_content, language_section

    section_level = get_level_by_section_name(section_name)
    if section_limit == section_name:
        if debug_level > d:
            print(' ajout dans la sous-section existante "' + section_name + '" (car '
                  + str(get_order_by_section_name(section_limit)) + ' = ' + str(section_to_add_order)
                  + ')\n')
    elif section_name not in ['catégorie', 'clé de tri']:
        section_to_add = '\n\n' + section_level + ' {{S|' + section_name + '}} ' + section_level + '\n'
        if section_to_add_order >= get_order_by_section_name(section_limit):
            if debug_level > d:
                print(' ajout de la sous-section "' + section_name + '" après "' + section_limit + '" (car '
                      + str(section_to_add_order) + ' > ' + str(get_order_by_section_name(section_limit)) + ')')
            regex = r'{{S\|' + section_limit + r'[\|}]'
            s = re.search(regex, language_section)
            if section_limit == sections_in_page[-1][0]:
                if debug_level > d:
                    print(' ajout de la sous-section après la dernière de la section langue : ' + section_limit)
                categories = language_section.find('\n[[Catégorie:')
                default_sort = language_section.find('\n{{clé de tri|')
                if categories != -1 and (categories < default_sort or default_sort == -1):
                    if debug_level > d:
                        print('  avant les catégories')
                    page_content = page_content[:start_position] + language_section[:categories] \
                                                                + section_to_add \
                                                                + language_section[categories:]\
                                                                + page_content[start_position+end_position:]
                elif default_sort != -1:
                    if debug_level > d:
                        print('  avant la clé de tri')
                    page_content = page_content[:start_position] + language_section[:default_sort] + '\n' \
                                       + section_to_add + language_section[default_sort:] \
                                       + page_content[start_position+end_position:]
                else:
                    if debug_level > d:
                        print('  sans catégorie')
                    page_content = page_content[:start_position] + language_section + section_to_add \
                                        + page_content[start_position+end_position:]
                if debug_level > d + 1:
                    input(page_content)
            else:
                last_section_level = get_level_by_section_name(sections_in_page[o + 1][0])
                if debug_level > d:
                    print('   Saut des sections incluses dans la précédente (de niveau titre inférieur)')
                while o + 2 < len(sections_in_page) and len(section_level) < len(last_section_level):
                    o += 1
                    if debug_level > d:
                        print(' saut de ' + sections_in_page[o + 1][0])

                if debug_level > d:
                    print(' ajout de la sous-section "' + section_name + '" avant "' + sections_in_page[o + 1][0] + '"')
                regex = r'\n=* *{{S\|' + sections_in_page[o + 1][0]
                s = re.search(regex, language_section)
                if s:
                    if section_name in natures:
                        section_to_add = section_to_add.replace('}}', '|' + language_code + '}}')
                        if line_content[:1] == '#' or line_content[:2] == '\n#':
                            section_to_add += u"'''{{subst:PAGENAME}}''' {{genre ?|" + language_code + \
                                u"}} {{pluriel ?|" + language_code + u"}}\n"
                    page_content = page_content[:start_position] + language_section[:s.start()] + \
                        section_to_add + language_section[s.start():] + page_content[start_position+end_position:]
                else:
                    input(' bug section')
            language_section, start_position, end_position = get_language_section(page_content, language_code)
            if language_section is None:
                return page_content
        else:
            if debug_level > d:
                print(' ajout de "' + section_name + '" avant "' + section_limit + '" (car '
                      + str(section_to_add_order) + ' < ' + str(get_order_by_section_name(section_limit)) + ')')
            regex = r'\n=* *{{S\|' + section_limit
            s = re.search(regex, language_section)
            if s:
                page_content = page_content[:start_position] + language_section[:s.start()] + section_to_add\
                               + language_section[s.start():] + page_content[start_position+end_position:]
                language_section, start_position, end_position = get_language_section(page_content, language_code)
                if language_section is None:
                    return page_content
            else:
                print(' Error, cannot add section: ' + section_name)
    return page_content, language_section, start_position, end_position


def add_line_test(page_content, language_code='fr'):
    # TODO move to /tests
    page_content = add_category(page_content, language_code, 'Tests en français')
    page_content = add_line(page_content, language_code, 'prononciation', '* {{écouter|||lang=fr|audio=test.ogg}}')
    page_content = add_line(page_content, language_code, 'prononciation', '* {{écouter|||lang=fr|audio=test2.ogg}}')
    page_content = add_line(page_content, language_code, 'étymologie', ':{{étyl|test|fr}}')
    page_content = add_line(page_content, language_code, 'traductions', '{{trad-début}}\n123\n{{trad-fin}}')
    page_content = add_line(page_content, language_code, 'vocabulaire', '* [[voc]]')
    page_content = add_line(page_content, language_code, 'nom', '# Définition')
    page_content = add_line(page_content, language_code, 'nom', 'Note')
    return page_content


def add_pronunciation(page_content, language_code, section, line_content):
    if page_content == '' or language_code == '' or section == '' or line_content == '' \
            or line_content in page_content or '{{langue|' + language_code + '}}' not in page_content:
        return page_content

    # TODO generic preformator
    page_content = page_content.replace('{{S|Références}}', '{{S|références}}')
    if section == 'catégorie' and line_content.find('[[Catégorie:') == -1:
        line_content = '[[Catégorie:' + line_content + ']]'
    if section == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
        line_content = '{{clé de tri|' + line_content + '}}'

    # Recherche de l'ordre théorique de la section à ajouter
    section_number = get_order_by_section_name(section)
    if section_number == len(sections):
        if debug_level > 0:
            print(' ajout de ' + section + ' dans une section inconnue')
            print('  (car ' + str(len(sections)) + ' = ' + str(section_number) + ')')
        return page_content

    # Recherche de l'ordre réel de la section à ajouter
    old_language_section, l_start, l_end = get_language_section(page_content, language_code)
    if old_language_section is None:
        return page_content

    language_section = old_language_section
    # sections_in_page = re.findall("{{S\|([^}]+)}}", language_section)
    sections_in_page = re.findall(r"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", language_section)
    o = 0
    # TODO pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
    while o < len(sections_in_page) and sections_in_page[o][0] != 'langue' \
        and get_order_by_section_name(sections_in_page[o][0]) <= section_number:
        if debug_level > 0:
            print(' ' + sections_in_page[o][0] + ' ' + str(get_order_by_section_name(sections_in_page[o][0])))
        o = o + 1
    if debug_level > 0:
        print(' ' + str(len(sections_in_page)) + ' >? ' + str(o))
    if o == len(sections_in_page):
        if debug_level > 0:
            print(' section à ajouter dans le dernier paragraphe')
        # TODO if section == sections_in_page[-1][0]?
        if section not in ['catégorie', 'clé de tri']:
            if language_section.find('[[Catégorie:') != -1:
                if debug_level > 0:
                    print('  avant les catégories')
                language_section = language_section[:language_section.find('[[Catégorie:')] + \
                                   line_content + '\n' + language_section[language_section.find('[[Catégorie:'):]
            elif language_section.find('{{clé de tri') != -1:
                if debug_level > 0:
                    print('  avant la clé de tri')
                language_section = language_section[:language_section.find('{{clé de tri')] + \
                                   line_content + '\n' + language_section[language_section.find('{{clé de tri'):]
            else:
                if debug_level > 0:
                    print(' section à ajouter en fin de section langue')
                language_section = language_section + '\n' + line_content + '\n'
        else:
            if debug_level > 0:
                print(' section à ajouter en fin de section langue')
            language_section = language_section + '\n' + line_content + '\n'
    else:
        try:
            sectionLimit = str(sections_in_page[o][0])
        except UnicodeEncodeError:
            print('UnicodeEncodeError (relancer en Python3)', o, sections_in_page[o][0])
            return page_content
        o = o - 1
        if debug_level > 1:
            print(' position O : ' + o)
        if debug_level > 0:
            print(' ajout de "' + section + '" avant "' + repr(sectionLimit) + '"')
            print('  (car ' + str(get_order_by_section_name(sectionLimit)) + ' > ' + str(section_number) + ')')

        # Ajout après la section trouvée
        if language_section.find('{{S|' + sections_in_page[o][0]) == -1:
            print('sites_errors d\'encodage')
            return page_content

        end_of_language_section = language_section[language_section.rfind('{{S|' + sections_in_page[o][0]):]
        if debug_level > 1:
            input(end_of_language_section)
        if sections_in_page[o][0] != section and not section in ['catégorie', 'clé de tri']:
            if debug_level > 0:
                print(' ajout de la section "' + section + '" après "'+ sections_in_page[o][0] + '"')
            line_content = '\n' + sections_level[section_number] + ' {{S|' + section + '}} ' + \
                           sections_level[section_number] + '\n' + line_content
        else:
            if debug_level > 0:
                print(' ajout dans la section existante')
        if debug_level > 1:
            input(line_content)

        if end_of_language_section.find('\n==') == -1:
            regex = r'\n\[\[\w?\w?\w?:'
            if re.compile(regex).search(language_section):
                interwikis = re.search(regex, language_section).start()
                categories = language_section.find('\n[[Catégorie:')
                default_sort = language_section.find('\n{{clé de tri|')

                if (interwikis < categories or categories == -1) and (interwikis < default_sort
                                                                      or default_sort == -1):
                    if debug_level > 0:
                        print('  ajout avant les interwikis')
                    try:
                        language_section = language_section[:interwikis] + '\n' + line_content + '\n' \
                                           + language_section[interwikis:]
                    except BaseException as e:
                        print(str(e))
                        print(' pb regex interwiki')
                elif categories != -1 and (categories < default_sort or default_sort == -1):
                    if debug_level > 0:
                        print('  ajout avant les catégories')
                    language_section = language_section[:language_section.find('\n[[Catégorie:')] \
                                       + line_content + \
                        language_section[language_section.find('\n[[Catégorie:'):]
                elif default_sort != -1:
                    if debug_level > 0:
                        print('  ajout avant la clé de tri')
                    language_section = language_section[:language_section.find('\n{{clé de tri|')] \
                                       + line_content + \
                        language_section[language_section.find('\n{{clé de tri|'):]
                else:
                    if debug_level > 0:
                        print('  ajout en fin de section langue')
                    language_section = language_section + line_content + '\n'
            else:
                if debug_level > 0:
                    print('  ajout en fin de section langue')
                language_section = language_section + line_content + '\n'
        else:
            if debug_level > 0:
                print('  ajout standard')
            language_section = language_section[:-len(language_section)] + language_section[:-len(end_of_language_section)] + \
                end_of_language_section[:end_of_language_section.find('\n==')] + line_content + '\n' + \
                end_of_language_section[end_of_language_section.find('\n=='):]
    if language_section.find('\n* {{écouter|') != -1 and language_section.find('=== {{S|prononciation}} ===') == -1:
        language_section = language_section.replace('\n* {{écouter|', '\n\n=== {{S|prononciation}} ===\n* {{écouter|')

    language_section = language_section.replace('\n\n\n\n', '\n\n\n')
    page_content = page_content.replace(old_language_section, language_section)

    return page_content


def add_line_into_section(page_content, language_code, section, line_content):
    d = 1
    if debug_level > d:
        pywikibot.output("\n\03{red}---------------------------------------------\03{default}")
        print('\naddLineIntoSection "' + section + '"')
    if page_content != '' and language_code != '' and section != '' and line_content != '':
        if page_content.find(line_content) == -1 and page_content.find('{{langue|' + language_code + '}}') != -1:
            if section == 'catégorie' and line_content.find('[[Catégorie:') == -1:
                line_content = '[[Catégorie:' + line_content + ']]'
            if section == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
                line_content = '{{clé de tri|' + line_content + '}}'
    sections = re.findall(r"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", page_content)
    # TODO: complete parsing
    # input(str(sections))
    return page_content


def get_order_by_section_name(section):
    if debug_level > 0:
        print(' get_order_by_section_name()')
    s = 0
    try:
        s = sections.index(section)
        section_order = sections_order[s]
    except BaseException as e:
        print(str(e))
        section_order = 2  # Grammatical natures (ex: nom)
    if debug_level > 0:
        print('  ' + section + ' (' + str(s) + 'e) = ordre ' + str(section_order))
    return section_order


def get_level_by_section_name(section):
    if debug_level > 0:
        print(' get_level_by_section_name()')
    s = 0
    try:
        s = sections.index(section)
        section_level = sections_level[s]
    except BaseException as e:
        print(str(e))
        section_level = '==='  # Grammatical natures (ex: === {{S|nom)
    if debug_level > 0:
        print('  ' + section + ' (' + str(s) + 'e) = ordre ' + str(section_level))
    return section_level


# TODO: def addlanguage_codeToTemplate(final_page_content, page_content, current_template = None, language_code = None):
def add_language_code_with_named_parameter_to_template(
    final_page_content,
    page_content,
    current_template=None,
    language_code=None,
    end_position=0
):        
    if debug_level > 0:
        pywikibot.output("  Template with lang=: \03{green}" + current_template + u"\03{default}")
    page_content2 = page_content[end_position + 1:]

    is_category = current_template != 'cf' or (page_content2.find('}}') > end_position + 1
        and (page_content2.find(':') == -1 or page_content2.find(':') > page_content2.find('}}'))
        and page_content2[:1] != '#')
    has_subtemplate_included = False
    regex = r''
    if page_content.find('}}') > page_content.find('{{') != -1:
        # Inifnite loop in [[tomme]] on ^date\|[^{}]*({{(.*?)}}|.)+[^{}]*\|lang=
        regex = r'^' + re.escape(current_template) + r'\|[^{}]*({{(.*?)}}|.)+[^{}]*\|lang='
        if re.search(regex, page_content):
            has_subtemplate_included = True
    if debug_level > 1:
        print('  ' + page_content.find('lang=') == -1 or page_content.find('lang=') > page_content.find('}}'))
        print('  ' + is_category)
        print('  ' + str(not has_subtemplate_included))
        print('   ' + regex)
        if has_subtemplate_included:
            print(' ' + page_content[re.search(regex, page_content).start():re.search(regex, page_content).end()])

    # TODO syntax has_parameters(['lang', 'lang1'])
    if (page_content.find('lang=') == -1 or page_content.find('lang=') > page_content.find('}}')) and \
        (page_content.find('langue=') == -1 or page_content.find('langue=') > page_content.find('}}')) and \
        (page_content.find('lang1=') == -1 or page_content.find('lang1=') > page_content.find('}}')) and \
        is_category and not has_subtemplate_included and language_code is not None:
        if debug_level > 0:
            print('   "lang=" addition')
        while page_content2.find('{{') < page_content2.find('}}') and page_content2.find('{{') != -1:
            page_content2 = page_content2[page_content2.find('}}')+2:]
        if page_content.find('lang=') == -1 or page_content.find('lang=') > page_content.find('}}'):
            if debug_level > 1:
                print('    at ' + str(end_position))
            final_page_content = final_page_content + current_template + '|lang=' + language_code\
                                 + page_content[end_position:page_content.find('}}') + 2]
            page_content = page_content[page_content.find('}}')+2:]
            return final_page_content, page_content
        else:
            if debug_level > 0:
                print('    "lang=" addition cancellation')
            return next_template(final_page_content, page_content)

    else:
        if debug_level > 0:
            print('   "lang=" already present')
        return next_template(final_page_content, page_content)


def next_template(final_page_content, current_page_content, current_template=None, language_code=None):
    if language_code is None:
        final_page_content = final_page_content + current_page_content[:current_page_content.find('}}')+2]
    else:
        final_page_content = final_page_content + current_template + "|" + language_code + '}}'
    current_page_content = current_page_content[current_page_content.find('}}')+2:]
    return final_page_content, current_page_content


def next_translation_template(final_page_content, current_page_content, result='-'):
    final_page_content = final_page_content + current_page_content[:len('trad')] + result
    current_page_content = current_page_content[current_page_content.find('|'):]
    return final_page_content, current_page_content


def remove_false_homophons(page_content, language_code, page_name, related_page_name, summary):
    if debug_level > 1:
        print('\nremove_false_homophons(' + related_page_name + ')')
    regex = r"==== *{{S\|homophones\|" + language_code + u"}} *====\n\* *'''" + re.escape(page_name) + \
        r"''' *{{cf\|[^\|]*\|?" + re.escape(related_page_name) + r"[\|}][^\n]*\n"
    if re.search(regex, page_content):
        page_content = re.sub(regex, "==== {{S|homophones|" + language_code + u"}} ====\n", page_content)
        summary = summary + ', homophone erroné'
    regex = r"==== *{{S\|homophones\|" + language_code + u"}} *====\n\* *\[\[[^}\n]+{{cf\|[^\|]*\|?" \
            + re.escape(related_page_name) + r"[\|}][^\n]*\n?"
    if re.search(regex, page_content):
        page_content = re.sub(regex, "==== {{S|homophones|" + language_code + u"}} ====\n", page_content)
        summary = summary + ', homophone erroné'
    regex = r"==== *{{S\|homophones\|" + language_code + u"}} *====\n\* *\[\[" + re.escape(related_page_name) \
            + r"\]\](\n|$)"
    if re.search(regex, page_content):
        page_content = re.sub(regex, "==== {{S|homophones|" + language_code + u"}} ====\n", page_content)
        summary = summary + ', homophone erroné'

    regex = r"=== {{S\|prononciation}} ===\n==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
    if re.search(regex, page_content): page_content = re.sub(regex, r'\1', page_content)
    regex = r"==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
    if re.search(regex, page_content): page_content = re.sub(regex, r'\1', page_content)

    return page_content, summary


def rec_anagram(counter):
    # Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1


def get_anagram(word):
    return rec_anagram(collections.Counter(word))


def sort_translations(page_content, summary):
    summary2 = ''
    if debug_level > 0:
        print(' Translations sorting, by adding {{T}} if needed')
    if debug_level > 1:
        print(' First translation detection')
    regex = r'\* ?{{[a-z][a-z][a-z]?-?[a-z]?[a-z]?[a-z]?}} :'
    final_page_content = ''
    while page_content.find('{{trad-début') != -1:
        final_page_content = final_page_content + page_content[:page_content.find('{{trad-début')]
        page_content = page_content[page_content.find('{{trad-début'):]
        final_page_content = final_page_content + page_content[:page_content.find('\n')+1]
        page_content = page_content[page_content.find('\n')+1:]
        if re.search(regex, page_content) and re.search(regex, page_content).start() < page_content.find('{{'):
            if debug_level > 0:
                print(' {{T}} addition')
            page_content = page_content[:page_content.find('{{')+2] + 'T|' + page_content[page_content.find('{{')+2:]
    page_content = final_page_content + page_content
    final_page_content = ''

    while page_content.find('{{T|') != -1:
        final_page_content = final_page_content + page_content[:page_content.find('{{T|')]
        page_content = page_content[page_content.find('{{T|'):]
        if debug_level > 2:
            print(' Ajout des T')
        page_content2 = page_content[page_content.find('\n'):]
        if re.search(regex, page_content2):
            if re.search(regex, page_content2).start() < page_content2.find('{{'):
                if debug_level > 0:
                    print('Ajout d\'un modèle T')
                page_content = page_content[:page_content.find('\n') + page_content2.find('{{')+2] + 'T|' + \
                    page_content[page_content.find('\n') + page_content2.find('{{')+2:]

        language = get_next_translation(page_content)
        if language != '' and (final_page_content.find('<!--') == -1 or final_page_content.find('-->') != -1):
            language2 = 'zzz'
            if final_page_content.rfind('\n') == -1 or page_content.find('\n') == -1:
                break
            current_translation = final_page_content[final_page_content.rfind('\n'):] \
                                  + page_content[:page_content.find('\n')]
            next_translations = ''
            final_page_content = final_page_content[:final_page_content.rfind('\n')]
            page_content = page_content[page_content.find('\n'):]
            while language2 > language \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{S|') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{trad-début') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{trad-fin') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{(') \
                    and final_page_content.rfind('{{T') != final_page_content.rfind('{{T|conv'):

                language2 = get_next_language_translation(final_page_content)
                if debug_level > 1:
                    print(language2, language)
                if language2 != '' and language2 > language:
                    if debug_level > 1:
                        print(language2 + ' > ' + language)
                    if final_page_content.rfind('\n') > final_page_content.rfind('trad-début'):
                        next_translations = final_page_content[final_page_content.rfind('\n'):] + next_translations
                        final_page_content = final_page_content[:final_page_content.rfind('\n')]
                        summary2 += ', ' + language2 + ' > ' + language
                    elif final_page_content.rfind('\n') != -1:
                        # Cas de la première de la liste
                        current_translation = final_page_content[final_page_content.rfind('\n'):] + current_translation
                        final_page_content = final_page_content[:final_page_content.rfind('\n')]
                    if debug_level > 1:
                        try:
                            print(final_page_content[final_page_content.rfind('\n'):].encode('utf-8'))
                        except UnicodeEncodeError as e:
                            print(str(e), final_page_content.rfind('\n'))
                            input(final_page_content)
                else:
                    break
            final_page_content = final_page_content + current_translation + next_translations
        elif page_content.find('\n') != -1:
            if debug_level > 0:
                print(' Retrait de commentaire de traduction : ' + page_content[:page_content.find('\n')+1])
            final_page_content = final_page_content + page_content[:page_content.find('\n')]
            page_content = page_content[page_content.find('\n'):]
        else:
            final_page_content = final_page_content + page_content
            page_content = ''

        final_page_content = final_page_content + page_content[:page_content.find('\n')+1]
        page_content = page_content[page_content.find('\n')+1:]
        if debug_level > 2:
            print(final_page_content)
        if debug_level > 2:
            print(page_content)
        if debug_level > 1:
            print('')
    page_content = final_page_content + page_content

    if debug_level > 1:
        input(' fin du tri des traductions')
    if summary2 != '':
        summary += ', traductions :' + summary2[1:]
    return page_content, summary


def get_next_translation(page_content):
    language = page_content[page_content.find('{{T|')+4:page_content.find('}')]

    return get_langage_name_by_code(language)


def get_next_language_translation(final_page_content):
    language = final_page_content[final_page_content.rfind('{{T|')+len('{{T|'):]
    language = language[:language.find('}}')]
    return get_langage_name_by_code(language)


def get_langage_name_by_code(language_code):
    language_name = ''
    if language_code.find('|') != -1:
        language_code = language_code[:language_code.find('|')]
    if language_code != '':
        if len(language_code) > 3 and language_code.find('-') == -1:
            if debug_level > 0:
                print('No ISO code (ex: gallo)')
            language_name = language_code
        else:
            try:
                # Works in Python 2 without future:
                # language_name = sort_by_encoding(languages[language_code].decode('utf8'), 'UTF-8')
                # "éa" > "ez":
                # language_name = sort_by_encoding(languages[language_code])
                language_name = sort_by_encoding(languages[language_code], 'UTF-8')
                if debug_level > 1:
                    print(' Language name: ' + language_name)
            except KeyError:
                if debug_level > 0:
                    print('KeyError l 2556')
            except UnboundLocalError:
                if debug_level > 0:
                    print('UnboundLocalError l 2559')
    return language_name


def get_language_code_by_name(language_code):
    if language_code == 'Italian':
        language_code = 'it'
    elif language_code == 'Irish':
        language_code = 'ga'
    elif language_code == 'German':
        language_code = 'de'
    elif language_code == 'Middle English':
        language_code = 'enm'
    elif language_code == 'Old English':
        language_code = 'ang'
    elif language_code == 'Dutch':
        language_code = 'nl'
    elif language_code == 'Romanian':
        language_code = 'ro'
    elif language_code == 'Spanish':
        language_code = 'es'
    elif language_code == 'Catalan':
        language_code = 'ca'
    elif language_code == 'Portuguese':
        language_code = 'pt'
    elif language_code == 'Russian':
        language_code = 'ru'
    elif language_code == 'French':
        language_code = 'fr'
    elif language_code == 'Scots':
        language_code = 'sco'
    elif language_code == 'Chinese':
        language_code = 'zh'
    elif language_code == 'Mandarin':
        language_code = 'zh'
    elif language_code == 'Japanese':
        language_code = 'ja'
    return language_code


def get_language_code_ISO693_1_from_ISO693_3(code):
    if code == 'ben':
        return 'bn'
    elif code == 'epo':
        return 'eo'
    elif code == 'ori':
        return 'or'
    elif code == 'pol':
        return 'pl'
    elif code == 'por':
        return 'pt'
    elif code in ['afr', 'ara', 'cat', 'deu', 'eng', 'eus', 'fra', 'ita', 'nld', 'oci', 'rus', 'zho']:
        return code[:2]
    return code


def add_banner_see(page_name, page_content, summary):
    if debug_level > 0:
        print(' {{voir}}')
    if debug_level == 1:
        return page_content, summary
    default_sort = sort_by_encoding(page_name)

    if page_content.find('{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{lc:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].lower() + page_name[1:] + \
                page_content[page_content.find('{{voir|{{lc:{{PAGENAME}}}}}}')+len('{{voir|{{lc:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{lc:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].upper() + page_name[1:] + \
                page_content[page_content.find('{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len('{{voir|{{ucfirst:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{ucfirst:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{LC:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].lower() + page_name[1:] + \
                page_content[page_content.find('{{voir|{{LC:{{PAGENAME}}}}}}')+len('{{voir|{{LC:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{LC:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].upper() + page_name[1:] + \
                page_content[page_content.find('{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len('{{voir|{{UCFIRST:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{UCFIRST:{{PAGENAME}}}}'
    if page_content.find('{{voir|') == -1 and page_content.find('{{voir/') == -1:
        # TODO: always empty
        PageVoir = ''
        # Liste de toutes les pages potentiellement "à voir"
        pages_keys = page_name
        if pages_keys.find(page_name.lower()) == -1:
            pages_keys = pages_keys + '|' + page_name.lower()
        if pages_keys.find(page_name.upper()) == -1:
            pages_keys = pages_keys + '|' + page_name.upper()
        if pages_keys.find(page_name[:1].lower() + page_name[1:]) == -1:
            pages_keys = pages_keys + '|' + page_name[:1].lower() + page_name[1:]
        if pages_keys.find(page_name[:1].upper() + page_name[1:]) == -1:
            pages_keys = pages_keys + '|' + page_name[:1].upper() + page_name[1:]
        if pages_keys.find('-' + page_name[:1].lower() + page_name[1:]) == -1:
            pages_keys = pages_keys + '|-' + page_name[:1].lower() + page_name[1:]
        if pages_keys.find(page_name[:1].lower() + page_name[1:] + '-') == -1:
            pages_keys = pages_keys + '|' + page_name[:1].lower() + page_name[1:] + '-'
        if pages_keys.find('-') != -1: pages_keys = pages_keys + '|' + pages_keys.replace('-', '')
        diacritics = [['a', u'á', u'à', u'ä', u'â', u'ã'], ['c', u'ç'], ['e', u'é', u'è', u'ë', u'ê'],
                      ['i', u'í', u'ì', u'ï', u'î'], ['n', u'ñ'], ['o', u'ó', u'ò', u'ö', u'ô', u'õ'],
                      ['u', u'ú', u'ù', u'ü', u'û']]
        for l in range(0, len(diacritics)):
            for d in range(0, len(diacritics[l])):
                if page_name.find(diacritics[l][d]) != -1:
                    if debug_level > 1:
                        print('Titre contenant : ' + diacritics[l][d])
                    letter = diacritics[l][d]
                    for diac in range(0, len(diacritics[l])):
                        pages_keys = pages_keys + '|' + page_name.replace(letter, diacritics[l][diac])
        if pages_keys.find(default_sort) == -1:
            # exception ? and page_content.find('{{langue|eo}}') == -1
            pages_keys = pages_keys + '|' + default_sort

        # Filtre des pages de la liste "à voir"
        remaining_pages_keys = pages_keys + '|'
        pages_keys = ''
        PagesVoir = ''
        if debug_level > 0:
            print(' Recherche des clés...')
        while remaining_pages_keys != '':
            if debug_level > 1:
                print(remaining_pages_keys)
            current_page = remaining_pages_keys[:remaining_pages_keys.find('|')]
            remaining_pages_keys = remaining_pages_keys[remaining_pages_keys.find('|')+1:]
            if current_page == '':
                continue
            key_page = Page(site, current_page)
            key_page_content = get_content_from_page(key_page)
            if key_page_content is not None:
                if debug_level > 1:
                    print(pages_keys)
                if pages_keys.find('|' + current_page) == -1:
                    pages_keys = pages_keys + '|' + current_page
                if key_page_content.find('{{voir|') != -1:
                    page_content_key2 = key_page_content[key_page_content.find('{{voir|')+len('{{voir|'):]
                    PagesVoir = PagesVoir + '|' + page_content_key2[:page_content_key2.find('}}')]
                elif key_page_content.find('{{voir/') != -1:
                    page_content_key2 = key_page_content[key_page_content.find('{{voir/')+len('{{voir/'):]
                    page_content = '{{voir/' + page_content_key2[:page_content_key2.find('}}')+3] + page_content
                    pageMod = Page(site, 'Template:voir/' + page_content_key2[:page_content_key2.find('}}')])
                    page_contentModBegin = get_content_from_page(pageMod)
                    if page_contentModBegin is None:
                        break
                    page_contentMod = page_contentModBegin
                    if page_contentMod.find('!') == -1:
                        if page_contentMod.find(page_name) == -1:
                            page_contentMod = page_contentMod[:page_contentMod.find('}}')] + '|' + page_name + \
                                page_contentMod[page_contentMod.find('}}'):len(page_contentMod)]
                        if page_contentMod.find(PageVoir) == -1:
                            page_contentMod = page_contentMod[:page_contentMod.find('}}')] + '|' + PageVoir + \
                                page_contentMod[page_contentMod.find('}}'):len(page_contentMod)]
                    if debug_level > 0:
                        print('remaining_pages_keys vide')
                    else:
                        if page_contentMod != page_contentModBegin:
                            save_page(pageMod, page_contentMod, summary)
                    remaining_pages_keys = ''
                    break

        if PagesVoir != '':
            if debug_level > 0:
                print(' Filtre des doublons...')
            if debug_level > 1:
                print('  avant : ' + PagesVoir)
            PagesVoir = PagesVoir + '|'
            while PagesVoir.find('|') != -1:
                if pages_keys.find(PagesVoir[:PagesVoir.find('|')]) == -1:
                    pages_keys = pages_keys + '|' + PagesVoir[:PagesVoir.find('|')]
                PagesVoir = PagesVoir[PagesVoir.find('|')+1:]
            if debug_level > 1:
                print('  après : ' + pages_keys)
        if debug_level > 2: input(pages_keys)

        if debug_level > 0:
            print(' Balayage de toutes les pages "à voir"...')
        if pages_keys != '':
            while pages_keys[:1] == '|':
                pages_keys = pages_keys[1:]
        if pages_keys != page_name:
            if debug_level > 0:
                print('  Différent de la page courante')
            remaining_pages_keys = pages_keys + '|'
            key_page = None
            while remaining_pages_keys.find('|') != -1:
                current_page = remaining_pages_keys[:remaining_pages_keys.find('|')]
                if current_page == '':
                    if debug_level > 0:
                        print('current_page vide')
                    break
                remaining_pages_keys = remaining_pages_keys[remaining_pages_keys.find('|')+1:]
                if current_page != page_name and current_page.find('*') == -1:
                    key_page = Page(site, current_page)
                    page_content_key_start = get_content_from_page(key_page)
                else:
                    page_content_key_start = page_content
                if page_content_key_start is not None and key_page is not None and ':' not in key_page.title() \
                        and '{' not in key_page.title():
                    key_page_content = page_content_key_start
                    if key_page_content.find('{{voir/') != -1:
                        if debug_level > 0:
                            print(' {{voir/ trouvé')
                        break
                    elif key_page_content.find('{{voir|') != -1:
                        if debug_level > 0:
                            print(' {{voir| trouvé')
                        if pages_keys.find('|' + current_page) != -1:
                            page_content_key2 = key_page_content[key_page_content.find('{{voir|')+len('{{voir|'):]
                            key_page_content = key_page_content[:key_page_content.find('{{voir|')+len('{{voir|')] \
                             + pages_keys[:pages_keys.find('|' + current_page)] \
                             + pages_keys[pages_keys.find('|' + current_page)+len('|' + current_page):] \
                             + key_page_content[key_page_content.find('{{voir|')+len('{{voir|')
                                                + page_content_key2.find('}}'):]
                        else:  # Cas du premier
                            page_content_key2 = key_page_content[key_page_content.find('{{voir|')+len('{{voir'):]
                            key_page_content = key_page_content[:key_page_content.find('{{voir|')+len('{{voir|')] \
                             + pages_keys[len(current_page):] \
                             + key_page_content[key_page_content.find('{{voir|')+len('{{voir')
                                                + page_content_key2.find('}}'):]
                        if key_page_content != page_content_key_start:
                            if current_page == page_name:
                                page_content = key_page_content
                            else:
                                if debug_level > 0:
                                    print(' Première savePage dédiée à {{voir}}')
                                else:
                                    save_page(key_page, key_page_content, summary)
                    else:
                        if pages_keys.find('|' + current_page) != -1:
                            key_page_content = '{{voir|' + pages_keys[:pages_keys.find('|' + current_page)] \
                             + pages_keys[pages_keys.find('|' + current_page)+len('|' + current_page):] + '}}\n' \
                             + key_page_content
                        else:    # Cas du premier
                            key_page_content = '{{voir' + pages_keys[len(current_page):len(pages_keys)] + '}}\n' \
                            + key_page_content
                        if current_page == page_name:
                            page_content = key_page_content
                        else:    
                            if debug_level > 0:
                                print(' Deuxième savePage dédiée à {{voir}}')
                            else:
                                save_page(key_page, key_page_content, summary)

    elif page_content.find('{{voir|') != -1:
        if debug_level > 0:
            print('  Identique à la page courante')
        page_content2 = page_content[page_content.find('{{voir|'):]
        if page_content2.find('|' + page_name + '|') != -1 and page_content2.find('|' + page_name + '|') \
                < page_content2.find('}}'):
            page_content = page_content[:page_content.find('{{voir|') + page_content2.find('|' + page_name + '|')] \
                + page_content[page_content.find('{{voir|') + page_content2.find('|' + page_name + '|')+len('|'
                                                                                                            + page_name):]
        if page_content2.find('|' + page_name + '}') != -1 and page_content2.find('|' + page_name + '}') \
                < page_content2.find('}}'):
            page_content = page_content[:page_content.find('{{voir|') + page_content2.find('|' + page_name + '}')] \
                + page_content[page_content.find('{{voir|') + page_content2.find('|' + page_name + '}')+len('|'
                                                                                                    + page_name):]

    if debug_level > 0:
        print(' Nettoyage des {{voir}}...')
    if page_content.find('{{voir}}\n') != -1:
        page_content = page_content[:page_content.find('{{voir}}\n')] \
        + page_content[page_content.find('{{voir}}\n')+len('{{voir}}\n'):]
    if page_content.find('{{voir}}') != -1:
        page_content = page_content[:page_content.find('{{voir}}')] \
        + page_content[page_content.find('{{voir}}')+len('{{voir}}'):]
    page_content = update_html_to_unicode(page_content)
    page_content = page_content.replace('}}&#32;[[', '}} [[')
    page_content = page_content.replace(']]&#32;[[', ']] [[')
    regex = r'\[\[([^\]]*)\|\1\]\]'
    if re.search(regex, page_content):
        if debug_level > 0:
            print('Lien interne inutile')
        page_content = re.sub(regex, r'[[\1]]', page_content)
    return page_content, summary


def format_sections(page_content, summary):
    if debug_level > 0:
        print(' format_sections()')
    regex = r'{{=([a-z\-]+)=}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{langue|\1}}', page_content)

    # Titres en minuscules
    # page_content = re.sub(r'{{S\|([^}]+)}}', r'{{S|' + r'\1'.lower() + r'}}', page_content)
    for f in re.findall("{{S\|([^}]+)}}", page_content):
        page_content = page_content.replace(f, f.lower())

    # Alias peu intuitifs des sections avec langue
    page_content = page_content.replace('{{S|adj|', '{{S|adjectif|')
    page_content = page_content.replace('{{S|adjectifs|', '{{S|adjectif|')
    page_content = page_content.replace('{{S|adj-num|', '{{S|adjectif numéral|')
    page_content = page_content.replace('{{S|adv|', '{{S|adverbe|')
    page_content = page_content.replace('{{S|class|', '{{S|classificateur|')
    page_content = page_content.replace('{{S|drv}}', '{{S|dérivés}}')
    page_content = page_content.replace('{{S|homo|', '{{S|homophones|')
    page_content = page_content.replace('{{S|homo}}', '{{S|homophones}}')
    page_content = page_content.replace('{{S|interj|', '{{S|interjection|')
    page_content = page_content.replace('{{S|locution adverbiale', '{{S|adverbe')
    page_content = page_content.replace('{{S|locution phrase|', '{{S|locution-phrase|')
    page_content = page_content.replace('{{S|nom commun|', '{{S|nom|')
    page_content = page_content.replace('{{S|nom-fam|', '{{S|nom de famille|')
    page_content = page_content.replace('{{S|nom-pr|', '{{S|nom propre|')
    page_content = page_content.replace('{{S|pron}}', '{{S|prononciation}}')
    page_content = page_content.replace('{{S|symb|', '{{S|symbole|')
    page_content = page_content.replace('{{S|verb|', '{{S|verbe|')
    page_content = page_content.replace('{{S|apparentés étymologiques', '{{S|apparentés')
    page_content = page_content.replace('{{S|modphon}', '{{S|modification phonétique}')
    page_content = page_content.replace('{{S|mutation}', '{{S|modification phonétique}')
    # Alias peu intuitifs des sections sans langue
    page_content = re.sub(r'{{S\| ?abr[éèe]v(iations)?\|?[a-z\- ]*}}', '{{S|abréviations}}', page_content)
    page_content = re.sub(r'{{S\| ?anagr(ammes)?\|?[a-z\- ]*}}', '{{S|anagrammes}}', page_content)
    page_content = re.sub(r'{{S\| ?anciennes orthographes?\|?[a-z\- ]*}}', '{{S|anciennes orthographes}}', page_content)
    page_content = re.sub(r'{{S\| ?ant(onymes)?\|?[a-z\- ]*}}', '{{S|antonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?app(arentés)?\|?[a-zé]*}}', '{{S|apparentés}}', page_content)
    page_content = re.sub(r'{{S\| ?apr\|?[a-zé]*}}', '{{S|apparentés}}', page_content)
    page_content = re.sub(r'{{S\| ?compos(és)?\|?[a-zé]*}}', '{{S|composés}}', page_content)
    page_content = re.sub(r'{{S\| ?dial\|?[a-z\- ]*}}', '{{S|variantes dialectales}}', page_content)
    page_content = re.sub(r'{{S\| ?dimin(inutifs)?\|?[a-z\- ]*}}', '{{S|diminutifs}}', page_content)
    page_content = re.sub(r'{{S\| ?d[éèe]riv[éèe]s?(\|[a-z\- ]*}}|}})', '{{S|dérivés}}', page_content)
    page_content = re.sub(r'{{S\| ?drv\|?[a-z\- ]*}}', '{{S|dérivés}}', page_content)
    page_content = re.sub(r'{{S\| ?dérivés int\|?[a-z\- ]*}}', '{{S|dérivés autres langues}}', page_content)
    page_content = re.sub(r'{{S\| ?drv-int\|?[a-z\- ]*}}', '{{S|dérivés autres langues}}', page_content)
    page_content = re.sub(r'{{S\| ?[éèe]tym(ologie)?\|?[a-z\- ]*}}', '{{S|étymologie}}', page_content)
    page_content = re.sub(r'{{S\| ?exp(ressions)?\|?[a-z\- ]*}}', '{{S|expressions}}', page_content)
    page_content = re.sub(r'{{S\| ?gent(ilés)?\|?[a-zé]*}}', '{{S|gentilés}}', page_content)
    page_content = re.sub(r'{{S\| ?faux-amis?\|?[a-zé]*}}', '{{S|faux-amis}}', page_content)
    page_content = re.sub(r'{{S\| ?holo(nymes)?\|?[a-z\- ]*}}', '{{S|holonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?hyper(onymes)?\|?[a-z\- ]*}}', '{{S|hyperonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?hypo(nymes)?\|?[a-z\- ]*}}', '{{S|hyponymes}}', page_content)
    page_content = re.sub(r'{{S\| ?m[éèe]ro(nymes)?\|?[a-z\- ]*}}', '{{S|méronymes}}', page_content)
    page_content = re.sub(r'{{S\| ?notes?(\|?[a-z ]*)?}}', '{{S|notes}}', page_content)
    page_content = re.sub(r'{{S\| ?paro(nymes)?\|?[a-z\- ]*}}', '{{S|paronymes}}', page_content)
    page_content = re.sub(r'{{S\| ?phrases?\|?[a-z\- ]*}}', '{{S|phrases}}', page_content)
    page_content = re.sub(r'{{S\| ?pron(onciation)?\|?[a-z\- ]*}}', '{{S|prononciation}}', page_content)
    page_content = re.sub(r'{{S\| ?q-syn\|?[a-z\- ]*}}', '{{S|quasi-synonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?quasi[- ]syn(onymes)?\|?[a-z\- ]*}}', '{{S|quasi-synonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?r[éèe]f[a-zé]*\|?[a-z\- ]*}}', '{{S|références}}', page_content)
    page_content = re.sub(r'{{S\| ?syn(onymes)?\|?[a-z\- ]*}}', '{{S|synonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?taux de reconnaissance\|?[a-z\- ]*}}', '{{S|taux de reconnaissance}}', page_content)
    page_content = re.sub(r'{{S\| ?trad(uctions)?\|?[a-z]*}}', '{{S|traductions}}', page_content)
    page_content = re.sub(r'{{S\| ?trad-trier\|?[a-z\- ]*}}', '{{S|traductions à trier}}', page_content)
    page_content = re.sub(r'{{S\| ?traductions à trier\|?[a-z\- ]*}}', '{{S|traductions à trier}}', page_content)
    page_content = re.sub(r'{{S\| ?variantes dial\|?[a-z\- ]*}}', '{{S|variantes dialectales}}', page_content)
    page_content = re.sub(r'{{S\| ?variantes dialectales\|?[a-z\- ]*}}', '{{S|variantes dialectales}}', page_content)
    page_content = re.sub(r'{{S\| ?var[a-z]*[- ]ortho(graphiques)?\|?[a-z\- ]*}}', '{{S|variantes orthographiques}}', page_content)
    page_content = re.sub(r'{{S\| ?var(iantes)?\|?[a-z\-]*}}', '{{S|variantes}}', page_content)
    page_content = re.sub(r'{{S\| ?voc(abulaire)?\|?[a-z\- ]*}}', '{{S|vocabulaire}}', page_content)
    page_content = re.sub(r'{{S\| ?vocabulaire apparenté\|?[a-z\- ]*}}', '{{S|vocabulaire}}', page_content)
    page_content = re.sub(r'{{S\| ?voir( aussi)?\|?[a-z\- ]*}}', '{{S|voir aussi}}', page_content)
    page_content = page_content.replace('{{S|descendants}}', '{{S|dérivés autres langues}}')
    page_content = page_content.replace('num=1|num=', 'num=1')
    regex = r'({{trad\-fin}}[^={]+)(\n==== {{S\|homophones)'
    s = re.search(regex, page_content)
    if s:
        page_content = page_content.replace(s.group(1) + s.group(2), s.group(1) + '\n=== {{S|prononciation}} ==='
                                            + s.group(2))

    regex = r"(==== {{S\|dérivés autres langues}} ====" + r"(:?\n\* *{{L\|[^\n]+)?"*10 + r"\n\* *{{)T\|"
    for i in range(10):
        page_content = re.sub(regex, r'\1L|', page_content)

    regex = r"\n=* *({{langue\|[^}]+}}) *=*\n"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\n== \1 ==\n", page_content)

    regex = r'({{S\|[^}]+)€'
    while re.search(regex, page_content):
        page_content = re.sub(regex, r'\1⿕', page_content)

    return page_content, summary


def format_translations(page_content, summary):
    if debug_level > 0:
        print(' format_translations()')
    regex = r'({{langue\|(?!fr}).*}[^€]*)\n=* *{{S\|traductions}} *=*\n*{{trad\-début}}\n{{ébauche\-trad}}\n{{trad\-fin}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1', page_content)
        summary = summary + ', retrait de {{S|traductions}}'

    regex = r'({{langue\|(?!fr}).*}[^€]*)\n=* *{{S\|traductions}} *=*\n*{{\(}}\n{{ébauche\-trad}}\n{{\)}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1', page_content)
        summary = summary + ', retrait de {{S|traductions}}'

    # Formatage général des traductions
    page_content = page_content.replace('{{trad|', '{{trad-|')
    page_content = page_content.replace('{{(}}\n{{ébauche-trad}}\n{{)}}', '')
    page_content = page_content.replace('{{trad-début|{{trad-trier}}}}', '{{trad-trier}}\n{{trad-début}}')
    page_content = page_content.replace('{{trad-début|{{trad-trier|fr}}}}', '{{trad-trier}}\n{{trad-début}}')

        # 1) Suppression de {{ébauche-trad|fr}} (WT:PPS)
    page_content = page_content.replace(r'{{ébauche-trad|fr}}', '{{ébauche-trad}}')
    regex = r'{{ébauche\-trad\|fr}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, '{{ébauche-trad}}', page_content)

        # 2) Aucun modèle d'ébauche en dehors d'une boite déroulante
    page_content = page_content.replace(r'{{ébauche-trad}}\n{{trad-début}}', '{{trad-début}}\n{{ébauche-trad}}')
    regex = r'{{ébauche\-trad}}\n{{trad\-début}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, '{{trad-début}}\n{{ébauche-trad}}', page_content)

    page_content = page_content.replace(r'==== {{S|traductions}} ====\n{{ébauche-trad}}\n', 
        '==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n')
    regex = r'==== {{S\|traductions}} ====\n{{ébauche\-trad}}(\n<![^>]+>)*(\n|$)'
    if re.search(regex, page_content):
        if debug_level > 0: print(' ébauche sans boite')
        page_content = re.sub(regex, '==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad|en}}\n{{trad-fin}}\n',
            page_content)

        # 3) Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
    page_content = page_content.replace(r'<!--* {{T|en}} : {{trad|en|}}-->', '')     # bug ?
    regex = r'<!\-\-[^{>]*{{T\|[^>]+>\n?'
    if re.search(regex, page_content):
        if debug_level > 0: print(' Commentaire trouvé l 1517')
        page_content = re.sub(regex, '', page_content)
    regex = r'{{ébauche\-trad}}{{'
    if re.search(regex, page_content):
        page_content = re.sub(regex, '{{ébauche-trad}}\n{{', page_content)

    while page_content.find('{{trad-fin}}\n* {{T|') != -1:
        page_content2 = page_content[page_content.find('{{trad-fin}}\n* {{T|'):]
        delta = page_content2.find('\n')+1
        page_content2 = page_content2[delta:]
        if page_content2.find('\n') != -1:
            if debug_level > 0: print(page_content2[:page_content2.find('\n')+1])
            if page_content2[:page_content2.find('\n')+1].find('trier') != -1: break
            page_content = page_content[:page_content.find('{{trad-fin}}\n* {{T|'):] + \
                page_content2[:page_content2.find('\n')+1] + '{{trad-fin}}\n' + \
                page_content[page_content.find('{{trad-fin}}\n* {{T|')+delta+page_content2.find('\n')+1:]
        else:
            if debug_level > 0: print(page_content2)
            if page_content2[:len(page_content2)].find('trier') != -1: break
            page_content = page_content[:page_content.find('{{trad-fin}}\n* {{T|'):] + \
                page_content2[:len(page_content2)] + '{{trad-fin}}\n' + \
                page_content[page_content.find('{{trad-fin}}\n* {{T|')+delta+len(page_content2):]
    regex = r'}}{{trad\-fin}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, '}}\n{{trad-fin}}', page_content)

    while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(page_content):
        i1 = re.search(r'{{T\|.*\n\n\*[ ]*{{T\|', page_content).end()
        page_content = page_content[:i1][:page_content[:i1].rfind('\n')-1] \
                       + page_content[:i1][page_content[:i1].rfind('\n'):len(page_content[:i1])] + page_content[i1:]

    if debug_level > 1:
        print('  Modèles à déplacer')
    regex = r'(==== {{S\|traductions}} ====)(\n{{ébauche\-trad[^}]*}})(\n{{trad-début}})'
    page_content = re.sub(regex, r'\1\3\2', page_content)

    regex = r'({{trad\-début}})\n*{{trad\-début}}'
    page_content = re.sub(regex, r'\1', page_content)

    regex = r'({{trad\-fin}})\n*{{trad\-fin}}'
    page_content = re.sub(regex, r'\1', page_content)

    return page_content, summary


def add_templates(page_content, summary):
    if debug_level > 1:
        print(' add_templates()')

    if debug_level > 1:
        print('  add etymology templates')
    word_regex = r'\'*(?:\[\[|{{lien\||{{l\|)([^}\]\n]+)(?:\]\]|\|[a-z]+}})\'*'
    regex = r'(=== {{S\|étymologie}} ===\n(?:{{ébauche-étym\|[^}]+}}\n)?: *(?:{{(?:' \
            + '|'.join(etymology_date_templates) + r')\|?[^}]*}})* *)' \
            + r'(?:[cC]omposé|[dD]érivé) de ' + word_regex + r' (?:et|avec le (?:préfixe|suffixe)) ' \
            + word_regex + r'\.*\n'
    page_content = re.sub(regex, r'\1{{composé de|m=1|\2|\3}}.', page_content)

    if debug_level > 1:
        print('  add form templates')
    # TODO by language
    regex = r'\|fr}} (\'+adverbe de (' + '|'.join(adverbs) + r')\'+)'
    page_content = re.sub(regex, r'|fr}} {{adverbe de \2|fr}}', page_content)
    for adverb in adverbs:
        if '{{adverbe de ' + adverb + '|fr}}' in page_content:
            page_content, summary = remove_category(page_content, 'Adverbes de temps en français', summary)

    if debug_level > 1:
        print('  add definition templates')
    regex = r'\n#\* *(?:\'\')?\n'
    # TODO lang=
    page_content = re.sub(regex, r'\n#* {{ébauche}}\n', page_content)
    regex = r"(\|en}}\n# *'*(?:Participe présent|Participe passé|Prétérit|Troisième personne du singulier du présent) de *'* *)to "
    page_content = re.sub(regex, r'\1', page_content, re.IGNORECASE)
    regex = r"(\|([a-z]+)}}\n# *'*(?:Participe présent|Participe passé|Prétérit|Troisième personne du singulier du présent) de *'* *)([a-zçæéë \-’']+)\."
    page_content = re.sub(regex, r'\1{{l|\3|\2}}.', page_content, re.IGNORECASE)

    if debug_level > 1:
        print('  add translation templates')
    regex = r'\n\* *[Ss]olr[eé]sol *: *:* *\[\[«?([^\]\n«»]+)»?\]\]'
    page_content = re.sub(regex, r'\n* {{T|solrésol}} : {{trad--|solrésol|\1}}', page_content)
    regex = r'(\n\* {{T\|tsolyáni}} *: *)\[\[([^\]\n]+)\]\]'
    page_content = re.sub(regex, r'\1{{trad--|tsolyáni|\2}}', page_content)

    return page_content, summary


def replace_templates(page_content, summary):
    if debug_level > 1:
        print('  replace_templates')
    page_content, summary = replace_etymology_templates(page_content, summary)

    if debug_level > 1:
        print(' Remplacements des anciens codes langue')
    page_content = page_content.replace('|ko-hani}}', '|ko-Hani}}')
    page_content = page_content.replace('|lang=API}}', '|lang=conv}}')
    page_content = page_content.replace('|lang=gr}}', '|lang=grc}}')
    page_content = page_content.replace('|lang=gr|', '|lang=grc|')
    # TODO vi-Hani ?
    # TODO move some to incubator_languages
    old_template = []
    new_template = []
    old_template.append('ko-hanja')
    new_template.append('ko-Hani')
    old_template.append('be-x-old')
    new_template.append('be-tarask')
    old_template.append('zh-min-nan')
    new_template.append('nan')
    old_template.append('lsf')
    new_template.append('fsl')
    old_template.append('arg')
    new_template.append('an')
    old_template.append('nav')
    new_template.append('nv')
    old_template.append('prv')
    new_template.append('oc')
    old_template.append('nds-NL')
    new_template.append('nds-nl')
    old_template.append('gsw-FR')
    new_template.append('gsw-fr')
    old_template.append('zh-sc')
    new_template.append('zh-Hans')
    old_template.append('roa-rup')
    new_template.append('rup')
    old_template.append('gaul')
    new_template.append('gaulois')
    old_template.append('xtg')
    new_template.append('gaulois')
    for p in range(1, len(old_template)):
        # TODO select templates https://fr.wiktionary.org/w/index.php?title=van&diff=prev&oldid=24107783&diffmode=source
        # regex = r'((?!:voir).*[\|{=])' + old_template[p] + r'([\|}])'
        regex = r'({{T\|)' + re.escape(old_template[p]) + r'}}'
        page_content = re.sub(regex, r'\1' + new_template[p] + r'}}', page_content)
        regex = r'({{trad[\-\+]\-?\|)' + re.escape(old_template[p]) + r'\|'
        page_content = re.sub(regex, r'\1' + new_template[p] + r'|', page_content)

    if debug_level > 1:
        print(' Modèles trop courts')
    page_content = page_content.replace('{{f}} {{fsing}}', '{{f}}')
    page_content = page_content.replace('{{m}} {{msing}}', '{{m}}')
    page_content = page_content.replace('{{f}} {{p}}', '{{fplur}}')
    page_content = page_content.replace('{{m}} {{p}}', '{{mplur}}')
    page_content = page_content.replace('{{fp}}', '{{fplur}}')
    page_content = page_content.replace('{{mp}}', '{{mplur}}')
    page_content = page_content.replace('{{np}}', '{{nlur}}')
    page_content = page_content.replace('{{fs}}', '{{fsing}}')
    page_content = page_content.replace('{{mascul}}', '{{au masculin}}')
    page_content = page_content.replace('{{fémin}}', '{{au féminin}}')
    page_content = page_content.replace('{{femin}}', '{{au féminin}}')
    page_content = page_content.replace('{{sing}}', '{{au singulier}}')
    page_content = page_content.replace('{{plur}}', '{{au pluriel}}')
    page_content = page_content.replace('{{pluri}}', '{{au pluriel}}')
    page_content = page_content.replace('{{mascul|', '{{au masculin|')
    page_content = page_content.replace('{{fémin|', '{{au féminin|')
    page_content = page_content.replace('{{femin|', '{{au féminin|')
    page_content = page_content.replace('{{sing|', '{{au singulier|')
    page_content = page_content.replace('{{plur|', '{{au pluriel|')
    page_content = page_content.replace('{{pluri|', '{{au pluriel|')
    page_content = page_content.replace('{{dét|', '{{déterminé|')
    page_content = page_content.replace('{{dén|', '{{dénombrable|')
    page_content = page_content.replace('{{pl-cour}}', '{{plus courant}}')
    page_content = page_content.replace('{{pl-rare}}', '{{plus rare}}')
    page_content = page_content.replace('{{mf?}}', '{{mf ?}}')
    page_content = page_content.replace('{{fm?}}', '{{fm ?}}')
    page_content = page_content.replace('{{coll}}', '{{collectif}}')

    page_content = re.sub(r'{{ordin *([\|}\n])', r'{{ordinal\1', page_content)
    page_content = re.sub(r'{{cardin *([\|}\n])', r'{{cardinal\1', page_content)
    page_content = re.sub(r'{{comp *([\|}\n])', r'{{comparatif\1', page_content)
    page_content = re.sub(r'{{super *([\|}\n])', r'{{superlatif\1', page_content)
    page_content = re.sub(r'{{irrég *([\|}\n])', r'{{irrégulier\1', page_content)
    page_content = re.sub(r'{{perf *([\|}\n])', r'{{perfectif\1', page_content)
    page_content = re.sub(r'{{imperf *([\|}\n])', r'{{imperfectif\1', page_content)
    page_content = re.sub(r'{{nomin *([\|}\n])', r'{{nominatif\1', page_content)
    page_content = re.sub(r'{{acron *([\|}\n])', r'{{acronyme\1', page_content)
    page_content = re.sub(r'{{abrév *([\|}\n])', r'{{abréviation\1', page_content)
    page_content = re.sub(r'{{fig *([\|}\n])', r'{{figuré\1', page_content)

    if debug_level > 1:
        print(' Modèles des définitions')
    page_content = re.sub(r'{{régio *\| *', r'{{région|', page_content)
    page_content = re.sub(r'{{terme *\| *', r'{{term|', page_content)
    page_content = re.sub(r'{{term *\|Registre neutre}} *', r'', page_content)

    regex = r"{{ *dés *([\|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"{{désuet\1", page_content)
    regex = r"{{ *fam *([\|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"{{familier\1", page_content)
    regex = r"{{ *péj *([\|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"{{péjoratif\1", page_content)
    regex = r"{{ *vx *([\|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"{{vieilli\1", page_content)

    if debug_level > 1:
        print(' Modèles alias en doublon')
    regex = r"(\{\{figuré\|[^}]*\}\}) ?\{\{métaphore\|[^}]*\}\}"
    pattern = re.compile(regex)
    page_content = pattern.sub(r"\1", page_content)
    regex = r"(\{\{métaphore\|[^}]*\}\}) ?\{\{figuré\|[^}]*\}\}"
    pattern = re.compile(regex)
    page_content = pattern.sub(r"\1", page_content)

    regex = r"(\{\{départements\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    page_content = pattern.sub(r"\1", page_content)

    regex = r"(\{\{localités\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    page_content = pattern.sub(r"\1", page_content)

    regex = r"(\{\{provinces\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
    pattern = re.compile(regex)
    page_content = pattern.sub(r"\1", page_content)

    regex = r"(\#\* {{ébauche\-exe\|[^}]*}})\n\#\*: {{trad\-exe\|[^}]*}}"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1", page_content)

    page_content = page_content.replace('{{arbre|', '{{arbres|')
    page_content = page_content.replace('{{arme|', '{{armement|')
    page_content = page_content.replace('{{astro|', '{{astronomie|')
    page_content = page_content.replace('{{bota|', '{{botanique|')
    page_content = page_content.replace('{{électro|', '{{électronique|')
    page_content = page_content.replace('{{équi|', '{{équitation|')
    page_content = page_content.replace('{{ex|', '{{e|')
    page_content = page_content.replace('{{gastro|', '{{gastronomie|')
    page_content = page_content.replace('{{légume|', '{{légumes|')
    page_content = page_content.replace('{{minéral|', '{{minéralogie|')
    page_content = page_content.replace('{{myth|', '{{mythologie|')
    page_content = page_content.replace('{{oiseau|', '{{oiseaux|')
    page_content = page_content.replace('{{péj|', '{{péjoratif|')
    page_content = page_content.replace('{{plante|', '{{plantes|')
    page_content = page_content.replace('{{psycho|', '{{psychologie|')
    page_content = page_content.replace('{{réseau|', '{{réseaux|')
    page_content = page_content.replace('{{typo|', '{{typographie|')
    page_content = page_content.replace('{{vêtement|', '{{vêtements|')
    page_content = page_content.replace('{{en-nom-rég-double|', '{{en-nom-rég|')
    page_content = page_content.replace('{{Valence|ca}}', '{{valencien}}')
    page_content = page_content.replace('{{abrév|', '{{abréviation|')
    page_content = page_content.replace('{{abrév}}', '{{abréviation}}')
    page_content = page_content.replace('{{acron|', '{{acronyme|')
    page_content = page_content.replace('{{cours d\'eau', '{{cours d’eau')

    if debug_level > 1:
        print(' Modèles trop longs')
    page_content = page_content.replace('{{boîte début', '{{(')
    page_content = page_content.replace('{{boîte fin', '{{)')
    page_content = page_content.replace('\n{{-}}', '')

    if debug_level > 1:
        print(' Modèles en doublon')
    imported_sites = ['DAF8', 'Littré']
    for importedSite in imported_sites:
        regex = r'\n\** *{{R:' + importedSite + r'}} *\n\** *({{Import:' + importedSite + r'}})'
        if re.search(regex, page_content):
            summary = summary + ', doublon {{R:' + importedSite + r'}}'
            page_content = re.sub(regex, r'\n* \1', page_content)
        regex = r'\n\** *({{Import:' + importedSite + r'}}) *\n\** *{{R:' + importedSite + r'}}'
        if re.search(regex, page_content):
            summary = summary + ', doublon {{R:' + importedSite + r'}}'
            page_content = re.sub(regex, r'\n* \1', page_content)

    if debug_level > 1:
        print(' Modèles bandeaux')
    while page_content.find('\n{{colonnes|') != -1:
        if debug_level > 0:
            pywikibot.output('\n \03{green}colonnes\03{default}')
        page_content2 = page_content[:page_content.find('\n{{colonnes|')]
        if page_content2.rfind('{{') != -1 and page_content2.rfind('{{') == page_content2.rfind('{{trad-début'):
            # modèles impriqués dans trad
            page_content2 = page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            if page_content2.find('\n}}\n') != -1:
                if page_content2[:len('titre=')] == 'titre=':
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                                   + '\n{{trad-fin}}' + page_content[page_content.find('\n{{colonnes|')
                                                 + len('\n{{colonnes|') + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] + '\n{{trad-début|' \
                        + page_content[page_content.find('\n{{colonnes|')
                        + len('\n{{colonnes|titre='):page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                        + page_content2.find('|')] \
                        + '}}' + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                        + page_content2.find('|') + 1:]
                else:
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                                   + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                  + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] \
                                   + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            else:
                if debug_level > 0:
                    print('pb {{colonnes}} 1')
                break

        elif page_content2.rfind('{{') != -1 and page_content2.rfind('{{') == page_content2.rfind('{{('):
            # modèles impriqués ailleurs
            if debug_level > 0:
                pywikibot.output('\nTemplate: \03{blue}(\03{default}')
            page_content2 = page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            if page_content2.find('\n}}\n') != -1:
                if page_content2[:len('titre=')] == 'titre=':
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                                   + '\n{{)}}' + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                              + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] + '\n{{(|' \
                                   + page_content[page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|titre='):page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|') + page_content2.find('|')] + '}}' \
                                   + page_content[page_content.find('\n{{colonnes|')
                                                  + len('\n{{colonnes|') + page_content2.find('|') + 1:]
                else:
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                                   + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                  + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] \
                                   + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            else:
                if debug_level > 0:
                    print('pb {{colonnes}} 2')
                break

        elif page_content2.rfind('{{') != -1 and (page_content2.rfind('{{') == page_content2.rfind('{{trad-fin') or
                                                  page_content2.rfind('{{') == page_content2.rfind('{{S|trad')):
            # modèle à utiliser dans {{S|trad
            page_content2 = page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            if page_content2.find('\n}}\n') != -1:
                if page_content2[:len('titre=')] == 'titre=':
                    page_content = page_content[:page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|')
                                   + page_content2.find('\n}}\n')] \
                                   + '\n{{trad-fin}}' \
                                   + page_content[page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|')
                                   + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] \
                                   + '\n{{trad-début|' \
                                   + page_content[page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|titre='):page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|')
                                   + page_content2.find('|')] + '}}' \
                                   + page_content[page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|') + page_content2.find('|') + 1:]
                else:
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                   + page_content2.find('\n}}\n')] \
                                   + '\n{{trad-fin}}' + page_content[page_content.find('\n{{colonnes|')
                                   + len('\n{{colonnes|') + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] + '\n{{trad-début}}' \
                                   + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            else:
                if debug_level > 0:
                    print('pb {{colonnes}} 3')
                break

        else:  # modèle ailleurs que {{S|trad
            page_content2 = page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            if page_content2.find('\n}}\n') != -1:
                if page_content2[:len('titre=')] == 'titre=':
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                        + '\n{{)}}' + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                   + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] + '\n{{(|' \
                        + page_content[page_content.find('\n{{colonnes|')
                                       + len('\n{{colonnes|titre='):page_content.find('\n{{colonnes|')
                                                                    + len('\n{{colonnes|') + page_content2.find('|')] \
                        + '}}' + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                              + page_content2.find('|') + 1:]
                else:
                    page_content = page_content[:page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                 + page_content2.find('\n}}\n')] \
                                   + '\n{{)}}' + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|')
                                                              + page_content2.find('\n}}\n') + len('\n}}'):]
                    page_content = page_content[:page_content.find('\n{{colonnes|')] + '\n{{(}}' \
                                    + page_content[page_content.find('\n{{colonnes|') + len('\n{{colonnes|'):]
            else:
                if debug_level > 0:
                    print('pb {{colonnes}} 4')
                break
        while page_content.find('}}1=') != -1:
            page_content = page_content[:page_content.find('}}1=')] + page_content[page_content.find('}}1=')
                                                                                        + len('}}1='):]

    page_content = page_content.replace('{{pron-rég|', '{{écouter|')
    regex = r'\* ?{{sound}} ?: \[\[Media:([^\|\]]*)\|[^\|\]]*\]\]'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{écouter|audio=\1}}', page_content)
        summary = summary + ', conversion de modèle de son'
    regex = r'\{{audio\|([^\|}]*)\|[^\|}]*}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{écouter|audio=\1}}', page_content)
        summary = summary + ', conversion de modèle de son'

    page_content = page_content.replace('{{Citation needed}}', '{{référence nécessaire}}')
    page_content = page_content.replace('{{Référence nécessaire}}', '{{référence nécessaire}}')
    page_content = page_content.replace('{{clef de tri', '{{clé de tri')

    # TODO: replace {{fr-rég|ɔs vɛʁ.tɛ.bʁal|s=os vertébral|p=os vertébraux|pp=ɔs vɛʁ.tɛ.bʁo}} by {{fr-accord-mf-al|

    # Hotfix
    regex = r'\n{{\(}}nombre= *[0-9]*\|\n'
    page_content = re.sub(regex, r'\n{{(}}\n', page_content)
    regex = r'\n{{\(}}taille= *[0-9]*\|\n'
    page_content = re.sub(regex, r'\n{{(}}\n', page_content)

    return page_content, summary


def replace_etymology_templates(page_content, summary):
    if debug_level > 1:
        print('  replace_etymology_templates')

    regex = r"(\n:? *(?:{{date[^}]*}})? *(?:\[\[calque\|)?[Cc]alque\]* d(?:u |e l['’]){{)étyl\|"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1calque|", page_content)

    decision = ', [[Wiktionnaire:Prise de décision/Nettoyer les modèles de la section étymologie]]'
    initial_page_content = page_content
    # Alias replacing
    templates = {
        'abrév': 'abréviation',
        'acron': 'acronyme',
        'compos': 'composé de',
        'contr': 'contraction'
    }
    for alias in templates:
        regex = r"({{)" + alias + r"([|}])"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r"\1" + templates[alias] + r"\2", page_content)

    # Alias replacing with: |m=1
    regex = r"({{)deet([|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1composé de|m=1\2", page_content)

    regex = r'[Ll]ocution {{composé de[^{}]+}}'
    templates = re.findall(regex, page_content)
    for template in templates:
        regex2 = r'\| *f *= *1[\|}]'
        if not re.search(regex2, template):
            new_template = template.replace('composé de', 'composé de|f=1')
            page_content = page_content.replace(template, new_template)

    return page_content, summary
    # TODO fix https://fr.wiktionary.org/w/index.php?title=nos&type=revision&diff=27795087&oldid=27614294
    # Fix https://fr.wiktionary.org/w/index.php?title=mac&diff=27795089&oldid=27788198
    # Replacing with: |m=1 and .
    for template in etymology_templates:
        # regex = r"({{)" + template + r"([^}]*)}}"              # {{abréviation|fr|m=1|m=1}}.
        # regex = r"({{)" + template + r"((?!\|m=1).)*}}"        # {{abréviationr|m=1}}
        # regex = r"({{)" + template + r"((?!\|m=1)[^}]*)*}}"    # {{abréviation|m=1}}.
        # regex = r"({{)" + template + r"(((?!\|m=1)[^}]*)*)}}"  # {{abréviation|fr|m=1|m=1}}.
        regex = r"({{)" + template + r"([^}]*)}}"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r"\1" + template + r"\2|m=1}}.", page_content)
    # Fix doubles. TODO prevent them just above
    regex = r"({{[^}]+)\|m=1([^}]*\|m=1[\|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1\2", page_content)

    if initial_page_content != page_content and decision not in summary:
        summary += decision
    return page_content, summary


def move_templates(page_content, summary):
    if debug_level > 1:
        print(' move_templates()')

    page_content, summary = move_etymology_templates(page_content, summary)
    return page_content, summary


def remove_double_category_when_template(page_content, summary):
    if debug_level > 1:
        print(' Retrait des catégories contenues dans les modèles')

    if '{{info|conv}}' in page_content and '[[Catégorie:Noms de domaine internet]]' in page_content:
        page_content = page_content.replace('[[Catégorie:Noms de domaine internet]]', '')
        page_content = page_content.replace('{{info|conv}}', '{{noms de domaine}}')
    if '{{informatique|conv}}' in page_content and '[[Catégorie:Noms de domaine internet]]' in page_content:
        page_content = page_content.replace('[[Catégorie:Noms de domaine internet]]', '')
        page_content = page_content.replace('{{informatique|conv}}', '{{noms de domaine}}')

    if page_content.find('\n[[Catégorie:Noms scientifiques]]') != -1 and page_content.find('{{S|nom scientifique|conv}}') != -1:
        page_content = page_content.replace('\n[[Catégorie:Noms scientifiques]]', '')

    if page_content.find('[[Catégorie:Villes') != -1 and page_content.find('{{localités|') != -1:
        summary = summary + ', {{villes}} -> {{localités}}'
        page_content = re.sub(r'\n\[\[Catégorie:Villes[^\]]*\]\]', r'', page_content)

    # TODO: retraiter toutes les paires catégorie / templates, dynamiquement, pour tous les codes langues
    if '{{argot|fr}}' in page_content:
        page_content = re.sub(r'\n\[\[Catégorie:Argot en français\]\]', r'', page_content)

    if page_content.find('\n[[Catégorie:Gentilés en français]]') != -1 and page_content.find('{{note-gentilé|fr}}') != -1:
        page_content = page_content.replace('\n[[Catégorie:Gentilés en français]]', '')

    return page_content, summary


def format_templates(page_content, summary):
    page_content = page_content.replace('}} \n', '}}\n')
    page_content = page_content.replace('\n {{', '\n{{')

    if debug_level > 1:
        print(' Formatage de la ligne de forme')
    page_content = page_content.replace('{{PAGENAME}}', '{{subst:PAGENAME}}')
    page_content = page_content.replace('-rég}}\'\'\'', '-rég}}\n\'\'\'')
    page_content = page_content.replace(']] {{imperf}}', ']] {{imperf|nocat=1}}')
    page_content = page_content.replace(']] {{perf}}', ']] {{perf|nocat=1}}')
    page_content = page_content.replace('{{perf}} / \'\'\'', '{{perf|nocat=1}} / \'\'\'')

    page_content = page_content.replace('|nocat=}}', '|nocat}}')
    page_content = page_content.replace('|pinv=. ', '|pinv=.')
    page_content = page_content.replace('|pinv=. ', '|pinv=.')

    if page_content.find('{{vérifier création automatique}}') != -1:
        if debug_level > 0:
            print(' {{vérifier création automatique}} trouvé')
        page_content2 = page_content
        language_value = '|'
        while page_content2.find('{{langue|') > 0:
            page_content2 = page_content2[page_content2.find('{{langue|')+len('{{langue|'):]
            language_value += '|' + page_content2[:page_content2.find('}}')]
        if language_value != '|':
            page_content = page_content.replace('{{vérifier création automatique}}',
                                                '{{vérifier création automatique' + language_value + '}}')
        if debug_level > 2:
            input(page_content)

    if debug_level > 0:
        print(' {{étyl}}')
    # TODO: regex for each language
    page_content = page_content.replace('Du {{étyl|en|', 'De l’{{étyl|en|')
    page_content = page_content.replace('du {{étyl|en|', 'de l’{{étyl|en|')
    page_content = page_content.replace('Du {{étyl|fro|', 'De l’{{étyl|fro|')
    page_content = page_content.replace('du {{étyl|fro|', 'de l’{{étyl|fro|')

    page_content = page_content.replace('Du {{étyl|en|', 'De l’{{étyl|en|')
    page_content = page_content.replace('Du {{étyl|it|', 'De l’{{étyl|it|')

    regex = r"({{cf|)lang=[^\|}]+\|(:Catégorie:)"
    page_content = re.sub(regex, r"\1\2", page_content)
    page_content = page_content.replace('\n \n', '\n\n')

    page_content = page_content.replace('#*: {{trad-exe|fr}}', '')
    page_content = page_content.replace('\n{{WP', '\n* {{WP')
    page_content = page_content.replace('{{Source-wikt|nan|', '{{Source-wikt|zh-min-nan|')
    page_content = page_content.replace('— {{source|', '{{source|')
    page_content = page_content.replace('- {{source|', '{{source|')
    regex = r"(\{\{source\|[^}]+ )p\. *([0-9])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1page \2", page_content)
    page_content = page_content.replace('myt=scandinave', 'myt=nordique')

    if debug_level > 1:
        print(' Modèles de prononciation')
    page_content = page_content.replace('{{pron|}}', '{{pron}}')
    page_content = page_content.replace('{{prononciation|}}', '{{prononciation}}')
    page_content = re.sub(r'({{pron\|[^|}]*)\|(}})', r"\1\2", page_content)
    page_content = re.sub(r'({{pron\|[^|}]*\|)\|([a-z\-]+}})', r"\1\2", page_content)
    page_content = re.sub(r'({{pron\|[^|}]*\|)\|nocat(?:=1)?(}})', r"\1\2", page_content)
    page_content = re.sub(r'}}\* *{{écouter\|', r"}}\n* {{écouter|", page_content)

    if debug_level > 1:
        print('  Modèles de son')
    regex = r'({{écouter\|lang=([^\|]+)\|{{Région \?)}}'
    page_content = re.sub(regex, r'\1|\2}}', page_content)
    regex = r'\n *{{écouter\|'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\n* {{écouter|', page_content)
    regex = r'{{S\|prononciation}} ===\*'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{S|prononciation}} ===\n*', page_content)

    for m in range(1, len(region_short_templates)):
        while page_content.find('{{écouter|' + region_short_templates[m] + '|') != -1:
            page_content = page_content[:page_content.find('{{écouter|' + region_short_templates[m] + '|')
                + len('{{écouter|')] \
                + '{{' + region_short_templates[m] + '|nocat=1}}' \
                + page_content[page_content.find('{{écouter|' + region_short_templates[m] + '|')
                + len('{{écouter|' + region_short_templates[m]):]

    regex = r"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation\|[^}]*)\|m=1}} de([ '])"
    page_content = re.sub(regex, r'\1}} De\2', page_content)
    regex = r"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation)\|m=1(\|[^}]*)}} de([ '])"
    page_content = re.sub(regex, r'\1\2}} De\3', page_content)

    if debug_level > 1:
        print(' Ajout des modèles de référence')
        # les URL ne contiennent pas les diacritiques des {{PAGENAME}}
    while page_content.find('[http://www.sil.org/iso639-3/documentation.asp?id=') != -1:
        page_content2 = page_content[page_content.find('[http://www.sil.org/iso639-3/documentation.asp?id=')
                                     + len('[http://www.sil.org/iso639-3/documentation.asp?id='):]
        page_content = page_content[:page_content.find('[http://www.sil.org/iso639-3/documentation.asp?id=')] \
                       + '{{R:SIL|' + page_content2[:page_content2.find(' ')] + '}}' \
                       + page_content2[page_content2.find(']')+1:]
        summary = summary + ', ajout de {{R:SIL}}'
    while page_content.find('[http://www.cnrtl.fr/definition/') != -1:
        page_content2 = page_content[page_content.find('[http://www.cnrtl.fr/definition/')
                                     + len('[http://www.cnrtl.fr/definition/'):]
        page_content = page_content[:page_content.find('[http://www.cnrtl.fr/definition/')] \
                       + '{{R:TLFi|' + page_content2[:page_content2.find(' ')] + '}}' \
                       + page_content2[page_content2.find(']')+1:]
        summary = summary + ', ajout de {{R:TLFi}}'
    while page_content.find('[http://www.mediadico.com/dictionnaire/definition/') != -1:
        page_content2 = page_content[page_content.find('[http://www.mediadico.com/dictionnaire/definition/')
                                     + len('[http://www.mediadico.com/dictionnaire/definition/'):]
        page_content = page_content[:page_content.find('[http://www.mediadico.com/dictionnaire/definition/')] \
                       + '{{R:Mediadico|' + page_content2[:page_content2.find('/1')] + '}}' \
                       + page_content2[page_content2.find(']')+1:]
        summary = summary + ', ajout de {{R:Mediadico}}'

    # TODO: Factorisation des citations
    # regex = r"(?:— \(|{{source\|)Cirad/Gret/MAE, ''Mémento de l['’]Agronome'', 1 *692 p(?:\.|ages), p(?:\.|age) ([0-9 ]+), 2002, Paris, France, Cirad/Gret/Ministère des Affaires [EÉ]trangères \(\+ 2 cdroms\)(?:\)|}})"
    # if re.search(regex, page_content):
    #    page_content = re.sub(regex, r"{{Citation/Cirad/Gret/MAE/Mémento de l’Agronome|\1}}", page_content)

    return page_content, summary


def format_languages_templates(page_content, summary, page_name):
    if debug_level > 0: print(' Templates by language')
    regex_page_name = re.escape(page_name)

    regex = r'{{(Latn|Grek|Cyrl|Armn|Geor|Hebr|Arab|Syrc|Thaa|Deva|Hang|Hira|Kana|Hrkt|Hani|Jpan|Hans|Hant|zh-mot|kohan|ko-nom|la-verb|grc-verb|polytonique|FAchar)[\|}]'
    if not re.search(regex, page_content):
        if debug_level > 0:
            print(' Headword addition')
        page_content = re.sub(r'([^d\-]+-\|[a-z]+\}\}\n{{[^\n]*\n)# *', r"\1'''" + page_name + r"''' {{pron}}\n# ",
                              page_content)

    if '{{langue|fr}}' in page_content:
        regex = r'^[ 0-9a-zàâçéèêëîôùûA-ZÀÂÇÉÈÊËÎÔÙÛ]+$'  # /:
        if re.search(regex, page_name):
            regex = r"\n{{clé de tri([^}]*)}}"
            if re.search(regex, page_content):
                if debug_level > 2:
                    input(page_content)
                summary = summary + ', retrait de {{clé de tri}}'
                page_content = re.sub(regex, '', page_content)

        if debug_level > 0:
            print(' Pronunciation categories')
        if page_name[-2:] == 'um' and page_content.find('ɔm|fr}}') != -1:
            page_content = add_category(page_content, 'fr', 'um prononcés /ɔm/ en français')
        if page_name[:2] == 'qu':
            regex = r'{{pron\|kw[^}\|]+\|fr}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'qu prononcés /kw/ en français')
        if page_name[:2] == 'qu' and page_name[:4] != 'quoi':
            regex = r'{{fr\-rég\|kw[^}\|]+}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'qu prononcés /kw/ en français')
        if page_name[:2] == 'ch':
            regex = r'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[:2] == 'ch':
            regex = r'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[:2] == 'Ch':
            regex = r'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[:2] == 'Ch':
            regex = r'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[-2:] == 'ch':
            regex = r'{{pron\|[^}\|]+k\|fr}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[-2:] == 'ch':
            regex = r'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[-3:] == 'chs':
            regex = r'{{pron\|[^}\|]+k}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')
        if page_name[-3:] == 'chs':
            regex = r'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, page_content):
                page_content = add_category(page_content, 'fr', 'ch prononcés /k/ en français')

        regex = r'({{fr\-[^}]*\|[\'’]+=[^}]*)\|[\'’]+=[oui|1]'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
        regex = r'({{fr\-[^}]*\|s=[^}]*)\|s=[^}\|]*'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
        regex = r'({{fr\-[^}]*\|ms=[^}]*)\|ms=[^}\|]*'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
        regex = r'({{fr\-[^}]*\|fs=[^}]*)\|fs=[^}\|]*'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)

        page_content = page_content.replace('{{louchébem|fr}}', '{{louchébem}}')
        page_content = page_content.replace('{{reverlanisation|fr}}', '{{reverlanisation}}')
        page_content = page_content.replace('{{verlan|fr}}', '{{verlan}}')

# Ajout des redirections des pronominaux
        if page_content.find('{{S|verbe|fr}}') != -1 and page_name[:3] != 'se' and page_name[:2] != 's’':
            page_content2 = page_content[page_content.find('{{S|verbe|fr}}'):]
            regex = r'(\n|\')s(e |’)\'\'\''
            if re.search(regex, page_content2) is not None:
                if re.search(regex, page_content2).start() < page_content2.find('{{S|') or \
                        page_content2.find('{{S|') == -1:
                    regex = r'^[aeiouyàéèêôù]'
                    if re.search(regex, page_name):  # not [:1] car = & si encodage ASCII du paramètre DOS / Unix
                        page_name2 = 's’' + page_name
                    else:
                        page_name2 = 'se ' + page_name
                    page2 = Page(site, page_name2)
                    if not page2.exists():
                        if debug_level > 0:
                            print('Création de ') + sort_by_encoding(page_name2)
                        summary2 = 'Création d\'une redirection provisoire catégorisante du pronominal'
                        save_page(page2, '#REDIRECT[[' + page_name + ']]\n<!-- Redirection temporaire avant de créer le verbe pronominal -->\n[[Catégorie:Wiktionnaire:Verbes pronominaux à créer en français]]', summary2)

        # Ajout de modèles pour les gentités et leurs adjectifs
        if debug_level > 0:
            print(' Demonyms')
        regex = r'({{fr\-[^}]+)\\'
        while re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)

        line = 6
        column = 4
        # TODO : fusionner avec le tableau des modèles de flexion
        demonym_templates = [[0] * (column+1) for _ in range(line+1)]
        demonym_templates[1][1] = r'fr-accord-mixte'
        demonym_templates[1][2] = r's'
        demonym_templates[1][3] = r'e'
        demonym_templates[1][4] = r'es'
        demonym_templates[2][1] = r'fr-accord-s'
        demonym_templates[2][2] = r''
        demonym_templates[2][3] = r'e'
        demonym_templates[2][4] = r'es'
        demonym_templates[3][1] = r'fr-accord-el'
        demonym_templates[3][2] = r's'
        demonym_templates[3][3] = r'le'
        demonym_templates[3][4] = r'les'
        demonym_templates[4][1] = r'fr-accord-en'
        demonym_templates[4][2] = r's'
        demonym_templates[4][3] = r'ne'
        demonym_templates[4][4] = r'nes'
        demonym_templates[5][1] = r'fr-accord-et'
        demonym_templates[5][2] = r's'
        demonym_templates[5][3] = r'te'
        demonym_templates[5][4] = r'tes'
        demonym_templates[6][1] = r'fr-rég'
        demonym_templates[6][2] = r's'
        demonym_templates[6][3] = r''
        demonym_templates[6][4] = r's'

        for l in range(1, line + 1):
            # Depuis un masculin
            regex = r'\({{p}} : [\[\']*' + regex_page_name + demonym_templates[l][2] + r'[\]\']*, {{f}} : [\[\']*' + regex_page_name + demonym_templates[l][3] + r'[\]\']*, {{fplur}} : [\[\']*' + regex_page_name + demonym_templates[l][4] + r'[\]\']*\)'
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|pron=}}', page_content)
                summary = summary + ', conversion des liens flexions en modèle boite'
            # Depuis un féminin
            if demonym_templates[l][1] == r'fr-accord-s' and regex_page_name[-1:] == 'e' and regex_page_name[-2:-1] == 's':
                regex = r'\({{p}} : [\[\']*' + regex_page_name + r's[\]\']*, {{m}} : [\[\']*' + regex_page_name[:-1] + r'[\]\']*\)'
                if re.search(regex, page_content):
                    page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|ms=' + regex_page_name[:-1].replace('\\', '') + '}}', page_content)
                    summary = summary + ', conversion des liens flexions en modèle boite'
            regex = r'\({{f}} : [\[\']*' + regex_page_name + demonym_templates[l][3] + r'[\]\']*, {{mplur}} : [\[\']*' + regex_page_name + demonym_templates[l][2] + r'[\]\']*, {{fplur}} : [\[\']*' + regex_page_name + demonym_templates[l][4] + r'[\]\']*\)'
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|pron=}}', page_content)
                summary = summary + ', conversion des liens flexions en modèle boite'
            if debug_level > 1: print(' avec son')
            regex = r'(\n\'\'\'' + regex_page_name + '\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + demonym_templates[l][1] + r'\|[pron\=]*)}}'
            if re.search(regex, page_content):
                page_content = re.sub(regex, r'\n\4\2}}\1\2\3', page_content)

            deplacement_modele_inflexion = False
            # On différencie les cas pas d'espace avant le modèle / espace avant le modèle
            regex = r'( ===\n)(\'\'\'[^\n]+[^ ])({{' + demonym_templates[l][1] + r'\|[^}]*}})'
            if re.search(regex, page_content):
                page_content = re.sub(regex, r'\1\3\n\2', page_content)
                deplacement_modele_inflexion = True
            # Espace avant le modèle
            regex_space = r'( ===\n)(\'\'\'[^\n]+) ({{' + demonym_templates[l][1] + r'\|[^}]*}})'
            if re.search(regex_space, page_content):
                page_content = re.sub(regex_space, r'\1\3\n\2', page_content)
                deplacement_modele_inflexion = True
            if deplacement_modele_inflexion:
                summary = summary + ', déplacement des modèles de flexions'
                
        regex = r'({{fr\-accord\-comp\-mf[^}]*\| *trait *=) *([\|}])'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1&nbsp;\2', page_content)

    elif '{{langue|en}}' in page_content:
        regex = r'(\|en}} ===\n{{)fr\-rég'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1en-nom-rég', page_content)

        regex = r"({{S\|verbe\|en}} *=* *\n'*)to "
        if re.search(regex, page_content):
            page_content = re.sub(regex, r"\1", page_content)

        regex = r'(=== {{S\|adjectif\|en}} ===\n[^\n]*) *{{pluriel \?\|en}}'
        page_content = re.sub(regex, r"\1", page_content)

    elif '{{langue|es}}' in page_content:
        regex = r'(\|es}} ===\n{{)fr\-rég'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1es-rég-voy', page_content)

        line = 1
        column = 4
        demonym_templates = [[0] * (column+1) for _ in range(line+1)]
        demonym_templates[1][1] = r'es-accord-oa'
        demonym_templates[1][2] = r'os'
        demonym_templates[1][3] = r'a'
        demonym_templates[1][4] = r'as'
        re_page_radical_name = re.escape(page_name[:-1])

        for l in range(1, line + 1):
            regex = r'\({{p}} : [\[\']*' + re_page_radical_name + demonym_templates[l][2] + r'[\]\']*, {{f}} : [\[\']*' \
             + re_page_radical_name + demonym_templates[l][3] + r'[\]\']*, {{fplur}} : [\[\']*' + re_page_radical_name \
                    + demonym_templates[l][4] + r'[\]\']*\)'
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|' + re_page_radical_name + r'}}', page_content)
                summary = summary + ', conversion des liens flexions en modèle boite'
            regex = r'\({{f}} : [\[\']*' + re_page_radical_name + demonym_templates[l][3] + r'[\]\']*, {{mplur}} : [\[\']*' \
                + re_page_radical_name + demonym_templates[l][2] + r'[\]\']*, {{fplur}} : [\[\']*' + re_page_radical_name \
                + demonym_templates[l][4] + r'[\]\']*\)'
            if debug_level > 1:
                print(regex)
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|' + re_page_radical_name + r'}}', page_content)
                summary = summary + ', conversion des liens flexions en modèle boite'
            # Son
            if debug_level > 0:
                print(' son')
            regex = r'(\n\'\'\'' + regex_page_name + '\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' \
                    + demonym_templates[l][1] + r'\|' + re_page_radical_name + r')}}'
            if re.search(regex, page_content):
                page_content = re.sub(regex, r'\n\4|\2}}\1\2\3', page_content)

    language_codes = ['fc', 'fro', 'frm', 'pt', 'pcd']
    for l in language_codes:
        regex = r'(\|' + l + r'(:?\|num=[0-9])?}} ===\n{{)fr(\-rég)'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1' + l + r'\3', page_content)
    regex = r'\n{{fro\-rég[^}]*}}'
    page_content = re.sub(regex, r'', page_content)

    return page_content, summary


def move_etymology_templates(page_content, summary):
    if debug_level > 0:
        print(' move_etymology_templates()')
    page_languages = get_page_languages(page_content)
    for page_language in page_languages:
        for etym_template in etymology_templates:
            page_content, summary = move_etymology_template(page_content, summary, page_language, etym_template)

    if debug_level > 0:
        print('  Replace template otherwise')
    regex = r'{{(' + '|'.join(etymology_templates) + r')\|nocat(?:=1)*}}'
    page_content = re.sub(regex, r"{{term|\1}}", page_content)

    return page_content, summary


def move_etymology_template(page_content, summary, language_code, etym_template):
    if debug_level > 1:
        print(' move_etymology_template(' + etym_template + ')')
    language_section, l_start, l_end = get_language_section(page_content, language_code)
    if language_section is not None and len(get_natures_sections(language_section)) == 1 \
            and language_section.find(etym_template[1:]) != -1:
        regex_template = r"\n'''[^\n]+(\n#)? *({{[^}]+}})? *({{[^}]+}})? *{{" + etym_template + r'(\||})'
        if re.search(regex_template, language_section):
            new_language_section, summary = move_template_to_etymology(language_section, etym_template, summary,
                                                                       language_code)
            page_content = page_content.replace(language_section, new_language_section)
    return page_content, summary


def move_template_to_etymology(language_section, etym_template, summary, language_code):
    new_language_section, summary = remove_template(language_section, etym_template, summary, in_section=natures)
    etymology, s_start, s_end = get_section_by_name(new_language_section, 'étymologie')
    if etymology is None:
        new_language_section = add_line(new_language_section, language_code, 'étymologie',
                                        ': {{ébauche-étym|' + language_code + '}}')
        etymology, s_start, s_end = get_section_by_name(new_language_section, 'étymologie')
    if etymology is not None and etymology.find('{{' + etym_template) == -1:
        regex_etymology = r'(=\n:* *(\'*\([^\)]*\)\'*)?) *'
        if re.search(regex_etymology, language_section):
            etymology2 = re.sub(regex_etymology, r'\1 {{' + etym_template + r'}} ', etymology)
            new_language_section = new_language_section.replace(etymology, etymology2)
            summary = summary + ', [[Wiktionnaire:Prise de décision/Déplacer les modèles de contexte' \
                + ' étymologiques dans la section « Étymologie »|ajout de {{' \
                + etym_template + r"}} dans l'étymologie]]"

    l = etym_template[:1]
    regex = r'{{' + etym_template + r'(?:\|' + language_code + r')?(?:\|m=1)?}} *(?:\[\[' + etym_template \
            + r'\|)?[' + l + l.upper() + r']' + etym_template[1:] + r'(?:\]\])? de '
    new_language_section = re.sub(regex, '{{' + etym_template + '|' + language_code + '|m=1}} de ', new_language_section)
    return new_language_section, summary


def format_wikicode(page_content, summary, page_name):
    # TODO hors modèles https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:fr-accord-comp-mf&oldid=prev&diff=26238109
    # page_content = page_content.replace('&nbsp;', ' ')
    # page_content = re.sub(r'«[  \t]*', r'« ', page_content) # pb &#160;
    # page_content = re.sub(r'[  \t]*»', r' »', page_content)
    page_content = page_content.replace('{|\n|}', '')
    page_content = page_content.replace('[[' + page_name + ']]', '\'\'\'' + page_name + '\'\'\'')

    if debug_level > 1:
        print(' #* or #:')
    page_content = page_content.replace('\n #*', '\n#*')
    page_content = page_content.replace('\n #:', '\n#:')
    final_page_content = ''
    while page_content.find('\n#:') != -1:
        final_page_content = final_page_content + page_content[:page_content.find('\n#:')+2]
        if final_page_content.rfind('{{langue|') == final_page_content.rfind('{{langue|fr}}'):
            separator = '*'
        else:
            separator = ':'
        page_content = separator + page_content[page_content.find('\n#:')+len('\n#:'):]
    page_content = final_page_content + page_content

    if debug_level > 1:
        print(' add form line')
    # TODO fix https://fr.wiktionary.org/w/index.php?title=Theresa&diff=27792535&oldid=25846879
    # page_content = re.sub(r'([^d\-]+-\|[a-z]+\}\}\n)# *', r"\1'''" + page_name + r"''' {{pron}}\n# ", page_content)

    return page_content, summary


def add_appendix_links(page_content, summary, page_name):
    language_suffixes = [('es', 'ar', 'arsi', 'er', 'ersi', 'ir', 'irsi'),
         ('pt', 'ar', 'ar-se', 'er', 'er-se', 'ir', 'ir-se'),
         ('it', 'are', 'arsi', 'ere', 'ersi', 'ire', 'irsi'),
         ('fr', 'er', 'er', 'ir', 'ir', 're', 'ar'),
         ('ru', '', '', '', '', '', '')
       ]
    if ' ' not in page_name and page_content.find('{{voir-conj') == -1 \
            and page_content.find('{{invar') == -1 and page_content.find('{{verbe non standard') == -1 \
            and page_content.find('[[Image:') == -1:
        # Sinon bug https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687
        if debug_level > 0:
            print(' {{conj}}')
        for l in language_suffixes:
            if not (l[0] == 'fr' and page_name[-3:] == 'ave'):
                if re.compile(r'{{S\|verbe\|'+l[0]+'}}').search(page_content) and not \
                    re.compile(r'{{S\|verbe\|'+l[0]+u'}}[= ]+\n+[^\n]*\n*[^\n]*\n*{{(conj[a-z1-3| ]*|invar)').search(page_content):
                    if debug_level > 0:
                        print(' {{conj|')+l[0]+u'}} manquant'
                    if re.compile(r'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^{]*{{pron\|[^}]*}}').search(page_content):
                        if debug_level > 0:
                            print(' ajout de {{conj|')+l[0]+u'}} après {{pron|...}}'
                        try:
                            i1 = re.search(r'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^{]*{{pron\|[^\}]*}}', page_content).end()
                            page_content = page_content[:i1] + ' {{conjugaison|'+l[0]+'}}' + page_content[i1:]
                        except:
                            if debug_level > 0:
                                print(' sites_errors l 5390')
                    else:
                        if debug_level > 0:
                            print(' pas de prononciation pour ajouter {{conj}}')

    return page_content, summary


def treat_conjugation(page_content, final_page_content, summary, current_template, language_code, page_name):
    if current_template == '1ergroupe':
        page_content = '|grp=1' + page_content[len('1ergroupe'):]
        final_page_content = final_page_content + 'conj'
    elif current_template == '2egroupe':
        page_content = '|grp=2' + page_content[len('2egroupe'):]
        final_page_content = final_page_content + 'conj'
    elif current_template == '3egroupe':
        page_content = '|grp=3' + page_content[len('3egroupe'):]
        final_page_content = final_page_content + 'conj'
    elif current_template == 'conjugaison':
        page_content = page_content[len('conjugaison'):]
        final_page_content = final_page_content + 'conjugaison'
    elif current_template == 'conj':
        page_content = page_content[len('conj'):]
        final_page_content = final_page_content + 'conj'

    # Vérification des groupes en espagnol, portugais et italien
    if language_code == 'es':
        if page_name[len(page_name) - 2:] == 'ar' or page_name[len(page_name) - 4:] == 'arsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' + page_content[
                        page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' + page_content[
                        page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=1' + page_content
        elif page_name[len(page_name) - 2:] == 'er' or page_name[len(page_name) - 4:] == 'ersi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' + page_content[
                        page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' + page_content[
                        page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=2' + page_content
        elif page_name[len(page_name) - 2:] == 'ir' or page_name[len(page_name) - 4:] == 'irsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' + page_content[
                        page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' + page_content[
                        page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=3' + page_content

    elif language_code == 'pt':
        if page_name[len(page_name) - 2:] == 'ar' or page_name[len(page_name) - 4:] == 'ar-se':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                                   + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                                   + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=1' + page_content
        elif page_name[len(page_name) - 2:] == 'er' or page_name[len(page_name) - 4:] == 'er-se':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                                   + page_content[page_content.find('|grp=') + len( '|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                                   + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=2' + page_content
        elif page_name[len(page_name) - 2:] == 'ir' or page_name[len(page_name) - 4:] == 'ir-se':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                                   + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                                   + page_content[ page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                                   + page_content[ page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=3' + page_content

    elif language_code == 'it':
        if page_name[len(page_name) - 3:] == 'are' or page_name[len(page_name) - 4:] == 'arsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                                   + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                                   + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=1' + page_content
        elif page_name[len(page_name) - 3:] == 'ere' or page_name[len(page_name) - 4:] == 'ersi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                                   + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                                   + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                                   + page_content[ page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=2' + page_content
        elif page_name[len(page_name) - 3:] == 'ire' or page_name[len(page_name) - 4:] == 'irsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') == page_content.find('|grp=}') or page_content.find(
                        '|grp=') == page_content.find('|grp=|'):
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                                   + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                                   + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') == page_content.find('|groupe=}') or page_content.find(
                        '|groupe=') == page_content.find('|groupe=|'):
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                                   + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=3' + page_content

    if (page_content.find(language_code) != -1 and page_content.find(language_code) < page_content.find(
            '}}')) or language_code == 'fr':
        final_page_content, page_content = next_template(final_page_content, page_content)
    else:
        if page_content.find('|nocat=1') != -1:
            page_content = page_content[:page_content.find('|nocat=1')] + page_content[
                                                                          page_content.find('|nocat=1') + len(
                                                                              '|nocat=1'):]
        final_page_content = final_page_content + '|' + language_code + '}}'
        page_content = page_content[page_content.find('}}') + 2:]
    return page_content, final_page_content, summary


def treat_verb_inflexion(page_content, final_page_content, summary, current_page_content):
    if debug_level > 0:
        print('treat_verb_inflexion()')
    infinitive = get_lemma_from_conjugation(current_page_content)
    if infinitive != '':
        # TODO check infinitive suffix to avoid spreading human errors:
        # https://fr.wiktionary.org/w/index.php?title=d%C3%A9sappartient&diff=prev&oldid=27612966
        infinitive_page = get_content_from_page_name(infinitive, site)
        if infinitive_page is not None:
            # http://fr.wiktionary.org/w/index.php?title=Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet
            page_content2 = page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
            if page_content2.find('flexion=') != -1 and page_content2.find('flexion=') < page_content2.find('}}'):
                page_content3 = page_content2[page_content2.find('flexion='):len(page_content2)]
                if page_content3.find('|') != -1 and page_content3.find('|') < page_content3.find('}'):
                    page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                   + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')
                                                  + page_content2.find('flexion=')+page_content3.find('|'):]
            page_content2 = page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
            if page_content2.find(infinitive) == -1 or page_content2.find(infinitive) > page_content2.find('}}'):
                page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] + '|' \
                    + infinitive + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                if page_content.find('|' + infinitive + '\n') != -1:    # Bug de l'hyperlien vers l'annexe
                    page_content = page_content[:page_content.find('|' + infinitive + '\n')+len('|' + infinitive)] \
                        + page_content[page_content.find('|' + infinitive + '\n')+len('|' + infinitive + '\n'):]
            # Analyse du modèle en cours
            page_content2 = page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
            page_content2 = page_content2[:page_content2.find('}}')+2]
            if page_content2.find('impers=oui') == -1:
                # http://fr.wiktionary.org/w/index.php?title=Modèle:fr-verbe-flexion&action=edit
                fr_section, l_start, l_end = get_language_section(infinitive_page, 'fr')
                if infinitive_page.find('{{impers|fr}}') != -1 or (infinitive_page.find('{{impersonnel|fr}}') != -1
                                                   and fr_section is not None and count_definitions(fr_section) == 1):
                    page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                        + '|impers=oui' + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                elif (infinitive_page.find('|groupe=1') != -1 or infinitive_page.find('|grp=1') != -1) \
                        and infinitive_page.find('|groupe2=') == -1:
                    # je
                    if page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        pass
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|imp.p.2s=oui' + page_content[page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|sub.p.3s=oui' + page_content[page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|sub.p.1s=oui' + page_content[page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|ind.p.3s=oui' + page_content[page_content.find('ind.p.1s=oui') + len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                        + len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                                       + '|ind.p.3s=oui|imp.p.2s=oui' + page_content[page_content.find('ind.p.1s=oui')
                                                                                     + len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|imp.p.2s=oui|ind.p.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                          + len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                   + '|ind.p.1s=oui|ind.p.3s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                                     + len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                                       + '|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + page_content[page_content.find('ind.p.3s=oui')
                                                                                       + len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.3s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.1s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.1s=oui|sub.p.1s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.1s=oui|sub.p.1s=oui|ind.p.3s=oui' \
                            + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.1s=oui|ind.p.3s=oui|sub.p.1s=oui|ind.p.3s=oui' \
                                       + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]
                    # tu
                    if page_content2.find('ind.p.2s=oui') != -1 and page_content2.find('sub.p.2s=oui') != -1:
                        pass
                    elif page_content2.find('ind.p.2s=oui') != -1 and page_content2.find('sub.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                            + '|sub.p.2s=oui' + page_content[page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.2s=oui') == -1 and page_content2.find('sub.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.2s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # nous
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui')] \
                            + '|sub.p.1p=oui' + page_content[page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui'):]
                    if page_content2.find('ind.i.1p=oui') == -1 and page_content2.find('sub.p.1p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')]\
                            + '|ind.i.1p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # vous
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui')] \
                               + '|sub.p.2p=oui' + page_content[page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui'):]
                    if page_content2.find('ind.i.2p=oui') == -1 and page_content2.find('sub.p.2p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.2p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # ils
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui')] \
                            + '|sub.p.3p=oui' + page_content[page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui'):]
                    if page_content2.find('ind.p.3p=oui') == -1 and page_content2.find('sub.p.3p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.3p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                # Certains -ir sont du 3ème
                elif (infinitive_page.find('|groupe=2') != -1 or infinitive_page.find('|grp=2') != -1) \
                        and infinitive_page.find('{{impers') == -1 and infinitive_page.find('|groupe2=') == -1:
                    # je
                    if page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        pass
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.ps.2s=oui')+len('ind.ps.2s=oui')] \
                            + '|imp.p.2s=oui' + page_content[page_content.find('ind.ps.2s=oui')+len('ind.ps.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.ps.1s=oui')+len('ind.ps.1s=oui')] \
                            + '|ind.ps.2s=oui' + page_content[page_content.find('ind.ps.1s=oui')+len('ind.ps.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                            + '|ind.ps.1s=oui' + page_content[page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') == -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|ind.p.2s=oui' + page_content[page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')]\
                            + '|ind.p.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.ps.1s=oui')+len('ind.ps.1s=oui')] \
                                       + '|ind.ps.2s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('ind.ps.1s=oui')+len('ind.ps.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                                       + '|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') == -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                                       + '|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.2s=oui') == -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                                       + '|ind.p.1s=oui|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' \
                                       + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]

                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                            + '|ind.ps.1s=oui|ind.ps.2s=oui' + page_content[page_content.find('ind.p.2s=oui')
                                                                            + len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') == -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                                       + '|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' \
                                       + page_content[page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') == -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                                       + '|ind.p.1s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' \
                                       + page_content[page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui'):]

                    # ...
                    if page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('sub.i.1s=oui') != -1:
                        pass
                    elif page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('sub.i.1s=oui') == -1:
                        page_content = page_content[:page_content.find('sub.p.3s=oui')+len('sub.p.3s=oui')] \
                            + '|sub.i.1s=oui' + page_content[page_content.find('sub.p.3s=oui')+len('sub.p.3s=oui'):]
                    elif page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('sub.i.1s=oui') != -1:
                        page_content = page_content[:page_content.find('sub.p.1s=oui')+len('sub.p.1s=oui')] \
                            + '|sub.p.3s=oui' + page_content[page_content.find('sub.p.1s=oui')+len('sub.p.1s=oui'):]
                    elif page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('sub.i.1s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    elif page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('sub.i.1s=oui') == -1:
                        page_content = page_content[:page_content.find('sub.p.1s=oui')+len('sub.p.1s=oui')]\
                            + '|sub.p.3s=oui|sub.i.1s=oui' + page_content[page_content.find('sub.p.1s=oui')
                                                                          + len('sub.p.1s=oui'):]
                    elif page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('sub.i.1s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.1s=oui|sub.p.3s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                          +len('fr-verbe-flexion'):]
                    elif page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('sub.i.1s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.1s=oui|sub.i.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                          +len('fr-verbe-flexion'):]
                    # tu
                    if page_content2.find('sub.p.2s=oui') != -1 and page_content2.find('sub.i.2s=oui') != -1:
                        pass
                    if page_content2.find('sub.p.2s=oui') != -1 and page_content2.find('sub.i.2s=oui') == -1:
                        page_content = page_content[:page_content.find('sub.p.2s=oui')+len('sub.p.2s=oui')] \
                            + '|sub.i.2s=oui' + page_content[page_content.find('sub.p.2s=oui')+len('sub.p.2s=oui'):]
                    if page_content2.find('sub.p.2s=oui') == -1 and page_content2.find('sub.i.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.2s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # il
                    if page_content2.find('ind.p.3s=oui') != -1 and page_content2.find('ind.ps.3s=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3s=oui') != -1 and page_content2.find('ind.ps.3s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|ind.ps.3s=oui' + page_content[page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    if page_content2.find('ind.p.3s=oui') == -1 and page_content2.find('ind.ps.3s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.3s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # nous
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui')] \
                            + '|sub.p.1p=oui' + page_content[page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui'):]
                    if page_content2.find('ind.i.1p=oui') == -1 and page_content2.find('sub.p.1p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.1p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # vous
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui')] \
                            + '|sub.p.2p=oui' + page_content[page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui'):]
                    if page_content2.find('ind.i.2p=oui') == -1 and page_content2.find('sub.p.2p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.2p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # ils
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui')] \
                            + '|sub.p.3p=oui' + page_content[page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui'):]
                    if page_content2.find('ind.p.3p=oui') == -1 and page_content2.find('sub.p.3p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.3p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                elif (infinitive_page.find('|groupe=3') != -1 or infinitive_page.find('|grp=3') != -1) \
                        and infinitive_page.find('|groupe2=') == -1:
                    if page_content2.find('grp=3') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|grp=3' + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion'):]

    final_page_content = final_page_content + page_content[:page_content.find('\n')+1]
    page_content = page_content[page_content.find('\n')+1:]
    return page_content, final_page_content, summary


def treat_noun_inflexion(page_content, summary, page_name, regex_page_name, natures_with_plural, language_code,
                         singular_page_name):
    if debug_level > 0:
        print(' treat_noun_inflexion()')
    for nature in natures_with_plural:
        regex = r"(== {{langue|" + language_code + r"}} ==\n=== {{S\|" + nature + r"\|" + language_code + r")\|num=2"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
            summary = summary + ', retrait de |num='

        regex = r"(=== {{S\|" + nature + r"\|" + language_code + r")(\}} ===\n[^\n]*\n*'''" + regex_page_name \
                + r"'''[^\n]*\n# *'*'*(Masculin)*(Féminin)* *[P|p]luriel de *'*'* *\[\[)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1|flexion\2', page_content)
            summary = summary + ', ajout de |flexion'

        if page_name[-2:] == 'ss':
            if debug_level > 0:
                print('  -ss')
        elif singular_page_name != '':
            inflexion_inflexion_template = get_inflexion_template(page_name, language_code, nature)
            if inflexion_inflexion_template is None or inflexion_inflexion_template == '':
                if debug_level > 0:
                    print('  Ajout d\'une boite dans une flexion')
                lemma_inflexion_template = get_inflexion_template_from_lemma(singular_page_name, language_code, nature)
                if lemma_inflexion_template is not None:
                    for inflexion_template_fr_with_ms in inflexion_templates_fr_with_ms:
                        if lemma_inflexion_template.find(inflexion_template_fr_with_ms) != -1:
                            if debug_level > 0:
                                print('  inflexion_templates_fr_with_ms')
                            regex = r"\|ms=[^\|}]*"
                            if not re.search(regex, lemma_inflexion_template):
                                lemma_inflexion_template = lemma_inflexion_template + r'|ms=' + singular_page_name
                    for inflexion_template_fr_with_s in inflexion_templates_fr_with_s:
                        if lemma_inflexion_template.find(inflexion_template_fr_with_s) != -1:
                            regex = r"\|s=[^\|}]*"
                            if not re.search(regex, lemma_inflexion_template):
                                lemma_inflexion_template = lemma_inflexion_template + r'|s=' + singular_page_name

                    ''' Remplacement des {{fr-rég}} par plus précis (lancé pour patcher des pages)
                    if lemma_inflexion_template.find(language_code + r'-rég') != -1: lemma_inflexion_template = ''
                    if lemma_inflexion_template != '':
                        regex = r"(=== {{S\|" + nature + r"\|" + language_code + r"\|flexion}} ===\n){{fr\-rég\|[^}]*}}"
                        if re.search(regex, page_content):
                            page_content = re.sub(regex, r'\1{{' + lemma_inflexion_template + r'}}', page_content)
                            summary = summary + ', remplacement de {{' + language_code + r'-rég}} par {{' \
                            + lemma_inflexion_template + r'}}'
                    '''

                if lemma_inflexion_template is not None and lemma_inflexion_template != '':
                    regex = r"(=== {{S\|" + nature + r"\|" + language_code + r"\|flexion}} ===\n)('''" + page_name \
                            + r"''')"
                    if re.search(regex, page_content):
                        page_content = re.sub(regex, r'\1{{' + lemma_inflexion_template + r'}}\n\2', page_content)
                        summary = summary + ', ajout de {{' + lemma_inflexion_template + r'}} depuis le lemme'

        if page_name[-1:] != 's':
            regex = r"(=== {{S\|" + nature + r"\|" + language_code + r"\|flexion}} ===\n)('''" + page_name \
                    + r"''' {{pron\|)([^\|}]*)(\|" + language_code \
                    + r"}}\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
            if re.search(regex, page_content):
                # page_content = re.sub(regex, r'\1{{' + language_code + r'-rég|s=\7|\3}}\n\2\3\4\7', page_content)
                page_content = re.sub(regex,
                                      r'\1{{' + language_code + r'-rég|s=' + singular_page_name + '|\3}}\n\2\3\4\5',
                                      page_content)
                summary = summary + ', ajout de {{' + language_code + r'-rég}}'

            regex = r"(=== {{S\|" + nature + r"\|" + language_code + r"\|flexion}} ===\n)('''" + page_name \
                    + r"'''\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
            if re.search(regex, page_content):
                page_content = re.sub(regex, r'\1{{' + language_code + r'-rég|s=' + singular_page_name
                                      + '|}}\n\2\5', page_content)
                summary = summary + ', ajout de {{' + language_code + r'-rég}}'

    if debug_level > 1:
        input(page_content)

    if debug_level > 1:
        print('  en')
    if page_name[-2:] != 'ss' and page_name[-3:] != 'hes' and page_name[-3:] != 'ies' \
            and page_name[-3:] != 'ses' and page_name[-3:] != 'ves':
        regex = r"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + page_name \
                + r"''' {{pron\|)([^\|}]*)([s|z]\|en}}\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1{{en-nom-rég|sing=\5|\3}}\n\2\3\4\5', page_content)
            summary = summary + ', ajout de {{en-nom-rég}}'

        regex = r"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + page_name \
                + r"'''\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1{{en-nom-rég|sing=\3|}}\n\2\3', page_content)
            summary = summary + ', ajout de {{en-nom-rég}}'
    return page_content, summary


def treat_translations(page_content, final_page_content, summary, end_position, site_family):
    if end_position == page_content.find('}}') or end_position == page_content.find(
            '--}}') - 2 or end_position == page_content.find('|en|}}') - 4:
        final_page_content = final_page_content + page_content[:page_content.find('}}') + 2]
        final_page_content, page_content = next_template(final_page_content, page_content)
    else:
        # Lettres spéciales à remplacer dans les traductions vers certaines langues
        page_content2 = page_content[end_position + 1:]
        current_language = page_content2[:page_content2.find('|')]
        if current_language == 'ro' or current_language == 'mo':
            while page_content.find('ş') != -1 and page_content.find('ş') < page_content.find('\n'):
                page_content = page_content[:page_content.find('ş')] + 'ș' + page_content[page_content.find('ş') + 1:]
            while page_content.find('Ş') != -1 and page_content.find('Ş') < page_content.find('\n'):
                page_content = page_content[:page_content.find('Ş')] + 'Ș' + page_content[page_content.find('Ş') + 1:]
            while page_content.find('ţ') != -1 and page_content.find('ţ') < page_content.find('\n'):
                page_content = page_content[:page_content.find('ţ')] + 'ț' + page_content[page_content.find('ţ') + 1:]
            while page_content.find('Ţ') != -1 and page_content.find('Ţ') < page_content.find('\n'):
                page_content = page_content[:page_content.find('Ţ')] + 'Ț' + page_content[page_content.find('Ţ') + 1:]
        elif current_language == 'az' or current_language == 'ku' or current_language == 'sq' or \
                current_language == 'tk' or current_language == 'tr' or current_language == 'tt':
            while page_content.find('ș') != -1 and page_content.find('ș') < page_content.find('\n'):
                page_content = page_content[:page_content.find('ș')] + 'ş' + page_content[page_content.find('ș') + 1:]
            while page_content.find('Ș') != -1 and page_content.find('Ș') < page_content.find('\n'):
                page_content = page_content[:page_content.find('Ș')] + 'Ş' + page_content[page_content.find('Ș') + 1:]
            while page_content.find('ț') != -1 and page_content.find('ț') < page_content.find('\n'):
                page_content = page_content[:page_content.find('ț')] + 'ţ' + page_content[page_content.find('ț') + 1:]
            while page_content.find('Ț') != -1 and page_content.find('Ț') < page_content.find('\n'):
                page_content = page_content[:page_content.find('Ț')] + 'Ţ' + page_content[page_content.find('Ț') + 1:]
        elif current_language == 'fon':
            while page_content.find('ε') != -1 and page_content.find('ε') < page_content.find('\n'):
                page_content = page_content[:page_content.find('ε')] + 'ɛ' + page_content[page_content.find('ε') + 1:]
        # http://fr.wiktionary.org/wiki/Mod%C3%A8le:code_interwiki
        elif current_language == 'cmn':
            page_content = page_content[:page_content.find('cmn')] + 'zh' + page_content[
                                                                            page_content.find('cmn') + len('cmn'):]
        elif current_language == 'nn':
            page_content = page_content[:page_content.find('nn')] + 'no' + page_content[
                                                                           page_content.find('nn') + len('nn'):]
        elif current_language == 'per':
            page_content = page_content[:page_content.find('per')] + 'fa' + page_content[
                                                                            page_content.find('per') + len('per'):]
        elif current_language == 'wel':
            page_content = page_content[:page_content.find('wel')] + 'cy' + page_content[
                                                                            page_content.find('wel') + len('wel'):]
        elif current_language == 'zh-classical':
            page_content = page_content[:page_content.find('zh-classical')] + 'lzh' + page_content[page_content.find(
                'zh-classical') + len('zh-classical'):]
        elif current_language == 'ko-Hani':
            page_content = page_content[:page_content.find('ko-Hani')] + 'ko' + page_content[
                                                                                page_content.find('ko-Hani') + len(
                                                                                    'ko-Hani'):]
        elif current_language == 'ko-hanja':
            page_content = page_content[:page_content.find('ko-hanja')] + 'ko' + page_content[
                                                                                 page_content.find('ko-hanja') + len(
                                                                                     'ko-hanja'):]
        elif current_language == 'zh-min-nan':
            page_content = page_content[:page_content.find('zh-min-nan')] + 'nan' + page_content[page_content.find(
                'zh-min-nan') + len('zh-min-nan'):]
        elif current_language == 'roa-rup':
            page_content = page_content[:page_content.find('roa-rup')] + 'rup' + page_content[
                                                                                 page_content.find('roa-rup') + len(
                                                                                     'roa-rup'):]
        elif current_language == 'zh-yue':
            page_content = page_content[:page_content.find('zh-yue')] + 'yue' + page_content[
                                                                                page_content.find('zh-yue') + len(
                                                                                    'zh-yue'):]
        page_content2 = page_content[end_position + 1:]
        current_language = page_content2[:page_content2.find('|')]

        if current_language != '':
            # TODO: reproduire bug site fermé https://fr.wiktionary.org/w/index.php?title=chat&diff=prev&oldid=9366302
            # Identification des Wiktionnaires hébergeant les traductions
            external_site_name = ''
            external_page_name = ''
            d = 0
            page_content3 = page_content2[page_content2.find('|') + 1:]
            if debug_level > d:
                print(' langue distante : ' + current_language)
            if page_content3.find('}}') == '' or not page_content3.find('}}'):
                if debug_level > d:
                    print('  aucun mot distant')
                if final_page_content.rfind('<!--') == -1 or final_page_content.rfind(
                        '<!--') < final_page_content.rfind('-->'):
                    # On retire le modèle pour que la page ne soit plus en catégorie de maintenance
                    if debug_level > d:
                        print(' Retrait de commentaire de traduction l 4362')
                    final_page_content = final_page_content[:-2]
                    backward = True
            elif current_language == 'conv':
                external_site_name = get_wiki('species', 'species')
            elif current_language in incubator_wiktionaries:
                # Otherwise: Non-JSON response received from server wiktionary:ba; the server may be down.
                external_site_name = None
            else:
                external_site_name = get_wiki(current_language, site_family)
            if external_site_name is None:
                if debug_level > d:
                    print('  no site (--)')
                final_page_content, page_content = next_translation_template(final_page_content, page_content, '--')
                external_site_name = ''
            elif external_site_name != '':
                if page_content3.find('|') != -1 and page_content3.find('|') < page_content3.find('}}'):
                    external_page_name = page_content3[:page_content3.find('|')]
                else:
                    external_page_name = page_content3[:page_content3.find('}}')]
            if external_page_name != '' and external_page_name.find('<') != -1:
                external_page_name = external_page_name[:external_page_name.find('<')]
            if debug_level > d:
                msg = ' page distante : ' + external_page_name
                try:
                    print(msg)
                except UnicodeEncodeError as e:
                    # Python 2 only
                    print(msg.encode(config.console_encoding, 'replace'))
            # Connexions aux Wiktionnaires pour vérifier la présence de la page (TODO: et de sa section langue)
            if external_site_name != '' and external_page_name != '':
                is_page_found = True
                try:
                    external_page = Page(external_site_name, external_page_name)
                except pywikibot.exceptions.InconsistentTitleError as e:
                    if debug_level > d:
                        print(str(e))
                    final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')
                    is_page_found = False
                except pywikibot.exceptions.InvalidTitleError as e:
                    if debug_level > d:
                        print(str(e))
                    final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')
                    is_page_found = False
                except pywikibot.exceptions.NoPageError as e:
                    if debug_level > d:
                        print(str(e))
                    if external_page_name.find('\'') != -1:
                        external_page_name = external_page_name.replace('\'', '’')
                    elif external_page_name.find('’') != -1:
                        external_page_name = external_page_name.replace('’', '\'')
                    if external_page_name != external_page.title():
                        try:
                            external_page = Page(external_site_name, external_page_name)
                        except pywikibot.exceptions.NoPageError:
                            final_page_content, page_content = next_translation_template(final_page_content,
                                                                                         page_content, '-')
                            is_page_found = False
                            external_page = None
                except BaseException as e:
                    if debug_level > d:
                        print(str(e))
                    is_page_found = False

                if is_page_found:
                    try:
                        is_external_page_exist = external_page.exists()
                    except AttributeError:
                        if debug_level > d:
                            print('  removed site (--)')
                        final_page_content, page_content = next_translation_template(final_page_content,
                                                                                     page_content, '--')
                        is_external_page_exist = False
                    except pywikibot.exceptions.InconsistentTitleError:
                        if debug_level > d:
                            print('  InconsistentTitleError (-)')
                        final_page_content, page_content = next_translation_template(final_page_content,
                                                                                     page_content, '-')
                        is_external_page_exist = False

                    if is_external_page_exist:
                        if debug_level > d:
                            print('  exists (+)')
                        final_page_content, page_content = next_translation_template(final_page_content,
                                                                                     page_content, '+')
    return page_content, final_page_content, summary


def treat_pronunciation(page_content, final_page_content, summary, end_position, current_template, language_code):
    # Tri des lettres de l'API
    if current_template == 'pron':
        page_content2 = page_content[end_position+1:page_content.find('}}')]
        while page_content2.find('\'') != -1 and page_content2.find('\'') < page_content2.find('}}') \
            and (page_content2.find('\'') < page_content2.find('|') or page_content2.find('|') == -1):
            page_content = page_content[:page_content.find('\'')] + 'ˈ' + page_content[page_content.find('\'')+1:]
        while page_content2.find('ˈˈˈ') != -1 and page_content2.find('ˈˈˈ') < page_content2.find('}}') \
            and (page_content2.find('ˈˈˈ') < page_content2.find('|') or page_content2.find('|') == -1):
            page_content = page_content[:page_content.find('ˈˈˈ')] + '\'\'\'' + page_content[page_content.find('ˈˈˈ')+3:]
        while page_content2.find('ε') != -1 and page_content2.find('ε') < page_content2.find('}}') \
            and (page_content2.find('ε') < page_content2.find('|') or page_content2.find('|') == -1):
            page_content = page_content[:page_content.find('ε')] + 'ɛ' + page_content[page_content.find('ε')+1:]
        while page_content2.find('ε̃') != -1 and page_content2.find('ε̃') < page_content2.find('}}') \
            and (page_content2.find('ε̃') < page_content2.find('|') or page_content2.find('|') == -1):
            page_content = page_content[:page_content.find('ε̃')] + 'ɛ̃' + page_content[page_content.find('ε̃')+1:]
        while page_content2.find(':') != -1 and page_content2.find(':') < page_content2.find('}}') \
            and (page_content2.find(':') < page_content2.find('|') or page_content2.find('|') == -1):
            page_content = page_content[:page_content.find(':')] + 'ː' + page_content[page_content.find(':')+1:]
        while page_content2.find('g') != -1 and page_content2.find('g') < page_content2.find('}}') \
            and (page_content2.find('g') < page_content2.find('|') or page_content2.find('|') == -1) \
            and page_content2.find('g') != page_content2.find('lang=')+3:
            page_content = page_content[:page_content.find('g')] + 'ɡ' + page_content[page_content.find('g')+1:]

        # if language_code == 'es': β/, /ð/ et /ɣ/ au lieu de de /b/, /d/ et /ɡ/
    if page_content[:8] == 'pron||}}':
        final_page_content = final_page_content + page_content[:page_content.find('}}')] + language_code + '}}'
    elif page_content[end_position:end_position+3] == '|}}' or page_content[end_position:end_position+4] == '| }}':
        final_page_content = final_page_content + current_template + "||" + language_code + '}}'
    elif (page_content.find("lang=") != -1 and page_content.find("lang=") < page_content.find('}}')):
        final_page_content = final_page_content + page_content[:page_content.find('}}')+2]
    elif end_position == page_content.find('|'):
        page_content2 = page_content[end_position+1:page_content.find('}}')]
        if page_content2.find('|') == -1:
            final_page_content = final_page_content + page_content[:page_content.find('}}')] + "|" + language_code + '}}'
        else:
            final_page_content = final_page_content + page_content[:page_content.find('}}')+2]
    elif end_position == page_content.find('}}'):
        final_page_content = final_page_content + current_template + "||" + language_code + '}}'
    else:
        final_page_content = final_page_content + page_content[:page_content.find('}}')] + "|" + language_code + '}}'
    page_content = page_content[page_content.find('}}')+2:]
    return page_content, final_page_content, summary


def add_anagrams(page_content, summary, page_name, language_code):
    anagrams = get_anagram(page_name)
    anagrams_list = ''
    for anagram in anagrams:
        if anagram != page_name:
            if debug_level > 0:
                print(' ' + anagram)
            anagram_page = Page(site, anagram)
            if anagram_page.exists():
                if anagram_page.namespace() != 0 and anagram != 'User:JackBot/test':
                    break
                else:
                    anagram_page_content = get_content_from_page(anagram_page)
                    if anagram_page_content is None:
                        break
                if anagram_page_content.find('{{langue|' + language_code + '}}') != -1:
                    anagrams_list = anagrams_list + '* {{lien|' + anagram + '|' + language_code + '}}\n'
                    if debug_level > 0:
                        print(' trouvé')
    if anagrams_list != '':
        summary = summary + ', ajout d\'anagrammes ' + language_code
        anagram_position = page_content.find('{{langue|' + language_code + '}}') + len(
            '{{langue|' + language_code + '}}')
        page_content2 = page_content[anagram_position:]
        if page_content2.find('\n=== {{S|voir') != -1 and ((page_content2.find(
                '{{langue|') != -1 and page_content2.find('{{S|voir') < page_content2.find(
                '{{langue|')) or page_content2.find('{{langue|') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '\n=== {{S|voir')] + '\n=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('\n=== {{S|voir'):]
        elif page_content2.find('\n=== {{S|références}}') != -1 and ((page_content2.find(
                '{{langue|') != -1 and page_content2.find('\n=== {{S|références}}') < page_content2.find(
                '{{langue|')) or page_content2.find('{{langue|') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '\n=== {{S|références}}')] + '\n=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('\n=== {{S|références}}'):]
        elif page_content2.find('== {{langue|') != -1 and ((page_content2.find(
                '[[Catégorie:') != -1 and page_content2.find('== {{langue|') < page_content2.find(
                '[[Catégorie:')) or page_content2.find('[[Catégorie:') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '== {{langue|')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('== {{langue|'):]
        elif page_content2.find('=={{langue|') != -1 and ((page_content2.find(
                '[[Catégorie:') != -1 and page_content2.find('=={{langue|') < page_content2.find(
                '[[Catégorie:')) or page_content2.find('[[Catégorie:') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '=={{langue|')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('=={{langue|'):]
        elif page_content2.find('{{clé de tri') != -1:
            page_content = page_content[:anagram_position + page_content2.find(
                '{{clé de tri')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('{{clé de tri'):]
        elif page_content2.find('[[Catégorie:') != -1:
            page_content = page_content[:anagram_position + page_content2.find(
                '[[Catégorie:')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                           + page_content[anagram_position + page_content2.find('[[Catégorie:'):]
        else:
            if debug_level > 0:
                print(" Ajout avant les interwikis")
            regex = r'\n\[\[\w?\w?\w?:'
            if re.compile(regex).search(page_content):
                try:
                    page_content = page_content[:re.search(regex,
                   page_content).start()] + '\n=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                                   + page_content[re.search(regex, page_content).start():]
                except BaseException as e:
                    if debug_level > 0:
                        print('pb regex interwiki')
            else:
                page_content = page_content + '\n\n=== {{S|anagrammes}} ===\n' + anagrams_list
    return page_content, summary

'''
TODO:
    deploy add_pronunciationFromContent()
    def sortSections(page_content):
    def uncategorizeDoubleTemplateWhenCategory(page_content, summary):
    def checkTranslationParagraphsNumberBySense(page_content, summary):

if page_content.find('{{conj') != -1:
    if debug_level > 0: print(' Ajout des groupes dans {{conj}}')
'''

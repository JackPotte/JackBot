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
from fr_wiktionary_old_templates import *


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
            print(f' lemme de locution trouvé : {lemma_page_name}')
        lemma_page_name = page_name[:page_name.find(' ')]
    return lemma_page_name


def get_gender_from_page_name(page_name, language_code='fr', nature=None):
    if debug_level > 1:
        print('\nget_gender_from_page_name')
    gender = None
    page_content = get_content_from_page_name(page_name, site)
    if page_content is None:
        return gender
    if page_content.find(f'|{language_code}' + '}} {{m}}') != -1:
        gender = '{{m}}'
    elif page_content.find(f'|{language_code}' + '}} {{f}}') != -1:
        gender = '{{f}}'
    elif page_content.find("''' {{m}}") != -1:
        gender = '{{m}}'
    elif page_content.find("''' {{f}}") != -1:
        gender = '{{f}}'
    if debug_level > 1:
        input(gender)
    return gender


def get_lemma_from_content(page_content, language_code='fr'):
    if debug_level > 1:
        print('\ngetLemmaFromContent')
    lemma_page_name = get_lemma_from_plural(page_content, language_code)
    if lemma_page_name == '':
        lemma_page_name = get_lemma_from_conjugation(
            page_content, language_code)
    return lemma_page_name


def get_lemma_from_plural(page_content, language_code='fr', natures=None):
    if natures is None:
        natures = ['nom', 'adjectif', 'suffixe']
    if debug_level > 1:
        print('\nget_lemma_from_plural')
    lemma_page_name = ''
    regex = r"(=== {{S\|(" + '|'.join(natures) + r")\|" + language_code + r"\|flexion}} ===\n({{" + language_code + \
        r"\-[^}]*}}\n)?'''[^\n]+\n# *'* *([Mm]asculin|[Ff]éminin)* *'* *'*[P|p]luriel *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            print(s[1])
            input(s[6])
        lemma_page_name = s[6]
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03<<red>>" +
                         lemma_page_name + "\03<<default>>")
    if debug_level > 1:
        input(page_content)

    return lemma_page_name


def get_lemma_from_feminine(page_content, language_code='fr', natures=None):
    if natures is None:
        natures = ['nom', 'adjectif']
    if debug_level > 1:
        print('\nget_lemma_from_feminine()')
    lemma_page_name = ''
    regex = r"(=== {{S\|(" + '|'.join(natures) + ")\|" + language_code + "\|flexion}} ===\n({{" + language_code + \
        "\-[^}]*}}\n)?'''[^\n]+\n# *'* *[Ff]éminin *'* *'*(singulier|pluriel)? *'* *de'* *'* *(\[\[|{{li?e?n?\|))([^#\|\]}]+)"
    s = re.search(regex, page_content)
    if s:
        if debug_level > 1:
            # 2 = adjectif, 3 = fr-rég, 4 = Féminin, 5 = {{lien|, 6 = lemme
            print(s[1])
            input(s[6])
        lemma_page_name = s[6]
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03<<red>>" +
                         lemma_page_name + "\03<<default>>")
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
            print(s[1])
            input(s[4])
        lemma_page_name = s[4]
    if debug_level > 0:
        pywikibot.output(" lemma_page_name found: \03<<red>>" +
                         lemma_page_name + "\03<<default>>")

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
            if s[1] is not None:
                print(f' {s[1]}')
            if s[2] is not None:
                print(f' {s[2]}')
            if s[3] is not None:
                print(f' {s[3]}')
            if s[4] is not None:
                print(f' {s[4]}')
        inflexion_template = s[4]
    if debug_level > 0:
        pywikibot.output(" inflexion_template found: \03<<green>>" +
                         inflexion_template + "\03<<default>>")
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

    regex = r"=== {{S\|" + nature + r"\|" + language + \
        r"(\|num=[0-9])?}} ===\n{{(" + language + r"\-[^}]+)}}"
    if debug_level > d:
        print(f' {regex}')
    s = re.search(regex, page_content)
    if s:
        if debug_level > d:
            if s[1] is not None:
                print(f' {s[1]}')
            if s[2] is not None:
                print(f' {s[2]}')
        inflexion_template = s[2]
    if debug_level > d:
        print(f' inflexion_template found: {inflexion_template}')
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
    return s or []


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
        print(s[1])
    return s[1]


def count_definitions(page_content):
    if debug_level > 1:
        print('\ncount_definitions')
    definitions = get_definitions(page_content)
    if definitions is None:
        return 0
    definitions = definitions.split('\n')
    return sum(
        definition[:1] == '#' and definition[:2] not in [u'#:', '#*']
        for definition in definitions
    )


def count_first_definition_size(page_content):
    if debug_level > 1:
        print('\ncount_first_definition_size')

    definition = get_definitions(page_content)
    if definition is None:
        return 0
    if definition.find('\n') != -1:
        definition = definition[:definition.find('\n')]
    if debug_level > 1:
        print(
            ' First definition:')  # regex = r"\n'''[^\n]*(\n#(!:\*)?.*(\n|$))"
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
        print(f' count_first_definition_size(): {len(words)}')
    return len(words)


def get_pronunciation(page_content, language_code):
    if debug_level > 1:
        print('\nget_pronunciation')

    pronunciation = get_pronunciation_from_pron(page_content, language_code)
    if pronunciation is not None:
        return pronunciation

    pronunciation = get_pronunciation_from_fr(page_content, language_code)
    if pronunciation is not None:
        return pronunciation

    return ''

def get_pronunciation_from_pron(page_content, language_code):
    regex = r"{{pron\|([^}]+)\|" + language_code + "}}"
    s = re.search(regex, page_content)
    pronunciation = None
    if s:
        pronunciation = s[1]
        pronunciation = pronunciation[:pronunciation.find('=')]
        pronunciation = pronunciation[:pronunciation.rfind('|')]
    return pronunciation

def get_pronunciation_from_fr(page_content, language_code):
    if language_code != 'fr':
        return None

    regex = r".*'''([^']+)'''.*"
    s = re.search(regex, page_content, re.MULTILINE | re.DOTALL)
    if not s:
        return
    page_name = s[1]

    templates = '|'.join(flexion_templates_fr_with_s) + '|' + '|'.join(flexion_templates_fr_with_ms)
    templates2 = '|'.join(flexion_templates_fr)

    pronunciation = ''
    regex = r'{{(' + re.escape(templates) + r")\|([^{}\|=]+)([^{}]*}}\n\'\'\'" \
        + re.escape(page_name).replace('User:', '') + r"'\'\')( *{*f?m?n?}* *)\n"
    s = re.search(regex, page_content)
    if s:
        pronunciation = s[1]
        if debug_level > 0:
            print(' prononciation trouvée en {{{1}}} dans une boite de flexion : ' + pronunciation)
        return pronunciation

    regex = r'{{(' + re.escape(templates) + r")\|([^{}]+)}}"
    s = re.search(regex, page_content)
    if s:
        template = s[1]
        if debug_level > 0:
            print(template)

    regex = r'{{(' + templates2 + r")\|([^{}]+)}}"
    s = re.search(regex, page_content)
    if s:
        template = s[1]
        parameters = s[2]
        if debug_level > 0:
            print(f' template trouvé : {template}')
        if debug_level > 0:
            print(f' paramètres : {parameters}')

        if template == 'fr-accord-comp':
            # pronunciation = get_parameter(template, 3)
            pass
        elif template == 'fr-accord-comp-mf':
            # pronunciation = get_parameter(template, 3)
            pass
        elif template == 'fr-accord-eur':
            # TODO pronunciation = get_parameter(template, 2)
            pronunciation = parameters[parameters.rfind('|')+1:]
            pronunciation = f'{pronunciation}œʁ'
        elif template == 'fr-accord-eux':
            # pronunciation = get_parameter(template, 2)
            pronunciation = f'{pronunciation}ø'
        elif template == 'fr-accord-f':
            # pronunciation = get_parameter(template, 2)
            pronunciation = f'{pronunciation}f'
        elif template == 'fr-accord-ind':
            pronunciation = get_parameter(template, 'pm')
        elif template == 'fr-accord-mf':
            pronunciation = get_parameter(template, 'pron')
        # TODO
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

        if '.' in pronunciation and debug_level > 0:
            print(f' prononciation trouvée dans une boite de flexion : {pronunciation}')
    if debug_level > 1:
        input('Fin du test des flexions féminines')
    return pronunciation


def get_plural_pronunciation(page_content, language_code):
    global debug_level
    if debug_level > 0:
        print('\nget_plural_pronunciation')
    if language_code != 'fr':
        return None

    if page_content.find('|pp=') != -1 and page_content.find('|pp=') < page_content.find('}}'):
        if debug_level > 0:
            print(' pp=')
        page_content2 = page_content[page_content.find('|pp=')+4:page_content.find('}}')]
        if page_content2.find('|') != -1:
            pron = page_content[page_content.find('|pp=')+4:page_content.find('|pp=')+4+page_content2.find('|')]
        else:
            pron = page_content[page_content.find('|pp=')+4:page_content.find('}}')]
    else:
        if debug_level > 1:
            print('  pronunciation identical between singular and plural')
        pron = page_content[:page_content.find('}}')]
        if debug_level > 1:
            print(f'  pron before while: {pron}')
        if '|pron=' in pron:
            pron = '|' + pron[pron.find('|pron=')+len('|pron='):]

        pron_array = pron.split('|')
        # Ex: {{fr-rég|a.kʁɔ.sɑ̃.tʁik|mf=oui}}
        n = 0
        while n < len(pron_array) and (pron_array[n] == '' or pron_array[n].find('=') != -1):
            n += 1
        pron = '|' if n == len(pron_array) else f'|{pron_array[n]}'
        if debug_level > 1:
            print(f'  pron after while: {pron}')
    pron = trim(pron)

    if pron[:1] == '|':
        pron = pron[1:]
    if '|' in pron:
        pron = trim(pron[:pron.find('|')])
    if '/' in pron:
        pron = trim(pron[:pron.find('/')])

    if debug_level > 0:
        try:
            print(f'  Pronunciation found: {pron}')
        except UnicodeDecodeError:
            print('  Pronunciation to decode')
        except UnicodeEncodeError:
            print('  Pronunciation to encode')

    return pron


def add_pronunciation_from_content(page_content, language_code):
    if debug_level > 1:
        print('\nadd_pronunciationFromContent')
    if page_content.find('{{pron||' + language_code + '}}') != -1:
        pronunciation = get_pronunciation(page_content, language_code)
        if pronunciation != '':
            page_content = page_content.replace(
                '{{pron||' + language_code + '}}',
                '{{pron|' + pronunciation + '|' + language_code + '}}'
            )
    return page_content


def add_category(page_content, language_code, line_content):
    if debug_level > 1:
        print('\ndo_add_category')
    if line_content.find('[[Catégorie:') == -1:
        line_content = f'[[Catégorie:{line_content}]]'

    return add_line(page_content, language_code, 'catégorie', line_content)


def remove_category(page_content, category, summary):
    if debug_level > 1:
        print('\nremoveCategory(' + category + ')')
    regex_category = r'(\n\[\[Catégorie:' + category + r'(\||\])[^\]]*\]\]?)'
    new_page_content = re.sub(regex_category, r'', page_content)
    if new_page_content != page_content:
        summary = f'{summary}, retrait de [[Catégorie:{category}]]'

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
            old_section, l_start, l_end = get_language_section(
                old_section, language)
        if old_section is not None:
            for section in in_section:
                old_sub_section, s_start, s_end = get_section_by_name(
                    old_section, section)
                if old_sub_section is not None:
                    new_sub_section = re.sub(regex_template, r'', old_sub_section)
                    if old_sub_section != new_sub_section:
                        page_content = page_content.replace(
                            old_sub_section, new_sub_section)
                        summary = summary + \
                            ', retrait de {{' + template + \
                            '}} dans {{S|' + section + '}}'
    else:
        new_section = re.sub(regex_template, r'', old_section)
        if old_section != new_section:
            page_content = page_content.replace(old_section, new_section)
            summary = summary + ', retrait de {{' + template + '}}'
    return page_content, summary


def add_line(page_content, language_code, section_name, line_content):
    d = 0
    if debug_level > d:
        pywikibot.output(
            "\n\03<<red>>---------------------------------------------\03<<default>>")
        print('\nadd_line(' + language_code + ', ' + section_name + ')')
    if (
        page_content != ''
        and language_code != ''
        and section_name != ''
        and line_content != ''
        and page_content.find(line_content) == -1
        and page_content.find('{{langue|' + language_code + '}}') != -1
    ):
        if section_name == 'catégorie' and line_content.find('[[Catégorie:') == -1:
            line_content = f'[[Catégorie:{line_content}]]'
        if section_name == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
            line_content = '{{clé de tri|' + line_content + '}}'

        section_to_add_order = get_order_by_section_name(section_name)
        if section_to_add_order == len(sections):
            if debug_level > d:
                print(
                    f' ajout de la sous-section : {section_name} dans une section inconnue'
                    + f' (car {len(sections)} = {str(section_to_add_order)})\n'
                )
            return page_content

        # Recherche de l'ordre réel de la section à ajouter
        language_section, start_position, end_position = get_language_section(page_content, language_code)
        if language_section is None:
            # TODO add section language too in option
            return page_content

        sections_in_page = re.findall(r"\n=+ *{{S\|?([^}/|]+)([^}]*)}}", language_section)
        if debug_level > d + 1:
            # ex : [('nom', '|fr|num=1'), ('synonymes', '')]
            input(str(sections_in_page))

        final_section = None
        regex = r'\n=* *{{S\|' + section_name + r'[}\|]'
        if not re.search(regex, language_section):
            page_content, language_section, start_position, end_position = add_section(
                page_content,
                sections_in_page,
                section_name,
                section_to_add_order,
                language_section,
                start_position,
                end_position,
                line_content,
                language_code
            )

            s = re.search(regex, language_section)
            if s:
                final_section = language_section[s.end():]
            else:
                regex = r'\n=* *{{S\|' + \
                    sections_in_page[len(sections_in_page)-1][0]
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
                + '\n' + line_content + \
                final_section[s.start():] + \
                page_content[start_position + end_position:]
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
        pywikibot.output(
            "\n\03<<red>>---------------------------------------------\03<<default>>")
    return page_content


def add_section(
        page_content,
        sections_in_page,
        section_name,
        section_to_add_order,
        language_section,
        start_position,
        end_position,
        line_content,
        language_code
    ):
    d = 0
    o = 0
    section_order = get_order_by_section_name(sections_in_page[o][0])
    while o < len(sections_in_page) and section_order <= section_to_add_order:
        try:
            current_section_name = sections_in_page[o][0]
        except IndexError:
            print('IndexError:')
            print(sections_in_page)
            print(o)
            return page_content, language_section
        section_order = get_order_by_section_name(current_section_name)
        o += 1

    if o > 0:
        o -= 1
    if debug_level > d:
        print(
            f' while {str(section_order)} <= {str(section_to_add_order)} and {o} < {len(sections_in_page)} and {sections_in_page[o][0]} != langue'
        )

    section_limit = sections_in_page[o][0]
    # TODO pb encodage : "étymologie" non fusionnée + "catégorie" = 1 au lieu de 20
    if language_section.find('{{S|' + section_limit) == -1 and section_limit != 'langue':
        if debug_level > d:
            print(' sites_errors d\'encodage sur "' + section_limit + '"')
        if debug_level > d:
            input(language_section)
        return page_content, language_section

    section_level = get_level_by_section_name(section_name)
    section_order = get_order_by_section_name(section_limit)
    if section_limit == section_name:
        if debug_level > d:
            print(
                f' ajout dans la sous-section existante "{section_name}" (car {str(section_order)} = {str(section_to_add_order)})\n'
            )
    elif section_name not in ['catégorie', 'clé de tri']:
        section_to_add = '\n\n' + section_level + \
            ' {{S|' + section_name + '}} ' + section_level + '\n'
        if section_to_add_order >= section_order:
            if debug_level > d:
                print(
                    f' ajout de la sous-section "{section_name}" après "{section_limit}" (car {str(section_to_add_order)} > {str(section_order)})'
                )
            regex = r'{{S\|' + section_limit + r'[\|}]'
            s = re.search(regex, language_section)
            if section_limit == sections_in_page[-1][0]:
                if debug_level > d:
                    print(f' ajout de la sous-section après la dernière de la section langue : {section_limit}')
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
                        print(f' saut de {sections_in_page[o + 1][0]}')

                if debug_level > d:
                    print(f' ajout de la sous-section "{section_name}" avant "{sections_in_page[o + 1][0]}"')
                regex = r'\n=* *{{S\|' + sections_in_page[o + 1][0]
                s = re.search(regex, language_section)
                if s:
                    if section_name in natures:
                        section_to_add = section_to_add.replace('}}', f'|{language_code}' + '}}')
                        if line_content[:1] == '#' or line_content[:2] == '\n#':
                            section_to_add += "'''{{subst:PAGENAME}}''' {{genre ?|" + language_code + \
                                "}} {{pluriel ?|" + language_code + "}}\n"
                    page_content = page_content[:start_position] + language_section[:s.start()] + \
                        section_to_add + \
                        language_section[s.start():] + \
                        page_content[start_position+end_position:]
                else:
                    input(' bug section')
            language_section, start_position, end_position = get_language_section(
                page_content, language_code)
            if language_section is None:
                return page_content
        else:
            if debug_level > d:
                print(
                    f' ajout de "{section_name}" avant "{section_limit}" (car {str(section_to_add_order)} < {str(section_order)})'
                )
            regex = r'\n=* *{{S\|' + section_limit
            s = re.search(regex, language_section)
            if s:
                page_content = page_content[:start_position] + language_section[:s.start()] + section_to_add\
                    + language_section[s.start():] + \
                    page_content[start_position+end_position:]
                language_section, start_position, end_position = get_language_section(
                    page_content, language_code)
                if language_section is None:
                    return page_content
            else:
                print(f' Error, cannot add section: {section_name}')
    return page_content, language_section, start_position, end_position


def add_line_test(page_content, language_code='fr'):
    # TODO move to /tests
    page_content = add_category(
        page_content, language_code, 'Tests en français')
    page_content = add_line(page_content, language_code,
                            'prononciation', '* {{écouter|||lang=fr|audio=test.ogg}}')
    page_content = add_line(page_content, language_code,
                            'prononciation', '* {{écouter|||lang=fr|audio=test2.ogg}}')
    page_content = add_line(page_content, language_code,
                            'étymologie', ':{{étyl|test|fr}}')
    page_content = add_line(page_content, language_code,
                            'traductions', '{{trad-début}}\n123\n{{trad-fin}}')
    page_content = add_line(page_content, language_code,
                            'vocabulaire', '* [[voc]]')
    page_content = add_line(page_content, language_code, 'nom', '# Définition')
    page_content = add_line(page_content, language_code, 'nom', 'Note')
    return page_content


def add_pronunciation(page_content, language_code, section, line_content):
    if page_content == '' or language_code == '' or section == '' or line_content == '' \
            or line_content in page_content or '{{langue|' + language_code + '}}' not in page_content:
        return page_content

    # TODO generic preformatter
    page_content = page_content.replace('{{S|Références}}', '{{S|références}}')
    if section == 'catégorie' and line_content.find('[[Catégorie:') == -1:
        line_content = f'[[Catégorie:{line_content}]]'
    if section == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
        line_content = '{{clé de tri|' + line_content + '}}'

    # Recherche de l'ordre théorique de la section à ajouter
    section_number = get_order_by_section_name(section)
    if section_number == len(sections):
        if debug_level > 0:
            print(f' ajout de {section} dans une section inconnue')
            print(f'  (car {len(sections)} = {str(section_number)})')
        return page_content

    # Recherche de l'ordre réel de la section à ajouter
    old_language_section, l_start, l_end = get_language_section(
        page_content, language_code)
    if old_language_section is None:
        return page_content

    language_section = old_language_section
    # sections_in_page = re.findall("{{S\|([^}]+)}}", language_section)
    sections_in_page = re.findall(
        r"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", language_section)
    o = 0
    # TODO pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
    while o < len(sections_in_page) and sections_in_page[o][0] != 'langue' \
            and get_order_by_section_name(sections_in_page[o][0]) <= section_number:
        if debug_level > 0:
            print(f' {sections_in_page[o][0]} {str(get_order_by_section_name(sections_in_page[o][0]))}')
        o += 1
    if debug_level > 0:
        print(f' {len(sections_in_page)} >? {o}')
    if o == len(sections_in_page):
        if debug_level > 0:
            print(' section à ajouter dans le dernier paragraphe')
        # TODO if section == sections_in_page[-1][0]?
        if (
            section not in ['catégorie', 'clé de tri']
            and language_section.find('[[Catégorie:') != -1
        ):
            if debug_level > 0:
                print('  avant les catégories')
            language_section = language_section[:language_section.find('[[Catégorie:')] + \
                line_content + '\n' + \
                language_section[language_section.find('[[Catégorie:'):]
        elif (
            section not in ['catégorie', 'clé de tri']
            and language_section.find('[[Catégorie:') == -1
            and language_section.find('{{clé de tri') != -1
        ):
            if debug_level > 0:
                print('  avant la clé de tri')
            language_section = language_section[:language_section.find('{{clé de tri')] + \
                line_content + '\n' + \
                language_section[language_section.find('{{clé de tri'):]
        else:
            if debug_level > 0:
                print(' section à ajouter en fin de section langue')
            language_section = language_section + '\n' + line_content + '\n'
    else:
        try:
            section_limit = str(sections_in_page[o][0])
        except UnicodeEncodeError:
            print('UnicodeEncodeError (relancer en Python3)',
                  o, sections_in_page[o][0])
            return page_content
        o -= 1
        if debug_level > 1:
            print(f' position O : {o}')
        if debug_level > 0:
            print(f' ajout de "{section}" avant "{repr(section_limit)}"')
            print(f'  (car {str(get_order_by_section_name(section_limit))} > {str(section_number)})')

        # Ajout après la section trouvée
        if language_section.find('{{S|' + sections_in_page[o][0]) == -1:
            print('sites_errors d\'encodage')
            return page_content

        end_of_language_section = language_section[language_section.rfind(
            '{{S|' + sections_in_page[o][0]):]
        if debug_level > 1:
            input(end_of_language_section)
        if sections_in_page[o][0] != section and section not in [
            'catégorie',
            'clé de tri',
        ]:
            if debug_level > 0:
                print(f' ajout de la section "{section}" après "{sections_in_page[o][0]}"')
            line_content = '\n' + sections_level[section_number] + ' {{S|' + section + '}} ' + \
                           sections_level[section_number] + '\n' + line_content
        elif debug_level > 0:
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
                        print(e)
                        print(' pb regex interwiki')
                elif categories != -1 and (categories < default_sort or default_sort == -1):
                    if debug_level > 0:
                        print('  ajout avant les catégories')
                    language_section = language_section[:language_section.find('\n[[Catégorie:')] \
                        + line_content + \
                        language_section[language_section.find(
                            '\n[[Catégorie:'):]
                else:
                    if debug_level > 0:
                        print('  ajout avant la clé de tri')
                    language_section = language_section[:language_section.find('\n{{clé de tri|')] \
                        + line_content + \
                        language_section[language_section.find(
                            '\n{{clé de tri|'):]
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
        language_section = language_section.replace(
            '\n* {{écouter|', '\n\n=== {{S|prononciation}} ===\n* {{écouter|')

    language_section = language_section.replace('\n\n\n\n', '\n\n\n')
    page_content = page_content.replace(old_language_section, language_section)

    return page_content


def add_line_into_section(page_content, language_code, section, line_content):
    d = 1
    if debug_level > d:
        pywikibot.output(
            "\n\03<<red>>---------------------------------------------\03<<default>>")
        print('\naddLineIntoSection "' + section + '"')
    if (
        page_content != ''
        and language_code != ''
        and section != ''
        and line_content != ''
        and page_content.find(line_content) == -1
        and page_content.find('{{langue|' + language_code + '}}') != -1
    ):
        if section == 'catégorie' and line_content.find('[[Catégorie:') == -1:
            line_content = f'[[Catégorie:{line_content}]]'
        if section == 'clé de tri' and line_content.find('{{clé de tri|') == -1:
            line_content = '{{clé de tri|' + line_content + '}}'
    # TODO: complete parsing
    #sections = re.findall(r"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", page_content)
    # input(str(sections))
    return page_content


def get_order_by_section_name(section):
    if debug_level > 0:
        print('\nget_order_by_section_name()')
    s = 0
    try:
        s = sections.index(section)
        section_order = sections_order[s]
    except BaseException as e:
        print(e)
        section_order = 2  # Grammatical natures (ex: nom)
    if debug_level > 0:
        print(f'  {section} ({str(s)}e) : ordre {section_order}')
    return section_order


def get_level_by_section_name(section):
    if debug_level > 0:
        print('\nget_level_by_section_name()')
    s = 0
    try:
        s = sections.index(section)
        section_level = sections_level[s]
    except BaseException as e:
        print(e)
        section_level = '==='  # Grammatical natures (ex: === {{S|nom)
    if debug_level > 0:
        print(f'  {section} ({str(s)}e) : ordre {section_level}')
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
        pywikibot.output(f"  Template with lang=: \03<<green>>{current_template}\03<<default>>")
    page_content2 = page_content[end_position + 1:]

    has_subtemplate_included = False
    if page_content.find('}}') > page_content.find('{{') != -1:
        # TODO Infinite loop in [[tomme]] with ^date\|[^{}]*({{(.*?)}}|.)+[^{}]*\|lang=
        regex_has_subtemplate = r'^' + re.escape(current_template) +  r'\|[^{}]*({{(.*?)}}|.)+[^{}]*\| *lang(?:ue|1)? *='
        if re.search(regex_has_subtemplate, page_content):
            has_subtemplate_included = True

    if has_subtemplate_included or language_code is None:
        if debug_level > 0:
            print('   "lang=" addition ignored')
        return next_template(final_page_content, page_content)

    is_not_category_name = current_template != 'cf' or (
            page_content2.find('}}') > end_position + 1
            and (page_content2.find(':') == -1 or page_content2.find(':') > page_content2.find('}}'))
            and page_content2[:1] != '#'
    )

    regex_has_lang = r'^[^{}]+\| *lang(?:ue|1)? *='
    if is_not_category_name and not re.search(regex_has_lang, page_content):
        if debug_level > 0:
            print('   "lang=" addition')
        while page_content2.find('{{') < page_content2.find('}}') and page_content2.find('{{') != -1:
            page_content2 = page_content2[page_content2.find('}}')+2:]

        final_page_content = final_page_content + current_template + '|lang=' + language_code \
            + page_content[end_position:page_content.find('}}') + 2]
        page_content = page_content[page_content.find('}}')+2:]
        return final_page_content, page_content

    if debug_level > 0:
        print('   "lang=" already present')

    if current_template == 'cf':
        return next_template(final_page_content, page_content)

    # Correct language code with the paragraph's one
    regex_lang = r'^[^{}]+\| *lang(?:ue|1)? *= *([\w\- \'’]*)'
    p = re.compile(regex_lang)
    m = p.match(page_content)
    if m is None:
        if debug_level > 0:
            print('  weird case')
        return next_template(final_page_content, page_content)

    start = end = 0
    old_language_code = ''
    if m.span(1) is not None:
        [start, end] = m.span(1)
        old_language_code = page_content[start:end]
    if debug_level > 0:
        print('   "lang=" ' + old_language_code)

    if language_code == old_language_code:
        return next_template(final_page_content, page_content)

    if debug_level > 0:
        print('   "lang=" correction to ' + language_code)
    page_content = page_content[:start] + language_code + page_content[end:]

    return next_template(final_page_content, page_content)


def next_template(final_page_content, current_page_content, current_template=None, language_code=None):
    if language_code is None:
        final_page_content = final_page_content + \
            current_page_content[:current_page_content.find('}}')+2]
    else:
        final_page_content = final_page_content + \
            current_template + '|' + language_code + '}}'
    current_page_content = current_page_content[current_page_content.find(
        '}}')+2:]
    return final_page_content, current_page_content


def next_translation_template(final_page_content, current_page_content, result='-'):
    final_page_content = final_page_content + current_page_content[:len('trad')] + result
    current_page_content = current_page_content[current_page_content.find('|'):]
    return final_page_content, current_page_content


def check_false_homophons(final_page_content, summary, page_name, infinitive, singular_page_name):
    language = 'fr'  # TODO: intl
    if final_page_content.find('{{langue|' + language + '}}') != -1:
        if debug_level > 0:
            print(' Fix false homophons (lemma and its inflexion)')
        # TODO: {{S}} forced locutions parameter

        flexion_page_name = ''
        lemma_template_suffix = f'|{language}' + '}}'
        flexion_template_suffix = f'|{language}' + '|flexion}}'
        if flexion_template_suffix in final_page_content and lemma_template_suffix not in final_page_content:
            # Recherche d'éventuelles flexions dans la page du lemme
            inflexion_template = get_inflexion_template(page_name, language)
            if inflexion_template.find('inv=') == -1 and \
                    (inflexion_template[:inflexion_template.find('|')] in inflexion_templates_fr_with_s
                     or inflexion_template[:inflexion_template.find('|')] in inflexion_templates_fr_with_ms):
                flexion_page_name = get_parameter_value(
                    inflexion_template, 'p')
                if flexion_page_name == '':
                    flexion_page_name = f'{page_name}s'

            if infinitive is not None and infinitive != '':
                final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                     infinitive, summary)
            if singular_page_name is not None and singular_page_name != '':
                final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                     singular_page_name, summary)
            if flexion_page_name is not None and flexion_page_name != '':
                final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                     flexion_page_name, summary)
            ms_page_name = get_lemma_from_feminine(
                final_page_content, language, ['adjectif'])
            if ms_page_name is not None and ms_page_name != '':
                final_page_content, summary = remove_false_homophons(final_page_content, language, page_name,
                                                                     ms_page_name, summary)
        if debug_level > 2:
            input(final_page_content)

    return final_page_content, summary


def remove_false_homophons(page_content, language_code, page_name, related_page_name, summary):
    if debug_level > 1:
        print('\nremove_false_homophons(' + related_page_name + ')')

    for _ in range(2):
        regex = r"==== *{{S\|homophones\|" + language_code + r"}} *====\n\* *'''" + re.escape(page_name) + \
            r"''' *{{cf\|[^\|]*\|?" + \
                re.escape(related_page_name) + r"[\|}][^\n]*\n"
        if re.search(regex, page_content):
            page_content = re.sub(regex, "==== {{S|homophones|" + language_code + r"}} ====\n", page_content)
            summary = f'{summary}, homophone erroné'

        regex = r"==== *{{S\|homophones\|" + language_code + r"}} *====\n\* *\[\[[^}\n]+{{cf\|[^\|]*\|?" \
                + re.escape(related_page_name) + r"[\|}][^\n]*\n?"
        if re.search(regex, page_content):
            page_content = re.sub(regex, "==== {{S|homophones|" + language_code + r"}} ====\n", page_content)
            summary = f'{summary}, homophone erroné'

        regex = r"==== *{{S\|homophones\|" + language_code + r"}} *====\n\* *\[\[" + re.escape(related_page_name) \
                + r"\]\](\n|$)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, "==== {{S|homophones|" + language_code + r"}} ====\n", page_content)
            summary = f'{summary}, homophone erroné'

        regex = r"=== {{S\|prononciation}} ===\n==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)

        regex = r"==== *{{S\|homophones\|[^}]*}} *====\n*(=|$|{{clé de tri|\[\[Catégorie:)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)

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
    if debug_level > 0:
        print(' sort_translations()')
    if debug_level > 1:
        print(' First translation detection')

    regex = r'\* ?{{[a-z][a-z][a-z]?-?[a-z]?[a-z]?[a-z]?}} :'
    final_page_content = ''
    while page_content.find('{{trad-début') != -1:
        final_page_content = final_page_content + \
            page_content[:page_content.find('{{trad-début')]
        page_content = page_content[page_content.find('{{trad-début'):]
        final_page_content = final_page_content + \
            page_content[:page_content.find('\n')+1]
        page_content = page_content[page_content.find('\n')+1:]
        if re.search(regex, page_content) and re.search(regex, page_content).start() < page_content.find('{{'):
            if debug_level > 0:
                print(' {{T}} addition')
            page_content = page_content[:page_content.find(
                '{{')+2] + 'T|' + page_content[page_content.find('{{')+2:]
    page_content = final_page_content + page_content
    final_page_content = ''

    summary2 = ''
    while page_content.find('{{T|') != -1:
        final_page_content = final_page_content + \
            page_content[:page_content.find('{{T|')]
        page_content = page_content[page_content.find('{{T|'):]
        if debug_level > 2:
            print(' Ajout des T')
        page_content2 = page_content[page_content.find('\n'):]
        if re.search(regex, page_content2) and re.search(
            regex, page_content2
        ).start() < page_content2.find('{{'):
            if debug_level > 0:
                print('Ajout d\'un modèle T')
            page_content = page_content[:page_content.find('\n') + page_content2.find('{{')+2] + 'T|' + \
                page_content[page_content.find(
                    '\n') + page_content2.find('{{')+2:]

        language = get_next_translation(page_content)
        if language != '' and (final_page_content.find('<!--') == -1 or final_page_content.find('-->') != -1):
            language2 = 'zzz'
            if final_page_content.rfind('\n') == -1 or page_content.find('\n') == -1:
                break
            current_translation = final_page_content[final_page_content.rfind('\n'):] \
                + page_content[:page_content.find('\n')]
            next_translations = ''
            final_page_content = final_page_content[:final_page_content.rfind(
                '\n')]
            page_content = page_content[page_content.find('\n'):]

            d = 0
            if debug_level > d:
                print(f' 1 {language2} > {language} ?')
            while compare(language2, language) \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{S|') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{trad-début') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{trad-fin') \
                    and final_page_content.rfind('{{') != final_page_content.rfind('{{(') \
                    and final_page_content.rfind('{{T') != final_page_content.rfind('{{T|conv'):
                if debug_level > d:
                    print(f' 1 {language2} > {language}')

                language2 = get_next_language_translation(final_page_content)
                if debug_level > d:
                    print(f' 2 {language2} > {language} ?')
                if language2 == '' or not compare(language2, language):
                    break
                if debug_level > d:
                    print(f' 2 {language2} > {language}')
                if final_page_content.rfind('\n') > final_page_content.rfind('trad-début'):
                    next_translations = final_page_content[final_page_content.rfind(
                        '\n'):] + next_translations
                    final_page_content = final_page_content[:final_page_content.rfind(
                        '\n')]
                    summary2 += f', {language2} > {language}'
                elif final_page_content.rfind('\n') != -1:
                    # Cas de la première de la liste
                    current_translation = final_page_content[final_page_content.rfind(
                        '\n'):] + current_translation
                    final_page_content = final_page_content[:final_page_content.rfind(
                        '\n')]
            final_page_content = final_page_content + \
                current_translation + next_translations
        elif page_content.find('\n') != -1:
            if debug_level > 0:
                print(' Retrait de commentaire de traduction : ' +
                      page_content[:page_content.find('\n')+1])
            final_page_content = final_page_content + \
                page_content[:page_content.find('\n')]
            page_content = page_content[page_content.find('\n'):]
        else:
            final_page_content = final_page_content + page_content
            page_content = ''

        final_page_content = final_page_content + \
            page_content[:page_content.find('\n')+1]
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
        summary += f', traductions :{summary2[1:]}'
    return page_content, summary


def get_next_translation(page_content):
    language = page_content[page_content.find('{{T|')+4:page_content.find('}')]

    return get_langage_name_by_code(language)


def get_next_language_translation(final_page_content):
    language = final_page_content[final_page_content.rfind(
        '{{T|')+len('{{T|'):]
    language = language[:language.find('}}')]
    return get_langage_name_by_code(language)


def get_langage_name_by_code(language_code):
    language_name = ''
    if language_code.find('|') != -1:
        language_code = language_code[:language_code.find('|')]
    if language_code != '':
        if len(language_code) > 3 and language_code.find('-') == -1:
            if debug_level > 0:
                print(f' No ISO code for {language_code}')
            language_name = language_code
        else:
            try:
                # Works in Python 2 without future:
                # language_name = sort_by_encoding(languages[language_code].decode('utf8'), 'UTF-8')
                # "éa" > "ez":
                # language_name = sort_by_encoding(languages[language_code])
                language_name = sort_by_encoding(
                    languages[language_code], 'UTF-8')
                if debug_level > 1:
                    print(f' Language name: {language_name}')
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

    default_sort = sort_by_encoding(page_name)

    if page_content.find('{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{lc:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].lower() + page_name[1:] + \
            page_content[page_content.find(
                '{{voir|{{lc:{{PAGENAME}}}}}}')+len('{{voir|{{lc:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{lc:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].upper() + page_name[1:] + \
            page_content[page_content.find(
                '{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len('{{voir|{{ucfirst:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{ucfirst:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{LC:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].lower() + page_name[1:] + \
            page_content[page_content.find(
                '{{voir|{{LC:{{PAGENAME}}}}}}')+len('{{voir|{{LC:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{LC:{{PAGENAME}}}}'
    if page_content.find('{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
        page_content = page_content[:page_content.find('{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len('{{voir|')] + \
            page_name[:1].upper() + page_name[1:] + \
            page_content[page_content.find(
                '{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len('{{voir|{{UCFIRST:{{PAGENAME}}}}'):]
        summary = summary + ', subst de {{UCFIRST:{{PAGENAME}}}}'

    if '{{voir|' not in page_content and '{{voir/' not in page_content:
        # TODO: always empty
        PageVoir = ''
        # Liste de toutes les pages potentiellement "à voir"
        pages_keys = page_name
        if pages_keys.find(page_name.lower()) == -1:
            pages_keys = f'{pages_keys}|{page_name.lower()}'
        if pages_keys.find(page_name.upper()) == -1:
            pages_keys = f'{pages_keys}|{page_name.upper()}'
        if pages_keys.find(page_name[:1].lower() + page_name[1:]) == -1:
            pages_keys = f'{pages_keys}|{page_name[:1].lower()}{page_name[1:]}'
        if pages_keys.find(page_name[:1].upper() + page_name[1:]) == -1:
            pages_keys = f'{pages_keys}|{page_name[:1].upper()}{page_name[1:]}'
        if pages_keys.find(f'-{page_name[:1].lower()}{page_name[1:]}') == -1:
            pages_keys = f'{pages_keys}|-{page_name[:1].lower()}{page_name[1:]}'
        if pages_keys.find(page_name[:1].lower() + page_name[1:] + '-') == -1:
            pages_keys = f'{pages_keys}|{page_name[:1].lower()}{page_name[1:]}-'
        if pages_keys.find('-') != -1:
            pages_keys = f'{pages_keys}|' + pages_keys.replace('-', '')

        if debug_level > 0:
            print('  page keys: ' + pages_keys)

        # TODO fix https://fr.wiktionary.org/w/index.php?title=n%C3%BC%C3%BCd&diff=prev&oldid=34336497
        # where remaining_pages_keys contains several keys looking like memory leaks
        # diacritics = [
        #     ['a', 'á', 'à', 'ä', 'â', 'ã'],
        #     ['c', 'ç'],
        #     ['e', 'é', 'è', 'ë', 'ê'],
        #     ['i', 'í', 'ì', 'ï', 'î'],
        #     ['n', 'ñ'],
        #     ['o', 'ó', 'ò', 'ö', 'ô', 'õ'],
        #     ['', 'ú', 'ù', 'ü', 'û']
        # ]
        #
        # for diacritic in diacritics:
        #     for d in range(len(diacritic)):
        #         if page_name.find(diacritic[d]) != -1:
        #             if debug_level > 1:
        #                 print(f'Title containing: {diacritic[d]}')
        #             letter = diacritic[d]
        #             for diac in range(len(diacritic)):
        #                 pages_keys = f'{pages_keys}|{page_name.replace(letter, diacritic[diac])}'

        if pages_keys.find(default_sort) == -1:
            pages_keys = f'{pages_keys}|{default_sort}'

        # Filtre des pages de la liste "à voir"
        remaining_pages_keys = f'{pages_keys}|'
        pages_keys = ''
        PagesVoir = ''
        if debug_level > 0:
            print('  search existing pages...')

        while remaining_pages_keys != '':
            if debug_level > 0:
                print('  remaining keys: ' + remaining_pages_keys)

            current_page = remaining_pages_keys[:remaining_pages_keys.find('|')]
            remaining_pages_keys = remaining_pages_keys[remaining_pages_keys.find('|')+1:]
            # TODO escape ":"
            if current_page == '' or ':' in current_page:
                continue

            key_page = Page(site, current_page)
            key_page_content = get_content_from_page(key_page)
            if key_page_content is not None:
                if debug_level > 1:
                    print(pages_keys)

                if pages_keys.find(f'|{current_page}') == -1:
                    pages_keys = f'{pages_keys}|{current_page}'
                if key_page_content.find('{{voir|') != -1:
                    page_content_key2 = key_page_content[key_page_content.find('{{voir|')+len('{{voir|'):]
                    PagesVoir = (
                        f'{PagesVoir}|'
                        + page_content_key2[: page_content_key2.find('}}')]
                    )
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
                            page_contentMod = (
                                page_contentMod[: page_contentMod.find('}}')]
                                + '|'
                                + page_name
                                + page_contentMod[page_contentMod.find('}}') :]
                            )
                        if page_contentMod.find(PageVoir) == -1:
                            page_contentMod = (
                                page_contentMod[: page_contentMod.find('}}')]
                                + '|'
                                + PageVoir
                                + page_contentMod[page_contentMod.find('}}') :]
                            )
                    if debug_level > 0:
                        print('remaining_pages_keys vide')
                    elif page_contentMod != page_contentModBegin:
                        save_page(pageMod, page_contentMod, summary)
                    remaining_pages_keys = ''
                    break

        if PagesVoir != '':
            if debug_level > 0:
                print(' Filtre des doublons...')
            if debug_level > 1:
                print(f'  avant : {PagesVoir}')
            PagesVoir = f'{PagesVoir}|'
            while PagesVoir.find('|') != -1:
                if pages_keys.find(PagesVoir[:PagesVoir.find('|')]) == -1:
                    pages_keys = (f'{pages_keys}|' + PagesVoir[:PagesVoir.find('|')])
                PagesVoir = PagesVoir[PagesVoir.find('|')+1:]
            if debug_level > 1:
                print(f'  après : {pages_keys}')

        if debug_level > 2:
            input(pages_keys)

        if debug_level > 0:
            print(' Balayage de toutes les pages "à voir"...')
        if pages_keys != '':
            while pages_keys[:1] == '|':
                pages_keys = pages_keys[1:]

        if pages_keys != page_name:
            if debug_level > 0:
                print('  ' + pages_keys + ' is different from ' + page_name)
            remaining_pages_keys = f'{pages_keys}|'
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
                        if pages_keys.find(f'|{current_page}') != -1:
                            page_content_key2 = key_page_content[key_page_content.find(
                                '{{voir|')+len('{{voir|'):]
                            key_page_content = key_page_content[:key_page_content.find('{{voir|')+len('{{voir|')] \
                                + pages_keys[:pages_keys.find('|' + current_page)] \
                                + pages_keys[pages_keys.find('|' + current_page)+len('|' + current_page):] \
                                + key_page_content[key_page_content.find('{{voir|')+len('{{voir|')
                                                   + page_content_key2.find('}}'):]
                        else:  # Cas du premier
                            page_content_key2 = key_page_content[key_page_content.find(
                                '{{voir|')+len('{{voir'):]
                            key_page_content = key_page_content[:key_page_content.find('{{voir|')+len('{{voir|')] \
                                + pages_keys[len(current_page):] \
                                + key_page_content[key_page_content.find('{{voir|')+len('{{voir')
                                                   + page_content_key2.find('}}'):]
                        if key_page_content != page_content_key_start:
                            if current_page == page_name:
                                page_content = key_page_content
                            else:
                                if debug_level > 0:
                                    print(
                                        ' Première savePage dédiée à {{voir}}')
                                else:
                                    save_page(
                                        key_page, key_page_content, summary)
                    else:
                        if pages_keys.find('|' + current_page) != -1:
                            key_page_content = '{{voir|' + pages_keys[:pages_keys.find('|' + current_page)] \
                                + pages_keys[pages_keys.find('|' + current_page)+len('|' + current_page):] + '}}\n' \
                                + key_page_content
                        else:    # Cas du premier
                            key_page_content = (
                                '{{voir'
                                + pages_keys[len(current_page) :]
                                + '}}\n'
                                + key_page_content
                            )
                        if current_page == page_name:
                            page_content = key_page_content
                        else:
                            if debug_level > 0:
                                print(' Deuxième savePage dédiée à {{voir}}')
                            else:
                                save_page(key_page, key_page_content, summary)

    elif '{{voir|' in page_content:
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
        print('\nformat_sections()')

    # Format old language section
    regex = r'{{=([a-z\-]+)=}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{langue|\1}}', page_content)

    # Normalize sections title casing
    for f in re.findall(r'{{S\|([^}]+)}}', page_content):
        page_content = page_content.replace(f, f.lower())

    # Replace deprecated aliases with language parameter
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

    # Replace deprecated aliases without language parameter
    page_content = re.sub(r'{{S\| ?abr[éèe]v(iations)?\|?[a-z\- ]*}}', '{{S|abréviations}}', page_content)
    page_content = re.sub(r'{{S\| ?anagr(ammes)?\|?[a-z\- ]*}}', '{{S|anagrammes}}', page_content)
    page_content = re.sub(r'{{S\| ?anciennes orthographes?\|?[a-z\- ]*}}', '{{S|anciennes orthographes}}', page_content)
    page_content = re.sub(r'{{S\| ?ant(onymes)?\|?[a-z\- ]*}}', '{{S|antonymes}}', page_content)
    page_content = re.sub(r'{{S\| ?app(arentés)?\|?[a-zé]*}}', '{{S|apparentés}}', page_content)
    page_content = re.sub(r'{{S\| ?ap(p|r)\|?[a-zé]*}}', '{{S|apparentés}}', page_content)
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

    page_content = page_content.replace('{{msing}}', '{{m}} {{s}}')
    page_content = page_content.replace('{{fsing}}', '{{f}} {{s}}')
    page_content = page_content.replace('{{nsing}}', '{{n}} {{s}}')
    page_content = page_content.replace('{{mplur}}', '{{m}} {{p}}')
    page_content = page_content.replace('{{fplur}}', '{{f}} {{p}}')
    page_content = page_content.replace('{{nplur}}', '{{n}} {{p}}')

    regex = r'({{trad\-fin}}[^={]+)(\n==== {{S\|homophones)'
    s = re.search(regex, page_content)
    if s:
        page_content = page_content.replace(s[1] + s[2], s[1] + '\n=== {{S|prononciation}} ===' + s[2])

    regex = r"\n=* *({{langue\|[^}]+}}) *=*\n"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\n== \1 ==\n", page_content)

    # Replace old sort key
    regex = r'({{S\|[^}]+)€'
    while re.search(regex, page_content):
        page_content = re.sub(regex, r'\1⿕', page_content)

    return page_content, summary


def format_translations(page_content, summary):
    if debug_level > 0:
        print('\nformat_translations()')
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
    page_content = page_content.replace(
        '{{trad-début|{{trad-trier}}}}', '{{trad-trier}}\n{{trad-début}}')
    page_content = page_content.replace(
        '{{trad-début|{{trad-trier|fr}}}}', '{{trad-trier}}\n{{trad-début}}')

        # Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
    page_content = page_content.replace(
        r'<!--* {{T|en}} : {{trad|en|}}-->', '')     # bug ?
    regex = r'<!\-\-[^{>]*{{T\|[^>]+>\n?'
    if re.search(regex, page_content):
        if debug_level > 0:
            print(' Commentaire trouvé l 1517')
        page_content = re.sub(regex, '', page_content)

    while page_content.find('{{trad-fin}}\n* {{T|') != -1:
        page_content2 = page_content[page_content.find(
            '{{trad-fin}}\n* {{T|'):]
        delta = page_content2.find('\n')+1
        page_content2 = page_content2[delta:]
        if page_content2.find('\n') != -1:
            if debug_level > 0:
                print(page_content2[:page_content2.find('\n')+1])
            if page_content2[:page_content2.find('\n')+1].find('trier') != -1:
                break
            page_content = page_content[:page_content.find('{{trad-fin}}\n* {{T|'):] + \
                page_content2[:page_content2.find('\n')+1] + '{{trad-fin}}\n' + \
                page_content[page_content.find(
                    '{{trad-fin}}\n* {{T|')+delta+page_content2.find('\n')+1:]
        else:
            if debug_level > 0:
                print(page_content2)
            if page_content2[:].find('trier') != -1:
                break
            page_content = (
                (
                    page_content[: page_content.find('{{trad-fin}}\n* {{T|') :]
                    + page_content2[:]
                )
                + '{{trad-fin}}\n'
            ) + page_content[
                page_content.find('{{trad-fin}}\n* {{T|')
                + delta
                + len(page_content2) :
            ]
    regex = r'}}{{trad\-fin}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, '}}\n{{trad-fin}}', page_content)

    while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(page_content):
        i1 = re.search(r'{{T\|.*\n\n\*[ ]*{{T\|', page_content).end()
        page_content = (
            page_content[:i1][: page_content[:i1].rfind('\n') - 1]
            + page_content[:i1][page_content[:i1].rfind('\n') :]
        ) + page_content[i1:]

    if debug_level > 1:
        print('  Modèles à déplacer')
    regex = r'(==== {{S\|traductions}} ====)(\n{{ébauche\-trad[^}]*}})(\n{{trad-début}})'
    page_content = re.sub(regex, r'\1\3\2', page_content)

    regex = r'({{trad\-début}})\n*{{trad\-début}}'
    page_content = re.sub(regex, r'\1', page_content)

    regex = r'({{trad\-fin}})\n*{{trad\-fin}}'
    page_content = re.sub(regex, r'\1', page_content)

    regex = r'{{trad-\|hr\|(\([0-9]\))\|dif=([^}\|]+)}}'
    page_content = re.sub(regex, r'{{trad-|hr|\2}} \1', page_content)

    regex = r"(==== {{S\|dérivés autres langues}} ====" + \
        r"(:?\n\* *{{L\|[^\n]+)?"*10 + r"\n\* *{{)T\|"
    for _ in range(10):
        page_content = re.sub(regex, r'\1L|', page_content)

    return page_content, summary


def add_templates(page_content, summary):
    if debug_level > 0:
        print('\nadd_templates()')

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
            page_content, summary = remove_category(
                page_content, 'Adverbes de temps en français', summary)

    if debug_level > 1:
        print('  add definition templates')

    regex = r'\n#\* *(?:\'\')?\n'
    page_content = re.sub(regex, r'\n#* {{exemple}}\n', page_content)

    regex = r"(\|en}}\n# *'*(?:Participe présent|Participe passé|Prétérit|Troisième personne du singulier du présent) de *'* *)to "
    page_content = re.sub(regex, r'\1', page_content, re.IGNORECASE)
    regex = r"(\|([a-z]+)}}\n# *'*(?:Participe présent|Participe passé|Prétérit|Troisième personne du singulier du présent) de *'* *)([a-zçæéë \-’']+)\."
    page_content = re.sub(regex, r'\1{{l|\3|\2}}.', page_content, re.IGNORECASE)

    if debug_level > 1:
        print('  add translation templates')
    regex = r'\n\* *[Ss]olr[eé]sol *: *:* *\[\[«?([^\]\n«»]+)»?\]\]'
    page_content = re.sub(regex, r'\n* {{T|solrésol}} : {{trad|solrésol|\1}}', page_content)
    regex = r'(\n\* {{T\|tsolyáni}} *: *)\[\[([^\]\n]+)\]\]'
    page_content = re.sub(regex, r'\1{{trad|tsolyáni|\2}}', page_content)

    return page_content, summary


def replace_template(page_content, old_template, new_template):
    regex = r"({{) *" + old_template + r" *([|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1" + new_template + r"\2", page_content)

    return page_content


def replace_templates(page_content, summary):
    if debug_level > 1:
        print('  replace_templates()')

    for old_template in old_templates:
        page_content = replace_template(page_content, old_template, old_templates[old_template])

    page_content, summary = replace_etymology_templates(page_content, summary)
    page_content, summary = replace_languages_templates(page_content, summary)
    page_content, summary = replace_doubles_templates(page_content, summary)
    page_content, summary = replace_banner_templates(page_content, summary)

    t = '{{ucf|'
    while t in page_content:
        page_end = page_content[page_content.find(t) + len(t):]
        word = page_end[:page_end.find('}}')]
        if '|' in word:
            break
        page_content = (
            f'{page_content[:page_content.find(t)]}[[{word}|{word[:1].upper()}{word[1:]}]]'
            + page_end[page_end.find('}}') + 2:]
        )

    page_content = page_content.replace('{{liaison}}', '‿')

    regex = r'\* ?{{sound}} ?: \[\[Media:([^\|\]]*)\|[^\|\]]*\]\]'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{écouter|audio=\1}}', page_content)
        summary = f'{summary}, conversion de modèle de son'
    regex = r'\{{audio\|([^\|}]*)\|[^\|}]*}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{écouter|audio=\1}}', page_content)
        summary = f'{summary}, conversion de modèle de son'

    # TODO: replace {{fr-rég|ɔs vɛʁ.tɛ.bʁal|s=os vertébral|p=os vertébraux|pp=ɔs vɛʁ.tɛ.bʁo}} by {{fr-accord-mf-al|

    if debug_level > 1:
        print(' Template replacement fixes')
    regex = r'\n{{\(}}nombre= *[0-9]*\|\n'
    page_content = re.sub(regex, r'\n{{(}}\n', page_content)
    regex = r'\n{{\(}}taille= *[0-9]*\|\n'
    page_content = re.sub(regex, r'\n{{(}}\n', page_content)

    regex = r'({{composé de)\|m=1(([^}]+)\|m=1}})'
    page_content = re.sub(regex, r'\1\2', page_content)

    return page_content, summary


def replace_etymology_templates(page_content, summary):
    if debug_level > 1:
        print('  replace_etymology_templates()')

    regex = r"(\n:? *(?:{{date[^}]*}})? *(?:\[\[calque\|)?[Cc]alque\]* d(?:u |e l['’]){{)étyl\|"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1calque|", page_content)

    # TODO
    # decision = ', [[Wiktionnaire:Prise de décision/Nettoyer les modèles de la section étymologie]]'
    # initial_page_content = page_content

    # Alias replacing with: |m=1
    regex = r"({{)deet([|}])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1composé de|m=1\2", page_content)

    regex = r'[Ll]ocution {{composé de[^{}]+}}'
    page_templates = re.findall(regex, page_content)
    regex2 = r'\| *f *= *(1|oui)[\|}]'
    for template in page_templates:
        if not re.search(regex2, template):
            new_template = template.replace('composé de', 'composé de|f=1')
            page_content = page_content.replace(template, new_template)

    page_content = page_content.replace('Du {{étyl|en|', 'De l’{{étyl|en|')
    page_content = page_content.replace('Du {{étyl|es|', 'De l’{{étyl|es|')
    page_content = page_content.replace('Du {{étyl|de|', 'De l’{{étyl|de|')
    page_content = page_content.replace('Du {{étyl|ar|', 'De l’{{étyl|ar|')

    page_content = page_content.replace('du {{étyl|en|', 'de l’{{étyl|en|')
    page_content = page_content.replace('du {{étyl|es|', 'de l’{{étyl|es|')
    page_content = page_content.replace('du {{étyl|de|', 'de l’{{étyl|de|')
    page_content = page_content.replace('du {{étyl|ar|', 'de l’{{étyl|ar|')

    return page_content, summary


def replace_languages_templates(page_content, summary):
    if debug_level > 1:
        print(' replace_languages_templates()')
    page_content = page_content.replace('|ko-hani}}', '|ko-Hani}}')
    page_content = page_content.replace('|lang=API}}', '|lang=conv}}')
    page_content = page_content.replace('|lang=gr}}', '|lang=grc}}')
    page_content = page_content.replace('|lang=gr|', '|lang=grc|')

    for old_language_template in old_language_templates:
        # TODO select templates https://fr.wiktionary.org/w/index.php?title=van&diff=prev&oldid=24107783&diffmode=source
        # regex = r'((?!:voir).*[\|{=])' + old_template[p] + r'([\|}])'
        regex = r'({{T\|)' + re.escape(old_language_template) + r'}}'
        page_content = re.sub(regex, r'\1' + old_language_templates[old_language_template] + r'}}', page_content)
        regex = r'({{trad[\-\+]\-?\|)' + \
            re.escape(old_language_template) + r'\|'
        page_content = re.sub(regex, r'\1' + old_language_templates[old_language_template] + r'|', page_content)

    return page_content, summary


def replace_doubles_templates(page_content, summary):
    if debug_level > 1:
        print(' replace_doubles_templates()')

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

    imported_sites = ['DAF8', 'Littré']
    for importedSite in imported_sites:
        regex = r'\n\** *{{R:' + importedSite + \
            r'}} *\n\** *({{Import:' + importedSite + r'}})'
        if re.search(regex, page_content):
            summary = summary + ', doublon {{R:' + importedSite + r'}}'
            page_content = re.sub(regex, r'\n* \1', page_content)
        regex = r'\n\** *({{Import:' + importedSite + \
            r'}}) *\n\** *{{R:' + importedSite + r'}}'
        if re.search(regex, page_content):
            summary = summary + ', doublon {{R:' + importedSite + r'}}'
            page_content = re.sub(regex, r'\n* \1', page_content)

    return page_content, summary


def replace_banner_templates(page_content, summary):
    if debug_level > 1:
        print(' replace_banner_templates()')
    while page_content.find('\n{{colonnes|') != -1:
        if debug_level > 0:
            pywikibot.output('\n \03<<green>>colonnes\03<<default>>')
        page_content2 = page_content[:page_content.find('\n{{colonnes|')]
        if page_content2.rfind('{{') != -1 and page_content2.rfind('{{') == page_content2.rfind('{{trad-début'):
            # modèles impriqués dans trad
            page_content2 = page_content[page_content.find(
                '\n{{colonnes|') + len('\n{{colonnes|'):]
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
            # modèles imbriqués ailleurs
            if debug_level > 0:
                pywikibot.output('\nTemplate: \03<<blue>>(\03<<default>>')
            page_content2 = page_content[page_content.find(
                '\n{{colonnes|') + len('\n{{colonnes|'):]
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

        elif page_content2.rfind('{{') != -1 and page_content2.rfind('{{') in [
            page_content2.rfind('{{trad-fin'),
            page_content2.rfind('{{S|trad'),
        ]:
            # modèle à utiliser dans {{S|trad
            page_content2 = page_content[page_content.find(
                '\n{{colonnes|') + len('\n{{colonnes|'):]
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
            page_content2 = page_content[page_content.find(
                '\n{{colonnes|') + len('\n{{colonnes|'):]
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

    return page_content, summary


def move_templates(page_content, summary):
    if debug_level > 1:
        print('\nmove_templates()')

    page_content, summary = move_etymology_templates(page_content, summary)
    return page_content, summary


def remove_double_category_when_template(page_content, summary):
    if debug_level > 1:
        print(' Retrait des catégories contenues dans les modèles')

    if '{{info|conv}}' in page_content and '[[Catégorie:Noms de domaine internet]]' in page_content:
        page_content = page_content.replace(
            '[[Catégorie:Noms de domaine internet]]', '')
        page_content = page_content.replace(
            '{{info|conv}}', '{{noms de domaine}}')
    if '{{informatique|conv}}' in page_content and '[[Catégorie:Noms de domaine internet]]' in page_content:
        page_content = page_content.replace(
            '[[Catégorie:Noms de domaine internet]]', '')
        page_content = page_content.replace(
            '{{informatique|conv}}', '{{noms de domaine}}')

    if page_content.find('\n[[Catégorie:Noms scientifiques]]') != -1 and page_content.find('{{S|nom scientifique|conv}}') != -1:
        page_content = page_content.replace(
            '\n[[Catégorie:Noms scientifiques]]', '')

    if page_content.find('[[Catégorie:Villes') != -1 and page_content.find('{{localités|') != -1:
        summary = summary + ', {{villes}} -> {{localités}}'
        page_content = re.sub(r'\n\[\[Catégorie:Villes[^\]]*\]\]', r'', page_content)

    # TODO foreach language: foreach useless category because categorizing template
    if '{{argot|fr}}' in page_content:
        page_content = re.sub(r'\n\[\[Catégorie:Argot en français\]\]', r'', page_content)
    if '\n[[Catégorie:Gentilés en français]]' in page_content and '{{note-gentilé|fr}}' in page_content:
        page_content = page_content.replace('\n[[Catégorie:Gentilés en français]]', '')

    return page_content, summary


def format_titles(page_content, summary):
    page_content = page_content.replace('{{S|nom scientifique|fr}}', '{{S|nom|fr}}')

    page_content = page_content.replace('{{S|etymologie}}', '{{S|étymologie}}')
    page_content = page_content.replace('{{S|variante orthographiques}}', '{{S|variantes orthographiques}}')
    page_content = page_content.replace('{{S|variante dialectales}}', '{{S|variantes dialectales}}')

    for section in sections:
        if section[-1:] == 's':
            page_content = page_content.replace('{{S|' + section[:-1] + '}}', '{{S|' + section + '}}')

    return page_content, summary


def format_templates(page_content, summary):
    page_content = page_content.replace('}} \n', '}}\n')
    page_content = page_content.replace('\n {{', '\n{{')
    page_content = page_content.replace('|lang=}}', '}}')
    page_content = page_content.replace('|}}', '}}')

    if debug_level > 1:
        print(' Formatage de la ligne de forme')
    page_content = page_content.replace('{{PAGENAME}}', '{{subst:PAGENAME}}')
    page_content = page_content.replace('-rég}}\'\'\'', '-rég}}\n\'\'\'')
    page_content = page_content.replace(
        ']] {{imperf}}', ']] {{imperf|nocat=1}}')
    page_content = page_content.replace(']] {{perf}}', ']] {{perf|nocat=1}}')
    page_content = page_content.replace(
        '{{perf}} / \'\'\'', '{{perf|nocat=1}} / \'\'\'')

    page_content = page_content.replace('|nocat=}}', '|nocat}}')
    page_content = page_content.replace('|pinv=. ', '|pinv=.')
    page_content = page_content.replace('|pinv=. ', '|pinv=.')

    if page_content.find('{{vérifier création automatique}}') != -1:
        if debug_level > 0:
            print(' {{vérifier création automatique}} trouvé')
        page_content2 = page_content
        language_value = '|'
        while page_content2.find('{{langue|') > 0:
            page_content2 = page_content2[page_content2.find(
                '{{langue|')+len('{{langue|'):]
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
    page_content = page_content.replace(
        '{{Source-wikt|nan|', '{{Source-wikt|zh-min-nan|')
    page_content = page_content.replace('— {{source|', '{{source|')
    page_content = page_content.replace('- {{source|', '{{source|')
    regex = r"(\{\{source\|[^}]+ )p\. *([0-9])"
    if re.search(regex, page_content):
        page_content = re.sub(regex, r"\1page \2", page_content)
    page_content = page_content.replace('myt=scandinave', 'myt=nordique')

    if debug_level > 1:
        print(' Modèles de prononciation')
    page_content = page_content.replace('{{pron|}}', '{{pron}}')
    page_content = page_content.replace(
        '{{prononciation|}}', '{{prononciation}}')
    page_content = re.sub(r'({{pron\|[^|}]*)\|(}})', r"\1\2", page_content)
    page_content = re.sub(r'({{pron\|[^|}]*\|)\|([a-z\-]+}})', r"\1\2", page_content)
    page_content = re.sub(r'({{pron\|[^|}]*\|)\|nocat(?:=1)?(}})', r"\1\2", page_content)
    page_content = re.sub(r'}}\* *{{écouter\|',
                          r"}}\n* {{écouter|", page_content)

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
    if debug_level > 0:
        print(' Templates by language')
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
                page_content = add_category(
                    page_content, 'fr', 'qu prononcés /kw/ en français')
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

        page_content = page_content.replace(
            '{{louchébem|fr}}', '{{louchébem}}')
        page_content = page_content.replace(
            '{{reverlanisation|fr}}', '{{reverlanisation}}')
        page_content = page_content.replace('{{verlan|fr}}', '{{verlan}}')

        # Ajout des redirections des pronominaux
        if page_content.find('{{S|verbe|fr}}') != -1 and page_name[:3] != 'se' and page_name[:2] != 's’':
            page_content2 = page_content[page_content.find('{{S|verbe|fr}}'):]
            regex = r'(\n|\')s(e |’)\'\'\''
            if re.search(regex, page_content2) is not None and (
                re.search(regex, page_content2).start()
                < page_content2.find('{{S|')
                or page_content2.find('{{S|') == -1
            ):
                regex = r'^[aeiouyàéèêôù]'
                    # not [:1] car = & si encodage ASCII du paramètre DOS / Unix
                if re.search(regex, page_name):
                    page_name2 = f's’{page_name}'
                else:
                    page_name2 = f'se {page_name}'
                page2 = Page(site, page_name2)
                if not page2.exists():
                    if debug_level > 0:
                        print('Création de ') + \
                            sort_by_encoding(page_name2)
                    summary2 = 'Création d\'une redirection provisoire catégorisante du pronominal'
                    save_page(
                        page2,
                        f'#REDIRECT[[{page_name}'
                        + ']]\n<!-- Redirection temporaire avant de créer le verbe pronominal -->\n[[Catégorie:Wiktionnaire:Verbes pronominaux à créer en français]]',
                        summary2,
                    )

        page_content, summary = add_fr_demonyms_templates(page_content, summary)

    elif '{{langue|en}}' in page_content:
        regex = r'(\|en}} ===\n{{)fr\-rég'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1en-nom-rég', page_content)

        regex = r"({{S\|verbe\|en}} *=* *\n'*)to "
        if re.search(regex, page_content):
            page_content = re.sub(regex, r"\1", page_content)

        regex = r'(=== {{S\|adjectif\|en}} ===\n[^\n]*) *{{pluriel \?\|en}}'
        page_content = re.sub(regex, r"\1", page_content)

        regex = r"(# *''Prétérit de'' )([A-Za-z\- ]+)\."
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1{{l|\2|en}}.', page_content)
        regex = r"(# *''Participe passé de'' )([A-Za-z\- ]+)\."
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1{{l|\2|en}}.', page_content)

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
                summary = f'{summary}, conversion des liens flexions en modèle boite'
            regex = r'\({{f}} : [\[\']*' + re_page_radical_name + demonym_templates[l][3] + r'[\]\']*, {{mplur}} : [\[\']*' \
                + re_page_radical_name + demonym_templates[l][2] + r'[\]\']*, {{fplur}} : [\[\']*' + re_page_radical_name \
                + demonym_templates[l][4] + r'[\]\']*\)'
            if debug_level > 1:
                print(regex)
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|' + re_page_radical_name + r'}}', page_content)
                summary = f'{summary}, conversion des liens flexions en modèle boite'
            # Son
            if debug_level > 0:
                print(' son')
            regex = r'(\n\'\'\'' + regex_page_name + '\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' \
                    + demonym_templates[l][1] + r'\|' + \
                re_page_radical_name + r')}}'
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
        print('\nmove_etymology_templates()')
    page_languages = get_page_languages(page_content)
    for page_language in page_languages:
        for etym_template in etymology_templates:
            page_content, summary = move_etymology_template(
                page_content, summary, page_language, etym_template)

    if debug_level > 0:
        print('  Replace template otherwise')
    regex = r'{{(' + '|'.join(etymology_templates) + r')\|nocat(?:=1)*}}'
    page_content = re.sub(regex, r"{{term|\1}}", page_content)

    return page_content, summary


def move_etymology_template(page_content, summary, language_code, etym_template):
    if debug_level > 1:
        print(f' move_etymology_template({etym_template})')
    language_section, l_start, l_end = get_language_section(
        page_content, language_code)
    if language_section is not None and len(get_natures_sections(language_section)) == 1 \
            and language_section.find(etym_template[1:]) != -1:
        regex_template = r"\n'''[^\n]+(\n#)? *({{[^}]+}})? *({{[^}]+}})? *{{" + \
            etym_template + r'(\||})'
        if re.search(regex_template, language_section):
            new_language_section, summary = move_template_to_etymology(language_section, etym_template, summary,
                                                                       language_code)
            page_content = page_content.replace(
                language_section, new_language_section)
    return page_content, summary


def move_template_to_etymology(language_section, etym_template, summary, language_code):
    new_language_section, summary = remove_template(
        language_section, etym_template, summary, in_section=natures)
    etymology, s_start, s_end = get_section_by_name(
        new_language_section, 'étymologie')
    if etymology is None:
        new_language_section = add_line(new_language_section, language_code, 'étymologie',
                                        ': {{ébauche-étym|' + language_code + '}}')
        etymology, s_start, s_end = get_section_by_name(
            new_language_section, 'étymologie')
    if etymology is not None and etymology.find('{{' + etym_template) == -1:
        regex_etymology = r'(=\n:* *(\'*\([^\)]*\)\'*)?) *'
        if re.search(regex_etymology, language_section):
            etymology2 = re.sub(regex_etymology, r'\1 {{' + etym_template + r'}} ', etymology)
            new_language_section = new_language_section.replace(
                etymology, etymology2)
            summary = (
                (
                    f'{summary}, [[Wiktionnaire:Prise de décision/Déplacer les modèles de contexte'
                    + ' étymologiques dans la section « Étymologie »|ajout de {{'
                )
                + etym_template
            ) + r"}} dans l'étymologie]]"

    l = etym_template[:1]
    regex = r'{{' + etym_template + r'(?:\|' + language_code + r')?(?:\|m=1)?}} *(?:\[\[' + etym_template \
            + r'\|)?[' + l + l.upper() + r']' + \
        etym_template[1:] + r'(?:\]\])? de '
    new_language_section = re.sub(regex, '{{' + etym_template + '|' + language_code + '|m=1}} de ', new_language_section)
    return new_language_section, summary


def format_wikicode(page_content, summary, page_name):
    # TODO hors modèles https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:fr-accord-comp-mf&oldid=prev&diff=26238109
    # page_content = page_content.replace('&nbsp;', ' ')
    # page_content = re.sub(r'«[  \t]*', r'« ', page_content) # pb &#160;
    # page_content = re.sub(r'[  \t]*»', r' »', page_content)
    page_content = page_content.replace('{|\n|}', '')
    page_content = page_content.replace(
        f'[[{page_name}]]', '\'\'\'' + page_name + '\'\'\''
    )

    if debug_level > 1:
        print(' #* or #:')
    page_content = page_content.replace('\n #*', '\n#*')
    page_content = page_content.replace('\n #:', '\n#:')
    final_page_content = ''
    while page_content.find('\n#:') != -1:
        final_page_content = final_page_content + \
            page_content[:page_content.find('\n#:')+2]
        if final_page_content.rfind('{{langue|') == final_page_content.rfind('{{langue|fr}}'):
            separator = '*'
        else:
            separator = ':'
        page_content = separator + \
            page_content[page_content.find('\n#:')+len('\n#:'):]
    page_content = final_page_content + page_content

    if debug_level > 1:
        print(' add form line')
    # TODO fix https://fr.wiktionary.org/w/index.php?title=Theresa&diff=27792535&oldid=25846879
    # page_content = re.sub(r'([^d\-]+-\|[a-z]+\}\}\n)# *', r"\1'''" + page_name + r"''' {{pron}}\n# ", page_content)

    return page_content, summary


def add_appendix_links(page_content, summary, page_name):
    if debug_level > 0:
        print('\nadd_appendix_links()')
    if (' ' not in page_name or 'JackBot' in page_name) and page_content.find('{{voir-conj') == -1 \
            and page_content.find('{{invar') == -1 and page_content.find('{{verbe non standard') == -1 \
            and '[[Image:' not in page_content and '[[image:' not in page_content \
            and '[[File:' not in page_content and '[[file:' not in page_content \
            and '[[Fichier:' not in page_content and '[[Fichier:' not in page_content:
        # Sinon bug https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687
        # TODO add if images
        if debug_level > 0:
            print(' {{conj}}')
        language_suffixes = [('es', 'ar', 'arsi', 'er', 'ersi', 'ir', 'irsi'),
                             ('pt', 'ar', 'ar-se', 'er', 'er-se', 'ir', 'ir-se'),
                             ('it', 'are', 'arsi', 'ere', 'ersi', 'ire', 'irsi'),
                             ('fr', 'er', 'er', 'ir', 'ir', 're', 'ar'),
                             ('ru', '', '', '', '', '', '')
                             ]
        for l in language_suffixes:
            # Pas de conjugaison pour les verbes français avec infinitif en -ave
            # TODO use l[>0] instead
            if l[0] == 'fr' and page_name[-3:] == 'ave':
                continue

            # TODO treat verbe|num=1...
            section_title = r'{{S\|verbe\|' + l[0] + '}}'
            if re.compile(section_title).search(page_content) and not \
                    re.compile(section_title + r'[= ]+\n+[^\n]*\n*[^\n]*\n*{{(conj[a-z1-3| ]*|invar)').search(page_content):
                if debug_level > 0:
                    print(' Missing {{conj|' + l[0] + '}} in a verb section')

                if re.compile(section_title + r'[^\n]*\n*[^\n]*\n*[^{]*{{pron\|[^}]*}}').search(page_content):
                    if debug_level > 0:
                        print(' Add {{conj|' + l[0] + '}} after {{pron|...}}')

                    i1 = re.search(
                        section_title + r'[^\n]*\n*[^\n]*\n*[^{]*{{pron\|[^\}]*}}', page_content).end()
                    page_content = page_content[:i1] + \
                        ' {{conjugaison|' + l[0] + '}}' + page_content[i1:]

                elif debug_level > 0:
                    print(' No pronunciation to add {{conj}} after')

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
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' + page_content[
                        page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' + page_content[
                        page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=1' + page_content
        elif page_name[len(page_name) - 2:] == 'er' or page_name[len(page_name) - 4:] == 'ersi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' + page_content[
                        page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' + page_content[
                        page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=2' + page_content
        elif page_name[len(page_name) - 2:] == 'ir' or page_name[len(page_name) - 4:] == 'irsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' + page_content[
                        page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' + page_content[
                        page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
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
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                        + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '1' \
                        + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                        + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '1' \
                        + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=1' + page_content
        elif page_name[len(page_name) - 2:] == 'er' or page_name[len(page_name) - 4:] == 'er-se':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                        + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '2' \
                        + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                        + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '2' \
                        + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=2' + page_content
        elif page_name[len(page_name) - 2:] == 'ir' or page_name[len(page_name) - 4:] == 'ir-se':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                        + page_content[page_content.find('|grp=') + len('|grp='):]
                else:
                    page_content = page_content[:page_content.find('|grp=') + len('|grp=')] + '3' \
                        + page_content[page_content.find('|grp=') + len('|grp=') + 1:]
            elif page_content.find('groupe=') != -1 and page_content.find('groupe=') < page_content.find('}}'):
                if page_content.find('|groupe=') in [
                    page_content.find('|groupe=}'),
                    page_content.find('|groupe=|'),
                ]:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                        + page_content[page_content.find('|groupe=') + len('|groupe='):]
                else:
                    page_content = page_content[:page_content.find('|groupe=') + len('|groupe=')] + '3' \
                        + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
            else:
                page_content = '|groupe=3' + page_content

    elif language_code == 'it':
        if page_name[len(page_name) - 3:] == 'are' or page_name[len(page_name) - 4:] == 'arsi':
            if page_content.find('grp=') != -1 and page_content.find('grp=') < page_content.find('}}'):
                if page_content.find('|grp=') in [
                    page_content.find('|grp=}'),
                    page_content.find('|grp=|'),
                ]:
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
                        + page_content[page_content.find('|groupe=') + len('|groupe=') + 1:]
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
        final_page_content, page_content = next_template(
            final_page_content, page_content)
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
        print('\ntreat_verb_inflexion()')
    infinitive = get_lemma_from_conjugation(current_page_content)
    if infinitive != '':
        # TODO check infinitive suffix to avoid spreading human errors:
        # https://fr.wiktionary.org/w/index.php?title=d%C3%A9sappartient&diff=prev&oldid=27612966
        infinitive_page = get_content_from_page_name(infinitive, site)
        if infinitive_page is not None:
            # http://fr.wiktionary.org/w/index.php?title=Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet
            page_content2 = page_content[page_content.find(
                'fr-verbe-flexion')+len('fr-verbe-flexion'):]
            if page_content2.find('flexion=') != -1 and page_content2.find('flexion=') < page_content2.find('}}'):
                page_content3 = page_content2[page_content2.find(
                    'flexion='):len(page_content2)]
                if page_content3.find('|') != -1 and page_content3.find('|') < page_content3.find('}'):
                    page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                        + page_content[page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')
                                       + page_content2.find('flexion=')+page_content3.find('|'):]
            page_content2 = page_content[page_content.find(
                'fr-verbe-flexion')+len('fr-verbe-flexion'):]
            if page_content2.find(infinitive) == -1 or page_content2.find(infinitive) > page_content2.find('}}'):
                page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] + '|' \
                    + infinitive + \
                    page_content[page_content.find(
                        'fr-verbe-flexion')+len('fr-verbe-flexion'):]
                # Bug de l'hyperlien vers l'annexe
                if page_content.find('|' + infinitive + '\n') != -1:
                    page_content = page_content[:page_content.find('|' + infinitive + '\n')+len('|' + infinitive)] \
                        + page_content[page_content.find('|' + infinitive + '\n')+len('|' + infinitive + '\n'):]
            # Analyse du modèle en cours
            page_content2 = page_content[page_content.find(
                'fr-verbe-flexion')+len('fr-verbe-flexion'):]
            page_content2 = page_content2[:page_content2.find('}}')+2]
            if page_content2.find('impers=oui') == -1:
                # http://fr.wiktionary.org/w/index.php?title=Modèle:fr-verbe-flexion&action=edit
                fr_section, l_start, l_end = get_language_section(
                    infinitive_page, 'fr')
                if infinitive_page.find('{{impers|fr}}') != -1 or (infinitive_page.find('{{impersonnel|fr}}') != -1
                                                                   and fr_section is not None and count_definitions(fr_section) == 1):
                    page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                        + '|impers=oui' + \
                        page_content[page_content.find(
                            'fr-verbe-flexion')+len('fr-verbe-flexion'):]
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
                            + '|imp.p.2s=oui' + \
                            page_content[page_content.find(
                                'ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|sub.p.3s=oui' + \
                            page_content[page_content.find(
                                'ind.p.1s=oui')+len('ind.p.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') != -1 \
                            and page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|sub.p.1s=oui' + \
                            page_content[page_content.find(
                                'ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.3s=oui') == -1 \
                            and page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|ind.p.3s=oui' + \
                            page_content[page_content.find(
                                'ind.p.1s=oui') + len('ind.p.1s=oui'):]
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
                            + '|sub.p.2s=oui' + \
                            page_content[page_content.find(
                                'ind.p.2s=oui')+len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.2s=oui') == -1 and page_content2.find('sub.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.2s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # nous
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui')] \
                            + '|sub.p.1p=oui' + \
                            page_content[page_content.find(
                                'ind.i.1p=oui')+len('ind.i.1p=oui'):]
                    if page_content2.find('ind.i.1p=oui') == -1 and page_content2.find('sub.p.1p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')]\
                            + '|ind.i.1p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # vous
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui')] \
                            + '|sub.p.2p=oui' + \
                            page_content[page_content.find(
                                'ind.i.2p=oui')+len('ind.i.2p=oui'):]
                    if page_content2.find('ind.i.2p=oui') == -1 and page_content2.find('sub.p.2p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.2p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # ils
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui')] \
                            + '|sub.p.3p=oui' + \
                            page_content[page_content.find(
                                'ind.p.3p=oui')+len('ind.p.3p=oui'):]
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
                            + '|imp.p.2s=oui' + \
                            page_content[page_content.find(
                                'ind.ps.2s=oui')+len('ind.ps.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') == -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.ps.1s=oui')+len('ind.ps.1s=oui')] \
                            + '|ind.ps.2s=oui' + \
                            page_content[page_content.find(
                                'ind.ps.1s=oui')+len('ind.ps.1s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') != -1 \
                            and page_content2.find('ind.ps.1s=oui') == -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.2s=oui')+len('ind.p.2s=oui')] \
                            + '|ind.ps.1s=oui' + \
                            page_content[page_content.find(
                                'ind.p.2s=oui')+len('ind.p.2s=oui'):]
                    elif page_content2.find('ind.p.1s=oui') != -1 and page_content2.find('ind.p.2s=oui') == -1 \
                            and page_content2.find('ind.ps.1s=oui') != -1 and page_content2.find('ind.ps.2s=oui') != -1\
                            and page_content2.find('imp.p.2s=oui') != -1:
                        page_content = page_content[:page_content.find('ind.p.1s=oui')+len('ind.p.1s=oui')] \
                            + '|ind.p.2s=oui' + \
                            page_content[page_content.find(
                                'ind.p.1s=oui')+len('ind.p.1s=oui'):]
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
                            + '|sub.i.1s=oui' + \
                            page_content[page_content.find(
                                'sub.p.3s=oui')+len('sub.p.3s=oui'):]
                    elif page_content2.find('sub.p.1s=oui') != -1 and page_content2.find('sub.p.3s=oui') == -1 \
                            and page_content2.find('sub.i.1s=oui') != -1:
                        page_content = page_content[:page_content.find('sub.p.1s=oui')+len('sub.p.1s=oui')] \
                            + '|sub.p.3s=oui' + \
                            page_content[page_content.find(
                                'sub.p.1s=oui')+len('sub.p.1s=oui'):]
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
                                                                          + len('fr-verbe-flexion'):]
                    elif page_content2.find('sub.p.1s=oui') == -1 and page_content2.find('sub.p.3s=oui') != -1 \
                            and page_content2.find('sub.i.1s=oui') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.1s=oui|sub.i.1s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                                          + len('fr-verbe-flexion'):]
                    # tu
                    if page_content2.find('sub.p.2s=oui') != -1 and page_content2.find('sub.i.2s=oui') != -1:
                        pass
                    if page_content2.find('sub.p.2s=oui') != -1 and page_content2.find('sub.i.2s=oui') == -1:
                        page_content = page_content[:page_content.find('sub.p.2s=oui')+len('sub.p.2s=oui')] \
                            + '|sub.i.2s=oui' + \
                            page_content[page_content.find(
                                'sub.p.2s=oui')+len('sub.p.2s=oui'):]
                    if page_content2.find('sub.p.2s=oui') == -1 and page_content2.find('sub.i.2s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|sub.p.2s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # il
                    if page_content2.find('ind.p.3s=oui') != -1 and page_content2.find('ind.ps.3s=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3s=oui') != -1 and page_content2.find('ind.ps.3s=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3s=oui')+len('ind.p.3s=oui')] \
                            + '|ind.ps.3s=oui' + \
                            page_content[page_content.find(
                                'ind.p.3s=oui')+len('ind.p.3s=oui'):]
                    if page_content2.find('ind.p.3s=oui') == -1 and page_content2.find('ind.ps.3s=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.3s=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # nous
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.1p=oui') != -1 and page_content2.find('sub.p.1p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.1p=oui')+len('ind.i.1p=oui')] \
                            + '|sub.p.1p=oui' + \
                            page_content[page_content.find(
                                'ind.i.1p=oui')+len('ind.i.1p=oui'):]
                    if page_content2.find('ind.i.1p=oui') == -1 and page_content2.find('sub.p.1p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.1p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # vous
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') != -1:
                        pass
                    if page_content2.find('ind.i.2p=oui') != -1 and page_content2.find('sub.p.2p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.i.2p=oui')+len('ind.i.2p=oui')] \
                            + '|sub.p.2p=oui' + \
                            page_content[page_content.find(
                                'ind.i.2p=oui')+len('ind.i.2p=oui'):]
                    if page_content2.find('ind.i.2p=oui') == -1 and page_content2.find('sub.p.2p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.i.2p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                    # ils
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') != -1:
                        pass
                    if page_content2.find('ind.p.3p=oui') != -1 and page_content2.find('sub.p.3p=oui') == -1:
                        page_content = page_content[:page_content.find('ind.p.3p=oui')+len('ind.p.3p=oui')] \
                            + '|sub.p.3p=oui' + \
                            page_content[page_content.find(
                                'ind.p.3p=oui')+len('ind.p.3p=oui'):]
                    if page_content2.find('ind.p.3p=oui') == -1 and page_content2.find('sub.p.3p=oui') != -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|ind.p.3p=oui' + page_content[page_content.find('fr-verbe-flexion')
                                                             + len('fr-verbe-flexion'):]
                elif (infinitive_page.find('|groupe=3') != -1 or infinitive_page.find('|grp=3') != -1) \
                        and infinitive_page.find('|groupe2=') == -1:
                    if page_content2.find('grp=3') == -1:
                        page_content = page_content[:page_content.find('fr-verbe-flexion')+len('fr-verbe-flexion')] \
                            + '|grp=3' + \
                            page_content[page_content.find(
                                'fr-verbe-flexion')+len('fr-verbe-flexion'):]

    final_page_content = final_page_content + \
        page_content[:page_content.find('\n')+1]
    page_content = page_content[page_content.find('\n')+1:]
    return page_content, final_page_content, summary


def treat_noun_inflexion(page_content, summary, page_name, regex_page_name, natures_with_plural, language_code,
                         singular_page_name):
    if debug_level > 0:
        print('\ntreat_noun_inflexion()')
    for nature in natures_with_plural:
        regex = r"(== {{langue|" + language_code + r"}} ==\n=== {{S\|" + \
            nature + r"\|" + language_code + r")\|num=2"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1', page_content)
            summary = f'{summary}, retrait de |num='

        regex = r"(=== {{S\|" + nature + r"\|" + language_code + r")(\}} ===\n[^\n]*\n*'''" + regex_page_name \
                + r"'''[^\n]*\n# *'*'*(Masculin)*(Féminin)* *[P|p]luriel de *'*'* *\[\[)"
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1|flexion\2', page_content)
            summary = f'{summary}, ajout de |flexion'

        if page_name[-2:] == 'ss':
            if debug_level > 0:
                print('  -ss')
        elif singular_page_name != '':
            inflexion_inflexion_template = get_inflexion_template(
                page_name, language_code, nature)
            if inflexion_inflexion_template is None or inflexion_inflexion_template == '':
                if debug_level > 0:
                    print('  Ajout d\'une boite dans une flexion')
                lemma_inflexion_template = get_inflexion_template_from_lemma(
                    singular_page_name, language_code, nature)
                if lemma_inflexion_template is not None:
                    for inflexion_template_fr_with_ms in inflexion_templates_fr_with_ms:
                        if lemma_inflexion_template.find(inflexion_template_fr_with_ms) != -1:
                            if debug_level > 0:
                                print('  inflexion_templates_fr_with_ms')
                            regex = r"\|ms=[^\|}]*"
                            if not re.search(regex, lemma_inflexion_template):
                                lemma_inflexion_template = f'{lemma_inflexion_template}|ms={singular_page_name}'
                    for inflexion_template_fr_with_s in inflexion_templates_fr_with_s:
                        if lemma_inflexion_template.find(inflexion_template_fr_with_s) != -1:
                            regex = r"\|s=[^\|}]*"
                            if not re.search(regex, lemma_inflexion_template):
                                lemma_inflexion_template = f'{lemma_inflexion_template}|s={singular_page_name}'

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
                        summary = summary + \
                            ', ajout de {{' + lemma_inflexion_template + \
                            r'}} depuis le lemme'

        if page_name[-1:] != 's':
            regex = r"(=== {{S\|" + nature + r"\|" + language_code + r"\|flexion}} ===\n)('''" + page_name \
                    + r"''' {{pron\|)([^\|}]*)(\|" + language_code \
                    + r"}}\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
            if re.search(regex, page_content):
                # page_content = re.sub(regex, r'\1{{' + language_code + r'-rég|s=\7|\3}}\n\2\3\4\7', page_content)
                page_content = re.sub(regex,
                                      r'\1{{' + language_code + r'-rég|s=' +
                                      singular_page_name + '|\3}}\n\2\3\4\5',
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


# (TODO: check other wikt language section)
def update_if_page_exists_on_other_wiktionaries(
        final_page_content,
        page_content,
        external_site,
        external_page_name
):
    if external_site == '' or external_page_name == '':
        return final_page_content, page_content

    d = 0
    is_page_found = True
    try:
        external_page = Page(external_site, external_page_name)
    except pywikibot.exceptions.InconsistentTitleError as e:
        if debug_level > d:
            print(e)
        final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')
        is_page_found = False
    except pywikibot.exceptions.InvalidTitleError as e:
        if debug_level > d:
            print(e)
        final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')
        is_page_found = False
    except pywikibot.exceptions.NoPageError as e:
        if debug_level > d:
            print(e)
        if external_page_name.find('\'') != -1:
            external_page_name = external_page_name.replace('\'', '’')
        elif external_page_name.find('’') != -1:
            external_page_name = external_page_name.replace('’', '\'')
        if external_page_name != external_page.title():
            try:
                external_page = Page(external_site, external_page_name)
            except pywikibot.exceptions.NoPageError:
                final_page_content, page_content = next_translation_template(
                    final_page_content,
                    page_content,
                    '-'
                )
                is_page_found = False
                external_page = None
    except BaseException as e:
        if debug_level > d:
            print(e)
        is_page_found = False
    if debug_level > d:
        print(f'  is_page_found: {is_page_found}')

    is_external_page_exist = False
    if is_page_found:
        do_treat_new_missing = True
        try:
            is_external_page_exist = external_page.exists()
        except AttributeError:
            if debug_level > d:
                print('  removed site (--)')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '--')
            do_treat_new_missing = False
        except pywikibot.exceptions.InvalidPageError:
            if debug_level > d:
                print(f'  InvalidPageError: {external_page_name}')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '--')
            do_treat_new_missing = False
        except pywikibot.exceptions.InconsistentTitleError:
            if debug_level > d:
                print(f'  InconsistentTitleError: {external_page_name}')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')
            do_treat_new_missing = False
        except pywikibot.exceptions.InvalidTitleError:
            if debug_level > d:
                print(f'  InvalidTitleError: {external_page_name}')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '')
            do_treat_new_missing = False

        if is_external_page_exist:
            if debug_level > d:
                print('  exists (+)')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '+')
        elif do_treat_new_missing and external_site.lang != 'zh':
            # TODO handle simplified/traditional https://fr.wiktionary.org/w/index.php?title=poussin&diff=31244062&oldid=31244057
            if debug_level > d:
                print('  not exists (-)')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '-')

    if debug_level > d:
        print('')

    return final_page_content, page_content


def treat_translations(page_content, final_page_content, summary, end_position, site_family):
    # Empty or stub
    has_not_to_call_interwiki_link = end_position in [
        page_content.find('}}'),
        page_content.find('|}}') - 1,
    ]

    if has_not_to_call_interwiki_link:
        final_page_content = final_page_content + page_content[:page_content.find('}}') + 2]
        final_page_content, page_content = next_template(final_page_content, page_content)
    else:
        page_content2 = page_content[end_position + 1:]
        current_language = page_content2[:page_content2.find('|')]

        if current_language == '':
            return page_content, final_page_content, summary

        page_content = replace_letters_by_language(page_content, current_language)
        page_content2 = page_content[end_position + 1:]

        # TODO: reproduce the closed site bug https://fr.wiktionary.org/w/index.php?title=chat&diff=prev&oldid=9366302
        # Get the other wiktionary page
        external_site = ''
        external_page_name = ''
        d = 0
        page_content3 = page_content2[page_content2.find('|') + 1:]
        if debug_level > d:
            print(f' remote wiki language: {current_language}')
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
            external_site = get_wiki('species', 'species')
        elif current_language in incubator_wiktionaries:
            # Otherwise: Non-JSON response received from server wiktionary:ba; the server may be down.
            external_site = None
        else:
            external_site = get_wiki(current_language, site_family)
        if external_site is None:
            if debug_level > d:
                print('  no site (--)')
            final_page_content, page_content = next_translation_template(final_page_content, page_content, '')
            external_site = ''
        elif external_site != '':
            if page_content3.find('|') != -1 and page_content3.find('|') < page_content3.find('}}'):
                external_page_name = page_content3[:page_content3.find('|')]
            else:
                external_page_name = page_content3[:page_content3.find('}}')]
        if external_page_name != '' and external_page_name.find('<') != -1:
            external_page_name = external_page_name[:external_page_name.find('<')]
        if debug_level > d:
            msg = f' remote wiki page: {external_page_name}'
            try:
                print(msg)
            except UnicodeEncodeError as e:
                # Python 2 only
                print(msg.encode(config.console_encoding, 'replace'))

        final_page_content, page_content = update_if_page_exists_on_other_wiktionaries(
            final_page_content,
            page_content,
            external_site,
            external_page_name
        )

    return page_content, final_page_content, summary


def treat_pronunciation(page_content, final_page_content, summary, end_position, current_template, language_code):
    if current_template == 'pron':
        page_content2 = page_content[end_position+1:page_content.find('}}')]
        # TODO generic regex
        if '|lang=' in page_content2:
            page_content = page_content[:page_content.find('|lang=')+1] + page_content[page_content.find('|lang=')+6:]

        # Replace IPA letters
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
        # TODO if language_code == 'es': β/, /ð/ et /ɣ/ instead of /b/, /d/ et /ɡ/

    if page_content[:8] == 'pron||}}':
        final_page_content = final_page_content + page_content[:page_content.find('}}')] + language_code + '}}'
    elif page_content[end_position:end_position+3] == '|}}' or page_content[end_position:end_position+4] == '| }}':
        final_page_content = final_page_content + current_template + "||" + language_code + '}}'
    elif page_content.find("lang=") != -1 and page_content.find("lang=") < page_content.find('}}'):
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


# TODO use {{voir anagrammes|fr}}
def add_anagrams(page_content, summary, page_name, language_code):
    anagrams = get_anagram(page_name)
    anagrams_list = ''
    for anagram in anagrams:
        if anagram != page_name:
            if debug_level > 0:
                print(f' {anagram}')
            anagram_page = Page(site, anagram)
            if anagram_page.exists():
                if anagram_page.namespace() != 0 and not is_test_page(anagram):
                    break
                anagram_page_content = get_content_from_page(anagram_page)
                if anagram_page_content is None:
                    break
                if anagram_page_content.find('{{langue|' + language_code + '}}') != -1:
                    anagrams_list = anagrams_list + \
                        '* {{lien|' + anagram + '|' + language_code + '}}\n'
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
                + page_content[anagram_position +
                               page_content2.find('\n=== {{S|voir'):]
        elif page_content2.find('\n=== {{S|références}}') != -1 and ((page_content2.find(
                '{{langue|') != -1 and page_content2.find('\n=== {{S|références}}') < page_content2.find(
                '{{langue|')) or page_content2.find('{{langue|') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '\n=== {{S|références}}')] + '\n=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                + page_content[anagram_position +
                               page_content2.find('\n=== {{S|références}}'):]
        elif page_content2.find('== {{langue|') != -1 and ((page_content2.find(
                '[[Catégorie:') != -1 and page_content2.find('== {{langue|') < page_content2.find(
                '[[Catégorie:')) or page_content2.find('[[Catégorie:') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '== {{langue|')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                + page_content[anagram_position +
                               page_content2.find('== {{langue|'):]
        elif page_content2.find('=={{langue|') != -1 and ((page_content2.find(
                '[[Catégorie:') != -1 and page_content2.find('=={{langue|') < page_content2.find(
                '[[Catégorie:')) or page_content2.find('[[Catégorie:') == -1):
            page_content = page_content[:anagram_position + page_content2.find(
                '=={{langue|')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                + page_content[anagram_position +
                               page_content2.find('=={{langue|'):]
        elif page_content2.find('{{clé de tri') != -1:
            page_content = page_content[:anagram_position + page_content2.find(
                '{{clé de tri')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                + page_content[anagram_position +
                               page_content2.find('{{clé de tri'):]
        elif page_content2.find('[[Catégorie:') != -1:
            page_content = page_content[:anagram_position + page_content2.find(
                '[[Catégorie:')] + '=== {{S|anagrammes}} ===\n' + anagrams_list + '\n'\
                + page_content[anagram_position +
                               page_content2.find('[[Catégorie:'):]
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
                page_content = page_content + \
                    '\n\n=== {{S|anagrammes}} ===\n' + anagrams_list
    return page_content, summary


def add_fr_demonyms_templates(page_content, summary):
    # TODO fix https://fr.wiktionary.org/w/index.php?title=Utilisateur:JackBot/test&action=rollback&from=JackBot&token=2de622be0b7aaabdcffd784e9ed0dad66500d3f9%2B%5C
    return page_content, summary

    if debug_level > 0:
        print(' add_demonyms_templates()')
    regex = r'({{fr\-[^}]+)\\'
    while re.search(regex, page_content):
        page_content = re.sub(regex, r'\1', page_content)

    line = 6
    column = 4
    # TODO use inflexion_templates_fr_with_s
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
        regex = r'\({{p}} : [\[\']*' + regex_page_name + demonym_templates[l][2] + r'[\]\']*, {{f}} : [\[\']*' + regex_page_name + \
            demonym_templates[l][3] + r'[\]\']*, {{fplur}} : [\[\']*' + \
                regex_page_name + demonym_templates[l][4] + r'[\]\']*\)'
        if re.search(regex, page_content):
            page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|pron=}}', page_content)
            summary = f'{summary}, conversion des liens flexions en modèle boite'
        # Depuis un féminin
        if demonym_templates[l][1] == r'fr-accord-s' and regex_page_name[-1:] == 'e' and regex_page_name[-2:-1] == 's':
            regex = r'\({{p}} : [\[\']*' + regex_page_name + \
                r's[\]\']*, {{m}} : [\[\']*' + \
                    regex_page_name[:-1] + r'[\]\']*\)'
            if re.search(regex, page_content):
                page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|ms=' + regex_page_name[:-1].replace('\\', '') + '}}', page_content)
                summary = f'{summary}, conversion des liens flexions en modèle boite'
        regex = r'\({{f}} : [\[\']*' + regex_page_name + demonym_templates[l][3] + r'[\]\']*, {{mplur}} : [\[\']*' + regex_page_name + \
            demonym_templates[l][2] + r'[\]\']*, {{fplur}} : [\[\']*' + \
                regex_page_name + demonym_templates[l][4] + r'[\]\']*\)'
        if re.search(regex, page_content):
            page_content = re.sub(regex, '{{' + demonym_templates[l][1] + '|pron=}}', page_content)
            summary = f'{summary}, conversion des liens flexions en modèle boite'
        if debug_level > 1:
            print(' avec son')
        regex = r'(\n\'\'\'' + regex_page_name + '\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + \
            demonym_templates[l][1] + r'\|[pron\=]*)}}'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\n\4\2}}\1\2\3', page_content)

        deplacement_modele_inflexion = False
        # On différencie les cas pas d'espace avant le modèle / espace avant le modèle
        regex = r'( ===\n)(\'\'\'[^\n]+[^ ])({{' + demonym_templates[l][1] + r'\|[^}]*}})'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1\3\n\2', page_content)
            deplacement_modele_inflexion = True
        # Espace avant le modèle
        regex_space = r'( ===\n)(\'\'\'[^\n]+) ({{' + \
            demonym_templates[l][1] + r'\|[^}]*}})'
        if re.search(regex_space, page_content):
            page_content = re.sub(regex_space, r'\1\3\n\2', page_content)
            deplacement_modele_inflexion = True
        if deplacement_modele_inflexion:
            summary = f'{summary}, déplacement des modèles de flexions'

    regex = r'({{fr\-accord\-comp\-mf[^}]*\| *trait *=) *([\|}])'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1&nbsp;\2', page_content)

    return page_content, summary


def replace_letters_by_language(page_content, current_language):
    if current_language == 'en':
        while page_content.find('’') != -1 and page_content.find('’') < page_content.find('\n'):
            page_content = page_content[:page_content.find('’')] + '\'' + page_content[page_content.find('’') + 1:]
    elif current_language in ['ro', 'mo']:
        while page_content.find('ş') != -1 and page_content.find('ş') < page_content.find('\n'):
            page_content = page_content[:page_content.find('ş')] + 'ș' + page_content[page_content.find('ş') + 1:]
        while page_content.find('Ş') != -1 and page_content.find('Ş') < page_content.find('\n'):
            page_content = page_content[:page_content.find('Ş')] + 'Ș' + page_content[page_content.find('Ş') + 1:]
        while page_content.find('ţ') != -1 and page_content.find('ţ') < page_content.find('\n'):
            page_content = page_content[:page_content.find('ţ')] + 'ț' + page_content[page_content.find('ţ') + 1:]
        while page_content.find('Ţ') != -1 and page_content.find('Ţ') < page_content.find('\n'):
            page_content = page_content[:page_content.find('Ţ')] + 'Ț' + page_content[page_content.find('Ţ') + 1:]
    elif current_language in ['az', 'ku', 'sq', 'tk', 'tr', 'tt']:
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
    elif current_language == 'cmn':
        page_content = page_content[:page_content.find('cmn')] + 'zh' + page_content[page_content.find('cmn') + 3:]
    elif current_language == 'nn':
        page_content = page_content[:page_content.find('nn')] + 'no' + page_content[page_content.find('nn') + 2:]
    elif current_language == 'per':
        page_content = page_content[:page_content.find('per')] + 'fa' + page_content[page_content.find('per') + 3:]
    elif current_language == 'wel':
        page_content = page_content[:page_content.find('wel')] + 'cy' + page_content[page_content.find('wel') + 3:]
    elif current_language == 'zh-classical':
        page_content = (page_content[:page_content.find('zh-classical')] + 'lzh'
                        + page_content[page_content.find('zh-classical') + len('zh-classical'):])
    elif current_language == 'ko-Hani':
        page_content = (page_content[:page_content.find('ko-Hani')] + 'ko'
                        + page_content[page_content.find('ko-Hani') + len('ko-Hani'):])
    elif current_language == 'ko-hanja':
        page_content = (page_content[:page_content.find('ko-hanja')] + 'ko'
                        + page_content[page_content.find('ko-hanja') + len('ko-hanja'):])
    elif current_language == 'zh-min-nan':
        page_content = (page_content[:page_content.find('zh-min-nan')] + 'nan'
                        + page_content[page_content.find('zh-min-nan') + len('zh-min-nan'):])
    elif current_language == 'roa-rup':
        page_content = (page_content[:page_content.find('roa-rup')] + 'rup'
                        + page_content[page_content.find('roa-rup') + len('roa-rup'):])
    elif current_language == 'zh-yue':
        page_content = (page_content[:page_content.find('zh-yue')] + 'yue'
                        + page_content[page_content.find('zh-yue') + len('zh-yue'):])

    return page_content

'''
TODO:
    deploy add_pronunciationFromContent()
    def sortSections(page_content):
    def uncategorizeDoubleTemplateWhenCategory(page_content, summary):
    def checkTranslationParagraphsNumberBySense(page_content, summary):
    def get_form_line() & get_definition_line()

if page_content.find('{{conj') != -1:
    if debug_level > 0: print(' Ajout des groupes dans {{conj}}')
'''

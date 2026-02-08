#!/usr/bin/env python
# coding: utf-8
"""
Ce script traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}})
TODO handle more errors from https://wstat.fr/template/info/Article
"""

from __future__ import absolute_import, unicode_literals
import re
import pywikibot
from page_functions import *
from templates_translator_list import *

do_check_url = False

month_line = 12
month_column = 2
months_translations = [[0] * (month_column + 1) for _ in range(month_line + 1)]
months_translations[1][1] = 'January'
months_translations[1][2] = 'janvier'
months_translations[2][1] = 'February'
months_translations[2][2] = 'février'
months_translations[3][1] = 'March'
months_translations[3][2] = 'mars'
months_translations[4][1] = 'April'
months_translations[4][2] = 'avril'
months_translations[5][1] = 'May'
months_translations[5][2] = 'mai'
months_translations[6][1] = 'June'
months_translations[6][2] = 'juin'
months_translations[7][1] = 'July'
months_translations[7][2] = 'juillet'
months_translations[8][1] = 'August'
months_translations[8][2] = 'août'
months_translations[9][1] = 'September'
months_translations[9][2] = 'septembre'
months_translations[10][1] = 'October'
months_translations[10][2] = 'octobre'
months_translations[11][1] = 'November'
months_translations[11][2] = 'novembre'
months_translations[12][1] = 'December'
months_translations[12][2] = 'décembre'

languages_line = 17
languages_column = 2
languages_translations = [[0] * (languages_column + 1)
                          for _ in range(languages_line + 1)]
languages_translations[1][1] = 'French'
languages_translations[1][2] = 'fr'
languages_translations[2][1] = 'English'
languages_translations[2][2] = 'en'
languages_translations[3][1] = 'German'
languages_translations[3][2] = 'de'
languages_translations[4][1] = 'Spanish'
languages_translations[4][2] = 'es'
languages_translations[5][1] = 'Italian'
languages_translations[5][2] = 'it'
languages_translations[6][1] = 'Portuguese'
languages_translations[6][2] = 'pt'
languages_translations[7][1] = 'Dutch'
languages_translations[7][2] = 'nl'
languages_translations[8][1] = 'Russian'
languages_translations[8][2] = 'ru'
languages_translations[9][1] = 'Chinese'
languages_translations[9][2] = 'zh'
languages_translations[10][1] = 'Japanese'
languages_translations[10][2] = 'ja'
languages_translations[11][1] = 'Polish'
languages_translations[11][2] = 'pl'
languages_translations[12][1] = 'Norwegian'
languages_translations[12][2] = 'no'
languages_translations[13][1] = 'Swedish'
languages_translations[13][2] = 'sv'
languages_translations[14][1] = 'Finnish'
languages_translations[14][2] = 'fi'
languages_translations[15][1] = 'Indonesian'
languages_translations[15][2] = 'id'
languages_translations[16][1] = 'Hindi'
languages_translations[16][2] = 'hi'
languages_translations[17][1] = 'Arabic'
languages_translations[17][2] = 'ar'

access_line = 4
access_column = 2
access_translations = [[0] * (access_column + 1)
                       for _ in range(access_line + 1)]
access_translations[1][1] = 'free'
access_translations[1][2] = 'libre'
access_translations[2][1] = 'registration'
access_translations[2][2] = 'inscription'
access_translations[3][1] = 'limited'
access_translations[3][2] = 'limité'
access_translations[4][1] = 'subscription'
access_translations[4][2] = 'payant'


def set_globals_translator(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


def translate_templates(current_page, summary):
    if debug_level > 1:
        print('\ntranslate_templates()')

    current_page = current_page.replace('[//https://', '[https://')
    current_page = current_page.replace('[//http://', '[http://')
    current_page = current_page.replace('http://http://', 'http://')
    current_page = current_page.replace('https://https://', 'https://')
    current_page = current_page.replace('<ref>{{en}}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}}} ', '<ref>{{en}} ')
    current_page = re.sub(r'[C|c]ita(tion)? *\n* *(\|[^}{]*title *=)', r'ouvrage\2', current_page)
    current_page = translate_link_templates(current_page)
    current_page = translate_dates(current_page)
    current_page = translate_languages(current_page)
    current_page = translate_access(current_page)

    # Paramètres inutiles
    current_page = re.sub(
        r'{{ *Références *\| *colonnes *= *}}', r'{{Références}}', current_page)
    # Dans {{article}}, "éditeur" vide bloque "périodique", "journal" ou "revue"
    current_page = re.sub(
        r'{{ *(a|A)rticle *((?:\||\n)[^{}]*)\| *éditeur *= *([\||}|\n]+)', r'{{\1rticle\2\3', current_page)
    # https://fr.wikipedia.org/w/index.php?title=Discussion_utilisateur:JackPotte&oldid=prev&diff=165491794#Suggestion_pour_JackBot_:_Signalement_param%C3%A8tre_obligatoire_manquant_+_Lien_web_vs_Article
    current_page = re.sub(
        r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *(?:ref|référence|référence simplifiée) *= *harv *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Bot/Requ%C3%AAtes/2020/01#Remplacement_automatique_d%27un_message_d%27erreur_du_mod%C3%A8le_%7B%7BOuvrage%7D%7D
    current_page = re.sub(
        r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *display\-authors *= *etal *([\|}\n]+)', r'{{\1uvrage\2|et al.=oui\3', current_page)
    current_page = re.sub(
        r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *display\-authors *= *[0-9]* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    current_page = re.sub(
        r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *df *= *(?:mdy\-all|dmy\-all)* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # Empty 1=
    current_page = re.sub(
        r'{{ *(a|A)rticle *((?:\|)[^{}]*)\|[ \t]*([\|}]+)', r'{{\1rticle\2\3', current_page)
    current_page = re.sub(
        r'{{ *(l|L)ien web *((?:\|)[^{}]*)\|[ \t]*([\|}]+)', r'{{\1ien web\2\3', current_page)
    # 1= exists: current_page = re.sub(r'{{ *(o|O)uvrage *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1uvrage\2\3', current_page)
    ''' TODO : à vérifier
    while current_page.find('|deadurl=no|') != -1:
        current_page = current_page[:current_page.find('|deadurl=no|')+1] + current_page[current_page.find('|deadurl=no|')+len('|deadurl=no|'):]
    '''

    # TODO: avoid these fixes when: old_template.append('lien mort')
    current_page = current_page.replace('{{lien mortarchive', '{{lien mort archive')
    current_page = current_page.replace('|langue=None', '')
    current_page = current_page.replace('|langue=en|langue=en', '|langue=en')
    current_page = current_page.replace('deadurl=yes', 'brisé le=oui')
    current_page = current_page.replace('brisé le=ja', 'brisé le=oui')
    current_page = current_page.replace('<ref></ref>', '')

    return current_page, summary


def translate_template_parameters(current_template):
    if debug_level > 1:
        print('\ntranslate_template_parameters()')
    for p in range(param_limit):
        if not has_parameter(current_template, old_param[p]):
            continue

        if debug_level > 1:
            print(f'  "{old_param[p]}" found')
        fr_name = new_param[p]

        new_template = remove_parameter_if_empty(
            current_template, old_param[p])
        if new_template != current_template:
            current_template = new_template
            if debug_level > 0:
                print(f'  empty parameter in double removed"{old_param[p]}')
            continue

        if old_param[p] == 'agency':
            if is_template_name_start(current_template, 'article') \
                    and not has_parameter(current_template, 'périodique') \
                    and not has_parameter(current_template, 'work'):
                fr_name = 'périodique'
            else:
                fr_name = 'auteur institutionnel'

        elif old_param[p] == 'editor':
            if has_parameter(current_template, 'éditeur'):
                fr_name = 'auteur'

        elif old_param[p] == 'en ligne le':
            if 'archiveurl' not in current_template and 'archive url' not in current_template \
                    and 'archive-url' not in current_template:
                continue
            elif 'archivedate' in current_template or 'archive date' in current_template \
                    or 'archive-date' in current_template:
                continue
            elif debug_level > 0:
                print('  archive url + archive date')

        elif old_param[p] == 'issue' and has_parameter(current_template, 'numéro'):
            fr_name = 'date'

        elif old_param[p] == 'publisher':
            if (is_template_name_start(current_template, 'article')
                    and not is_template_name_start(current_template, 'article encyclopédique')
                    and not has_parameter(current_template, 'périodique')
                    and not has_parameter(current_template, 'work')):
                fr_name = 'périodique'
            else:
                fr_name = 'éditeur'

        elif old_param[p] == 'script-title':
            if has_parameter(current_template, 'titre'):
                continue
            old_param_value = get_parameter_value(current_template, old_param[p])
            if old_param_value == '':
                continue
            param_values = old_param_value.split(':')
            if len(param_values) != 2:
                continue
            language_parameter = ''
            if not has_parameter(current_template, 'langue') or get_parameter_value(current_template, 'langue') == 'None':
                language_code = param_values[0]
                language_parameter = f'|langue={language_code}'
            title = param_values[1]
            current_template = current_template.replace(old_param_value, title + language_parameter)

        elif old_param[p] == 'type':
            if is_template_name_start(current_template, 'article'):
                fr_name = 'nature article'
            elif is_template_name_start(current_template, 'ouvrage'):
                fr_name = 'nature ouvrage'
            else:
                fr_name = 'type'

        elif old_param[p] == 'website':
            if not is_template_name_start(current_template, 'article') or has_parameter(current_template, 'périodique'):
                fr_name = old_param[p]

        elif old_param[p] == 'work':
            if is_template_name_start(current_template, 'article') and not has_parameter(current_template, 'périodique'):
                fr_name = 'périodique'
            elif is_template_name_start(current_template, 'lien web') and not has_parameter(current_template, 'site') \
                    and not has_parameter(current_template, 'website'):
                fr_name = 'site'
            else:
                fr_name = 'série'

        is_already_present = False
        if new_param[p] != 'langue':  # TODO because "|langue=None" in current_template
            regex = r'(\| *)' + new_param[p] + r'( *=)'
            is_already_present = re.search(regex, current_template)

            # Because "nom" = "nom1"
            if not is_already_present:
                if new_param[p].endswith('1') and not new_param[p].endswith('11'):
                    new_param_alias = new_param[p].replace('1', '')
                else:
                    new_param_alias = new_param[p] + '1'
                regex = r'(\| *)' + new_param_alias + r'( *=)'
                is_already_present = re.search(regex, current_template)

        if is_already_present:
            # Remove double if value is the same
            old_param_value = get_parameter_value(current_template, old_param[p])
            new_param_value = get_parameter_value(current_template, fr_name)
            if debug_level > 0:
                print(f'  "{old_param[p]}" has double, value:')
                print(f'   {old_param_value}')
                print(f'  "{fr_name}" value:')
                print(f'   {new_param_value}')
            # Nested templates engenders a false empty value for now
            if old_param_value == new_param_value and old_param_value != '':
                regex = r'(\| *)' + re.escape(old_param[p]) + r'( *=[^\|}\[]*)([\|}])'
                current_template = re.sub(regex, r'\3', current_template)
                # TODO choose the best double value. Ex: keep only the last date between doubles "access-date" and "consulté le"
        else:
            # TODO change "editor1" behavior along with "editor1-last"?
            # if old_param[p] != 'editor' and old_param[p].startswith('editor'):
            #     param_number = re.search(r'(\d+)', old_param[p])
            #     if param_number:
            #         fr_name = '|directeur' + param_number[0] + '=oui |' + fr_name

            regex = r'(\| *)' + re.escape(old_param[p]) + r'( *=)'
            current_template = re.sub(regex, r'\1' + fr_name + r'\2', current_template)

    current_template = current_template.replace('|=', u'|')
    current_template = current_template.replace('| =', u'|')
    current_template = current_template.replace('|  =', u'|')
    current_template = current_template.replace('|}}', u'}}')
    current_template = current_template.replace('| }}', u'}}')
    has_included_template = current_template.find('{{') != -1
    if not has_included_template and '{{date' not in current_template:
        current_template = current_template.replace('||', u'|')

    return current_template


def translate_link_templates(current_page):
    for i in range(templates_limit):
        if i <= translated_templates_limit:
            current_page = format_old_link_template(current_page, old_templates[i])
        current_page = translate_link_template(current_page, old_templates[i], new_templates[i])

    return current_page


def format_old_link_template(current_page, old_template):
    if debug_level > 1:
        print(f' translate_old_link_template: {old_template}')

    if old_template != 'cite':
        current_page = current_page.replace(
            '{{' + old_template.replace(' ', '_') + ' ', '{{' + old_template + '')
        current_page = current_page.replace(
            '{{' + old_template + ' ', '{{' + old_template + '')

    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]).replace(' ', '_') + r' *\|', old_template + r'|', current_page)
    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]).replace(' ', '  ') + r' *\|', old_template + r'|', current_page)
    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]) + r' *\|', old_template + r'|', current_page)

    final_page = ''
    regex = r'[^}]*lang(ue|uage)* *=[^}]*}}'
    while re.search(r'{{[\n ]*' + old_template + r' *[|\n]+', current_page):
        template_end = re.search(
            r'{{[\n ]*' + old_template + r' *[|\n]', current_page).end() - 1
        if debug_level > 1:
            print(current_page[template_end:][:100])

        final_page = final_page + current_page[:template_end]
        final_page, language_code = get_template_language_from_template_page(
            final_page)
        current_page = current_page[template_end:]

        if not re.search(regex, current_page) or re.search(regex, current_page).end() > current_page.find('}}') + 2:
            current_page = f'|langue={language_code}{current_page}'

    current_page = final_page + current_page

    return current_page


def translate_link_template(current_page, old_template, new_template):
    if debug_level > 1:
        print(f' translate_link_template: {old_template}')

    current_page = re.sub(r'({{[\n ]*)[' + old_template[:1] + r'|' + old_template[:1].upper() + r']'
                          + old_template[1:] + r'( *[|\n\t}])', r'\1' + new_template + r'\2', current_page)

    # Delete empty templates
    regex = r'{{ *[' + new_template[:1] + r'|' + new_template[:1].upper() + r']' \
            + new_template[1:] + r' *}}'
    while re.search(regex, current_page):
        current_page = current_page[:re.search(regex, current_page).start()] \
            + current_page[re.search(regex, current_page).end():]

    # Translate parameters
    regex = r'{{ *[' + new_template[:1].lower() + new_template[:1].upper() + r']' + new_template[1:] \
            + r' *[\|\n{}]'
    final_page = ''
    while re.search(regex, current_page):
        final_page = final_page + \
            current_page[:re.search(regex, current_page).start() + 2]
        current_page = current_page[re.search(
            regex, current_page).start() + 2:]
        current_template, template_end_position = get_current_link_template(
            current_page)
        current_page = translate_template_parameters(
            current_template) + current_page[template_end_position:]
        # TODO stop looping several times on the same template (template_end_position stays the same)
    current_page = final_page + current_page

    return current_page


def get_template_language_from_template_page(final_page):
    # Ex: {{de}} {{cite news|...
    language_code = ''
    if '{{' in final_page:
        page_start_without_current_template = final_page[:final_page.rfind(
            '{{')]
        regex_get_last_template = r'{{([a-z]{2})}} *$'
        s = re.search(regex_get_last_template,
                      page_start_without_current_template, re.IGNORECASE)
        if s:
            language_code = page_start_without_current_template[s.start(
            ):s.end()]
            language_code = language_code.replace('{{', '').replace('}}', '')
            final_page = re.sub(regex_get_last_template, '', page_start_without_current_template) \
                + final_page[final_page.rfind('{{'):]
    if language_code == '':
        language_code = 'None'
    if debug_level > 0:
        print(f' language to add to template: {language_code}')
    return final_page, language_code


def get_valid_language_code(language_code):
    if site.family in ['wikipedia', 'wiktionary']:
        if language_code.find('}}') != -1:
            language_code = language_code[:language_code.find('}}')]
        if debug_level > 1:
            print(f' Template:{language_code}')
        template_page = Page(site, f'Template:{language_code}')
        template_page_content = ''
        try:
            template_page_content = template_page.get()
        except pywikibot.exceptions.NoPageError as e:
            print(e)
        except pywikibot.exceptions.LockedPageError as e:
            print(e)
        except pywikibot.exceptions.IsRedirectPageError as e:
            template_page_content = template_page.get(get_redirect=True)
        if debug_level > 1:
            print(template_page_content)
    return language_code


def translate_dates(current_page):
    if debug_level > 1:
        print('\ntranslate_dates()')
    date_parameters = ['date', 'mois', 'consulté le', 'en ligne le', 'dts', 'Dts', 'date triable', 'Date triable']
    for m in range(1, month_line + 1):
        if debug_level > 1:
            print(f'Month {str(m)}')
            print(months_translations[m][1])
        for p in range(1, len(date_parameters)):
            if debug_level > 1:
                print('Recherche de ' + date_parameters[p] + ' *=[ ,0-9]*)' + months_translations[m][1])
            if p > 4:
                current_page = re.sub(
                    r'({{ *' + date_parameters[p] + r'[^}]+)' + months_translations[m][1] + r'([^}]+}})',
                    r'\1' + months_translations[m][2] + r'\2',
                    current_page)
                current_page = re.sub(
                    r'({{ *' + date_parameters[p] + r'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' +
                    months_translations[m][2] + r'(\|[ 0-9][ 0-9])}}', r'\1\3|' + months_translations[m][2] + r'\2}}',
                    current_page)
            else:
                current_page = re.sub(
                    r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][1] +
                    r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' + months_translations[m][2] + r'\2',
                    current_page)
                current_page = re.sub(
                    r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][1][:1].lower() +
                    months_translations[m][1][1:] + r'([ ,0-9]*\.? *[<|\||\n\t|}])',
                    r'\1' + months_translations[m][2] + r'\2',
                    current_page)

                # TODO Date order: jj mm aaaa
                if debug_level > 1:
                    regex = (r'(\| *' + date_parameters[p] + r' *= *)' + months_translations[m][2] +
                             r' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])')
                    print('Recherche de ' + regex)
                    current_page = re.sub(
                        regex,
                        r'\1' + r'\2' + r' ' +  months_translations[m][2] + r' ' + r'\3' + r'\4',
                        current_page)  # trim('\3') does not work

                # TODO print('Recherche de ' + date_parameters[p] + ' *= *' + months_translations[m][1] + '[ ,0-9]*')

    return current_page


def translate_languages(current_page):
    if debug_level > 0:
        print('\ntranslate_languages()')
    for l in range(1, languages_line + 1):
        if debug_level > 1:
            print(f'Langue {str(l)}')
            print(languages_translations[l][1])
        current_page = re.sub(r'(\| *langue *= *)' + languages_translations[l][1] + r'( *[<|\||\n\t|}])',
                              r'\1' + languages_translations[l][2] + r'\2', current_page)

        # TODO rustine suite à un imprévu censé être réglé ci-dessus, mais qui touche presque 10 % des pages.
        current_page = re.sub(
            r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Aa]rticle\|langue=' + languages_translations[l][
                2] + r'\|)', r'\1', current_page)
        current_page = re.sub(
            r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Ll]ien web\|langue=' + languages_translations[l][
                2] + r'\|)', r'\1', current_page)
        current_page = re.sub(
            r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Oo]uvrage\|langue=' + languages_translations[l][
                2] + r'\|)', r'\1', current_page)

    return current_page


def translate_access(current_page):
    if debug_level > 0:
        print('\ntranslate_access()')
    for l in range(1, access_line + 1):
        if debug_level > 1:
            print(f'Access {str(l)}')
            print(access_translations[l][1])
        current_page = re.sub(r'(\| *accès (?:url|doi|hdl) *= *)' + access_translations[l][1] + r'( *[<|\||\n\t|}])',
                              r'\1' + access_translations[l][2] + r'\2', current_page)

        # TODO rustine suite à un imprévu censé être réglé ci-dessus, mais qui touche presque 10 % des pages.
        current_page = re.sub(
            r'{{' + access_translations[l][2] + r'}}[ \n]*({{[Aa]rticle\|langue=' + access_translations[l][
                2] + r'\|)', r'\1', current_page)
        current_page = re.sub(
            r'{{' + access_translations[l][2] + r'}}[ \n]*({{[Ll]ien web\|langue=' + access_translations[l][
                2] + r'\|)', r'\1', current_page)
        current_page = re.sub(
            r'{{' + access_translations[l][2] + r'}}[ \n]*({{[Oo]uvrage\|langue=' + access_translations[l][
                2] + r'\|)', r'\1', current_page)

    return current_page


def get_current_link_template(current_page):
    # Extraction du modèle de lien en tenant compte des modèles inclus dedans
    current_page2 = current_page
    template_end_position = 0
    while current_page2.find('{{') != -1 and current_page2.find('{{') < current_page2.find('}}'):
        template_end_position = template_end_position + \
            current_page.find('}}')+2
        current_page2 = current_page2[current_page2.find('}}')+2:]
    template_end_position = template_end_position + current_page2.find('}}')+2
    current_template = current_page[:template_end_position]

    if debug_level > 1:
        print('\nget_current_link_template()')
        print(template_end_position)
        input(current_template)

    return current_template, template_end_position

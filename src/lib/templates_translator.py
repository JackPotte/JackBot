#!/usr/bin/env python
# coding: utf-8
"""
Ce script traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}})
cf http://www.tradino.org/
"""

from __future__ import absolute_import, unicode_literals
import re
import pywikibot
from pywikibot import *
from page_functions import *

do_check_url = False

# Modèles qui incluent des URL dans leurs paramètres
old_templates = []
new_templates = []
old_templates.append('cite web')
new_templates.append('lien web')
old_templates.append('citeweb')
new_templates.append('lien web')
old_templates.append('cite news')
new_templates.append('article')
old_templates.append('citenews')
new_templates.append('article')
old_templates.append('cite journal')
new_templates.append('article')
old_templates.append('cite magazine')
new_templates.append('article')
old_templates.append('cite newspaper')
new_templates.append('article')
old_templates.append('lien news')
new_templates.append('article')
old_templates.append('cite video')
new_templates.append('lien vidéo')
old_templates.append('cite episode')
new_templates.append('citation épisode')
old_templates.append('cite arXiv')
new_templates.append('lien arXiv')
old_templates.append('cite press release')
new_templates.append('lien web')
old_templates.append('cite pr')
new_templates.append('lien web')
old_templates.append('web site')
new_templates.append('lien web')
old_templates.append('cite conference')
new_templates.append('lien conférence')
old_templates.append('docu')
new_templates.append('lien vidéo')
old_templates.append('cite book')
new_templates.append('ouvrage')
old_templates.append('cite Book')
new_templates.append('ouvrage')
old_templates.append('cite')
new_templates.append('ouvrage')
old_templates.append('cite encyclopedia')
new_templates.append('article encyclopédique')
# es
old_templates.append('cita noticia')
new_templates.append('article')
old_templates.append('cita web')
new_templates.append('lien web')
# it
old_templates.append('cita pubblicazione')
new_templates.append('article')
old_templates.append('cita libro')
new_templates.append('ouvrage')
# sv
old_templates.append('webbref')
new_templates.append('lien web')
# de
old_templates.append('internetquelle')
new_templates.append('lien web')
translated_templates_limit = len(new_templates)

# Modèle avec alias français
old_templates.append('deadlink')
new_templates.append('lien brisé')
# old_template.append('dead link') TODO: if previous template is {{lien brisé}} then remove else replace
# new_template.append('lien brisé')
old_templates.append('webarchive')
new_templates.append('lien brisé')
old_templates.append('lien brise')
new_templates.append('lien brisé')
old_templates.append('lien cassé')
new_templates.append('lien brisé')
old_templates.append('lien mort')
new_templates.append('lien brisé')
old_templates.append('lien web brisé')
new_templates.append('lien brisé')
old_templates.append('lien Web')
new_templates.append('lien web')
old_templates.append('site web')
new_templates.append('lien web')
old_templates.append('périodique')
new_templates.append('article')
old_templates.append('quote')
new_templates.append('citation bloc')

# Modèles pour traduire leurs paramètres uniquement
old_templates.append('lire en ligne')
new_templates.append('lire en ligne')
old_templates.append('dts')
new_templates.append('dts')
old_templates.append('Chapitre')
new_templates.append('Chapitre')
templates_limit = len(new_templates)

# Paramètres à remplacer
old_param = []
new_param = []
old_param.append('author')
new_param.append('auteur')
old_param.append('authorlink1')
new_param.append('lien auteur1')
old_param.append('title')
new_param.append('titre')
old_param.append('publisher')
new_param.append('éditeur')
old_param.append('work')  # TODO write here those parameters, translated differently between {{lien web}} & {{article}}
new_param.append('périodique')
old_param.append('newspaper')
new_param.append('journal')
old_param.append('day')
new_param.append('jour')
old_param.append('month')
new_param.append('mois')
old_param.append('year')
new_param.append('année')
old_param.append('accessdate')
new_param.append('consulté le')
old_param.append('access-date')
new_param.append('consulté le')
old_param.append('language')
new_param.append('langue')
old_param.append('lang')
new_param.append('langue')
old_param.append('quote')
new_param.append('extrait')
old_param.append('titre vo')
new_param.append('titre original')
old_param.append('first')
new_param.append('prénom')
old_param.append('surname')
new_param.append('nom')
old_param.append('last')
new_param.append('nom')
for p in range(1, 100):
    old_param.append('first' + str(p))
    new_param.append('prénom' + str(p))
    old_param.append('given' + str(p))
    new_param.append('prénom' + str(p))
    old_param.append('last' + str(p))
    new_param.append('nom' + str(p))
    old_param.append('surname' + str(p))
    new_param.append('nom' + str(p))
    old_param.append('author' + str(p))
    new_param.append('auteur' + str(p))
old_param.append('issue')
new_param.append('numéro')
old_param.append('authorlink')
new_param.append('lien auteur')
old_param.append('author-link')
new_param.append('lien auteur')
for p in range(1, 100):
    old_param.append('authorlink' + str(p))
    new_param.append('lien auteur' + str(p))
    old_param.append('author' + str(p) + 'link')
    new_param.append('lien auteur' + str(p))
old_param.append('coauthorlink')
new_param.append('lien coauteur')
old_param.append('coauthor-link')
new_param.append('lien coauteur')
old_param.append('surname1')
new_param.append('nom1')
old_param.append('coauthors')
new_param.append('coauteurs')
old_param.append('co-auteurs')
new_param.append('coauteurs')
old_param.append('co-auteur')
new_param.append('coauteur')
old_param.append('given')
new_param.append('prénom')
old_param.append('trad')
new_param.append('traducteur')
old_param.append('at')
new_param.append('passage')
old_param.append('origyear')
new_param.append('année première édition')  # TODO "année première impression" on sister projects
old_param.append('année première impression')
new_param.append('année première édition')
old_param.append('location')
new_param.append('lieu')
old_param.append('place')
new_param.append('lieu')
old_param.append('publication-date')
new_param.append('année')
old_param.append('writers')
new_param.append('scénario')
old_param.append('episodelink')
new_param.append('lien épisode')
old_param.append('serieslink')
new_param.append('lien série')
old_param.append('titlelink')
new_param.append('lien titre')
old_param.append('credits')
new_param.append('crédits')
old_param.append('network')
new_param.append('réseau')
old_param.append('station')
new_param.append('chaîne')
old_param.append('city')
new_param.append('ville')
old_param.append('began')
new_param.append('début')
old_param.append('ended')
new_param.append('fin')
old_param.append('airdate')
new_param.append('diffusion')
old_param.append('number')
new_param.append('numéro')
old_param.append('season')
new_param.append('saison')
old_param.append('year2')
new_param.append('année2')
old_param.append('month2')
new_param.append('mois2')
old_param.append('time')
new_param.append('temps')
old_param.append('accessyear')
new_param.append('année accès')
old_param.append('accessmonth')
new_param.append('mois accès')
old_param.append('conference')
new_param.append('conférence')
old_param.append('conferenceurl')
new_param.append('urlconférence')
old_param.append('booktitle')
new_param.append('titre livre')
old_param.append('others')
new_param.append('champ libre')
old_param.append('type')
new_param.append('nature ouvrage')
old_param.append('edition')
new_param.append('numéro d\'édition')
old_param.append('website')
new_param.append('périodique')
old_param.append('pp')
new_param.append('passage')

# Fix
old_param.append('en ligne le')
new_param.append('archivedate')
old_param.append('autres')
new_param.append('champ libre')
old_param.append('Auteur')
new_param.append('auteur')
old_param.append('auteur-')
new_param.append('auteur')
old_param.append('editor')
new_param.append('éditeur')
old_param.append('editor2')
new_param.append('auteur2')

# de
old_param.append('werk')
new_param.append('périodique')
old_param.append('titel')
new_param.append('titre')
old_param.append('TitelErg')
new_param.append('sous-titre')
old_param.append('titelerg')
new_param.append('sous-titre')
old_param.append('hrsg')
new_param.append('éditeur')
old_param.append('offline')
new_param.append('brisé le')
old_param.append('zugriff')
new_param.append('consulté le')
old_param.append('abruf')
new_param.append('consulté le')
old_param.append('archiv-url')
new_param.append('archiveurl')
old_param.append('archiv-datum')
new_param.append('archivedate')
old_param.append('autor')
new_param.append('auteur')
old_param.append('datum')
new_param.append('date')
old_param.append('datum-jahr')
new_param.append('année')
old_param.append('datum-monat')
new_param.append('mois')
old_param.append('datum-tag')
new_param.append('jour')
old_param.append('sprache')
new_param.append('langue')
old_param.append('seiten')
new_param.append('pages')
old_param.append('zitat')
new_param.append('citation')  # "extrait" ailleurs
old_param.append('kommentar')
new_param.append('description')

# es
old_param.append('autor')
new_param.append('auteur')
old_param.append('título')
new_param.append('titre')
old_param.append('fechaacceso')
new_param.append('consulté le')
old_param.append('fecha')
new_param.append('date')
old_param.append('obra')
new_param.append('série')
old_param.append('idioma')
new_param.append('langue')
old_param.append('publicació')
new_param.append('éditeur')
old_param.append('editorial')
new_param.append('journal')
old_param.append('series')
new_param.append('collection')
old_param.append('agency')
new_param.append('auteur institutionnel')  # TODO write here the alternatives when absent ("périodique")
old_param.append('magazine')
new_param.append('périodique')

# it
old_param.append('autore')
new_param.append('auteur')
old_param.append('titolo')
new_param.append('titre')
old_param.append('accesso')
new_param.append('consulté le')
old_param.append('data')
new_param.append('date')
old_param.append('nome')
new_param.append('prénom')
old_param.append('cognome')
new_param.append('nom')
old_param.append('linkautore')
new_param.append('lien auteur')
old_param.append('coautori')
new_param.append('coauteurs')
old_param.append('rivista')
new_param.append('journal')
old_param.append('giorno')
new_param.append('jour')
old_param.append('mese')
new_param.append('mois')
old_param.append('anno')
new_param.append('année')
old_param.append('pagine')
new_param.append('page')
old_param.append('editore')
new_param.append('éditeur')

# sv
old_param.append('författar')
new_param.append('auteur')
old_param.append('titel')
new_param.append('titre')
old_param.append('hämtdatum')
new_param.append('consulté le')
old_param.append('datum')
new_param.append('date')
old_param.append('förnamn')
new_param.append('prénom')
old_param.append('efternamn')
new_param.append('nom')
old_param.append('författarlänk')
new_param.append('lien auteur')
old_param.append('utgivare')
new_param.append('éditeur')
old_param.append('månad')
new_param.append('mois')
old_param.append('år')
new_param.append('année')
old_param.append('sida')
new_param.append('page')
old_param.append('verk')
new_param.append('périodique')

param_limit = len(old_param)
if param_limit != len(new_param):
    input('Fatal error: unbalanced new and old parameters')

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
languages_translations = [[0] * (languages_column + 1) for _ in range(languages_line + 1)]
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


def set_globals_translator(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


def translate_templates(current_page, summary):
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

    # Paramètres inutiles
    current_page = re.sub(r'{{ *Références *\| *colonnes *= *}}', r'{{Références}}', current_page)
    # Dans {{article}}, "éditeur" vide bloque "périodique", "journal" ou "revue"
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\||\n)[^{}]*)\| *éditeur *= *([\||}|\n]+)', r'{{\1rticle\2\3', current_page)
    # https://fr.wikipedia.org/w/index.php?title=Discussion_utilisateur:JackPotte&oldid=prev&diff=165491794#Suggestion_pour_JackBot_:_Signalement_param%C3%A8tre_obligatoire_manquant_+_Lien_web_vs_Article
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *(?:ref|référence|référence simplifiée) *= *harv *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Bot/Requ%C3%AAtes/2020/01#Remplacement_automatique_d%27un_message_d%27erreur_du_mod%C3%A8le_%7B%7BOuvrage%7D%7D
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *display\-authors *= *etal *([\|}\n]+)', r'{{\1uvrage\2|et al.=oui\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *display\-authors *= *[0-9]* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^{}]*)\| *df *= *(?:mdy\-all|dmy\-all)* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # Empty 1=
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\|)[^{}]*)\|[ \t]*([\|}]+)', r'{{\1rticle\2\3', current_page)
    current_page = re.sub(r'{{ *(l|L)ien web *((?:\|)[^{}]*)\|[ \t]*([\|}]+)', r'{{\1ien web\2\3', current_page)
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
    if debug_level > 0:
        print('\ntranslate_template_parameters()')
    for p in range(0, param_limit):
        if not has_parameter(current_template, old_param[p]):
            continue

        if debug_level > 0:
            print('  "' + old_param[p] + '" found')
        fr_name = new_param[p]

        new_template = remove_parameter_if_empty(current_template, old_param[p])
        if new_template != current_template:
            current_template = new_template
            if debug_level > 0:
                print('  empty parameter in double removed"' + old_param[p])
            continue

        if old_param[p] == 'agency':
            if is_template_name(current_template, 'article') and not has_parameter(current_template, 'périodique') \
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
            if is_template_name(current_template, 'article') and not has_parameter(current_template, 'périodique') \
                    and not has_parameter(current_template, 'work'):
                fr_name = 'périodique'
            else:
                fr_name = 'éditeur'

        elif old_param[p] == 'type':
            if is_template_name(current_template, 'article'):
                fr_name = 'nature article'
            elif is_template_name(current_template, 'ouvrage'):
                fr_name = 'nature ouvrage'
            else:
                fr_name = 'type'

        elif old_param[p] == 'website':
            if not (is_template_name(current_template, 'article') and not has_parameter(current_template, 'périodique')):
                fr_name = old_param[p]

        elif old_param[p] == 'work':
            if is_template_name(current_template, 'article') and not has_parameter(current_template, 'périodique'):
                fr_name = 'périodique'
            elif is_template_name(current_template, 'lien web') and not has_parameter(current_template, 'site') \
                    and not has_parameter(current_template, 'website'):
                fr_name = 'site'
            else:
                fr_name = 'série'

        is_already_present = False
        if new_param[p] != 'langue':  # TODO because "|langue=None" in current_template
            regex = r'(\| *)' + new_param[p] + r'( *=)'
            is_already_present = re.search(regex, current_template)

        if is_already_present:
            # Remove double if value is the same
            old_param_value = get_parameter_value(current_template, old_param[p])
            new_param_value = get_parameter_value(current_template, fr_name)
            if debug_level > 0:
                print('  "' + old_param[p] + '" has double, value:')
                print('   ' + old_param_value)
                print('  "' + fr_name + '" value:')
                print('   ' + new_param_value)
            # Nested templates engenders a false empty value for now
            if old_param_value == new_param_value and old_param_value != '':
                regex = r'(\| *)' + old_param[p] + r'( *=[^\|}]*)([\|}])'
                current_template = re.sub(regex, r'\3', current_template)
        else:
            regex = r'(\| *)' + old_param[p] + r'( *=)'
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
    for m in range(0, templates_limit):
        if m <= translated_templates_limit:
            current_page = format_old_link_template(current_page, old_templates[m])
        current_page = translate_link_template(current_page, old_templates[m], new_templates[m])

    return current_page


def format_old_link_template(current_page, old_template):
    if debug_level > 1:
        print(' translate_old_link_template: ' + old_template)

    if 'cite' != old_template:
        current_page = current_page.replace('{{' + old_template.replace(' ', '_') + ' ', '{{' + old_template + '')
        current_page = current_page.replace('{{' + old_template + ' ', '{{' + old_template + '')

    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]).replace(' ', '_') + r' *\|', old_template + r'|', current_page)
    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]).replace(' ', '  ') + r' *\|', old_template + r'|', current_page)
    current_page = re.sub((r'(Modèle:)?[' + old_template[:1] + r'|' + old_template[:1].upper() + r']' +
                           old_template[1:]) + r' *\|', old_template + r'|', current_page)

    final_page = ''
    while re.search(r'{{[\n ]*' + old_template + r' *[|\n]+', current_page):
        template_end = re.search(r'{{[\n ]*' + old_template + r' *[|\n]', current_page).end() - 1
        if debug_level > 1:
            print(current_page[template_end:][:100])

        final_page = final_page + current_page[:template_end]
        final_page, language_code = get_template_language_from_template_page(final_page)
        current_page = current_page[template_end:]

        regex = r'[^}]*lang(ue|uage)* *=[^}]*}}'
        if not re.search(regex, current_page) or re.search(regex, current_page).end() > current_page.find('}}') + 2:
            current_page = '|langue=' + language_code + current_page

    current_page = final_page + current_page

    return current_page


def translate_link_template(current_page, old_template, new_template):
    if debug_level > 1:
        print(' translate_link_template: ' + old_template)

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
        final_page = final_page + current_page[:re.search(regex, current_page).start() + 2]
        current_page = current_page[re.search(regex, current_page).start() + 2:]
        current_template, template_end_position = get_current_link_template(current_page)
        current_page = translate_template_parameters(current_template) + current_page[template_end_position:]
        # TODO stop looping several times on the same template (template_end_position stays the same)
    current_page = final_page + current_page

    return current_page


def get_template_language_from_template_page(final_page):
    # Ex: {{de}} {{cite news|...
    language_code = ''
    if '{{' in final_page:
        page_start_without_current_template = final_page[:final_page.rfind('{{')]
        regex_get_last_template = r'{{([a-z]{2})}} *$'
        s = re.search(regex_get_last_template, page_start_without_current_template, re.IGNORECASE)
        if s:
            language_code = page_start_without_current_template[s.start():s.end()]
            language_code = language_code.replace('{{', '').replace('}}', '')
            final_page = re.sub(regex_get_last_template, '', page_start_without_current_template) \
                         + final_page[final_page.rfind('{{'):]
            # TODO language_code = get_valid_language_code(language_code)

    if language_code == '':
        language_code = 'None'
    if debug_level > 0:
        print(' language to add to template: ' + language_code)
    return final_page, language_code


def get_valid_language_code(language_code):
    if site.family in ['wikipedia', 'wiktionary']:
        if language_code.find('}}') != -1:
            language_code = language_code[:language_code.find('}}')]
        if debug_level > 1:
            print(' Template:' + language_code)
        template_page = Page(site, 'Template:' + language_code)
        template_page_content = ''
        try:
            template_page_content = template_page.get()
        except pywikibot.exceptions.NoPageError as e:
            print(str(e))
        except pywikibot.exceptions.LockedPageError as e:
            print(str(e))
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
            print('Mois ' + str(m))
            print(months_translations[m][1])
        for p in range(1, len(date_parameters)):
            if debug_level > 1:
                print('Recherche de ') + date_parameters[p] + ' *=[ ,0-9]*' + months_translations[m][1]
            if p > 4:
                current_page = re.sub(
                    r'({{ *' + date_parameters[p] + r'[^}]+)' + months_translations[m][1] + r'([^}]+}})',
                    r'\1' + months_translations[m][2] + r'\2', current_page)
                current_page = re.sub(
                    r'({{ *' + date_parameters[p] + r'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' + months_translations[m][
                        2] + r'(\|[ 0-9][ 0-9])}}', r'\1\3|' + months_translations[m][2] + r'\2}}', current_page)
            else:
                current_page = re.sub(r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][
                    1] + r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' + months_translations[m][2] + r'\2', current_page)
                current_page = re.sub(
                    r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][1][:1].lower() +
                    months_translations[m][1][1:] + r'([ ,0-9]*\.? *[<|\||\n\t|}])',
                    r'\1' + months_translations[m][2] + r'\2', current_page)

                # Ordre des dates : jj mois aaaa
                if debug_level > 1: print('Recherche de ') + date_parameters[p] + ' *= *' + months_translations[m][
                    2] + ' *([0-9]+), '
                current_page = re.sub(r'(\| *' + date_parameters[p] + ' *= *)' + months_translations[m][
                    2] + r' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])',
                                      r'\1' + r'\2' + r' ' + months_translations[m][2] + r' ' + r'\3' + r'\4',
                                      current_page)  # trim('\3') ne fonctionne pas

    return current_page


def translate_languages(current_page):
    if debug_level > 0:
        print('\ntranslate_languages()')
    for l in range(1, languages_line + 1):
        if debug_level > 1:
            print('Langue ') + str(l)
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


def get_current_link_template(current_page):
    # Extraction du modèle de lien en tenant compte des modèles inclus dedans
    current_page2 = current_page
    template_end_position = 0
    while current_page2.find('{{') != -1 and current_page2.find('{{') < current_page2.find('}}'):
        template_end_position = template_end_position + current_page.find('}}')+2
        current_page2 = current_page2[current_page2.find('}}')+2:]
    template_end_position = template_end_position + current_page2.find('}}')+2
    current_template = current_page[:template_end_position]

    if debug_level > 1:
        print('\nget_current_link_template()')
        print(template_end_position)
        input(current_template)

    return current_template, template_end_position

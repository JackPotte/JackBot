#!/usr/bin/env python
# coding: utf-8
"""
Ce script traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}}) cf http://www.tradino.org/
Optionellement, il vérifie toutes les URL des articles de la forme http://, https:// et [// ou incluses dans certains modèles
(pas tous étant donnée leur complexité, car certains incluent des {{{1}}} et {{{2}}} dans leurs URL)

TODO: split in two modules, check and translate
"""

from __future__ import absolute_import, unicode_literals
import re
import ssl
import urllib
import webbrowser
import requests
import pywikibot
from pywikibot import *
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
try:
    import http.client as httplib
except ImportError:
    import httplib
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
try:
    import http.cookiejar as cookielib
except ImportError:
    import cookielib
try:
    from src.lib import *
except ImportError:
    from lib import *

debug_level = 0
username = 'JackBot'
site = pywikibot.Site('fr', 'wiktionary')


# *** General functions ***
def setGlobalsHL(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


is_semi_auto = False
do_retest_broken_links = False
check_url = False

broken_domains = []
# broken_domains.append('marianne2.fr')  # Site remplacé par marianne.net en mai 2017

blocked_domains = []  # à cause des popovers ou Node.js ?
blocked_domains.append('bbc.co.uk')
blocked_domains.append('biodiversitylibrary.org')
blocked_domains.append('charts.fi')
blocked_domains.append('cia.gov')
blocked_domains.append('finnishcharts.com')
blocked_domains.append('history.navy.mil') # IP Free bloquée en lecture
blocked_domains.append('itunes.apple.com')
blocked_domains.append('nytimes.com')
blocked_domains.append('psaworldtour.com')
blocked_domains.append('rottentomatoes.com')
blocked_domains.append('soundcloud.com')
blocked_domains.append('twitter.com')
blocked_domains.append('w-siberia.ru')

authorized_files = []
authorized_files.append('.pdf')

templates_with_url_line = 4
templates_with_url_column = 2
templates_with_url = [[0] * (templates_with_url_column + 1) for _ in range(templates_with_url_line + 1)]
templates_with_url[1][1] = 'Import:DAF8'
templates_with_url[1][2] = 'http://www.cnrtl.fr/definition/academie8/'
templates_with_url[2][1] = 'R:DAF8'
templates_with_url[2][2] = 'http://www.cnrtl.fr/definition/academie8/'
templates_with_url[3][1] = 'Import:Littré'
templates_with_url[3][2] = 'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='
templates_with_url[4][1] = 'R:Littré'
templates_with_url[4][2] = 'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='

# Modèles qui incluent des URL dans leurs paramètres
old_template = []
new_template = []
old_template.append('cite web')
new_template.append('lien web')
old_template.append('citeweb')
new_template.append('lien web')
old_template.append('cite news')
new_template.append('article')
old_template.append('cite journal')
new_template.append('article')
old_template.append('cite magazine')
new_template.append('article')
old_template.append('lien news')
new_template.append('article')
old_template.append('cite video')
new_template.append('lien vidéo')
old_template.append('cite episode')
new_template.append('citation épisode')
old_template.append('cite arXiv')
new_template.append('lien arXiv')
old_template.append('cite press release')
new_template.append('lien web')
old_template.append('cite press_release')
new_template.append('lien web')
old_template.append('cite conference')
new_template.append('lien conférence')
old_template.append('docu')
new_template.append('lien vidéo')
old_template.append('cite book')
new_template.append('ouvrage')
# old_template.append('cite')
# new_template.append('ouvrage')
# it
old_template.append('cita pubblicazione')
new_template.append('article')
old_template.append('cita libro')
new_template.append('ouvrage')
# sv
old_template.append('webbref')
new_template.append('lien web')
# de
old_template.append('internetquelle')
new_template.append('lien web')
translated_templates_limit = len(new_template)

# Modèle avec alias français
old_template.append('deadlink')
new_template.append('lien brisé')
# old_template.append('dead link') TODO: if previous template is {{lien brisé}} then remove else replace
# new_template.append('lien brisé')
old_template.append('webarchive')
new_template.append('lien brisé')
old_template.append('lien brise')
new_template.append('lien brisé')
old_template.append('lien cassé')
new_template.append('lien brisé')
old_template.append('lien mort')
new_template.append('lien brisé')
old_template.append('lien web brisé')
new_template.append('lien brisé')
old_template.append('lien Web')
new_template.append('lien web')
old_template.append('cita web')
new_template.append('lien web')
old_template.append('cita noticia')
new_template.append('lien news')
old_template.append('web site')
new_template.append('lien web')
old_template.append('site web')
new_template.append('lien web')
old_template.append('périodique')
new_template.append('article')
old_template.append('quote')
new_template.append('citation bloc')

# Modèles pour traduire leurs paramètres uniquement
old_template.append('lire en ligne')
new_template.append('lire en ligne')
old_template.append('dts')
new_template.append('dts')
old_template.append('Chapitre')
new_template.append('Chapitre')
templates_limit = len(new_template)

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
new_param.append('nom')
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

url_to_replace = ['athena.unige.ch/athena', 'un2sg4.unige.ch/athena']
url_to_replace_limit = len(url_to_replace)

# http://tools.ietf.org/html/rfc3986
# http://fr.wiktionary.org/wiki/Annexe:Titres_non_pris_en_charge
url_ends = [' ', '\n', '[', ']', '{', '}', '<', '>', '|', '^', '\\', '`', '"']
# url_ends.append('~'    # dans 1ère RFC seulement
url_limit = len(url_ends)
# Caractères qui ne peuvent pas être en dernière position d'une URL :
url_ends2 = ['.', ',', ';', '!', '?', ')', u"'"]
url_limit2 = len(url_ends2)

tag_line = 6
tag_column = 2
tags_without_url = [[0] * (tag_column + 1) for _ in range(tag_line + 1)]
tags_without_url[1][1] = '<pre>'
tags_without_url[1][2] = '</pre>'
tags_without_url[2][1] = '<nowiki>'
tags_without_url[2][2] = '</nowiki>'
tags_without_url[3][1] = '<ref name='
tags_without_url[3][2] = '>'
tags_without_url[4][1] = '<rdf'
tags_without_url[4][2] = '>'
tags_without_url[5][1] = '<source'
tags_without_url[5][2] = '</source' + '>'
tags_without_url[6][1] = '\n '
tags_without_url[6][2] = '\n'
'''
TODO '<!--' '-->'?
'''

broken_link_templates = []
if not do_retest_broken_links:
    broken_link_templates.append('lien brisé')

sites_errors = ["403 Forbidden", "404 – File not found", "404 error", "404 Not Found", "404. That’s an error.",
          "Error 404 - Not found", "Error 404 (Not Found)", "Error 503 (Server Error)", "page_content not found",
          "Runtime Error", "server timedout", "Sorry, no matching records for query",
          "The page you requested cannot be found", "this page can't be found",
          "The service you requested is not available at this time", "There is currently no text in this page.",
          "500 Internal Server Error", "Cette forme est introuvable !", "Soit vous avez mal &#233;crit le titre",
          'Soit vous avez mal écrit le titre', 'Terme introuvable', "nom de domaine demandé n'est plus actif",
          "Il n'y a pour l'instant aucun texte sur cette page."]
errors_limit = len(sites_errors)

# Too large media to ignore
large_media = ['RIFF', 'WAV', 'BWF', 'Ogg', 'AIFF', 'CAF', 'PCM', 'RAW', 'CDA', 'FLAC', 'ALAC', 'AC3', 'MP3', 'mp3PRO',
          'Ogg Vorbis', 'VQF', 'TwinVQ', 'WMA', 'AU', 'ASF', 'AA', 'AAC', 'MPEG-2 AAC', 'ATRAC', 'iKlax', 'U-MYX',
          'MXP4', 'avi', 'mpg', 'mpeg', 'mkv', 'mka', 'mks', 'asf', 'wmv', 'wma', 'mov', 'ogv', 'oga', 'ogx', 'ogm',
          '3gp', '3g2', 'webm', 'weba', 'nut', 'rm', 'mxf', 'asx', 'ts', 'flv']
large_media_limit = len(large_media)

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


def hyper_lynx(current_page):
    if debug_level > 0:
        print('------------------------------------')
    summary = 'Vérification des URL'
    html_source = ''
    url = ''
    current_page = current_page.replace('[//https://', '[https://')
    current_page = current_page.replace('[//http://', '[http://')
    current_page = current_page.replace('http://http://', 'http://')
    current_page = current_page.replace('https://https://', 'https://')
    current_page = current_page.replace('<ref>{{en}}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}}} ', '<ref>{{en}} ')
    current_page = re.sub('[C|c]ita(tion)? *\n* *(\|[^}{]*title *=)', r'ouvrage\2', current_page)
    current_page = translateLinkTemplates(current_page)
    current_page = translateDates(current_page)
    current_page = translateLanguages(current_page)

    if debug_level > 1:
        print('Fin des traductions :')
        input(current_page)

    # Recherche de chaque hyperlien en clair -------------------------------------------------------------------------
    final_page = ''
    while current_page.find('//') != -1:
        if debug_level > 0:
            print('-----------------------------------------------------------------')
        url = ''
        url_start = ''
        url_end_char = ''
        titre = ''
        template_end_position = 0
        is_broken_link = False
        # Avant l'URL
        PageDebut = current_page[:current_page.find('//')]
        while current_page.find('//') > current_page.find('}}') != -1:
            if debug_level > 0:
                print('URL après un modèle')
            final_page = final_page + current_page[:current_page.find('}}')+2]
            current_page = current_page[current_page.find('}}')+2:]

        # noTags interdisant la modification de l'URL
        ignored_link = False
        for b in range(1, tag_line):
            if PageDebut.rfind(tags_without_url[b][1]) != -1 and PageDebut.rfind(tags_without_url[b][1]) > \
                    PageDebut.rfind(tags_without_url[b][2]):
                ignored_link = True
                if debug_level > 0:
                    print('URL non traitée, car dans ' + tags_without_url[b][1])
                break
            if final_page.rfind(tags_without_url[b][1]) != -1 and final_page.rfind(tags_without_url[b][1]) > \
                    final_page.rfind(tags_without_url[b][2]):
                ignored_link = True
                if debug_level > 0:
                    print('URL non traitée, car dans ' + tags_without_url[b][1])
                break
        for noTemplate in broken_link_templates:
            if PageDebut.rfind('{{' + noTemplate + '|') != -1 and PageDebut.rfind('{{' + noTemplate + '|') > \
                    PageDebut.rfind('}}'):
                ignored_link = True
                if debug_level > 0:
                    print('URL non traitée, car dans ') + noTemplate
                break
            if PageDebut.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') != -1 and \
                PageDebut.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') > PageDebut.rfind('}}'):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTemplate
                break
            if final_page.rfind('{{' + noTemplate + '|') != -1 and final_page.rfind('{{' + noTemplate + '|') > \
                    final_page.rfind('}}'):
                ignored_link = True
                if debug_level > 0:
                    print('URL non traitée, car dans ') + noTemplate
                break
            if final_page.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') != -1 and \
                final_page.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') > final_page.rfind('}}'):
                ignored_link = True
                if debug_level > 0:
                    print('URL non traitée, car dans ') + noTemplate
                break

        if not ignored_link:
            is_broken_link = False
            # titre=
            if PageDebut.rfind('titre=') != -1 and PageDebut.rfind('titre=') > PageDebut.rfind('{{') \
                    and PageDebut.rfind('titre=') > PageDebut.rfind('}}'):
                current_page3 = PageDebut[PageDebut.rfind('titre=')+len('titre='):]
                if current_page3.find('|') != -1 and (current_page3.find('|') < current_page3.find('}}')
                                                      or current_page3.rfind('}}') == -1):
                    titre = current_page3[:current_page3.find('|')]
                else:
                    titre = current_page3
                if debug_level > 0:
                    print('Titre= avant URL : ' + titre)
            elif PageDebut.rfind('titre =') != -1 and PageDebut.rfind('titre =') > PageDebut.rfind('{{') \
                    and PageDebut.rfind('titre =') > PageDebut.rfind('}}'):
                current_page3 = PageDebut[PageDebut.rfind('titre =')+len('titre ='):]
                if current_page3.find('|') != -1 and (current_page3.find('|') < current_page3.find('}}')
                                                      or current_page3.rfind('}}') == -1):
                    titre = current_page3[:current_page3.find('|')]
                else:
                    titre = current_page3
                if debug_level > 0:
                    print('Titre = avant URL : ') + titre
        
            # url=
            if PageDebut[-1:] == '[':
                if debug_level > 0:
                    print('URL entre crochets sans protocole')
                url_start = 1
            elif PageDebut[-5:] == 'http:':
                if debug_level > 0:
                    print('URL http')
                url_start = 5
            elif PageDebut[-6:] == 'https:':
                if debug_level > 0:
                    print('URL https')
                url_start = 6
            elif PageDebut[-2:] == '{{':
                if debug_level > 0:
                    print("URL d'un modèle")
                break
            else:
                if debug_level > 0:
                    print('URL sans http ni crochet')
                url_start = 0
            if url_start != 0:
                # Après l'URL
                url_page_end = current_page[current_page.find('//'):]
                # url=    
                url_end_char = ' '
                for l in range(1, url_limit):
                    if url_page_end.find(url_end_char) == -1 or (url_page_end.find(url_ends[l]) != -1
                         and url_page_end.find(url_ends[l]) < url_page_end.find(url_end_char)):
                        url_end_char = url_ends[l]
                if debug_level > 0:
                    print('*Caractère de fin URL : ' + url_end_char)
                
                if url_start == 1:
                    url = 'http:' + current_page[current_page.find('//'):current_page.find('//')+url_page_end.find(url_end_char)]
                    if titre == '':
                        titre = current_page[current_page.find('//')+url_page_end.find(url_end_char):]
                        titre = trim(titre[:titre.find(']')])
                else:
                    url = current_page[current_page.find('//')-url_start:current_page.find('//')+url_page_end.find(url_end_char)]
                if len(url) <= 10:
                    url = ''
                    html_source = ''
                    is_broken_link = False
                else:
                    for u in range(1, url_limit2):
                        while url[len(url)-1:] == url_ends2[u]:
                            url = url[:len(url)-1]
                            if debug_level > 0:
                                print('Réduction de l\'URL de ' + url_ends2[u])
                    
                    is_large_media = False
                    for f in range(1, large_media_limit):
                        if url[len(url) - len(large_media[f]) - 1:].lower() == '.' + large_media[f].lower():
                            if debug_level > 0:
                                print(url)
                                print('Média détecté (memory error potentielle)')
                            is_large_media = True
                    if not is_large_media:
                        if debug_level > 0:
                            print('Recherche de la page distante : ' + url)
                        html_source = testURL(url, debug_level)
                        if debug_level > 0:
                            print('Recherche dans son contenu')
                        is_broken_link = testURLPage(html_source, url)
                
                # Site réputé HS mais invisible car ses sous-pages ont toutes été déplacées, et renvoient vers l'accueil
                for u in range(1, url_to_replace_limit):
                    if url.find(url_to_replace[u]) != -1 and len(url) > len(url_to_replace[u]) + 8:  # http://.../
                        is_broken_link = True
                
                # Confirmation manuelle
                if is_semi_auto:
                    webbrowser.open_new_tab(url)
                    if is_broken_link:
                        result = input("Lien brisé ? (o/n) ")
                    else:
                        result = input("Lien fonctionnel ? (o/n) ")
                    if result != "n" and result != "no" and result != "non":
                        is_broken_link = True
                    else:
                        is_broken_link = False
                        
                if debug_level > 0:
                    # Compte-rendu des URL détectées
                    try:
                        print('*URL : ' + url)
                        print('*Titre : ' + titre)
                        print('*HS : ' + str(is_broken_link))
                    except UnicodeDecodeError:
                        print('*HS : ' + str(is_broken_link))
                        print("UnicodeDecodeError l 466")
                if debug_level > 1: input(html_source[:7000])
                
                # Modification du wiki en conséquence    
                page_start = current_page[:current_page.find('//')+2]
                url_start = max(page_start.find('http://'), page_start.find('https://'), page_start.find('[//'))
                
                # Saut des modèles inclus dans un modèle de lien
                while page_start.rfind('{{') != -1 and page_start.rfind('{{') < page_start.rfind('}}'):
                    # pb des multiples crochets fermants sautés : {{ ({{ }} }})
                    current_page2 = page_start[page_start.rfind('{{'):]
                    if current_page2.rfind('}}') == current_page2.rfind('{{'):
                        page_start = page_start[:page_start.rfind('{{')]
                    else:
                        page_start = ''
                        break
                    if debug_level > 1:
                        input(page_start[-100:])
                    
                
                # Détection si l'hyperlien est dans un modèle (si aucun modèle n'est fermé avant eux)
                if (page_start.rfind('{{') != -1 and page_start.rfind('{{') > page_start.rfind('}}')) or \
                    (page_start.rfind('url=') != -1 and page_start.rfind('url=') > page_start.rfind('}}')) or \
                    (page_start.rfind('url =') != -1 and page_start.rfind('url =') > page_start.rfind('}}')):
                    template_start = page_start.rfind('{{')
                    page_start = page_start[page_start.rfind('{{'):len(page_start)]
                    replaced_template = ''
                    # Lien dans un modèle connu (consensus en cours pour les autres, atention aux infobox)
                    '''for m in range(1,templates_limit):
                        regex = '{{ *[' + new_template[m][0:1] + r'|' + new_template[m][0:1].upper() + r']' + new_template[m][1:len(new_template[m])] + r' *[\||\n]'
                    ''' 
                    if re.search('{{ *[L|l]ien web *[\||\n]', page_start):
                        replaced_template = 'lien web'
                        if debug_level > 0:
                            print('Détection de ' + replaced_template)
                    elif re.search('{{ *[L|l]ire en ligne *[\||\n]', page_start):
                        replaced_template = 'lire en ligne'
                        if debug_level > 0:
                            print('Détection de ' + replaced_template)
                    elif do_retest_broken_links and re.search('{{ *[L|l]ien brisé *[\||\n]', page_start):
                        replaced_template = 'lien brisé'
                        if debug_level > 0:
                            print('Détection de ' + replaced_template)
                        
                    # if page_start[0:2] == '{{': replaced_template = trim(page_start[2:page_start.find('|')])
                    
                    template_end_position = current_page.find('//')+2
                    template_page_end = current_page[template_end_position:]
                    # Calcul des modèles inclus dans le modèle de lien
                    while template_page_end.find('}}') != -1 \
                            and template_page_end.find('}}') > template_page_end.find('{{') != -1:
                        template_end_position = template_end_position + template_page_end.find('}}')+2
                        template_page_end = template_page_end[template_page_end.find('}}')+2:]
                    template_end_position = template_end_position + template_page_end.find('}}')+2
                    current_template = current_page[template_start:template_end_position]
                    # if debug_level > 0: print(")*Modele : " + current_template[:100]
                    
                    if replaced_template != '':
                        if debug_level > 0:
                            print('Ancien modèle à traiter : ' + replaced_template)
                        if is_broken_link:
                            try:
                                current_page = current_page[:template_start] + '{{lien brisé' \
                                    + current_page[re.search('{{ *[' + replaced_template[:1] + '|'
                                    + replaced_template[:1].upper() + ']'
                                    + replaced_template[1:] + ' *[\||\n]', current_page).end()-1:]
                            except AttributeError:
                                raise Exception("Regex introuvable ligne 811")
                                
                        elif replaced_template == 'lien brisé':
                            if debug_level > 0:
                                print('Rétablissement d\'un ancien lien brisé')
                            current_page = current_page[:current_page.find(replaced_template)] + 'lien web' \
                                           + current_page[current_page.find(replaced_template)+len(replaced_template):]
                    else:
                        if debug_level > 0:
                            print(url + " dans modèle non géré")

                else:
                    if debug_level > 0:
                        print('URL hors modèle')
                    if is_broken_link:
                        summary = summary + ', ajout de {{lien brisé}}'
                        if url_start == 1:
                            if debug_level > 0:
                                print('Ajout de lien brisé entre crochets sans protocole')
                            if titre != '':
                                current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                               + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre + '}}' \
                                               + current_page[current_page.find('//')+url_page_end.find(url_end_char):]
                            else:
                                current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                               + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' \
                                               + current_page[current_page.find('//')+url_page_end.find(url_end_char):]
                            # if debug_level > 0: input(current_page)
                        else:
                            if debug_level > 0:
                                print('Ajout de lien brisé 2')
                            if current_page[url_start-1:url_start] == '[' \
                                    and current_page[url_start-2:url_start] != '[[':
                                if debug_level > 0:
                                    print('entre crochet')
                                url_start = url_start - 1
                                current_page2 = ''
                                if titre == '':
                                    if debug_level > 0:
                                        print("Titre vide")
                                    # Prise en compte des crochets inclus dans un titre
                                    current_page2 = current_page[current_page.find('//')+url_page_end.find(url_end_char):]
                                    # if debug_level > 0: input(current_page2)
                                    if current_page2.find(']]') != -1 and current_page2.find(']]') < current_page2.find(']'):
                                        while current_page2.find(']]') != -1 and current_page2.find('[[') != -1 \
                                                and current_page2.find('[[') < current_page2.find(']]'):
                                            titre = titre + current_page2[:current_page2.find(']]')+1]
                                            current_page2 = current_page2[current_page2.find(']]')+1:]
                                        titre = trim(titre + current_page2[:current_page2.find(']]')])
                                        current_page2 = current_page2[current_page2.find(']]'):]
                                    while current_page2.find(']') != -1 and current_page2.find('[') != -1 \
                                            and current_page2.find('[') < current_page2.find(']'):
                                        titre = titre + current_page2[:current_page2.find(']')+1]
                                        current_page2 = current_page2[current_page2.find(']')+1:]
                                    titre = trim(titre + current_page2[:current_page2.find(']')])
                                    current_page2 = current_page2[current_page2.find(']'):]
                                if titre != '':
                                    if debug_level > 0:
                                        print("Ajout avec titre")
                                    current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                                   + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre \
                                                   + '}}' + current_page[len(current_page)-len(current_page2)+1:]
                                else:
                                    if debug_level > 0:
                                        print("Ajout sans titre")
                                    current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                                   + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' \
                                                   + current_page[current_page.find('//')+url_page_end.find(']')+1:]
                            else:    
                                if titre != '': 
                                    # Présence d'un titre
                                    if debug_level > 0:
                                        print('URL nue avec titre')
                                    current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                       + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' \
                                       + current_page[current_page.find('//')+url_page_end.find(url_end_char)+1:
                                                      current_page.find('//')+url_page_end.find(']')] + '}}' \
                                       + current_page[current_page.find('//')+url_page_end.find(']')+1:]
                                else:
                                    if debug_level > 0:
                                        print('URL nue sans titre')
                                    current_page = current_page[:url_start] + '{{lien brisé|consulté le=' \
                                       + time.strftime('%Y-%m-%d') + '|url=' + url + '}} ' \
                                       + current_page[current_page.find('//')+url_page_end.find(url_end_char):]
                        
                    else:
                        if debug_level > 0:
                            print('Aucun changement sur l\'URL http')
            else:
                if debug_level > 0:
                    print('Aucun changement sur l\'URL non http')
        else:
            if debug_level > 1:
                print('URL entre balises sautée')

        # Lien suivant, en sautant les URL incluses dans l'actuelle, et celles avec d'autres protocoles que http(s)
        if template_end_position == 0 and not is_broken_link:
            url_page_end = current_page[current_page.find('//')+2:]
            url_end_char = ' '
            for l in range(1, url_limit):
                if url_page_end.find(url_ends[l]) != -1 and url_page_end.find(url_ends[l]) \
                        < url_page_end.find(url_end_char):
                    url_end_char = url_ends[l]
            if debug_level > 0:
                print('Saut après "' + url_end_char + '"')
            final_page = final_page + current_page[:current_page.find('//')+2+url_page_end.find(url_end_char)]
            current_page = current_page[current_page.find('//')+2+url_page_end.find(url_end_char):]
        else:
            # Saut du reste du modèle courant (contenant parfois d'autres URL à laisser)
            if debug_level > 0:
                print('Saut après "}}"')
            final_page = final_page + current_page[:template_end_position]
            current_page = current_page[template_end_position:]
        if debug_level > 1:
            input(final_page)

    if final_page.find('|langue=None') != -1:
        if not is_broken_link:
            url_language = get_url_site_language(html_source)
            if url_language != 'None':
                try:
                    final_page = final_page.replace('|langue=None', '|langue=' + url_language)
                except UnicodeDecodeError:
                    if debug_level > 0:
                        print('UnicodeEncodeError l 1038')

    current_page = final_page + current_page
    final_page = ''    
    if debug_level > 0:
        print("Fin des tests URL")

    # Recherche de chaque hyperlien de modèles -----------------------------------------------------------------------
    if current_page.find('{{langue') != -1:  # du Wiktionnaire
        if debug_level > 0:
            print("Modèles Wiktionnaire")
        for m in range(1, templates_with_url_line):
            final_page = ''
            while current_page.find('{{' + templates_with_url[m][1] + '|') != -1:
                final_page = final_page + current_page[:current_page.find('{{' + templates_with_url[m][1] + '|')
                                                        + len('{{' + templates_with_url[m][1] + '|')]
                current_page = current_page[current_page.find('{{' + templates_with_url[m][1] + '|') + len('{{'
                                                                                   + templates_with_url[m][1] + '|'):]
                if current_page[0:current_page.find('}}')].find('|') != -1:
                    Param1Encode = current_page[:current_page.find('|')].replace(' ', '_')
                else:
                    Param1Encode = current_page[:current_page.find('}}')].replace(' ', '_')
                html_source = testURL(templates_with_url[m][2] + Param1Encode, debug_level)
                is_broken_link = testURLPage(html_source, url)
                if is_broken_link:
                    final_page = final_page[:final_page.rfind('{{' + templates_with_url[m][1] + '|')] \
                        + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + templates_with_url[m][2]
            current_page = final_page + current_page
            final_page = ''
        current_page = final_page + current_page
        final_page = ''
    if debug_level > 0:
        print('Fin des tests modèle')

    # Paramètres inutiles
    current_page = re.sub(r'{{ *Références *\| *colonnes *= *}}', r'{{Références}}', current_page)
    # Dans {{article}}, "éditeur" vide bloque "périodique", "journal" ou "revue"
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\||\n)[^}]*)\| *éditeur *= *([\||}|\n]+)', r'{{\1rticle\2\3', current_page)
    # https://fr.wikipedia.org/w/index.php?title=Discussion_utilisateur:JackPotte&oldid=prev&diff=165491794#Suggestion_pour_JackBot_:_Signalement_param%C3%A8tre_obligatoire_manquant_+_Lien_web_vs_Article
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *(?:ref|référence|référence simplifiée) *= *harv *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Bot/Requ%C3%AAtes/2020/01#Remplacement_automatique_d%27un_message_d%27erreur_du_mod%C3%A8le_%7B%7BOuvrage%7D%7D
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *display\-authors *= *etal *([\|}\n]+)', r'{{\1uvrage\2|et al.=oui\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *display\-authors *= *[0-9]* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *df *= *(?:mdy\-all|dmy\-all)* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # Empty 1=
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1rticle\2\3', current_page)
    current_page = re.sub(r'{{ *(l|L)ien web *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1ien web\2\3', current_page)
    # 1= exists: current_page = re.sub(r'{{ *(o|O)uvrage *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1uvrage\2\3', current_page)
    ''' TODO : à vérifier
    while current_page.find('|deadurl=no|') != -1:
        current_page = current_page[:current_page.find('|deadurl=no|')+1] + current_page[current_page.find('|deadurl=no|')+len('|deadurl=no|'):]
    '''

    final_page = final_page + current_page

    # TODO: avoid these fixes when: old_template.append('lien mort')
    final_page = final_page.replace('<ref></ref>', '')
    final_page = final_page.replace('{{lien mortarchive', '{{lien mort archive')
    final_page = final_page.replace('|langue=None', '')
    final_page = final_page.replace('|langue=en|langue=en', '|langue=en')
    final_page = final_page.replace('deadurl=yes', 'brisé le=oui')
    final_page = final_page.replace('deadurl=ja', 'brisé le=oui')
    if debug_level > 0:
        print('Fin hyperlynx.py')

    return final_page


def get_url_site_language(html_source, debug_level=0):
    if debug_level > 0:
        print('getURLsite_language: code langue à remplacer une fois trouvé sur la page distante...')
    url_language = 'None'
    try:
        regex = '<html [^>]*lang *= *"?\'?([a-zA-Z\-]+)'
        result = re.search(regex, html_source)
        if result:
            url_language = result.group(1)
            if debug_level > 0:
                print(' Langue trouvée sur le site')
            if (len(url_language)) > 6:
                url_language = 'None'
    except UnicodeDecodeError:
        if debug_level > 0:
            print('UnicodeEncodeError l 1032')
    if debug_level > 0:
        print(' Langue retenue : ') + url_language
    return url_language


def testURL(url, debug_level=0, opener=None):
    # Renvoie la page web d'une URL dès qu'il arrive à la lire.
    if not check_url:
        return 'ok'
    if debug_level > 0:
        print('--------')

    for blacklisted in broken_domains:
        if url.find(blacklisted) != -1:
            if debug_level > 0:
                print(' broken domain')
            return 'ko'
    for whitelisted in blocked_domains:
        if url.find(whitelisted) != -1:
            if debug_level > 0:
                print(' authorized domain')
            return 'ok'
    for whitelisted in authorized_files:
        if url[len(url)-len(whitelisted):] == whitelisted:
            if debug_level > 0:
                print(' authorized file')
            return 'ok'

    html_source = ''
    connection_method = 'Request'
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req) # If blocked here for hours, just whitelist the domain if the page isn't forbidden
        # TODO : ssl.CertificateError: hostname 'www.mediarodzina.com.pl' doesn't match either of 'mediarodzina.pl', 'www.mediarodzina.pl'
        # UnicodeWarning: Unicode unequal comparison failed to convert both arguments to Unicode
        html_source = res.read()
        if debug_level > 0:
            print(str(len(html_source)))
        if html_source != str(''):
            return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')  # ex : got more than 100 headers
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'opener'
        try:
            opener = urllib2.build_opener()
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''):
                return str(html_source)
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
        # pb avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304 qui renvoie 301 car son suffixe est facultatif
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : ssl.CertificateError')
        # HS : https://fr.wikipedia.org/w/index.php?title=Herv%C3%A9_Moulin&type=revision&diff=135989688&oldid=135121040
        url = url.replace('https:', 'http:')
        try:
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return str(html_source)
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = "urllib2.urlopen(url.encode('utf8'))"
    try:
        html_source = urllib2.urlopen(url.encode('utf8')).read()
        if debug_level > 0:
            print(str(len(html_source)))
        if html_source != str(''):
            return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'HTTPCookieProcessor'
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''):
                return str(html_source)
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
        
    connection_method = 'Request text/html'    
    try:
        req = urllib2.Request(url)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0: print(connection_method + ' : text/html ' + str(len(html_source)))
        if html_source != str(''):
            return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'geturl()'
        try:
            resp = urllib2.urlopen(url)
            req = urllib2.Request(resp.geturl())
            res = urllib2.urlopen(req)
            html_source = res.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return str(html_source)
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'Request Mozilla/5.0'
    agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        headers = {'User-Agent': agent}
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0:
            print(connection_method + ' : ' + agent + ' : ' + str(len(html_source)))
        if html_source != str(''):
            return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        if e.code == "404": return "404 error"
        if socket.gethostname() == 'PavilionDV6':
            connection_method = 'follow_all_redirects'    # fonctionne avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304
            try:
                r = requests.get(url)
                req = urllib2.Request(r.url)
                res = urllib2.urlopen(req)
                html_source = res.read()
                if debug_level > 0: print(str(len(html_source)))
                if html_source != str(''): return str(html_source)
            except UnicodeEncodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
            except UnicodeDecodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
            except UnicodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeError')
                connection_method = "Méthode url.encode('utf8')"
                try:
                    sock = urllib.urlopen(url.encode('utf8'))
                    html_source = sock.read()
                    sock.close()
                    if debug_level > 0: print(str(len(html_source)))
                    if html_source != str(''): return str(html_source)
                except UnicodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeError')
                except UnicodeEncodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
                except UnicodeDecodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
                except httplib.BadStatusLine:
                    if debug_level > 0: print(connection_method + ' : BadStatusLine')
                except httplib.InvalidURL:
                    if debug_level > 0: print(connection_method + ' : InvalidURL')
                except httplib.HTTPException:
                    if debug_level > 0: print(connection_method + ' : HTTPException')
                except urllib2.HTTPError as e:
                    if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
                except IOError as e:
                    if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
                except urllib2.URLError:
                    if debug_level > 0: print(connection_method + ' : URLError')
                except MemoryError:
                    if debug_level > 0: print(connection_method + ' : MemoryError')
                except requests.exceptions.HTTPError:
                    if debug_level > 0: print(connection_method + ' : HTTPError')
                except requests.exceptions.SSLError:
                    if debug_level > 0: print(connection_method + ' : SSLError')
                except ssl.CertificateError:
                    if debug_level > 0: print(connection_method + ' : CertificateError')
            except httplib.BadStatusLine:
                if debug_level > 0: print(connection_method + ' : BadStatusLine')
            except httplib.InvalidURL:
                if debug_level > 0: print(connection_method + ' : InvalidURL')
            except httplib.HTTPException:
                if debug_level > 0: print(connection_method + ' : HTTPException')
            except urllib2.HTTPError as e:
                if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
            except urllib2.URLError:
                if debug_level > 0: print(connection_method + ' : URLError')
            except requests.exceptions.TooManyRedirects:
                if debug_level > 0: print(connection_method + ' : TooManyRedirects')
            except IOError as e:
                if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
            except requests.exceptions.SSLError:
                if debug_level > 0: print(connection_method + ' : SSLError')
            except requests.exceptions.ConnectionError:
                if debug_level > 0: print(connection_method + ' ConnectionError')
            except requests.exceptions.InvalidSchema:
                if debug_level > 0: print(connection_method + ' InvalidSchema')
            except MemoryError:
                if debug_level > 0: print(connection_method + ' : MemoryError')
            except requests.exceptions.HTTPError:
                if debug_level > 0: print(connection_method + ' : HTTPError')
            except ssl.CertificateError:
                if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'Request &_r=4&'
    agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        if url.find('_r=') == -1:
            if url.find('?') != -1:
                url = url + "&_r=4&"
            else:
                url = url + "?_r=4&"
        else:
            if url.find('?') != -1:
                url = url[0:url.find('_r=')-1] + "&_r=4&"
            else:
                url = url[0:url.find('_r=')-1] + "?_r=4&"
        headers = {'User-Agent': agent}
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept', 'text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'HTTPRedirectHandler'
        try:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            request = opener.open(url)
            req = urllib2.Request(request.url)
            res = urllib2.urlopen(req)
            html_source = res.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return str(html_source)
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')     
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'urlopen'    # fonctionne avec http://voxofilm.free.fr/vox_0/500_jours_ensemble.htm, et http://www.kurosawa-drawings.com/page/27
    try:
        res = urllib2.urlopen(url)
        html_source = res.read()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return str(html_source)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        if e.code == 401: return "ok"    # http://www.nature.com/nature/journal/v442/n7104/full/nature04945.html
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'urllib.urlopen'
    try:
        sock = urllib.urlopen(url)
        html_source = sock.read()
        sock.close()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return str(html_source)
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error')
    except urllib2.URLError as e:
        if debug_level > 0: print(connection_method + ' : URLError %s.' % e.code)
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
        connection_method = "Méthode url.encode('utf8')"
        try:
            sock = urllib.urlopen(url.encode('utf8'))
            html_source = sock.read()
            sock.close()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return str(html_source)
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    if debug_level > 0:
        print(connection_method + ' Fin du test d\'existance du site')
    return ''


def testURLPage(html_source, url, debug_level=0):
    is_broken_link = False
    try:
        # if debug_level > 1 and html_source != str('') and html_source is not None: input(html_source[0:1000])
        if html_source is None:
            if debug_level > 0:
                print(url + " none type")
            return True
        elif html_source == str('ok') or (html_source == str('') and (url.find('à') != -1 or url.find('é') != -1
            or url.find('è') != -1 or url.find('ê') != -1 or url.find('ù') != -1)):
            # bug http://fr.wikipedia.org/w/index.php?title=Acad%C3%A9mie_fran%C3%A7aise&diff=prev&oldid=92572792
            return False
        elif html_source == str('ko') or html_source == str(''):
            if debug_level > 0:
                print(url + " page vide")
            return True
        else:
            if debug_level > 0:
                print(' page_content non vide')
            # Recherche des erreurs
            for e in range(0, errors_limit):
                if debug_level > 1:
                    print(sites_errors[e])
                if html_source.find(sites_errors[e]) != -1 and not re.search(r"\n[^\n]*if[^\n]*" + sites_errors[e],
                                                                             html_source):
                    if debug_level > 1:
                        print('  Trouvé')
                    # Exceptions
                    if sites_errors[e] == "404 Not Found" and url.find("audiofilemagazine.com") == -1:
                        # Exception avec popup formulaire en erreur
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    # Wikis : page vide à créer
                    if sites_errors[e] == "Soit vous avez mal &#233;crit le titre" and url.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    elif sites_errors[e] == "Il n'y a pour l'instant aucun texte sur cette page." != -1 \
                            and html_source.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    elif sites_errors[e] == "There is currently no text in this page." != -1 \
                            and html_source.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    # Sites particuliers
                    elif sites_errors[e] == "The page you requested cannot be found" \
                            and url.find("restaurantnewsresource.com") == -1:
                        # bug avec http://www.restaurantnewsresource.com/article35143 (Landry_s_Restaurants_Opens_T_REX_Cafe_at_Downtown_Disney.html)
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    elif sites_errors[e] == "Terme introuvable" != -1 and html_source.find("Site de l'ATILF") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    elif sites_errors[e] == "Cette forme est introuvable !" != -1 \
                            and html_source.find("Site de l'ATILF") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    elif sites_errors[e] == "Sorry, no matching records for query" != -1 \
                            and html_source.find("ATILF - CNRS") != -1:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break
                    else:
                        is_broken_link = True
                        if debug_level > 0:
                            print(url + " : " + sites_errors[e])
                        break

    except UnicodeError:
        if debug_level > 0: print('UnicodeError lors de la lecture')
        is_broken_link = False
    except UnicodeEncodeError:
        if debug_level > 0: print('UnicodeEncodeError lors de la lecture')
        is_broken_link = False
    except UnicodeDecodeError:
        if debug_level > 0: print('UnicodeDecodeError lors de la lecture')
        is_broken_link = False
    except httplib.BadStatusLine:
        if debug_level > 0: print('BadStatusLine lors de la lecture')
    except httplib.InvalidURL:
        if debug_level > 0: print('InvalidURL lors de la lecture')
        is_broken_link = False
    except httplib.HTTPException:
        if debug_level > 0: print('HTTPException')
        is_broken_link = False
    except urllib2.HTTPError as e:
        if debug_level > 0: print('HTTPError %s.' % e.code +  ' lors de la lecture')
        is_broken_link = False
    except IOError as e:
        if debug_level > 0: print('I/O error({0}): {1}'.format(e.errno, e.strerror) +  ' lors de la lecture')
        is_broken_link = False
    except urllib2.URLError:
        if debug_level > 0: print('URLError lors de la lecture')
        is_broken_link = False
    else:
        if debug_level > 1: print('Fin du test du contenu')
    return is_broken_link


def getCurrentLinkTemplate(current_page):
    # Extraction du modèle de lien en tenant compte des modèles inclus dedans
    current_page2 = current_page
    templateEndPosition = 0
    while current_page2.find('{{') != -1 and current_page2.find('{{') < current_page2.find('}}'):
        templateEndPosition = templateEndPosition + current_page.find('}}')+2
        current_page2 = current_page2[current_page2.find('}}')+2:]
    templateEndPosition = templateEndPosition + current_page2.find('}}')+2
    currentTemplate = current_page[:templateEndPosition]

    if debug_level > 1:
        print('  getCurrentLinkTemplate()')
        print(templateEndPosition)
        input(currentTemplate)

    return currentTemplate, templateEndPosition


def translateTemplateParameters(current_template):
    if debug_level > 1:
        print('Remplacement des anciens paramètres, en tenant compte des doublons et des variables selon les modèles')
    for p in range(0, param_limit):
        if debug_level > 1:
            print(old_param[p])
        fr_name = new_param[p]
        if old_param[p] == 'work':
            if isTemplate(current_template, 'article') and not hasParameter(current_template, 'périodique'):
                fr_name = 'périodique'
            elif isTemplate(current_template, 'lien web') and not hasParameter(current_template, 'site') \
                    and not hasParameter(current_template, 'website'):
                fr_name = 'site'
            else:
                fr_name = 'série'
        elif old_param[p] == 'publisher':
            if isTemplate(current_template, 'article') and not hasParameter(current_template, 'périodique') \
                    and not hasParameter(current_template, 'work'):
                fr_name = 'périodique'
            else:
                fr_name = 'éditeur'
        elif old_param[p] == 'agency':
            if isTemplate(current_template, 'article') and not hasParameter(current_template, 'périodique') \
                    and not hasParameter(current_template, 'work'):
                fr_name = 'périodique'
            else:
                fr_name = 'auteur institutionnel'
        elif old_param[p] == 'issue' and hasParameter(current_template, 'numéro'):
            fr_name = 'date'
        elif old_param[p] == 'editor':
            if hasParameter(current_template, 'éditeur'):
                fr_name = 'auteur'
        elif old_param[p] == 'en ligne le':
            if current_template.find('archiveurl') == -1 and current_template.find('archive url') == -1 \
                    and current_template.find('archive-url') == -1:
                continue
            elif current_template.find('archivedate') != -1 or current_template.find('archive date') != -1 \
                    or current_template.find('archive-date') != -1:
                continue
            elif debug_level > 0:
                print(' archiveurl ' + ' archivedate')
        elif old_param[p] == 'type':
            if isTemplate(current_template, 'article'):
                fr_name = 'nature article'
            elif isTemplate(current_template, 'ouvrage'):
                fr_name = 'nature ouvrage'
            else:
                fr_name = 'type'
        has_double = False
        if new_param[p] != 'langue':  # TODO because "|langue=None" in current_template
            regex = r'(\| *)' + new_param[p] + r'( *=)'
            has_double = re.search(regex, current_template)
        if not has_double:
            regex = r'(\| *)' + old_param[p] + r'( *=)'
            current_template = re.sub(regex, r'\1' + fr_name + r'\2', current_template)
            if debug_level > 1:
                print(regex)
    current_template = current_template.replace('|=', u'|')
    current_template = current_template.replace('| =', u'|')
    current_template = current_template.replace('|  =', u'|')
    current_template = current_template.replace('|}}', u'}}')
    current_template = current_template.replace('| }}', u'}}')
    has_included_template = current_template.find('{{') != -1
    if not has_included_template:
        current_template = current_template.replace('||', u'|')

    return current_template


def translateLinkTemplates(current_page):
    final_page = ''
    for m in range(0, translated_templates_limit):
        # Formatage des anciens modèles
        current_page = re.sub(('(Modèle:)?[' + old_template[m][:1] + r'|' + old_template[m][:1].upper() + r']' + old_template[m][1:]).replace(' ', '_') + r' *\|', old_template[m] + r'|', current_page)
        current_page = re.sub(('(Modèle:)?[' + old_template[m][:1] + r'|' + old_template[m][:1].upper() + r']' + old_template[m][1:]).replace(' ', '  ') + r' *\|', old_template[m] + r'|', current_page)
        current_page = re.sub(('(Modèle:)?[' + old_template[m][:1] + r'|' + old_template[m][:1].upper() + r']' + old_template[m][1:]) + r' *\|', old_template[m] + r'|', current_page)
        # Traitement de chaque modèle à traduire
        while re.search('{{[\n ]*' + old_template[m] + ' *[\||\n]+', current_page):
            if debug_level > 1:
                print('Modèle n°' + str(m))
                print(current_page[re.search('{{[\n ]*' + old_template[m] + ' *[\||\n]', current_page).end() - 1:][:100])
            final_page = final_page + current_page[:re.search('{{[\n ]*' + old_template[m] + ' *[\||\n]', current_page).end() - 1]
            current_page = current_page[re.search('{{[\n ]*' + old_template[m] + ' *[\||\n]', current_page).end() - 1:]
            # Identification du code langue existant dans le modèle
            language_code = ''
            if final_page.rfind('{{') != -1:
                page_start = final_page[:final_page.rfind('{{')]
                if page_start.rfind('{{') != -1 and page_start.rfind('}}') != -1 \
                        and (page_start[len(page_start)-2:] == '}}' or page_start[len(page_start)-3:] == '}} '):
                    language_code = page_start[page_start.rfind('{{')+2:page_start.rfind('}}')]
                    if site.family in ['wikipedia', 'wiktionary']:
                        # Recherche de validité mais tous les codes ne sont pas encore sur les sites francophones
                        if language_code.find('}}') != -1:
                            language_code = language_code[:language_code.find('}}')]
                        if debug_level > 1:
                            print('Modèle:') + language_code
                        page2 = Page(site, 'Modèle:' + language_code)
                        try:
                            page_code = page2.get()
                        except pywikibot.exceptions.NoPage:
                            print('NoPage l 425')
                            page_code = ''
                        except pywikibot.exceptions.LockedPage: 
                            print('Locked l 428')
                            page_code = ''
                        except pywikibot.exceptions.IsRedirectPage: 
                            page_code = page2.get(get_redirect=True)
                        if debug_level > 0:
                            print(page_code)
                        if page_code.find('Indication de langue') != -1:
                            if len(language_code) == 2:  # or len(language_code) == 3: if language_code == 'pdf': |format=language_code, absent de {{lien web}}
                                # Retrait du modèle de langue devenu inutile
                                final_page = final_page[:final_page.rfind('{{' + language_code + '}}')] + final_page[final_page.rfind('{{' + language_code + '}}')+len('{{' + language_code + '}}'):]
            if language_code == '':
                if debug_level > 0:
                    print(' Code langue à remplacer une fois trouvé sur la page distante...')
                language_code = 'None'
            # Ajout du code langue dans le modèle
            if debug_level > 0:
                print('Modèle préalable : ' + language_code)
            regex = r'[^}]*lang(ue|uage)* *=[^}]*}}'
            if not re.search(regex, current_page):
                current_page = '|langue=' + language_code + current_page
            elif re.search(regex, current_page).end() > current_page.find('}}')+2:
                current_page = '|langue=' + language_code + current_page
                
        current_page = final_page + current_page
        final_page = ''

    for m in range(0, templates_limit):
        if debug_level > 1:
            print(' Traduction des noms du modèle ' + old_template[m])
        current_page = current_page.replace('{{' + old_template[m] + ' ', '{{' + old_template[m] + '')
        current_page = re.sub(r'({{[\n ]*)[' + old_template[m][:1] + r'|' + old_template[m][:1].upper() + r']' +
                              old_template[m][1:len(old_template[m])] + r'( *[|\n\t}])', r'\1'
                              + new_template[m] + r'\2', current_page)
        # Suppression des modèles vides
        regex = '{{ *[' + new_template[m][:1] + r'|' + new_template[m][:1].upper() + r']' + new_template[m][1:len(new_template[m])] + r' *}}'
        while re.search(regex, current_page):
            current_page = current_page[:re.search(regex, current_page).start()] + current_page[re.search(regex, current_page).end():]
        # Traduction des paramètres de chaque modèle de la page
        regex = '{{ *[' + new_template[m][:1] + r'|' + new_template[m][:1].upper() + r']' + new_template[m][1:len(new_template[m])] + r' *[\||\n]'
        while re.search(regex, current_page):
            final_page = final_page + current_page[:re.search(regex, current_page).start()+2]
            current_page = current_page[re.search(regex, current_page).start()+2:]
            currentTemplate, templateEndPosition = getCurrentLinkTemplate(current_page)
            current_page = translateTemplateParameters(currentTemplate) + current_page[templateEndPosition:]

        current_page = final_page + current_page
        final_page = ''

    return current_page


def translateDates(current_page):
    if debug_level > 1:
        print('  translateDates()')
    date_parameters = ['date', 'mois', 'consulté le', 'en ligne le', 'dts', 'Dts', 'date triable', 'Date triable']
    for m in range(1, month_line + 1):
        if debug_level > 1:
            print('Mois ') + str(m)
            print(months_translations[m][1])
        for p in range(1, len(date_parameters)):
            if debug_level > 1: print('Recherche de ') + date_parameters[p] + ' *=[ ,0-9]*' + months_translations[m][1]
            if p > 4:
                current_page = re.sub(r'({{ *' + date_parameters[p] + r'[^}]+)' + months_translations[m][1] + r'([^}]+}})', r'\1' + months_translations[m][2] + r'\2', current_page)
                current_page = re.sub(r'({{ *' + date_parameters[p] + r'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' + months_translations[m][2] + r'(\|[ 0-9][ 0-9])}}', r'\1\3|' + months_translations[m][2] + r'\2}}', current_page)
            else:
                current_page = re.sub(r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][1] + r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' + months_translations[m][2] + r'\2', current_page)
                current_page = re.sub(r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + months_translations[m][1][:1].lower() + months_translations[m][1][1:] + r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' + months_translations[m][2] + r'\2', current_page)
                
                # Ordre des dates : jj mois aaaa
                if debug_level > 1: print('Recherche de ') + date_parameters[p] + ' *= *' + months_translations[m][2] + ' *([0-9]+), '
                current_page = re.sub(r'(\| *' + date_parameters[p] + ' *= *)' + months_translations[m][2] + r' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])', r'\1' + r'\2' + r' ' + months_translations[m][2] + r' ' + r'\3' + r'\4', current_page)    # trim('\3') ne fonctionne pas
 
    return current_page


def translateLanguages(current_page):
    if debug_level > 1: print('  translateLanguages()')
    for l in range(1, languages_line + 1):
        if debug_level > 1:
            print('Langue ') + str(l)
            print(languages_translations[l][1])
        current_page = re.sub(r'(\| *langue *= *)' + languages_translations[l][1] + r'( *[<|\||\n\t|}])', r'\1' + languages_translations[l][2] + r'\2', current_page)

        # TODO rustine suite à un imprévu censé être réglé ci-dessus, mais qui touche presque 10 % des pages.
        current_page = re.sub(r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Aa]rticle\|langue=' + languages_translations[l][2] + r'\|)', r'\1', current_page)
        current_page = re.sub(r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Ll]ien web\|langue=' + languages_translations[l][2] + r'\|)', r'\1', current_page)
        current_page = re.sub(r'{{' + languages_translations[l][2] + r'}}[ \n]*({{[Oo]uvrage\|langue=' + languages_translations[l][2] + r'\|)', r'\1', current_page)
 
    return current_page


def isTemplate(string, template):
    regex = r'^(' + template[:1].upper() + r'|' + template[:1].lower() + r')' + template[1:]
    return re.search(regex, string)


def hasParameter(string, param):
    regex = r'\| *' + param + r' *='
    return re.search(regex, string)

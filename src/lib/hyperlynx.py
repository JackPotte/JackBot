#!/usr/bin/env python
# coding: utf-8
"""
Ce script vérifie toutes les URL des articles de la forme http://, https:// et [// ou incluses dans certains modèles
(pas tous étant donnée leur complexité, car certains incluent des {{{1}}} et {{{2}}} dans leurs URL)
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


def set_globals_url_checker(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


is_semi_auto = False
do_retest_broken_links = False

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

url_to_replace = ['athena.unige.ch/athena', 'un2sg4.unige.ch/athena']
url_to_replace_limit = len(url_to_replace)

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

authorized_files = []
authorized_files.append('.pdf')

# Too large media to ignore
large_media = ['RIFF', 'WAV', 'BWF', 'Ogg', 'AIFF', 'CAF', 'PCM', 'RAW', 'CDA', 'FLAC', 'ALAC', 'AC3', 'MP3', 'mp3PRO',
          'Ogg Vorbis', 'VQF', 'TwinVQ', 'WMA', 'AU', 'ASF', 'AA', 'AAC', 'MPEG-2 AAC', 'ATRAC', 'iKlax', 'U-MYX',
          'MXP4', 'avi', 'mpg', 'mpeg', 'mkv', 'mka', 'mks', 'asf', 'wmv', 'wma', 'mov', 'ogv', 'oga', 'ogx', 'ogm',
          '3gp', '3g2', 'webm', 'weba', 'nut', 'rm', 'mxf', 'asx', 'ts', 'flv']
large_media_limit = len(large_media)


def treat_broken_links(current_page, summary):
    if debug_level > 0:
        print('------------------------------------')
    summary += ', vérification des URL'
    html_source = ''
    url = ''

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
                        html_source = check_url(url, debug_level)
                        if debug_level > 0:
                            print('Recherche dans son contenu')
                        is_broken_link = check_url_page(html_source, url)
                
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
                        regex = r'{{ *[' + new_template[m][0:1] + r'|' + new_template[m][0:1].upper() + r']' + new_template[m][1:len(new_template[m])] + r' *[\||\n]'
                    ''' 
                    if re.search(r'{{ *[L|l]ien web *[\||\n]', page_start):
                        replaced_template = 'lien web'
                        if debug_level > 0:
                            print('Détection de ' + replaced_template)
                    elif re.search(r'{{ *[L|l]ire en ligne *[\||\n]', page_start):
                        replaced_template = 'lire en ligne'
                        if debug_level > 0:
                            print('Détection de ' + replaced_template)
                    elif do_retest_broken_links and re.search(r'{{ *[L|l]ien brisé *[\||\n]', page_start):
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
                                    + current_page[re.search(r'{{ *[' + replaced_template[:1] + '|'
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

    current_page = final_page + current_page
    final_page = ''
    if debug_level > 0:
        print("Fin des tests URL")

    # TODO: return the site language
    if current_page.find('|langue=None') != -1:
        if not is_broken_link:
            url_language = get_url_site_language(html_source)
            if url_language != 'None':
                try:
                    current_page = current_page.replace('|langue=None', '|langue=' + url_language)
                except UnicodeDecodeError as e:
                    if debug_level > 0:
                        print(str(e))

    # Recherche de chaque hyperlien de modèles -----------------------------------------------------------------------
    if current_page.find('{{langue') != -1:  # du Wiktionnaire
        if debug_level > 0:
            print(" Modèles Wiktionnaire")
        for m in range(1, templates_with_url_line):
            final_page = ''
            while current_page.find('{{' + templates_with_url[m][1] + '|') != -1:
                final_page = final_page + current_page[:current_page.find('{{' + templates_with_url[m][1] + '|')
                                                        + len('{{' + templates_with_url[m][1] + '|')]
                current_page = current_page[current_page.find('{{' + templates_with_url[m][1] + '|') + len('{{'
                                                                                   + templates_with_url[m][1] + '|'):]
                if current_page[:current_page.find('}}')].find('|') != -1:
                    encoded_param1 = current_page[:current_page.find('|')].replace(' ', '_')
                else:
                    encoded_param1 = current_page[:current_page.find('}}')].replace(' ', '_')
                html_source = check_url(templates_with_url[m][2] + encoded_param1, debug_level)
                is_broken_link = check_url_page(html_source, url)
                if is_broken_link:
                    final_page = final_page[:final_page.rfind('{{' + templates_with_url[m][1] + '|')] \
                        + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + templates_with_url[m][2]
            current_page = final_page + current_page
            final_page = ''
        current_page = final_page + current_page
        final_page = ''
    if debug_level > 0:
        print(' Fin des tests modèle')
        print('------------------------------------')

    final_page = final_page + current_page
    return final_page, summary


def get_url_site_language(html_source, debug_level=0):
    if debug_level > 0:
        print('get_url_site_language(): code langue à remplacer une fois trouvé sur la page distante...')
    url_language = 'None'
    try:
        regex = r'<html [^>]*lang *= *"?\'?([a-zA-Z\-]+)'
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


def check_url(url, debug_level=0, opener=None):
    # Renvoie la page web d'une URL dès qu'il arrive à la lire.
    if not do_check_url:
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


def check_url_page(html_source, url, debug_level=0):
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

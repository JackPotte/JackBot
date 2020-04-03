#!/usr/bin/env python
# coding: utf-8
"""
Ce script :
#     Vérifie tous les hyperliens, les marque comme {{lien brisé}} le cas échéant, et traduit leurs modèles en français
#     Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
# A terme peut-être :
#     Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...), et remplacement des liens bleu fr.wikipedia.org/wiki par [[ ]], des liens rouges par {{lien|lang=xx}}
#     Mettra à jour les évaluations à partir du bandeau ébauche
#     Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto) ou : python cosmetic_changes.py -lang:"fr" -recentchanges
"""
from __future__ import absolute_import, unicode_literals
import os
import re
import sys
import pywikibot
from pywikibot import *
# JackBot
dir_src = os.path.dirname(__file__)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
from lib import *
from html2unicode import *
from default_sort import *
from hyperlynx import *
from languages import *
from languages_generator import *
from page_functions import *
from PageProvider import *

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

translate_url = True
fix_tags = False
fix_files = True
treat_all_namespaces = False
fix_article = False
fix_missing_titles = False
safe_mode = True  # Count if the braces & brackets are even before saving
output = 'dumps/articles_WPout.txt'
referencesAliases = []


def treat_page_by_name(page_name):
    print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    if not page.exists():
        return
    if not has_more_than_time(page):
        return
    if not treat_all_namespaces and page.namespace() != 0 and page_name.find(username) == -1 \
            and page_name.find('Template:Cite pmid/') == -1:
        return
    current_page_content = get_content_from_page(page, 'All')
    if current_page_content == 'KO':
        print('page_content illisible')
        return
    current_page = current_page_content

    # *** Traitement des textes ***
    if debug_level > 0:
        print(' Traitements généraux')
    current_page = global_operations(current_page)
    if fix_files:
        current_page = replace_files_errors(current_page)
    if fix_tags:
        current_page = replace_deprecated_tags(current_page)
    if translate_url:
        if debug_level > 0:
            print('Test des URL')
        current_page = hyper_lynx(current_page)
    regex = r'({{[Ll]ien *\|[^}]*)traducteur( *=)'
    if re.search(regex, current_page):
        current_page = re.sub(regex, r'\1trad\2', current_page)
    current_page = current_page.replace('hhttp://', 'http://')

    regex = r'({{[Ll]ien brisé*\|[^}]*url *=[^\|\'}]*)\'\'(\| *titre *=[^\|\'}]*)\'\''
    if re.search(regex, current_page):
        current_page = re.sub(regex, r'\1\2', current_page)

    # *** Traitement des modèles ***
    # https://fr.wikipedia.org/wiki/Catégorie:Page_utilisant_un_modèle_avec_un_paramètre_obsolète
    regex = r' *{{[Rr]eflist([^}]*)}}'
    if re.search(regex, current_page):
        current_page = re.sub(regex,  r'{{Références\1}}', current_page)
    # TODO: garder les paramètres non vides : pasdecol, group(e), références, mais quid de taille et colonnes ?

    # https://fr.wikipedia.org/wiki/Catégorie:Page_du_modèle_Article_comportant_une_erreur
    if fix_article:
        final_page = ''
        while current_page.find('{{article') != -1:
            final_page = final_page + current_page[:current_page.find('{{article')+len('{{article')]
            current_page = current_page[current_page.find('{{article')+len('{{article'):]
            if current_page.find('éditeur=') != -1 and current_page.find('éditeur=') < current_page.find('}}') \
                and (current_page.find('périodique=') == -1
                or current_page.find('périodique=') > current_page.find('}}')) \
                and (current_page.find('revue=') == -1 or current_page.find('revue=') > current_page.find('}}')) \
                and (current_page.find('journal=') == -1 or current_page.find('journal=') > current_page.find('}}')):
                final_page = final_page + current_page[:current_page.find('éditeur=')] + 'périodique='
                current_page = current_page[current_page.find('éditeur=')+len('éditeur='):]
        current_page = final_page + current_page
        final_page = ''
        while current_page.find('{{Article') != -1:
            final_page = final_page + current_page[:current_page.find('{{Article')+len('{{Article')]
            current_page = current_page[current_page.find('{{Article')+len('{{Article'):]
            if current_page.find('éditeur=') != -1 and current_page.find('éditeur=') < current_page.find('}}') \
                and (current_page.find('périodique=') == -1
                 or current_page.find('périodique=') > current_page.find('}}')) \
                and (current_page.find('revue=') == -1 or current_page.find('revue=') > current_page.find('}}')) \
                and (current_page.find('journal=') == -1 or current_page.find('journal=') > current_page.find('}}')):
                final_page = final_page + current_page[:current_page.find('éditeur=')] + 'périodique='
                current_page = current_page[current_page.find('éditeur=')+len('éditeur='):]        
        current_page = final_page + current_page

    if fix_missing_titles:
        # Titres manquants (TODO: en test)
        final_page = ''
        regex = r'{{[l|L]ien web *\|'
        if re.search(regex, current_page):
            final_page = current_page[:re.search(regex, current_page).start()]
            current_page = current_page[re.search(regex, current_page).start():]
            current_page = add_parameter(current_page, 'titre')
        current_page = final_page + current_page

    # *** Traitement des Catégories ***
    if page_name.find('Template:Cite pmid/') != -1:
        current_page = current_page.replace('Catégorie:Modèle de source‎', 'Catégorie:Modèle pmid')
        current_page = current_page.replace('[[Catégorie:Modèle pmid]]', '[[Catégorie:Modèle pmid‎|{{SUBPAGENAME}}]]')

    # Analyse des crochets et accolades (à faire : hors LaTex)
    if current_page.count('{') - current_page.count('}') != 0:
        if page_name.find('User:JackBot/') == -1: log('*[[' + page_name + ']] : accolade cassée')
        # if debug_level > 1: raise Exception('Accolade cassée')
    if current_page.count('[') - current_page.count(']') != 0:
        if page_name.find('User:JackBot/') == -1: log('*[[' + page_name + ']] : crochet cassé')
        # if debug_level > 1: raise Exception('Crochet cassé')
    if current_page_content.count('[[') - current_page_content.count(']]') != current_page.count('[[') \
            - current_page.count(']]'):
        txt_file = codecs.open(output, 'a', 'utf-8')
        txt_file.write(current_page + '\n\n-----------------------------------------------------------------------\n\n')
        txt_file.close()
        if debug_level > 0:
            print('Crochets cassés')    # raise Exception('Crochets cassés')
            input(current_page_content)
        if safe_mode: return
    if current_page_content.count('{{') - current_page_content.count('}}') != current_page.count('{{') - current_page.count('}}'):
        txt_file = codecs.open(output, 'a', 'utf-8')
        txt_file.write(current_page + '\n\n-----------------------------------------------------------------------\n\n')
        txt_file.close()
        if debug_level > 0:
            print('Accolades cassées')    #raise Exception('Accolades cassées')
            input(current_page)
        if safe_mode:
            return

    final_page = current_page
    if debug_level > 0:
        print('--------------------------------------------------------------------------------------------')
    if final_page != current_page_content and final_page != current_page_content.replace('{{chapitre |', '{{chapitre|') \
            and final_page != current_page_content.replace('{{Chapitre |', '{{Chapitre|'):
        summary = summary + ', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer_les_.7B.7BCite_web.7D.7D_par_.7B.7BLien_web.7D.7D|traduction des modèles de liens]]'
        final_page = final_page.replace(r'</ref><ref>', r'</ref>{{,}}<ref>')
        save_page(page, final_page, summary)


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)
setGlobalsHL(debug_level, site, username)


def main(*args):
    global treat_all_namespaces
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2' or sys.argv[1] == '-tu':
            treat_page_by_name('User:' + username + '/test unitaire')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_all_namespaces = True
            treat_page_by_name('SIMP J013656.5+093347')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = r'\| *French *\|'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            p.pages_by_user('User:' + username)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2], namespaces=[0])
            else:
                p.pages_by_search('insource:/\| *display-authors *= *etal */')
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Modèle:Dead link')
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            after_page = ''
            if len(sys.argv) > 2: after_page = sys.argv[2]
            p.pages_by_cat('Catégorie:page_content du modèle Ouvrage comportant une erreur', namespaces=None,
                           after_page=after_page)
            # treat_all_namespaces = True
            # p.pagesByCat('Catégorie:Pages utilisant des liens magiques ISBN', namespaces = None, after_page = after_page)
            # p.pagesByCat('Catégorie:Pages avec ISBN invalide', namespaces = None, after_page = after_page)
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
            p.pages_by_special_lint(lint_categories='missing-end-tag', namespaces=[0])
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(update_html_to_unicode(sys.argv[1]))
    else:
        # Daily:
        p.pages_by_cat('Catégorie:Modèle de source', namespaces=[10], names=['pmid'])
        p.pages_by_link('Template:Cite web')
        p.pages_by_link('Template:Cite journal')
        p.pages_by_link('Template:Cite news')
        p.pages_by_link('Template:Cite press release')
        p.pages_by_link('Template:Cite episode')
        p.pages_by_link('Template:Cite video')
        p.pages_by_link('Template:Cite conference')
        p.pages_by_link('Template:Cite arXiv')
        p.pages_by_link('Template:Lien news')
        p.pages_by_link('Template:deadlink')
        p.pages_by_link('Template:lien brise')
        p.pages_by_link('Template:lien cassé')
        p.pages_by_link('Template:lien mort')
        p.pages_by_link('Template:lien web brisé')
        p.pages_by_link('Template:webarchive')
        p.pages_by_link('Template:Docu')
        p.pages_by_link('Template:Cita web')
        p.pages_by_link('Template:Cita noticia')
        p.pages_by_link('Template:Citeweb')
        p.pages_by_link('Template:Cite magazine')
        p.pages_by_link('Template:Cite')
        p.pages_by_link('Template:Cite book')
        p.pages_by_link('Template:Cita libro')
        p.pages_by_link('Template:Webbref')
        p.pages_by_link('Template:Internetquelle')
        # p.pagesByLink('Template:Reflist')  # Interblocages quotidients


if __name__ == "__main__":
    main(sys.argv)

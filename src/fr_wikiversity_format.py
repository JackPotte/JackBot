#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate les pages de la Wikiversité :
1) Il retire les clés de tri devenues inutiles.
2) Il complète les modèles {{Chapitre}} à partir des {{Leçon}}.
3) Ajoute {{Bas de page}}.
TODO:
4) Remplir les {{Département}} à remplir à partir des {{Leçon}}.
5) Compléter les {{Bas de page}} existants.
"""
from __future__ import absolute_import, unicode_literals
import os
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

do_check_url = False
fix_tags = False
fix_files = True
fix_templates = False
do_add_category = False

oldParameters = []
newParameters = []
oldParameters.append('numero')
newParameters.append('numéro')

# https://fr.wikiversity.org/wiki/Catégorie:Modèles_de_l'université
categorizing_templates = []
categorizing_templates.append('Faculté')
categorizing_templates.append('Département')
categorizing_templates.append('Cours')
categorizing_templates.append('Leçon')
categorizing_templates.append('Chapitre')
categorizing_templates.append('Annexe')
categorizing_templates.append('Quiz')

sub_pages = []
# {{leçon}}
sub_pages.append('Présentation de la leçon')
sub_pages.append('Objectifs')
sub_pages.append('Prérequis conseillés')
sub_pages.append('Référents')
sub_pages.append('Post-notions')
# {{cours}}
sub_pages.append('Présentation du cours')
sub_pages.append('Leçons')
sub_pages.append('Fiche')
sub_pages.append('Feuille d\'exercices')
sub_pages.append('Annexe')
sub_pages.append('Voir aussi')
# {{département}}
sub_pages.append('Présentation du département')
sub_pages.append('Leçons par thèmes')
sub_pages.append('Leçons par niveaux')
sub_pages.append('Contributeurs')

# {{faculté}}
sub_pages.append('Présentation de la faculté')
sub_pages.append('Départements')
sub_pages.append('Transverse')

# {{Chapitre}} parameters
'''
param = []
param.append('titre ') # espace pour disambiguiser
param.append('titre_leçon')
param.append('idfaculté')
param.append(' leçon')
param.append('page')
param.append('numero')
param.append('précédent')
param.append('suivant')
param.append('align')
param.append('niveau')
'''


def treat_page_by_name(page_name):
    if debug_level > 0:
        print('------------------------------------')
        print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    page_content = current_page_content
    final_page_content = ''

    page_content = global_operations(page_content)
    if fix_files:
        page_content = replace_files_errors(page_content)
    if fix_tags:
        page_content = replace_deprecated_tags(page_content)
    if do_check_url:
        page_content, summary = treat_broken_links(page_content, summary)
        
    page_content = page_content.replace('[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
    page_content = page_content.replace('[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
    page_content = page_content.replace('{{autoCat}}', '{{AutoCat}}')
    if do_add_category and page_name.find('/') != -1:
        sub_page_name = page_name[page_name.rfind('/')+1:]
        if debug_level > 0:
            print(sub_page_name)
        if sub_page_name in sub_pages and page_content.find('[[Catégorie:') == -1 \
                and page_content.find('{{AutoCat}}') == -1 and page_content.find('{{imprimable') == -1:
            page_content = page_content + '\n\n{{AutoCat}}'
            summary = summary + ', [[Spécial:Pages non catégorisées]]'

    if page.namespace() == 0:
        # Remplacements consensuels (ex : numero -> numéro)
        if debug_level > 1:
            print(' Balises désuètes <center>')
        ''' Solution 1 : bug d'inclusion dans les modèles (qui demandent "|1=")
        regex = r'<div *style *= *"? *text\-align: *center;? *"? *>((?!div).*)</div>'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'{{centrer|1=\1}}', page_content)
        regex = r'<div *style *= *"? *text\-align: *right;? *"? *>((?!div).*)</div>'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'{{droite|1=\1}}', page_content)
            Solution 2 : absconse
        regex = r'<div *style *= *"? *text\-align: *center;? *"? *>({{[Ee]ncadre\|)((?!div).*)</div>'
        if re.search(regex, page_content):
            page_content = re.sub(regex, r'\1class=center|\2', page_content)
            Solution 3 : modèle connu sur WP
        '''
        nested_tag = r'[^<]*(?:<(.*?)>|.)*[^<]*'
        regex = r'<div style *= *"text\-align: *center;">(' + nested_tag + r')</div>'
        if re.search(regex, page_content):
            summary += ', [[Modèle:centrer]]'
            page_content = re.sub(regex, r'{{centrer|\1}}', page_content, re.DOTALL)

        # Fix parameters
        for p in range(1, len(oldParameters)-1):
            if page_content.find('{{' + temp[p] + '|') != -1 or page_content.find('{{' + oldParameters[p] + '}}') != -1:
                page_content = page_content[0:page_content.find(temp[p])] + newParameters[p] + page_content[page_content.find(temp[p])+len(temp[p]):]

        # https://fr.wikiversity.org/wiki/Catégorie:Chapitres_sans_pied_de_page
        if re.search(r'{{[cC]hapitre[ \n|]', page_content) and not re.search(r'{{[bB]as de page[ \n|]', page_content):
            chapter = get_first_template_by_name(page_content, 'chapitre')
            if chapter != '':
                footer = '\n\n{{Bas de page\n'
                for p in ['idfaculté', 'leçon', 'précédent', 'suivant']:
                    parameter = get_parameter(chapter, p)
                    if len(parameter) > 0:
                        footer = footer + '  |' + parameter
                footer = footer + '}}'
                page_content = page_content + footer

        # http://fr.wikiversity.org/wiki/Catégorie:Modèle_mal_utilisé
        if fix_templates:
            if re.search(r'{{[cC]hapitre[ \n|{}]', page_content):
                    ''' Bug du modèle tronqué :
                    if re.compile('{Chapitre').search(page_content):
                            if re.compile('{Chapitre[.\n]*(\n.*align.*=.*\n)').search(page_content):
                                    i1 = re.search(r'{{Chapitre[.\n]*(\n.*align.*=.*\n)',page_content).end()
                                    i2 = re.search(r'(\n.*align.*=.*\n)',page_content[:i1]).start()
                                    page_content = page_content[:i2] + '\n' + page_content[i1:]
                            final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                            page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                    elif re.compile('{chapitre').search(page_content):
                            if re.compile('{chapitre[.\n]*(\n.*align.*=.*\n)').search(page_content):
                                    i1 = re.search(r'{{chapitre[.\n]*(\n.*align.*=.*\n)',page_content).end()
                                    i2 = re.search(r'(\n.*align.*=.*\n)',page_content[:i1]).start()
                                    page_content = page_content[:i2] + '\n' + page_content[i1:]
                            final_page_content = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                            page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):]

                            if re.compile('{{Chapitre[\n.]*(\n.*leçon.*=.*\n)').search(page_content):
                                    print("leçon1")
                            if re.compile('{{Chapitre.*\n.*\n.*(\n.*leçon.*=.*\n)').search(page_content):
                                    print("leçon2")
                            if re.compile('{{Chapitre.*\n.*\n.*\n.*(\n.*leçon.*=.*\n)').search(page_content):
                                    print("leçon3")
                            if re.compile('{{Chapitre[.\n]*(\n.*niveau.*=.*\n)').search(page_content):
                                    print("niveau")
                                    print(re.compile('{{Chapitre[.\n])*(\n.*niveau.*=.*\n)').search(page_content)
                            if re.compile('{{Chapitre[.\n]*(\n.*précédent.*=.*\n)').search(page_content):
                                    print("précédent")
                            if re.compile('{{Chapitre[.\n]*(\n.*suivant.*=.*\n)').search(page_content):
                                    print("suivant")
                    else: # Pas de modèle chapitre
                            print('Pas de chapitre dans :')
                            print(page_name)
                            return
                    input(page_content)'''

                    lecon = ''
                    # Majuscule
                    if page_content.find('Leçon') != -1 and page_content.find('Leçon') < 100:
                            page_content2 = page_content[page_content.find('Leçon'):]
                            lecon = get_value('Leçon', page_content)
                    # Minuscule
                    elif page_content.find('leçon') != -1 and page_content.find('leçon') < 100:
                            page_content2 = page_content[page_content.find('leçon'):]
                            lecon = get_value('leçon', page_content)

                    if lecon.find('|') != -1:
                            lecon = lecon[0:lecon.find('|')]
                    while lecon[0:1] == '[':
                            lecon = lecon[1:len(lecon)]
                    while lecon[len(lecon)-1:len(lecon)] == ']':
                            lecon = lecon[0:len(lecon)-1]
                    if (lecon == '../' or lecon == '') and page_name.find('/') != -1:
                            lecon = page_name[0:page_name.rfind('/')]

                    if lecon != '' and lecon.find('.') == -1:
                        page2 = Page(site,lecon)
                        if page2.exists():
                            if page2.namespace() != 0 and page2.title() != 'User:JackBot/test':
                                return
                            else:
                                try:
                                    page_lecon = page2.get()
                                except pywikibot.exceptions.NoPage as e:
                                    print(str(e))
                                    return
                                except pywikibot.exceptions.IsRedirectPage:
                                    page_lecon = page2.getRedirectTarget().get()
                                except pywikibot.exceptions.LockedPage as e:
                                    print(str(e))
                                    return

                            # Majuscule
                            if page_lecon.find('{{Leçon') != -1:
                                if get_value('Leçon', page_content) == '':
                                    if page_content.find('Leçon') < page_content.find('}}') or page_content.find('Leçon') < page_content.find('}}'):
                                        if get_value('Leçon', page_content) == '':
                                            page_content2 = page_content[page_content.find('Leçon')+len('Leçon'):]
                                            page_content2 = page_content2[:page_content2.find('\n')]
                                            while page_content2[-1:] == ' ' or page_content2[-1:] == '\t':
                                                page_content2 = page_content2[:-1]
                                            if page_content2[-1:] == '=':
                                                final_page_content = final_page_content + page_content[:
                                                    page_content.find('Leçon') + len('Leçon')
                                                    + page_content2.find('=')+1] \
                                                    + page2.title()
                                                page_content = page_content[page_content.find('Leçon') + len('Leçon')
                                                                            + page_content2.find('=')+1:]
                                            else:
                                                print('Signe égal manquant dans :')
                                                print(page_content2[-1:])
                                    else:
                                        final_page_content = final_page_content + '\n|Leçon=' + page2.title()
                                final_page_content = final_page_content + page_content
                                if page_lecon.find('niveau') != -1:
                                    page_content = page_lecon[page_lecon.find('niveau'):]
                                    if page_content.find('=') < page_content.find('\n') and page_content.find('=') != -1:
                                        if get_value('niveau', page_lecon) != -1:
                                            page_content = final_page_content
                                            if page_content.find('{{Chapitre') != -1:
                                                final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                            elif page_content.find('{{chapitre') != -1:
                                                final_page_content = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                                                page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):]
                                            else: return
                                            if page_content.find('niveau') < page_content.find('}}') and page_content.find('niveau') != -1:
                                                page_content2 = page_content[page_content.find('niveau')+len('niveau'):]
                                                while page_content2[:1] == " " or page_content2[:1] == "=":
                                                    page_content2 = page_content2[1:len(page_content2)]
                                                if page_content2[:page_content2.find('\n')] == '':
                                                    final_page_content = final_page_content + page_content[0:page_content.find('niveau')+len('niveau')] + "=" + get_value('niveau', page_lecon)
                                                    page_content = page_content2
                                                elif get_value('niveau', page_lecon) != page_content2[0:page_content2.find('\n')]:
                                                    if debug_level > 0:
                                                        print('Différence de niveau dans ') + page_name + ' : '
                                                        print(get_value('niveau', page_lecon))
                                                        print(page_content2[0:page_content2.find('\n')])
                                            else:
                                                final_page_content = final_page_content + '\n  | niveau      = ' + get_value('niveau', page_lecon)
                                            # print(final_page_content)
                                            # input(page_content)
                            # Minuscule
                            elif page_lecon.find('{{leçon') != -1:
                                if get_value('leçon', page_content) == '':
                                    if page_content.find('leçon') < page_content.find('}}') or page_content.find('leçon') < page_content.find('}}'):
                                        if get_value('leçon', page_content) == '':
                                            page_content2 = page_content[page_content.find('leçon')+len('leçon'):]
                                            page_content2 = page_content2[0:page_content2.find('\n')]
                                            while page_content2[len(page_content2)-1:len(page_content2)] == ' ' or page_content2[len(page_content2)-1:len(page_content2)] == '\t':
                                                page_content2 = page_content2[0:len(page_content2)-1]
                                            if page_content2[len(page_content2)-1:len(page_content2)] == '=':
                                                final_page_content = final_page_content + page_content[0:page_content.find('leçon')+len('leçon')+page_content2.find('=')+1] + page2.title()
                                                page_content = page_content[page_content.find('leçon')+len('leçon')+page_content2.find('=')+1:]
                                            else:
                                                print('Signe égal manquant dans :')
                                                print(page_content2[len(page_content2)-1:len(page_content2)])
                                    else:
                                        final_page_content = final_page_content + '\n|leçon=' + page2.title()
                                final_page_content = final_page_content + page_content
                                page_content = ''
                                if page_lecon.find('niveau') != -1:
                                    niveauLecon = get_value('niveau', page_lecon)
                                    print(niveauLecon)
                                    page_content = page_lecon[page_lecon.find('niveau'):len(page_lecon)]
                                    if page_content.find('=') < page_content.find('\n') and page_content.find('=') != -1:
                                        if niveauLecon != -1:
                                            page_content = final_page_content
                                            if page_content.find('{{Chapitre') != -1:
                                                final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                            elif page_content.find('{{chapitre') != -1:
                                                final_page_content = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                                                page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):]
                                            else:
                                                return
                                            if page_content.find('niveau') < page_content.find('}}') and page_content.find('niveau') != -1:
                                                page_content2 = page_content[page_content.find('niveau')+len('niveau'):]
                                                while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                    page_content2 = page_content2[1:]
                                                niveauChapitre = page_content2[:page_content2.find('\n')]
                                                if niveauChapitre == '':
                                                    final_page_content = final_page_content + page_content[0:page_content.find('niveau')+len('niveau')] + "=" + niveauLecon
                                                    page_content = page_content2
                                                elif niveauChapitre != niveauLecon:
                                                    print('Niveau du chapitre différent de celui de la leçon dans ') + page_name
                                            else:
                                                final_page_content = final_page_content + '\n|niveau=' + niveauLecon

                            final_page_content = final_page_content + page_content
                            page_content = ''
                            # input(final_page_content)

                            '''print(Valeur('niveau',final_page_content))
                            print('********************************************')
                            print(Valeur('numéro',final_page_content))
                            print('********************************************')
                            print(Valeur('précédent',final_page_content))
                            print('********************************************')
                            print(Valeur('suivant',final_page_content))
                            input('Fin de paramètres')'''
                            NumLecon = ''
                            page_content2 = ''
                            if get_value('numéro', final_page_content) == '' \
                                    or get_value('précédent', final_page_content) == ''\
                                    or get_value('suivant', final_page_content) == '':
                                if page_lecon.find(page_name) != -1:
                                        page_content2 = page_lecon[0:page_lecon.find(page_name)]
                                        # Nécessite que le département ait un nom déifférent et que les leçons soient bien nommées différemment
                                elif page_lecon.find(page_name[page_name.rfind('/')+1:len(page_name)]) != -1:
                                        page_content2 = page_lecon[:page_lecon.find(page_name[page_name.rfind('/')+1:])]
                                if page_content2 != '':
                                        while page_content2[len(page_content2)-1:len(page_content2)] == " " \
                                                or page_content2[len(page_content2)-1:len(page_content2)] == "=" \
                                                or page_content2[len(page_content2)-1:len(page_content2)] == "[" \
                                                or page_content2[len(page_content2)-1:len(page_content2)] == "{" \
                                                or page_content2[len(page_content2)-1:len(page_content2)] == "|" \
                                                or page_content2[len(page_content2)-2:len(page_content2)] == "{C" \
                                                or page_content2[len(page_content2)-2:len(page_content2)] == "{c" \
                                                or page_content2[len(page_content2)-2:len(page_content2)] == "{L"\
                                                or page_content2[len(page_content2)-2:len(page_content2)] == "{l":
                                                page_content2 = page_content2[:-1]
                                        if page_content2.rfind(' ') > page_content2.rfind('|'):
                                                NumLecon = page_content2[page_content2.rfind(' ')+1:]
                                        else:
                                                NumLecon = page_content2[page_content2.rfind('|')+1:]
                                        # print(page_content2)
                                        if NumLecon != '' and NumLecon != 'département':
                                            # Le numéro de la leçon permet de remplir les champs : |numéro=, |précédent=, |suivant=
                                            if get_value('numéro', final_page_content) == '':
                                                if final_page_content.find('numéro') == -1:
                                                    page_content = final_page_content
                                                    final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                    page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                                    if page_content.find('numéro') < page_content.find('}}') and page_content.find('numéro') != -1:
                                                        page_content2 = page_content[page_content.find('numéro')+len('numéro'):]
                                                        while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                            page_content2 = page_content2[1:]
                                                        final_page_content = final_page_content + page_content[:page_content.find('numéro')+len('numéro')] + "=" + NumLecon
                                                        page_content = page_content2
                                                    else:
                                                        final_page_content = final_page_content + '\n|numéro=' + NumLecon
                                                    final_page_content = final_page_content + page_content
                                                    page_content = ''
                                            if get_value('précédent', final_page_content) == '' and NumLecon == 1:
                                                page_content = final_page_content
                                                final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                                if page_content.find('précédent') < page_content.find('}}') and page_content.find('précédent') != -1:
                                                    page_content2 = page_content[page_content.find('précédent')+len('précédent'):]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    final_page_content = final_page_content + page_content[0:page_content.find('précédent')+len('précédent')] + "=" + NumLecon
                                                    page_content = page_content2
                                                else:
                                                    final_page_content = final_page_content + '\n|précédent=' + NumLecon
                                                final_page_content = final_page_content + page_content
                                                page_content = ''                                
                                            elif get_value('précédent', final_page_content) == '' and get_value(str(int(NumLecon) - 1), page_lecon) != '':
                                                page_content = final_page_content
                                                final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                                if page_content.find('précédent') < page_content.find('}}') and page_content.find('précédent') != -1:
                                                    page_content2 = page_content[page_content.find('précédent')+len('précédent'):]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    final_page_content = final_page_content + page_content[:page_content.find('précédent')+len('précédent')] + "=" + get_value(str(int(NumLecon) - 1), page_lecon)
                                                    page_content = page_content2
                                                else:
                                                    final_page_content = final_page_content + '\n|précédent=' + get_value(str(int(NumLecon) - 1), page_lecon)
                                                final_page_content = final_page_content + page_content
                                                page_content = ''
                                            if get_value('suivant', final_page_content) == '' and get_value(str(int(NumLecon) + 1), page_lecon) != '':
                                                page_content = final_page_content
                                                final_page_content = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):]
                                                if page_content.find('suivant') < page_content.find('}}') and page_content.find('suivant') != -1:
                                                    page_content2 = page_content[page_content.find('suivant')+len('suivant'):]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    final_page_content = final_page_content + page_content[0:page_content.find('suivant')+len('suivant')] + "=" + get_value(str(int(NumLecon) + 1), page_lecon)
                                                    page_content = page_content2
                                                else:
                                                    if page_content.find('précédent') != -1:
                                                        page_content2 = page_content[page_content.find('précédent'):]
                                                        final_page_content = final_page_content + page_content[0:page_content.find('précédent')+page_content2.find('\n')] + '\n|suivant=' + get_value(str(int(NumLecon) + 1), page_lecon)
                                                        page_content = page_content[page_content.find('précédent')+page_content2.find('\n'):]
                                                    else:
                                                        final_page_content = final_page_content + '\n|suivant=' + get_value(str(int(NumLecon) + 1), page_lecon)
                                                final_page_content = final_page_content + page_content
                                                page_content = ''
                        else:  # Pas de leçon
                            print('Pas de leçon : ')
                            print(lecon.encode(config.console_encoding,'replace'))
                            print('dans : ')
                            print(page_name)
                            # input('Attente')
                        final_page_content = final_page_content + page_content
                        page_content = ''
            elif re.search(r'{{[lL]eçon[ \n|{}]', page_content):
                # Evaluations
                page2 = Page(site,'Discussion:' + page_name)
                if page2.exists():
                    try:
                        talk_page = page2.get()
                    except pywikibot.exceptions.NoPage as e:
                        print(str(e))
                        return
                    except pywikibot.exceptions.IsRedirectPage as e:
                        print(str(e))
                        return
                    except pywikibot.exceptions.LockedPage as e:
                        print(str(e))
                        return
                else: 
                    talk_page = ''
                if talk_page.find('{{Évaluation') == -1 and talk_page.find('{{évaluation') == -1:
                    save_page(page2, '{{Évaluation|idfaculté=' + get_value('idfaculté', page_content) + '|avancement=?}}\n' + talk_page, 'Ajout d\'évaluation inconnue')

                # Synchronisations avec les niveaux des départements, et les évaluations des onglets Discussion:
                #...
            final_page_content = final_page_content + page_content

            # Bas de page
            if (final_page_content.find('{{Chapitre') != -1
                    or final_page_content.find('{{chapitre') != -1) \
                    and final_page_content.find('{{Bas de page') == -1 \
                    and final_page_content.find('{{bas de page') == -1:
                idfaculte = ''
                precedent = ''
                suivant = ''
                if final_page_content.find('idfaculté') != -1:
                    page_content = final_page_content[final_page_content.find('idfaculté'):]
                    idfaculte = page_content[0:page_content.find('\n')]
                    # pb si tout sur la même ligne, faire max(0, min(page_content.find('\n'),?))
                    if final_page_content.find('précédent') != -1:
                        page_content = final_page_content[final_page_content.find('précédent'):]
                        precedent = page_content[0:page_content.find('\n')]
                    if final_page_content.find('suivant') != -1:
                        page_content = final_page_content[final_page_content.find('suivant'):]
                        suivant = page_content[0:page_content.find('\n')]
                    final_page_content = final_page_content + '\n\n{{Bas de page|' + idfaculte + '\n|' + precedent \
                                         + '\n|' + suivant + '}}'

            # Exercices (pb http://fr.wikiversity.org/w/index.php?title=Allemand%2FVocabulaire%2FFormes_et_couleurs&diff=354352&oldid=354343)
            '''page_content = final_page_content
            final_page_content = ''
            while final_page_content.find('{{CfExo') != -1 or final_page_content.find('{{cfExo') != -1:
                page_content = final_page_content[
                if 
                |exercice=[[
                /Exercices/
                /quiz/
            final_page_content = final_page_content + page_content'''

    final_page_content = final_page_content + page_content
    page_content = ''

    if debug_level > 1:
        input('--------------------------------------------------------------------------------------------')
    if current_page_content != final_page_content:
        save_page(page, final_page_content, summary)


# *** Wikiversity functions ***
def get_value(word, page_content):
    # TODO Bug http://fr.wikiversity.org/w/index.php?title=Initiation_%C3%A0_l%27arithm%C3%A9tique/PGCD&diff=prev&oldid=386685'
    return ''
    if re.search(r'\n *' + word + ' *=', page_content):
        value = re.sub(r'\n *' + word + ' *=()[\n|||}|{]', r'$1', page_content)
        if debug_level > 0:
            input(value)
        return value
    '''
    if page_content.find(' ' + word) != page_content.find(word)-1 and page_content.find('|' + word) != page_content.find(word)-1: # Pb du titre_leçon
        page_content2 = page_content[page_content.find(word)+len(word):len(page_content)]
    else:
        page_content2 = page_content
    if page_content2.find(word) == -1:
        return ''
    else:
        page_content2 = page_content2[page_content2.find(word)+len(word):len(page_content2)]
        page_content2 = page_content2[0:page_content2.find('\n')]
        if page_content2.find ('{{C|') != -1:        
            page_content2 = page_content2[page_content2.find ('{{C|')+4:len(page_content2)]
            page_content2 = '[[../' + page_content2[0:page_content2.find ('|')] + '/]]'
        while page_content2[0:1] == ' ' or page_content2[0:1] == '\t' or page_content2[0:1] == '=':
            page_content2 = page_content2[1:len(page_content2)]
        if page_content2[0:3] == '[[/':        
            page_content2 = '[[..' + page_content2[2:len(page_content2)]
        return page_content2
    '''


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)


def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name("Fonctions_d'une_variable_réelle/Continuité")
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            # regex = r'{{[Ee]ncadre *\|[^}]*text-align: center'
            regex = r'text-align'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            p.pages_by_user('User:' + username)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search('insource:text-align: center', namespaces=[0])
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Modèle:Encadre')
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            after_page = ''
            if len(sys.argv) > 2: after_page = sys.argv[2]
            p.pages_by_cat('Catégorie:Pages utilisant des liens magiques ISBN', namespaces=None, after_page=after_page)
            p.pages_by_cat('Catégorie:Pages avec ISBN invalide', namespaces=None, after_page=after_page)
        elif sys.argv[1] == '-redirects':
            p.pages_by_redirects()
        elif sys.argv[1] == '-all':
           p.pages_by_all()
        elif sys.argv[1] == '-RC':
            while 1:
                p.pages_by_rc_last_day()
        elif sys.argv[1] == '-nocat':
            global do_add_category
            do_add_category = True
            p.pages_by_special_not_categorized()
            p.pages_by_cat('Catégorie:Chapitres sans pied de page', namespaces=[0])
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(sys.argv[1])
    else:
        while 1:
            p.pages_by_rc()


if __name__ == "__main__":
    main(sys.argv)

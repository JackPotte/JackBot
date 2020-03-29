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
import sys
import pywikibot
from pywikibot import *
try:
    from src.lib import *
except ImportError:
    from lib import *

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level= 1
        sys.argv.remove(debugAlias)

file_name = __file__
if debug_level > 0: print(file_name)
if file_name.rfind('/') != -1: file_name = file_name[file_name.rfind('/')+1:]
site_language = file_name[:2]
if debug_level > 1: print(site_language)
site_family = file_name[3:]
site_family = site_family[:site_family.find('.')]
if debug_level > 1: print(site_family)
site = pywikibot.Site(site_language, site_family)
username = config.usernames[site_family][site_language]

checkURL = False
fix_tags = False
fixFiles = True
fixTemplates = False
addCategory = False


oldParameters = []
newParameters = []
oldParameters.append('numero')
newParameters.append('numéro')

# https://fr.wikiversity.org/wiki/Catégorie:Modèles_de_l'université
categorizingTemplates = []
categorizingTemplates.append('Faculté')
categorizingTemplates.append('Département')
categorizingTemplates.append('Cours')
categorizingTemplates.append('Leçon')
categorizingTemplates.append('Chapitre')
categorizingTemplates.append('Annexe')
categorizingTemplates.append('Quiz')

subPages = []
# {{leçon}}
subPages.append('Présentation de la leçon')
subPages.append('Objectifs')
subPages.append('Prérequis conseillés')
subPages.append('Référents')
subPages.append('Post-notions')
# {{cours}}
subPages.append('Présentation du cours')
subPages.append('Leçons')
subPages.append('Fiche')
subPages.append('Feuille d\'exercices')
subPages.append('Annexe')
subPages.append('Voir aussi')
# {{département}}
subPages.append('Présentation du département')
subPages.append('Leçons par thèmes')
subPages.append('Leçons par niveaux')
subPages.append('Contributeurs')

# {{faculté}}
subPages.append('Présentation de la faculté')
subPages.append('Départements')
subPages.append('Transverse')

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
    if debug_level > 0: print('------------------------------------')
    print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    page_content = current_page_content
    PageEnd = '' # On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première

    page_content = global_operations(page_content)
    if fixFiles: page_content = replace_files_errors(page_content)
    if fix_tags: page_content = replace_deprecated_tags(page_content)
    if checkURL: page_content = hyper_lynx(page_content)
        
    page_content = page_content.replace('[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
    page_content = page_content.replace('[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', '{{AutoCat}}')
    page_content = page_content.replace('{{autoCat}}', '{{AutoCat}}')
    if addCategory and page_name.find('/') != -1:
        subPage_name = page_name[page_name.rfind('/')+1:]
        if debug_level > 0: print(subPage_name)
        if subPage_name in subPages and page_content.find('[[Catégorie:') == -1 and page_content.find('{{AutoCat}}') == -1 and page_content.find('{{imprimable') == -1:
            page_content = page_content + '\n\n{{AutoCat}}'
            summary = summary + ', [[Spécial:Pages non catégorisées]]'

    if page.namespace() == 0:
        # Remplacements consensuels (ex : numero -> numéro)
        if debug_level > 1: print(' Balises désuètes <center>')
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
        nestedTag = r'[^<]*(?:<(.*?)>|.)*[^<]*'
        regex = r'<div style *= *"text\-align: *center;">(' + nestedTag + r')</div>'
        if re.search(regex, page_content):
            summary += ', [[Modèle:centrer]]'
            page_content = re.sub(regex, r'{{centrer|\1}}', page_content, re.DOTALL)

        # Fix parameters
        for p in range(1, len(oldParameters)-1):
            if page_content.find('{{' + temp[p] + '|') != -1 or page_content.find('{{' + oldParameters[p] + '}}') != -1:
                page_content = page_content[0:page_content.find(temp[p])] + newParameters[p] + page_content[page_content.find(temp[p])+len(temp[p]):]

        # https://fr.wikiversity.org/wiki/Catégorie:Chapitres_sans_pied_de_page
        if re.search('{{[cC]hapitre[ \n|]', page_content) and not re.search('{{[bB]as de page[ \n|]', page_content):
            chapter = get_template_by_name(page_content, 'chapitre')
            if chapter != '':
                footer = '\n\n{{Bas de page\n'
                for p in ['idfaculté', 'leçon', 'précédent', 'suivant']:
                    parameter = get_parameter(chapter, p)
                    if len(parameter) > 0:
                        footer = footer + '  |' + parameter
                footer = footer + '}}'
                page_content = page_content + footer

        # http://fr.wikiversity.org/wiki/Catégorie:Modèle_mal_utilisé
        if fixTemplates == True:
            if re.search('{{[cC]hapitre[ \n|{}]', page_content):
                    ''' Bug du modèle tronqué :
                    if re.compile('{Chapitre').search(page_content):
                            if re.compile('{Chapitre[.\n]*(\n.*align.*=.*\n)').search(page_content):
                                    i1 = re.search('{{Chapitre[.\n]*(\n.*align.*=.*\n)',page_content).end()
                                    i2 = re.search('(\n.*align.*=.*\n)',page_content[:i1]).start()
                                    page_content = page_content[:i2] + '\n' + page_content[i1:]
                            PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                            page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                    elif re.compile('{chapitre').search(page_content):
                            if re.compile('{chapitre[.\n]*(\n.*align.*=.*\n)').search(page_content):
                                    i1 = re.search('{{chapitre[.\n]*(\n.*align.*=.*\n)',page_content).end()
                                    i2 = re.search('(\n.*align.*=.*\n)',page_content[:i1]).start()
                                    page_content = page_content[:i2] + '\n' + page_content[i1:]
                            PageEnd = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                            page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):len(page_content)]

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

                    Lecon = ''
                    # Majuscule
                    if page_content.find('Leçon') != -1 and page_content.find('Leçon') < 100:
                            page_content2 = page_content[page_content.find('Leçon'):len(page_content)]
                            Lecon = Valeur('Leçon',page_content)
                    # Minuscule
                    elif page_content.find('leçon') != -1 and page_content.find('leçon') < 100:
                            page_content2 = page_content[page_content.find('leçon'):len(page_content)]
                            Lecon = Valeur('leçon',page_content)
                    #input(Lecon)

                    if Lecon.find('|') != -1:
                            Lecon = Lecon[0:Lecon.find('|')]
                    while Lecon[0:1] == '[':
                            Lecon = Lecon[1:len(Lecon)]
                    while Lecon[len(Lecon)-1:len(Lecon)] == ']':
                            Lecon = Lecon[0:len(Lecon)-1]
                    if (Lecon == '../' or Lecon == '') and page_name.find('/') != -1:
                            Lecon = page_name[0:page_name.rfind('/')]
                    #input(Lecon)

                    if Lecon != '' and Lecon.find('.') == -1: 
                        page2 = Page(site,Lecon)
                        if page2.exists():
                            if page2.namespace() != 0 and page2.title() != 'User:JackBot/test':
                                return
                            else:
                                try:
                                    PageLecon = page2.get()
                                except pywikibot.exceptions.NoPage:
                                    print("NoPage")
                                    return
                                except pywikibot.exceptions.IsRedirectPage:
                                    PageLecon = page2.getRedirectTarget().get()
                                except pywikibot.exceptions.LockedPage:
                                    print("Locked/protected page")
                                    return
                            #input(PageLecon)

                            # Majuscule
                            if PageLecon.find('{{Leçon') != -1:
                                if Valeur('Leçon',page_content) == '':
                                    if page_content.find('Leçon') < page_content.find('}}') or page_content.find('Leçon') < page_content.find('}}'):
                                        if Valeur('Leçon',page_content) == '':
                                            page_content2 = page_content[page_content.find('Leçon')+len('Leçon'):len(page_content)]
                                            page_content2 = page_content2[0:page_content2.find('\n')]
                                            while page_content2[len(page_content2)-1:len(page_content2)] == ' ' or page_content2[len(page_content2)-1:len(page_content2)] == '\t':
                                                page_content2 = page_content2[0:len(page_content2)-1]
                                            if page_content2[len(page_content2)-1:len(page_content2)] == '=':
                                                PageEnd = PageEnd + page_content[0:page_content.find('Leçon')+len('Leçon')+page_content2.find('=')+1] + page2.title()
                                                page_content = page_content[page_content.find('Leçon')+len('Leçon')+page_content2.find('=')+1:len(page_content)]
                                            else:
                                                print('Signe égal manquant dans :')
                                                print(page_content2[len(page_content2)-1:len(page_content2)])
                                    else:
                                        PageEnd = PageEnd + '\n|Leçon=' + page2.title()
                                PageEnd = PageEnd + page_content
                                if PageLecon.find('niveau') != -1:
                                    page_content = PageLecon[PageLecon.find('niveau'):len(PageLecon)]
                                    if page_content.find('=') < page_content.find('\n') and page_content.find('=') != -1:
                                        if Valeur('niveau',PageLecon) != -1:
                                            page_content = PageEnd
                                            if page_content.find('{{Chapitre') != -1:
                                                PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                            elif page_content.find('{{chapitre') != -1:
                                                PageEnd = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                                                page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):len(page_content)]
                                            else: return
                                            if page_content.find('niveau') < page_content.find('}}') and page_content.find('niveau') != -1:
                                                page_content2 = page_content[page_content.find('niveau')+len('niveau'):len(page_content)]
                                                while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                    page_content2 = page_content2[1:len(page_content2)]
                                                if page_content2[0:page_content2.find('\n')] == '':
                                                    PageEnd = PageEnd + page_content[0:page_content.find('niveau')+len('niveau')] + "=" + Valeur('niveau', PageLecon)
                                                    page_content = page_content2
                                                elif Valeur('niveau',PageLecon) != page_content2[0:page_content2.find('\n')]:
                                                    if debug_level > 0:
                                                        print('Différence de niveau dans ') + page_name + ' : '
                                                        print(Valeur('niveau',PageLecon))
                                                        print(page_content2[0:page_content2.find('\n')])
                                            else:
                                                PageEnd = PageEnd + '\n  | niveau      = ' + Valeur('niveau',PageLecon)
                                            #print(PageEnd)
                                            #input(page_content)
                            # Minuscule
                            elif PageLecon.find('{{leçon') != -1:
                                if Valeur('leçon',page_content) == '':
                                    if page_content.find('leçon') < page_content.find('}}') or page_content.find('leçon') < page_content.find('}}'):
                                        if Valeur('leçon',page_content) == '':
                                            page_content2 = page_content[page_content.find('leçon')+len('leçon'):len(page_content)]
                                            page_content2 = page_content2[0:page_content2.find('\n')]
                                            while page_content2[len(page_content2)-1:len(page_content2)] == ' ' or page_content2[len(page_content2)-1:len(page_content2)] == '\t':
                                                page_content2 = page_content2[0:len(page_content2)-1]
                                            if page_content2[len(page_content2)-1:len(page_content2)] == '=':
                                                PageEnd = PageEnd + page_content[0:page_content.find('leçon')+len('leçon')+page_content2.find('=')+1] + page2.title()
                                                page_content = page_content[page_content.find('leçon')+len('leçon')+page_content2.find('=')+1:len(page_content)]
                                            else:
                                                print('Signe égal manquant dans :')
                                                print(page_content2[len(page_content2)-1:len(page_content2)])
                                    else:
                                        PageEnd = PageEnd + '\n|leçon=' + page2.title()
                                PageEnd = PageEnd + page_content
                                page_content = ''
                                if PageLecon.find('niveau') != -1:
                                    niveauLecon = Valeur('niveau',PageLecon)
                                    print(niveauLecon)
                                    page_content = PageLecon[PageLecon.find('niveau'):len(PageLecon)]
                                    if page_content.find('=') < page_content.find('\n') and page_content.find('=') != -1:
                                        if niveauLecon != -1:
                                            page_content = PageEnd
                                            if page_content.find('{{Chapitre') != -1:
                                                PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                            elif page_content.find('{{chapitre') != -1:
                                                PageEnd = page_content[0:page_content.find('{{chapitre')+len('{{chapitre')]
                                                page_content = page_content[page_content.find('{{chapitre')+len('{{chapitre'):len(page_content)]
                                            else: return
                                            if page_content.find('niveau') < page_content.find('}}') and page_content.find('niveau') != -1:
                                                page_content2 = page_content[page_content.find('niveau')+len('niveau'):len(page_content)]
                                                while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                    page_content2 = page_content2[1:len(page_content2)]
                                                niveauChapitre = page_content2[0:page_content2.find('\n')]
                                                if niveauChapitre == '':
                                                    PageEnd = PageEnd + page_content[0:page_content.find('niveau')+len('niveau')] + "=" + niveauLecon
                                                    page_content = page_content2
                                                elif niveauChapitre != niveauLecon:
                                                    print('Niveau du chapitre différent de celui de la leçon dans ') + page_name
                                            else:
                                                PageEnd = PageEnd + '\n|niveau=' + niveauLecon

                            PageEnd = PageEnd + page_content
                            page_content = ''
                            #input(PageEnd)

                            '''print(Valeur('niveau',PageEnd))
                            print('********************************************')
                            print(Valeur('numéro',PageEnd))
                            print('********************************************')
                            print(Valeur('précédent',PageEnd))
                            print('********************************************')
                            print(Valeur('suivant',PageEnd))
                            input('Fin de paramètres')'''
                            NumLecon = ''
                            page_content2 = ''
                            if Valeur('numéro',PageEnd) == '' or Valeur('précédent',PageEnd) == '' or Valeur('suivant',PageEnd) == '':
                                if PageLecon.find(page_name) != -1:
                                        page_content2 = PageLecon[0:PageLecon.find(page_name)]    # Nécessite que le département ait un nom déifférent et que les leçons soient bien nommées différemment
                                elif PageLecon.find(page_name[page_name.rfind('/')+1:len(page_name)]) != -1:
                                        page_content2 = PageLecon[0:PageLecon.find(page_name[page_name.rfind('/')+1:len(page_name)])]
                                if page_content2 != '':
                                        while page_content2[len(page_content2)-1:len(page_content2)] == " " or page_content2[len(page_content2)-1:len(page_content2)] == "=" or page_content2[len(page_content2)-1:len(page_content2)] == "[" or page_content2[len(page_content2)-1:len(page_content2)] == "{" or page_content2[len(page_content2)-1:len(page_content2)] == "|" or page_content2[len(page_content2)-2:len(page_content2)] == "{C" or page_content2[len(page_content2)-2:len(page_content2)] == "{c" or page_content2[len(page_content2)-2:len(page_content2)] == "{L" or page_content2[len(page_content2)-2:len(page_content2)] == "{l":
                                                page_content2 = page_content2[0:len(page_content2)-1]
                                        if page_content2.rfind(' ') > page_content2.rfind('|'):
                                                NumLecon = page_content2[page_content2.rfind(' ')+1:len(page_content2)]
                                        else:
                                                NumLecon = page_content2[page_content2.rfind('|')+1:len(page_content2)]
                                        #print(page_content2)
                                        if NumLecon != '' and NumLecon != 'département':
                                            # Le numéro de la leçon permet de remplir les champs : |numéro=, |précédent=, |suivant=
                                            if Valeur('numéro',PageEnd) == '':
                                                if PageEnd.find('numéro') == -1:
                                                    page_content = PageEnd
                                                    PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                    page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                                    if page_content.find('numéro') < page_content.find('}}') and page_content.find('numéro') != -1:
                                                        page_content2 = page_content[page_content.find('numéro')+len('numéro'):len(page_content)]
                                                        while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                            page_content2 = page_content2[1:len(page_content2)]
                                                        PageEnd = PageEnd + page_content[0:page_content.find('numéro')+len('numéro')] + "=" + NumLecon
                                                        page_content = page_content2
                                                    else:
                                                        PageEnd = PageEnd + '\n|numéro=' + NumLecon
                                                    PageEnd = PageEnd + page_content
                                                    page_content = ''
                                            if Valeur('précédent',PageEnd) == '' and NumLecon    == 1:
                                                page_content = PageEnd
                                                PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                                if page_content.find('précédent') < page_content.find('}}') and page_content.find('précédent') != -1:
                                                    page_content2 = page_content[page_content.find('précédent')+len('précédent'):len(page_content)]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    PageEnd = PageEnd + page_content[0:page_content.find('précédent')+len('précédent')] + "=" + NumLecon
                                                    page_content = page_content2
                                                else:
                                                    PageEnd = PageEnd + '\n|précédent=' + NumLecon
                                                PageEnd = PageEnd + page_content
                                                page_content = ''                                
                                            elif Valeur('précédent',PageEnd) == '' and Valeur(str(int(NumLecon)-1),PageLecon) != '':
                                                page_content = PageEnd
                                                PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                                if page_content.find('précédent') < page_content.find('}}') and page_content.find('précédent') != -1:
                                                    page_content2 = page_content[page_content.find('précédent')+len('précédent'):len(page_content)]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    PageEnd = PageEnd + page_content[0:page_content.find('précédent')+len('précédent')] + "=" + Valeur(str(int(NumLecon)-1),PageLecon)
                                                    page_content = page_content2
                                                else:
                                                    PageEnd = PageEnd + '\n|précédent=' + Valeur(str(int(NumLecon)-1),PageLecon)
                                                PageEnd = PageEnd + page_content
                                                page_content = ''
                                            if Valeur('suivant',PageEnd) == '' and Valeur(str(int(NumLecon)+1),PageLecon) != '':
                                                page_content = PageEnd
                                                PageEnd = page_content[0:page_content.find('{{Chapitre')+len('{{Chapitre')]
                                                page_content = page_content[page_content.find('{{Chapitre')+len('{{Chapitre'):len(page_content)]
                                                if page_content.find('suivant') < page_content.find('}}') and page_content.find('suivant') != -1:
                                                    page_content2 = page_content[page_content.find('suivant')+len('suivant'):len(page_content)]
                                                    while page_content2[0:1] == " " or page_content2[0:1] == "=":
                                                        page_content2 = page_content2[1:len(page_content2)]
                                                    PageEnd = PageEnd + page_content[0:page_content.find('suivant')+len('suivant')] + "=" + Valeur(str(int(NumLecon)+1),PageLecon)
                                                    page_content = page_content2
                                                else:
                                                    if page_content.find('précédent') != -1:
                                                        page_content2 = page_content[page_content.find('précédent'):len(page_content)]
                                                        PageEnd = PageEnd + page_content[0:page_content.find('précédent')+page_content2.find('\n')] + '\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
                                                        page_content = page_content[page_content.find('précédent')+page_content2.find('\n'):len(page_content)]
                                                    else:
                                                        PageEnd = PageEnd + '\n|suivant=' + Valeur(str(int(NumLecon)+1),PageLecon)
                                                PageEnd = PageEnd + page_content
                                                page_content = ''
                        else: # Pas de leçon
                            print('Pas de leçon : ')
                            print(Lecon.encode(config.console_encoding,'replace'))
                            print('dans : ')
                            print(page_name)
                            #input('Attente')
                        PageEnd = PageEnd + page_content
                        page_content = ''
            elif re.search('{{[lL]eçon[ \n|{}]', page_content):
                # Evaluations
                page2 = Page(site,'Discussion:' + page_name)
                if page2.exists():
                    try:
                        PageDisc = page2.get()
                    except pywikibot.exceptions.NoPage:
                        print("NoPage")
                        return
                    except pywikibot.exceptions.IsRedirectPage:
                        print("Redirect page")
                        return
                    except pywikibot.exceptions.LockedPage:
                        print("Locked/protected page")
                        return
                else: 
                    PageDisc = ''
                if PageDisc.find('{{Évaluation') == -1 and PageDisc.find('{{évaluation') == -1: save_page(page2, '{{Évaluation|idfaculté=' + Valeur('idfaculté', page_content) + '|avancement=?}}\n' + PageDisc, 'Ajout d\'évaluation inconnue')

                # Synchronisations avec les niveaux des départements, et les évaluations des onglets Discussion:
                #...
            PageEnd = PageEnd + page_content

            # Bas de page
            if (PageEnd.find('{{Chapitre') != -1 or PageEnd.find('{{chapitre') != -1) and PageEnd.find('{{Bas de page') == -1 and PageEnd.find('{{bas de page') == -1:
                idfaculte = ''
                precedent = ''
                suivant = ''
                if PageEnd.find('idfaculté') != -1:
                    page_content = PageEnd[PageEnd.find('idfaculté'):len(PageEnd)]
                    idfaculte = page_content[0:page_content.find('\n')]    # pb si tout sur la même ligne, faire max(0,min(page_content.find('\n'),?))
                    if PageEnd.find('précédent') != -1:
                        page_content = PageEnd[PageEnd.find('précédent'):len(PageEnd)]
                        precedent = page_content[0:page_content.find('\n')]
                    if PageEnd.find('suivant') != -1:
                        page_content = PageEnd[PageEnd.find('suivant'):len(PageEnd)]
                        suivant = page_content[0:page_content.find('\n')]
                    PageEnd = PageEnd + '\n\n{{Bas de page|' + idfaculte + '\n|' + precedent + '\n|' + suivant + '}}'

            # Exercices (pb http://fr.wikiversity.org/w/index.php?title=Allemand%2FVocabulaire%2FFormes_et_couleurs&diff=354352&oldid=354343)
            '''page_content = PageEnd
            PageEnd = ''
            while PageEnd.find('{{CfExo') != -1 or PageEnd.find('{{cfExo') != -1:
                page_content = PageEnd[
                if 
                |exercice=[[
                /Exercices/
                /quiz/
            PageEnd = PageEnd + page_content'''

    PageEnd = PageEnd + page_content
    page_content = ''

    if debug_level > 1: input('--------------------------------------------------------------------------------------------')
    if current_page_content != PageEnd: save_page(page, PageEnd, summary)


#*** Wikiversity functions ***
def Valeur(Mot, Page):
    #input('Bug http://fr.wikiversity.org/w/index.php?title=Initiation_%C3%A0_l%27arithm%C3%A9tique/PGCD&diff=prev&oldid=386685')
    if re.search('\n *' + Mot + ' *=', Page):
        niveau = re.sub('\n *' + Mot + ' *=()[\n|||}|{]', r'$1', Page)
        if debug_level > 0: input(niveau)
        #return
    '''
    if Page.find(' ' + Mot) != Page.find(Mot)-1 and Page.find('|' + Mot) != Page.find(Mot)-1: # Pb du titre_leçon
        page_content2 = Page[Page.find(Mot)+len(Mot):len(Page)]
    else:
        page_content2 = Page
    if page_content2.find(Mot) == -1:
        return ''
    else:
        page_content2 = page_content2[page_content2.find(Mot)+len(Mot):len(page_content2)]
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
set_globals(debug_level, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1: print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name("Fonctions_d'une_variable_réelle/Continuité")
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            #regex = '{{[Ee]ncadre *\|[^}]*text-align: center'
            regex = 'text-align'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            p.pages_by_user('User:' + username)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search('insource:text-align: center', namespaces = [0])
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Modèle:Encadre')
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            afterPage = ''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pages_by_cat('Catégorie:Pages utilisant des liens magiques ISBN', namespaces = None, afterPage = afterPage)
            p.pages_by_cat('Catégorie:Pages avec ISBN invalide', namespaces = None, afterPage = afterPage)
        elif sys.argv[1] == '-redirects':
            p.pages_by_redirects()
        elif sys.argv[1] == '-all':
           p.pages_by_all()
        elif sys.argv[1] == '-RC':
            while 1:
                p.pages_by_rc_last_day()
        elif sys.argv[1] == '-nocat':
            global addCategory
            addCategory = True
            p.pages_by_special_not_categorized()
            p.pages_by_cat('Catégorie:Chapitres sans pied de page', namespaces = [0])
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(sys.argv[1])
    else:
        while 1:
            p.pages_by_rc()

if __name__ == "__main__":
    main(sys.argv)

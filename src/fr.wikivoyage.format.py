#!/usr/bin/env python
# coding: utf-8
"""
Ce script formate Wikivoyage
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


def treat_page_by_name(page_name):
    print(page_name)
    summary = 'Formatage'
    page = Page(site, page_name)
    current_page_content = get_content_from_page(page, 'All')
    PageTemp = current_page_content
    PageEnd = ''

    PageTemp = global_operations(PageTemp)
    if fixFiles: PageTemp = replace_files_errors(PageTemp)
    if fix_tags: PageTemp = replace_deprecated_tags(PageTemp)
    if checkURL: PageTemp = hyper_lynx(PageTemp)

    PageTemp = PageTemp.replace('\n,', ',')

    # Traitements des modèles
    templates = ['Aller', 'Circuler', 'Voir', 'Faire', 'Acheter', 'Manger', 'Sortir', 'Se loger', 'Destination',
        'Listing', 'Représentation diplomatique', 'Marqueur', 'Ville'
    ]
    parameters = [
        ['handicap', 'description', 'Handicap'],
        ['wifi', 'description', 'Wi-Fi'],
        #['numéro gratuit', 'téléphone'],
        #['téléphone portable', 'téléphone'],
    ]
    #for template in templates:
    for parameter in parameters:
        #PageTemp = mergeParameters(PageTemp, template, parameter)
        PageTemp = search_doubles(PageTemp, parameter)

    # Analyse des crochets et accolades (à faire : hors LaTex)
    if PageTemp.count('{') - PageTemp.count('}') != 0:
        if page_name.find('User:JackBot/') == -1: log('*[[' + page_name + ']] : accolade cassée')
        #if debug_level > 1: raise Exception('Accolade cassée')
    if PageTemp.count('[') - PageTemp.count(']') != 0:
        if page_name.find('User:JackBot/') == -1: log('*[[' + page_name + ']] : crochet cassé')
        #if debug_level > 1: raise Exception('Crochet cassé')
    if current_page_content.count('[[') - current_page_content.count(']]') != PageTemp.count('[[') - PageTemp.count(']]'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + '\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debug_level > 0: print('Crochets cassés')    #raise Exception('Crochets cassés')
        return
    if current_page_content.count('{{') - current_page_content.count('}}') != PageTemp.count('{{') - PageTemp.count('}}'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + '\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debug_level > 0: print('Accolades cassées')    #raise Exception('Accolades cassées')
        return

    # Sauvegarde
    PageEnd = PageTemp
    if PageEnd != current_page_content:
        save_page(page, PageEnd, summary)


def mergeParameters(PageTemp, template, parameter):
    if debug_level > 1:
        print(template + ' : ' + parameter[0] + ' => ' + parameter[1])
    PageEnd = ''

    tRegex = r'{{[' + template[:1].lower() + '|' + template[:1].upper() + ']' + template[1:] + r'([^\|}]*\|)'
    if debug_level > 1:
        print(str(len(re.findall(tRegex, PageTemp))) + ' ' + template)
    while re.search(tRegex, PageTemp):
        # Positionnement au premier paramètre du modèle à modifier
        PageEnd = PageEnd + PageTemp[:re.search(tRegex, PageTemp).end()+len('{{' + template)]
        PageTemp = PageTemp[re.search(tRegex, PageTemp).end()+len('{{' + template):]

        # Recherche du paramètre dans le modèle courant
        pRegex = r'\| *' + parameter[0] + r' *=[^}\|]*'
        nRegex = r' *' + parameter[0] + r' *='
        while not re.match(pRegex, PageTemp, re.MULTILINE) and ( \
            (PageTemp.find('{{') < PageTemp.find('}}') and PageTemp.find('{{') != -1) or \
            (PageTemp.find('|') < PageTemp.find('}}') and PageTemp.find('|') != -1) \
        ) :
            #if template == 'Se loger': input(PageTemp[:PageTemp.find('}}')])
            if PageTemp.find('}}') < PageTemp.find('|') or (PageTemp.find('{{') < PageTemp.find('|') and PageTemp.find('{{') != -1):
                PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                PageTemp = PageTemp[PageTemp.find('}}')+2:]
            else:
                PageEnd = PageEnd + PageTemp[:PageTemp.find('|')+1]
                PageTemp = PageTemp[PageTemp.find('|')+1:]

                if re.match(nRegex, PageTemp, re.MULTILINE):
                    PageEnd = PageEnd[:-1]
                    PageTemp = '|' + PageTemp

        if re.match(pRegex, PageTemp, re.MULTILINE):
            if debug_level > 0:
                print(' ' + parameter[0] + ' trouvé dans ' + template + ' en ' + str(re.match(pRegex, PageTemp, re.MULTILINE).start()))

            # Capitalisation des modèles
            PageEnd = re.sub(tRegex, r'{{' + template + r'\1', PageEnd)
            PageTemp = re.sub(tRegex, r'{{' + template + r'\1', PageTemp)

            modele = PageTemp[re.match(pRegex, PageTemp, re.MULTILINE).start():re.match(pRegex, PageTemp, re.MULTILINE).end()]
            if debug_level > 1: print(' retrait de : ') + modele
            PageTemp = PageTemp[:re.match(pRegex, PageTemp, re.MULTILINE).start()] + PageTemp[re.match(pRegex, PageTemp, re.MULTILINE).end():]
            modele = trim(modele[modele.find('=')+1:])

            # Fusion de l'ancien paramètre trouvé
            if modele != '' and len(parameter) > 1:
                # Dans le modèle courant, après les modèles imbriqués, voire parameter[1] s'il n'existe pas
                #regex = r'\| *' + parameter[1] + r' *=({{.*?}}|.)*$' + re.search = modèle précédent
                #regex = r'\| *' + parameter[1] + r' *=[^{}]*$' + re.match = modèle suivant
                regex = r'\| *' + parameter[1] + r' *=[^{}]*$'    # Si rien, tél dans mdl suivant, sinon mdl précédent, d'où le rfind à la place
                if re.search(regex, PageEnd, re.MULTILINE):
                    if debug_level > 0: print(' paramètre : ') + parameter[1] + '= situé avant ' + parameter[0] + '='
                    if debug_level > 1: input(PageEnd[re.search(regex, PageEnd, re.MULTILINE).end():])
                    if PageEnd.rfind(template) != -1:
                        PageTemp = PageEnd[PageEnd.rfind(template):] + PageTemp
                        PageEnd = PageEnd[:PageEnd.rfind(template)]
                    else:
                        return PageEnd + PageTemp

                regex = r'^({{.*?}}|.)*\| *' + parameter[1] + r' *='
                while PageTemp.find('{{') != -1 and PageTemp.find('}}') != -1 and PageTemp.find('{{') < PageTemp.find('}}') \
                    and (not re.search(regex, PageTemp, re.MULTILINE) or re.search(regex, PageTemp, re.MULTILINE).end() > PageTemp.find('}}')):
                    PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                    PageTemp = PageTemp[PageTemp.find('}}')+2:]

                if not re.search(regex, PageTemp, re.MULTILINE):
                    # BUG
                    if debug_level > 1: print(' ajout du paramètre : ') + parameter[1]
                    PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')]
                    PageTemp = '| ' + parameter[1] + ' = ' + PageTemp[PageTemp.find('}}'):]
                else:
                    if debug_level > 1: print(' paramètre ') + parameter[1] + ' existant'
                    PageEnd = PageEnd + PageTemp[:re.search(regex, PageTemp, re.MULTILINE).end()]
                    PageTemp = PageTemp[re.search(regex, PageTemp, re.MULTILINE).end():]

                if len(parameter) > 2:
                    # à proposer ? if modele == 'non défini': parameter[2] = ''
                    newTemplate = '{{' + parameter[2] + '|' + modele + '}} '
                else:
                    if modele.find('(') != -1:
                        newTemplate = modele
                    else:
                        newTemplate = modele + ' (' + parameter[0] + ')'

                    # Après le contenu du paramètre
                    regex = r'[^\|}]*'
                    if re.match(regex, PageTemp, re.MULTILINE):
                        PageEnd = PageEnd + PageTemp[:re.match(regex, PageTemp, re.MULTILINE).end()]
                        PageTemp = PageTemp[re.match(regex, PageTemp, re.MULTILINE).end():]

                    while PageEnd[-1:] == ' ':
                        PageEnd = PageEnd[:-1]
                    if PageEnd[-1:] != '=':
                        newTemplate = ', ' + newTemplate
                # Ajout de parameter[0] en début de parameter[1]
                if debug_level > 1: print(' ajout de : ') + newTemplate
                PageEnd = PageEnd + newTemplate

            if debug_level > 1:
                #print(template)
                input(PageTemp[:PageTemp.find('=')])

        elif debug_level > 1:
            print(parameter[0] + ' non trouvé dans ' + template + ' ' + str(len(PageEnd)))

    return PageEnd + PageTemp


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
            treat_page_by_name('Catégorie:Python')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = '\n[ \t]*,'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.page_by_xml(site_language + site_family + '\-.*xml', regex)
        elif sys.argv[1] == '-u':
            p.pages_by_user('User:' + username)
        elif sys.argv[1] == '-search' or sys.argv[1] == '-s' or sys.argv[1] == '-r':
            if len(sys.argv) > 2:
                p.pages_by_search(sys.argv[2])
            else:
                p.pages_by_search('chinois')
        elif sys.argv[1] == '-link' or sys.argv[1] == '-l' or sys.argv[1] == '-template' or sys.argv[1] == '-m':
            p.pages_by_link('Template:autres projets')
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
            p.pages_by_special_not_categorized()
        elif sys.argv[1] == '-lint':
            p.pages_by_special_lint()
        elif sys.argv[1] == '-extlinks':
            p. pages_by_special_link_search('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(html2unicode(sys.argv[1]))
    else:
        while 1:
            p.pages_by_rc()

if __name__ == "__main__":
    main(sys.argv)

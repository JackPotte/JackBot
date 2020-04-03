#!/usr/bin/env python
# coding: utf-8
"""
Ce script importe les sons de Commons dans le Wiktionnaire en français
"""
from __future__ import absolute_import, unicode_literals
import os
import sys
import pywikibot
from pywikibot import *
# JackBot
dir_wt = os.path.dirname(__file__)
dir_src = os.path.dirname(dir_wt)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
from lib import *
from wiktionary import *

debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

site = pywikibot.Site('commons', 'commons')
summary = 'Ajout du son depuis [[commons:Category:Pronunciation]]'


def treat_page_by_name(page_name):
    print(page_name)
    if username in page_name:
        file_name = 'LL-Q143 (epo)-Robin van der Vliet-lipharoj.wav'
    else:
        if page_name[-4:] != '.ogg' and page_name[-4:] != '.oga' and page_name[-4:] != '.wav':
            if debug_level > 0: print(' No supported file format found')
            return
        file_name = page_name
        if page_name.find('File:') == 0: file_name = file_name[len('File:'):]
    fileDesc = file_name[:-len('.ogg')]

    if fileDesc.find('-') == -1:
        if debug_level > 0: print(' No language code found')
        return

    language_code = fileDesc[:fileDesc.find('-')]
    if language_code == 'LL':
        if debug_level > 0: print(' Lingua Libre formats')
        # LL-<Qid de la langue> (<code iso 693-3>)-<Username>-<transcription> (<précision>).wav

        if fileDesc.count('-') > 3:
            if debug_level > 0: print(' Compound word')
            word = fileDesc
            for i in range(3):
                word = word[word.find('-')+1:]
        else:
            word = fileDesc[fileDesc.rfind('-')+1:]

        s = re.search(r'\(([^)]+)\)', fileDesc)
        if s:
            language_code = get_language_code_ISO693_1_from_ISO693_3(s.group(1))
        else:
            if debug_level > 0: print(' No parenthesis found')
            s = re.search(r'-([^\-]+)-[^\-]+$', fileDesc)
            if not s:
                if debug_level > 0: print(' No language code found')
                return
            language_code = get_language_code_ISO693_1_from_ISO693_3(s.group(1))

    else:
        language_code = language_code.lower()
        if language_code == 'qc': language_code = 'fr'
        word = fileDesc[fileDesc.find('-')+1:]
        word = word.replace('-',' ')
        word = word.replace('_',' ')
        word = word.replace('\'',u'’')

    if debug_level > 0:
        print(' Language code: ') + language_code
        print(' Word: ') + word

    region = ''
    if username in page_name:
        page1 = Page(siteDest, page_name)
    else:
        page1 = Page(siteDest, word)
    try:
        current_page_content = page1.get()
    except pywikibot.exceptions.NoPage:
        # Retrait d'un éventuel article ou une région dans le nom du fichier
        word1 = word

        if language_code == 'de':
            if word[0:4] == 'der ' or word[0:4] == 'die ' or word[0:4] == 'das ' or word[0:4] == 'den ':
                word = word[word.find(' ')+1:]
            if word[0:3] == 'at ':
                region = '{{' + word[0:2].upper() + '|nocat=1}}'
                word = word[word.find(' ')+1:]
                
        elif language_code == 'en':
            if word[0:4] == 'the ' or word[0:2] == 'a ':
                word = word[word.find(' ')+1:]
            if word[0:3] == 'au ' or word[0:3] == 'gb ' or word[0:3] == 'ca ' or word[0:3] == 'uk ' or word[0:3] == 'us ':
                region = '{{' + word[0:2].upper() + '|nocat=1}}'
                word = word[word.find(' ')+1:]
            
        elif language_code == 'es':
            if word[0:3] == 'el ' or word[0:3] == 'lo ' or word[0:3] == 'la ' or word[0:3] == 'un ' or word[0:4] == 'uno ' or word[0:4] == 'una ' or word[0:5] == 'unos ' or word[0:5] == 'unas ' or word[0:4] == 'los ':
                word = word[word.find(' ')+1:]
            if word[0:3] == 'mx ' or word[0:3] == 'ar ':
                region = '{{' + word[0:2].upper() + '|nocat=1}}'
                word = word[word.find(' ')+1:]
            if word[0:7] == 'am lat ':
                region = '{{AM|nocat=1}}'
                word = word[word.find(' ')+1:]
                word = word[word.find(' ')+1:]
                
        elif language_code == 'fr':
            if word[:3] == 'le ' or word[:3] == 'la ' or word[:4] == 'les ' or word[:3] == 'un ' or word[:3] == 'une ' or word[:4] == 'des ':
                word = word[word.find(' ')+1:]
            if word[:3] == 'ca ' or word[:3] == 'be ':
                region = '{{' + word[:2].upper() + '|nocat=1}}'
                word = word[word.find(' ')+1:]
            if word[:6] == 'Paris ':
                region = 'Paris (France)'
                word = word[word.find(' ')+1:]
                
        elif language_code == 'it':
            if word[0:3] == "l'" or word[0:3] == 'la ' or word[0:3] == 'le ' or word[0:3] == 'lo ' or word[0:4] == 'gli ' or word[0:3] == 'un ' or word[0:4] == 'uno ' or word[0:4] == 'una ':
                word = word[word.find(' ')+1:]
        
        elif language_code == 'nl':
            if word[0:3] == 'de ' or word[0:4] == 'een ' or word[0:4] == 'het ':
                word = word[word.find(' ')+1:]
                            
        elif language_code == 'pt':
            if word[0:2] == 'a ' or word[0:2] == 'o ' or word[0:3] == 'as ' or word[0:3] == 'os ':
                word = word[word.find(' ')+1:]
            if word[0:3] == 'br ' or word[0:3] == 'pt ':
                region = '{{' + word[0:2].upper() + '|nocat=1}}'

        elif language_code == 'sv':
            if word[0:3] == 'en ' or word[0:4] == 'ett ':
                word = word[word.find(' ')+1:]                
        
        if debug_level > 1: print(' word potentiel : ') + word
        # Deuxième tentative de recherche sur le Wiktionnaire    
        if word != word1:
            page1 = Page(siteDest, word)
            try:
                current_page_content = page1.get()
            except pywikibot.exceptions.NoPage:
                if debug_level > 0: print(' page_content not found 1')
                return
            except pywikibot.exceptions.IsRedirectPage:
                current_page_content = page1.get(get_redirect=True)
        else:
            if debug_level > 0: print(' page_content not found 2')
            return
    except pywikibot.exceptions.IsRedirectPage:
        current_page_content = page1.get(get_redirect=True)
    # à faire : 3e tentative en retirant les suffixes numériques (ex : File:De-aber2.ogg)

    prononciation = ''
    '''
    TODO: getPronunciationFromArticle()
    regex = r'{{pron\|[^\}|]*\|' + language_code + '}}'
    if re.compile(regex).search(current_page_content):
        prononciation = current_page_content[re.search(regex, current_page_content).start()+len('{{pron|'):re.search(regex,current_page_content).end()-len('|'+language_code+u'}}')]
    if debug_level > 1: print(prononciation)
    
    TODO: getUserRegion()
    '''

    if debug_level > 1: print(' word du Wiktionnaire : ') + word
    if current_page_content.find('{{langue|' + language_code) == -1:
        if debug_level > 0: print(' Language section absent')
        return

    if file_name[:1].lower() == file_name[:1]:
        file_nameCap = file_name[:1].upper() + file_name[1:]
    else:
        file_nameCap = file_name[:1].lower() + file_name[1:]
    if file_name in current_page_content or file_nameCap in current_page_content or \
        file_name.replace(' ', '_') in current_page_content or file_nameCap.replace(' ', '_') in current_page_content:
        if debug_level > 0: print(' File already present')
        if debug_level > 1: input(current_page_content)
        return

    page_content = current_page_content
    final_page_content = addPronunciation(page_content, language_code, 'prononciation', '* {{écouter|' + region + '|' + prononciation + '|lang=' + language_code + '|audio=' + file_name + '}}')
    if final_page_content is not None:
        # Hardfixes
        regex = r'{{S\|prononciation}} ===\*'
        if re.search(regex, final_page_content):
            final_page_content = re.sub(regex, r'{{S|prononciation}} ===\n*', final_page_content)
        regex = r'\n\n+(\* {{écouter\|)'
        if re.search(regex, final_page_content):
            final_page_content = re.sub(regex, r'\n\1', final_page_content)

        if final_page_content != current_page_content:
            save_page(page1, final_page_content, summary)


p = PageProvider(treat_page_by_name, site, debug_level)
set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1: print(sys.argv)
        if sys.argv[1] == '-test' or sys.argv[1] == '-t':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2' or sys.argv[1] == '-tu':
            treat_page_by_name('User:' + username + '/test unitaire')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            if len(sys.argv) > 2:
                sound = sys.argv[2]
            else:
                sound = 'File:LL-Q150 (fra)-Pamputt-suivant.wav'
            treat_page_by_name(sound)
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('src/lists/articles_' + site_language + '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = ''
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
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat' or sys.argv[1] == '-c':
            after_page = ''
            if len(sys.argv) > 2: after_page = sys.argv[2]
            p.pages_by_cat('Canadian English pronunciation', after_page = after_page, recursive = True, namespaces = [6])
            p.pages_by_cat('Australian English pronunciation', after_page = after_page, recursive = True, namespaces = [6])
            p.pages_by_cat('British English pronunciation', after_page = after_page, recursive = True, namespaces = [6])
            p.pages_by_cat('U.S. English pronunciation‎', after_page = after_page, recursive = True, namespaces = [6])
            #Bug: too long? p.pagesByCat('Lingua Libre pronunciation-fr', after_page = after_page, recursive = True, namespaces = [6])
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
        else:
            treat_page_by_name(sys.argv[1])
    else:
        p.pages_by_cat('Category:Pronunciation', recursive = True, not_names= ['spoken ', 'Wikipedia', 'Wikinews'])

if __name__ == "__main__":
    main(sys.argv)

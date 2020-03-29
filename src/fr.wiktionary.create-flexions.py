#!/usr/bin/env python
# coding: utf-8
"""
Ce script importe les flexions d'un Wiktionary dans un autre où le lemme se trouve
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

addDefaultSort = False
siteSource = pywikibot.Site('en', site_family)
templateSource = 'en-past of'
textTranslated = 'Passé de'
DebutScan = 'interspersed'
# TODO pluriels fr + en


def treat_page_by_name(page_name):
    if debug_level > 0: print('------------------------------------')
    print(page_name)
    page = Page(site, page_name)
    if not has_more_than_time(page, 1440): return
    if page.exists():
        if page.namespace() != 0 and page.title() != 'User:JackBot/test':
            print(' Autre namespace l 45')
            return
    else:
        print(' Page inexistante')
        return
    PageSing = get_content_from_page(page, 'All')
    if PageSing.find('{{formater') != -1 or PageSing.find('{{SI|') != -1 or PageSing.find('{{SI}}') != -1 or \
        PageSing.find('{{supp|') != -1 or PageSing.find('{{supp}}') != -1 or PageSing.find('{{supprimer|') != -1 or \
        PageSing.find('{{supprimer') != -1 or PageSing.find('{{PàS') != -1 or PageSing.find('{{S|faute') != -1 or \
        PageSing.find('{{S|erreur') != -1:
        if debug_level > 0: print('Page en travaux : non traitée l 65')
        return

    template = [] # Liste des modèles du site à traiter
    param  = [] # paramètre du lemme associé
    template.append('fr-rég-x')
    param.append('s')
    template.append('fr-rég')
    param.append('s')
    #template.append('fr-accord-cons') TODO https://fr.wiktionary.org/w/index.php?title=arnaudes&type=revision&diff=26192327&oldid=26191304
    #param.append('ms')
    # TODO: traiter le reste de [[Catégorie:Modèles d’accord en français]]
    # TODO: 430 faux-positifs corrigés pour les prononciations et |rice=1 des -eur
    #https://fr.wiktionary.org/w/index.php?title=anticonservateurs&type=revision&diff=25375891&oldid=24393947
    #template.append('fr-accord-eur')
    #param.append('1')

    for m in range(0, len(template)):
        if debug_level > 1: print(' début du for ') + str(m) + ', recherche du modèle : ' + template[m]

        if PageSing.find(template[m] + '|') == -1 and PageSing.find(template[m] + '}') == -1:
            if debug_level > 1: pywikibot.output(' Modèle : \03{blue}' + template[m] + '\03{default} absent')
            continue
        else:
            if debug_level > 0: pywikibot.output(' Modèle : \03{blue}' + template[m] + '\03{default} trouvé')
            page_content = PageSing

        language_code = template[m][:2]
        #TODO pronunciation = getParameterValue(template, 2) / class Flexion extends Word
        if debug_level > 1: pron = getPronunciationFromContent(page_content, language_code)

        while page_content.find(template[m]) != -1:
            if len(template[m]) < 3:
                if debug_level > 0: print(' bug')
                break
            if debug_level > 1: 
                print(template[m])
                print(page_content.find(template[m]))

            # Vérification que la langue en cours est bien la langue du modèle
            page_content_till_template = page_content[:page_content.find(template[m])]
            currentLanguage = re.findall(r'{{langue\|([^}]+)}}', page_content_till_template)[-1]
            if currentLanguage != language_code:
                if debug_level > 0: print(' fr-xxx en section étrangère')
                break
                
            # Parcours de la page pour chaque occurence du modèle
            nature = page_content_till_template[page_content_till_template.rfind('{{S|')+len('{{S|'):]
            nature = nature[:nature.find('|')]
            if debug_level > 0:
                try:
                    print('  Nature : ') + nature
                except UnicodeDecodeError:
                    print('  Nature à décoder')
                except UnicodeEncodeError:
                    print('  Nature à encoder')
            if nature == 'erreur' or nature == 'faute':
                print('  section erreur')
                return

            page_content = page_content[page_content.find(template[m])+len(template[m]):]
            plural = getWordPlural(page_content, page_name, template[m])
            if plural is None: return
            if debug_level > 0: print('  Pluriel : ') + plural
            pronunciation = getWordPronunciation(page_content)

            # h aspiré
            H = ''
            if page_content.find('|prefpron={{h aspiré') != -1 and page_content.find('|prefpron={{h aspiré') < page_content.find('}}'):
                H = '|prefpron={{h aspiré}}'
            if page_content.find('|préfpron={{h aspiré') != -1 and page_content.find('|préfpron={{h aspiré') < page_content.find('}}'):
                H = '|préfpron={{h aspiré}}'

            gender = ''
            page_content2 = page_content[page_content.find('\n')+1:len(page_content)]
            while page_content2[:1] == '[' or page_content2[:1] == '\n' and len(page_content2) > 1:
                page_content2 = page_content2[page_content2.find('\n')+1:len(page_content2)]
            if page_content2.find('{{m}}') != -1 and page_content2.find('{{m}}') < page_content2.find('\n'): gender = ' {{m}}'    
            if page_content2.find('{{f}}') != -1 and page_content2.find('{{f}}') < page_content2.find('\n'): gender = ' {{f}}'
            MF = ''
            if page_content2.find('{{mf}}') != -1 and page_content2.find('{{mf}}') < page_content2.find('\n'):
                gender = ' {{mf}}'
                MF = '|mf=oui'
                if PageSing.find('|mf=') == -1:
                    PageSing = PageSing[:PageSing.find(template[m])+len(template[m])] + '|mf=oui' + PageSing[PageSing.find(template[m])+len(template[m]):]
                    save_page(page, PageSing, '|mf=oui')
            if page_content.find('|mf=') != -1 and page_content.find('|mf=') < page_content.find('}}'): MF = '|mf=oui' 

            page2 = Page(site, plural)
            if page2.exists():
                pluralPage = get_content_from_page(page2)
                if pluralPage.find('{{langue|' + language_code + '}}') != -1:
                    if debug_level > 0: print('  Pluriel existant l 216 : ') + plural
                    break
            else:
                if debug_level > 0: print('  Pluriel introuvable l 219')
                pluralPage = ''

            # **************** Pluriel 1 ****************
            if debug_level > 1: print('  Pluriel n°1')
            if plural[-2:] == 'xs':
                print(' Pluriel en xs : erreur')
                return
            elif plural[-2:] == 'ss' and page_name[-2:] != 'ss':
                lemmaParam = '|' + param[m] + '=' + plural[:-2]
                PageSing = PageSing[:PageSing.find(template[m])+len(template[m])] + lemmaParam + \
                    PageSing[PageSing.find(template[m])+len(template[m]):]
                save_page(page, PageSing, '{{' + template[m] + '|s=...}}')
                break
            elif param[m] == '1':
                lemmaParam = ''
            else:
                lemmaParam = '|' + param[m] + '=' + page_name

            flexionTemplate = '{{' + template[m] + pronunciation + H + MF + lemmaParam
            if plural != page_name + 's' and plural != page_name + 'x':
                flexionTemplate += '|p={{subst:PAGENAME}}'
            flexionTemplate += '}}'

            PageEnd = '== {{langue|' + language_code + '}} ==\n=== {{S|' + nature + '|' + \
                language_code + '|flexion}} ===\n' + flexionTemplate + '\n\'\'\'' + plural + '\'\'\' {{pron' + \
                pronunciation + '|' + language_code + '}}' + gender + '\n# \'\'Pluriel de\'\' [[' + page_name +']].\n'
            while PageEnd.find('{{pron|' + language_code + '}}') != -1:
                PageEnd = PageEnd[:PageEnd.find('{{pron|' + language_code + '}}')+7] + '|' + \
                    PageEnd[PageEnd.find('{{pron|' + language_code + '}}')+7:]
            PageEnd = PageEnd + '\n' + pluralPage

            CleTri = default_sort(plural)
            if add_default_sort:
                if PageEnd.find('{{clé de tri') == -1 and CleTri != '' and CleTri.lower() != plural.lower():
                    PageEnd = PageEnd +  '\n{{clé de tri|' + CleTri + '}}\n'
            PageEnd = html2Unicode.html2unicode(PageEnd)

            summary = 'Création du pluriel de [[' + page_name + ']]'
            save_page(page2, PageEnd, summary)

            # TODO: pluriel n°2
            #input(page_content)
            if debug_level > 1: print('  Fin du while')
        if debug_level > 1: print(' Fin du for ') + str(m)


def createPluralFromForeignWiki(Page2):
    page2 = Page(siteSource, Page2)
    page1 = Page(site,Page2)
    if debug_level > 0: print(Page2)
    if page2.exists() and page2.namespace() == 0 and not page1.exists():
        page_content = getPage(page2)
        if page_content == '': return
        # Nature grammaticale
        page_content2 = page_content[:page_content.find(templateSource)]
        # Code langue
        page_content = page_content[page_content.find(templateSource)+len(templateSource)+1:len(page_content)]
        if page_content.find("lang=") != -1 and page_content.find("lang=") < page_content.find('}}'):
            page_content2 = page_content[page_content.find("lang=")+5:len(page_content)]
            if page_content2.find('|') != -1 and page_content2.find('|') < page_content2.find('}}'):
                language_code = page_content2[:page_content2.find("|")]
                page_content = page_content[:page_content.find("lang=")] + page_content[page_content.find("lang=")+5+page_content2.find("|"):]
            else:
                language_code = page_content2[:page_content2.find("}}")]
                page_content = page_content[:page_content.find("lang=")] + page_content[page_content.find("lang=")+5+page_content2.find("}"):]
            if language_code == '': language_code = 'en'
            elif language_code == 'Italian': language_code = 'it'
            elif language_code == 'Irish': language_code = 'ga'
            elif language_code == 'German': language_code = 'de'
            elif language_code == 'Middle English': language_code = 'enm'
            elif language_code == 'Old English': language_code = 'ang'
            elif language_code == 'Dutch': language_code = 'nl'
            elif language_code == 'Romanian': language_code = 'ro'
            elif language_code == 'Spanish': language_code = 'es'
            elif language_code == 'Catalan': language_code = 'ca'
            elif language_code == 'Portuguese': language_code = 'pt'
            elif language_code == 'Russian': language_code = 'ru'
            elif language_code == 'French': language_code = 'fr'
            elif language_code == 'Scots': language_code = 'sco'
            elif language_code == 'Chinese': language_code = 'zh'
            elif language_code == 'Mandarin': language_code = 'zh'
            elif language_code == 'Japanese': language_code = 'ja'
        else:
            language_code = 'en'
        
        while page_content[:1] == ' ' or page_content[:1] == '|':
            page_content = page_content[1:len(page_content)]
        # Lemme
        if page_content.find(']]') != -1 and page_content.find(']]') < page_content.find('}}'): # Si on est dans un lien
            mot = page_content[:page_content.find(']]')+2]
        elif page_content.find('|') != -1 and page_content.find('|') < page_content.find('}}'):
            mot = page_content[:page_content.find('|')]
            # A faire : si dièse on remplace en même temps que les language_code ci-dessous, à patir d'un tableau des langues
        else:
            mot = page_content[:page_content.find('}}')]
        if mot[:2] != '[[': mot = '[[' + mot + ']]'
        
        # On ne crée que les flexions des lemmes existant
        page3 = Page(site, mot[2:-2])
        if page3.exists() == 'False':
            print('Page du lemme absente du Wiktionnaire')
            return
        PageLemme = getPage(page3)
        if PageLemme == '': return
        if PageLemme.find('{{langue|' + language_code + '}}') == -1:
            print(' Paragraphe du lemme absent du Wiktionnaire')
            return
        else:
            # Prononciation
            pron = ''
            PageLemme = PageLemme[PageLemme.find('{{langue|' + language_code + '}}'):]
            if debug_level > 1: input(PageLemme)

            p = re.compile(r'{{pron\|([^}]+)\|en}}')
            result = p.findall(PageLemme)
            if len(result) > 0:
                if debug_level > 0: print(' à partir de {{pron}}')
                r = 0
                while result[r] == '' and r < len(result):
                    r += 1
                pron = result[r]

            elif PageLemme.find('{{en-conj-rég') != -1:
                if debug_level > 0: print(' à partir de {{en-conj-rég')
                pron = PageLemme[PageLemme.find('{{en-conj-rég')+len('{{en-conj-rég'):]
                if pron.find('|inf.pron=') != -1 and pron.find('|inf.pron=') < pron.find('}}'):
                    pron = pron[pron.find('|inf.pron=')+len('|inf.pron='):]
                    if pron.find('}}') < pron.find('|') or pron.find('|') == -1:
                        pron = pron[:pron.find('}}')]
                    else:
                        pron = pron[:pron.find('|')]
                else:
                    pron = ''

            if pron != '':
                # Suffixe du -ed
                letter = pron[-1:]
                if letter in ('f', 'k', 'p', 'θ', 's', 'ʃ'):
                    pron = pron + 't'
                elif letter in ('t', 'd'):
                    pron = pron + 'ɪd' 
                else:
                    pron = pron + 'd'
            if debug_level > 0: print(' prononciation : ') + pron #
        
        if page_content2.rfind('===') == -1:
            return
        else:
            page_content3 = page_content2[:page_content2.rfind('===')]
            nature = page_content3[page_content3.rfind('===')+3:]
            if debug_level > 1: input(nature)
        if nature == 'Noun':
            nature = 'S|nom'
        elif nature == 'Adjective':
            nature = 'S|adjectif'
        elif nature == 'Pronoun':
            nature = 'S|pronom'
        elif nature == 'Verb':
            nature = 'S|verbe'
        else:
            if debug_level > 0: print(' Nature inconnue')
            return
        if debug_level > 0: print(' nature : ') + nature

        Page1 = '== {{langue|' + language_code + '}} ==\n=== {{' + nature + '|' + language_code + '|flexion}} ===\n\'\'\'' + \
            page2.title() + '\'\'\' {{pron|'+pron+'|' + language_code + '}}\n# \'\'Prétérit de\'\' ' + mot + \
            '.\n# \'\'Participe passé de\'\' ' + mot + '.\n\n[[en:' + page2.title() + ']]\n'
        summary = 'Importation depuis [[en:' + page2.title() + ']]'
        save_page(page1, Page1, summary)


def getWordPlural(page_content, page_name, currentTemplate):
    # TODO: getWordPluralByTemplate...
    plural = get_parameter_value(page_content, 'p')
    suffix = get_parameter_value(page_content, 'inv')
    if plural != '' and suffix != '':
        plural = plural + ' ' + suffix

    if plural == '':
        singular = get_parameter_value(page_content, 's')
        if suffix != '':
            if singular == '':
                if debug_level > 0: print('  inv= sans s=')
                return None
            plural = singular + 's ' + suffix
            singular = singular + ' ' + suffix
        elif singular != '' and singular != page_name:
            if debug_level > 0:
                print('  s= ne correspond pas')
                print(singular)
            return None
        else:
            if currentTemplate[-1:] == 'x':
                plural = page_name + 'x'
            else:
                plural = page_name + 's'

            if (plural[-2:] == 'ss' or plural.find('{') != -1) and suffix == '':
                print(' pluriel en -ss')
                return
            if debug_level > 1:
                print('  paramètre du modèle du lemme : ') + page_content[:page_content.find('}}')]

    return trim(plural)
    

def getWordPronunciation(page_content):
    if page_content.find('|pp=') != -1 and page_content.find('|pp=') < page_content.find('}}'):
        if debug_level > 0: print(' pp=')
        page_content2 = page_content[page_content.find('|pp=')+4:page_content.find('}}')]
        if page_content2.find('|') != -1:
            pron = page_content[page_content.find('|pp=')+4:page_content.find('|pp=')+4+page_content2.find('|')]
        else:
            pron = page_content[page_content.find('|pp=')+4:page_content.find('}}')]
    else:
        if debug_level > 1: print('  prononciation identique au singulier')
        pron = page_content[:page_content.find('}}')]
        if debug_level > 1: print('  pron avant while : ') + pron
        if pron.find('|pron=') != -1:
            pron = '|' + pron[pron.find('|pron=')+len('|pron='):]

        TabPron = pron.split('|')
        # {{fr-rég|a.kʁɔ.sɑ̃.tʁik|mf=oui}}
        n = 0
        while n < len(TabPron) and (TabPron[n] == '' or TabPron[n].find('=') != -1):
            if debug_level > 1: print(TabPron[n].find('='))
            n += 1
        if n == len(TabPron):
            pron = '|'
        else:
            pron = '|' + TabPron[n]
        '''
        while pron.find('=') != -1:
            pron2 = pron[:pron.find('=')]
            pron3 = pron[pron.find('='):]
            if debug_level > 0: print('  pron2 : ') + pron2
            if pron2.find('|') == -1:
                pron = pron[pron.find('|')+1:]
                if debug_level > 1: print('  pron dans while1 : ') + pron
            else:
                if debug_level > 0: print('  pron3 : ') + pron3
                if pron3.rfind('|') == -1:
                    limitPron = len(pron3)
                else:
                    limitPron = pron3.rfind('|')
                if debug_level > 0: print('  limitPron : ') + str(limitPron)
                pron = pron[pron.find('=')+limitPron:]
                if debug_level > 0: print('  pron dans while2 : ') + pron
        '''
        if debug_level > 1: print('  pron après while : ') + pron
    pron = trim(pron)
    if pron.rfind('|') > 0:
        pronM = pron[:pron.rfind('|')]
        while pronM.rfind('|') > 0:
            pronM = pronM[:pronM.rfind('|')]
    else:
        pronM = pron
    if pronM[:1] != '|': pronM = '|' + pronM
    if debug_level > 0:
        try:
            print('  Prononciation : ') + pronM
        except UnicodeDecodeError:
            print('  Prononciation à décoder')
        except UnicodeEncodeError:
            print('  Prononciation à encoder')

    return trim(pronM)


p = PageProvider(treat_page_by_name, site, debug_level)
set_globals(debug_level, site, username)
setGlobalsWiktionary(debug_level, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debug_level > 1: print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name('saisie de schéma')
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
        elif sys.argv[1] == '-category' or sys.argv[1] == '-cat':
            afterPage = ''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pages_by_cat('Catégorie:Python', afterPage = afterPage)
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
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(html2unicode(sys.argv[1]))
    else:
        # Daily
        p.pages_by_cat('Catégorie:Pluriels manquants en français', False, '')
        # TODO: python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"

if __name__ == "__main__":
    main(sys.argv)

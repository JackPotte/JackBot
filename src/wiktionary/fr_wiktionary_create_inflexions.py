#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import os
import sys
from pywikibot import config, Page, User
# JackBot
dir_wt = os.path.dirname(__file__)
dir_src = os.path.dirname(dir_wt)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
from lib import *
from html2unicode import *
from default_sort import *
from hyperlynx import *
from languages import *
from page_functions import *
from PageProvider import *
from wiktionary import *
from fr_wiktionary_functions import *

# Global variables
debug_level = 0
debug_aliases = ['-debug', '-d']
for debugAlias in debug_aliases:
    if debugAlias in sys.argv:
        debug_level = 1
        sys.argv.remove(debugAlias)

site_language, site_family, site = get_site_by_file_name(__file__)
username = config.usernames[site_family][site_language]

addDefaultSort = False


def treat_page_by_name(page_name):
    page = Page(site, page_name)
    return treat_page(page)


def treat_page(page):
    if debug_level > 0:
        print('------------------------------------')
    page_name = page.title()
    pywikibot.output("\n\03<<blue>>" + page_name + u"\03<<default>>")

    if not has_more_than_time(page, 1440):
        return
    if page.exists():
        if page.namespace() != 0 and 'Utilisateur:' + username not in page.title():
            print(' untreated namespace')
            return
    else:
        print(' missing page content')
        return

    singular_page = get_content_from_page(page, 'All')
    if singular_page.find('{{formater') != -1 \
            or singular_page.find('{{SI|') != -1 \
            or singular_page.find('{{SI}}') != -1 \
            or singular_page.find('{{supp|') != -1 \
            or singular_page.find('{{supp}}') != -1 \
            or singular_page.find('{{supprimer|') != -1 \
            or singular_page.find('{{supprimer') != -1 \
            or singular_page.find('{{PàS') != -1 \
            or singular_page.find('{{S|faute') != -1 \
            or singular_page.find('{{S|erreur') != -1:
        if debug_level > 0:
            print('page_content en travaux : non traitée')
        return

    template = []  # Liste des modèles du site à traiter
    param = []  # paramètre du lemme associé
    template.append('fr-rég-x')
    param.append('s')
    template.append('fr-rég')
    param.append('s')
    # template.append('fr-accord-cons')
    # TODO https://fr.wiktionary.org/w/index.php?title=arnaudes&type=revision&diff=26192327&oldid=26191304
    # param.append('ms')
    # TODO: traiter le reste de [[Catégorie:Modèles d’accord en français]]
    # TODO: 430 faux-positifs corrigés pour les prononciations et |rice=1 des -eur
    # https://fr.wiktionary.org/w/index.php?title=anticonservateurs&type=revision&diff=25375891&oldid=24393947
    # template.append('fr-accord-eur')
    # param.append('1')

    for m in range(0, len(template)):
        if debug_level > 1:
            print(' début du for ' + str(m) +
                  ', recherche du modèle : ' + template[m])

        if singular_page.find(template[m] + '|') == -1 and singular_page.find(template[m] + '}') == -1:
            if debug_level > 1:
                pywikibot.output(' Modèle : \03<<blue>>' +
                                 template[m] + '\03<<default>> absent')
            continue
        else:
            if debug_level > 0:
                pywikibot.output(' Modèle : \03<<blue>>' +
                                 template[m] + '\03<<default>> trouvé')
            page_content = singular_page

        language_code = template[m][:2]
        # TODO pronunciation = getParameterValue(template, 2) / class Flexion extends Word
        if debug_level > 1:
            pron = getPronunciationFromContent(page_content, language_code)

        while page_content.find(template[m]) != -1:
            if len(template[m]) < 3:
                if debug_level > 0:
                    print(' bug')
                break
            if debug_level > 1:
                print(template[m])
                print(page_content.find(template[m]))

            # Vérification que la langue en cours est bien la langue du modèle
            page_content_till_template = page_content[:page_content.find(
                template[m])]
            current_language = None
            matches = re.findall(
                r'{{langue\|([^}]+)}}', page_content_till_template)
            if len(matches) > 0:
                current_language = matches[-1]
            if current_language != language_code:
                if debug_level > 0:
                    print(' fr-xxx en section étrangère')
                break

            # Parcours de la page pour chaque occurence du modèle
            nature = page_content_till_template[page_content_till_template.rfind(
                '{{S|')+len('{{S|'):]
            nature = nature[:nature.find('|')]
            if debug_level > 0:
                try:
                    print('  Nature : ' + nature)
                except UnicodeDecodeError:
                    print('  Nature à décoder')
                except UnicodeEncodeError:
                    print('  Nature à encoder')
            if nature == 'erreur' or nature == 'faute':
                print('  section erreur')
                return

            page_content = page_content[page_content.find(
                template[m])+len(template[m]):]
            plural = getWordPlural(page_content, page_name, template[m])
            if plural is None:
                return
            if debug_level > 0:
                print('  Pluriel : ' + plural)
            pronunciation = getWordPronunciation(page_content)

            # h aspiré
            H = ''
            if page_content.find('|prefpron={{h aspiré') != -1 \
                    and page_content.find('|prefpron={{h aspiré') < page_content.find('}}'):
                H = '|prefpron={{h aspiré}}'
            if page_content.find('|préfpron={{h aspiré') != -1 \
                    and page_content.find('|préfpron={{h aspiré') < page_content.find('}}'):
                H = '|préfpron={{h aspiré}}'

            gender = ''
            page_content2 = page_content[page_content.find(
                '\n')+1:len(page_content)]
            while page_content2[:1] == '[' or page_content2[:1] == '\n' and len(page_content2) > 1:
                page_content2 = page_content2[page_content2.find(
                    '\n')+1:len(page_content2)]
            if page_content2.find('{{m}}') != -1 and page_content2.find('{{m}}') < page_content2.find('\n'):
                gender = ' {{m}}'
            if page_content2.find('{{f}}') != -1 and page_content2.find('{{f}}') < page_content2.find('\n'):
                if '' == gender:
                    gender = ' {{f}}'
                else:
                    gender = ' {{mf}}'

            MF = ''
            if page_content2.find('{{mf}}') != -1 and page_content2.find('{{mf}}') < page_content2.find('\n'):
                gender = ' {{mf}}'
                MF = '|mf=oui'
                if singular_page.find('|mf=') == -1:
                    singular_page = singular_page[:singular_page.find(template[m])+len(template[m])] + '|mf=oui' \
                        + singular_page[singular_page.find(template[m])+len(template[m]):]
                    save_page(page, singular_page, '|mf=oui')
            if page_content.find('|mf=') != -1 and page_content.find('|mf=') < page_content.find('}}'):
                MF = '|mf=oui'

            page2 = Page(site, plural)
            if page2.exists():
                plural_page = get_content_from_page(page2, 'All')
                if plural_page.find('{{langue|' + language_code + '}}') != -1:
                    if debug_level > 0:
                        print('  Pluriel existant l 216 : ' + plural)
                    break
            else:
                if debug_level > 0:
                    print('  Pluriel introuvable l 219')
                plural_page = ''

            # **************** Pluriel 1 ****************
            if debug_level > 1:
                print('  Pluriel n°1')
            if plural[-2:] == 'xs':
                print(' Pluriel en xs : ' + plural)
                log('*[[' + page_name + ']]')
                return
            elif plural[-2:] == 'ss' and page_name[-2:] != 'ss':
                lemma_param = '|' + param[m] + '=' + plural[:-2]
                singular_page = singular_page[:singular_page.find(template[m])+len(template[m])] + lemma_param + \
                    singular_page[singular_page.find(
                        template[m])+len(template[m]):]
                save_page(page, singular_page, '{{' + template[m] + '|s=...}}')
                break
            elif param[m] == '1':
                lemma_param = ''
            else:
                lemma_param = '|' + param[m] + '=' + page_name

            flexion_template = '{{' + template[m] + \
                pronunciation + H + MF + lemma_param
            if plural != page_name + 's' and plural != page_name + 'x':
                flexion_template += '|p={{subst:PAGENAME}}'
            flexion_template += '}}'

            final_page_content = '== {{langue|' + language_code + '}} ==\n=== {{S|' + nature + '|' + \
                language_code + '|flexion}} ===\n' + flexion_template + '\n\'\'\'' + plural + '\'\'\' {{pron' + \
                pronunciation + '|' + language_code + '}}' + gender + \
                '\n# \'\'Pluriel de\'\' [[' + page_name + ']].\n'
            while final_page_content.find('{{pron|' + language_code + '}}') != -1:
                final_page_content = final_page_content[:final_page_content.find('{{pron|' + language_code + '}}')+7] \
                    + '|' + \
                    final_page_content[final_page_content.find(
                        '{{pron|' + language_code + '}}')+7:]
            final_page_content = final_page_content + '\n' + plural_page

            default_sort = sort_by_encoding(plural)
            if add_default_sort:
                if final_page_content.find('{{clé de tri') == -1 and default_sort != '' \
                        and default_sort.lower() != plural.lower():
                    final_page_content = final_page_content + \
                        '\n{{clé de tri|' + default_sort + '}}\n'
            final_page_content = update_html_to_unicode(final_page_content)

            summary = 'Création du pluriel de [[' + page_name + ']]'
            save_page(page2, final_page_content, summary)

            # TODO: pluriel n°2
            if debug_level > 1:
                print('  Fin du while')
        if debug_level > 1:
            print(' Fin du for ' + str(m))


def getWordPlural(page_content, page_name, current_template):
    # TODO: getWordPluralByTemplate...
    plural = get_parameter_value(page_content, 'p')
    suffix = get_parameter_value(page_content, 'inv')
    if plural != '' and suffix != '':
        plural = plural + ' ' + suffix

    if plural == '':
        singular = get_parameter_value(page_content, 's')
        if suffix != '':
            if singular == '':
                if debug_level > 0:
                    print('  inv= sans s=')
                return None
            plural = singular + 's ' + suffix
            singular = singular + ' ' + suffix
        elif singular != '' and singular != page_name:
            if debug_level > 0:
                print('  s= ne correspond pas')
                print(singular)
            return None
        else:
            if current_template[-1:] == 'x':
                plural = page_name + 'x'
            else:
                plural = page_name + 's'

            if (plural[-2:] == 'ss' or plural.find('{') != -1) and suffix == '':
                print(' Pluriel en -ss : ' + plural)
                log('*[[' + page_name + ']]')
                return
            if debug_level > 1:
                print('  paramètre du modèle du lemme : ' +
                      page_content[:page_content.find('}}')])

    return trim(plural)


def getWordPronunciation(page_content):
    if page_content.find('|pp=') != -1 and page_content.find('|pp=') < page_content.find('}}'):
        if debug_level > 0:
            print(' pp=')
        page_content2 = page_content[page_content.find(
            '|pp=')+4:page_content.find('}}')]
        if page_content2.find('|') != -1:
            pron = page_content[page_content.find(
                '|pp=')+4:page_content.find('|pp=')+4+page_content2.find('|')]
        else:
            pron = page_content[page_content.find(
                '|pp=')+4:page_content.find('}}')]
    else:
        if debug_level > 1:
            print('  prononciation identique au singulier')
        pron = page_content[:page_content.find('}}')]
        if debug_level > 1:
            print('  pron avant while : ' + pron)
        if pron.find('|pron=') != -1:
            pron = '|' + pron[pron.find('|pron=')+len('|pron='):]

        pron_array = pron.split('|')
        # {{fr-rég|a.kʁɔ.sɑ̃.tʁik|mf=oui}}
        n = 0
        while n < len(pron_array) and (pron_array[n] == '' or pron_array[n].find('=') != -1):
            if debug_level > 1:
                print(pron_array[n].find('='))
            n += 1
        if n == len(pron_array):
            pron = '|'
        else:
            pron = '|' + pron_array[n]
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
        if debug_level > 1:
            print('  pron après while : ' + pron)
    pron = trim(pron)
    if pron.rfind('|') > 0:
        pronM = pron[:pron.rfind('|')]
        while pronM.rfind('|') > 0:
            pronM = pronM[:pronM.rfind('|')]
    else:
        pronM = pron
    if pronM[:1] != '|':
        pronM = '|' + pronM
    if debug_level > 0:
        try:
            print('  Prononciation : ' + pronM)
        except UnicodeDecodeError:
            print('  Prononciation à décoder')
        except UnicodeEncodeError:
            print('  Prononciation à encoder')

    return trim(pronM)


p = PageProvider(treat_page, site, debug_level)
set_functions_globals(debug_level, site, username)
set_fr_wiktionary_functions_globals(debug_level, site, username)


def main(*args) -> int:
    if len(sys.argv) > 1:
        if debug_level > 1:
            print(sys.argv)
        if sys.argv[1] == '-test':
            treat_page_by_name('User:' + username + '/test')
        elif sys.argv[1] == '-test2':
            treat_page_by_name('User:' + username + '/test2')
        elif sys.argv[1] == str('-tu') or sys.argv[1] == str('-t'):
            treat_page_by_name('User:' + username + '/test unitaire')
        elif sys.argv[1] == '-page' or sys.argv[1] == '-p':
            treat_page_by_name('saisie de schéma')
        elif sys.argv[1] == '-file' or sys.argv[1] == '-txt':
            p.pages_by_file('lists/articles_' + site_language +
                            '_' + site_family + '.txt')
        elif sys.argv[1] == '-dump' or sys.argv[1] == '-xml':
            regex = r''
            if len(sys.argv) > 2:
                regex = sys.argv[2]
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
            after_page = ''
            if len(sys.argv) > 2:
                after_page = sys.argv[2]
            p.pages_by_cat('Catégorie:Python', after_page=after_page)
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
            # large_media: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treat_page_by_name(update_html_to_unicode(sys.argv[1]))
    else:
        # Daily
        p.pages_by_cat('Catégorie:Pluriels manquants en français', False, '')
        # TODO: python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"
    return 0


if __name__ == "__main__":
    main(sys.argv)

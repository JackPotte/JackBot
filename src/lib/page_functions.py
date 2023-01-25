#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import codecs
import datetime
import re
import time
import pywikibot
from pywikibot import config, Page, User
# JackBot
from lib import *


def get_global_variables(args):
    global debug_level  # TODO remove when proper dependency injections
    debug_level = 0
    site_family = 'wiktionary'
    site_language = 'fr'
    page_name = None

    for arg in args:
        option, sep, value = arg.partition(':')
        if option in ['-debug', '-d']:
            debug_level = value
        elif option in ['-family', '-f']:
            site_family = value
        elif option in ['-language', '-lang', '-l']:
            site_language = value
        elif option in ['-tu', '-t']:
            page_name = '/test unitaire'

    site = pywikibot.Site(site_language, site_family)
    user_name = config.usernames[site_family][site_language]
    if page_name is not None:
        page_name = 'User:' + user_name + page_name
    debug_level = int(debug_level)
    if debug_level > 0:
        print('get_global_variables() =', site_language,
              site_family, user_name, page_name)

    return site, user_name, debug_level, page_name


def set_functions_globals(my_debug_level, my_site, my_username):
    global debug_level
    global site
    global username
    debug_level = my_debug_level
    site = my_site
    username = my_username


def global_operations(page_content):
    # Dmoz a fermé et bug https://fr.wikipedia.org/w/index.php?title=Flup,_N%C3%A9nesse,_Poussette_et_Cochonnet&diff=150799141&oldid=150798957
    # page_content = replaceDMOZ(page_content)
    # page_content = replaceISBN(page_content)
    # page_content = replaceRFC(page_content)

    # Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
    try:
        page_content = re.sub(
            r'{{ *(formatnum|Formatnum|FORMATNUM)\:([0-9]*) *([0-9]*)}}', r'{{\1:\2\3}}', page_content)
    except TypeError as e:
        print(str(e))
    return page_content


def trim(s):
    return s.strip(" \t\n\r\0\x0B")


def date_plus_month(months):
    year, month, day = datetime.date.today().timetuple()[:3]
    new_month = month + months
    if new_month == 0:
        new_month = 12
        year = year - 1
    elif new_month == -1:
        new_month = 11
        year = year - 1
    elif new_month == -2:
        new_month = 10
        year = year - 1
    elif new_month == -3:
        new_month = 9
        year = year - 1
    elif new_month == -4:
        new_month = 8
        year = year - 1
    elif new_month == -5:
        new_month = 7
        year = year - 1
    if new_month == 2 and day > 28:
        day = 28
    return datetime.date(year, new_month, day)


def time_after_last_edition(page):
    try:
        last_edit_time = page.getVersionHistory()[0][1]
    except TypeError as e:
        return 0
    except pywikibot.exceptions.NoPageError as e:
        return 0
    if debug_level > 1:
        print(last_edit_time)  # Zulu format, ex: 2017-07-29T21:57:34Z
    match_time = re.match(
        r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(last_edit_time))
    date_last_edit_time = datetime.datetime(int(match_time.group(1)), int(match_time.group(2)),
                                            int(match_time.group(3)), int(
                                                match_time.group(4)),
                                            int(match_time.group(5)), int(match_time.group(6)))
    datetime_now = datetime.datetime.utcnow()
    diff_last_edit_time = datetime_now - date_last_edit_time
    return diff_last_edit_time.seconds / 60 + diff_last_edit_time.days * 24 * 60


def has_more_than_time(page, time_after_last_edition=60):  # minutes
    if page.exists():
        date_now = datetime.datetime.utcnow()
        max_date = date_now - \
            datetime.timedelta(minutes=time_after_last_edition)
        has_more_than_time = str(
            page.latest_revision.timestamp) < max_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        if debug_level > 1:
            print(str(max_date.strftime('%Y-%m-%dT%H:%M:%SZ')),
                  str(page.latest_revision.timestamp), str(has_more_than_time))
        if has_more_than_time or username in page.title() or \
                list(page.contributors(total=1).keys())[0] in ['JackBot', 'JackPotte']:
            # TODO config.usernames[site_family][site_language] for human user
            return True
        if debug_level > 0:
            pywikibot.output(
                ' \03<<red>>the last edition is too recent to edit: \03<<default>>' + str(page.latest_revision.timestamp))
    return False


def is_trusted_version(site, page):
    first_editor = page.oldest_revision['user']
    last_editor = list(page.contributors(total=1).keys())[0]
    if first_editor == last_editor:
        if debug_level > 0:
            pywikibot.output(
                ' \03<<green>> the page belongs to its last edition user: \03<<default>>' + last_editor)
        return True
    user_page_name = ' user: ' + last_editor
    user_page = Page(site, user_page_name)
    user = User(user_page)
    if 'autoconfirmed' in user.groups():
        if debug_level > 0:
            pywikibot.output(
                ' \03<<green>> the last edition user can be trusted: \03<<default>>' + last_editor)
        return True
    if user.isAnonymous():
        if debug_level > 0:
            pywikibot.output(
                ' \03<<red>>the last edition user cannot be trusted: \03<<default>>' + last_editor)
        pywikibot.output(' \03<<red>>The page needs to be categorized manually\03<<default>>: ' +
                         'https://' + page.site.hostname() + '/wiki/' + page.title().replace(' ', '_'))
        return False
    if debug_level > 0:
        pywikibot.output(
            ' \03<<green>> the last edition user could be trusted: \03<<default>>' + last_editor)
    return True


def get_content_from_page_name(page_name, site, allowed_namespaces=None):
    page = Page(site, page_name)
    return get_content_from_page(page, allowed_namespaces)


def get_content_from_page(page, allowed_namespaces=None):
    global debug_level
    if debug_level > 0:
        print('\nget_content_from_page()')
    if debug_level > 1:
        pywikibot.output(
            ' \03<<blue>>get_content_from_page : \03<<default>>' + page.title())

    current_page_content = ''
    try:
        does_exist = page.exists()
    except pywikibot.exceptions.InvalidTitleError as e:
        if debug_level > 0:
            print(str(e))
        return current_page_content

    if not does_exist:
        if debug_level > 0:
            print(' No page in ' + __file__)
        return None

    if isinstance(allowed_namespaces, list):
        if debug_level > 1:
            print(' namespace : ' + str(page.namespace()))
        condition = page.namespace() in allowed_namespaces
    elif allowed_namespaces == 'All':
        if debug_level > 1:
            print(' all namespaces')
        condition = True
    else:
        if debug_level > 1:
            print(' content namespaces')
        condition = page.namespace() in [
            0, 12, 14, 100] or username in page.title()

    if not condition:
        if debug_level > 0:
            print(' Forbidden namespace')
        return None

    try:
        current_page_content = page.get()
    except pywikibot.exceptions.InvalidTitleError as e:
        if debug_level > 0:
            print(str(e))
        return None
    except pywikibot.exceptions.IsRedirectPageError as e:
        if debug_level > 0:
            print(str(e))
        if page.namespace() == 'Template:':
            return None
            # TODO takes the HTML page, ex: https://fr.wikipedia.org/w/index.php?title=Mod%C3%A8le:Donn%C3%A9es_de_la_pand%C3%A9mie_de_maladie_%C3%A0_coronavirus_de_2019-2020&diff=prev&oldid=184135983
            # current_page_content = page.get(get_redirect=True)
            # if current_page_content[:len('#REDIRECT')] == '#REDIRECT':
            #     regex = r'\[\[([^\]]+)\]\]'
            #     s = re.search(regex, current_page_content)
            #     if s:
            #         current_page_content = get_content_from_page_name(s.group(1), site,
            #                                                           allowed_namespaces=allowed_namespaces)
            #     else:
            #         return None
            # else:
            #     return None
        else:
            # This would erase redirection pages by their target pages
            # redir_target = page.getRedirectTarget()
            # if redir_target.exists():
            #     current_page_content = redir_target.get()
            # else:
            return None
    except pywikibot.exceptions.NoPageError as e:
        if debug_level > 0:
            print(str(e))
        return None
    except pywikibot.exceptions.ServerError as e:
        if debug_level > 0:
            print(str(e))
        return None
    except pywikibot.exceptions.SiteDefinitionError as e:
        if debug_level > 0:
            print(str(e))
        return None

    if debug_level > 0:
        print(' Page retrieved')

    return current_page_content


def get_wiki(language, family):
    wiki = None
    try:
        wiki = pywikibot.Site(language, family)
    except pywikibot.exceptions.ServerError:
        if debug_level > 1:
            print('  ServerError in getWiki')
    except pywikibot.exceptions.SiteDefinitionError:
        if debug_level > 1:
            print('  SiteDefinitionError in getWiki')
    except UnicodeEncodeError:
        if debug_level > 1:
            print('  UnicodeEncodeError in getWiki')
    # TODO: UserWarning: Site wiktionary:ro instantiated using different code "mo"
    return wiki


def get_first_template_by_name(page_content, template):
    regex = r'{{[' + template[:1].lower() + template[:1].upper() + \
        r']' + template[1:] + r'[^{}]+}}'
    if re.search(regex, page_content):
        return page_content[re.search(regex, page_content).start():re.search(regex, page_content).end()]
    return ''


def get_all_templates_by_name(page_content, template):
    regex = r'{{[' + template[:1].lower() + template[:1].upper() + \
        r']' + template[1:] + r'[^{}]+}}'
    return re.findall(regex, page_content)


def get_parameter(page_content, p):
    if debug_level > 0:
        print('\nget_parameter()')
    regex = r'\| *' + p + r' *='
    if '}}' not in page_content or not re.search(regex, page_content) \
            or re.search(regex, page_content).start() > page_content.find('}}'):
        if debug_level > 0:
            print(' no template end after parameter')
        if debug_level > 1:
            # TODO ignore nested templates
            print(re.search(regex, page_content).start())
            print(page_content.find('}}'))
        return ''

    parameter = page_content[re.search(regex, page_content).start() + 1:]
    parameter_end = parameter
    while parameter_end.find('[') != -1 and parameter_end.find('[') < parameter_end.find('|') \
            and parameter_end.find('[') < parameter_end.find('}') and parameter_end.find('|') < parameter_end.find('}'):
        # The parameter contains a link like "[[ | ]]"
        parameter_end = parameter_end[parameter_end.find(']') + 1:]

    return parameter[:len(parameter) - len(parameter_end) + re.search(r'[\|{}]', parameter_end).start()]


def get_parameter_value(page_content, p):
    parameter = get_parameter(page_content, p)
    return trim(parameter[parameter.find('=') + 1:])


def add_parameter(page_content, parameter, content=None):
    final_page_content = ''
    if parameter == 'titre' and content is None:
        # Détermination du titre d'un site web
        # URL = get_parameter('url')
        final_page_content = page_content
    else:
        # TODO
        print('TODO')
    return final_page_content


def replace_parameter_value(page_content, template, parameter_key, old_value, new_value):
    regex = r'({{ *(' + template[:1].lower() + r'|' + template[:1].upper() + r')' + \
            template[1:] + r' *\n* *\|[^}]*' + \
        parameter_key + r' *= *)' + old_value
    if debug_level > 0:
        print(regex)
    page_content = re.sub(regex, r'\1' + new_value, page_content)
    return page_content


def replace_template(page_content, old_template, new_template=''):
    if debug_level > 0:
        print('\nreplaceTemplate : ' + old_template)
    regex = r'({{[ \n]*)' + old_template + r'([ \n]*[{}\|][^{}]*}}?)'
    if re.search(regex, page_content):
        if debug_level > 0:
            print(' trouvé')
        result = r''
        if new_template != '':
            result = r'\1' + new_template + r'\2'
        page_content = re.sub(regex, result, page_content)
    return page_content


def replace_deprecated_tags(page_content):
    if debug_level > 0:
        print('Remplacements des balises HTML')

    deprecated_tags = {}
    deprecated_tags['big'] = 'strong'
    deprecated_tags['center'] = 'div style="text-align: center;"'
    deprecated_tags['font *color *= *"?'] = 'span style="color:'
    deprecated_tags['font *face *= *"?'] = 'span style="font-family:'
    deprecated_tags['font *\-?size *= *"?\+?\-?'] = 'span style="font-size:'
    deprecated_tags['font *style *= *"?\+?\-?'] = 'span style="'
    # deprecated_tags['font '] = 'span ' # TODO: ajouter des ";" entre plusieurs param
    deprecated_tags['strike'] = 's'
    deprecated_tags['tt'] = 'code'
    deprecated_tags['BIG'] = 'strong'
    deprecated_tags['CENTER'] = 'div style="text-align: center;"'
    deprecated_tags['FONT COLOR *= *"?'] = 'span style="color:'
    deprecated_tags['FONT SIZE *= *"?\+?'] = 'span style="font-size:'
    deprecated_tags['STRIKE'] = 's'
    deprecated_tags['TT'] = 'code'
    font_size = {}
    font_size[1] = 0.63
    font_size[2] = 0.82
    font_size[3] = 1.0
    font_size[4] = 1.13
    font_size[5] = 1.5
    font_size[6] = 2.0
    font_size[7] = 3.0
    font_color = []
    font_color.append('black')
    font_color.append('blue')
    font_color.append('green')
    font_color.append('orange')
    font_color.append('red')
    font_color.append('white')
    font_color.append('yellow')
    font_color.append('#808080')

    page_content = page_content.replace('</br>', '<br/>')
    page_content = page_content.replace(
        '<source lang="html4strict">', '<source lang="html">')

    # TODO: {{citation}} https://fr.wikiversity.org/w/index.php?title=Matrice%2FD%C3%A9terminant&action=historysubmit&type=revision&diff=669911&oldid=664849
    # TODO: multiparamètre
    page_content = page_content.replace(
        '<font size="+1" color="red">', r'<span style="font-size:0.63em; color:red;>')
    regex = r'<font color="?([^>"]*)"?>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(page_content):
        if debug_level > 1:
            print('Remplacement de ' + match.group(0) +
                  ' par <span style="color:' + match.group(1) + '">')
        page_content = page_content.replace(match.group(
            0), '<span style="color:' + match.group(1) + '">')
        page_content = page_content.replace('</font>', '</span>')

    for old_tag, new_tag in deprecated_tags.items():
        if debug_level > 1:
            print("Clé : %s, valeur : %s." % (old_tag, new_tag))
        if old_tag.find(' ') == -1:
            closing_old_tag = old_tag
        else:
            closing_old_tag = old_tag[:old_tag.find(' ')]
        if new_tag.find(' ') == -1:
            closing_new_tag = new_tag
        else:
            closing_new_tag = new_tag[:new_tag.find(' ')]
        # regex = r'<' + old_tag + r'([^>]*)>([^\n]*)</' + closing_old_tag + '>'
        # TODO bug
        # https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:-flex-nom-fam-/Documentation&diff=prev&oldid=24027702
        regex = r'< *' + old_tag + r'([^>]*) *>'
        if re.search(regex, page_content):
            # summary = summary + ', ajout de ' + new_tag
            # page_content = re.sub(regex, r'<' + new_tag + r'\1>', page_content)
            pattern = re.compile(regex, re.UNICODE)
            for match in pattern.finditer(page_content):
                if debug_level > 1:
                    print(str(match.group(1)))
                if new_tag.find('font-size') != -1:
                    size = match.group(1).replace('"', '')
                    try:
                        size = int(size)
                        if size > 7:
                            size = 7
                        opening_tag = new_tag + str(font_size[size]) + r'em"'
                    except ValueError:
                        opening_tag = new_tag + size + '"'
                else:
                    opening_tag = new_tag + match.group(1)
                page_content = page_content.replace(
                    match.group(0), r'<' + opening_tag + r'>')

        regex = r'</ *' + closing_old_tag + ' *>'
        page_content = re.sub(
            regex, r'</' + closing_new_tag + '>', page_content)
    page_content = page_content.replace('<strong">', r'<strong>')
    page_content = page_content.replace('<s">', r'<s>')
    page_content = page_content.replace('<code">', r'<code>')
    page_content = page_content.replace(';"">', r';">')

    # Fix
    regex = r'<span style="font\-size:([a-z]+)>'
    pattern = re.compile(regex, re.UNICODE)
    for match in pattern.finditer(page_content):
        # summary = summary + ', correction de color'
        page_content = page_content.replace(match.group(
            0), '<span style="color:' + match.group(1) + '">')
    page_content = page_content.replace('</font>', '</span>')
    page_content = page_content.replace('</font>'.upper(), '</span>')

    regex = r'<span style="font\-size:(#[0-9]+)"?>'
    s = re.search(regex, page_content)
    if s:
        # summary = summary + ', correction de color'
        page_content = re.sub(regex, r'<span style="color:' +
                              s.group(1) + r'">', page_content)

    regex = r'<span style="text\-size:([0-9]+)"?>'
    s = re.search(regex, page_content)
    if s:
        # summary = summary + ', correction de font-size'
        page_content = re.sub(regex, r'<span style="font-size:' + str(font_size[int(s.group(1))]) + r'em">',
                              page_content)

    # Fix :
    regex = r'(<span style="font\-size:[0-9]+px;">)[0-9]+px</span>([^<]*)</strong></strong>'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1 \2</span>', page_content)

    page_content = page_content.replace('<strong><strong><strong><strong><strong><strong>',
                                        '<span style="font-size:75px;">')
    page_content = page_content.replace(
        '<strong><strong><strong><strong><strong>', '<span style="font-size:50px;">')
    page_content = page_content.replace(
        '<strong><strong><strong><strong>', '<span style="font-size:40px;">')
    page_content = page_content.replace(
        '<strong><strong><strong>', '<span style="font-size:25px;">')
    page_content = page_content.replace(
        '<strong><strong>', '<span style="font-size:20px;">')
    page_content = re.sub(
        r'</strong></strong></strong></strong></strong></strong>', r'</span>', page_content)
    page_content = re.sub(
        r'</strong></strong></strong></strong></strong>', r'</span>', page_content)
    page_content = re.sub(
        r'</strong></strong></strong></strong>', r'</span>', page_content)
    page_content = re.sub(r'</strong></strong></strong>',
                          r'</span>', page_content)
    page_content = re.sub(r'</strong></strong>', r'</span>', page_content)
    regex = r'<strong>([^<]*)</span>'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'<strong>\1</strong>', page_content)
    regex = r'<strong><span ([^<]*)</span></span>'
    if re.search(regex, page_content):
        page_content = re.sub(
            regex, r'<strong><span \1</span></strong>', page_content)
    # page_content = re.sub(r'</span></span>', r'</span>', page_content)
    return page_content


def replace_files_errors(page_content):
    # https://fr.wiktionary.org/wiki/Sp%C3%A9cial:LintErrors/bogus-image-options
    bad_file_parameters = []
    bad_file_parameters.append('')
    # bad_file_parameters.append('cadre')
    for badFileParameter in bad_file_parameters:
        regex = r'(\[\[(Image|Fichier|File) *: *[^\]{]+)\| *' + \
            badFileParameter + r' *(\||\])'
        try:
            page_content = re.sub(regex, r'\1\3', page_content)
        except TypeError:
            print('TypeError')

    # Remove doubles
    regex = r'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *(?:thumb|vignette) *(\| *(?:thumb|vignette) *[\|\]])'
    try:
        page_content = re.sub(regex, r'\1\3', page_content)
    except TypeError:
        print('TypeError')

    return page_content


def replaceDMOZ(page_content):
    # http://www.dmoz.org => http://dmoztools.net
    URLend = ' \\n\[\]}{<>\|\^`\\"\''
    if page_content.find('dmoz.org/search?') == -1 and page_content.find('dmoz.org/license.html') == -1:
        if debug_level > 1:
            print(URLend)
        regex = r'\[http://(www\.)?dmoz\.org/([^' + URLend + r']*)([^\]]*)\]'
        page_content = re.sub(regex, r'[[dmoz:\2|\3]]', page_content)
        regex = r'http://(www\.)?dmoz\.org/([^' + URLend + r']*)'
        page_content = re.sub(regex, r'[[dmoz:\2]]', page_content)
    return page_content


def replaceISBN(page_content):
    # TODO: out of <source> <nowiki> <pre>
    page_content = page_content.replace('ISBN&#160;', 'ISBN ')
    regex = r'\(*ISBN +([0-9Xx\- ]+)\)*( [^0-9Xx\- ])'
    if debug_level > 1:
        print(regex)
    if re.search(regex, page_content):
        if debug_level > 0:
            'ISBN'
        page_content = re.sub(regex, r'{{ISBN|\1}}\2', page_content)
    regex = r'\(*ISBN +([0-9Xx\- ]+)\)*'
    if debug_level > 1:
        print(regex)
    if re.search(regex, page_content):
        if debug_level > 0:
            'ISBN'
        page_content = re.sub(regex, r'{{ISBN|\1}}', page_content)

    # TODO: remove fix
    regex = r'{{ISBN *\|([0-9X\- ]+)}}([Xx]?)'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'{{ISBN|\1\2}}', page_content)
    regex = r'{{ISBN *\| *(1[03]) *}}'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'ISBN \1', page_content)

    regex = r'({{ISBN *\|.*)\-\-}}>'
    if re.search(regex, page_content):
        page_content = re.sub(regex, r'\1}}-->', page_content)

    if debug_level > 1:
        input(page_content)
    return page_content


def replaceRFC(page_content):
    # TODO?
    return page_content


def search_doubles(page_content, parameter):
    if debug_level > 0:
        ' Recherche de doublons dans le modèle : ' + parameter[1]
    final_page_content = ''
    regex = r'{{' + parameter[1] + r'[^\n]*{{' + parameter[1]
    while re.search(regex, page_content):
        # TODO: final_page_content = page_content[:], page_content = page_content[:]
        print(page_content[re.search(regex, page_content).start():re.search(regex, page_content).end()].encode(
            config.console_encoding, 'replace'))
    return final_page_content + page_content


def log(source):
    txtfile = codecs.open('JackBot.log', 'a', 'utf-8')
    txtfile.write('\n' + source + '\n')
    txtfile.close()


def stop_required(username, site):
    page_content = get_content_from_page_name('User talk:' + username, site)
    if page_content is None:
        return
    if page_content != u"{{/Stop}}":
        pywikibot.output(
            "\n*** \03<<yellow>>Arrêt d'urgence demandé\03<<default>> ***")
        exit(0)


def save_page(current_page, page_content, summary, is_minor=True):
    result = "ok"
    if debug_level > 0:
        pywikibot.output("\n\03<<blue>>" + summary + u"\03<<default>>")
        pywikibot.output(
            "\n\03<<red>>---------------------------------------------------\03<<default>>")
        if len(page_content) < 6000:
            try:
                print(page_content)
            except UnicodeEncodeError:
                print(page_content.encode(config.console_encoding, 'replace'))
        else:
            page_size = 3000
            try:
                print(page_content[:page_size])
                print('\n[...]\n')
                print(page_content[len(page_content) - page_size:])
            except UnicodeEncodeError as e:
                print(str(e))
                print(page_content[:page_size].encode(
                    config.console_encoding, 'replace'))
                print('\n[...]\n')
                print(page_content[len(
                    page_content) - page_size:].encode(config.console_encoding, 'replace'))
        result = input(
            '\nSauvegarder [[' + current_page.title() + ']] ? (o/n) ')
    if str(result) not in ['n', 'no', 'non']:
        if current_page.title().find(username + '/') == -1:
            stop_required(username, site)
        if not summary:
            summary = '[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            current_page.put(page_content, summary=summary, minor=is_minor)
        except pywikibot.exceptions.NoPageError as e:
            print(str(e))
            return
        except pywikibot.exceptions.IsRedirectPageError as e:
            print(str(e))
            return
        except pywikibot.exceptions.LockedPageError as e:
            print(str(e))
            return
        # except pywikibot.EditConflict as e:
        #     print(str(e))
        #     return
        except pywikibot.exceptions.ServerError as e:
            print(str(e))
            time.sleep(100)
            save_page(current_page, page_content, summary)
            return
        except pywikibot.exceptions.InvalidTitleError as e:
            print(str(e))
            return
        except pywikibot.exceptions.OtherPageSaveError as e:
            print(str(e))
            # Ex : [[SIMP J013656.5+093347]]
            return
        except AttributeError as e:
            print(str(e))
            return


def is_patrolled(version):
    # TODO: extensions Patrolled Edits & Flagged Revisions
    if debug_level > 1:
        # eg: [{'timestamp': '2017-07-25T02:26:15Z', 'user': '27.34.18.159'}]
        print(version)
    if debug_level > 0:
        print(' user: ') + version[0]['user']
    return False
    # admins = site.allusers(group='sysop')  #<pywikibot.data.api.ListGenerator object at 0x7f6ebc521fd0>
    # patrollers = site.allusers(group='patrollers')


def get_line_number():
    # TODO magic word
    from inspect import currentframe, getframeinfo
    frame_info = getframeinfo(currentframe())
    return str(frame_info.lineno)


def cancel_edition(page, cancel_user, summary=''):
    old_page_content = ''
    user_name = cancel_user['user']
    if debug_level > 1:
        print(page.userName() + ' trouvé')

    if cancel_user['action'].lower() in ['revocation', 'révocation']:
        summary = 'Révocation de ' + user_name
        if page.getCreator() == user_name:
            page.delete(reason=summary, prompt=False)
            return ''
        else:
            i = 0
            while page.getVersionHistory()[i][2] == user_name:
                i = i + 1
                if debug_level > 1:
                    print(i)
            if i > 0:
                old_page_content = get_old_page_content(
                    page, page.getVersionHistory()[i][0])
        if debug_level > 2:
            input(old_page_content)
    elif page.userName() == user_name:
        summary = 'Annulation de ' + user_name
        old_page_content = get_old_page_content(page, page.previousRevision())
    return old_page_content, summary


def get_old_page_content(page, revision):
    try:
        return page.getOldVersion(revision, get_redirect=True)
    except pywikibot.exceptions.InvalidTitleError:
        if debug_level > 0:
            print(' IsRedirect l 548')
    except pywikibot.exceptions.NoPageError:
        if debug_level > 0:
            print(' NoPage l 551')
    except pywikibot.exceptions.ServerError:
        if debug_level > 0:
            print(' ServerError l 554')
    return ''


def get_site_by_file_name(file_name):
    # Ex : ~/JackBot/src/wiktionary/fr_wiktionary_format.py
    if file_name.rfind('/') != -1:
        file_name = file_name[file_name.rfind('/') + 1:].replace('_', '.')
    elif file_name.rfind('\\') != -1:
        file_name = file_name[file_name.rfind('\\') + 1:].replace('_', '.')
    site_language = file_name[:2]
    site_family = file_name[3:]
    site_family = site_family[:site_family.find('.')]
    if debug_level > 1:
        print(file_name, site_language, site_family)
    site = pywikibot.Site(site_language, site_family)
    return site_language, site_family, site


def get_sections_titles(page_content, regex=r'\n=[^\n]+\n'):
    if debug_level > 1:
        print('\nget_sections_titles()')
    s = re.findall(regex, page_content, re.DOTALL)
    if s:
        if debug_level > 1:
            print(' ' + regex + ' found')
        return s
    if debug_level > 1:
        print(' ' + regex + ' not found')
    return []


def get_section_by_name(page_content, section_name):
    if debug_level > 0:
        print('\nget_section_by_name(' + section_name + ')')
    section_title = r'=* *{{S\|' + section_name + r'(\||})'
    return get_section_by_title(page_content, section_title)


def get_section_by_title(page_content, section_title_regex, section_level=2):
    global debug_level
    if debug_level > 0:
        print('\nget_section_by_title()')
    start_position = 0
    end_position = len(page_content)
    s = re.search(section_title_regex, page_content)
    if not s:
        if debug_level > 1:
            print(' Missing section: ' + section_title_regex)
        return None, start_position, end_position
    start_position = s.start()

    page_content = page_content[s.start():]
    if page_content.find('\n') == -1:
        if debug_level > 0:
            print(' Without next section. start: ' +
                  str(start_position) + ', end: ' + str(end_position))
        return page_content, start_position, end_position

    next_section_regex = r'\n='
    for level in range(section_level - 1):
        next_section_regex += r'=?'
    next_section_regex += r'[^=]'

    # TODO jump nested tag and template content
    delta = page_content.find('\n') + 1
    # Commence normalement par [1:section_title_regex]
    page_content2 = page_content[delta:]
    s = re.search(next_section_regex, page_content2, re.DOTALL)
    if not s:
        if debug_level > 0:
            print(' Without next section2. start: ' +
                  str(start_position) + ', end: ' + str(end_position))
        return page_content, start_position, end_position

    end_position = delta + s.start()
    page_content = page_content[:end_position]
    if debug_level > 0:
        print(' With next section. start: ' +
              str(start_position) + ', end: ' + str(end_position))

    return page_content, start_position, end_position


def is_template_name(string, template_name):
    regex = r'^(' + template_name[:1].upper() + r'|' + \
        template_name[:1].lower() + r')' + template_name[1:]
    return re.search(regex, string)


def has_parameter(string, param):
    regex = r'\| *' + param + r' *='
    return re.search(regex, string)


def remove_parameter_if_empty(template, parameter_name):
    regex = r'(\| *)' + parameter_name + r'( *=\n*)([\|}])'
    return re.sub(regex, r'\3', template)

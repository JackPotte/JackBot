#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, unicode_literals
from html2unicode import *

debug_level = 0
'''TODO: uca-default gère af, am, ar, as, ast, az, be, be-tarask, bg, bn, bn@collation=traditional, bo, br, bs, 
    bs-Cyrl, ca, chr, co, cs, cy, da, de, de-AT@collation=phonebook, dsb, ee, el, en, eo, es, et, eu, fa, fi, 
    fil, fo, fr, fr-CA, fur, fy, ga, gd, gl, gu, ha, haw, he, hi, hr, hsb, hu, hy, id, ig, is, it, ka, kk, kl, 
    km, kn, kok, ku, ky, la, lb, lkt, ln, lo, lt, lv, mk, ml, mn, mo, mr, ms, mt, nb, ne, nl, nn, no, oc, om, 
    or, pa, pl, pt, rm, ro, ru, rup, sco, se, si, sk, sl, smn, sq, sr, sr-Latn, sv, sv@collation=standard, sw, 
    ta, te, th, tk, tl, to, tr, tt, uk, uz, vi, vo, yi, yo, zu
'''


def sort_by_encoding(page_name, encoding='uca-default'):
    if debug_level > 0:
        print('\nsort_by_encoding()')

    page_name = update_html_to_unicode(page_name)
    word_key = ''
    add_key = False

    for letter in page_name:
        letter_to_treat = False
        if letter in ('’', '\''):  # 'ʼ' : pb en breton
            add_key = True
        elif letter in ('\\', '/', '×', '·', '…', '-', '\'', '.', ', ', '(', ')'):
            word_key += ' '
            add_key = True
        elif encoding != 'uca-default':
            # Latin
            if letter in [
                'à',
                'Á',
                'á',
                'â',
                'ä',
                'ā',
                'ă',
                'ą',
                'ǎ',
                'ǻ',
                'ȁ',
                'ȃ',
                'ȧ',
                'ɑ',
                'ạ',
                'ả',
                'ấ',
                'Ấ',
                'ⱥ',
                'À',
                'Â',
                'Ä',
                'Å',
                'Ā',
                'Ă',
                'Ą',
                'Ǎ',
                'Ǻ',
                'Ȁ',
                'Ȃ',
                'Ȧ',
                'Ⱥ',
                'Ɑ',
                'Ǟ',
                'Ǡ',
                'ắ',
                'Ắ',
                'å',
                'ã',
                'Ã',
            ]:
                word_key += "a"
                add_key = True
            elif letter in ['æ', 'ǣ', 'ǽ', 'Æ', 'Ǣ', 'Ǽ']:
                word_key += "ae"
                add_key = True
            elif letter in ['ƀ', 'ƃ', 'Ɓ', 'Ƃ', 'Ƀ']:
                word_key += "b"
                add_key = True
            elif letter in [
                'ç',
                'ć',
                'ċ',
                'č',
                'ƈ',
                'ȼ',
                'Ç',
                'Ć',
                'Ĉ',
                'Ċ',
                'Č',
                'Ƈ',
                'Ȼ',
            ]:
                word_key += "c"
                add_key = True
            elif letter == 'ĉ':
                word_key += "cx"
                add_key = True
            elif letter in [
                'ď',
                'đ',
                'ƌ',
                'ȡ',
                'Ď',
                'Đ',
                'Ɖ',
                'Ɗ',
                'Ƌ',
                'ȸ',
                'ǆ',
                'ǳ',
                'Ǆ',
                'ǅ',
                'Ǳ',
                'ǲ',
            ]:
                word_key += "d"
                add_key = True
            elif letter in [
                'è',
                'È',
                'é',
                'É',
                'ê',
                'Ê',
                'ë',
                'Ë',
                'ē',
                'ĕ',
                'ė',
                'ę',
                'ě',
                'ǝ',
                'ɛ',
                'ȅ',
                'ȇ',
                'ȩ',
                'ɇ',
                'ế',
                'Ế',
                'Ē',
                'Ĕ',
                'Ė',
                'Ę',
                'Ě',
                'Ǝ',
                'Ɛ',
                'Ȅ',
                'Ȇ',
                'Ȩ',
                'Ɇ',
                'ệ',
                'Ệ',
            ]:
                word_key += "e"
                add_key = True
            elif letter in ['ƒ', 'Ƒ']:
                word_key += "f"
                add_key = True
            elif letter == 'ĝ':
                word_key += "gx"
                add_key = True
            elif letter in [
                'ğ',
                'ġ',
                'ģ',
                'ǥ',
                'ǧ',
                'ǵ',
                'Ĝ',
                'Ğ',
                'Ġ',
                'Ģ',
                'Ɠ',
                'Ǥ',
                'Ǧ',
                'Ǵ',
            ]:
                word_key += "g"
                add_key = True
            elif letter == 'ĥ':
                word_key += "hx"
                add_key = True
            elif letter in ['ħ', 'ȟ', 'Ĥ', 'Ħ', 'Ȟ']:
                word_key += "h"
                add_key = True
            elif letter in [
                'ı',
                'î',
                'ĩ',
                'ī',
                'ĭ',
                'į',
                'ǐ',
                'ȉ',
                'ȋ',
                'Î',
                'Ĩ',
                'Ī',
                'Ĭ',
                'Į',
                'İ',
                'Ɨ',
                'Ǐ',
                'Ȉ',
                'Ȋ',
                'ĳ',
                'Ĳ',
                'ì',
                'Ì',
                'ï',
                'Ï',
                'ǈ',
                'ị',
                'Ị',
                'í',
                'Í',
            ]:
                word_key += "i"
                add_key = True
            elif letter == 'ĵ':
                word_key += "jx"
                add_key = True
            elif letter in ['ǰ', 'ȷ', 'ɉ', 'Ĵ', 'Ɉ']:
                word_key += "j"
                add_key = True
            elif letter in ['ķ', 'ƙ', 'ǩ', 'Ķ', 'Ƙ', 'Ǩ']:
                word_key += "k"
                add_key = True
            elif letter in [
                'ĺ',
                'ļ',
                'ľ',
                'ŀ',
                'ł',
                'ƚ',
                'ȴ',
                'ɫ',
                'Ɫ',
                'Ĺ',
                'Ļ',
                'Ľ',
                'Ŀ',
                'Ł',
                'Ƚ',
                'ǉ',
                'Ǉ',
            ]:
                word_key += "l"
                add_key = True
            elif letter == 'Ɯ':
                word_key += "m"
                add_key = True
            elif letter in [
                'ń',
                'ņ',
                'ň',
                'ŋ',
                'ǹ',
                'ƞ',
                'ȵ',
                'Ń',
                'Ņ',
                'Ň',
                'Ŋ',
                'Ɲ',
                'Ǹ',
                'Ƞ',
                'ǌ',
                'Ǌ',
                'ǋ',
                'ɲ',
                'ṉ',
                'Ṉ',
                'ñ',
                'Ñ',
            ]:
                word_key += "n"
                add_key = True
            elif letter in [
                'ô',
                'Ô',
                'ø',
                'ō',
                'ŏ',
                'ő',
                'ơ',
                'ǒ',
                'ǫ',
                'ǭ',
                'ǿ',
                'ȍ',
                'ȏ',
                'ȫ',
                'ȭ',
                'ȯ',
                'ȱ',
                'Ø',
                'Ō',
                'Ŏ',
                'Ő',
                'Ɔ',
                'Ɵ',
                'ɵ',
                'Ơ',
                'Ǒ',
                'Ǫ',
                'Ǭ',
                'Ǿ',
                'Ȍ',
                'Ȏ',
                'Ȫ',
                'Ȭ',
                'Ȯ',
                'Ȱ',
                'ɔ',
                'ở',
                'Ở',
                'ợ',
                'Ợ',
                'ò',
                'ó',
                'ö',
                'Ö',
                'õ',
                'Õ',
            ]:
                word_key += "o"
                add_key = True
            elif letter in ['œ', 'Œ']:
                word_key += "oe"
                add_key = True
            elif letter in ['ƥ', 'Ƥ']:
                word_key += "p"
                add_key = True
            elif letter in ['ɋ', 'Ɋ', 'ȹ']:
                word_key += "q"
                add_key = True
            elif letter in [
                'ŕ',
                'ŗ',
                'ř',
                'ȑ',
                'ȓ',
                'ɍ',
                'Ŕ',
                'Ŗ',
                'Ř',
                'Ȑ',
                'Ȓ',
                'Ɍ',
            ]:
                word_key += "r"
                add_key = True
            elif letter == 'ŝ':
                word_key += "sx"
                add_key = True
            elif letter in [
                'ſ',
                'ś',
                'ş',
                'š',
                'ƪ',
                'ș',
                'ȿ',
                'Ś',
                'Ŝ',
                'Ş',
                'Š',
                'Ʃ',
                'Ș',
            ]:
                word_key += "s"
                add_key = True
            elif letter in ['ß', 'ß']:
                word_key += "ss"
                add_key = True
            elif letter in [
                'ţ',
                'ť',
                'ŧ',
                'ƫ',
                'ƭ',
                'ț',
                'ȶ',
                'Ţ',
                'Ť',
                'Ŧ',
                'Ƭ',
                'Ʈ',
                'Ț',
                'Ⱦ',
                'ⱦ',
            ]:
                word_key += "t"
                add_key = True
            elif letter == 'ŭ':
                word_key += "ux"
                add_key = True
            elif letter in [
                'û',
                'ũ',
                'ū',
                'ů',
                'ű',
                'ų',
                'ư',
                'ǔ',
                'ǖ',
                'ǘ',
                'ǚ',
                'ǜ',
                'ǟ',
                'ǡ',
                'ȕ',
                'ȗ',
                'ʉ',
                'Û',
                'Ũ',
                'Ū',
                'Ŭ',
                'Ů',
                'Ű',
                'Ų',
                'Ư',
                'Ǔ',
                'Ǖ',
                'Ǘ',
                'Ǚ',
                'Ǜ',
                'Ȕ',
                'Ȗ',
                'Ʉ',
                'ủ',
                'Ủ',
                'ú',
                'Ú',
                'ù',
                'Ù',
                'ü',
                'Ü',
            ]:
                word_key += "u"
                add_key = True
            elif letter in ['ʋ', 'Ʋ', 'Ʌ', 'ʌ']:
                word_key += "v"
                add_key = True
            elif letter in ['ŵ', 'Ŵ']:
                word_key += "w"
                add_key = True
            elif letter in ['ŷ', 'ƴ', 'ȳ', 'ɏ', 'Ŷ', 'Ÿ', 'Ƴ', 'Ȳ', 'Ɏ']:
                word_key += "y"
                add_key = True
            elif letter in [
                'ź',
                'ż',
                'ž',
                'ƶ',
                'ƹ',
                'ƺ',
                'ǯ',
                'ȥ',
                'ɀ',
                'Ź',
                'Ż',
                'Ž',
                'Ƶ',
                'Ʒ',
                'Ƹ',
                'Ǯ',
                'Ȥ',
            ]:
                word_key += "z"
                add_key = True

            elif letter in [
                'A',
                'B',
                'C',
                'D',
                'E',
                'F',
                'G',
                'H',
                'I',
                'J',
                'K',
                'L',
                'M',
                'N',
                'O',
                'P',
                'Q',
                'R',
                'S',
                'T',
                'U',
                'V',
                'W',
                'X',
                'Y',
                'Z',
            ]:
                word_key += letter.lower()
            else:
                letter_to_treat = True
        else:
            letter_to_treat = True

        if letter_to_treat:
            word_key += letter

    if add_key:
        return trim(word_key.replace('  ', ' '))

    if debug_level > 0:
        input(page_name)
    return page_name


def add_default_sort(page_name, page_content, empty=False):
    page_content = page_content.replace('{{DEFAULTSORT:', '{{clé de tri|')
    page_content = page_content.replace('{{defaultsort:', '{{clé de tri|')
    page_content = page_content.replace('{{clef de tri|', '{{clé de tri|')
    while page_content.find('\n{clé de tri') != -1:
        page_content = page_content[:page_content.find(
            '\n{clé de tri')+1] + '{' + page_content[page_content.find('\n{clé de tri'):]

    default_sort_key = '' if empty else sort_by_encoding(page_name)
    if page_content.find('{{clé de tri') == -1 and default_sort_key != '' \
            and default_sort_key.lower() != page_name.lower():
        # summary = summary + ', {{clé de tri}} ajoutée'
        if page_content.rfind('\n\n[[') != -1:
            page_content2 = page_content[page_content.rfind('\n\n[['):]
            if page_content2[4:5] == ':' or page_content2[5:6] == ':':
                page_content = page_content[:page_content.rfind('\n\n[[')] + '\n\n{{clé de tri|' \
                    + default_sort_key + '}}' + \
                    page_content[page_content.rfind('\n\n[['):]
            else:
                page_content = page_content + \
                    '\n\n{{clé de tri|' + default_sort_key + '}}\n'
        else:
            page_content = page_content + \
                '\n\n{{clé de tri|' + default_sort_key + '}}\n'

    elif page_content.find('{{clé de tri|') != -1 and (page_content.find('{{langue|fr}}') != -1
                                                       or page_content.find('{{langue|eo}}') != -1
                                                       or page_content.find('{{langue|en}}') != -1
                                                       or page_content.find('{{langue|es}}') != -1
                                                       or page_content.find('{{langue|de}}') != -1
                                                       or page_content.find('{{langue|pt}}') != -1
                                                       or page_content.find('{{langue|it}}') != -1):
        if debug_level > 0:
            print(' vérification de clé existante pour alphabets connus')
        page_content2 = page_content[page_content.find(
            '{{clé de tri|')+len('{{clé de tri|'):]
        default_sort_key = page_content2[:page_content2.find('}}')]
        '''if CleTri.lower() != default_sort_key.lower():
            summary = summary + ', {{clé de tri}} corrigée'
            page_content = page_content[:page_content.find('{{clé de tri|')+len('{{clé de tri|')] + CleTri + page_content[page_content.find('{{clé de tri|')+len('{{clé de tri|')+page_content2.find('}}'):]'''
        '''pb ʻokina
            if CleTri.lower() == page_name.lower():
            summary = summary + ', {{clé de tri}} supprimée'
            page_content = page_content[:page_content.find('{{clé de tri|')] + page_content[page_content.find('{{clé de tri|')+len('{{clé de tri|')+page_content2.find('}}')+2:]'''
    if debug_level > 1:
        input(page_content)

    baratin = '{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
    if page_content.find(baratin) != -1:
        page_content = page_content[:page_content.find(
            baratin)] + page_content[page_content.find(baratin)+len(baratin):]
        # summary = summary + ', {{clé de tri|}} supprimée'
    baratin = '{{clé de tri|}}<!-- Veuillez mettre juste après « {{clé de tri| » le titre de la page en y enlevant tous les accents et éventuels apostrophes, et en changeant les éventuels traits d’union et autres caractères spéciaux par une espace ; s’il n’y a rien à changer, merci d’effacer ces lignes. -->'
    '''Inhibé depuis migration Lua :
    if page_content.find(baratin) != -1:
        page_content = page_content[:page_content.find(baratin)] + page_content[page_content.find(baratin)+len(baratin):]
        summary = summary + ', {{clé de tri|}} supprimée'
    if page_content.find('{{clé de tri|}}') != -1:
        page_content = page_content[:page_content.find('{{clé de tri|}}')] + page_content[page_content.find('{{clé de tri|}}')+len('{{clé de tri|}}'):]
        summary = summary + ', {{clé de tri|}} supprimée'
    if page_content.find('{{clé de tri}}') != -1:
        page_content = page_content[:page_content.find('{{clé de tri}}')] + page_content[page_content.find('{{clé de tri}}')+len('{{clé de tri}}'):]
        summary = summary + ', {{clé de tri}} supprimée'
    if page_content.find('{{clé de tri|' + page_name.lower() + '}}') != -1 and page_content.find('{{S|verb pronominal|fr}}') == -1:
        page_content = page_content[:page_content.find('{{clé de tri|' + page_name.lower() + '}}')] + page_content[page_content.find('{{clé de tri|' + page_name.lower() + '}}')+len('{{clé de tri|' + page_name.lower() + '}}'):]
        summary = summary + ', {{clé de tri}} supprimée'''

    while page_content.find('{{S|verbe pronominal|') != -1:
        # Remplacement de modèle suite à vote
        page_content2 = page_content[page_content.find(
            '{{S|verbe pronominal|'):]
        if page_content2.find('{{conj') != -1 and page_content2.find('{{pronominal|') == -1 \
                and page_content2.find('{{pronl|') == -1 and page_content2.find('{{prnl|') == -1 \
                and page_content2.find('{{réflexif|') == -1 and page_content2.find('{{réfléchi|') == -1 \
                and page_content2.find('{{réfl|') == -1:
            page_content3 = page_content2[page_content2.find('{{conj'):]
            if page_content3.find('|prnl=') == -1 or page_content3.find('|prnl=') > page_content3.find('}}'):
                page_content = page_content[:page_content.find('{{S|verbe pronominal|')] \
                    + page_content2[:page_content2.find('{{conj')] \
                    + page_content3[:page_content3.find('}}')] \
                    + '|prnl=1' + \
                    page_content3[page_content3.find('}}'):]
        page_content = page_content[:page_content.find('{{S|verbe pronominal|')] + '{{S|verbe|' \
            + page_content[page_content.find('{{S|verbe pronominal|') + len('{{S|verbe pronominal|'):]
    while page_content.find("''(pronominal)''") != -1:
        page_content2 = page_content[page_content.find("''(pronominal)''"):]
        if page_content2.find('|prnl=1') != -1 and page_content2.find('|prnl=1') < page_content2.find('\n'):
            page_content = page_content[:page_content.find("''(pronominal)''")] \
                + page_content[page_content.find("''(pronominal)''") + len("''(pronominal)''"):]
        else:
            page_content = page_content[:page_content.find("''(pronominal)''")] + '{{prnl}}' \
                + page_content[page_content.find("''(pronominal)''") + len("''(pronominal)''"):]

    return page_content


def default_sort_by_language(page_name, language_code):
    if language_code == 'br':
        page_name = page_name.replace('ch', 'c⿕')
        page_name = page_name.replace('ch'.upper(), 'c⿕')
        page_name = page_name.replace('cʼh', 'c⿕⿕')
        page_name = page_name.replace('cʼh'.upper(), 'c⿕⿕')

    elif language_code == 'es':
        page_name = page_name.replace('ñ', 'n⿕')
        page_name = page_name.replace('ñ'.upper(), 'n⿕')

    elif language_code == 'fi':
        page_name = page_name.replace('å', 'z⿕')
        page_name = page_name.replace('å'.upper(), 'z⿕')
        page_name = page_name.replace('ä', 'z⿕⿕')
        page_name = page_name.replace('ä'.upper(), 'z⿕⿕')
        page_name = page_name.replace('ö', 'z⿕⿕⿕')
        page_name = page_name.replace('ö'.upper(), 'z⿕⿕⿕')

    elif language_code == 'lac':
        page_name = page_name.replace('ꞌ', '')
        page_name = page_name.replace('ʌ', 'a⿕')
        page_name = page_name.replace('ʌ'.upper(), 'a⿕')

    elif language_code == 'lv':
        page_name = page_name.replace('ā', 'a⿕')
        page_name = page_name.replace('č', 'c⿕')
        page_name = page_name.replace('ē', 'e⿕')
        page_name = page_name.replace('ģ', 'g⿕')
        page_name = page_name.replace('ī', 'i⿕')
        page_name = page_name.replace('ķ', 'k⿕')
        page_name = page_name.replace('ļ', 'l⿕')
        page_name = page_name.replace('ņ', 'n⿕')
        page_name = page_name.replace('š', 's⿕')
        page_name = page_name.replace('ū', 'u⿕')
        page_name = page_name.replace('ž', 'z⿕')

    elif language_code == 'mt':
        # source : Document MSA (2009) p. 7
        page_name = page_name.replace('ċ', 'b⿕') # pour éviter après le « c » dans les emprunts
        page_name = page_name.replace('ġ', 'f⿕')
        page_name = page_name.replace('għ', 'g⿕')
        page_name = page_name.replace('ħ', 'h⿕')
        page_name = page_name.replace('ie', 'i⿕')
        page_name = page_name.replace('ż', 'y⿕')

    elif language_code == 'os':
        page_name = page_name.replace('ё', 'е⿕')
        page_name = page_name.replace('ё'.upper(), 'е⿕')
        page_name = page_name.replace('ӕ', 'а⿕')
        page_name = page_name.replace('ӕ'.upper(), 'а⿕')
        # Digrammes
        page_name = page_name.replace('гъ', 'г⿕')
        page_name = page_name.replace('дж', 'д⿕')
        page_name = page_name.replace('дз', 'д⿕⿕')
        page_name = page_name.replace('къ', 'к⿕')
        page_name = page_name.replace('пъ', 'п⿕')
        page_name = page_name.replace('тъ', 'т⿕')
        page_name = page_name.replace('хъ', 'х⿕')
        page_name = page_name.replace('цъ', 'ц⿕')
        page_name = page_name.replace('чъ', 'ч⿕')

    elif language_code == 'ru':
        # page_name = page_name.replace('ё', 'е⿕')
        # page_name = page_name.replace('ё'.upper(), 'е⿕')
        page_name = page_name.replace('ӕ', 'а⿕')
        page_name = page_name.replace('ӕ'.upper(), 'а⿕')

    elif language_code == 'sl':
        page_name = page_name.replace('č', 'c⿕')
        page_name = page_name.replace('č'.upper(), 'c⿕')
        page_name = page_name.replace('š', 's⿕')
        page_name = page_name.replace('š'.upper(), 's⿕')
        page_name = page_name.replace('ž', 'z⿕')
        page_name = page_name.replace('ž'.upper(), 'z⿕')

    elif language_code == 'sv':
        page_name = page_name.replace('å', 'z⿕')
        page_name = page_name.replace('å'.upper(), 'z⿕')
        page_name = page_name.replace('ä', 'z⿕⿕')
        page_name = page_name.replace('ä'.upper(), 'z⿕⿕')
        page_name = page_name.replace('ö', 'z⿕⿕⿕')
        page_name = page_name.replace('ö'.upper(), 'z⿕⿕⿕')

    elif language_code == 'shi':
        page_name = page_name.replace('g', 'b龠')
        page_name = page_name.replace('ḍ', 'd龠')
        page_name = page_name.replace('k', 'f龠')
        page_name = page_name.replace('ḥ', 'h龠')
        page_name = page_name.replace('ɛ', 'h龠龠')
        page_name = page_name.replace('x', 'h龠龠龠')
        page_name = page_name.replace('q', 'h龠龠龠龠')
        page_name = page_name.replace('u', 'n龠')
        page_name = page_name.replace('ṛ', 'r龠')
        page_name = page_name.replace('ɣ', 'r龠龠')
        page_name = page_name.replace('ṣ', 's龠')
        page_name = page_name.replace('c', 's龠龠')
        page_name = page_name.replace('ṭ', 't龠')
        page_name = page_name.replace('w', 't龠龠')
        page_name = page_name.replace('ẓ', 'z龠')
        page_name = page_name.replace('ʷ', 'z龠龠')
        page_name = page_name.replace('°', 'z龠龠龠')

    elif language_code == 'vi':
        page_name = page_name.replace('ả', 'a⿕')
        page_name = page_name.replace('ả'.upper(), 'a')
        page_name = page_name.replace('ă', 'a⿕')
        page_name = page_name.replace('ă'.upper(), 'a⿕')
        page_name = page_name.replace('ắ', 'a⿕')
        page_name = page_name.replace('ắ'.upper(), 'a⿕')
        page_name = page_name.replace('ặ', 'a⿕')
        page_name = page_name.replace('ặ'.upper(), 'a⿕')
        page_name = page_name.replace('ẳ', 'a⿕')
        page_name = page_name.replace('ẳ'.upper(), 'a⿕')
        page_name = page_name.replace('ằ', 'a⿕')
        page_name = page_name.replace('ằ'.upper(), 'a⿕')
        page_name = page_name.replace('â', 'a⿕⿕')
        page_name = page_name.replace('â'.upper(), 'a⿕⿕')
        page_name = page_name.replace('ầ', 'a⿕⿕')
        page_name = page_name.replace('ầ'.upper(), 'a⿕⿕')
        page_name = page_name.replace('ậ', 'a⿕⿕')
        page_name = page_name.replace('ậ'.upper(), 'a⿕⿕')
        page_name = page_name.replace('ấ', 'a⿕⿕')
        page_name = page_name.replace('ấ'.upper(), 'a⿕⿕')
        page_name = page_name.replace('ẩ', 'a⿕⿕')
        page_name = page_name.replace('ẩ'.upper(), 'a⿕⿕')
        page_name = page_name.replace('đ', 'd⿕')
        page_name = page_name.replace('đ'.upper(), 'd⿕')
        page_name = page_name.replace('ẹ', 'e')
        page_name = page_name.replace('ẹ'.upper(), 'e')
        page_name = page_name.replace('ê', 'e⿕')
        page_name = page_name.replace('ê'.upper(), 'e⿕')
        page_name = page_name.replace('ệ', 'e⿕')
        page_name = page_name.replace('ệ'.upper(), 'e⿕')
        page_name = page_name.replace('ễ', 'e⿕')
        page_name = page_name.replace('ễ'.upper(), 'e⿕')
        page_name = page_name.replace('ề', 'e⿕')
        page_name = page_name.replace('ề'.upper(), 'e⿕')
        page_name = page_name.replace('ể', 'e⿕')
        page_name = page_name.replace('ể'.upper(), 'e⿕')
        page_name = page_name.replace('ị', 'i')
        page_name = page_name.replace('ị'.upper(), 'i')
        page_name = page_name.replace('ì', 'i')
        page_name = page_name.replace('ì'.upper(), 'i')
        page_name = page_name.replace('í', 'i')
        page_name = page_name.replace('í'.upper(), 'i')
        page_name = page_name.replace('ỉ', 'i')
        page_name = page_name.replace('ỉ'.upper(), 'i')
        page_name = page_name.replace('î', 'i')
        page_name = page_name.replace('î'.upper(), 'i')
        page_name = page_name.replace('ĩ', 'i')
        page_name = page_name.replace('ĩ'.upper(), 'i')
        page_name = page_name.replace('ọ', 'o')
        page_name = page_name.replace('ọ'.upper(), 'o')
        page_name = page_name.replace('ỏ', 'o')
        page_name = page_name.replace('ỏ'.upper(), 'o')
        page_name = page_name.replace('ô', 'o⿕')
        page_name = page_name.replace('ô'.upper(), 'o⿕')
        page_name = page_name.replace('ơ', 'o⿕⿕')
        page_name = page_name.replace('ơ'.upper(), 'o⿕⿕')
        page_name = page_name.replace('ộ', 'o⿕')
        page_name = page_name.replace('ộ'.upper(), 'o⿕')
        page_name = page_name.replace('ố', 'o⿕')
        page_name = page_name.replace('ố'.upper(), 'o⿕')
        page_name = page_name.replace('ồ', 'o⿕')
        page_name = page_name.replace('ồ'.upper(), 'o⿕')
        page_name = page_name.replace('ổ', 'o⿕')
        page_name = page_name.replace('ổ'.upper(), 'o⿕')
        page_name = page_name.replace('ỗ', 'o⿕')
        page_name = page_name.replace('ỗ'.upper(), 'o⿕')
        page_name = page_name.replace('ỡ', 'o⿕⿕')
        page_name = page_name.replace('ỡ'.upper(), 'o⿕⿕')
        page_name = page_name.replace('ở', 'o⿕⿕')
        page_name = page_name.replace('ở'.upper(), 'o⿕⿕')
        page_name = page_name.replace('ớ', 'o⿕⿕')
        page_name = page_name.replace('ớ'.upper(), 'o⿕⿕')
        page_name = page_name.replace('ờ', 'o⿕⿕')
        page_name = page_name.replace('ờ'.upper(), 'o⿕⿕')
        page_name = page_name.replace('ụ', 'u')
        page_name = page_name.replace('ụ'.upper(), 'u')
        page_name = page_name.replace('ủ', 'u')
        page_name = page_name.replace('ủ'.upper(), 'u')
        page_name = page_name.replace('ư', 'u⿕')
        page_name = page_name.replace('ư'.upper(), 'u⿕')
        page_name = page_name.replace('ử', 'u⿕')
        page_name = page_name.replace('ử'.upper(), 'u⿕')
        page_name = page_name.replace('ự', 'u⿕')
        page_name = page_name.replace('ự'.upper(), 'u⿕')
        page_name = page_name.replace('ừ', 'u⿕')
        page_name = page_name.replace('ừ'.upper(), 'u⿕')
        page_name = page_name.replace('ữ', 'u⿕')
        page_name = page_name.replace('ữ'.upper(), 'u⿕')

    return page_name


def trim(s):
    return s.strip(" \t\n\r\0\x0B")


def compare(string1, string2):
    return sort_by_encoding(string1, 'UTF-8') > sort_by_encoding(string2, 'UTF-8')

# TODO : tsolyáni, {{clé de tri|dhu'onikh}}<!-- exception à la règle de la clé de tri car "'" est une lettre à part entière en tsolyáni -->

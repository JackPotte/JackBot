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
        if page_name.find('ch') != -1:
            page_name = page_name.replace('ch', 'c⿕')
        if page_name.find('ch'.upper()) != -1:
            page_name = page_name.replace('ch'.upper(), 'c⿕')
        if page_name.find('cʼh') != -1:
            page_name = page_name.replace('cʼh', 'c⿕⿕')
        if page_name.find('cʼh'.upper()) != -1:
            page_name = page_name.replace('cʼh'.upper(), 'c⿕⿕')

    elif language_code == 'es':
        if page_name.find('ñ') != -1:
            page_name = page_name.replace('ñ', 'n⿕')
        if page_name.find('ñ'.upper()) != -1:
            page_name = page_name.replace('ñ'.upper(), 'n⿕')

    elif language_code == 'fi':
        if page_name.find('å') != -1:
            page_name = page_name.replace('å', 'z⿕')
        if page_name.find('å'.upper()) != -1:
            page_name = page_name.replace('å'.upper(), 'z⿕')
        if page_name.find('ä') != -1:
            page_name = page_name.replace('ä', 'z⿕⿕')
        if page_name.find('ä'.upper()) != -1:
            page_name = page_name.replace('ä'.upper(), 'z⿕⿕')
        if page_name.find('ö') != -1:
            page_name = page_name.replace('ö', 'z⿕⿕⿕')
        if page_name.find('ö'.upper()) != -1:
            page_name = page_name.replace('ö'.upper(), 'z⿕⿕⿕')

    elif language_code == 'os':
        if page_name.find('ё') != -1:
            page_name = page_name.replace('ё', 'е⿕')
        if page_name.find('ё'.upper()) != -1:
            page_name = page_name.replace('ё'.upper(), 'е⿕')
        if page_name.find('ӕ') != -1:
            page_name = page_name.replace('ӕ', 'а⿕')
        if page_name.find('ӕ'.upper()) != -1:
            page_name = page_name.replace('ӕ'.upper(), 'а⿕')
        # Digrammes
        if page_name.find('гъ') != -1:
            page_name = page_name.replace('гъ', 'г⿕')
        if page_name.find('дж') != -1:
            page_name = page_name.replace('дж', 'д⿕')
        if page_name.find('дз') != -1:
            page_name = page_name.replace('дз', 'д⿕⿕')
        if page_name.find('къ') != -1:
            page_name = page_name.replace('къ', 'к⿕')
        if page_name.find('пъ') != -1:
            page_name = page_name.replace('пъ', 'п⿕')
        if page_name.find('тъ') != -1:
            page_name = page_name.replace('тъ', 'т⿕')
        if page_name.find('хъ') != -1:
            page_name = page_name.replace('хъ', 'х⿕')
        if page_name.find('цъ') != -1:
            page_name = page_name.replace('цъ', 'ц⿕')
        if page_name.find('чъ') != -1:
            page_name = page_name.replace('чъ', 'ч⿕')

    elif language_code == 'ru':
        # if page_name.find('ё') != -1: page_name = page_name.replace('ё', 'е⿕')
        # if page_name.find('ё'.upper()) != -1: page_name = page_name.replace('ё'.upper(), 'е⿕')
        if page_name.find('ӕ') != -1:
            page_name = page_name.replace('ӕ', 'а⿕')
        if page_name.find('ӕ'.upper()) != -1:
            page_name = page_name.replace('ӕ'.upper(), 'а⿕')

    if language_code == 'sl':
        if page_name.find('č') != -1:
            page_name = page_name.replace('č', 'c⿕')
        if page_name.find('č'.upper()) != -1:
            page_name = page_name.replace('č'.upper(), 'c⿕')
        if page_name.find('š') != -1:
            page_name = page_name.replace('š', 's⿕')
        if page_name.find('š'.upper()) != -1:
            page_name = page_name.replace('š'.upper(), 's⿕')
        if page_name.find('ž') != -1:
            page_name = page_name.replace('ž', 'z⿕')
        if page_name.find('ž'.upper()) != -1:
            page_name = page_name.replace('ž'.upper(), 'z⿕')

    elif language_code == 'sv':
        if page_name.find('å') != -1:
            page_name = page_name.replace('å', 'z⿕')
        if page_name.find('å'.upper()) != -1:
            page_name = page_name.replace('å'.upper(), 'z⿕')
        if page_name.find('ä') != -1:
            page_name = page_name.replace('ä', 'z⿕⿕')
        if page_name.find('ä'.upper()) != -1:
            page_name = page_name.replace('ä'.upper(), 'z⿕⿕')
        if page_name.find('ö') != -1:
            page_name = page_name.replace('ö', 'z⿕⿕⿕')
        if page_name.find('ö'.upper()) != -1:
            page_name = page_name.replace('ö'.upper(), 'z⿕⿕⿕')

    elif language_code == 'vi':
        if page_name.find('ả') != -1:
            page_name = page_name.replace('ả', 'a⿕')
        if page_name.find('ả'.upper()) != -1:
            page_name = page_name.replace('ả'.upper(), 'a')
        if page_name.find('ă') != -1:
            page_name = page_name.replace('ă', 'a⿕')
        if page_name.find('ă'.upper()) != -1:
            page_name = page_name.replace('ă'.upper(), 'a⿕')
        if page_name.find('ắ') != -1:
            page_name = page_name.replace('ắ', 'a⿕')
        if page_name.find('ắ'.upper()) != -1:
            page_name = page_name.replace('ắ'.upper(), 'a⿕')
        if page_name.find('ặ') != -1:
            page_name = page_name.replace('ặ', 'a⿕')
        if page_name.find('ặ'.upper()) != -1:
            page_name = page_name.replace('ặ'.upper(), 'a⿕')
        if page_name.find('ẳ') != -1:
            page_name = page_name.replace('ẳ', 'a⿕')
        if page_name.find('ẳ'.upper()) != -1:
            page_name = page_name.replace('ẳ'.upper(), 'a⿕')
        if page_name.find('ằ') != -1:
            page_name = page_name.replace('ằ', 'a⿕')
        if page_name.find('ằ'.upper()) != -1:
            page_name = page_name.replace('ằ'.upper(), 'a⿕')
        if page_name.find('â') != -1:
            page_name = page_name.replace('â', 'a⿕⿕')
        if page_name.find('â'.upper()) != -1:
            page_name = page_name.replace('â'.upper(), 'a⿕⿕')
        if page_name.find('ầ') != -1:
            page_name = page_name.replace('ầ', 'a⿕⿕')
        if page_name.find('ầ'.upper()) != -1:
            page_name = page_name.replace('ầ'.upper(), 'a⿕⿕')
        if page_name.find('ậ') != -1:
            page_name = page_name.replace('ậ', 'a⿕⿕')
        if page_name.find('ậ'.upper()) != -1:
            page_name = page_name.replace('ậ'.upper(), 'a⿕⿕')
        if page_name.find('ấ') != -1:
            page_name = page_name.replace('ấ', 'a⿕⿕')
        if page_name.find('ấ'.upper()) != -1:
            page_name = page_name.replace('ấ'.upper(), 'a⿕⿕')
        if page_name.find('ẩ') != -1:
            page_name = page_name.replace('ẩ', 'a⿕⿕')
        if page_name.find('ẩ'.upper()) != -1:
            page_name = page_name.replace('ẩ'.upper(), 'a⿕⿕')
        if page_name.find('đ') != -1:
            page_name = page_name.replace('đ', 'd⿕')
        if page_name.find('đ'.upper()) != -1:
            page_name = page_name.replace('đ'.upper(), 'd⿕')
        if page_name.find('ẹ') != -1:
            page_name = page_name.replace('ẹ', 'e')
        if page_name.find('ẹ'.upper()) != -1:
            page_name = page_name.replace('ẹ'.upper(), 'e')
        if page_name.find('ê') != -1:
            page_name = page_name.replace('ê', 'e⿕')
        if page_name.find('ê'.upper()) != -1:
            page_name = page_name.replace('ê'.upper(), 'e⿕')
        if page_name.find('ệ') != -1:
            page_name = page_name.replace('ệ', 'e⿕')
        if page_name.find('ệ'.upper()) != -1:
            page_name = page_name.replace('ệ'.upper(), 'e⿕')
        if page_name.find('ễ') != -1:
            page_name = page_name.replace('ễ', 'e⿕')
        if page_name.find('ễ'.upper()) != -1:
            page_name = page_name.replace('ễ'.upper(), 'e⿕')
        if page_name.find('ề') != -1:
            page_name = page_name.replace('ề', 'e⿕')
        if page_name.find('ề'.upper()) != -1:
            page_name = page_name.replace('ề'.upper(), 'e⿕')
        if page_name.find('ể') != -1:
            page_name = page_name.replace('ể', 'e⿕')
        if page_name.find('ể'.upper()) != -1:
            page_name = page_name.replace('ể'.upper(), 'e⿕')
        if page_name.find('ị') != -1:
            page_name = page_name.replace('ị', 'i')
        if page_name.find('ị'.upper()) != -1:
            page_name = page_name.replace('ị'.upper(), 'i')
        if page_name.find('ì') != -1:
            page_name = page_name.replace('ì', 'i')
        if page_name.find('ì'.upper()) != -1:
            page_name = page_name.replace('ì'.upper(), 'i')
        if page_name.find('í') != -1:
            page_name = page_name.replace('í', 'i')
        if page_name.find('í'.upper()) != -1:
            page_name = page_name.replace('í'.upper(), 'i')
        if page_name.find('ỉ') != -1:
            page_name = page_name.replace('ỉ', 'i')
        if page_name.find('ỉ'.upper()) != -1:
            page_name = page_name.replace('ỉ'.upper(), 'i')
        if page_name.find('î') != -1:
            page_name = page_name.replace('î', 'i')
        if page_name.find('î'.upper()) != -1:
            page_name = page_name.replace('î'.upper(), 'i')
        if page_name.find('ĩ') != -1:
            page_name = page_name.replace('ĩ', 'i')
        if page_name.find('ĩ'.upper()) != -1:
            page_name = page_name.replace('ĩ'.upper(), 'i')
        if page_name.find('ọ') != -1:
            page_name = page_name.replace('ọ', 'o')
        if page_name.find('ọ'.upper()) != -1:
            page_name = page_name.replace('ọ'.upper(), 'o')
        if page_name.find('ỏ') != -1:
            page_name = page_name.replace('ỏ', 'o')
        if page_name.find('ỏ'.upper()) != -1:
            page_name = page_name.replace('ỏ'.upper(), 'o')
        if page_name.find('ô') != -1:
            page_name = page_name.replace('ô', 'o⿕')
        if page_name.find('ô'.upper()) != -1:
            page_name = page_name.replace('ô'.upper(), 'o⿕')
        if page_name.find('ơ') != -1:
            page_name = page_name.replace('ơ', 'o⿕⿕')
        if page_name.find('ơ'.upper()) != -1:
            page_name = page_name.replace('ơ'.upper(), 'o⿕⿕')
        if page_name.find('ộ') != -1:
            page_name = page_name.replace('ộ', 'o⿕')
        if page_name.find('ộ'.upper()) != -1:
            page_name = page_name.replace('ộ'.upper(), 'o⿕')
        if page_name.find('ố') != -1:
            page_name = page_name.replace('ố', 'o⿕')
        if page_name.find('ố'.upper()) != -1:
            page_name = page_name.replace('ố'.upper(), 'o⿕')
        if page_name.find('ồ') != -1:
            page_name = page_name.replace('ồ', 'o⿕')
        if page_name.find('ồ'.upper()) != -1:
            page_name = page_name.replace('ồ'.upper(), 'o⿕')
        if page_name.find('ổ') != -1:
            page_name = page_name.replace('ổ', 'o⿕')
        if page_name.find('ổ'.upper()) != -1:
            page_name = page_name.replace('ổ'.upper(), 'o⿕')
        if page_name.find('ỗ') != -1:
            page_name = page_name.replace('ỗ', 'o⿕')
        if page_name.find('ỗ'.upper()) != -1:
            page_name = page_name.replace('ỗ'.upper(), 'o⿕')
        if page_name.find('ỡ') != -1:
            page_name = page_name.replace('ỡ', 'o⿕⿕')
        if page_name.find('ỡ'.upper()) != -1:
            page_name = page_name.replace('ỡ'.upper(), 'o⿕⿕')
        if page_name.find('ở') != -1:
            page_name = page_name.replace('ở', 'o⿕⿕')
        if page_name.find('ở'.upper()) != -1:
            page_name = page_name.replace('ở'.upper(), 'o⿕⿕')
        if page_name.find('ớ') != -1:
            page_name = page_name.replace('ớ', 'o⿕⿕')
        if page_name.find('ớ'.upper()) != -1:
            page_name = page_name.replace('ớ'.upper(), 'o⿕⿕')
        if page_name.find('ờ') != -1:
            page_name = page_name.replace('ờ', 'o⿕⿕')
        if page_name.find('ờ'.upper()) != -1:
            page_name = page_name.replace('ờ'.upper(), 'o⿕⿕')
        if page_name.find('ụ') != -1:
            page_name = page_name.replace('ụ', 'u')
        if page_name.find('ụ'.upper()) != -1:
            page_name = page_name.replace('ụ'.upper(), 'u')
        if page_name.find('ủ') != -1:
            page_name = page_name.replace('ủ', 'u')
        if page_name.find('ủ'.upper()) != -1:
            page_name = page_name.replace('ủ'.upper(), 'u')
        if page_name.find('ư') != -1:
            page_name = page_name.replace('ư', 'u⿕')
        if page_name.find('ư'.upper()) != -1:
            page_name = page_name.replace('ư'.upper(), 'u⿕')
        if page_name.find('ử') != -1:
            page_name = page_name.replace('ử', 'u⿕')
        if page_name.find('ử'.upper()) != -1:
            page_name = page_name.replace('ử'.upper(), 'u⿕')
        if page_name.find('ự') != -1:
            page_name = page_name.replace('ự', 'u⿕')
        if page_name.find('ự'.upper()) != -1:
            page_name = page_name.replace('ự'.upper(), 'u⿕')
        if page_name.find('ừ') != -1:
            page_name = page_name.replace('ừ', 'u⿕')
        if page_name.find('ừ'.upper()) != -1:
            page_name = page_name.replace('ừ'.upper(), 'u⿕')
        if page_name.find('ữ') != -1:
            page_name = page_name.replace('ữ', 'u⿕')
        if page_name.find('ữ'.upper()) != -1:
            page_name = page_name.replace('ữ'.upper(), 'u⿕')

    return page_name


def trim(s):
    return s.strip(" \t\n\r\0\x0B")


def compare(string1, string2):
    return sort_by_encoding(string1, 'UTF-8') > sort_by_encoding(string2, 'UTF-8')

# TODO : tsolyáni, {{clé de tri|dhu'onikh}}<!-- exception à la règle de la clé de tri car "'" est une lettre à part entière en tsolyáni -->

#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, unicode_literals
try:
    from src.lib import html2unicode
except ImportError:
    from lib import html2Unicode

debug_level = 0
'''TODO: uca-default gère af, am, ar, as, ast, az, be, be-tarask, bg, bn, bn@collation=traditional, bo, br, bs, 
    bs-Cyrl, ca, chr, co, cs, cy, da, de, de-AT@collation=phonebook, dsb, ee, el, en, eo, es, et, eu, fa, fi, 
    fil, fo, fr, fr-CA, fur, fy, ga, gd, gl, gu, ha, haw, he, hi, hr, hsb, hu, hy, id, ig, is, it, ka, kk, kl, 
    km, kn, kok, ku, ky, la, lb, lkt, ln, lo, lt, lv, mk, ml, mn, mo, mr, ms, mt, nb, ne, nl, nn, no, oc, om, 
    or, pa, pl, pt, rm, ro, ru, rup, sco, se, si, sk, sl, smn, sq, sr, sr-Latn, sv, sv@collation=standard, sw, 
    ta, te, th, tk, tl, to, tr, tt, uk, uz, vi, vo, yi, yo, zu
'''


def default_sort(page_name, encoding='uca-default'):
    if debug_level > 0:
        print(' defaultSort.default_sort()')

    page_name = html2Unicode.html2unicode(page_name)
    word_key = ''
    add_key = False

    for letter in page_name:
        letter_to_treat = False
        if letter in ('’', '\''): # 'ʼ' : pb en breton
            add_key = True
        elif letter in ('\\', '/', '×', '·', '…', '-', '\'', '.', ',', '(', ')'):
            word_key += ' '
            add_key = True
        elif encoding != 'uca-default':
            # Latin
            if letter == 'à' or letter == 'Á' or letter == 'á' or letter == 'â' or letter == 'ä' or \
                letter == 'ā' or letter == 'ă' or letter == 'ą' or letter == 'ǎ' or letter == 'ǻ' or \
                letter == 'ȁ' or letter == 'ȃ' or letter == 'ȧ' or letter == 'ɑ' or letter == 'ạ' or \
                letter == 'ả' or letter == 'ấ' or letter == 'Ấ' or letter == 'ⱥ' or letter == 'À' or \
                letter == 'Â' or letter == 'Ä' or letter == 'Å' or letter == 'Ā' or letter == 'Ă' or \
                letter == 'Ą' or letter == 'Ǎ' or letter == 'Ǻ' or letter == 'Ȁ' or letter == 'Ȃ' or \
                letter == 'Ȧ' or letter == 'Ⱥ' or letter == 'Ɑ' or letter == 'Ǟ' or letter == 'Ǡ' or \
                letter == 'ắ' or letter == 'Ắ' or letter == 'å' or letter == 'Å' or letter == 'ã' or \
                letter == 'Ã':
                word_key += "a"
                add_key = True
            elif letter == 'æ' or letter == 'ǣ' or letter == 'ǽ' or letter == 'Æ' or letter == 'Ǣ' or letter == 'Ǽ':
                word_key += "ae"
                add_key = True
            elif letter == 'ƀ' or letter == 'ƃ' or letter == 'Ɓ' or letter == 'Ƃ' or letter == 'Ƀ':
                word_key += "b"
                add_key = True
            elif letter == 'ç' or letter == 'ć' or letter == 'ċ' or letter == 'č' or letter == 'ƈ' or \
                letter == 'ȼ' or letter == 'Ç' or letter == 'Ć' or letter == 'Ĉ' or letter == 'Ċ' or \
                letter == 'Č' or letter == 'Ƈ' or letter == 'Ȼ':
                word_key += "c"
                add_key = True
            elif letter == 'ĉ':
                word_key += "cx"
                add_key = True
            elif letter == 'ď' or letter == 'đ' or letter == 'ƌ' or letter == 'ȡ' or letter == 'Ď' or \
                letter == 'Đ' or letter == 'Ɖ' or letter == 'Ɗ' or letter == 'Ƌ' or letter == 'ȸ' or \
                letter == 'ǆ' or letter == 'ǳ' or letter == 'Ǆ' or letter == 'ǅ' or letter == 'Ǳ' or \
                letter == 'ǲ':
                word_key += "d"
                add_key = True
            elif letter == 'è' or letter == 'È' or letter == 'é' or letter == 'É' or letter == 'ê' or \
                letter == 'Ê' or letter == 'ë' or letter == 'Ë' or letter == 'ē' or letter == 'ĕ' or \
                letter == 'ė' or letter == 'ę' or letter == 'ě' or letter == 'ǝ' or letter == 'ɛ' or \
                letter == 'ȅ' or letter == 'ȇ' or letter == 'ȩ' or letter == 'ɇ' or letter == 'ế' or \
                letter == 'Ế' or letter == 'Ē' or letter == 'Ĕ' or letter == 'Ė' or letter == 'Ę' or \
                letter == 'Ě' or letter == 'Ǝ' or letter == 'Ɛ' or letter == 'Ȅ' or letter == 'Ȇ' or \
                letter == 'Ȩ' or letter == 'Ɇ' or letter == 'ệ' or letter == 'Ệ':
                word_key += "e"
                add_key = True
            elif letter == 'ƒ' or letter == 'Ƒ':
                word_key += "f"
                add_key = True
            elif letter == 'ĝ':
                word_key += "gx"
                add_key = True
            elif letter == 'ğ' or letter == 'ġ' or letter == 'ģ' or letter == 'ǥ' or letter == 'ǧ' or \
                letter == 'ǵ' or letter == 'Ĝ' or letter == 'Ğ' or letter == 'Ġ' or letter == 'Ģ' or \
                letter == 'Ɠ' or letter == 'Ǥ' or letter == 'Ǧ' or letter == 'Ǵ':
                word_key += "g"
                add_key = True
            elif letter == 'ĥ':
                word_key += "hx"
                add_key = True
            elif letter == 'ħ' or letter == 'ȟ' or letter == 'Ĥ' or letter == 'Ħ' or letter == 'Ȟ':
                word_key += "h"
                add_key = True
            elif letter == 'ı' or letter == 'î' or letter == 'ĩ' or letter == 'ī' or letter == 'ĭ' or \
                letter == 'į' or letter == 'ǐ' or letter == 'ȉ' or letter == 'ȋ' or letter == 'Î' or \
                letter == 'Ĩ' or letter == 'Ī' or letter == 'Ĭ' or letter == 'Į' or letter == 'İ' or \
                letter == 'Ɨ' or letter == 'Ǐ' or letter == 'Ȉ' or letter == 'Ȋ' or letter == 'ĳ' or \
                letter == 'Ĳ' or letter == 'ì' or letter == 'Ì' or letter == 'ï' or letter == 'Ï' or \
                letter == 'ǈ' or letter == 'ị' or letter == 'Ị' or letter == 'í' or letter == 'Í':
                word_key += "i"
                add_key = True
            elif letter == 'ĵ':
                word_key += "jx"
                add_key = True
            elif letter == 'ǰ' or letter == 'ȷ' or letter == 'ɉ' or letter == 'Ĵ' or letter == 'Ɉ':
                word_key += "j"
                add_key = True
            elif letter == 'ķ' or letter == 'ƙ' or letter == 'ǩ' or letter == 'Ķ' or letter == 'Ƙ' or letter == 'Ǩ':
                word_key += "k"
                add_key = True
            elif letter == 'ĺ' or letter == 'ļ' or letter == 'ľ' or letter == 'ŀ' or letter == 'ł' or \
                letter == 'ƚ' or letter == 'ȴ' or letter == 'ɫ' or letter == 'Ɫ' or letter == 'Ĺ' or \
                letter == 'Ļ' or letter == 'Ľ' or letter == 'Ŀ' or letter == 'Ł' or letter == 'Ƚ' or \
                letter == 'ǉ' or letter == 'Ǉ':
                word_key += "l"
                add_key = True
            elif letter == 'Ɯ':
                word_key += "m"
                add_key = True
            elif letter == 'ń' or letter == 'ņ' or letter == 'ň' or letter == 'ŋ' or letter == 'ǹ' or \
                letter == 'ƞ' or letter == 'ȵ' or letter == 'Ń' or letter == 'Ņ' or letter == 'Ň' or \
                letter == 'Ŋ' or letter == 'Ɲ' or letter == 'Ǹ' or letter == 'Ƞ' or letter == 'ǌ' or \
                letter == 'Ǌ' or letter == 'ǋ' or letter == 'ɲ' or letter == 'ṉ' or letter == 'Ṉ' or \
                letter == 'ñ' or letter == 'Ñ':
                word_key += "n"
                add_key = True
            elif letter == 'ô' or letter == 'Ô' or letter == 'ø' or letter == 'ō' or letter == 'ŏ' or \
                letter == 'ő' or letter == 'ơ' or letter == 'ǒ' or letter == 'ǫ' or letter == 'ǭ' or \
                letter == 'ǿ' or letter == 'ȍ' or letter == 'ȏ' or letter == 'ȫ' or letter == 'ȭ' or \
                letter == 'ȯ' or letter == 'ȱ' or letter == 'Ø' or letter == 'Ō' or letter == 'Ŏ' or \
                letter == 'Ő' or letter == 'Ɔ' or letter == 'Ɵ' or letter == 'ɵ' or letter == 'Ơ' or \
                letter == 'Ǒ' or letter == 'Ǫ' or letter == 'Ǭ' or letter == 'Ǿ' or letter == 'Ȍ' or \
                letter == 'Ȏ' or letter == 'Ȫ' or letter == 'Ȭ' or letter == 'Ȯ' or letter == 'Ȱ' or \
                letter == 'ɔ' or letter == 'ở' or letter == 'Ở' or letter == 'ợ' or letter == 'Ợ' or \
                letter == 'ò' or letter == 'ó' or letter == 'ö' or letter == 'Ö' or letter == 'õ' or \
                letter == 'Õ':
                word_key += "o"
                add_key = True
            elif letter == 'œ' or letter == 'Œ':
                word_key += "oe"
                add_key = True
            elif letter == 'ƥ' or letter == 'Ƥ':
                word_key += "p"
                add_key = True
            elif letter == 'ɋ' or letter == 'Ɋ' or letter == 'ȹ':
                word_key += "q"
                add_key = True
            elif letter == 'ŕ' or letter == 'ŗ' or letter == 'ř' or letter == 'ȑ' or letter == 'ȓ' or \
                letter == 'ɍ' or letter == 'Ŕ' or letter == 'Ŗ' or letter == 'Ř' or letter == 'Ȑ' or \
                letter == 'Ȓ' or letter == 'Ɍ':
                word_key += "r"
                add_key = True
            elif letter == 'ŝ':
                word_key += "sx"
                add_key = True
            elif letter == 'ſ' or letter == 'ś' or letter == 'ş' or letter == 'š' or letter == 'ƪ' or \
                letter == 'ș' or letter == 'ȿ' or letter == 'Ś' or letter == 'Ŝ' or letter == 'Ş' or \
                letter == 'Š' or letter == 'Ʃ' or letter == 'Ș' or letter == 'ß':
                word_key += "s"
                add_key = True
            elif letter == 'ţ' or letter == 'ť' or letter == 'ŧ' or letter == 'ƫ' or letter == 'ƭ' or \
                letter == 'ț' or letter == 'ȶ' or letter == 'Ţ' or letter == 'Ť' or letter == 'Ŧ' or \
                letter == 'Ƭ' or letter == 'Ʈ' or letter == 'Ț' or letter == 'Ⱦ' or letter == 'ⱦ':
                word_key += "t"
                add_key = True
            elif letter == 'ŭ':
                word_key += "ux"
                add_key = True
            elif letter == 'û' or letter == 'ũ' or letter == 'ū' or letter == 'ů' or letter == 'ű' or \
                letter == 'ų' or letter == 'ư' or letter == 'ǔ' or letter == 'ǖ' or letter == 'ǘ' or \
                letter == 'ǚ' or letter == 'ǜ' or letter == 'ǟ' or letter == 'ǡ' or letter == 'ȕ' or \
                letter == 'ȗ' or letter == 'ʉ' or letter == 'Û' or letter == 'Ũ' or letter == 'Ū' or \
                letter == 'Ŭ' or letter == 'Ů' or letter == 'Ű' or letter == 'Ų' or letter == 'Ư' or \
                letter == 'Ǔ' or letter == 'Ǖ' or letter == 'Ǘ' or letter == 'Ǚ' or letter == 'Ǜ' or \
                letter == 'Ȕ' or letter == 'Ȗ' or letter == 'Ʉ' or letter == 'ủ' or letter == 'Ủ' or \
                letter == 'ú' or letter == 'Ú' or letter == 'ù' or letter == 'Ù' or letter == 'ü' or \
                letter == 'Ü':
                word_key += "u"
                add_key = True
            elif letter == 'ʋ' or letter == 'Ʋ' or letter == 'Ʌ' or letter == 'ʌ':
                word_key += "v"
                add_key = True
            elif letter == 'ŵ' or letter == 'Ŵ':
                word_key += "w"
                add_key = True
            elif letter == 'ŷ' or letter == 'ƴ' or letter == 'ȳ' or letter == 'ɏ' or letter == 'Ŷ' or \
                letter == 'Ÿ' or letter == 'Ƴ' or letter == 'Ȳ' or letter == 'Ɏ':
                word_key += "y"
                add_key = True
            elif letter == 'ź' or letter == 'ż' or letter == 'ž' or letter == 'ƶ' or letter == 'ƹ' or \
                letter == 'ƺ' or letter == 'ǯ' or letter == 'ȥ' or letter == 'ɀ' or letter == 'Ź' or \
                letter == 'Ż' or letter == 'Ž' or letter == 'Ƶ' or letter == 'Ʒ' or letter == 'Ƹ' or \
                letter == 'Ǯ' or letter == 'Ȥ':
                word_key += "z"
                add_key = True

            elif letter == 'A' or letter == 'B' or letter == 'C' or letter == 'D' or letter == 'E' or \
                letter == 'F' or letter == 'G' or letter == 'H' or letter == 'I' or letter == 'J' or \
                letter == 'K' or letter == 'L' or letter == 'M' or letter == 'N' or letter == 'O' or \
                letter == 'P' or letter == 'Q' or letter == 'R' or letter == 'S' or letter == 'T' or \
                letter == 'U' or letter == 'V' or letter == 'W' or letter == 'X' or letter == 'Y' or \
                letter == 'Z':
                word_key += letter.lower()
            else:
                letter_to_treat = True
        else:
          letter_to_treat = True  

        if letter_to_treat:
           word_key += letter

    if add_key:
        return trim(word_key.replace('  ', ' '))
    else:
        if debug_level > 0: input(page_name)
        return page_name


def add_default_sort(page_name, page_content, empty = False):
    page_content = page_content.replace('{{DEFAULTSORT:', '{{clé de tri|')
    page_content = page_content.replace('{{defaultSort:', '{{clé de tri|')
    page_content = page_content.replace('{{clef de tri|', '{{clé de tri|')
    while page_content.find('\n{clé de tri') != -1:
        page_content = page_content[:page_content.find('\n{clé de tri')+1] + '{' + page_content[page_content.find('\n{clé de tri'):]

    if empty:
        ClePage = ''
    else:
        ClePage = default_sort(page_name)

    if page_content.find('{{clé de tri') == -1 and ClePage != '' and ClePage.lower() != page_name.lower():
            #summary = summary + ', {{clé de tri}} ajoutée'
            if page_content.rfind('\n\n[[') != -1:
                page_content2 = page_content[page_content.rfind('\n\n[['):]
                if page_content2[4:5] == ':' or page_content2[5:6] == ':':
                    page_content = page_content[:page_content.rfind('\n\n[[')] + '\n\n{{clé de tri|' + ClePage + '}}' + \
                        page_content[page_content.rfind('\n\n[['):]
                else:
                    page_content = page_content + '\n\n{{clé de tri|' + ClePage + '}}\n'
            else:
                page_content = page_content + '\n\n{{clé de tri|' + ClePage + '}}\n'

    elif page_content.find('{{clé de tri|') != -1 and (page_content.find('{{langue|fr}}') != -1 or \
        page_content.find('{{langue|eo}}') != -1 or page_content.find('{{langue|en}}') != -1 or \
        page_content.find('{{langue|es}}') != -1 or page_content.find('{{langue|de}}') != -1 or \
        page_content.find('{{langue|pt}}') != -1 or page_content.find('{{langue|it}}') != -1):
        if debug_level > 0: print(' vérification de clé existante pour alphabets connus')
        page_content2 = page_content[page_content.find('{{clé de tri|')+len('{{clé de tri|'):]
        ClePage = page_content2[0:page_content2.find('}}')]
        '''if CleTri.lower() != ClePage.lower():
            summary = summary + ', {{clé de tri}} corrigée'
            page_content = page_content[:page_content.find('{{clé de tri|')+len('{{clé de tri|')] + CleTri + page_content[page_content.find('{{clé de tri|')+len('{{clé de tri|')+page_content2.find('}}'):]'''
        '''pb ʻokina
            if CleTri.lower() == page_name.lower():
            summary = summary + ', {{clé de tri}} supprimée'
            page_content = page_content[:page_content.find('{{clé de tri|')] + page_content[page_content.find('{{clé de tri|')+len('{{clé de tri|')+page_content2.find('}}')+2:]'''
    if debug_level > 1: input(page_content)

    baratin = '{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
    if page_content.find(baratin) != -1:
        page_content = page_content[:page_content.find(baratin)] + page_content[page_content.find(baratin)+len(baratin):]
        #summary = summary + ', {{clé de tri|}} supprimée'
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
        page_content2 = page_content[page_content.find('{{S|verbe pronominal|'):]
        if page_content2.find('{{conj') != -1 and page_content2.find('{{pronominal|') == -1 and page_content2.find('{{pronl|') == -1 and page_content2.find('{{prnl|') == -1 and page_content2.find('{{réflexif|') == -1 and page_content2.find('{{réfléchi|') == -1 and page_content2.find('{{réfl|') == -1:
            page_content3 = page_content2[page_content2.find('{{conj'):]
            if page_content3.find('|prnl=') == -1 or page_content3.find('|prnl=') > page_content3.find('}}'):
                page_content = page_content[:page_content.find('{{S|verbe pronominal|')] + page_content2[:page_content2.find('{{conj')] + page_content3[:page_content3.find('}}')] + '|prnl=1' + page_content3[page_content3.find('}}'):]
        page_content = page_content[:page_content.find('{{S|verbe pronominal|')] + '{{S|verbe|' + page_content[page_content.find('{{S|verbe pronominal|')+len('{{S|verbe pronominal|'):]
    while page_content.find('\'\'(pronominal)\'\'') != -1:
        page_content2 = page_content[page_content.find('\'\'(pronominal)\'\''):]
        if page_content2.find('|prnl=1') != -1 and page_content2.find('|prnl=1') < page_content2.find('\n'):
            page_content = page_content[:page_content.find('\'\'(pronominal)\'\'')] + page_content[page_content.find('\'\'(pronominal)\'\'')+ len('\'\'(pronominal)\'\''):]
        else:
            page_content = page_content[:page_content.find('\'\'(pronominal)\'\'')] + '{{prnl}}' + page_content[page_content.find('\'\'(pronominal)\'\'')+ len('\'\'(pronominal)\'\''):]

    return page_content


def default_sort_by_language(page_name, language_code):
    if language_code == 'br':
        if page_name.find('cʼh') !=-1: page_name = page_name.replace('cʼh','c⿕h')
        if page_name.find('cʼh'.upper()) !=-1: page_name = page_name.replace('cʼh'.upper(),'c⿕h')

    elif language_code == 'es':
        if page_name.find('ñ') !=-1: page_name = page_name.replace('ñ','n⿕')
        if page_name.find('ñ'.upper()) !=-1: page_name = page_name.replace('ñ'.upper(),'n⿕')

    elif language_code == 'fi':
        if page_name.find('å') !=-1: page_name = page_name.replace('å','z⿕')
        if page_name.find('å'.upper()) !=-1: page_name = page_name.replace('å'.upper(),'z⿕')
        if page_name.find('ä') !=-1: page_name = page_name.replace('ä','z⿕⿕')
        if page_name.find('ä'.upper()) !=-1: page_name = page_name.replace('ä'.upper(),'z⿕⿕')
        if page_name.find('ö') !=-1: page_name = page_name.replace('ö','z⿕⿕⿕')
        if page_name.find('ö'.upper()) !=-1: page_name = page_name.replace('ö'.upper(),'z⿕⿕⿕')

    elif language_code == 'os':
        if page_name.find('ё') !=-1: page_name = page_name.replace('ё',u'е⿕')
        if page_name.find('ё'.upper()) !=-1: page_name = page_name.replace('ё'.upper(),u'е⿕')
        if page_name.find('ӕ') !=-1: page_name = page_name.replace('ӕ',u'а⿕')
        if page_name.find('ӕ'.upper()) !=-1: page_name = page_name.replace('ӕ'.upper(),u'а⿕')
        # Digrammes
        if page_name.find('гъ') !=-1: page_name = page_name.replace('гъ',u'г⿕')
        if page_name.find('дж') !=-1: page_name = page_name.replace('дж',u'д⿕')
        if page_name.find('дз') !=-1: page_name = page_name.replace('дз',u'д⿕⿕')
        if page_name.find('къ') !=-1: page_name = page_name.replace('къ',u'к⿕')
        if page_name.find('пъ') !=-1: page_name = page_name.replace('пъ',u'п⿕')
        if page_name.find('тъ') !=-1: page_name = page_name.replace('тъ',u'т⿕')
        if page_name.find('хъ') !=-1: page_name = page_name.replace('хъ',u'х⿕')
        if page_name.find('цъ') !=-1: page_name = page_name.replace('цъ',u'ц⿕')
        if page_name.find('чъ') !=-1: page_name = page_name.replace('чъ',u'ч⿕')

    elif language_code == 'ru':
        #if page_name.find('ё') !=-1: page_name = page_name.replace('ё',u'е⿕')
        #if page_name.find('ё'.upper()) !=-1: page_name = page_name.replace('ё'.upper(),u'е⿕')
        if page_name.find('ӕ') !=-1: page_name = page_name.replace('ӕ',u'а⿕')
        if page_name.find('ӕ'.upper()) !=-1: page_name = page_name.replace('ӕ'.upper(),u'а⿕')

    if language_code == 'sl':
        if page_name.find('č') !=-1: page_name = page_name.replace('č','c⿕')
        if page_name.find('č'.upper()) !=-1: page_name = page_name.replace('č'.upper(),'c⿕')
        if page_name.find('š') !=-1: page_name = page_name.replace('š','s⿕')
        if page_name.find('š'.upper()) !=-1: page_name = page_name.replace('š'.upper(),'s⿕')
        if page_name.find('ž') !=-1: page_name = page_name.replace('ž','z⿕')
        if page_name.find('ž'.upper()) !=-1: page_name = page_name.replace('ž'.upper(),'z⿕')

    elif language_code == 'sv':
        if page_name.find('å') !=-1: page_name = page_name.replace('å','z⿕')
        if page_name.find('å'.upper()) !=-1: page_name = page_name.replace('å'.upper(),'z⿕')
        if page_name.find('ä') !=-1: page_name = page_name.replace('ä','z⿕⿕')
        if page_name.find('ä'.upper()) !=-1: page_name = page_name.replace('ä'.upper(),'z⿕⿕')
        if page_name.find('ö') !=-1: page_name = page_name.replace('ö','z⿕⿕⿕')
        if page_name.find('ö'.upper()) !=-1: page_name = page_name.replace('ö'.upper(),'z⿕⿕⿕')

    elif language_code == 'vi':
        if page_name.find('ả') !=-1: page_name = page_name.replace('ả','a⿕')
        if page_name.find('ả'.upper()) !=-1: page_name = page_name.replace('ả'.upper(),'a')
        if page_name.find('ă') !=-1: page_name = page_name.replace('ă','a⿕')
        if page_name.find('ă'.upper()) !=-1: page_name = page_name.replace('ă'.upper(),'a⿕')
        if page_name.find('ắ') !=-1: page_name = page_name.replace('ắ','a⿕')
        if page_name.find('ắ'.upper()) !=-1: page_name = page_name.replace('ắ'.upper(),'a⿕')
        if page_name.find('ặ') !=-1: page_name = page_name.replace('ặ','a⿕')
        if page_name.find('ặ'.upper()) !=-1: page_name = page_name.replace('ặ'.upper(),'a⿕')
        if page_name.find('ẳ') !=-1: page_name = page_name.replace('ẳ','a⿕')
        if page_name.find('ẳ'.upper()) !=-1: page_name = page_name.replace('ẳ'.upper(),'a⿕')
        if page_name.find('ằ') !=-1: page_name = page_name.replace('ằ','a⿕')
        if page_name.find('ằ'.upper()) !=-1: page_name = page_name.replace('ằ'.upper(),'a⿕')
        if page_name.find('â') !=-1: page_name = page_name.replace('â','a⿕⿕')
        if page_name.find('â'.upper()) !=-1: page_name = page_name.replace('â'.upper(),'a⿕⿕')
        if page_name.find('ầ') !=-1: page_name = page_name.replace('ầ','a⿕⿕')
        if page_name.find('ầ'.upper()) !=-1: page_name = page_name.replace('ầ'.upper(),'a⿕⿕')
        if page_name.find('ậ') !=-1: page_name = page_name.replace('ậ','a⿕⿕')
        if page_name.find('ậ'.upper()) !=-1: page_name = page_name.replace('ậ'.upper(),'a⿕⿕')
        if page_name.find('ấ') !=-1: page_name = page_name.replace('ấ','a⿕⿕')
        if page_name.find('ấ'.upper()) !=-1: page_name = page_name.replace('ấ'.upper(),'a⿕⿕')
        if page_name.find('ẩ') !=-1: page_name = page_name.replace('ẩ','a⿕⿕')
        if page_name.find('ẩ'.upper()) !=-1: page_name = page_name.replace('ẩ'.upper(),'a⿕⿕')
        if page_name.find('đ') !=-1: page_name = page_name.replace('đ','d⿕')
        if page_name.find('đ'.upper()) !=-1: page_name = page_name.replace('đ'.upper(),'d⿕')
        if page_name.find('ẹ') !=-1: page_name = page_name.replace('ẹ','e')
        if page_name.find('ẹ'.upper()) !=-1: page_name = page_name.replace('ẹ'.upper(),'e')
        if page_name.find('ê') !=-1: page_name = page_name.replace('ê','e⿕')
        if page_name.find('ê'.upper()) !=-1: page_name = page_name.replace('ê'.upper(),'e⿕')
        if page_name.find('ệ') !=-1: page_name = page_name.replace('ệ','e⿕')
        if page_name.find('ệ'.upper()) !=-1: page_name = page_name.replace('ệ'.upper(),'e⿕')
        if page_name.find('ễ') !=-1: page_name = page_name.replace('ễ','e⿕')
        if page_name.find('ễ'.upper()) !=-1: page_name = page_name.replace('ễ'.upper(),'e⿕')
        if page_name.find('ề') !=-1: page_name = page_name.replace('ề','e⿕')
        if page_name.find('ề'.upper()) !=-1: page_name = page_name.replace('ề'.upper(),'e⿕')
        if page_name.find('ể') !=-1: page_name = page_name.replace('ể','e⿕')
        if page_name.find('ể'.upper()) !=-1: page_name = page_name.replace('ể'.upper(),'e⿕')
        if page_name.find('ị') !=-1: page_name = page_name.replace('ị','i')
        if page_name.find('ị'.upper()) !=-1: page_name = page_name.replace('ị'.upper(),'i')
        if page_name.find('ì') !=-1: page_name = page_name.replace('ì','i')
        if page_name.find('ì'.upper()) !=-1: page_name = page_name.replace('ì'.upper(),'i')
        if page_name.find('í') !=-1: page_name = page_name.replace('í','i')
        if page_name.find('í'.upper()) !=-1: page_name = page_name.replace('í'.upper(),'i')
        if page_name.find('ỉ') !=-1: page_name = page_name.replace('ỉ','i')
        if page_name.find('ỉ'.upper()) !=-1: page_name = page_name.replace('ỉ'.upper(),'i')
        if page_name.find('î') !=-1: page_name = page_name.replace('î','i')
        if page_name.find('î'.upper()) !=-1: page_name = page_name.replace('î'.upper(),'i')
        if page_name.find('ĩ') !=-1: page_name = page_name.replace('ĩ','i')
        if page_name.find('ĩ'.upper()) !=-1: page_name = page_name.replace('ĩ'.upper(),'i')
        if page_name.find('ọ') !=-1: page_name = page_name.replace('ọ','o')
        if page_name.find('ọ'.upper()) !=-1: page_name = page_name.replace('ọ'.upper(),'o')
        if page_name.find('ỏ') !=-1: page_name = page_name.replace('ỏ','o')
        if page_name.find('ỏ'.upper()) !=-1: page_name = page_name.replace('ỏ'.upper(),'o')
        if page_name.find('ô') !=-1: page_name = page_name.replace('ô','o⿕')
        if page_name.find('ô'.upper()) !=-1: page_name = page_name.replace('ô'.upper(),'o⿕')
        if page_name.find('ơ') !=-1: page_name = page_name.replace('ơ','o⿕⿕')
        if page_name.find('ơ'.upper()) !=-1: page_name = page_name.replace('ơ'.upper(),'o⿕⿕')
        if page_name.find('ộ') !=-1: page_name = page_name.replace('ộ','o⿕')
        if page_name.find('ộ'.upper()) !=-1: page_name = page_name.replace('ộ'.upper(),'o⿕')
        if page_name.find('ố') !=-1: page_name = page_name.replace('ố','o⿕')
        if page_name.find('ố'.upper()) !=-1: page_name = page_name.replace('ố'.upper(),'o⿕')
        if page_name.find('ồ') !=-1: page_name = page_name.replace('ồ','o⿕')
        if page_name.find('ồ'.upper()) !=-1: page_name = page_name.replace('ồ'.upper(),'o⿕')
        if page_name.find('ổ') !=-1: page_name = page_name.replace('ổ','o⿕')
        if page_name.find('ổ'.upper()) !=-1: page_name = page_name.replace('ổ'.upper(),'o⿕')
        if page_name.find('ỗ') !=-1: page_name = page_name.replace('ỗ','o⿕')
        if page_name.find('ỗ'.upper()) !=-1: page_name = page_name.replace('ỗ'.upper(),'o⿕')
        if page_name.find('ỡ') !=-1: page_name = page_name.replace('ỡ','o⿕⿕')
        if page_name.find('ỡ'.upper()) !=-1: page_name = page_name.replace('ỡ'.upper(),'o⿕⿕')
        if page_name.find('ở') !=-1: page_name = page_name.replace('ở','o⿕⿕')
        if page_name.find('ở'.upper()) !=-1: page_name = page_name.replace('ở'.upper(),'o⿕⿕')
        if page_name.find('ớ') !=-1: page_name = page_name.replace('ớ','o⿕⿕')
        if page_name.find('ớ'.upper()) !=-1: page_name = page_name.replace('ớ'.upper(),'o⿕⿕')
        if page_name.find('ờ') !=-1: page_name = page_name.replace('ờ','o⿕⿕')
        if page_name.find('ờ'.upper()) !=-1: page_name = page_name.replace('ờ'.upper(),'o⿕⿕')
        if page_name.find('ụ') !=-1: page_name = page_name.replace('ụ','u')
        if page_name.find('ụ'.upper()) !=-1: page_name = page_name.replace('ụ'.upper(),'u')
        if page_name.find('ủ') !=-1: page_name = page_name.replace('ủ','u')
        if page_name.find('ủ'.upper()) !=-1: page_name = page_name.replace('ủ'.upper(),'u')
        if page_name.find('ư') !=-1: page_name = page_name.replace('ư','u⿕')
        if page_name.find('ư'.upper()) !=-1: page_name = page_name.replace('ư'.upper(),'u⿕')
        if page_name.find('ử') !=-1: page_name = page_name.replace('ử','u⿕')
        if page_name.find('ử'.upper()) !=-1: page_name = page_name.replace('ử'.upper(),'u⿕')
        if page_name.find('ự') !=-1: page_name = page_name.replace('ự','u⿕')
        if page_name.find('ự'.upper()) !=-1: page_name = page_name.replace('ự'.upper(),'u⿕')
        if page_name.find('ừ') !=-1: page_name = page_name.replace('ừ','u⿕')
        if page_name.find('ừ'.upper()) !=-1: page_name = page_name.replace('ừ'.upper(),'u⿕')
        if page_name.find('ữ') !=-1: page_name = page_name.replace('ữ','u⿕')
        if page_name.find('ữ'.upper()) !=-1: page_name = page_name.replace('ữ'.upper(),'u⿕')

    return page_name


def trim(s):
    return s.strip(" \t\n\r\0\x0B")

# TODO : tsolyáni, {{clé de tri|dhu'onikh}}<!-- exception à la règle de la clé de tri car "'" est une lettre à part entière en tsolyáni -->

#!/usr/bin/env python
# coding: utf-8
import html2Unicode

debugLevel = 0
'''TODO: uca-default gère af, am, ar, as, ast, az, be, be-tarask, bg, bn, bn@collation=traditional, bo, br, bs, 
    bs-Cyrl, ca, chr, co, cs, cy, da, de, de-AT@collation=phonebook, dsb, ee, el, en, eo, es, et, eu, fa, fi, 
    fil, fo, fr, fr-CA, fur, fy, ga, gd, gl, gu, ha, haw, he, hi, hr, hsb, hu, hy, id, ig, is, it, ka, kk, kl, 
    km, kn, kok, ku, ky, la, lb, lkt, ln, lo, lt, lv, mk, ml, mn, mo, mr, ms, mt, nb, ne, nl, nn, no, oc, om, 
    or, pa, pl, pt, rm, ro, ru, rup, sco, se, si, sk, sl, smn, sq, sr, sr-Latn, sv, sv@collation=standard, sw, 
    ta, te, th, tk, tl, to, tr, tt, uk, uz, vi, vo, yi, yo, zu
'''
def defaultSort(pageName, encoding = 'uca-default'):
    if debugLevel > 0: print u' defaultSort()'

    pageName = html2Unicode.html2Unicode(pageName)
    word_key = u''
    add_key = False

    for letter in pageName:
        letter_to_treat = False
        if letter in (u'’', u'\''): # u'ʼ' : pb en breton
            add_key = True
        elif letter in (u'\\', u'/', u'×', u'·', u'…', u'-', u'\'', u'.', u',', u'(', u')'):
            word_key += ' '
            add_key = True
        elif encoding != 'uca-default':
            # Latin
            if letter == u'à' or letter == u'Á' or letter == u'á' or letter == u'â' or letter == u'ä' or \
                letter == u'ā' or letter == u'ă' or letter == u'ą' or letter == u'ǎ' or letter == u'ǻ' or \
                letter == u'ȁ' or letter == u'ȃ' or letter == u'ȧ' or letter == u'ɑ' or letter == u'ạ' or \
                letter == u'ả' or letter == u'ấ' or letter == u'Ấ' or letter == u'ⱥ' or letter == u'À' or \
                letter == u'Â' or letter == u'Ä' or letter == u'Å' or letter == u'Ā' or letter == u'Ă' or \
                letter == u'Ą' or letter == u'Ǎ' or letter == u'Ǻ' or letter == u'Ȁ' or letter == u'Ȃ' or \
                letter == u'Ȧ' or letter == u'Ⱥ' or letter == u'Ɑ' or letter == u'Ǟ' or letter == u'Ǡ' or \
                letter == u'ắ' or letter == u'Ắ' or letter == u'å' or letter == u'Å' or letter == u'ã' or \
                letter == u'Ã':
                word_key += "a"
                add_key = True
            elif letter == u'æ' or letter == u'ǣ' or letter == u'ǽ' or letter == u'Æ' or letter == u'Ǣ' or letter == u'Ǽ':
                word_key += "ae"
                add_key = True
            elif letter == u'ƀ' or letter == u'ƃ' or letter == u'Ɓ' or letter == u'Ƃ' or letter == u'Ƀ':
                word_key += "b"
                add_key = True
            elif letter == u'ç' or letter == u'ć' or letter == u'ċ' or letter == u'č' or letter == u'ƈ' or \
                letter == u'ȼ' or letter == u'Ç' or letter == u'Ć' or letter == u'Ĉ' or letter == u'Ċ' or \
                letter == u'Č' or letter == u'Ƈ' or letter == u'Ȼ':
                word_key += "c"
                add_key = True
            elif letter == u'ĉ':
                word_key += "cx"
                add_key = True
            elif letter == u'ď' or letter == u'đ' or letter == u'ƌ' or letter == u'ȡ' or letter == u'Ď' or \
                letter == u'Đ' or letter == u'Ɖ' or letter == u'Ɗ' or letter == u'Ƌ' or letter == u'ȸ' or \
                letter == u'ǆ' or letter == u'ǳ' or letter == u'Ǆ' or letter == u'ǅ' or letter == u'Ǳ' or \
                letter == u'ǲ':
                word_key += "d"
                add_key = True
            elif letter == u'è' or letter == u'È' or letter == u'é' or letter == u'É' or letter == u'ê' or \
                letter == u'Ê' or letter == u'ë' or letter == u'Ë' or letter == u'ē' or letter == u'ĕ' or \
                letter == u'ė' or letter == u'ę' or letter == u'ě' or letter == u'ǝ' or letter == u'ɛ' or \
                letter == u'ȅ' or letter == u'ȇ' or letter == u'ȩ' or letter == u'ɇ' or letter == u'ế' or \
                letter == u'Ế' or letter == u'Ē' or letter == u'Ĕ' or letter == u'Ė' or letter == u'Ę' or \
                letter == u'Ě' or letter == u'Ǝ' or letter == u'Ɛ' or letter == u'Ȅ' or letter == u'Ȇ' or \
                letter == u'Ȩ' or letter == u'Ɇ' or letter == u'ệ' or letter == u'Ệ':
                word_key += "e"
                add_key = True
            elif letter == u'ƒ' or letter == u'Ƒ':
                word_key += "f"
                add_key = True
            elif letter == u'ĝ':
                word_key += "gx"
                add_key = True
            elif letter == u'ğ' or letter == u'ġ' or letter == u'ģ' or letter == u'ǥ' or letter == u'ǧ' or \
                letter == u'ǵ' or letter == u'Ĝ' or letter == u'Ğ' or letter == u'Ġ' or letter == u'Ģ' or \
                letter == u'Ɠ' or letter == u'Ǥ' or letter == u'Ǧ' or letter == u'Ǵ':
                word_key += "g"
                add_key = True
            elif letter == u'ĥ':
                word_key += "hx"
                add_key = True
            elif letter == u'ħ' or letter == u'ȟ' or letter == u'Ĥ' or letter == u'Ħ' or letter == u'Ȟ':
                word_key += "h"
                add_key = True
            elif letter == u'ı' or letter == u'î' or letter == u'ĩ' or letter == u'ī' or letter == u'ĭ' or \
                letter == u'į' or letter == u'ǐ' or letter == u'ȉ' or letter == u'ȋ' or letter == u'Î' or \
                letter == u'Ĩ' or letter == u'Ī' or letter == u'Ĭ' or letter == u'Į' or letter == u'İ' or \
                letter == u'Ɨ' or letter == u'Ǐ' or letter == u'Ȉ' or letter == u'Ȋ' or letter == u'ĳ' or \
                letter == u'Ĳ' or letter == u'ì' or letter == u'Ì' or letter == u'ï' or letter == u'Ï' or \
                letter == u'ǈ' or letter == u'ị' or letter == u'Ị' or letter == u'í' or letter == u'Í':
                word_key += "i"
                add_key = True
            elif letter == u'ĵ':
                word_key += "jx"
                add_key = True
            elif letter == u'ǰ' or letter == u'ȷ' or letter == u'ɉ' or letter == u'Ĵ' or letter == u'Ɉ':
                word_key += "j"
                add_key = True
            elif letter == u'ķ' or letter == u'ƙ' or letter == u'ǩ' or letter == u'Ķ' or letter == u'Ƙ' or letter == u'Ǩ':
                word_key += "k"
                add_key = True
            elif letter == u'ĺ' or letter == u'ļ' or letter == u'ľ' or letter == u'ŀ' or letter == u'ł' or \
                letter == u'ƚ' or letter == u'ȴ' or letter == u'ɫ' or letter == u'Ɫ' or letter == u'Ĺ' or \
                letter == u'Ļ' or letter == u'Ľ' or letter == u'Ŀ' or letter == u'Ł' or letter == u'Ƚ' or \
                letter == u'ǉ' or letter == u'Ǉ':
                word_key += "l"
                add_key = True
            elif letter == u'Ɯ':
                word_key += "m"
                add_key = True
            elif letter == u'ń' or letter == u'ņ' or letter == u'ň' or letter == u'ŋ' or letter == u'ǹ' or \
                letter == u'ƞ' or letter == u'ȵ' or letter == u'Ń' or letter == u'Ņ' or letter == u'Ň' or \
                letter == u'Ŋ' or letter == u'Ɲ' or letter == u'Ǹ' or letter == u'Ƞ' or letter == u'ǌ' or \
                letter == u'Ǌ' or letter == u'ǋ' or letter == u'ɲ' or letter == u'ṉ' or letter == u'Ṉ' or \
                letter == u'ñ' or letter == u'Ñ':
                word_key += "n"
                add_key = True
            elif letter == u'ô' or letter == u'Ô' or letter == u'ø' or letter == u'ō' or letter == u'ŏ' or \
                letter == u'ő' or letter == u'ơ' or letter == u'ǒ' or letter == u'ǫ' or letter == u'ǭ' or \
                letter == u'ǿ' or letter == u'ȍ' or letter == u'ȏ' or letter == u'ȫ' or letter == u'ȭ' or \
                letter == u'ȯ' or letter == u'ȱ' or letter == u'Ø' or letter == u'Ō' or letter == u'Ŏ' or \
                letter == u'Ő' or letter == u'Ɔ' or letter == u'Ɵ' or letter == u'ɵ' or letter == u'Ơ' or \
                letter == u'Ǒ' or letter == u'Ǫ' or letter == u'Ǭ' or letter == u'Ǿ' or letter == u'Ȍ' or \
                letter == u'Ȏ' or letter == u'Ȫ' or letter == u'Ȭ' or letter == u'Ȯ' or letter == u'Ȱ' or \
                letter == u'ɔ' or letter == u'ở' or letter == u'Ở' or letter == u'ợ' or letter == u'Ợ' or \
                letter == u'ò' or letter == u'ó' or letter == u'ö' or letter == u'Ö' or letter == u'õ' or \
                letter == u'Õ':
                word_key += "o"
                add_key = True
            elif letter == u'œ' or letter == u'Œ':
                word_key += "oe"
                add_key = True
            elif letter == u'ƥ' or letter == u'Ƥ':
                word_key += "p"
                add_key = True
            elif letter == u'ɋ' or letter == u'Ɋ' or letter == u'ȹ':
                word_key += "q"
                add_key = True
            elif letter == u'ŕ' or letter == u'ŗ' or letter == u'ř' or letter == u'ȑ' or letter == u'ȓ' or \
                letter == u'ɍ' or letter == u'Ŕ' or letter == u'Ŗ' or letter == u'Ř' or letter == u'Ȑ' or \
                letter == u'Ȓ' or letter == u'Ɍ':
                word_key += "r"
                add_key = True
            elif letter == u'ŝ':
                word_key += "sx"
                add_key = True
            elif letter == u'ſ' or letter == u'ś' or letter == u'ş' or letter == u'š' or letter == u'ƪ' or \
                letter == u'ș' or letter == u'ȿ' or letter == u'Ś' or letter == u'Ŝ' or letter == u'Ş' or \
                letter == u'Š' or letter == u'Ʃ' or letter == u'Ș' or letter == u'ß':
                word_key += "s"
                add_key = True
            elif letter == u'ţ' or letter == u'ť' or letter == u'ŧ' or letter == u'ƫ' or letter == u'ƭ' or \
                letter == u'ț' or letter == u'ȶ' or letter == u'Ţ' or letter == u'Ť' or letter == u'Ŧ' or \
                letter == u'Ƭ' or letter == u'Ʈ' or letter == u'Ț' or letter == u'Ⱦ' or letter == u'ⱦ':
                word_key += "t"
                add_key = True
            elif letter == u'ŭ':
                word_key += "ux"
                add_key = True
            elif letter == u'û' or letter == u'ũ' or letter == u'ū' or letter == u'ů' or letter == u'ű' or \
                letter == u'ų' or letter == u'ư' or letter == u'ǔ' or letter == u'ǖ' or letter == u'ǘ' or \
                letter == u'ǚ' or letter == u'ǜ' or letter == u'ǟ' or letter == u'ǡ' or letter == u'ȕ' or \
                letter == u'ȗ' or letter == u'ʉ' or letter == u'Û' or letter == u'Ũ' or letter == u'Ū' or \
                letter == u'Ŭ' or letter == u'Ů' or letter == u'Ű' or letter == u'Ų' or letter == u'Ư' or \
                letter == u'Ǔ' or letter == u'Ǖ' or letter == u'Ǘ' or letter == u'Ǚ' or letter == u'Ǜ' or \
                letter == u'Ȕ' or letter == u'Ȗ' or letter == u'Ʉ' or letter == u'ủ' or letter == u'Ủ' or \
                letter == u'ú' or letter == u'Ú' or letter == u'ù' or letter == u'Ù' or letter == u'ü' or \
                letter == u'Ü':
                word_key += "u"
                add_key = True
            elif letter == u'ʋ' or letter == u'Ʋ' or letter == u'Ʌ' or letter == u'ʌ':
                word_key += "v"
                add_key = True
            elif letter == u'ŵ' or letter == u'Ŵ':
                word_key += "w"
                add_key = True
            elif letter == u'ŷ' or letter == u'ƴ' or letter == u'ȳ' or letter == u'ɏ' or letter == u'Ŷ' or \
                letter == u'Ÿ' or letter == u'Ƴ' or letter == u'Ȳ' or letter == u'Ɏ':
                word_key += "y"
                add_key = True
            elif letter == u'ź' or letter == u'ż' or letter == u'ž' or letter == u'ƶ' or letter == u'ƹ' or \
                letter == u'ƺ' or letter == u'ǯ' or letter == u'ȥ' or letter == u'ɀ' or letter == u'Ź' or \
                letter == u'Ż' or letter == u'Ž' or letter == u'Ƶ' or letter == u'Ʒ' or letter == u'Ƹ' or \
                letter == u'Ǯ' or letter == u'Ȥ':
                word_key += "z"
                add_key = True

            elif letter == u'A' or letter == u'B' or letter == u'C' or letter == u'D' or letter == u'E' or \
                letter == u'F' or letter == u'G' or letter == u'H' or letter == u'I' or letter == u'J' or \
                letter == u'K' or letter == u'L' or letter == u'M' or letter == u'N' or letter == u'O' or \
                letter == u'P' or letter == u'Q' or letter == u'R' or letter == u'S' or letter == u'T' or \
                letter == u'U' or letter == u'V' or letter == u'W' or letter == u'X' or letter == u'Y' or \
                letter == u'Z':
                word_key += letter.lower()
            else:
                letter_to_treat = True
        else:
          letter_to_treat = True  

        if letter_to_treat:
           word_key += letter

    if add_key:
        return trim(word_key.replace(u'  ', u' '))
    else:
        if debugLevel > 0: raw_input(pageName.encode(config.console_encoding, 'replace'))
        return pageName


def addDefaultSort(pageName, pageContent, empty = False):
    pageContent = pageContent.replace(u'{{DEFAULTSORT:', u'{{clé de tri|')
    pageContent = pageContent.replace(u'{{defaultSort:', u'{{clé de tri|')
    pageContent = pageContent.replace(u'{{clef de tri|', u'{{clé de tri|')
    while pageContent.find(u'\n{clé de tri') != -1:
        pageContent = pageContent[:pageContent.find(u'\n{clé de tri')+1] + u'{' + pageContent[pageContent.find(u'\n{clé de tri'):]

    if empty:
        ClePage = u''
    else:
        ClePage = defaultSort(pageName)

    if pageContent.find(u'{{clé de tri') == -1 and ClePage != u'' and ClePage.lower() != pageName.lower():
            #summary = summary + u', {{clé de tri}} ajoutée'
            if pageContent.rfind(u'\n\n[[') != -1:
                pageContent2 = pageContent[pageContent.rfind(u'\n\n[['):]
                if pageContent2[4:5] == u':' or pageContent2[5:6] == u':':
                    pageContent = pageContent[:pageContent.rfind(u'\n\n[[')] + u'\n\n{{clé de tri|' + ClePage + u'}}' + \
                        pageContent[pageContent.rfind(u'\n\n[['):]
                else:
                    pageContent = pageContent + u'\n\n{{clé de tri|' + ClePage + u'}}\n'
            else:
                pageContent = pageContent + u'\n\n{{clé de tri|' + ClePage + u'}}\n'

    elif pageContent.find(u'{{clé de tri|') != -1 and (pageContent.find(u'{{langue|fr}}') != -1 or \
        pageContent.find(u'{{langue|eo}}') != -1 or pageContent.find(u'{{langue|en}}') != -1 or \
        pageContent.find(u'{{langue|es}}') != -1 or pageContent.find(u'{{langue|de}}') != -1 or \
        pageContent.find(u'{{langue|pt}}') != -1 or pageContent.find(u'{{langue|it}}') != -1):
        if debugLevel > 0: print u' vérification de clé existante pour alphabets connus'
        pageContent2 = pageContent[pageContent.find(u'{{clé de tri|')+len(u'{{clé de tri|'):]
        ClePage = pageContent2[0:pageContent2.find(u'}}')]
        '''if CleTri.lower() != ClePage.lower():
            summary = summary + u', {{clé de tri}} corrigée'
            pageContent = pageContent[:pageContent.find(u'{{clé de tri|')+len(u'{{clé de tri|')] + CleTri + pageContent[pageContent.find(u'{{clé de tri|')+len(u'{{clé de tri|')+pageContent2.find(u'}}'):]'''
        '''pb ʻokina
            if CleTri.lower() == pageName.lower():
            summary = summary + u', {{clé de tri}} supprimée'
            pageContent = pageContent[:pageContent.find(u'{{clé de tri|')] + pageContent[pageContent.find(u'{{clé de tri|')+len(u'{{clé de tri|')+pageContent2.find(u'}}')+2:]'''
    if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

    baratin = u'{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
    if pageContent.find(baratin) != -1:
        pageContent = pageContent[:pageContent.find(baratin)] + pageContent[pageContent.find(baratin)+len(baratin):]
        #summary = summary + u', {{clé de tri|}} supprimée'
    baratin = u'{{clé de tri|}}<!-- Veuillez mettre juste après « {{clé de tri| » le titre de la page en y enlevant tous les accents et éventuels apostrophes, et en changeant les éventuels traits d’union et autres caractères spéciaux par une espace ; s’il n’y a rien à changer, merci d’effacer ces lignes. -->'
    '''Inhibé depuis migration Lua :
    if pageContent.find(baratin) != -1:
        pageContent = pageContent[:pageContent.find(baratin)] + pageContent[pageContent.find(baratin)+len(baratin):]
        summary = summary + u', {{clé de tri|}} supprimée'
    if pageContent.find(u'{{clé de tri|}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{clé de tri|}}')] + pageContent[pageContent.find(u'{{clé de tri|}}')+len(u'{{clé de tri|}}'):]
        summary = summary + u', {{clé de tri|}} supprimée'
    if pageContent.find(u'{{clé de tri}}') != -1:
        pageContent = pageContent[:pageContent.find(u'{{clé de tri}}')] + pageContent[pageContent.find(u'{{clé de tri}}')+len(u'{{clé de tri}}'):]
        summary = summary + u', {{clé de tri}} supprimée'
    if pageContent.find(u'{{clé de tri|' + pageName.lower() + u'}}') != -1 and pageContent.find(u'{{S|verb pronominal|fr}}') == -1:
        pageContent = pageContent[:pageContent.find(u'{{clé de tri|' + pageName.lower() + u'}}')] + pageContent[pageContent.find(u'{{clé de tri|' + pageName.lower() + u'}}')+len(u'{{clé de tri|' + pageName.lower() + u'}}'):]
        summary = summary + u', {{clé de tri}} supprimée'''

    while pageContent.find(u'{{S|verbe pronominal|') != -1:
        # Remplacement de modèle suite à vote
        pageContent2 = pageContent[pageContent.find(u'{{S|verbe pronominal|'):]
        if pageContent2.find(u'{{conj') != -1 and pageContent2.find(u'{{pronominal|') == -1 and pageContent2.find(u'{{pronl|') == -1 and pageContent2.find(u'{{prnl|') == -1 and pageContent2.find(u'{{réflexif|') == -1 and pageContent2.find(u'{{réfléchi|') == -1 and pageContent2.find(u'{{réfl|') == -1:
            pageContent3 = pageContent2[pageContent2.find(u'{{conj'):]
            if pageContent3.find(u'|prnl=') == -1 or pageContent3.find(u'|prnl=') > pageContent3.find(u'}}'):
                pageContent = pageContent[:pageContent.find(u'{{S|verbe pronominal|')] + pageContent2[:pageContent2.find(u'{{conj')] + pageContent3[:pageContent3.find(u'}}')] + u'|prnl=1' + pageContent3[pageContent3.find(u'}}'):]
        pageContent = pageContent[:pageContent.find(u'{{S|verbe pronominal|')] + u'{{S|verbe|' + pageContent[pageContent.find(u'{{S|verbe pronominal|')+len(u'{{S|verbe pronominal|'):]
    while pageContent.find(u'\'\'(pronominal)\'\'') != -1:
        pageContent2 = pageContent[pageContent.find(u'\'\'(pronominal)\'\''):]
        if pageContent2.find(u'|prnl=1') != -1 and pageContent2.find(u'|prnl=1') < pageContent2.find(u'\n'):
            pageContent = pageContent[:pageContent.find(u'\'\'(pronominal)\'\'')] + pageContent[pageContent.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]
        else:
            pageContent = pageContent[:pageContent.find(u'\'\'(pronominal)\'\'')] + u'{{prnl}}' + pageContent[pageContent.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]

    return pageContent

def defaultSortByLanguage(pageName, languageCode):
    if languageCode == u'br':
        if pageName.find(u'cʼh') !=-1: pageName = pageName.replace(u'cʼh',u'c⿕h')
        if pageName.find(u'cʼh'.upper()) !=-1: pageName = pageName.replace(u'cʼh'.upper(),u'c⿕h')

    elif languageCode == u'es':
        if pageName.find(u'ñ') !=-1: pageName = pageName.replace(u'ñ',u'n⿕')
        if pageName.find(u'ñ'.upper()) !=-1: pageName = pageName.replace(u'ñ'.upper(),u'n⿕')

    elif languageCode == u'fi':
        if pageName.find(u'å') !=-1: pageName = pageName.replace(u'å',u'z⿕')
        if pageName.find(u'å'.upper()) !=-1: pageName = pageName.replace(u'å'.upper(),u'z⿕')
        if pageName.find(u'ä') !=-1: pageName = pageName.replace(u'ä',u'z⿕⿕')
        if pageName.find(u'ä'.upper()) !=-1: pageName = pageName.replace(u'ä'.upper(),u'z⿕⿕')
        if pageName.find(u'ö') !=-1: pageName = pageName.replace(u'ö',u'z⿕⿕⿕')
        if pageName.find(u'ö'.upper()) !=-1: pageName = pageName.replace(u'ö'.upper(),u'z⿕⿕⿕')

    elif languageCode == u'os':
        if pageName.find(u'ё') !=-1: pageName = pageName.replace(u'ё',u'е⿕')
        if pageName.find(u'ё'.upper()) !=-1: pageName = pageName.replace(u'ё'.upper(),u'е⿕')
        if pageName.find(u'ӕ') !=-1: pageName = pageName.replace(u'ӕ',u'а⿕')
        if pageName.find(u'ӕ'.upper()) !=-1: pageName = pageName.replace(u'ӕ'.upper(),u'а⿕')
        # Digrammes
        if pageName.find(u'гъ') !=-1: pageName = pageName.replace(u'гъ',u'г⿕')
        if pageName.find(u'дж') !=-1: pageName = pageName.replace(u'дж',u'д⿕')
        if pageName.find(u'дз') !=-1: pageName = pageName.replace(u'дз',u'д⿕⿕')
        if pageName.find(u'къ') !=-1: pageName = pageName.replace(u'къ',u'к⿕')
        if pageName.find(u'пъ') !=-1: pageName = pageName.replace(u'пъ',u'п⿕')
        if pageName.find(u'тъ') !=-1: pageName = pageName.replace(u'тъ',u'т⿕')
        if pageName.find(u'хъ') !=-1: pageName = pageName.replace(u'хъ',u'х⿕')
        if pageName.find(u'цъ') !=-1: pageName = pageName.replace(u'цъ',u'ц⿕')
        if pageName.find(u'чъ') !=-1: pageName = pageName.replace(u'чъ',u'ч⿕')

    elif languageCode == u'ru':
        #if pageName.find(u'ё') !=-1: pageName = pageName.replace(u'ё',u'е⿕')
        #if pageName.find(u'ё'.upper()) !=-1: pageName = pageName.replace(u'ё'.upper(),u'е⿕')
        if pageName.find(u'ӕ') !=-1: pageName = pageName.replace(u'ӕ',u'а⿕')
        if pageName.find(u'ӕ'.upper()) !=-1: pageName = pageName.replace(u'ӕ'.upper(),u'а⿕')

    if languageCode == u'sl':
        if pageName.find(u'č') !=-1: pageName = pageName.replace(u'č',u'c⿕')
        if pageName.find(u'č'.upper()) !=-1: pageName = pageName.replace(u'č'.upper(),u'c⿕')
        if pageName.find(u'š') !=-1: pageName = pageName.replace(u'š',u's⿕')
        if pageName.find(u'š'.upper()) !=-1: pageName = pageName.replace(u'š'.upper(),u's⿕')
        if pageName.find(u'ž') !=-1: pageName = pageName.replace(u'ž',u'z⿕')
        if pageName.find(u'ž'.upper()) !=-1: pageName = pageName.replace(u'ž'.upper(),u'z⿕')

    elif languageCode == u'sv':
        if pageName.find(u'å') !=-1: pageName = pageName.replace(u'å',u'z⿕')
        if pageName.find(u'å'.upper()) !=-1: pageName = pageName.replace(u'å'.upper(),u'z⿕')
        if pageName.find(u'ä') !=-1: pageName = pageName.replace(u'ä',u'z⿕⿕')
        if pageName.find(u'ä'.upper()) !=-1: pageName = pageName.replace(u'ä'.upper(),u'z⿕⿕')
        if pageName.find(u'ö') !=-1: pageName = pageName.replace(u'ö',u'z⿕⿕⿕')
        if pageName.find(u'ö'.upper()) !=-1: pageName = pageName.replace(u'ö'.upper(),u'z⿕⿕⿕')

    elif languageCode == u'vi':
        if pageName.find(u'ả') !=-1: pageName = pageName.replace(u'ả',u'a⿕')
        if pageName.find(u'ả'.upper()) !=-1: pageName = pageName.replace(u'ả'.upper(),u'a')
        if pageName.find(u'ă') !=-1: pageName = pageName.replace(u'ă',u'a⿕')
        if pageName.find(u'ă'.upper()) !=-1: pageName = pageName.replace(u'ă'.upper(),u'a⿕')
        if pageName.find(u'ắ') !=-1: pageName = pageName.replace(u'ắ',u'a⿕')
        if pageName.find(u'ắ'.upper()) !=-1: pageName = pageName.replace(u'ắ'.upper(),u'a⿕')
        if pageName.find(u'ặ') !=-1: pageName = pageName.replace(u'ặ',u'a⿕')
        if pageName.find(u'ặ'.upper()) !=-1: pageName = pageName.replace(u'ặ'.upper(),u'a⿕')
        if pageName.find(u'ẳ') !=-1: pageName = pageName.replace(u'ẳ',u'a⿕')
        if pageName.find(u'ẳ'.upper()) !=-1: pageName = pageName.replace(u'ẳ'.upper(),u'a⿕')
        if pageName.find(u'ằ') !=-1: pageName = pageName.replace(u'ằ',u'a⿕')
        if pageName.find(u'ằ'.upper()) !=-1: pageName = pageName.replace(u'ằ'.upper(),u'a⿕')
        if pageName.find(u'â') !=-1: pageName = pageName.replace(u'â',u'a⿕⿕')
        if pageName.find(u'â'.upper()) !=-1: pageName = pageName.replace(u'â'.upper(),u'a⿕⿕')
        if pageName.find(u'ầ') !=-1: pageName = pageName.replace(u'ầ',u'a⿕⿕')
        if pageName.find(u'ầ'.upper()) !=-1: pageName = pageName.replace(u'ầ'.upper(),u'a⿕⿕')
        if pageName.find(u'ậ') !=-1: pageName = pageName.replace(u'ậ',u'a⿕⿕')
        if pageName.find(u'ậ'.upper()) !=-1: pageName = pageName.replace(u'ậ'.upper(),u'a⿕⿕')
        if pageName.find(u'ấ') !=-1: pageName = pageName.replace(u'ấ',u'a⿕⿕')
        if pageName.find(u'ấ'.upper()) !=-1: pageName = pageName.replace(u'ấ'.upper(),u'a⿕⿕')
        if pageName.find(u'ẩ') !=-1: pageName = pageName.replace(u'ẩ',u'a⿕⿕')
        if pageName.find(u'ẩ'.upper()) !=-1: pageName = pageName.replace(u'ẩ'.upper(),u'a⿕⿕')
        if pageName.find(u'đ') !=-1: pageName = pageName.replace(u'đ',u'd⿕')
        if pageName.find(u'đ'.upper()) !=-1: pageName = pageName.replace(u'đ'.upper(),u'd⿕')
        if pageName.find(u'ẹ') !=-1: pageName = pageName.replace(u'ẹ',u'e')
        if pageName.find(u'ẹ'.upper()) !=-1: pageName = pageName.replace(u'ẹ'.upper(),u'e')
        if pageName.find(u'ê') !=-1: pageName = pageName.replace(u'ê',u'e⿕')
        if pageName.find(u'ê'.upper()) !=-1: pageName = pageName.replace(u'ê'.upper(),u'e⿕')
        if pageName.find(u'ệ') !=-1: pageName = pageName.replace(u'ệ',u'e⿕')
        if pageName.find(u'ệ'.upper()) !=-1: pageName = pageName.replace(u'ệ'.upper(),u'e⿕')
        if pageName.find(u'ễ') !=-1: pageName = pageName.replace(u'ễ',u'e⿕')
        if pageName.find(u'ễ'.upper()) !=-1: pageName = pageName.replace(u'ễ'.upper(),u'e⿕')
        if pageName.find(u'ề') !=-1: pageName = pageName.replace(u'ề',u'e⿕')
        if pageName.find(u'ề'.upper()) !=-1: pageName = pageName.replace(u'ề'.upper(),u'e⿕')
        if pageName.find(u'ể') !=-1: pageName = pageName.replace(u'ể',u'e⿕')
        if pageName.find(u'ể'.upper()) !=-1: pageName = pageName.replace(u'ể'.upper(),u'e⿕')
        if pageName.find(u'ị') !=-1: pageName = pageName.replace(u'ị',u'i')
        if pageName.find(u'ị'.upper()) !=-1: pageName = pageName.replace(u'ị'.upper(),u'i')
        if pageName.find(u'ì') !=-1: pageName = pageName.replace(u'ì',u'i')
        if pageName.find(u'ì'.upper()) !=-1: pageName = pageName.replace(u'ì'.upper(),u'i')
        if pageName.find(u'í') !=-1: pageName = pageName.replace(u'í',u'i')
        if pageName.find(u'í'.upper()) !=-1: pageName = pageName.replace(u'í'.upper(),u'i')
        if pageName.find(u'ỉ') !=-1: pageName = pageName.replace(u'ỉ',u'i')
        if pageName.find(u'ỉ'.upper()) !=-1: pageName = pageName.replace(u'ỉ'.upper(),u'i')
        if pageName.find(u'î') !=-1: pageName = pageName.replace(u'î',u'i')
        if pageName.find(u'î'.upper()) !=-1: pageName = pageName.replace(u'î'.upper(),u'i')
        if pageName.find(u'ĩ') !=-1: pageName = pageName.replace(u'ĩ',u'i')
        if pageName.find(u'ĩ'.upper()) !=-1: pageName = pageName.replace(u'ĩ'.upper(),u'i')
        if pageName.find(u'ọ') !=-1: pageName = pageName.replace(u'ọ',u'o')
        if pageName.find(u'ọ'.upper()) !=-1: pageName = pageName.replace(u'ọ'.upper(),u'o')
        if pageName.find(u'ỏ') !=-1: pageName = pageName.replace(u'ỏ',u'o')
        if pageName.find(u'ỏ'.upper()) !=-1: pageName = pageName.replace(u'ỏ'.upper(),u'o')
        if pageName.find(u'ô') !=-1: pageName = pageName.replace(u'ô',u'o⿕')
        if pageName.find(u'ô'.upper()) !=-1: pageName = pageName.replace(u'ô'.upper(),u'o⿕')
        if pageName.find(u'ơ') !=-1: pageName = pageName.replace(u'ơ',u'o⿕⿕')
        if pageName.find(u'ơ'.upper()) !=-1: pageName = pageName.replace(u'ơ'.upper(),u'o⿕⿕')
        if pageName.find(u'ộ') !=-1: pageName = pageName.replace(u'ộ',u'o⿕')
        if pageName.find(u'ộ'.upper()) !=-1: pageName = pageName.replace(u'ộ'.upper(),u'o⿕')
        if pageName.find(u'ố') !=-1: pageName = pageName.replace(u'ố',u'o⿕')
        if pageName.find(u'ố'.upper()) !=-1: pageName = pageName.replace(u'ố'.upper(),u'o⿕')
        if pageName.find(u'ồ') !=-1: pageName = pageName.replace(u'ồ',u'o⿕')
        if pageName.find(u'ồ'.upper()) !=-1: pageName = pageName.replace(u'ồ'.upper(),u'o⿕')
        if pageName.find(u'ổ') !=-1: pageName = pageName.replace(u'ổ',u'o⿕')
        if pageName.find(u'ổ'.upper()) !=-1: pageName = pageName.replace(u'ổ'.upper(),u'o⿕')
        if pageName.find(u'ỗ') !=-1: pageName = pageName.replace(u'ỗ',u'o⿕')
        if pageName.find(u'ỗ'.upper()) !=-1: pageName = pageName.replace(u'ỗ'.upper(),u'o⿕')
        if pageName.find(u'ỡ') !=-1: pageName = pageName.replace(u'ỡ',u'o⿕⿕')
        if pageName.find(u'ỡ'.upper()) !=-1: pageName = pageName.replace(u'ỡ'.upper(),u'o⿕⿕')
        if pageName.find(u'ở') !=-1: pageName = pageName.replace(u'ở',u'o⿕⿕')
        if pageName.find(u'ở'.upper()) !=-1: pageName = pageName.replace(u'ở'.upper(),u'o⿕⿕')
        if pageName.find(u'ớ') !=-1: pageName = pageName.replace(u'ớ',u'o⿕⿕')
        if pageName.find(u'ớ'.upper()) !=-1: pageName = pageName.replace(u'ớ'.upper(),u'o⿕⿕')
        if pageName.find(u'ờ') !=-1: pageName = pageName.replace(u'ờ',u'o⿕⿕')
        if pageName.find(u'ờ'.upper()) !=-1: pageName = pageName.replace(u'ờ'.upper(),u'o⿕⿕')
        if pageName.find(u'ụ') !=-1: pageName = pageName.replace(u'ụ',u'u')
        if pageName.find(u'ụ'.upper()) !=-1: pageName = pageName.replace(u'ụ'.upper(),u'u')
        if pageName.find(u'ủ') !=-1: pageName = pageName.replace(u'ủ',u'u')
        if pageName.find(u'ủ'.upper()) !=-1: pageName = pageName.replace(u'ủ'.upper(),u'u')
        if pageName.find(u'ư') !=-1: pageName = pageName.replace(u'ư',u'u⿕')
        if pageName.find(u'ư'.upper()) !=-1: pageName = pageName.replace(u'ư'.upper(),u'u⿕')
        if pageName.find(u'ử') !=-1: pageName = pageName.replace(u'ử',u'u⿕')
        if pageName.find(u'ử'.upper()) !=-1: pageName = pageName.replace(u'ử'.upper(),u'u⿕')
        if pageName.find(u'ự') !=-1: pageName = pageName.replace(u'ự',u'u⿕')
        if pageName.find(u'ự'.upper()) !=-1: pageName = pageName.replace(u'ự'.upper(),u'u⿕')
        if pageName.find(u'ừ') !=-1: pageName = pageName.replace(u'ừ',u'u⿕')
        if pageName.find(u'ừ'.upper()) !=-1: pageName = pageName.replace(u'ừ'.upper(),u'u⿕')
        if pageName.find(u'ữ') !=-1: pageName = pageName.replace(u'ữ',u'u⿕')
        if pageName.find(u'ữ'.upper()) !=-1: pageName = pageName.replace(u'ữ'.upper(),u'u⿕')

    return pageName

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

# TODO : tsolyáni, {{clé de tri|dhu'onikh}}<!-- exception à la règle de la clé de tri car "'" est une lettre à part entière en tsolyáni -->

#!/usr/bin/env python
# coding: utf-8
import html2Unicode

def defaultSort(pageName):
	pageName = html2Unicode.html2Unicode(pageName)
	#pageName = pageName.encode(config.console_encoding, 'replace')
	#print pageName
	PageT = u''
	Cle = "false"
	for lettre in range(0, len(pageName)):
		# Latin
		if pageName[lettre:lettre+1] == u'à' or pageName[lettre:lettre+1] == u'Á' or pageName[lettre:lettre+1] == u'á' or pageName[lettre:lettre+1] == u'â' or pageName[lettre:lettre+1] == u'ä' or pageName[lettre:lettre+1] == u'ā' or pageName[lettre:lettre+1] == u'ă' or pageName[lettre:lettre+1] == u'ą' or pageName[lettre:lettre+1] == u'ǎ' or pageName[lettre:lettre+1] == u'ǻ' or pageName[lettre:lettre+1] == u'ȁ' or pageName[lettre:lettre+1] == u'ȃ' or pageName[lettre:lettre+1] == u'ȧ' or pageName[lettre:lettre+1] == u'ɑ' or pageName[lettre:lettre+1] == u'ạ' or pageName[lettre:lettre+1] == u'ả' or pageName[lettre:lettre+1] == u'ấ' or pageName[lettre:lettre+1] == u'Ấ' or pageName[lettre:lettre+1] == u'ⱥ' or pageName[lettre:lettre+1] == u'À' or pageName[lettre:lettre+1] == u'Â' or pageName[lettre:lettre+1] == u'Ä' or pageName[lettre:lettre+1] == u'Å' or pageName[lettre:lettre+1] == u'Ā' or pageName[lettre:lettre+1] == u'Ă' or pageName[lettre:lettre+1] == u'Ą' or pageName[lettre:lettre+1] == u'Ǎ' or pageName[lettre:lettre+1] == u'Ǻ' or pageName[lettre:lettre+1] == u'Ȁ' or pageName[lettre:lettre+1] == u'Ȃ' or pageName[lettre:lettre+1] == u'Ȧ' or pageName[lettre:lettre+1] == u'Ⱥ' or pageName[lettre:lettre+1] == u'Ɑ' or pageName[lettre:lettre+1] == u'Ǟ' or pageName[lettre:lettre+1] == u'Ǡ' or pageName[lettre:lettre+1] == u'ắ' or pageName[lettre:lettre+1] == u'Ắ' or pageName[lettre:lettre+1] == u'å' or pageName[lettre:lettre+1] == u'Å' or pageName[lettre:lettre+1] == u'ã' or pageName[lettre:lettre+1] == u'Ã':
			PageT = PageT + "a"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'æ' or pageName[lettre:lettre+1] == u'ǣ' or pageName[lettre:lettre+1] == u'ǽ' or pageName[lettre:lettre+1] == u'Æ' or pageName[lettre:lettre+1] == u'Ǣ' or pageName[lettre:lettre+1] == u'Ǽ':
			PageT = PageT + "ae"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ƀ' or pageName[lettre:lettre+1] == u'ƃ' or pageName[lettre:lettre+1] == u'Ɓ' or pageName[lettre:lettre+1] == u'Ƃ' or pageName[lettre:lettre+1] == u'Ƀ':
			PageT = PageT + "b"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ç' or pageName[lettre:lettre+1] == u'ć' or pageName[lettre:lettre+1] == u'ċ' or pageName[lettre:lettre+1] == u'č' or pageName[lettre:lettre+1] == u'ƈ' or pageName[lettre:lettre+1] == u'ȼ' or pageName[lettre:lettre+1] == u'Ç' or pageName[lettre:lettre+1] == u'Ć' or pageName[lettre:lettre+1] == u'Ĉ' or pageName[lettre:lettre+1] == u'Ċ' or pageName[lettre:lettre+1] == u'Č' or pageName[lettre:lettre+1] == u'Ƈ' or pageName[lettre:lettre+1] == u'Ȼ':
			PageT = PageT + "c"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ĉ':
			PageT = PageT + "cx"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ď' or pageName[lettre:lettre+1] == u'đ' or pageName[lettre:lettre+1] == u'ƌ' or pageName[lettre:lettre+1] == u'ȡ' or pageName[lettre:lettre+1] == u'Ď' or pageName[lettre:lettre+1] == u'Đ' or pageName[lettre:lettre+1] == u'Ɖ' or pageName[lettre:lettre+1] == u'Ɗ' or pageName[lettre:lettre+1] == u'Ƌ' or pageName[lettre:lettre+1] == u'ȸ' or pageName[lettre:lettre+1] == u'ǆ' or pageName[lettre:lettre+1] == u'ǳ' or pageName[lettre:lettre+1] == u'Ǆ' or pageName[lettre:lettre+1] == u'ǅ' or pageName[lettre:lettre+1] == u'Ǳ' or pageName[lettre:lettre+1] == u'ǲ':
			PageT = PageT + "d"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'è' or pageName[lettre:lettre+1] == u'È' or pageName[lettre:lettre+1] == u'é' or pageName[lettre:lettre+1] == u'É' or pageName[lettre:lettre+1] == u'ê' or pageName[lettre:lettre+1] == u'Ê' or pageName[lettre:lettre+1] == u'ë' or pageName[lettre:lettre+1] == u'Ë' or pageName[lettre:lettre+1] == u'ē' or pageName[lettre:lettre+1] == u'ĕ' or pageName[lettre:lettre+1] == u'ė' or pageName[lettre:lettre+1] == u'ę' or pageName[lettre:lettre+1] == u'ě' or pageName[lettre:lettre+1] == u'ǝ' or pageName[lettre:lettre+1] == u'ɛ' or pageName[lettre:lettre+1] == u'ȅ' or pageName[lettre:lettre+1] == u'ȇ' or pageName[lettre:lettre+1] == u'ȩ' or pageName[lettre:lettre+1] == u'ɇ' or pageName[lettre:lettre+1] == u'ế' or pageName[lettre:lettre+1] == u'Ế' or pageName[lettre:lettre+1] == u'Ē' or pageName[lettre:lettre+1] == u'Ĕ' or pageName[lettre:lettre+1] == u'Ė' or pageName[lettre:lettre+1] == u'Ę' or pageName[lettre:lettre+1] == u'Ě' or pageName[lettre:lettre+1] == u'Ǝ' or pageName[lettre:lettre+1] == u'Ɛ' or pageName[lettre:lettre+1] == u'Ȅ' or pageName[lettre:lettre+1] == u'Ȇ' or pageName[lettre:lettre+1] == u'Ȩ' or pageName[lettre:lettre+1] == u'Ɇ' or pageName[lettre:lettre+1] == u'ệ' or pageName[lettre:lettre+1] == u'Ệ':
			PageT = PageT + "e"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ƒ' or pageName[lettre:lettre+1] == u'Ƒ':
			PageT = PageT + "f"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ĝ':
			PageT = PageT + "gx"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ğ' or pageName[lettre:lettre+1] == u'ġ' or pageName[lettre:lettre+1] == u'ģ' or pageName[lettre:lettre+1] == u'ǥ' or pageName[lettre:lettre+1] == u'ǧ' or pageName[lettre:lettre+1] == u'ǵ' or pageName[lettre:lettre+1] == u'Ĝ' or pageName[lettre:lettre+1] == u'Ğ' or pageName[lettre:lettre+1] == u'Ġ' or pageName[lettre:lettre+1] == u'Ģ' or pageName[lettre:lettre+1] == u'Ɠ' or pageName[lettre:lettre+1] == u'Ǥ' or pageName[lettre:lettre+1] == u'Ǧ' or pageName[lettre:lettre+1] == u'Ǵ':
			PageT = PageT + "g"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ĥ':
			PageT = PageT + "hx"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ħ' or pageName[lettre:lettre+1] == u'ȟ' or pageName[lettre:lettre+1] == u'Ĥ' or pageName[lettre:lettre+1] == u'Ħ' or pageName[lettre:lettre+1] == u'Ȟ':
			PageT = PageT + "h"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ı' or pageName[lettre:lettre+1] == u'î' or pageName[lettre:lettre+1] == u'ĩ' or pageName[lettre:lettre+1] == u'ī' or pageName[lettre:lettre+1] == u'ĭ' or pageName[lettre:lettre+1] == u'į' or pageName[lettre:lettre+1] == u'ǐ' or pageName[lettre:lettre+1] == u'ȉ' or pageName[lettre:lettre+1] == u'ȋ' or pageName[lettre:lettre+1] == u'Î' or pageName[lettre:lettre+1] == u'Ĩ' or pageName[lettre:lettre+1] == u'Ī' or pageName[lettre:lettre+1] == u'Ĭ' or pageName[lettre:lettre+1] == u'Į' or pageName[lettre:lettre+1] == u'İ' or pageName[lettre:lettre+1] == u'Ɨ' or pageName[lettre:lettre+1] == u'Ǐ' or pageName[lettre:lettre+1] == u'Ȉ' or pageName[lettre:lettre+1] == u'Ȋ' or pageName[lettre:lettre+1] == u'ĳ' or pageName[lettre:lettre+1] == u'Ĳ' or pageName[lettre:lettre+1] == u'ì' or pageName[lettre:lettre+1] == u'Ì' or pageName[lettre:lettre+1] == u'ï' or pageName[lettre:lettre+1] == u'Ï' or pageName[lettre:lettre+1] == u'ǈ' or pageName[lettre:lettre+1] == u'ị' or pageName[lettre:lettre+1] == u'Ị' or pageName[lettre:lettre+1] == u'í' or pageName[lettre:lettre+1] == u'Í':
			PageT = PageT + "i"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ĵ':
			PageT = PageT + "jx"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ǰ' or pageName[lettre:lettre+1] == u'ȷ' or pageName[lettre:lettre+1] == u'ɉ' or pageName[lettre:lettre+1] == u'Ĵ' or pageName[lettre:lettre+1] == u'Ɉ':
			PageT = PageT + "j"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ķ' or pageName[lettre:lettre+1] == u'ƙ' or pageName[lettre:lettre+1] == u'ǩ' or pageName[lettre:lettre+1] == u'Ķ' or pageName[lettre:lettre+1] == u'Ƙ' or pageName[lettre:lettre+1] == u'Ǩ':
			PageT = PageT + "k"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ĺ' or pageName[lettre:lettre+1] == u'ļ' or pageName[lettre:lettre+1] == u'ľ' or pageName[lettre:lettre+1] == u'ŀ' or pageName[lettre:lettre+1] == u'ł' or pageName[lettre:lettre+1] == u'ƚ' or pageName[lettre:lettre+1] == u'ȴ' or pageName[lettre:lettre+1] == u'ɫ' or pageName[lettre:lettre+1] == u'Ɫ' or pageName[lettre:lettre+1] == u'Ĺ' or pageName[lettre:lettre+1] == u'Ļ' or pageName[lettre:lettre+1] == u'Ľ' or pageName[lettre:lettre+1] == u'Ŀ' or pageName[lettre:lettre+1] == u'Ł' or pageName[lettre:lettre+1] == u'Ƚ' or pageName[lettre:lettre+1] == u'ǉ' or pageName[lettre:lettre+1] == u'Ǉ':
			PageT = PageT + "l"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ɯ':
			PageT = PageT + "m"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ń' or pageName[lettre:lettre+1] == u'ņ' or pageName[lettre:lettre+1] == u'ň' or pageName[lettre:lettre+1] == u'ŋ' or pageName[lettre:lettre+1] == u'ǹ' or pageName[lettre:lettre+1] == u'ƞ' or pageName[lettre:lettre+1] == u'ȵ' or pageName[lettre:lettre+1] == u'Ń' or pageName[lettre:lettre+1] == u'Ņ' or pageName[lettre:lettre+1] == u'Ň' or pageName[lettre:lettre+1] == u'Ŋ' or pageName[lettre:lettre+1] == u'Ɲ' or pageName[lettre:lettre+1] == u'Ǹ' or pageName[lettre:lettre+1] == u'Ƞ' or pageName[lettre:lettre+1] == u'ǌ' or pageName[lettre:lettre+1] == u'Ǌ' or pageName[lettre:lettre+1] == u'ǋ' or pageName[lettre:lettre+1] == u'ɲ' or pageName[lettre:lettre+1] == u'ṉ' or pageName[lettre:lettre+1] == u'Ṉ' or pageName[lettre:lettre+1] == u'ñ' or pageName[lettre:lettre+1] == u'Ñ':
			PageT = PageT + "n"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ô' or pageName[lettre:lettre+1] == u'Ô' or pageName[lettre:lettre+1] == u'ø' or pageName[lettre:lettre+1] == u'ō' or pageName[lettre:lettre+1] == u'ŏ' or pageName[lettre:lettre+1] == u'ő' or pageName[lettre:lettre+1] == u'ơ' or pageName[lettre:lettre+1] == u'ǒ' or pageName[lettre:lettre+1] == u'ǫ' or pageName[lettre:lettre+1] == u'ǭ' or pageName[lettre:lettre+1] == u'ǿ' or pageName[lettre:lettre+1] == u'ȍ' or pageName[lettre:lettre+1] == u'ȏ' or pageName[lettre:lettre+1] == u'ȫ' or pageName[lettre:lettre+1] == u'ȭ' or pageName[lettre:lettre+1] == u'ȯ' or pageName[lettre:lettre+1] == u'ȱ' or pageName[lettre:lettre+1] == u'Ø' or pageName[lettre:lettre+1] == u'Ō' or pageName[lettre:lettre+1] == u'Ŏ' or pageName[lettre:lettre+1] == u'Ő' or pageName[lettre:lettre+1] == u'Ɔ' or pageName[lettre:lettre+1] == u'Ɵ' or pageName[lettre:lettre+1] == u'ɵ' or pageName[lettre:lettre+1] == u'Ơ' or pageName[lettre:lettre+1] == u'Ǒ' or pageName[lettre:lettre+1] == u'Ǫ' or pageName[lettre:lettre+1] == u'Ǭ' or pageName[lettre:lettre+1] == u'Ǿ' or pageName[lettre:lettre+1] == u'Ȍ' or pageName[lettre:lettre+1] == u'Ȏ' or pageName[lettre:lettre+1] == u'Ȫ' or pageName[lettre:lettre+1] == u'Ȭ' or pageName[lettre:lettre+1] == u'Ȯ' or pageName[lettre:lettre+1] == u'Ȱ' or pageName[lettre:lettre+1] == u'ɔ' or pageName[lettre:lettre+1] == u'ở' or pageName[lettre:lettre+1] == u'Ở' or pageName[lettre:lettre+1] == u'ợ' or pageName[lettre:lettre+1] == u'Ợ' or pageName[lettre:lettre+1] == u'ò' or pageName[lettre:lettre+1] == u'ó' or pageName[lettre:lettre+1] == u'ö' or pageName[lettre:lettre+1] == u'Ö' or pageName[lettre:lettre+1] == u'õ' or pageName[lettre:lettre+1] == u'Õ':
			PageT = PageT + "o"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'œ' or pageName[lettre:lettre+1] == u'Œ':
			PageT = PageT + "oe"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ƥ' or pageName[lettre:lettre+1] == u'Ƥ':
			PageT = PageT + "p"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ɋ' or pageName[lettre:lettre+1] == u'Ɋ' or pageName[lettre:lettre+1] == u'ȹ':
			PageT = PageT + "q"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ŕ' or pageName[lettre:lettre+1] == u'ŗ' or pageName[lettre:lettre+1] == u'ř' or pageName[lettre:lettre+1] == u'ȑ' or pageName[lettre:lettre+1] == u'ȓ' or pageName[lettre:lettre+1] == u'ɍ' or pageName[lettre:lettre+1] == u'Ŕ' or pageName[lettre:lettre+1] == u'Ŗ' or pageName[lettre:lettre+1] == u'Ř' or pageName[lettre:lettre+1] == u'Ȑ' or pageName[lettre:lettre+1] == u'Ȓ' or pageName[lettre:lettre+1] == u'Ɍ':
			PageT = PageT + "r"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ŝ':
			PageT = PageT + "sx"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ſ' or pageName[lettre:lettre+1] == u'ś' or pageName[lettre:lettre+1] == u'ş' or pageName[lettre:lettre+1] == u'š' or pageName[lettre:lettre+1] == u'ƪ' or pageName[lettre:lettre+1] == u'ș' or pageName[lettre:lettre+1] == u'ȿ' or pageName[lettre:lettre+1] == u'Ś' or pageName[lettre:lettre+1] == u'Ŝ' or pageName[lettre:lettre+1] == u'Ş' or pageName[lettre:lettre+1] == u'Š' or pageName[lettre:lettre+1] == u'Ʃ' or pageName[lettre:lettre+1] == u'Ș' or pageName[lettre:lettre+1] == u'ß':
			PageT = PageT + "s"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ţ' or pageName[lettre:lettre+1] == u'ť' or pageName[lettre:lettre+1] == u'ŧ' or pageName[lettre:lettre+1] == u'ƫ' or pageName[lettre:lettre+1] == u'ƭ' or pageName[lettre:lettre+1] == u'ț' or pageName[lettre:lettre+1] == u'ȶ' or pageName[lettre:lettre+1] == u'Ţ' or pageName[lettre:lettre+1] == u'Ť' or pageName[lettre:lettre+1] == u'Ŧ' or pageName[lettre:lettre+1] == u'Ƭ' or pageName[lettre:lettre+1] == u'Ʈ' or pageName[lettre:lettre+1] == u'Ț' or pageName[lettre:lettre+1] == u'Ⱦ' or pageName[lettre:lettre+1] == u'ⱦ':
			PageT = PageT + "t"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ŭ':
			PageT = PageT + "ux"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'û' or pageName[lettre:lettre+1] == u'ũ' or pageName[lettre:lettre+1] == u'ū' or pageName[lettre:lettre+1] == u'ů' or pageName[lettre:lettre+1] == u'ű' or pageName[lettre:lettre+1] == u'ų' or pageName[lettre:lettre+1] == u'ư' or pageName[lettre:lettre+1] == u'ǔ' or pageName[lettre:lettre+1] == u'ǖ' or pageName[lettre:lettre+1] == u'ǘ' or pageName[lettre:lettre+1] == u'ǚ' or pageName[lettre:lettre+1] == u'ǜ' or pageName[lettre:lettre+1] == u'ǟ' or pageName[lettre:lettre+1] == u'ǡ' or pageName[lettre:lettre+1] == u'ȕ' or pageName[lettre:lettre+1] == u'ȗ' or pageName[lettre:lettre+1] == u'ʉ' or pageName[lettre:lettre+1] == u'Û' or pageName[lettre:lettre+1] == u'Ũ' or pageName[lettre:lettre+1] == u'Ū' or pageName[lettre:lettre+1] == u'Ŭ' or pageName[lettre:lettre+1] == u'Ů' or pageName[lettre:lettre+1] == u'Ű' or pageName[lettre:lettre+1] == u'Ų' or pageName[lettre:lettre+1] == u'Ư' or pageName[lettre:lettre+1] == u'Ǔ' or pageName[lettre:lettre+1] == u'Ǖ' or pageName[lettre:lettre+1] == u'Ǘ' or pageName[lettre:lettre+1] == u'Ǚ' or pageName[lettre:lettre+1] == u'Ǜ' or pageName[lettre:lettre+1] == u'Ȕ' or pageName[lettre:lettre+1] == u'Ȗ' or pageName[lettre:lettre+1] == u'Ʉ' or pageName[lettre:lettre+1] == u'ủ' or pageName[lettre:lettre+1] == u'Ủ' or pageName[lettre:lettre+1] == u'ú' or pageName[lettre:lettre+1] == u'Ú' or pageName[lettre:lettre+1] == u'ù' or pageName[lettre:lettre+1] == u'Ù' or pageName[lettre:lettre+1] == u'ü' or pageName[lettre:lettre+1] == u'Ü':
			PageT = PageT + "u"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ʋ' or pageName[lettre:lettre+1] == u'Ʋ' or pageName[lettre:lettre+1] == u'Ʌ' or pageName[lettre:lettre+1] == u'ʌ':
			PageT = PageT + "v"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ŵ' or pageName[lettre:lettre+1] == u'Ŵ':
			PageT = PageT + "w"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ŷ' or pageName[lettre:lettre+1] == u'ƴ' or pageName[lettre:lettre+1] == u'ȳ' or pageName[lettre:lettre+1] == u'ɏ' or pageName[lettre:lettre+1] == u'Ŷ' or pageName[lettre:lettre+1] == u'Ÿ' or pageName[lettre:lettre+1] == u'Ƴ' or pageName[lettre:lettre+1] == u'Ȳ' or pageName[lettre:lettre+1] == u'Ɏ':
			PageT = PageT + "y"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ź' or pageName[lettre:lettre+1] == u'ż' or pageName[lettre:lettre+1] == u'ž' or pageName[lettre:lettre+1] == u'ƶ' or pageName[lettre:lettre+1] == u'ƹ' or pageName[lettre:lettre+1] == u'ƺ' or pageName[lettre:lettre+1] == u'ǯ' or pageName[lettre:lettre+1] == u'ȥ' or pageName[lettre:lettre+1] == u'ɀ' or pageName[lettre:lettre+1] == u'Ź' or pageName[lettre:lettre+1] == u'Ż' or pageName[lettre:lettre+1] == u'Ž' or pageName[lettre:lettre+1] == u'Ƶ' or pageName[lettre:lettre+1] == u'Ʒ' or pageName[lettre:lettre+1] == u'Ƹ' or pageName[lettre:lettre+1] == u'Ǯ' or pageName[lettre:lettre+1] == u'Ȥ':
			PageT = PageT + "z"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'’' or pageName[lettre:lettre+1] == u'\'':	# pb en breton pour : or pageName[lettre:lettre+1] == u'ʼ'
			PageT = PageT + ""
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'\\' or pageName[lettre:lettre+1] == u'/' or pageName[lettre:lettre+1] == u'×' or pageName[lettre:lettre+1] == u'·' or pageName[lettre:lettre+1] == u'...' or pageName[lettre:lettre+1] == u'-' or pageName[lettre:lettre+1] == u'\'' or pageName[lettre:lettre+1] == u'.' or pageName[lettre:lettre+1] == u',' or pageName[lettre:lettre+1] == u'(' or pageName[lettre:lettre+1] == u')':
			PageT = PageT + " "
			Cle = "yes"
			'''
		# Grec
		elif pageName[lettre:lettre+1] == u'α' or pageName[lettre:lettre+1] == u'Ἀ' or pageName[lettre:lettre+1] == u'ἀ' or pageName[lettre:lettre+1] == u'Ἁ' or pageName[lettre:lettre+1] == u'ἁ' or pageName[lettre:lettre+1] == u'Ἂ' or pageName[lettre:lettre+1] == u'ἂ' or pageName[lettre:lettre+1] == u'Ἃ' or pageName[lettre:lettre+1] == u'ἃ' or pageName[lettre:lettre+1] == u'Ἄ' or pageName[lettre:lettre+1] == u'ἄ' or pageName[lettre:lettre+1] == u'Ἅ' or pageName[lettre:lettre+1] == u'ἅ' or pageName[lettre:lettre+1] == u'Ἆ' or pageName[lettre:lettre+1] == u'ἆ' or pageName[lettre:lettre+1] == u'Ἇ' or pageName[lettre:lettre+1] == u'ἇ' or pageName[lettre:lettre+1] == u'Ὰ' or pageName[lettre:lettre+1] == u'ὰ' or pageName[lettre:lettre+1] == u'Ά' or pageName[lettre:lettre+1] == u'ά' or pageName[lettre:lettre+1] == u'ᾈ' or pageName[lettre:lettre+1] == u'ᾀ' or pageName[lettre:lettre+1] == u'ᾉ' or pageName[lettre:lettre+1] == u'ᾁ' or pageName[lettre:lettre+1] == u'ᾊ' or pageName[lettre:lettre+1] == u'ᾂ' or pageName[lettre:lettre+1] == u'ᾋ' or pageName[lettre:lettre+1] == u'ᾃ' or pageName[lettre:lettre+1] == u'ᾌ' or pageName[lettre:lettre+1] == u'ᾄ' or pageName[lettre:lettre+1] == u'ᾍ' or pageName[lettre:lettre+1] == u'ᾅ' or pageName[lettre:lettre+1] == u'ᾎ' or pageName[lettre:lettre+1] == u'ᾆ' or pageName[lettre:lettre+1] == u'ᾏ' or pageName[lettre:lettre+1] == u'ᾇ' or pageName[lettre:lettre+1] == u'Ᾰ' or pageName[lettre:lettre+1] == u'ᾰ' or pageName[lettre:lettre+1] == u'Ᾱ' or pageName[lettre:lettre+1] == u'ᾱ' or pageName[lettre:lettre+1] == u'ᾼ' or pageName[lettre:lettre+1] == u'ᾳ' or pageName[lettre:lettre+1] == u'Ὰ' or pageName[lettre:lettre+1] == u'ᾲ' or pageName[lettre:lettre+1] == u'Ά' or pageName[lettre:lettre+1] == u'ᾴ' or pageName[lettre:lettre+1] == u'Ȃ' or pageName[lettre:lettre+1] == u'ᾶ' or pageName[lettre:lettre+1] == u'Ȃ' or pageName[lettre:lettre+1] == u'ᾷ':
			PageT = PageT + "α"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ἐ' or pageName[lettre:lettre+1] == u'ἐ' or pageName[lettre:lettre+1] == u'Ἑ' or pageName[lettre:lettre+1] == u'ἑ' or pageName[lettre:lettre+1] == u'Ἒ' or pageName[lettre:lettre+1] == u'ἒ' or pageName[lettre:lettre+1] == u'Ἓ' or pageName[lettre:lettre+1] == u'ἓ' or pageName[lettre:lettre+1] == u'Ἔ' or pageName[lettre:lettre+1] == u'ἔ' or pageName[lettre:lettre+1] == u'Ἕ' or pageName[lettre:lettre+1] == u'ἕ' or pageName[lettre:lettre+1] == u'Ὲ' or pageName[lettre:lettre+1] == u'ὲ' or pageName[lettre:lettre+1] == u'Έ' or pageName[lettre:lettre+1] == u'έ':
			PageT = PageT + "ε"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ἠ' or pageName[lettre:lettre+1] == u'ἠ' or pageName[lettre:lettre+1] == u'Ἡ' or pageName[lettre:lettre+1] == u'ἡ' or pageName[lettre:lettre+1] == u'Ἢ' or pageName[lettre:lettre+1] == u'ἢ' or pageName[lettre:lettre+1] == u'Ἣ' or pageName[lettre:lettre+1] == u'ἣ' or pageName[lettre:lettre+1] == u'Ἤ' or pageName[lettre:lettre+1] == u'ἤ' or pageName[lettre:lettre+1] == u'Ἥ' or pageName[lettre:lettre+1] == u'ἥ' or pageName[lettre:lettre+1] == u'Ἦ' or pageName[lettre:lettre+1] == u'ἦ' or pageName[lettre:lettre+1] == u'Ἧ' or pageName[lettre:lettre+1] == u'ἧ' or pageName[lettre:lettre+1] == u'ᾘ' or pageName[lettre:lettre+1] == u'ᾐ' or pageName[lettre:lettre+1] == u'ᾙ' or pageName[lettre:lettre+1] == u'ᾑ' or pageName[lettre:lettre+1] == u'ᾚ' or pageName[lettre:lettre+1] == u'ᾒ' or pageName[lettre:lettre+1] == u'ᾛ' or pageName[lettre:lettre+1] == u'ᾓ' or pageName[lettre:lettre+1] == u'ᾜ' or pageName[lettre:lettre+1] == u'ᾔ' or pageName[lettre:lettre+1] == u'ᾝ' or pageName[lettre:lettre+1] == u'ᾕ' or pageName[lettre:lettre+1] == u'ᾞ' or pageName[lettre:lettre+1] == u'ᾖ' or pageName[lettre:lettre+1] == u'ᾟ' or pageName[lettre:lettre+1] == u'ᾗ' or pageName[lettre:lettre+1] == u'Ὴ' or pageName[lettre:lettre+1] == u'ὴ' or pageName[lettre:lettre+1] == u'Ή' or pageName[lettre:lettre+1] == u'ή' or pageName[lettre:lettre+1] == u'ῌ' or pageName[lettre:lettre+1] == u'ῂ' or pageName[lettre:lettre+1] == u'Η' or pageName[lettre:lettre+1] == u'ῃ' or pageName[lettre:lettre+1] == u'Ή' or pageName[lettre:lettre+1] == u'ῄ' or pageName[lettre:lettre+1] == u'ῌ' or pageName[lettre:lettre+1] == u'ῆ' or pageName[lettre:lettre+1] == u'ῌ' or pageName[lettre:lettre+1] == u'ῇ':
			PageT = PageT + "η"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ὶ' or pageName[lettre:lettre+1] == u'ὶ' or pageName[lettre:lettre+1] == u'Ί' or pageName[lettre:lettre+1] == u'ί' or pageName[lettre:lettre+1] == u'Ί' or pageName[lettre:lettre+1] == u'ί' or pageName[lettre:lettre+1] == u'Ῐ' or pageName[lettre:lettre+1] == u'ῐ' or pageName[lettre:lettre+1] == u'Ῑ' or pageName[lettre:lettre+1] == u'ῑ' or pageName[lettre:lettre+1] == u'Ἰ' or pageName[lettre:lettre+1] == u'ἰ' or pageName[lettre:lettre+1] == u'Ἱ' or pageName[lettre:lettre+1] == u'ἱ' or pageName[lettre:lettre+1] == u'Ἲ' or pageName[lettre:lettre+1] == u'ἲ' or pageName[lettre:lettre+1] == u'Ἳ' or pageName[lettre:lettre+1] == u'ἳ' or pageName[lettre:lettre+1] == u'Ἴ' or pageName[lettre:lettre+1] == u'ἴ' or pageName[lettre:lettre+1] == u'Ἵ' or pageName[lettre:lettre+1] == u'ἵ' or pageName[lettre:lettre+1] == u'Ἶ' or pageName[lettre:lettre+1] == u'ἶ' or pageName[lettre:lettre+1] == u'Ἷ' or pageName[lettre:lettre+1] == u'ἷ' or pageName[lettre:lettre+1] == u'ΐ' or pageName[lettre:lettre+1] == u'ῖ' or pageName[lettre:lettre+1] == u'ῗ' or pageName[lettre:lettre+1] == u'ῒ':
			PageT = PageT + "ι"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ὀ' or pageName[lettre:lettre+1] == u'ὀ' or pageName[lettre:lettre+1] == u'Ὁ' or pageName[lettre:lettre+1] == u'ὁ' or pageName[lettre:lettre+1] == u'Ὂ' or pageName[lettre:lettre+1] == u'ὂ' or pageName[lettre:lettre+1] == u'Ὃ' or pageName[lettre:lettre+1] == u'ὃ' or pageName[lettre:lettre+1] == u'Ὄ' or pageName[lettre:lettre+1] == u'ὄ' or pageName[lettre:lettre+1] == u'Ὅ' or pageName[lettre:lettre+1] == u'ὅ' or pageName[lettre:lettre+1] == u'Ὸ' or pageName[lettre:lettre+1] == u'ὸ' or pageName[lettre:lettre+1] == u'Ό' or pageName[lettre:lettre+1] == u'ό':
			PageT = PageT + "ο"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ὠ' or pageName[lettre:lettre+1] == u'ὠ' or pageName[lettre:lettre+1] == u'Ὡ' or pageName[lettre:lettre+1] == u'ὡ' or pageName[lettre:lettre+1] == u'Ὢ' or pageName[lettre:lettre+1] == u'ὢ' or pageName[lettre:lettre+1] == u'Ὣ' or pageName[lettre:lettre+1] == u'ὣ' or pageName[lettre:lettre+1] == u'Ὤ' or pageName[lettre:lettre+1] == u'ὤ' or pageName[lettre:lettre+1] == u'Ὥ' or pageName[lettre:lettre+1] == u'ὥ' or pageName[lettre:lettre+1] == u'Ὦ' or pageName[lettre:lettre+1] == u'ὦ' or pageName[lettre:lettre+1] == u'Ὧ' or pageName[lettre:lettre+1] == u'ὧ' or pageName[lettre:lettre+1] == u'Ὼ' or pageName[lettre:lettre+1] == u'ὼ' or pageName[lettre:lettre+1] == u'Ώ' or pageName[lettre:lettre+1] == u'ώ' or pageName[lettre:lettre+1] == u'ᾨ' or pageName[lettre:lettre+1] == u'ᾠ' or pageName[lettre:lettre+1] == u'ᾩ' or pageName[lettre:lettre+1] == u'ᾡ' or pageName[lettre:lettre+1] == u'ᾪ' or pageName[lettre:lettre+1] == u'ᾢ' or pageName[lettre:lettre+1] == u'ᾫ' or pageName[lettre:lettre+1] == u'ᾣ' or pageName[lettre:lettre+1] == u'ᾬ' or pageName[lettre:lettre+1] == u'ᾤ' or pageName[lettre:lettre+1] == u'ᾭ' or pageName[lettre:lettre+1] == u'ᾥ' or pageName[lettre:lettre+1] == u'ᾮ' or pageName[lettre:lettre+1] == u'ᾦ' or pageName[lettre:lettre+1] == u'ᾯ' or pageName[lettre:lettre+1] == u'ᾧ' or pageName[lettre:lettre+1] == u'ῼ' or pageName[lettre:lettre+1] == u'ῳ' or pageName[lettre:lettre+1] == u'ῲ' or pageName[lettre:lettre+1] == u'ῴ' or pageName[lettre:lettre+1] == u'ῶ' or pageName[lettre:lettre+1] == u'ῷ':
			PageT = PageT + "ω"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ὓ' or pageName[lettre:lettre+1] == u'ὓ' or pageName[lettre:lettre+1] == u'Υ' or pageName[lettre:lettre+1] == u'ὔ' or pageName[lettre:lettre+1] == u'Ὕ' or pageName[lettre:lettre+1] == u'ὕ' or pageName[lettre:lettre+1] == u'Ὗ' or pageName[lettre:lettre+1] == u'ὗ' or pageName[lettre:lettre+1] == u'Ὺ' or pageName[lettre:lettre+1] == u'ὺ' or pageName[lettre:lettre+1] == u'Ύ' or pageName[lettre:lettre+1] == u'ύ' or pageName[lettre:lettre+1] == u'Ῠ' or pageName[lettre:lettre+1] == u'ῠ' or pageName[lettre:lettre+1] == u'Ῡ' or pageName[lettre:lettre+1] == u'ῡ' or pageName[lettre:lettre+1] == u'ῢ' or pageName[lettre:lettre+1] == u'ΰ' or pageName[lettre:lettre+1] == u'ῦ' or pageName[lettre:lettre+1] == u'ῧ' or pageName[lettre:lettre+1] == u'ὐ' or pageName[lettre:lettre+1] == u'ὑ' or pageName[lettre:lettre+1] == u'ὒ' or pageName[lettre:lettre+1] == u'ὖ':
			PageT = PageT + "υ"
			Cle = "yes"
		# Cyrillique
		elif pageName[lettre:lettre+1] == u'ѐ' or pageName[lettre:lettre+1] == u'Ѐ' or pageName[lettre:lettre+1] == u'ё' or pageName[lettre:lettre+1] == u'Ё':
			PageT = PageT + u'е'
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ѝ' or pageName[lettre:lettre+1] == u'й' or pageName[lettre:lettre+1] == u'И' or pageName[lettre:lettre+1] == u'Ѝ' or pageName[lettre:lettre+1] == u'Й':
			PageT = PageT + "и"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ў' or pageName[lettre:lettre+1] == u'У' or pageName[lettre:lettre+1] == u'Ў':
			PageT = PageT + "у"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ѓ' or pageName[lettre:lettre+1] == u'ґ' or pageName[lettre:lettre+1] == u'Г' or pageName[lettre:lettre+1] == u'Ѓ' or pageName[lettre:lettre+1] == u'Ґ':
			PageT = PageT + "г"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ќ' or pageName[lettre:lettre+1] == u'К' or pageName[lettre:lettre+1] == u'Ќ':
			PageT = PageT + "к"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ї' or pageName[lettre:lettre+1] == u'І' or pageName[lettre:lettre+1] == u'Ї':
			PageT = PageT + "і"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ѿ':
			PageT = PageT + "Ѡ"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'Ѵ' or pageName[lettre:lettre+1] == u'ѷ' or pageName[lettre:lettre+1] == u'Ѷ':
			PageT = PageT + "ѵ"
			Cle = "yes"
		# Arabe
		elif pageName[lettre:lettre+1] == u'أ' or pageName[lettre:lettre+1] == u'إ' or pageName[lettre:lettre+1] == u'آ' or pageName[lettre:lettre+1] == u'ٱ':
			PageT = PageT + "ا"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'دَ' or pageName[lettre:lettre+1] == u'دِ' or pageName[lettre:lettre+1] == u'دُ':
			PageT = PageT + "ﺩ"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'ذٰ':
			PageT = PageT + "ﺫ"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'لٰ':
			PageT = PageT + "ﻝ"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'مٰ':
			PageT = PageT + "ﻡ"
			Cle = "yes"
		elif pageName[lettre:lettre+1] == u'هٰ':
			PageT = PageT + "ﻩ"
			Cle = "yes"'''
		
		elif pageName[lettre:lettre+1] == u'A' or pageName[lettre:lettre+1] == u'B' or pageName[lettre:lettre+1] == u'C' or pageName[lettre:lettre+1] == u'D' or pageName[lettre:lettre+1] == u'E' or pageName[lettre:lettre+1] == u'F' or pageName[lettre:lettre+1] == u'G' or pageName[lettre:lettre+1] == u'H' or pageName[lettre:lettre+1] == u'I' or pageName[lettre:lettre+1] == u'J' or pageName[lettre:lettre+1] == u'K' or pageName[lettre:lettre+1] == u'L' or pageName[lettre:lettre+1] == u'M' or pageName[lettre:lettre+1] == u'N' or pageName[lettre:lettre+1] == u'O' or pageName[lettre:lettre+1] == u'P' or pageName[lettre:lettre+1] == u'Q' or pageName[lettre:lettre+1] == u'R' or pageName[lettre:lettre+1] == u'S' or pageName[lettre:lettre+1] == u'T' or pageName[lettre:lettre+1] == u'U' or pageName[lettre:lettre+1] == u'V' or pageName[lettre:lettre+1] == u'W' or pageName[lettre:lettre+1] == u'X' or pageName[lettre:lettre+1] == u'Y' or pageName[lettre:lettre+1] == u'Z':
			PageT = PageT + pageName[lettre:lettre+1].lower()
		else:
			PageT = PageT + pageName[lettre:lettre+1]
		#print (PageT)
		#raw_input("lettre")
		#print Cle
	if Cle == "yes":
		#while PageT[0:1] == u' ': PageT = PageT[1:len(PageT)]
		return trim(PageT)
	else:
		#raw_input(pageName.encode(config.console_encoding, 'replace'))
		return pageName


def addDefaultSort(PageTemp):
    PageTemp = PageTemp.replace(u'{{DEFAULTSORT:', u'{{clé de tri|')
    PageTemp = PageTemp.replace(u'{{defaultSort:', u'{{clé de tri|')
    PageTemp = PageTemp.replace(u'{{clef de tri|', u'{{clé de tri|')
    while PageTemp.find(u'\n{clé de tri') != -1:
        PageTemp = PageTemp[:PageTemp.find(u'\n{clé de tri')+1] + u'{' + PageTemp[PageTemp.find(u'\n{clé de tri'):len(PageTemp)]

    ClePage = CleTri
    if PageTemp.find(u'{{clé de tri') == -1 and ClePage != u'' and ClePage.lower() != pageName.lower():
            summary = summary + u', {{clé de tri}} ajoutée'
            if PageTemp.rfind(u'\n\n[[') != -1:
                PageTemp2 = PageTemp[PageTemp.rfind(u'\n\n[['):len(PageTemp)]
                if PageTemp2[4:5] == u':' or PageTemp2[5:6] == u':':
                    PageTemp = PageTemp[:PageTemp.rfind(u'\n\n[[')] + u'\n\n{{clé de tri|' + ClePage + u'}}' + PageTemp[PageTemp.rfind(u'\n\n[['):len(PageTemp)]
                else:
                    PageTemp = PageTemp + u'\n\n{{clé de tri|' + ClePage + u'}}\n'
            else:
                PageTemp = PageTemp + u'\n\n{{clé de tri|' + ClePage + u'}}\n'

    elif PageTemp.find(u'{{clé de tri|') != -1 and (PageTemp.find(u'{{langue|fr}}') != -1 or PageTemp.find(u'{{langue|eo}}') != -1 or PageTemp.find(u'{{langue|en}}') != -1 or PageTemp.find(u'{{langue|es}}') != -1 or PageTemp.find(u'{{langue|de}}') != -1 or PageTemp.find(u'{{langue|pt}}') != -1 or PageTemp.find(u'{{langue|it}}') != -1):
        if debugLevel > 0: print u' vérification de clé existante pour alphabets connus'
        PageTemp2 = PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|'):len(PageTemp)]
        ClePage = PageTemp2[0:PageTemp2.find(u'}}')]
        '''if CleTri.lower() != ClePage.lower():
            summary = summary + u', {{clé de tri}} corrigée'
            PageTemp = PageTemp[:PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')] + CleTri + PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')+PageTemp2.find(u'}}'):len(PageTemp)]'''
        '''pb ʻokina
            if CleTri.lower() == pageName.lower():
            summary = summary + u', {{clé de tri}} supprimée'
            PageTemp = PageTemp[:PageTemp.find(u'{{clé de tri|')] + PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')+PageTemp2.find(u'}}')+2:len(PageTemp)]'''
    if debugLevel > 1: raw_input(PageTemp.encode(config.console_encoding, 'replace'))

    baratin = u'{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
    if PageTemp.find(baratin) != -1:
        PageTemp = PageTemp[:PageTemp.find(baratin)] + PageTemp[PageTemp.find(baratin)+len(baratin):len(PageTemp)]
        summary = summary + u', {{clé de tri|}} supprimée'
    baratin = u'{{clé de tri|}}<!-- Veuillez mettre juste après « {{clé de tri| » le titre de la page en y enlevant tous les accents et éventuels apostrophes, et en changeant les éventuels traits d’union et autres caractères spéciaux par une espace ; s’il n’y a rien à changer, merci d’effacer ces lignes. -->'
    '''Inhibé depuis migration Lua :
    if PageTemp.find(baratin) != -1:
        PageTemp = PageTemp[:PageTemp.find(baratin)] + PageTemp[PageTemp.find(baratin)+len(baratin):len(PageTemp)]
        summary = summary + u', {{clé de tri|}} supprimée'
    if PageTemp.find(u'{{clé de tri|}}') != -1:
        PageTemp = PageTemp[:PageTemp.find(u'{{clé de tri|}}')] + PageTemp[PageTemp.find(u'{{clé de tri|}}')+len(u'{{clé de tri|}}'):len(PageTemp)]
        summary = summary + u', {{clé de tri|}} supprimée'
    if PageTemp.find(u'{{clé de tri}}') != -1:
        PageTemp = PageTemp[:PageTemp.find(u'{{clé de tri}}')] + PageTemp[PageTemp.find(u'{{clé de tri}}')+len(u'{{clé de tri}}'):len(PageTemp)]
        summary = summary + u', {{clé de tri}} supprimée'
    if PageTemp.find(u'{{clé de tri|' + pageName.lower() + u'}}') != -1 and PageTemp.find(u'{{S|verb pronominal|fr}}') == -1:
        PageTemp = PageTemp[:PageTemp.find(u'{{clé de tri|' + pageName.lower() + u'}}')] + PageTemp[PageTemp.find(u'{{clé de tri|' + pageName.lower() + u'}}')+len(u'{{clé de tri|' + pageName.lower() + u'}}'):len(PageTemp)]
        summary = summary + u', {{clé de tri}} supprimée'''
    while PageTemp.find(u'{{S|verbe pronominal|') != -1:
        # Remplacement de modèle suite à vote
        PageTemp2 = PageTemp[PageTemp.find(u'{{S|verbe pronominal|'):]
        if PageTemp2.find(u'{{conj') != -1 and PageTemp2.find(u'{{pronominal|') == -1 and PageTemp2.find(u'{{pronl|') == -1 and PageTemp2.find(u'{{prnl|') == -1 and PageTemp2.find(u'{{réflexif|') == -1 and PageTemp2.find(u'{{réfléchi|') == -1 and PageTemp2.find(u'{{réfl|') == -1:
            PageTemp3 = PageTemp2[PageTemp2.find(u'{{conj'):]
            if PageTemp3.find(u'|prnl=') == -1 or PageTemp3.find(u'|prnl=') > PageTemp3.find(u'}}'):
                PageTemp = PageTemp[:PageTemp.find(u'{{S|verbe pronominal|')] + PageTemp2[:PageTemp2.find(u'{{conj')] + PageTemp3[:PageTemp3.find(u'}}')] + u'|prnl=1' + PageTemp3[PageTemp3.find(u'}}'):]
        PageTemp = PageTemp[:PageTemp.find(u'{{S|verbe pronominal|')] + u'{{S|verbe|' + PageTemp[PageTemp.find(u'{{S|verbe pronominal|')+len(u'{{S|verbe pronominal|'):]
    while PageTemp.find(u'\'\'(pronominal)\'\'') != -1:
        PageTemp2 = PageTemp[PageTemp.find(u'\'\'(pronominal)\'\''):]
        if PageTemp2.find(u'|prnl=1') != -1 and PageTemp2.find(u'|prnl=1') < PageTemp2.find(u'\n'):
            PageTemp = PageTemp[:PageTemp.find(u'\'\'(pronominal)\'\'')] + PageTemp[PageTemp.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]
        else:
            PageTemp = PageTemp[:PageTemp.find(u'\'\'(pronominal)\'\'')] + u'{{prnl}}' + PageTemp[PageTemp.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]


def defaultSortByLanguage(pageName, languageCode):
    if languageCode == u'br':
        if pageName.find(u'cʼh') !=-1: pageName = pageName.replace(u'cʼh',u'c€h')
        if pageName.find(u'cʼh'.upper()) !=-1: pageName = pageName.replace(u'cʼh'.upper(),u'c€h')

    elif languageCode == u'es':
        if pageName.find(u'ñ') !=-1: pageName = pageName.replace(u'ñ',u'n€')
        if pageName.find(u'ñ'.upper()) !=-1: pageName = pageName.replace(u'ñ'.upper(),u'n€')

    elif languageCode == u'fi':
        if pageName.find(u'å') !=-1: pageName = pageName.replace(u'å',u'z€')
        if pageName.find(u'å'.upper()) !=-1: pageName = pageName.replace(u'å'.upper(),u'z€')
        if pageName.find(u'ä') !=-1: pageName = pageName.replace(u'ä',u'z€€')
        if pageName.find(u'ä'.upper()) !=-1: pageName = pageName.replace(u'ä'.upper(),u'z€€')
        if pageName.find(u'ö') !=-1: pageName = pageName.replace(u'ö',u'z€€€')
        if pageName.find(u'ö'.upper()) !=-1: pageName = pageName.replace(u'ö'.upper(),u'z€€€')

    elif languageCode == u'os':
        if pageName.find(u'ё') !=-1: pageName = pageName.replace(u'ё',u'е€')
        if pageName.find(u'ё'.upper()) !=-1: pageName = pageName.replace(u'ё'.upper(),u'е€')
        if pageName.find(u'ӕ') !=-1: pageName = pageName.replace(u'ӕ',u'а€')
        if pageName.find(u'ӕ'.upper()) !=-1: pageName = pageName.replace(u'ӕ'.upper(),u'а€')
        # Digrammes
        if pageName.find(u'гъ') !=-1: pageName = pageName.replace(u'гъ',u'г€')
        if pageName.find(u'дж') !=-1: pageName = pageName.replace(u'дж',u'д€')
        if pageName.find(u'дз') !=-1: pageName = pageName.replace(u'дз',u'д€€')
        if pageName.find(u'къ') !=-1: pageName = pageName.replace(u'къ',u'к€')
        if pageName.find(u'пъ') !=-1: pageName = pageName.replace(u'пъ',u'п€')
        if pageName.find(u'тъ') !=-1: pageName = pageName.replace(u'тъ',u'т€')
        if pageName.find(u'хъ') !=-1: pageName = pageName.replace(u'хъ',u'х€')
        if pageName.find(u'цъ') !=-1: pageName = pageName.replace(u'цъ',u'ц€')
        if pageName.find(u'чъ') !=-1: pageName = pageName.replace(u'чъ',u'ч€')

    elif languageCode == u'ru':
        #if pageName.find(u'ё') !=-1: pageName = pageName.replace(u'ё',u'е€')
        #if pageName.find(u'ё'.upper()) !=-1: pageName = pageName.replace(u'ё'.upper(),u'е€')
        if pageName.find(u'ӕ') !=-1: pageName = pageName.replace(u'ӕ',u'а€')
        if pageName.find(u'ӕ'.upper()) !=-1: pageName = pageName.replace(u'ӕ'.upper(),u'а€')

    if languageCode == u'sl':
        if pageName.find(u'č') !=-1: pageName = pageName.replace(u'č',u'c€')
        if pageName.find(u'č'.upper()) !=-1: pageName = pageName.replace(u'č'.upper(),u'c€')
        if pageName.find(u'š') !=-1: pageName = pageName.replace(u'š',u's€')
        if pageName.find(u'š'.upper()) !=-1: pageName = pageName.replace(u'š'.upper(),u's€')
        if pageName.find(u'ž') !=-1: pageName = pageName.replace(u'ž',u'z€')
        if pageName.find(u'ž'.upper()) !=-1: pageName = pageName.replace(u'ž'.upper(),u'z€')

    elif languageCode == u'sv':
        if pageName.find(u'å') !=-1: pageName = pageName.replace(u'å',u'z€')
        if pageName.find(u'å'.upper()) !=-1: pageName = pageName.replace(u'å'.upper(),u'z€')
        if pageName.find(u'ä') !=-1: pageName = pageName.replace(u'ä',u'z€€')
        if pageName.find(u'ä'.upper()) !=-1: pageName = pageName.replace(u'ä'.upper(),u'z€€')
        if pageName.find(u'ö') !=-1: pageName = pageName.replace(u'ö',u'z€€€')
        if pageName.find(u'ö'.upper()) !=-1: pageName = pageName.replace(u'ö'.upper(),u'z€€€')

    elif languageCode == u'vi':
        if pageName.find(u'ả') !=-1: pageName = pageName.replace(u'ả',u'a€')
        if pageName.find(u'ả'.upper()) !=-1: pageName = pageName.replace(u'ả'.upper(),u'a')
        if pageName.find(u'ă') !=-1: pageName = pageName.replace(u'ă',u'a€')
        if pageName.find(u'ă'.upper()) !=-1: pageName = pageName.replace(u'ă'.upper(),u'a€')
        if pageName.find(u'ắ') !=-1: pageName = pageName.replace(u'ắ',u'a€')
        if pageName.find(u'ắ'.upper()) !=-1: pageName = pageName.replace(u'ắ'.upper(),u'a€')
        if pageName.find(u'ặ') !=-1: pageName = pageName.replace(u'ặ',u'a€')
        if pageName.find(u'ặ'.upper()) !=-1: pageName = pageName.replace(u'ặ'.upper(),u'a€')
        if pageName.find(u'ẳ') !=-1: pageName = pageName.replace(u'ẳ',u'a€')
        if pageName.find(u'ẳ'.upper()) !=-1: pageName = pageName.replace(u'ẳ'.upper(),u'a€')
        if pageName.find(u'ằ') !=-1: pageName = pageName.replace(u'ằ',u'a€')
        if pageName.find(u'ằ'.upper()) !=-1: pageName = pageName.replace(u'ằ'.upper(),u'a€')
        if pageName.find(u'â') !=-1: pageName = pageName.replace(u'â',u'a€€')
        if pageName.find(u'â'.upper()) !=-1: pageName = pageName.replace(u'â'.upper(),u'a€€')
        if pageName.find(u'ầ') !=-1: pageName = pageName.replace(u'ầ',u'a€€')
        if pageName.find(u'ầ'.upper()) !=-1: pageName = pageName.replace(u'ầ'.upper(),u'a€€')
        if pageName.find(u'ậ') !=-1: pageName = pageName.replace(u'ậ',u'a€€')
        if pageName.find(u'ậ'.upper()) !=-1: pageName = pageName.replace(u'ậ'.upper(),u'a€€')
        if pageName.find(u'ấ') !=-1: pageName = pageName.replace(u'ấ',u'a€€')
        if pageName.find(u'ấ'.upper()) !=-1: pageName = pageName.replace(u'ấ'.upper(),u'a€€')
        if pageName.find(u'ẩ') !=-1: pageName = pageName.replace(u'ẩ',u'a€€')
        if pageName.find(u'ẩ'.upper()) !=-1: pageName = pageName.replace(u'ẩ'.upper(),u'a€€')
        if pageName.find(u'đ') !=-1: pageName = pageName.replace(u'đ',u'd€')
        if pageName.find(u'đ'.upper()) !=-1: pageName = pageName.replace(u'đ'.upper(),u'd€')
        if pageName.find(u'ẹ') !=-1: pageName = pageName.replace(u'ẹ',u'e')
        if pageName.find(u'ẹ'.upper()) !=-1: pageName = pageName.replace(u'ẹ'.upper(),u'e')
        if pageName.find(u'ê') !=-1: pageName = pageName.replace(u'ê',u'e€')
        if pageName.find(u'ê'.upper()) !=-1: pageName = pageName.replace(u'ê'.upper(),u'e€')
        if pageName.find(u'ệ') !=-1: pageName = pageName.replace(u'ệ',u'e€')
        if pageName.find(u'ệ'.upper()) !=-1: pageName = pageName.replace(u'ệ'.upper(),u'e€')
        if pageName.find(u'ễ') !=-1: pageName = pageName.replace(u'ễ',u'e€')
        if pageName.find(u'ễ'.upper()) !=-1: pageName = pageName.replace(u'ễ'.upper(),u'e€')
        if pageName.find(u'ề') !=-1: pageName = pageName.replace(u'ề',u'e€')
        if pageName.find(u'ề'.upper()) !=-1: pageName = pageName.replace(u'ề'.upper(),u'e€')
        if pageName.find(u'ể') !=-1: pageName = pageName.replace(u'ể',u'e€')
        if pageName.find(u'ể'.upper()) !=-1: pageName = pageName.replace(u'ể'.upper(),u'e€')
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
        if pageName.find(u'ô') !=-1: pageName = pageName.replace(u'ô',u'o€')
        if pageName.find(u'ô'.upper()) !=-1: pageName = pageName.replace(u'ô'.upper(),u'o€')
        if pageName.find(u'ơ') !=-1: pageName = pageName.replace(u'ơ',u'o€€')
        if pageName.find(u'ơ'.upper()) !=-1: pageName = pageName.replace(u'ơ'.upper(),u'o€€')
        if pageName.find(u'ộ') !=-1: pageName = pageName.replace(u'ộ',u'o€')
        if pageName.find(u'ộ'.upper()) !=-1: pageName = pageName.replace(u'ộ'.upper(),u'o€')
        if pageName.find(u'ố') !=-1: pageName = pageName.replace(u'ố',u'o€')
        if pageName.find(u'ố'.upper()) !=-1: pageName = pageName.replace(u'ố'.upper(),u'o€')
        if pageName.find(u'ồ') !=-1: pageName = pageName.replace(u'ồ',u'o€')
        if pageName.find(u'ồ'.upper()) !=-1: pageName = pageName.replace(u'ồ'.upper(),u'o€')
        if pageName.find(u'ổ') !=-1: pageName = pageName.replace(u'ổ',u'o€')
        if pageName.find(u'ổ'.upper()) !=-1: pageName = pageName.replace(u'ổ'.upper(),u'o€')
        if pageName.find(u'ỗ') !=-1: pageName = pageName.replace(u'ỗ',u'o€')
        if pageName.find(u'ỗ'.upper()) !=-1: pageName = pageName.replace(u'ỗ'.upper(),u'o€')
        if pageName.find(u'ỡ') !=-1: pageName = pageName.replace(u'ỡ',u'o€€')
        if pageName.find(u'ỡ'.upper()) !=-1: pageName = pageName.replace(u'ỡ'.upper(),u'o€€')
        if pageName.find(u'ở') !=-1: pageName = pageName.replace(u'ở',u'o€€')
        if pageName.find(u'ở'.upper()) !=-1: pageName = pageName.replace(u'ở'.upper(),u'o€€')
        if pageName.find(u'ớ') !=-1: pageName = pageName.replace(u'ớ',u'o€€')
        if pageName.find(u'ớ'.upper()) !=-1: pageName = pageName.replace(u'ớ'.upper(),u'o€€')
        if pageName.find(u'ờ') !=-1: pageName = pageName.replace(u'ờ',u'o€€')
        if pageName.find(u'ờ'.upper()) !=-1: pageName = pageName.replace(u'ờ'.upper(),u'o€€')
        if pageName.find(u'ụ') !=-1: pageName = pageName.replace(u'ụ',u'u')
        if pageName.find(u'ụ'.upper()) !=-1: pageName = pageName.replace(u'ụ'.upper(),u'u')
        if pageName.find(u'ủ') !=-1: pageName = pageName.replace(u'ủ',u'u')
        if pageName.find(u'ủ'.upper()) !=-1: pageName = pageName.replace(u'ủ'.upper(),u'u')
        if pageName.find(u'ư') !=-1: pageName = pageName.replace(u'ư',u'u€')
        if pageName.find(u'ư'.upper()) !=-1: pageName = pageName.replace(u'ư'.upper(),u'u€')
        if pageName.find(u'ử') !=-1: pageName = pageName.replace(u'ử',u'u€')
        if pageName.find(u'ử'.upper()) !=-1: pageName = pageName.replace(u'ử'.upper(),u'u€')
        if pageName.find(u'ự') !=-1: pageName = pageName.replace(u'ự',u'u€')
        if pageName.find(u'ự'.upper()) !=-1: pageName = pageName.replace(u'ự'.upper(),u'u€')
        if pageName.find(u'ừ') !=-1: pageName = pageName.replace(u'ừ',u'u€')
        if pageName.find(u'ừ'.upper()) !=-1: pageName = pageName.replace(u'ừ'.upper(),u'u€')
        if pageName.find(u'ữ') !=-1: pageName = pageName.replace(u'ữ',u'u€')
        if pageName.find(u'ữ'.upper()) !=-1: pageName = pageName.replace(u'ữ'.upper(),u'u€')

    return pageName

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

# TODO : tsolyáni, {{clé de tri|dhu'onikh}}<!-- exception à la règle de la clé de tri car "'" est une lettre à part entière en tsolyáni -->

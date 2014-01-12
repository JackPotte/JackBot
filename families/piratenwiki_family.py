# -*- coding: utf-8  -*-
__version__ = '$Id$'

import family

#  German Pirate Party Wiki
#  http://www.piratenwiki.de/
#  http://wiki.piratenpartei.de/

class Family(family.Family):

   def __init__(self):
       family.Family.__init__(self)
       self.name = "piratenwiki"
       self.langs = {
           "de": "wiki.piratenpartei.de",
       }
       self.namespaces[1] =  { "_default": u"Diskussion" }
       self.namespaces[2] =  { "_default": u"Benutzer" }
       self.namespaces[3] =  { "_default": u"Benutzer Diskussion" }
       self.namespaces[4] =  { "_default": u"Piratenwiki" }
       self.namespaces[5] =  { "_default": u"Piratenwiki Diskussion" }
       self.namespaces[6] =  { "_default": u"Datei" }
       self.namespaces[7] =  { "_default": u"Datei Diskussion" }

       self.namespaces[8] =  { "_default": u"MediaWiki" }
       self.namespaces[9] =  { "_default": u"MediaWiki Diskussion" }
       self.namespaces[10] =  { "_default": u"Vorlage" }
       self.namespaces[11] =  { "_default": u"Vorlage Diskussion" }
       self.namespaces[12] =  { "_default": u"Hilfe" }
       self.namespaces[13] =  { "_default": u"Hilfe Diskussion" }

       self.namespaces[14] =  { "_default": u"Kategorie" }
       self.namespaces[15] =  { "_default": u"Kategorie Diskussion" }
       self.namespaces[100] =  { "_default": u"Skin" }
       self.namespaces[101] =  { "_default": u"Skin talk" }
       self.namespaces[102] =  { "_default": u"Filler" }
       self.namespaces[103] =  { "_default": u"Filler talk" }

       self.namespaces[108] =  { "_default": u"LaTeX" }
       self.namespaces[109] =  { "_default": u"LaTeX Diskussion" }
       self.namespaces[110] =  { "_default": u"Fair2.0" }
       self.namespaces[111] =  { "_default": u"Fair2.0 Diskussion" }
       self.namespaces[112] =  { "_default": u"Orga" }
       self.namespaces[113] =  { "_default": u"Orga Diskussion" }

       self.namespaces[114] =  { "_default": u"Presse" }
       self.namespaces[115] =  { "_default": u"Presse Diskussion" }
       self.namespaces[116] =  { "_default": u"Termine" }
       self.namespaces[117] =  { "_default": u"Termine Diskussion" }
       self.namespaces[118] =  { "_default": u"Jupis" }
       self.namespaces[119] =  { "_default": u"Jupis Diskussion" }
       self.namespaces[120] =  { "_default": u"BW-Web" }
       self.namespaces[121] =  { "_default": u"BW-Web Diskussion" }
       self.namespaces[122] =  { "_default": u"BY-Web" }
       self.namespaces[123] =  { "_default": u"BY-Web Diskussion" }

       self.namespaces[124] =  { "_default": u"B-Web" }
       self.namespaces[125] =  { "_default": u"B-Web Diskussion" }
       self.namespaces[126] =  { "_default": u"BB-Web" }
       self.namespaces[127] =  { "_default": u"BB-Web Diskussion" }
       self.namespaces[128] =  { "_default": u"HB-Web" }
       self.namespaces[129] =  { "_default": u"HB-Web Diskussion" }
       self.namespaces[130] =  { "_default": u"HH-Web" }
       self.namespaces[131] =  { "_default": u"HH-Web Diskussion" }
       self.namespaces[132] =  { "_default": u"HE-Web" }
       self.namespaces[133] =  { "_default": u"HE-Web Diskussion" }
       self.namespaces[134] =  { "_default": u"MV-Web" }
       self.namespaces[135] =  { "_default": u"MV-Web Diskussion" }
       self.namespaces[136] =  { "_default": u"NDS-Web" }
       self.namespaces[137] =  { "_default": u"NDS-Web Diskussion" }
       self.namespaces[138] =  { "_default": u"NRW-Web" }
       self.namespaces[139] =  { "_default": u"NRW-Web Diskussion" }
       self.namespaces[140] =  { "_default": u"RP-Web" }
       self.namespaces[141] =  { "_default": u"RP-Web Diskussion" }
       self.namespaces[142] =  { "_default": u"SL-Web" }
       self.namespaces[143] =  { "_default": u"SL-Web Diskussion" }
       self.namespaces[144] =  { "_default": u"SN-Web" }
       self.namespaces[145] =  { "_default": u"SN-Web Diskussion" }
       self.namespaces[146] =  { "_default": u"SA-Web" }
       self.namespaces[147] =  { "_default": u"SA-Web Diskussion" }
       self.namespaces[148] =  { "_default": u"SH-Web" }
       self.namespaces[149] =  { "_default": u"SH-Web Diskussion" }
       self.namespaces[150] =  { "_default": u"TH-Web" }
       self.namespaces[151] =  { "_default": u"TH-Web Diskussion" }
       self.namespaces[220] =  { "_default": u"BW" }
       self.namespaces[221] =  { "_default": u"BW Diskussion" }
       self.namespaces[222] =  { "_default": u"BY" }
       self.namespaces[223] =  { "_default": u"BY Diskussion" }
       self.namespaces[224] =  { "_default": u"BE" }
       self.namespaces[225] =  { "_default": u"BE Diskussion" }
       self.namespaces[226] =  { "_default": u"BB" }
       self.namespaces[227] =  { "_default": u"BB Diskussion" }
       self.namespaces[228] =  { "_default": u"HB" }
       self.namespaces[229] =  { "_default": u"HB Diskussion" }
       self.namespaces[230] =  { "_default": u"HH" }
       self.namespaces[231] =  { "_default": u"HH Diskussion" }
       self.namespaces[232] =  { "_default": u"HE" }
       self.namespaces[233] =  { "_default": u"HE Diskussion" }
       self.namespaces[234] =  { "_default": u"MV" }
       self.namespaces[235] =  { "_default": u"MV Diskussion" }
       self.namespaces[236] =  { "_default": u"NDS" }
       self.namespaces[237] =  { "_default": u"NDS Diskussion" }
       self.namespaces[238] =  { "_default": u"NRW" }
       self.namespaces[239] =  { "_default": u"NRW Diskussion" }
       self.namespaces[240] =  { "_default": u"RP" }
       self.namespaces[241] =  { "_default": u"RP Diskussion" }
       self.namespaces[242] =  { "_default": u"SL" }
       self.namespaces[243] =  { "_default": u"SL Diskussion" }
       self.namespaces[244] =  { "_default": u"Sachsen" }
       self.namespaces[245] =  { "_default": u"Sachsen Diskussion" }
       self.namespaces[246] =  { "_default": u"SA" }
       self.namespaces[247] =  { "_default": u"SA Diskussion" }
       self.namespaces[248] =  { "_default": u"SH" }
       self.namespaces[249] =  { "_default": u"SH Diskussion" }
       self.namespaces[250] =  { "_default": u"TH" }
       self.namespaces[251] =  { "_default": u"TH Diskussion" }

       self.namespaces[252] =  { "_default": u"Crew" }
       self.namespaces[253] =  { "_default": u"Crew Diskussion" }
       self.namespaces[254] =  { "_default": u"Archiv" }
       self.namespaces[255] =  { "_default": u"Archiv Diskussion" }
       self.namespaces[256] =  { "_default": u"HSG" }
       self.namespaces[257] =  { "_default": u"HSG Diskussion" }
       self.namespaces[258] =  { "_default": u"HSG-Intern" }
       self.namespaces[259] =  { "_default": u"HSG-Intern Diskussion" }
       self.namespaces[260] =  { "_default": u"Finanzen" }
       self.namespaces[261] =  { "_default": u"Finanzen Diskussion" }
       self.namespaces[262] =  { "_default": u"Antrag" }
       self.namespaces[263] =  { "_default": u"Antrag Diskussion" }
       self.namespaces[302] =  { "_default": u"Attribut" }
       self.namespaces[303] =  { "_default": u"Attribut Diskussion" }
       self.namespaces[304] =  { "_default": u"Datentyp" }
       self.namespaces[305] =  { "_default": u"Datentyp Diskussion" }
       self.namespaces[306] =  { "_default": u"Formular" }
       self.namespaces[307] =  { "_default": u"Formular Diskussion" }
       self.namespaces[308] =  { "_default": u"Konzept" }
       self.namespaces[309] =  { "_default": u"Konzept Diskussion" }

   def scriptpath(self, code):
       # Yes, it needs to be /wiki/ not /wiki
       # because URLs are in the form
       # http://<server>/wiki//index.php?action=XXX
       return "/wiki/"

   def nicepath(self, code):
       return ""

   def version(self, code):
       return "1.16.0"

   if family.config.SSL_connection:
       def protocol(self, code):
           return "https"

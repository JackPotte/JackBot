#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for wikipedia.py"""

# This test script is intended to be used with mature unittest code.
#
# This script contains important unittests in order to ensure the function
# and stability of core code (for e.g. DrTrigonBot framework) and methods.
# You should not change code here except you want to add a new test case
# for a function, mechanism or else.

__version__ = '$Id$'

import unittest
import test_pywiki

import sys

import wikipedia as pywikibot


# a set of hard pages for Page.getSections()
PAGE_SET_Page_getSections = [
u'Benutzer Diskussion:Reiner Stoppok/Dachboden',
u'Wikipedia:Löschkandidaten/12. Dezember 2009',     # https://bugzilla.wikimedia.org/show_bug.cgi?id=32753
u'Wikipedia:Löschkandidaten/28. Juli 2006',
u'Wikipedia Diskussion:Persönliche Bekanntschaften/Archiv/2008',
u'Wikipedia:WikiProjekt München',                   # bugzilla:32753
u'Wikipedia Diskussion:Hauptseite',
u'Diskussion:Selbstkühlendes Bierfass',
u'Benutzer Diskussion:P.Copp',
u'Benutzer Diskussion:David Ludwig',
u'Diskussion:Zufall',
u'Benutzer Diskussion:Dekator',
u'Benutzer Diskussion:Bautsch',
u'Benutzer Diskussion:Henbeu',
u'Benutzer Diskussion:Olaf Studt',
u'Diskussion:K.-o.-Tropfen',
u'Portal Diskussion:Fußball/Archiv6',
u'Benutzer Diskussion:Roland.M/Archiv2006-2007',
u'Benutzer Diskussion:Tigerente/Archiv2006',
u'Wikipedia:WikiProjekt Bremen/Beobachtungsliste',  # bugzilla:32753
u'Diskussion:Wirtschaft Chiles',
u'Benutzer Diskussion:Ausgangskontrolle',
u'Benutzer Diskussion:Amnesty.tina',
#u'Diskussion:Chicagoer Schule',                    # [ DELETED ]
#u'Wikipedia Diskussion:Hausaufgabenhilfe',         # [ DELETED ]
u'Benutzer Diskussion:Niemot',
u'Benutzer Diskussion:Computer356',
u'Benutzer Diskussion:Bautsch',
u'Benutzer Diskussion:Infinite Monkey',
u'Benutzer Diskussion:Lsjm',
u'Benutzer Diskussion:Eduardo79',
u'Benutzer Diskussion:Rigidmc',
u'Benutzer Diskussion:Gilgamesch2010',
u'Benutzer Diskussion:Paulusschinew',
u'Benutzer Diskussion:Hollister71',
u'Benutzer Diskussion:Schott-PR',
u'Benutzer Diskussion:RoBoVsKi',
#u'Benutzer Diskussion:Tjaraaa',                    # [ REDIRECTED ]
u'Benutzer Diskussion:Jason Hits',
u'Benutzer Diskussion:Fit-Fabrik',
u'Benutzer Diskussion:SpaceRazor',
u'Benutzer Diskussion:Fachversicherer',
u'Benutzer Diskussion:Qniemiec',
u'Benutzer Diskussion:Ilikeriri',
u'Benutzer Diskussion:Casinoroyal',
u'Benutzer Diskussion:Havanabua',
u'Benutzer Diskussion:Euku/2010/II. Quartal',       # bugzilla:32753
u'Benutzer Diskussion:Mo4jolo/Archiv/2008',
u'Benutzer Diskussion:Eschweiler',
u'Benutzer Diskussion:Marilyn.hanson',
u'Benutzer Diskussion:A.Savin',
u'Benutzer Diskussion:W!B:/Knacknüsse',
u'Benutzer Diskussion:Euku/2009/II. Halbjahr',
u'Benutzer Diskussion:Gamma',
u'Hilfe Diskussion:Captcha',
u'Benutzer Diskussion:Zacke/Kokytos',
u'Benutzer Diskussion:Wolfgang1018',
u'Benutzer Diskussion:El bes',
u'Benutzer Diskussion:Janneman/Orkus',
u'Wikipedia Diskussion:Shortcuts',
u'Benutzer Diskussion:PDD',
u'Wikipedia:WikiProjekt Vorlagen/Werkstatt',
u'Wikipedia Diskussion:WikiProjekt Wuppertal/2008',
u'Benutzer Diskussion:SchirmerPower',
u'Benutzer Diskussion:Stefan Kühn/Check Wikipedia',
u'Benutzer Diskussion:Elian',
u'Wikipedia:Fragen zur Wikipedia',
u'Benutzer Diskussion:Michael Kühntopf',
u'Benutzer Diskussion:Drahreg01',
u'Wikipedia:Vandalismusmeldung',
u'Benutzer Diskussion:Jesusfreund',
u'Benutzer Diskussion:Velipp28',
u'Benutzer Diskussion:Jotge',
u'Benutzer Diskussion:DAJ',
u'Benutzer Diskussion:Karl-G. Walther',
u'Benutzer Diskussion:Pincerno',
u'Benutzer Diskussion:Polluks',
u'Portal:Serbien/Nachrichtenarchiv',
u'Benutzer Diskussion:Elly200253',
u'Benutzer Diskussion:Yak',
u'Wikipedia:Auskunft',
u'Benutzer Diskussion:Toolittle',
u'Benutzer Diskussion:He3nry',
u'Benutzer Diskussion:Euku/2009/I. Halbjahr',
u'Benutzer Diskussion:Elchbauer' ,
u'Benutzer Diskussion:Matthiasb',
u'Benutzer Diskussion:Gripweed',
u'Wikipedia:Löschkandidaten/10. Februar 2011',
u'Benutzer Diskussion:Funkruf',
u'Benutzer Diskussion:Vux',
u'Benutzer Diskussion:Zollernalb/Archiv/2008' ,
u'Benutzer Diskussion:Geiserich77/Archiv2009',
u'Benutzer Diskussion:Markus Mueller/Archiv' ,
u'Benutzer Diskussion:Capaci34/Archiv/2009',
u'Wikipedia Diskussion:Persönliche Bekanntschaften/Archiv/2010',
u'Benutzer Diskussion:Leithian/Archiv/2009/Aug',
u'Benutzer Diskussion:Lady Whistler/Archiv/2010',
u'Benutzer Diskussion:Jens Liebenau/Archiv1',
u'Benutzer Diskussion:Tilla/Archiv/2009/Juli',
u'Benutzer Diskussion:Xqt',
u'Vorlage Diskussion:Benutzerdiskussionsseite',
u'Wikipedia Diskussion:Meinungsbilder/Gestaltung von Signaturen',
u'Benutzer Diskussion:JvB1953',
u'Benutzer Diskussion:J.-H. Janßen',
u'Benutzer Diskussion:Xqt/Archiv/2009-1',
u'Hilfe Diskussion:Weiterleitung/Archiv/1',
u'Benutzer Diskussion:Raymond/Archiv 2006-2',
u'Wikipedia Diskussion:Projektneuheiten/Archiv/2009',
u'Vorlage Diskussion:Erledigt',
u'Wikipedia:Bots/Anfragen/Archiv/2008-2',
u'Diskussion:Golfschläger/Archiv',
u'Wikipedia:Löschkandidaten/9. Januar 2006',
u'Benutzer Diskussion:Church of emacs/Archiv5',
u'Wikipedia:WikiProjekt Vorlagen/Werkstatt/Archiv 2006',
u'Wikipedia Diskussion:Löschkandidaten/Archiv7',
u'Benutzer Diskussion:Physikr',
u'Benutzer Diskussion:Haring/Archiv, Dez. 2005',
u'Benutzer Diskussion:Seewolf/Archiv 7',
u'Benutzer Diskussion:Mipago/Archiv',
u'Wikipedia Diskussion:WikiProjekt Syntaxkorrektur/Archiv/2009',
u'Benutzer Diskussion:PDD/monobook.js',
u'Wikipedia:Löschkandidaten/9. April 2010',
u'Benutzer Diskussion:Augiasstallputzer/Archiv',
u'Hilfe Diskussion:Variablen',
u'Benutzer Diskussion:Merlissimo/Archiv/2009',
u'Benutzer Diskussion:Elya/Archiv 2007-01',
u'Benutzer Diskussion:Merlissimo/Archiv/2010',
u'Benutzer Diskussion:Jonathan Groß/Archiv 2006',
u'Benutzer Diskussion:Erendissss',
u'Diskussion:Ilse Elsner',
u'Diskussion:Pedro Muñoz',
u'Diskussion:Stimmkreis Nürnberg-Süd',
u'Diskussion:Geschichte der Sozialversicherung in Deutschland',
u'Diskussion:Josef Kappius',
u'Diskussion:Bibra (Adelsgeschlecht)',
#u'Diskussion:Stimmkreis Regensburg-Land-Ost',      # [ DELETED ] 
u'Diskussion:Volkmar Kretkowski',
u'Diskussion:KS Cracovia',
u'Diskussion:Livingston (Izabal)',
u'Wikipedia Diskussion:WikiProjekt Gesprochene Wikipedia/Howto',
u'Benutzer Diskussion:Otfried Lieberknecht',
u'Benutzer Diskussion:Jahn Henne',
u'Wikipedia:WikiProjekt Begriffsklärungsseiten/Fließband',
u'Wikipedia:Löschprüfung',
u'Benutzer Diskussion:Hubertl',
u'Benutzer Diskussion:Diba',
u'Wikipedia:Qualitätssicherung/11. März 2012',
u'Benutzer Diskussion:Heubergen/Archiv/2012',
u'Benutzer Diskussion:DrTrigon/Archiv',
u'Wikipedia:Fotowerkstatt',
u'Wikipedia:Urheberrechtsfragen',
]

PAGE_SINGLE_GENERIC = PAGE_SET_Page_getSections[0]

ITEM_SINGLE_GENERIC = u'Q4115189'


class PyWikiWikipediaTestCase(test_pywiki.PyWikiTestCase):

    def setUp(self):
        result    = test_pywiki.PyWikiTestCase.setUp(self)
        self.site = pywikibot.getSite('de', 'wikipedia')
        self.repo = self.site.data_repository()
        return result

    def test_module_import(self):
        self.assertTrue( "pywikibot" in sys.modules )

    def test_Site(self):
        self._check_member(pywikibot, "Site", call=True)

    def test_Site_getParsedString(self):
        self._check_member(self.site, "getParsedString", call=True)
        test_text = u'{{CURRENTTIMESTAMP}}'
        text = self.site.getParsedString(test_text, keeptags = [])
        self.assertTrue( len(text) <= len(test_text) )
        text = self.site.getParsedString(test_text)
        self.assertTrue( len(text) >= len(test_text) )

    def test_Site_getExpandedString(self):
        self._check_member(self.site, "getExpandedString", call=True)
        test_text = u'{{CURRENTTIMESTAMP}}'
        text = self.site.getExpandedString(test_text)
        self.assertTrue( len(text) <= len(test_text) )

    def test_Page(self):
        self._check_member(pywikibot, "Page", call=True)

    def test_Page_getSections(self):
        self._check_member(pywikibot.Page(self.site, PAGE_SINGLE_GENERIC),
                           "getSections", call=True)
        self.assertEqual( len(PAGE_SET_Page_getSections), 146 )
        count = 0
        problems = []
        for i, TESTPAGE in enumerate(PAGE_SET_Page_getSections):
            page = pywikibot.Page(self.site, TESTPAGE)
            try:
                sections = page.getSections(minLevel=1)
            except pywikibot.Error:
                count += 1
                problems.append( (i, page) )
        print "Number of pages total:", len(PAGE_SET_Page_getSections)
        print "Number of problematic pages:", count
        #print "Problematic pages:", problems
        print "Problematic pages:\n", "\n".join( map(str, problems) )
        self.assertLessEqual(count, round(len(PAGE_SET_Page_getSections)/50.))
        #self.assertTrue( count <= 0 )

    def test_Page_purgeCache(self):
        page = pywikibot.Page(self.site, PAGE_SINGLE_GENERIC)
        self._check_member(page, "purgeCache", call=True)
        self.assertEqual( page.purgeCache(), True )

    def test_Page_isRedirectPage(self):
        page = pywikibot.Page(self.site, PAGE_SINGLE_GENERIC)
        self._check_member(page, "isRedirectPage", call=True)
        page.isRedirectPage()

    def test_Page_getVersionHistory(self):
        page = pywikibot.Page(self.site, PAGE_SINGLE_GENERIC)
        self._check_member(page, "getVersionHistory", call=True)
        self.assertEqual( len(page.getVersionHistory(revCount=1)), 1 )
        self.assertGreater( len(page.getVersionHistory()), 1 )

    def test_Page_get(self):
        page = pywikibot.Page(self.site, PAGE_SINGLE_GENERIC)
        self._check_member(page, "get", call=True)
        page.get()

    def test_DataPage(self):
        self._check_member(pywikibot, "DataPage", call=True)

    def test_DataPage_setitem(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "setitem", call=True)
        # more tests ... ?!

    def test_DataPage_editclaim(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "editclaim", call=True)
        # more tests ... ?!

    def test_DataPage_createitem(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "createitem", call=True)
        # more tests ... ?!

    def test_DataPage_get(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "get", call=True)
        self._check_member(page, "getentities", call=True)
        page.get()

    def test_DataPage_searchentities(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "searchentities", call=True)
        # more tests ... ?!

    def test_DataPage_linktitles(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "linktitles", call=True)
        # more tests ... ?!

    def test_DataPage_removeclaim(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "removeclaim", call=True)
        # more tests ... ?!

    def test_DataPage_removereferences(self):
        page = pywikibot.DataPage(self.repo, ITEM_SINGLE_GENERIC)
        self._check_member(page, "removereferences", call=True)
        # more tests ... ?!

if __name__ == "__main__":
    unittest.main()

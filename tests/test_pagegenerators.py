#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for pagegenerators.py"""

# This test script is intended to be used with mature unittest code.
#
# This script contains important unittests in order to ensure the function
# and stability of core code (for e.g. DrTrigonBot framework) and methods.
# You should not change code here except you want to add a new test case
# for a function, mechanism or else.

__version__ = '$Id$'

import unittest
import test_pywiki, test_wikipedia

import sys, time

import wikipedia as pywikibot
import pagegenerators


PAGE_SET_GENERIC = test_wikipedia.PAGE_SET_Page_getSections[:5]


class PyWikiPageGeneratorsTestCase(test_pywiki.PyWikiTestCase):

    def setUp(self):
        pywikibot.setLogfileStatus(False)

        result    = test_pywiki.PyWikiTestCase.setUp(self)
        self.site = pywikibot.getSite('de', 'wikipedia')

        self.ignore_list = { self.site.family.name: 
                                { self.site.lang: [u'Benutzer Diskussion'] } }

        return result

    def test_module_import(self):
        self.assertTrue( "pagegenerators" in sys.modules )       

    def test_PagesFromTitlesGenerator(self):
        self._check_member(pagegenerators, "PagesFromTitlesGenerator",
                           call=True)
        gen0 = pagegenerators.PagesFromTitlesGenerator(PAGE_SET_GENERIC)
        self.assertTrue( len(PAGE_SET_GENERIC) == len(list(gen0)) )
        # more tests ... ?!

    def test_PageTitleFilterPageGenerator(self):
        self._check_member(pagegenerators, "PageTitleFilterPageGenerator",
                           call=True)
        gen0 = pagegenerators.PagesFromTitlesGenerator(PAGE_SET_GENERIC)
        gen1 = pagegenerators.PageTitleFilterPageGenerator(gen0,
                                                           self.ignore_list)
        self.assertTrue( len(PAGE_SET_GENERIC) > len(list(gen1)) )
        # more tests ... ?!

    def test_PreloadingGenerator(self):
        self._check_member(pagegenerators, "PreloadingGenerator",
                           call=True)
        # more tests ... ?!

    # (RegexFilterPageGenerator)

    def test_sequence_and_buffering(self):
        """Test of sequence with buffering:
            gen0: PagesFromTitlesGenerator
             gen1: (PageTitleFilterPageGenerator)
              gen2: PreloadingGenerator
               [output]
        When enabling API be switching on debug mode:
            pywikibot.logging.getLogger().setLevel(pywikibot.DEBUG)
        buffering seams NOT TO WORK ANYMORE ... ?!?!!
        """

        gen0 = pagegenerators.PagesFromTitlesGenerator(PAGE_SET_GENERIC)
        gen1 = pagegenerators.PageTitleFilterPageGenerator(gen0, 
                                                           self.ignore_list)
        num  = len(list(gen1))

        gen0 = pagegenerators.PagesFromTitlesGenerator(PAGE_SET_GENERIC)
        gen1 = pagegenerators.PageTitleFilterPageGenerator(gen0, 
                                                           self.ignore_list)
        gen2 = pagegenerators.PreloadingGenerator(gen1) # ThreadedGenerator would be nice!

# TODO: solve this API buffering (speed) issue !
#        # to enable the use of the API here (seams to be slower... ?!?)
#        pywikibot.logging.getLogger().setLevel(pywikibot.DEBUG)

        for page in gen2:
            buffd, unbuffd = {}, {}

            start = time.time()
            u = page.get()
            buffd['get'] = time.time()-start

            self.assertAlmostEqual( buffd['get'], 0., places=3 )

            start = time.time()
            u = page.getVersionHistory(revCount=1)
            buffd['getVersionHistory'] = time.time()-start

            self.assertAlmostEqual( buffd['getVersionHistory'], 0., places=4 )

            start = time.time()
            u = page.getSections(minLevel=1)
            unbuffd['getSections'] = time.time()-start

            start = time.time()
            u = page.getSections(minLevel=1)
            buffd['getSections'] = time.time()-start

            self.assertAlmostEqual( buffd['getSections'], 0., places=4 )

            start = time.time()
            u = page.get(force=True)  # triggers reload of 'getSections' also
            unbuffd['get'] = time.time()-start

            start = time.time()
            u = page.getVersionHistory(revCount=1, forceReload=True)
            unbuffd['getVersionHistory'] = time.time()-start

            self.assertGreaterEqual(unbuffd['get']/buffd['get'],
                                    1E3)
            self.assertGreaterEqual(unbuffd['getVersionHistory']/buffd['getVersionHistory'],
                                    1E4)
            self.assertGreaterEqual(unbuffd['getSections']/buffd['getSections'],
                                    1E5)

            num -= 1

        self.assertEqual(num, 0)

if __name__ == "__main__":
    unittest.main()

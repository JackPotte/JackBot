#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit test framework for pywiki"""
__version__ = '$Id: d810f81e2d8a41cc45a8f6e2e9aa2502277c7735 $'

import unittest
import test_utils

import wikipedia as pywikibot


class PyWikiTestCase(unittest.TestCase):

    def setUp(self):
        self.site = pywikibot.getSite('en', 'wikipedia')

    def _check_member(self, obj, member, call=False):
        self.assertTrue( hasattr(obj, member) )
        if call:
            self.assertTrue( callable(getattr(obj, member)) )

if __name__ == "__main__":
    unittest.main()

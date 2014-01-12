#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit test framework for pywiki"""
__version__ = '$Id$'

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

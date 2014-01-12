#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for botlist.py"""

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
import botlist


class PyWikiBotlistTestCase(test_pywiki.PyWikiTestCase):

    def test_module_import(self):
        self.assertTrue( "botlist" in sys.modules )

    def test_get(self):
        self._check_member(botlist, "get", call=True)
        self.assertTrue( len(botlist.get()) > 0 )

if __name__ == "__main__":
    unittest.main()

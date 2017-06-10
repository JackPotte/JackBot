#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for external imports (externals)"""

# This test script is intended to be used with mature unittest code.
#
# This script contains important unittests in order to ensure the function
# and stability of core code (for e.g. DrTrigonBot framework) and methods.
# You should not change code here except you want to add a new test case
# for a function, mechanism or else.

__version__ = '$Id: 8c45a94b7063aa4958596d9175bee05cc37a6bc8 $'

import unittest
import test_pywiki  # imports 'wikipedia' and sets externals path

import sys, os


scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))

os.chdir( os.path.join(scriptdir, '..') )


class PyWikiExternalImporterTestCase(test_pywiki.PyWikiTestCase):

    def test_spelling(self):
        self.assertTrue(os.path.exists(os.path.join(scriptdir, '../externals/spelling')))

    def test_i18n(self):
        import i18n
        self.assertTrue( "i18n" in sys.modules )

    def test_crontab(self):
        import crontab
        self.assertTrue( "crontab" in sys.modules )

    def test_odf(self):
        import odf
        self.assertTrue( "odf" in sys.modules )

    def test_openpyxl(self):
        import openpyxl
        self.assertTrue( "openpyxl" in sys.modules )

    def test_dtbext_compiled(self):
        # skip this test (temporary work-a-round)
        return

        target = os.path.join(scriptdir, '../dtbext')
        sys.path.append(target)

        import jseg
        self.assertTrue( "jseg" in sys.modules )

        #import _mlpy as mlpy
        #self.assertTrue( "_mlpy" in sys.modules )

        #_ocropus
        self.assertTrue( os.path.exists(os.path.join(scriptdir, '../dtbext/_ocropus')) )

        #opencv
        self.assertTrue( os.path.exists(os.path.join(scriptdir, '../dtbext/opencv/haarcascades')) )
        import opencv
        self.assertTrue( "opencv" in sys.modules )

        #from pdfminer import pdfparser, pdfinterp, pdfdevice, converter, cmapdb, layout
        #self.assertTrue( "pdfminer" in sys.modules )

        import pycolorname
        self.assertTrue( "pycolorname" in sys.modules )

        try:
            import pydmtx               # linux distro package (fedora)
        except:
            import _pydmtx as pydmtx    # TS (debian)
        self.assertTrue( "pydmtx" in sys.modules )

        from colormath.color_objects import RGBColor
        self.assertTrue( "colormath" in sys.modules )

        from py_w3c.validators.html.validator import HTMLValidator, ValidationFault
        self.assertTrue( "py_w3c" in sys.modules )

        #import slic
        #self.assertTrue( "slic" in sys.modules )

        #xbob.flandmark-1.0.7
        #self.assertTrue( "flandmark" in sys.modules )

        try:
            import zbar             # TS (debian)
        except:
            import _zbar as zbar    # other distros (fedora)
        self.assertTrue( "zbar" in sys.modules )

        sys.path.remove(target)

    def test_dtbext_packaged(self):
        # skip this test (temporary work-a-round)
        return

        import numpy
        self.assertTrue( "numpy" in sys.modules )

        import scipy
        self.assertTrue( "scipy" in sys.modules )

        import cv
        self.assertTrue( "cv" in sys.modules )

        # TS: nonofficial cv2.so backport of the testing-version of
        # python-opencv because of missing build-host, done by DaB
        sys.path.append('/usr/local/lib/python2.6/')
        import cv2
        sys.path.remove('/usr/local/lib/python2.6/')
        self.assertTrue( "cv2" in sys.modules )

        import pyexiv2
        self.assertTrue( "pyexiv2" in sys.modules )

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import gtk                  # ignore warning: "GtkWarning: could not open display"
        self.assertTrue( "gtk" in sys.modules )

        import rsvg                     # gnome-python2-rsvg (binding to librsvg)
        self.assertTrue( "rsvg" in sys.modules )

        import cairo
        self.assertTrue( "cairo" in sys.modules )

        import magic                    # python-magic (binding to libmagic)
        self.assertTrue( "magic" in sys.modules )

        import pywt                     # python-pywt
        self.assertTrue( "pywt" in sys.modules )

if __name__ == "__main__":
    unittest.main()

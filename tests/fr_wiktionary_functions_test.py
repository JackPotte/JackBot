#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import os
import sys
import unittest
# JackBot
dir_test = os.path.dirname(__file__)
dir_jb = os.path.dirname(dir_test)
dir_src = os.path.join(dir_jb, 'src')
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
sys.path.append(os.path.join(dir_src, 'wiktionary'))
from lib import *
from page_functions import *
from wiktionary import *
from fr_wiktionary_functions import *
from fr_wiktionary_templates import *


class TestFrWiktionary(unittest.TestCase):

    # TODO other methods & large inputs in .txt
    def test_replace_etymology_templates(self):
        for end_char in ['}', '|']:
            test_input = '{{deet' + end_char
            test_output = '{{composé de|m=1' + end_char
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

        for template in ['abréviation', 'acronyme', 'reverlanisation', 'sigle', 'verlan']:
            test_input = '{{' + template + '}}'
            test_output = '{{' + template + '|m=1}}.'
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

            test_input = '{{' + template + '|fr}}'
            test_output = '{{' + template + '|fr|m=1}}.'
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

            test_input = '{{' + template + '|fr|m=1}}'
            test_output = '{{' + template + '|fr|m=1}}.'
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

            test_input = '{{' + template + '|m=1|fr}}'
            test_output = '{{' + template + '|fr|m=1}}.'
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

            test_input = '{{' + template + '|m=1}}'
            test_output = '{{' + template + '|m=1}}.'
            output, summary = replace_etymology_templates(test_input, '')
            self.assertEqual(test_output, output)

    def test_add_templates(self):
        test_input = '* {{T|en}} : {{trad|en|test}}\n* Solrésol : [[res\'ol]]'
        test_output = '* {{T|en}} : {{trad|en|test}}\n* {{T|solrésol}} : {{trad--|solrésol|res\'ol}}'
        output, summary = add_templates(test_input, '')
        self.assertEqual(test_output, output)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import unittest
from src.lib.WiktionaryPageFunctions import replace_etymology_templates


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


if __name__ == '__main__':
    unittest.main()

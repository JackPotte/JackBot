#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import re
import sys
try:
    import src.lib.languages
except ImportError:
    import languages


def main(*args):
    # TODO
    # 1) get https://fr.wiktionary.org/wiki/Module:langues/data 
    # 2) Regex
    #   r"\n *\t*l\['([^']+)'\] = \{ nom = '([^']+)'[^\n]+" 
    #   r"\n    '$1': '$2',"
    # 4) sorting

    # 3) Treat commented redirections
    file = open('src/lib/languages.py','r+b')
    list = file.read()

    regex = r"\n *\t*l\['([^']+)'\] = l\['([^']+)'\]"
    redirects = re.findall(regex, list)
    print(str(len(redirects)) + ' redirections found')

    redirectNames = ''
    for redirect in redirects:
        redirectNames += "\n    '" + redirect[0] + "': '" + languages.languages[redirect[1]] + "',"
    file.write(redirectNames)
    file.close

if __name__ == "__main__":
    main(sys.argv)

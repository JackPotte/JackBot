#!/usr/bin/env python
# coding: utf-8

import os, re, sys
import languages

def main(*args):
    # TODO
    # 1) get https://fr.wiktionary.org/wiki/Module:langues/data 
    # 2) Regex
    #   ur"\n *\t*l\['([^']+)'\] = \{ nom = '([^']+)'[^\n]+" 
    #   ur"\n    '$1': '$2',"
    # 4) sorting

    # 3) Treat commented redirections
    file = open('src/lib/languages.py','r+b')
    list = file.read()

    regex = ur"\n *\t*l\['([^']+)'\] = l\['([^']+)'\]"
    redirects = re.findall(regex, list)
    print str(len(redirects)) + u' redirections found'

    redirectNames = ''
    for redirect in redirects:
        redirectNames += "\n    '" + redirect[0] + "': '" + languages.languages[redirect[1]] + "',"
    file.write(redirectNames)
    file.close

if __name__ == "__main__":
    main(sys.argv)

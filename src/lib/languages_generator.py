#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, unicode_literals
import re
import sys


def main(*args) -> int:
    # TODO
    # 1) get https://fr.wiktionary.org/wiki/Module:langues/data
    # 2) Regex
    #   r"\n *\t*l\['([^']+)'\] = \{ nom = '([^']+)'[^\n]+"
    #   r"\n    '$1': '$2',"
    # 4) sorting

    # 3) Treat commented redirections
    file = open('src/lib/languages.py', 'r+b')
    file_list = file.read()

    regex = r"\n *\t*l\['([^']+)'\] = l\['([^']+)'\]"
    redirects = re.findall(regex, str(file_list))
    print(f'{len(redirects)} redirections found')

    redirect_names = ''.join(
        "\n    '"
        + redirect[0]
        + "': '"
        + languages.languages[redirect[1]]
        + "',"
        for redirect in redirects
    )
    file.write(redirect_names)
    file.close
    return 0


if __name__ == "__main__":
    main(sys.argv)

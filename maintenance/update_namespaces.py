# -*- coding: utf-8  -*-
"""
Check the family files against the live site, and updates
both the generic family.py and the site-specific family.

options:
    -upmain        Modify the main family.py, too.
    -wikimedia     Update all the wikimedia families
    <family>       Work on a given wikimedia family file
"""
#
# (C) xqt, 2010-2013
# (C) Pywikipedia bot team, 2007-2009
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re
import sys
from operator import itemgetter

sys.path.insert(1, '..')
import wikipedia
from wikipedia import output
import family_check

r_namespace_section_main = r'(?s)self\.namespaces\s*\=\s*\{.*\s+%s\s*:\s*\{(.*?)\}'
r_namespace_section_sub = r'(?s)self\.namespaces\[%s\]\s*\=\s*\{(.*?)\}'
r_namespace_section_once = r"self\.namespaces\[%d\]\['%s'\]\s*\=\s*(.*?)$"

r_string = '[u]?[r]?[\'"].*?[\'"]'
r_list = '\\[.*?\\]'
r_namespace_def = re.compile(
    r'[\'"]([a-z_-]*)[\'"]\s*\:\s*((?:%s)|(?:%s))\s*,' % (r_string, r_list))


def update_family(family, changes, upmain):
    if family:
        output(u'\nUpdating family %s' % family.name)
        family_file_name = '../families/%s_family.py' % family.name
        r_namespace_section = r_namespace_section_sub
        base_indent = 8
        skip_namespace = ()
    else:
        output(u'\nUpdating family.py')
        family_file_name = '../family.py'
        r_namespace_section = r_namespace_section_main
        base_indent = 12
        skip_namespace = (4, 5)
    family_file = open(family_file_name, 'r')
    old_family_text = family_text = family_file.read()
    family_file.close()
    namespace_defs = {}
    oncedefs = {}
    oncetext = ''
    for lang, namespaces in sorted(changes.iteritems()):
        for namespace_id, namespace_list, predefined_namespace in \
                sorted(namespaces, key=itemgetter(0)):
            if namespace_id in skip_namespace:
                continue
            msg = u'Setting namespace[%s] for %s to ' \
                  + (u'[%s]' if len(namespace_list) > 1 else u'%s')
            output(msg % (namespace_id, lang, ', '.join(namespace_list)))
            once = False
            if family and not upmain and \
               namespace_id in range(-2, 16) + [828, 829]  and \
               namespace_id not in (4, 5):
                once = True
##                namespace_section = re.search(r_namespace_section_once
##                                              % (namespace_id, lang),
##                                              family_text)
            else:
                if not family:
                    if upmain and namespace_id in (828, 829):
                        r_namespace_section = r_namespace_section_sub
                    else:
                        r_namespace_section = r_namespace_section_main
                namespace_section = re.search(r_namespace_section
                                              % namespace_id, family_text)
                if not namespace_section:
                    continue
                namespace_section_text = namespace_section.group(1)
                namespace_defs = dict(
                    [(match.group(1), match.group(2)) for match in
                     r_namespace_def.finditer(namespace_section_text)])

            msg = u'Updating namespace[%s] to ' \
                  + (u'[%s]' if len(namespace_list) > 1 else u'%s')
            output(msg % (namespace_id, ', '.join(namespace_list)))
            if once:
                if len(namespace_list) == 1:
                    new_defs = escape_string(namespace_list[0].encode('utf-8'))
                else:
                    new_defs = u", ".join(escape_string(ns) for ns in
                                          namespace_list).encode('utf-8')
                oncetext += "        self.namespaces[%d]['%s'] = [" \
                            % (namespace_id, lang) + new_defs + ']\n'
            else:
                if len(namespace_list) == 1:
                    namespace_defs[lang] = escape_string(
                        namespace_list[0].encode('utf-8'))
                else:
                    namespaces = u", ".join(escape_string(ns) for ns in
                                            namespace_list).encode('utf-8')
                    namespace_defs[lang] = '[%s]' % namespaces
                new_defs = namespace_defs.items()
                new_defs.sort(key=lambda x: x[0])

                new_text = '\n' + ''.join(
                    [(base_indent + 4) * ' ' + "'%s': %s,\n"
                     % i for i in new_defs]) + ' ' * base_indent
                family_text = family_text.replace(namespace_section.group(1),
                                                  new_text)

    family_text = re.sub('(?s)# Override defaults.*?# Most',
                         '# Override defaults\n%s\n        # Most' % oncetext,
                         family_text)
    if family_text == old_family_text:
        output(u'No changes made')
    elif test_data(family_text):
        output(u'Saving to family file')
        family_file = open(family_file_name, 'w')
        family_file.write(family_text)
        family_file.close()
    else:
        output(u'Warning! Syntax error!')
        output(family_text.decode('utf-8'))


def escape_string(string):
    return "u'%s'" % string.replace('\\', '\\\\').replace("'", "\\'")


def test_data(_test_data):
    try:
        exec _test_data
    except SyntaxError:
        return False
    except:
        return True
    return True


def check_and_update(families, update_main=False):
    for family in families:
        family = wikipedia.Family(family)
        result = family_check.check_family(family)
        update_family(family, result, update_main)
        if update_main:
            # Update also the family.py file
            update_family(None, result, update_main)


if __name__ == '__main__':
    try:
        update_main_family = False
        update_wikimedia = False
        families = ['commons', 'incubator', 'mediawiki', 'meta', 'species',
                    'test', 'wikibooks', 'wikidata', 'wikinews', 'wikiquote',
                    'wikisource', 'wikiversity', 'wikivoyage', 'wiktionary']
        fam = []
        for arg in wikipedia.handleArgs():
            if arg == '-upmain':
                update_main_family = True
            elif arg == '-wikimedia':
                update_wikimedia = True
                fam = families
            elif arg == '-skipmain':
                fam = families
            elif arg in families:
                if not arg in fam:
                    fam.append(arg)
                    update_wikimedia = False
        if not fam:
            fam = [wikipedia.default_family]
        if update_wikimedia:
            check_and_update(['wikipedia'], True)
            update_main_family = False
        check_and_update(fam, update_main_family)
    finally:
        wikipedia.stopme()

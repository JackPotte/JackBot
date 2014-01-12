# -*- coding: utf-8 -*-
"""
This script helps to find expensive templates that are subject to be converted
to Lua. It counts parser functions and then orders templates by number of these
and uploads the first n titles or alternatively templates having count()>n.

Parameters:
-start            Will start from the given title (it does not have to exist).
                  Parameter may be given as "-start" or "-start:title".
                  Defaults to '!'.
-first            Returns the first n results in decreasing order of number
                  of hits (or without ordering if used with -nosort)
                  Parameter may be given as "-first" or "-first:n".
-atleast          Returns templates with at least n hits.
                  Parameter may be given as "-atleast" or "-atleast:n".
-nosort           Keeps the original order of templates. Default behaviour is
                  to sort them by decreasing order of count(parserfunctions).
-save             Saves the results. The file is in the form you may upload it
                  to a wikipage. May be given as "-save:<filename>".
                  If it exists, titles will be appended.
-upload           Specify a page in your wiki where results will be uploaded.
                  Parameter may be given as "-upload" or "-upload:title".
                  Say good-bye to previous content if existed.
Precedence of evaluation: results are first sorted in decreasing order of
templates, unless nosort is switched on. Then first n templates are taken if
first is specified, and at last atleast is evaluated. If nosort and first are
used together, the program will stop at the nth hit without scanning the rest
of the template namespace. This may be used to run it in more sessions
(continue with -start next time).
First is strict. That means if results #90-120 have the same number of parser
functions and you specify -first:100, only the first 100 will be listed (even
if atleast is used as well).
Should you specify neither first nor atleast, all templates using parser
functions will be listed.
"""

#
# (C) Bináris, 2013
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
'''
Todo:
* Using xml and xmlstart
* Using categories
* Error handling for uploading (anyway, that's the last action, it's only
  for the beauty of the program, does not effect anything).
'''

import codecs, re
import wikipedia as pywikibot
from pagegenerators import \
                    AllpagesPageGenerator as APG, \
                    RegexFilterPageGenerator as RPG

def main(*args):
    words = ['expr', 'if', 'ifeq', 'ifexpr', 'iferror', 'switch', 'ifexist',
             'time', 'timel', 'rel2abs', 'titleparts', 'len', 'pos', 'rpos',
             'sub', 'count', 'replace', 'explode', 'urldecode']
            # default is left out because it may occur within switch only.
    addwords = {
        # Write translated parser function names here.
        'hu': [u'kif', u'ha', u'haegyenlő', u'hakif', u'hahibás', u'halétezik',
               u'idő', u'hossz', u'pozíció', u'jpozíció'],
    }
    documentsubpage = {
        # You may write here a regex representing the name of template doc
        # subpages in your wiki. Defaults to /doc.
        # These subpages will be excluded for faster run.
        'de': ur'(?i).*/Doku',
        'fr': ur'(?i).*/Documentation',
    }
    editcomment = {
        # This will be used for uploading the list to your wiki.
        'en': u'Bot: uploading the list of templates having too many parser functions',
        'hu': u'A túl sok parserfüggvényt használó sablonok listájának feltöltése',
    }
    start = '!'
    results = []
    first = None
    atleast = None
    nosort = False
    filename = None # The name of the file to save titles
    titlefile = None
    uploadpage = None
    count = 0

    # Handling parameters:
    for arg in pywikibot.handleArgs(*args):
        if arg == '-start':
            start = pywikibot.input(
                    u'From which title do you want to continue?')
        elif arg.startswith('-start:'):
            start = arg[7:]
        elif arg == '-save':
            filename = pywikibot.input('Please enter the filename:')
        elif arg.startswith('-save:'):
            filename = arg[6:]
        elif arg == '-upload':
            uploadpage = pywikibot.input('Please enter the pagename:')
        elif arg.startswith('-upload:'):
            uploadpage = arg[8:]
        elif arg == '-first':
            first = pywikibot.input(
                'Please enter the max. number of templates to display:')
        elif arg.startswith('-first:'):
            first = arg[7:]
        elif arg == '-atleast':
            atleast = pywikibot.input(
                'Please enter the min. number of functions to display:')
        elif arg.startswith('-atleast:'):
            atleast = arg[9:]
        elif arg == '-nosort':
            nosort = True


    # File operations:
    if filename:
        try:
            # This opens in strict error mode, that means bot will stop
            # on encoding errors with ValueError.
            # See http://docs.python.org/library/codecs.html#codecs.open
            titlefile = codecs.open(filename, encoding='utf-8', mode='a')
        except IOError:
            pywikibot.output("%s cannot be opened for writing." % filename)
            return
    # Limitations for result:
    if first:
        try:
            first = int(first)
            if first < 1:
                first = None
        except ValueError:
            first = None
    if atleast:
        try:
            atleast = int(atleast)
            if atleast < 2: # 1 has no effect, don't waste resources.
                atleast = None
        except ValueError:
            atleast = None

    # Ready to initialize
    site = pywikibot.getSite()
    lang = site.lang
    try:
        words.extend(addwords[lang]) # Adding translated function names
    except KeyError:
        pass
    try:
        comment = editcomment[lang]
    except KeyError:
        comment = editcomment['en']
    try:
        docregex = documentsubpage[lang] # Finding document subpage names
    except KeyError:
        docregex = ur'(?i).*/doc'
    regex = re.compile(ur'(?i)#('+ur'|'.join(words)+'):')
    gen1 = APG(start=start, namespace=10, includeredirects=False, site=site)
    gen = RPG(gen1, docregex, inverse=True)

    # Processing:
    pywikibot.output(u'Hold on, this will need some time. '
                     u'You will be notified by 50 templates.')
    for page in gen:
        count += 1
        title = page.title()
        if not count % 50:
            # Don't let the poor user panic in front of a black screen.
            pywikibot.output('%dth template is beeing processed: %s' %
                (count, title))
        text = page.get()
        functions = regex.findall(text)
        if functions:
            results.append((title,len(functions)))
        if nosort and first and len(results) == first:
            break

    # Combing the results:
    if not nosort:
        results.sort(key=lambda x:str(5000-x[1])+'.'+x[0])
    if first:
        results = results[:first]
    if atleast:
        results = filter(lambda x: x[1] >= atleast, results)

    # Outputs:
    resultlist = '\n'.join(
        ['#[[%s]] (%d)' % (result[0], result[1]) for result in results])
    pywikibot.output(resultlist)
    pywikibot.output(u'%d templates were examined.' % count)
    pywikibot.output(u'%d templates were found.' % len(results))
    if titlefile:
        titlefile.write(resultlist)
        titlefile.close()
    if uploadpage:
        page = pywikibot.Page(site, uploadpage)
        page.put(resultlist, comment)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

# -*- coding: utf-8 -*-
"""
This script will collect articles that have n dash or m dash character in their
title, and create a redirect to them automatically from the corresponding
hyphenated title. If the target exists, will be skipped.
It may take several hours. You may quit by Ctrl C at any time and continue
later. Type the first few characters of the last shown title after -start.

The script is primarily designed for work in article namespace, but can be used
in any other one. Use in accordance with the rules of your community.

Known parameters:
-start            Will start from the given title (it does not have to exist).
                  Parameter may be given as "-start" or "-start:title"
                  Defaults to '!'.
-namespace        Works in the given namespace (only one at a time). Parameter
-ns               may be given as "-ns:<number>" or "-namespace:<number>".
                  Defaults to 0 (main namespace).
-nosub            Will not process subpages. Useful in template or portal
                  namespace. (Not recommended for main namespace that has no
                  real subpages.)
-save             Saves the title of existing hyphenated articles whose content
                  is _other_ than a redirect to the corresponding article with
                  n dash or m dash in the title and thus may need manual
                  treatment. If omitted, these titles will be written only to
                  the screen (or the log if logging is on). The file is in the
                  form you may upload it to a wikipage.
                  May be given as "-save:<filename>". If it exists, titles
                  will be appended.
                  After checking these titles, you may want to write them to
                  your ignore file (see below).
-ignore           A file that contains titles that are not to be claimed to
                  redirect somewhere else. For example, if X-1 (with hyphen)
                  redirects to a disambiguation page that lists X–1 (with n
                  dash), that's OK and you don't want it to appear at each run
                  as a problematic article.
                  File must be encoded in UTF-8 and contain titles among double
                  square brackets (e.g. *[[X-1]] or [[:File:X-1.gif]]).
                  May be given as "-ignore:<filename>".
"""

#
# (C) Bináris, 2012
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

import codecs, re
import wikipedia as pywikibot
from pagegenerators import RegexFilterPageGenerator as RPG
from pywikibot import i18n

def main(*args):
    regex = ur'.*[–—]' # Alt 0150 (n dash), alt 0151 (m dash), respectively.
    ns = 0
    start = '!'
    filename = None # The name of the file to save titles
    titlefile = None # The file object itself
    ignorefilename = None # The name of the ignore file
    ignorelist = [] # A list to ignore titles that redirect to somewhere else

    # Handling parameters:
    for arg in pywikibot.handleArgs(*args):
        if arg == '-start':
            start = pywikibot.input(
                    u'From which title do you want to continue?')
        elif arg.startswith('-start:'):
            start = arg[7:]
        elif arg in ['-ns', '-namespace']:
            ns = pywikibot.input(u'Which namespace should we process?')
        elif arg.startswith('-ns:') or arg.startswith('-namespace:'):
            ns = arg[arg.find(':')+1:]
        elif arg == '-nosub':
            regex = ur'[^/]*[–—][^/]*$'
        elif arg == '-save':
            filename = pywikibot.input('Please enter the filename:')
        elif arg.startswith('-save:'):
            filename = arg[6:]
        elif arg == '-ignore':
            ignorefilename = pywikibot.input('Please enter the filename:')
        elif arg.startswith('-ignore:'):
            ignorefilename = arg[8:]

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
    if ignorefilename:
        try:
            igfile = codecs.open(ignorefilename, encoding='utf-8', mode='r')
            ignorelist = re.findall(ur'\[\[:?(.*?)\]\]', igfile.read())
            igfile.close()
        except IOError:
            pywikibot.output("%s cannot be opened for reading." % ignorefilename)
            return

    # Ready to initialize
    site = pywikibot.getSite()
    redirword = site.redirect()
    gen = RPG(site.allpages(
          start=start, namespace=ns, includeredirects=False), [regex])

    # Processing:
    for page in gen:
        title = page.title()
        editSummary = i18n.twtranslate(site, 'ndashredir-create',
                                           {'title': title})
        newtitle = title.replace(u'–','-').replace(u'—','-')
        # n dash -> hyphen, m dash -> hyphen, respectively
        redirpage = pywikibot.Page(site, newtitle)
        if redirpage.exists():
            if redirpage.isRedirectPage() and \
                        redirpage.getRedirectTarget() == page:
                pywikibot.output(
                    u'[[%s]] already redirects to [[%s]], nothing to do with it.'
                    % (newtitle, title))
            elif newtitle in ignorelist:
                pywikibot.output(
                    u'Skipping [[%s]] because it is on your ignore list.'
                    % newtitle)
            else:
                pywikibot.output(
                    (u'\03{lightyellow}Skipping [[%s]] because it exists '
                     u'already with a different content.\03{default}')
                    % newtitle)
                if titlefile:
                    s = u'\n#%s does not redirect to %s.' %\
                    (redirpage.title(asLink=True, textlink=True),
                    page.title(asLink=True, textlink=True))
                    # For the unlikely case if someone wants to run it in
                    # file namespace.
                    titlefile.write(s)
                    titlefile.flush()
        else:
            text = u'#%s[[%s]]' % (redirword, title)
            try:
                redirpage.put(text, editSummary)
            except pywikibot.LockedPage, err:
                pywikibot.output(
                    (u'\03{lightyellow}Skipping [[%s]] because it is '
                     u'protected.\03{default}') % newtitle)
            except:
                pywikibot.output(
                    (u'\03{lightyellow}Skipping [[%s]] because of an error.'
                     u'\03{default}') % newtitle)
        # Todo: output the title upon Ctrl C? (KeyboardInterrupt always hits
        # RegexFilterPageGenerator or throttle.py or anything else and cannot
        # be catched in this loop.)
    if titlefile:
        titlefile.close() # For  the spirit of programming (it was flushed)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

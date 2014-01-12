# -*- coding: utf-8  -*-
"""Splits a interwiki.log file into chunks of warnings separated by language.

The following parameter is supported:

-folder:          The target folder to save warning files, if given. Otherwise
                  use the /logs/ folder.
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Pywikipedia bot team, 2004-2012
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import wikipedia as pywikibot
import codecs
import re

def splitwarning(folder):
    files={}
    count={}
    fn = pywikibot.config.datafilepath("logs", "interwiki.log")
    logFile = codecs.open(fn, 'r', 'utf-8')
    rWarning = re.compile('WARNING: (?P<family>.+?): \[\[(?P<code>.+?):.*')
    for line in logFile:
        m = rWarning.match(line)
        if m:
            family = m.group('family')
            code = m.group('code')
            if code in pywikibot.getSite().languages():
                if not code in files:
                    files[code] = codecs.open(
                        pywikibot.config.datafilepath(
                            folder, 'warning-%s-%s.log' % (family, code)),
                        'w', 'utf-8')
                    count[code] = 0
                files[code].write(line)
                count[code] += 1
    for code in files.keys():
        print '* %s (%d)' % (code, count[code])

def main(*args):
    folder = 'logs'
    for arg in pywikibot.handleArgs(*args):
        if arg.startswith("-folder"):
            folder = arg[len('-folder:'):]
    splitwarning(folder)

if __name__ == "__main__":
    # No need to have me on the stack - I don't contact the wiki
    pywikibot.stopme()
    main()

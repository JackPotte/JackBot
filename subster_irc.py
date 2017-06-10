#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Robot which connects to Recent Changes channel and runs "SubsterBot" whenever
needed. Alternative to test panel 'substersim.py' but no need of external
toolserver tool and web server to test correctness anymore - everything can be
done within wiki.

Note: the script requires the Python IRC library
http://python-irclib.sourceforge.net/
"""
## @package subster_irc
#  @brief   Dynamic Text Substitutions IRC surveillance Robot
#
#  @copyright Dr. Trigon, 2011
#  @copyright Balasyum
#
#  @section FRAMEWORK
#
#  Python wikipedia robot framework, DrTrigonBot.
#  @see http://pywikipediabot.sourceforge.net/
#  @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
#  @section LICENSE
#
#  Distributed under the terms of the LGPL license.
#
__version__ = '$Id: 859177f1f9ebdc7b29c3ec0965ddac52c070a5f1 $'
#

import wikipedia as pywikibot

import articlenos
import subster
#import botlist
from collections import deque
import time
import thread

# Configuration imported from 'subster.py'.


class SubsterTagModifiedBot(articlenos.ArtNoDisp):
#    def __init__(self, site, channel, nickname, server, port=6667):
#        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
#        self.channel = channel
#        self.site = site
#        self.other_ns = re.compile(
#            u'14\[\[07(' + u'|'.join(site.namespaces()) + u')')
#        self.api_url = self.site.api_address()
#        self.api_url += 'action=query&meta=siteinfo&siprop=statistics&format=xml'
#        self.api_found = re.compile(r'articles="(.*?)"')
#        self.re_edit = re.compile(
#            r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))
#
    def __init__(self, *arg):
        articlenos.ArtNoDisp.__init__(self, *arg)

        self.refs  = {}
        self.time  = 0.
        self.queue = deque([])

        self.templ = pywikibot.Page(self.site, subster.bot_config['TemplateName'])
        self.do_refresh_References()

        # init constants
        self._BotName = subster.bot_config['BotName']
        self._ConfCSSconfigPage = pywikibot.Page(self.site, subster.bot_config['ConfCSSconfig'])
        self._difflink = []
        if self._ConfCSSconfigPage.exists():
            exec(self._ConfCSSconfigPage.get())    # with variable: bot_config_wiki
            self._difflink = bot_config_wiki['difflink']

    def on_pubmsg(self, c, e):
        match = self.re_edit.match(e.arguments()[0])
        if not match:
            return
#        print match.groups(), match.group('page'), match.group('user')
        user = match.group('user').decode(self.site.encoding())
        if user == self._BotName:
            return
        #if botlist.isBot(user):
        #    return
        # test actual page against (template incl.) list
        page = match.group('page').decode(self.site.encoding())
        if page in self.refs:
            self.do_check(page)
        else:
            if page not in self.queue:
                self.queue.append( page ) # check later
        # refresh list and test (queued) old pages against new list
        (size, age) = ( len(self.queue), (time.time()-self.time) )
        if (size > 1000) or (age > 300):
            pywikibot.output(u'QUEUE: size=%i, age=%f' % (size, age))
            self.do_refresh_References()
            while self.queue:
                pop = self.queue.popleft()
                if pop in self.refs:
                    self.do_check(pop)
        # test actual page against 'difflink' list ("HACKY")
        p = page
        for (target, source, params) in self._difflink:
            if params['subpages']:
                p = p.split('/')
            else:
                p = [p]
            if (source == p[0]):
                pywikibot.output(u'DIFFLINK: target=%s, source=%s, params=%s' % (target, source, params))
                text = u'[[%s]] / [[User:%s]] / %s' % ( page,
                                                        user,
                                           match.group('summary').decode(self.site.encoding()) )
                self.do_check(target, params=(text, params['flags']))

    def do_refresh_References(self):
#        print "refresh"
        self.refs = {}
        self.time = time.time()
        for page in self.templ.getReferences(follow_redirects=False,
                                             onlyTemplateInclusion=True):
            self.refs[page.title()] = page

    def do_check(self, page_title, params=None):
        # Create two threads as follows
        # (simple 'thread' for more sophisticated code use 'threading')
        pywikibot.output(u"CHECK: %s" % page_title)
        try:
            thread.start_new_thread( main_subster, (self.refs[page_title], params) )
        except:
            pywikibot.warning(u"unable to start thread")

# Define a function for the thread
def main_subster(page, params=None):
    bot = subster.SubsterBot()
    page.get(force=True)     # refresh page content
    bot.silent  = True
    bot.pagegen = [ page ]   # single page, according to pagegenerators.py
    if params:
        bot.run(msg = params[0], EditFlags = params[1])
    else:
        bot.run()
    del bot

def main():
    args = pywikibot.handleArgs()
    site = pywikibot.getSite()
    site.forceLogin()
    chan = '#' + site.language() + '.' + site.family.name
    bot = SubsterTagModifiedBot(site, chan, site.loggedInAs(), "irc.wikimedia.org")
    for arg in args:
        pywikibot.showHelp()
        return
    try:
        bot.start()
    except KeyboardInterrupt:
        pywikibot.output('\nQuitting program...')

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

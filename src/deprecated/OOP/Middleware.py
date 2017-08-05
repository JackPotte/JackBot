#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
ébauche de middleware entre frameworks.

This script understands the following command-line arguments:

&params;

Furthermore, the following command line parameters are supported:

    -hours:#       Use this parameter if to make the script repeat itself
                   after # hours. Hours can be defined as a decimal. 0.01
                   hours are 36 seconds; 0.1 are 6 minutes.

    -delay:#       Use this parameter for a wait time after the last edit
                   was made. If no parameter is given it takes it from
                   hours and limits it between 5 and 15 minutes.
                   The minimum delay time is 5 minutes.

    -text          The text that substitutes in the sandbox, you can use this
                   when you haven't configured clean_candbox for your wiki.

    -summary       Summary of the edit made by bot.

"""
#
# (C) Hubert BOSSOT, 2017
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals
__version__ = '$Id$'
#

import datetime
import time
import pywikibot

from pywikibot import i18n, Bot, pagegenerators

content = {
    'en': u'',
    'fr': u'',
}

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}


class Middleware(Bot):

    availableOptions = {
        'hours': 1,
        'no_repeat': True,
        'delay': None,
        'delay_td': None,
        'text': "",
        'summary': "",
    }

    def __init__(self, **kwargs):
        """Constructor."""
        super(SandboxBot, self).__init__(**kwargs)
        if self.getOption('delay') is None:
            d = min(15, max(5, int(self.getOption('hours') * 60)))
            self.availableOptions['delay_td'] = datetime.timedelta(minutes=d)
        else:
            d = max(5, self.getOption('delay'))
            self.availableOptions['delay_td'] = datetime.timedelta(minutes=d)

        self.site = pywikibot.Site()
        if not content.get(self.site.code) and not self.getOption('text'):
            pywikibot.error(u'No content is given for pages, exiting.')
            raise RuntimeError
        if not self.generator:
            if self.site.code not in sandboxTitle:
                pywikibot.bot.suggest_help(missing_generator=True)
                raise RuntimeError
            local_sandbox_title = sandboxTitle[self.site.code]
            if not isinstance(local_sandbox_title, list):
                local_sandbox_title = [local_sandbox_title]
            self.generator = [pywikibot.Page(self.site, page_name) for
                              page_name in local_sandbox_title]

    def run(self):
        """Run bot."""
        self.site.login()
        while True:
            wait = False
            now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
            for sandboxPage in self.generator:
                pywikibot.output(u'Preparing to process sandbox page %s'
                                 % sandboxPage.title(asLink=True))
                if sandboxPage.isRedirectPage():
                    pywikibot.warning(
                        u'%s is a redirect page, cleaning it anyway'
                        % sandboxPage.title(asLink=True))
                try:
                    text = sandboxPage.text
                    if not self.getOption('text'):
                        translatedContent = i18n.translate(self.site, content)
                    else:
                        translatedContent = self.getOption('text')
                    if self.getOption('summary'):
                        translatedMsg = self.getOption('summary')
                    else:
                        translatedMsg = i18n.twtranslate(
                            self.site, 'clean_sandbox-cleaned')
                    subst = 'subst:' in translatedContent
                    pos = text.find(translatedContent.strip())
                    if text.strip() == translatedContent.strip():
                        pywikibot.output(
                            u'The sandbox is still clean, no change necessary.')
                    elif subst and sandboxPage.userName() == self.site.user():
                        pywikibot.output(
                            u'The sandbox might be clean, no change necessary.')
                    elif pos != 0 and not subst:
                        sandboxPage.put(translatedContent, translatedMsg)
                        pywikibot.showDiff(text, translatedContent)
                        pywikibot.output(u'Standard content was changed, '
                                         u'sandbox cleaned.')
                    else:
                        edit_delta = (datetime.datetime.utcnow() -
                                      sandboxPage.editTime())
                        delta = self.getOption('delay_td') - edit_delta
                        # Is the last edit more than 'delay' minutes ago?
                        if delta <= datetime.timedelta(0):
                            sandboxPage.put(translatedContent, translatedMsg)
                            pywikibot.showDiff(text, translatedContent)
                            pywikibot.output(u'Standard content was changed, '
                                             u'sandbox cleaned.')
                        else:  # wait for the rest
                            pywikibot.output(
                                u'Sandbox edited %.1f minutes ago...'
                                % (edit_delta.seconds / 60.0))
                            pywikibot.output(u'Sleeping for %d minutes.'
                                             % (delta.seconds // 60))
                            time.sleep(delta.seconds)
                            wait = True
                except pywikibot.EditConflict:
                    pywikibot.output(
                        u'*** Loading again because of edit conflict.\n')
                except pywikibot.NoPage:
                    pywikibot.output(
                        u'*** The sandbox is not existent, skipping.')
                    continue
            if self.getOption('no_repeat'):
                pywikibot.output(u'\nDone.')
                return
            elif not wait:
                if self.getOption('hours') < 1.0:
                    pywikibot.output('\nSleeping %s minutes, now %s'
                                     % ((self.getOption('hours') * 60), now))
                else:
                    pywikibot.output('\nSleeping %s hours, now %s'
                                     % (self.getOption('hours'), now))
                time.sleep(self.getOption('hours') * 60 * 60)


def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    opts = {}
    local_args = pywikibot.handle_args(args)
    gen_factory = pagegenerators.GeneratorFactory()
    for arg in local_args:
        if arg.startswith('-hours:'):
            opts['hours'] = float(arg[7:])
            opts['no_repeat'] = False
        elif arg.startswith('-delay:'):
            opts['delay'] = int(arg[7:])
        elif arg.startswith('-text'):
            if len(arg) == 5:
                opts['text'] = pywikibot.input(
                    u'What text do you want to substitute?')
            else:
                opts['text'] = arg[6:]
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                opts['summary'] = pywikibot.input(u'Enter the summary:')
            else:
                opts['summary'] = arg[9:]
        else:
            gen_factory.handleArg(arg)

    generator = gen_factory.getCombinedGenerator()

    bot = SandboxBot(generator=generator, **opts)
    bot.run()


if __name__ == "__main__":
    main()

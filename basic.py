#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is not a complete bot; rather, it is a template from which simple
bots can be made. You can rename it to mybot.py, then edit it in
whatever way you want.

The following parameters are supported:

&params;

-summary:XYZ      Set the summary message text for the edit to XYZ, bypassing
                  the predefined message texts with original and replacements
                  inserted.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
#
# (C) Pywikipedia bot team, 2006-2011
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re

import wikipedia as pywikibot
import pagegenerators
from pywikibot import i18n

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class BasicBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, summary):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
            @param summary: Set the summary message text for the edit.
            @type summary: (unicode) string.
        """
        self.generator = generator
        # init constants
        self.site = pywikibot.getSite(code=pywikibot.default_code)
        # Set the edit summary message
        if summary:
            self.summary = summary
        else:
            self.summary = i18n.twtranslate(self.site, 'basic-changing')

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        text = self.load(page)
        if not text:
            return

        ################################################################
        # NOTE: Here you can modify the text in whatever way you want. #
        ################################################################

        # If you find out that you do not want to edit this page, just return.
        # Example: This puts the text 'Test' at the beginning of the page.
        text = 'Test ' + text

        if not self.save(text, page, self.summary):
            pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))

    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment=None, **kwargs):
        # only save if something was changed
        if text != page.get():
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(page.get(), text)
            pywikibot.output(u'Comment: %s' % comment)
            choice = pywikibot.inputChoice(
                u'Do you want to accept these changes?',
                ['Yes', 'No'], ['y', 'N'], 'N')
            if choice == 'y':
                try:
                    # Save the page
                    page.put(text, comment=comment or self.comment, **kwargs)
                except pywikibot.LockedPage:
                    pywikibot.output(u"Page %s is locked; skipping."
                                     % page.title(asLink=True))
                except pywikibot.EditConflict:
                    pywikibot.output(
                        u'Skipping %s because of edit conflict'
                        % (page.title()))
                except pywikibot.SpamfilterError, error:
                    pywikibot.output(
                        u'Cannot change %s because of spam blacklist entry %s'
                        % (page.title(), error.url))
                else:
                    return True
        return False


class AutoBasicBot(BasicBot):
    # Intended for usage e.g. as cronjob without prompting the user.

    _REGEX_eol = re.compile(u'\n')

    def __init__(self):
        BasicBot.__init__(self, None, None)

    ## @since   10326
    #  @remarks needed by various bots
    def save(self, page, text, comment=None, **kwargs):
        pywikibot.output(u'\03{lightblue}Writing to wiki on %s...\03{default}'
                         % page.title(asLink=True))

        comment_output = comment or pywikibot.action
        pywikibot.output(u'\03{lightblue}Comment: %s\03{default}'
                         % comment_output)

        #pywikibot.showDiff(page.get(), text)

        for i in range(3):
            try:
                # Save the page
                page.put(text, comment=comment, **kwargs)
            except pywikibot.LockedPage:
                pywikibot.output(
                    u"\03{lightblue}Page %s is locked; skipping.\03{default}"
                    % page.title(asLink=True))
            except pywikibot.EditConflict:
                pywikibot.output(
                    u'\03{lightblue}Skipping %s because of edit '
                    u'conflict\03{default}' % (page.title()))
            except pywikibot.SpamfilterError, error:
                pywikibot.output(
                    u'\03{lightblue}Cannot change %s because of spam blacklist '
                    u'entry %s\03{default}' % (page.title(), error.url))
            else:
                return True
        return False

    ## @since   10326
    #  @remarks needed by various bots
    def append(self, page, text, comment=None, section=None, **kwargs):
        if section:
            pywikibot.output(
                u'\03{lightblue}Appending to wiki on %s in section '
                u'%s...\03{default}' % (page.title(asLink=True), section))
            for i in range(3):
                try:
                    # Append to page section
                    page.append(text, comment=comment, section=section,
                                **kwargs)
                except pywikibot.PageNotSaved, error:
                    pywikibot.output(
                        u'\03{lightblue}Cannot change %s because of '
                        u'%s\03{default}' % (page.title(), error))
                else:
                    return True
        else:
            content = self.load(page)     # 'None' if not existing page
            if not content:                 # (create new page)
                content = u''

            content += u'\n\n'
            content += text

            return self.save(page, content, comment=comment, **kwargs)

    ## @since   10326
    #  @remarks needed by various bots
    def loadTemplates(self, page, template, default={}):
        """Get operating mode from page with template by searching the template.

           @param page: The user (page) for which the data should be retrieved.

           Returns a list of dict with the templates parameters found.
        """

        self._content = self.load(page)  # 'None' if not existing page

        templates = []
        if not self._content:
            return templates  # catch empty or not existing page

        for tmpl in pywikibot.extract_templates_and_params(self._content):
            if tmpl[0] == template:
                param_default = {}
                param_default.update(default)
                param_default.update(tmpl[1])
                templates.append(param_default)
        return templates

    ## @since   10326
    #  @remarks common interface to bot job queue on wiki
    def loadJobQueue(self, page, queue_security, reset=True):
        """Check if the data queue security is ok to execute the jobs,
           if so read the jobs and reset the queue.

           @param page: Wiki page containing job queue.
           @type  page: page
           @param queue_security: This string must match the last edit
                              comment, or else nothing is done.
           @type  queue_security: string

           Returns a list of jobs. This list may be empty.
        """

        try:
            actual = page.getVersionHistory(revCount=1)[0]
        except:
            pass

        secure = False
        for item in queue_security[0]:
            secure = secure or (actual[2] == item)

        secure = secure and (actual[3] == queue_security[1])

        if not secure:
            return []

        data = self._REGEX_eol.split(page.get())
        if reset:
            pywikibot.output(u'\03{lightblue}Job queue reset...\03{default}')
            pywikibot.setAction(u'reset job queue')
            page.put(u'', minorEdit=True)

        queue = []
        for line in data:
            queue.append(line[1:].strip())
        return queue


def main():
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []
    # summary message
    editSummary = ''

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith('-summary:'):
            editSummary = arg[9:]
        else:
            # check if a standard argument like
            # -start:XYZ or -ref:Asdf was given.
            if not genFactory.handleArg(arg):
                pageTitleParts.append(arg)

    if pageTitleParts != []:
        # We will only work on a single page.
        pageTitle = ' '.join(pageTitleParts)
        page = pywikibot.Page(pywikibot.getSite(), pageTitle)
        gen = iter([page])

    if not gen:
        gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        bot = BasicBot(gen, editSummary)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

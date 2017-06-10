#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Usage:

python harvest_template.py -lang:nl -template:"Taxobox straalvinnige" orde P70 familie P71 geslacht P74

This will work on all pages that transclude the template in the article
namespace

You can use any typical pagegenerator to provide with a list of pages:

python harvest_template.py -lang:nl -cat:Sisoridae -template:"Taxobox straalvinnige" -namespace:0 orde P70 familie P71 geslacht P74

"""
#
# (C) 2013 Multichill, Amir
# (C) 2013 Pywikipediabot team
#
# Distributed under the terms of MIT License.
#
__version__ = '$Id: fe199c087a8b0176c8466d65365779343628b352 $'
#

import re
import wikipedia as pywikibot
import pagegenerators as pg


class HarvestRobot:
    """
    A bot to add Wikidata claims
    """
    def __init__(self, generator, templateTitle, fields):
        """
        Arguments:
            * generator     - A generator that yields Page objects.
            * templateTitle - The template to work on
            * fields        - A dictionary of fields that are of use to us

        """
        self.generator = generator
        self.templateTitle = templateTitle.replace(u'_', u' ')
        self.pregen = pg.PreloadingGenerator(generator)
        self.fields = fields
        self.site = pywikibot.getSite()
        self.repo = self.site.data_repository()

    def setSource(self, lang):
        '''
        Get the source
        '''
        source_values = {'en':  'Q328',
                         'sv':  'Q169514',
                         'de':  'Q48183',
                         'it':  'Q11920',
                         'no':  'Q191769',
                         'fa':  'Q48952',
                         'ar':  'Q199700',
                         'es':  'Q8449',
                         'pl':  'Q1551807',
                         'ca':  'Q199693',
                         'fr':  'Q8447',
                         'nl':  'Q10000',
                         'pt':  'Q11921',
                         'ru':  'Q206855',
                         'vi':  'Q200180',
                         'be':  'Q877583',
                         'uk':  'Q199698',
                         'tr':  'Q58255',
                        }  # TODO: Should be moved to a central wikidata library

        if lang in source_values:
            source = ('143', source_values.get(lang))
            return source
        else:
            return None

    def run(self):
        """
        Starts the robot.
        """
        for page in self.pregen:
            self.procesPage(page)

    def procesPage(self, page):
        """
        Proces a single page
        """
        item = pywikibot.DataPage(page)
        pywikibot.output('Processing %s' % page)
        if not item.exists():
            pywikibot.output('%s doesn\'t have a wikidata item :(' % page)
            #TODO FIXME: We should provide an option to create the page
        else:
            pagetext = page.get()
            pagetext = pywikibot.removeDisabledParts(pagetext)
            templates = pywikibot.extract_templates_and_params(pagetext)
            for (template, fielddict) in templates:
                # We found the template we were looking for
                if template.replace(u'_', u' ') == self.templateTitle:
                    for field, value in fielddict.items():
                        # This field contains something useful for us
                        if field in self.fields:
                            # Check if the property isn't already set
                            claim = self.fields[field]
                            if claim in item.get().get('claims'):
                                pywikibot.output(
                                    u'A claim for %s already exists. Skipping'
                                    % (claim,))
                                # TODO FIXME: This is a very crude way of dupe
                                # checking
                            else:
                                # Try to extract a valid page
                                match = re.search(re.compile(
                                    r'\[\[(?P<title>[^\]|[#<>{}]*)(\|.*?)?\]\]'),
                                                  value)
                                if match:
                                    try:
                                        link = match.group(1)
                                        linkedPage = pywikibot.Page(self.site,
                                                                    link)
                                        if linkedPage.isRedirectPage():
                                            linkedPage = linkedPage.getRedirectTarget()
                                        linkedItem = pywikibot.DataPage(linkedPage)
                                        pywikibot.output('Adding %s --> %s'
                                                         % (claim,
                                                            linkedItem.getID()))
                                        if self.setSource(self.site().language()):
                                            item.editclaim(
                                                str(claim),
                                                linkedItem.getID(),
                                                refs={self.setSource(
                                                    self.site().language())})
                                        else:
                                            item.editclaim(str(claim),
                                                           linkedItem.getID())
                                    except pywikibot.NoPage:
                                        pywikibot.output(
                                            "[[%s]] doesn't exist so I can't link to it"
                                            % linkedItem.title())


def main():
    genFactory = pg.GeneratorFactory()
    commandline_arguments = list()
    templateTitle = u''
    for arg in pywikibot.handleArgs():
        if arg.startswith('-template'):
            if len(arg) == 9:
                templateTitle = pywikibot.input(
                    u'Please enter the template to work on:')
            else:
                templateTitle = arg[10:]
        elif genFactory.handleArg(arg):
            continue
        else:
            commandline_arguments.append(arg)

    if len(commandline_arguments) % 2 or not templateTitle:
        raise ValueError  # or something.
    fields = dict()

    for i in xrange(0, len(commandline_arguments), 2):
        fields[commandline_arguments[i]] = commandline_arguments[i + 1]
    if templateTitle:
        gen = pg.ReferringPageGenerator(pywikibot.Page(pywikibot.getSite(),
                                                       "Template:%s"
                                                       % templateTitle),
                                        onlyTemplateInclusion=True)
    else:
        gen = genFactory.getCombinedGenerator()
    if not gen:
        # TODO: Build a transcluding generator based on templateTitle
        return

    bot = HarvestRobot(gen, templateTitle, fields)
    bot.run()

if __name__ == "__main__":
    main()

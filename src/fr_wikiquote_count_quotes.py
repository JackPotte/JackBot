#!/usr/bin/env python
# coding: utf-8	
"""
This script counts the number of quotes.

# TODO :
#  - Check for different quotes with the same 'original' field
#  - Check not only for equal, but similar quotes (distance d'edition)
#  - Check for same quote with different refs

This script understands various command-line arguments:

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

    -links         Work on all pages that are linked from a certain page.
                   Argument can also be given as "-links:linkingpagetitle".

    -new           Work on the most recent new pages on the wiki

    -subcat        When the pages to work on have been chosen by -cat, pages in
                   subcategories of the selected category are also included.
                   When -cat has not been selected, this has no effect.
    

    -file:         used as -file:file_name, read a list of pages to treat
                   from the named file


    -start:        used as -start:title, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.
    -output:       used as -output:page_name, generate report to page_name.
    -outputprefix: used as -output:page_name, create NUMBEROFQUOTES and
                   NUMBEROFARTICLES as subpages of page_name
    -outputquotes: used as -outputquotes:page_name, put the number of quotes on page_name
    -outputarticles: used as -outputarticles:page_name, put the number of articles containing quotes on page_name
"""
from __future__ import absolute_import, unicode_literals
import locale
import operator
import re
import sys
import time
import pywikibot
from pywikibot import config, pagegenerators, User

site = pywikibot.Site('fr', 'wikiquote')
msg = {
    'fr': (
        '<h1 style="border-bottom:none;margin-top:0;margin-bottom:0.8em;text-align:center;"> %d citations dans %d articles ',
        '<small>(Le nombre d\'articles n\'inclut que les articles qui possèdent au moins une citation. Les citations en plusieurs exemplaires ne sont comptées qu\'une fois.)',
        '== Répartion par article ==\n\n',
        '{| class="wikitable sortable"\n|+\'\'\'Nombre de citations par article\'\'\'\n! align="center" | Article\n! align="center" | Nombre de citations\n',
        '|- align="center" \n| \'\'\'Moyenne\'\'\' || %0.2f\n',
        '<small>La moyenne exclut les articles ne contenant aucune citation.</small>\n\n',
        '== Citations en plusieurs exemplaires ==\n',
        '<small>(Ce tableau recense le nombre de citations qui figurent dans plusieurs articles. Ainsi, si le premier champ vaut N et le second M, cela signifie que M citations figurent en N exemplaires (dans N articles))</small>\n\n',
        '{| class="wikitable" style="width: 40%%"\n|+\'\'\'Nombre d\'exemplaires de la citation\'\'\'\n! align="center" | Article\n! align="center" | Nombre de citations\n',
        'Mise à jour des statistiques'),
    'is': (
        '<h1 style="border-bottom:none;margin-top:0;margin-bottom:0.8em;text-align:center;"> %d tilvitnanir ÃƒÂ­ %d greinum ',
        '<small>(ÃƒÂ fjÃƒÂ¶lda greina eru greinar meÃƒÂ° engum tilvitnunum ekki taldar meÃƒÂ°. TvÃƒÂ¶faldaÃƒÂ°ar tilvitnanir eru taldar sem ein.)',
        '== Eftir greinum ==\n\n',
        '{| class="wikitable"\n|+\'\'\'FjÃƒÂ¶ldi tilvitnana eftir greinum\'\'\'\n! align="center" | Grein\n! align="center" | FjÃƒÂ¶ldi tilvitna\n',
        '|- align="center" \n| \'\'\'MeÃƒÂ°altal\'\'\' || %0.2f\n',
        '<small>MeÃƒÂ°altaliÃƒÂ° telur ekki meÃƒÂ° greinar sem innihalda engar tilvitnanir.</small>\n\n',
        '== TvÃƒÂ¶faldar tilvitnanir ==\n',
        '<small>(ÃƒÅ¾essi tafla sÃƒÂ½nir fjÃƒÂ¶lda tilvitnana sem koma fram ÃƒÂ­ fleirum en einni grein. If the first field is N and the second M, it means M quotes appear N times (in N articles))</small>\n\n',
        '{| class="wikitable" style="width: 40%%"\n|+\'\'\'FjÃƒÂ¶ldi greina sem tilvitnunin kemur fyrir\'\'\n! align="center" | Greinar\n! align="center" | FjÃƒÂ¶ldi tilvitnana\n',
        'Updated statistics'),
    'en': (
        '<h1 style="border-bottom:none;margin-top:0;margin-bottom:0.8em;text-align:center;"> %d quotes in %d articles ',
        '<small>(The number of articles does not include articles without quotes. Duplicated quotes are counted only once.)',
        '== By article ==\n\n',
        '{| class="wikitable"\n|+\'\'\'Number of quotes by article\'\'\'\n! align="center" | Article\n! align="center" | Number of quotes\n',
        '|- align="center" \n| \'\'\'Mean\'\'\' || %0.2f\n',
        '<small>Mean excludes articles without quotes.</small>\n\n',
        '== Duplicated quotes ==\n',
        '<small>(This table gives the number of quotes that appear in more than one article. If the first field is N and the second M, it means M quotes appear N times (in N articles))</small>\n\n',
        '{| class="wikitable" style="width: 40%%"\n|+\'\'\'Number of articles where the quote appears\'\'\n! align="center" | Articlse\n! align="center" | Number of quotes\n',
        'Updated statistics')
}


def trim(s):
    return s.strip(" \t\n\r\0\x0B")


def replace_citation(piece):
    for p in piece['parts']:
        if trim(p[0].lower()) == globalvar.quote_arg or trim(p[0]) == '1' or trim(p[0]) == '':
            return p[1]


def replace_lang(piece):
    # Return second argument.
    return piece['parts'][1][1]


def replace_template(piece):
    # Return title if no arg. 
    if len(piece['parts']) == 0:
        return piece['title']

    # Else : return first arg.
    return piece['parts'][0][1]


class Global(object):
    def __init__(self):
        self.lang = None

    """Container class for global settings.
       Use of globals outside of this is to be avoided."""
    mainpage_name = None
    quotes = {}
    # List of articles without quotes.
    noquotes = []
    quote_template = 'citation'
    quote_arg = 'citation'
    known_templates = {quote_template: replace_citation, 'lang': replace_lang}
    quiet = False
    debug = False


def outputq(s, newline=True):
    if not globalvar.quiet:
        pywikibot.output('%s' % s, newline=newline)


def debug(s):
    if globalvar.debug:
        pywikibot.output('%s' % s)


def error(s):
    # Output errors to ... stdout, because pywikipedia uses stderr for "normal"
    # output. *sigh*
    pywikibot.output('ERROR: %s' % s)


def parse_templates(text):
    """Parse text (should be the beginning of a quote template) to get the
    content of the quote with all known templates substituted."""
    # Mostly adapted from <includes/Parser.php>

    # Returned text
    quote = ""
    # Built from this
    pieces = []

    stack = []
    # index in stack
    lastOpeningBrace = -1

    debug('Parsing templates')
    debug('Showing first 200 chars from text')
    #    debug('%s' % text[:200])

    i = 0
    # End when the first found template ends, i.e. when stack is empty and
    # we're not at the beginning 
    while (stack != [] or i == 0) and i < len(text):
        if lastOpeningBrace == -1:
            search = r'({{)'
        else:
            search = r'({{|}}|\|)'

        debug("searching for %s" % search)

        s = re.compile(search)
        m = s.search(text[i:])
        if not m:
            error('ERROR: pattern not found: %s' % search)
            return

        i += m.start()
        span = m.end() - m.start()

        debug('%s (%d, %d)' % (m.group(), m.start(), m.end()))
        debug('%s' % text[i:])

        if m.group() == "{{":
            debug("new template starting from %d" % i)

            stack.append({})
            lastOpeningBrace += 1

            stack[lastOpeningBrace]['start'] = i
            i += span
            stack[lastOpeningBrace]['lastPartStart'] = i
        else:
            # End of part.
            debug("part ending at %d" % i)

            part = text[stack[lastOpeningBrace]['lastPartStart']:i]

            # First part : template title.
            if not 'parts' in stack[lastOpeningBrace]:
                stack[lastOpeningBrace]['title'] = trim(part)
                stack[lastOpeningBrace]['parts'] = []
            else:
                # Argument.
                sep = part.find('=')
                if sep != -1:
                    argname = part[:sep]
                    arg = part[sep + 1:]
                else:
                    argname = ''
                    arg = part

                debug("part : (%s, %s)" % (argname, arg))

                stack[lastOpeningBrace]['parts'].append([argname, arg])
            i += span
            stack[lastOpeningBrace]['lastPartStart'] = i

        if m.group() == "}}":
            # Replace template.
            title = stack[lastOpeningBrace]['title'].lower()

            debug("template: %s" % title)

            if title in globalvar.known_templates:
                debug("calling replace_citation on quote")
                piece = globalvar.known_templates[title](stack[lastOpeningBrace])
            else:
                # Default callback.
                debug("calling replace_template on other template")
                piece = replace_template(stack[lastOpeningBrace])

                debug("template %s replaced by %s" % (stack[lastOpeningBrace]['title'], piece))

            if piece is None:
                error("Found a null piece: probably unterminated %s template!" % title)

            start = stack[lastOpeningBrace]['start']
            text = text[:start] + piece + text[i:]
            i = start + len(piece)

            del stack[lastOpeningBrace]
            lastOpeningBrace -= 1

    if lastOpeningBrace != -1:
        error('quote template not finished at end of text!')
        return

    debug('Quote : %s' % text[:i])
    return [text, i]


def prepare_text(text):
    wikilinksR = re.compile(r"^([ %!\"$&'()*,\\\-.\\/0-9:;=?@A-Z\\\\^_`a-z~\\x80-\\xFF+#]+)(?:\|(.+?))?]](.*)",
                            re.DOTALL)
    links = text.split('[[')
    # All texts before the first link.
    text = links.pop(0)
    for l in links:
        add = ""
        m = wikilinksR.match(l)
        if m:
            # [[0|1]]2 
            if m.group(2):
                add += m.group(2)
            else:
                add += m.group(1)
            if m.group(3):
                add += m.group(3)
        else:
            add += '[[' + l
        text += add
    #        debug("Add: %s" % add)
    #    debug('After :')
    #    debug('%s' % text)

    # Remove tags.
    tagsR = re.compile(r'<[^>]*>')
    text = tagsR.sub('', text)
    return text


def parse_quote(text):
    # Subst templates.
    return parse_templates(text)


def workon(page):
    if page.title() == globalvar.mainpage_name:
        return

    outputq('handling : %s' % page.title())

    try:
        text = page.get()
    except:
        return

    text = prepare_text(text)

    if not site.siteinfo['case'] == 'case-sensitive':
        pattern = '[' + re.escape(globalvar.quote_template[0].upper()) + re.escape(
            globalvar.quote_template[0].lower()) + ']' + re.escape(globalvar.quote_template[1:])
    else:
        pattern = re.escape(globalvar.quote_template)

    r = re.compile(r'{{ *(?:[Tt]emplate:|[mM][sS][gG]:)?' + pattern)

    alnum = re.compile('\W')

    matches = r.finditer(text)
    offset = 0
    n_quotes = 0

    for m in matches:
        debug('match (200) : %s' % text[m.start():m.start() + 200])
        debug('offset: %d' % offset)
        # Real start of the match.
        n_quotes += 1
        start = m.start() - offset

        if trim(text[start:]) == '':
            return
        try:
            [endtext, qlen] = parse_quote(text[start:])
        except TypeError:
            debug('Unclosed template: "%s" in "%s"' % (text[start:100], page.title()))
            return

        offset += (len(text[start:]) - len(endtext))

        quote = endtext[:qlen]
        text = text[:start] + endtext

        debug('Quote 2: %s' % quote)
        debug('Text: %s' % text)

        # Strip all non-alphanumeric chars.
        squote = alnum.sub('', quote)
        h = hash(squote)

        if h not in globalvar.quotes:
            globalvar.quotes[h] = [squote, [[quote, page]]]
        else:
            if globalvar.quotes[h][0] != squote:
                error('hash collision! %s and %s have the same hash (%d).' % (globalvar.quotes[h][0], squote, h))
                sys.exit(-1)

            globalvar.quotes[h][1].append([quote, page])

    if n_quotes == 0:
        outputq("no quotes in %s" % page.title())
        globalvar.noquotes.append(page)


def generate_output(quotes):
    # Compute (unique) quotes and duplicates
    total_count = 0
    article_count = {}
    duplicate_count = {}
    # We also want :
    #  - to print similar-but-not-equal) quotes.
    #  - to print when the same quote appears twice in an article.

    outputq('quotes : %d' % len(quotes))
    for h in quotes:
        unique_quotes = {}
        [operator.setitem(unique_quotes, i[0], []) for i in quotes[h][1] if not i[0] in unique_quotes]
        # outputq('uquotes : %s' % uquotes)

        # Get associated pages.
        for q in quotes[h][1]:
            if q[0] in unique_quotes:
                unique_quotes[q[0]].append(q[1])

        debug('increasing count by one')
        # Only increment by one, because all quotes with the same hash
        # should be similar enough to be considered identical.
        total_count += 1

        pr = False
        # Are all quotes the same?
        if len(unique_quotes) > 1:
            pr = True
            outputq('Similar quotes found :')

        articles = 0
        for q in unique_quotes:
            if pr:
                outputq('\t%s (on:' % q, newline=False)
            for a in unique_quotes[q]:
                if pr:
                    outputq(' %s' % trim(a.title()), newline=False)
                if a in article_count:
                    article_count[a] += 1
                else:
                    article_count[a] = 1
                articles += 1
            if pr:
                outputq(')')

        if articles in duplicate_count:
            duplicate_count[articles] += 1
        else:
            duplicate_count[articles] = 1

    outputq('TOTAL NUMBER OF QUOTES : %d' % total_count)
    output = msg[globalvar.lang][0] % (total_count, len(article_count))
    output += '<small style="font-size: 70%%">(%s)</small></h1>\n'
    output += msg[globalvar.lang][1]
    output += '\n\n'

    # Sort dictionary by values (number of quotes) and return list of tuples (not dict)
    article_count = sorted(article_count.items(), key=lambda x: x[1], reverse=True)

    output += msg[globalvar.lang][2]
    output += msg[globalvar.lang][3]

    # Make it Unicode because the titles will be Unicode.

    for a in article_count:
        outputq('adding to table: %s' % a[0].title())
        output += '|-\n| [[%s]] || %d\n' % (a[0].title(), a[1])
    for p in globalvar.noquotes:
        output += '|-\n| [[%s]] || 0\n' % p.title()

    mean = 0
    if len(article_count) != 0:
        mean = total_count / float(len(article_count))

    output2 = ""
    output2 += msg[globalvar.lang][4] % mean
    output2 += '|}\n\n'
    output2 += msg[globalvar.lang][5]

    output2 += msg[globalvar.lang][6]
    output2 += msg[globalvar.lang][7]
    output2 += msg[globalvar.lang][8]

    output += output2

    for a in duplicate_count:
        output += '|-\n|%d || %d\n' % (a, duplicate_count[a])
    output += '|}\n\n'

    return [output, total_count, len(article_count)]


class Main(object):
    # Options
    __start = None
    __number = None
    ## Which page generator to use
    __workonnew = False
    __catname = None
    __catrecurse = False
    __linkpagetitle = None
    __refpagetitle = None
    __textfile = None
    __pagetitles = []

    __output = None
    __outputprefix = None
    __outputarticles = 'Utilisateur:JackBot/NUMBEROFARTICLES'
    __outputquotes = None

    def parse(self):
        # Parse options

        for arg in pywikibot.handle_args():
            if arg.startswith('-ref'):
                if len(arg) == 4:
                    self.__refpagetitle = pywikibot.input('Links to which page should be processed?')
                else:
                    self.__refpagetitle = arg[5:]
            elif arg.startswith('-cat'):
                if len(arg) == 4:
                    self.__catname = pywikibot.input('Please enter the category name:')
                else:
                    self.__catname = arg[5:]
            elif arg.startswith('-subcat'):
                self.__catrecurse = True
            elif arg.startswith('-links'):
                if len(arg) == 6:
                    self.__linkpagetitle = pywikibot.input('Links from which page should be processed?')
                else:
                    self.__linkpagetitle = arg[7:]
            elif arg.startswith('-file:'):
                if len(arg) == 5:
                    self.__textfile = pywikibot.input('File to read pages from?')
                else:
                    self.__textfile = arg[6:]
            elif arg == '-new':
                self.__workonnew = True
            elif arg.startswith('-start:'):
                if len(arg) == 6:
                    self.__start = pywikibot.input('Which page to start from: ')
                else:
                    self.__start = arg[7:]
            elif arg.startswith('-number:'):
                if len(arg) == 7:
                    self.__number = int(pywikibot.input('Number of pages to parse: '))
                else:
                    self.__number = int(arg[8:])
            elif arg.startswith('-output:'):
                if len(arg) == 7:
                    self.__output = pywikibot.input('Which page to save report to: ')
                else:
                    self.__output = arg[8:]
            elif arg.startswith('-outputprefix:'):
                if len(arg) == 12:
                    self.__outputprefix = pywikibot.input('Which page to save templates to: ')
                else:
                    self.__outputprefix = arg[13:]
            elif arg.startswith('-outputquotes:'):
                if len(arg) == 12:
                    self.__outputquotes = pywikibot.input('Which page to save number of quotes to: ')
                else:
                    self.__outputquotes = arg[13:]
            elif arg.startswith('-outputarticles:'):
                if len(arg) == 14:
                    self.__outputarticles = pywikibot.input('Which page to save number of quotes to: ')
                else:
                    self.__outputarticles = arg[15:]
            elif arg.startswith('-template:'):
                if len(arg) == 9:
                    globalvar.quote_template = pywikibot.input('Which template is used for quotes?')
                else:
                    globalvar.quote_template = arg[10:]
            elif arg.startswith('-arg:'):
                if len(arg) == 4:
                    globalvar.quote_arg = pywikibot.input('Which template arg is used for quotes?')
                else:
                    globalvar.quote_arg = arg[5:]
            elif arg == '-quiet':
                globalvar.quiet = True
            elif arg == '-debug':
                globalvar.debug = True
            else:
                self.__pagetitles.append(arg)

    def generator(self):
        # Choose which generator to use according to options.

        pagegen = None

        if self.__workonnew:
            if not self.__number:
                self.__number = 500
            pagegen = pagegenerators.NewpagesPageGenerator(number=self.__number)

        elif self.__refpagetitle:
            refpage = pywikibot.Page(site, self.__refpagetitle)
            pagegen = pagegenerators.LinkedPageGenerator(refpage)

        elif self.__linkpagetitle:
            linkpage = pywikibot.Page(site, self.__linkpagetitle)
            pagegen = pagegenerators.LinkedPageGenerator(linkpage)

        elif self.__catname:
            cat = pywikibot.Category(site, 'Category:%s' % self.__catname)

            if self.__start:
                pagegen = pagegenerators.CategorizedPageGenerator(cat, recurse=self.__catrecurse, start=self.__start)
            else:
                pagegen = pagegenerators.CategorizedPageGenerator(cat, recurse=self.__catrecurse)

        elif self.__textfile:
            pagegen = pagegenerators.TextfilePageGenerator(self.__textfile)

        else:
            if not self.__start:
                self.__start = '!'
            namespace = pywikibot.Page(site, self.__start).namespace()
            start = pywikibot.Page(site, self.__start).title(withNamespace=False)
            pagegen = pagegenerators.AllpagesPageGenerator(start, namespace, includeredirects=False, site=site)
        return pagegen

    def main(self):
        # Parse command line options
        self.parse()

        # ensure that we don't try to change main page
        globalvar.mainpage_name = pywikibot.Page(pywikibot.Link("Main page_content", site)).title(withNamespace=False)

        if site.lang in msg:
            globalvar.lang = site.lang
        else:
            globalvar.lang = 'en'

        pagegen = self.generator()

        generator = None
        if self.__pagetitles:
            pages = []
            for p in self.__pagetitles:
                try:
                    pages.append(pywikibot.Page(site, p))
                except pywikibot.exceptions.NoPageError:
                    pass
            generator = pagegenerators.PreloadingGenerator(iter(pages))
        else:
            generator = pagegenerators.PreloadingGenerator(pagegen)

        for page in generator:
            workon(page)

        [output, nquotes, npages] = generate_output(globalvar.quotes)
        outputpage = self.__output
        if self.__output:
            try:
                outputpage = pywikibot.Page(site, self.__output)
                if outputpage.exists():
                    oldtext = outputpage.get()
                else:
                    oldtext = ''

                if oldtext != output:
                    output = output % time.strftime('%d/%m/%y / %H:00')
                    outputpage.put(output, comment=msg[globalvar.lang][9])
            except:
                error('Getting/Modifying page %s failed, generated output was:\n%s' % (outputpage, output))
        else:
            pywikibot.output(output)

        nquotespage = None
        narticlespage = None
        if self.__outputprefix:
            if self.__outputquotes:
                pname = self.__outputquotes
            else:
                pname = "NUMBEROFQUOTES"
            nquotespage = pywikibot.Page(site, '%s%s' % (self.__outputprefix, pname))

            if self.__outputarticles:
                pname = self.__outputarticles
            else:
                pname = "Utilisateur:JackBot/NUMBEROFARTICLES"
            narticlespage = pywikibot.Page(site, '%s%s' % (self.__outputprefix, pname))
        else:
            if self.__outputquotes:
                nquotespage = pywikibot.Page(site, '%s' % self.__outputquotes)
            if self.__outputarticles:
                narticlespage = pywikibot.Page(site, '%s' % self.__outputarticles)

        if nquotespage:
            # April fool (replace %d by %s too)
            # nquotes = hex(nquotes)
            nquotespage.put("%d" % nquotes, comment=msg[globalvar.lang][9])

        if narticlespage:
            # Same as above
            # npages = hex(npages)
            narticlespage.put("%d" % npages, comment=msg[globalvar.lang][9])


globalvar = Global()
try:
    if __name__ == "__main__":
        Main().main()
finally:
    pywikibot.stopme()

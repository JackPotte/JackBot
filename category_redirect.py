# -*- coding: utf-8 -*-
"""This bot will move pages out of redirected categories

Usage: category_redirect.py [options]

The bot will look for categories that are marked with a category redirect
template, take the first parameter of the template as the target of the
redirect, and move all pages and subcategories of the category there. It
also changes hard redirects into soft redirects, and fixes double redirects.
A log is written under <userpage>/category_redirect_log. Only category pages
that haven't been edited for a certain cooldown period (currently 7 days)
are taken into account.

"""

#
# (C) Pywikipedia team, 2008-2013
#
__version__ = '$Id$'
#
# Distributed under the terms of the MIT license.
#

import cPickle
import math
import re
import sys
import time
import traceback
from datetime import datetime, timedelta
import wikipedia as pywikibot
import pagegenerators
import catlib
import query
from pywikibot import i18n


class APIError(Exception):
    """The wiki API returned an error message."""

    def __init__(self, errordict):
        """Save error dict returned by MW API."""
        self.errors = errordict

    def __str__(self):
        return "%(code)s: %(info)s" % self.errors


class CategoryRedirectBot(object):
    def __init__(self):
        self.cooldown = 7  # days
        self.site = pywikibot.getSite()
        self.catprefix = self.site.namespace(14)+":"
        self.log_text = []
        self.edit_requests = []
        self.log_page = pywikibot.Page(self.site,
                                       u"User:%(user)s/category redirect log"
                                       % {'user': self.site.loggedInAs()})

        # Localization:
        # Category that contains all redirected category pages
        self.cat_redirect_cat = {
            'wikipedia': {
                'ar': u"تصنيف:تحويلات تصنيفات ويكيبيديا",
                'cs': u"Kategorie:Zastaralé kategorie",
                'da': "Kategori:Omdirigeringskategorier",
                'en': "Category:Wikipedia soft redirected categories",
                'es': "Categoría:Wikipedia:Categorías redirigidas",
                'fa': u"رده:رده‌های منتقل شده",
                'hu': "Kategória:Kategóriaátirányítások",
                'ja': "Category:移行中のカテゴリ",
                'no': "Kategori:Wikipedia omdirigertekategorier",
                'pl': "Kategoria:Przekierowania kategorii",
                'pt': "Categoria:!Redirecionamentos de categorias",
                'ru': "Категория:Википедия:Категории-дубликаты",
                'simple': "Category:Category redirects",
                'vi': u"Thể loại:Thể loại đổi hướng",
                'zh': u"Category:已重定向的分类",
            },
            'commons': {
                'commons': "Category:Category redirects"
            }
        }

        self.move_comment = 'category_redirect-change-category'
        self.redir_comment = 'category_redirect-add-template'
        self.dbl_redir_comment = 'category_redirect-fix-double'
        self.maint_comment = 'category_redirect-comment'
        self.edit_request_text = i18n.twtranslate(
            self.site.lang, 'category_redirect-edit-request') + u'\n~~~~'
        self.edit_request_item = i18n.twtranslate(
            self.site.lang, 'category_redirect-edit-request-item')

    def change_category(self, article, oldCat, newCat, comment=None,
                        sortKey=None):
        """Given an article in category oldCat, moves it to category newCat.
        Moves subcategories of oldCat as well. oldCat and newCat should be
        Category objects. If newCat is None, the category will be removed.

        This is a copy of portions of [old] catlib.change_category(), with
        some changes.

        """
        oldtext = article.get(get_redirect=True, force=True)
        if newCat in article.categories() or newCat == article:
            newtext = pywikibot.replaceCategoryInPlace(oldtext, oldCat, None,
                                                       site=self.site)
        else:
            newtext = pywikibot.replaceCategoryInPlace(oldtext, oldCat, newCat,
                                                       site=self.site)
        try:
            # even if no changes, still save the page, in case it needs
            # an update due to changes in a transcluded template
            article.put(newtext, comment)
            if newtext == oldtext:
                pywikibot.output(u'No changes made in page %s.'
                                 % article.title(asLink=True))
                return False
            return True
        except pywikibot.EditConflict:
            pywikibot.output(u'Skipping %s because of edit conflict'
                             % article.title(asLink=True))
        except pywikibot.LockedPage:
            pywikibot.output(u'Skipping locked page %s'
                             % article.title(asLink=True))
            self.edit_requests.append({
                'title': article.title(asLink=True, textlink=True),
                'oldcat': oldCat.title(asLink=True, textlink=True),
                'newcat': newCat.title(asLink=True, textlink=True)})
        except pywikibot.SpamfilterError, error:
            pywikibot.output(
                u'Changing page %s blocked by spam filter (URL=%s)'
                % (article.title(asLink=True), error.url))
        except pywikibot.NoUsername:
            pywikibot.output(
                u"Page %s not saved; sysop privileges required."
                % article.title(asLink=True))
            self.edit_requests.append({
                'title': article.title(asLink=True, textlink=True),
                'oldcat': oldCat.title(asLink=True, textlink=True),
                'newcat': newCat.title(asLink=True, textlink=True)})
        except pywikibot.PageNotSaved, error:
            pywikibot.output(u"Saving page %s failed: %s"
                             % (article.title(asLink=True), error.message))
        return False

    def move_contents(self, oldCatTitle, newCatTitle, editSummary):
        """The worker function that moves pages out of oldCat into newCat"""
        while True:
            try:
                oldCat = catlib.Category(self.site,
                                         self.catprefix + oldCatTitle)
                newCat = catlib.Category(self.site,
                                         self.catprefix + newCatTitle)

                oldCatLink = oldCat.title()
                newCatLink = newCat.title()
                comment = editSummary % locals()
                # Move articles
                found, moved = 0, 0
                for result in self.query_results(list="categorymembers",
                                                 cmtitle=oldCat.title(),
                                                 cmprop="title|sortkey",
                                                 cmlimit="max"):
                    found += len(result['categorymembers'])
                    for item in result['categorymembers']:
                        article = pywikibot.Page(self.site, item['title'])
                        changed = self.change_category(article, oldCat, newCat,
                                                       comment=comment)
                        if changed:
                            moved += 1

                # pass 2: look for template doc pages
                for result in self.query_results(list="categorymembers",
                                                 cmtitle=oldCat.title(),
                                                 cmprop="title|sortkey",
                                                 cmnamespace="10",
                                                 cmlimit="max"):
                    for item in result['categorymembers']:
                        doc = pywikibot.Page(self.site, item['title']+"/doc")
                        try:
                            old_text = doc.get()
                        except pywikibot.Error:
                            continue
                        changed = self.change_category(doc, oldCat, newCat,
                                                       comment=comment)
                        if changed:
                            moved += 1

                if found:
                    pywikibot.output(u"%s: %s found, %s moved"
                                     % (oldCat.title(), found, moved))
                return (found, moved)
            except pywikibot.ServerError:
                pywikibot.output(u"Server error: retrying in 5 seconds...")
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                raise
            except:
                return (None, None)

    def readyToEdit(self, cat):
        """Return True if cat not edited during cooldown period, else False."""
        dateformat = "%Y%m%d%H%M%S"
        today = datetime.now()
        deadline = today + timedelta(days=-self.cooldown)
        if cat.editTime() is None:
            raise RuntimeError
        return (deadline.strftime(dateformat) > cat.editTime())

    def query_results(self, **data):
        """Iterate results from API action=query, using data as parameters."""
        querydata = {'action': 'query',
                     'maxlag': str(pywikibot.config.maxlag)}
        querydata = query.CombineParams(querydata, data)
        if not "action" in querydata or not querydata['action'] == 'query':
            raise ValueError(
                "query_results: 'action' set to value other than 'query'")
        waited = 0
        while True:
            try:
                result = query.GetData(querydata, self.site)
                #if data.startswith(u"unknown_action"):
                #    e = {'code': data[:14], 'info': data[16:]}
                #    raise APIError(e)
            except pywikibot.ServerError:
                pywikibot.output(u"Wikimedia Server Error; retrying...")
                time.sleep(5)
                continue
            except ValueError:
                # if the result isn't valid JSON, there must be a server
                # problem.  Wait a few seconds and try again
                # WARNING: if the server is down, this could
                # cause an infinite loop
                pywikibot.output(u"Invalid API response received; retrying...")
                time.sleep(5)
                continue
            if type(result) is dict and "error" in result:
                if result['error']['code'] == "maxlag":
                    print "Pausing due to server lag.\r",
                    time.sleep(5)
                    waited += 5
                    if waited % 30 == 0:
                        pywikibot.output(
                            u"(Waited %i seconds due to server lag.)" % waited)
                    continue
                else:
                    raise APIError(result['error'])
            waited = 0
            if type(result) is list:
                # query returned no results
                return
            assert type(result) is dict, \
                   "Unexpected result of type '%s' received." % type(result)
            if "query" not in result:
                # query returned no results
                return
            yield result['query']
            if 'query-continue' in result:
                assert len(result['query-continue'].keys()) == 1, \
                       "More than one query-continue key returned: %s" \
                       % result['query-continue'].keys()
                query_type = result['query-continue'].keys()[0]
                assert (query_type in querydata.keys()
                        or query_type in querydata.values()), \
                       "Site returned unknown query-continue type '%s'" \
                       % query_type
                querydata.update(result['query-continue'][query_type])
            else:
                return

    def get_log_text(self):
        """Rotate log text and return the most recent text."""
        LOG_SIZE = 7  # Number of items to keep in active log
        try:
            log_text = self.log_page.get()
        except pywikibot.NoPage:
            log_text = u""
        log_items = {}
        header = None
        for line in log_text.splitlines():
            if line.startswith("==") and line.endswith("=="):
                header = line[2:-2].strip()
            if header is not None:
                log_items.setdefault(header, [])
                log_items[header].append(line)
        all_log_text = log_text
        if len(log_items) < LOG_SIZE:
            return log_text
        # sort by keys and keep the first (LOG_SIZE-1) values
        keep = [text for (key, text) in
                sorted(log_items.items(), reverse=True)[:LOG_SIZE-1]]
        log_text = "\n".join("\n".join(line for line in text) for text in keep)
        # get permalink to older logs
        try:
            history = self.log_page.getVersionHistory(revCount=LOG_SIZE)
            # get the id of the newest log being archived
            rotate_revid = history[-1][0]
            # append permalink
            log_text = log_text + \
                       "\n\n'''[%s Older logs]'''" \
                       % self.log_page.permalink(oldid=rotate_revid)
        except IndexError:
            # don't die if getVersionHistory fails (again)
            return all_log_text
        return log_text

    def run(self):
        """Run the bot"""
        user = self.site.loggedInAs()
        redirect_magicwords = ["redirect"]
        other_words = self.site.redirect()
        if other_words:
            redirect_magicwords.extend(other_words)
        problems = []

        l = time.localtime()
        today = "%04d-%02d-%02d" % l[:3]
        edit_request_page = pywikibot.Page(
            self.site,
            u"User:%(user)s/category edit requests"
            % locals())
        datafile = pywikibot.config.datafilepath("%s-catmovebot-data"
                                                 % self.site.dbName())
        try:
            inp = open(datafile, "rb")
            record = cPickle.load(inp)
            inp.close()
        except IOError:
            record = {}
        if record:
            cPickle.dump(record, open(datafile + ".bak", "wb"))

        try:
            template_list = self.site.family.category_redirect_templates[
                self.site.lang]
        except KeyError:
            pywikibot.output(u"No redirect templates defined for %s"
                             % self.site.sitename())
            return
        # regex to match soft category redirects
        #  note that any templates containing optional "category:" are
        #  incorrect and will be fixed by the bot
        template_regex = re.compile(
            ur"""{{\s*(?:%(prefix)s\s*:\s*)?  # optional "template:"
                      (?:%(template)s)\s*\|   # catredir template name
                      (\s*%(catns)s\s*:\s*)?  # optional "category:"
                      ([^|}]+)                # redirect target cat
                      (?:\|[^|}]*)*}}         # optional arguments 2+, ignored
              """ % {'prefix': self.site.namespace(10).lower(),
                     'template': "|".join(item.replace(" ", "[ _]+")
                                          for item in template_list),
                     'catns': self.site.namespace(14)},
            re.I | re.X)

        # check for hard-redirected categories that are not already marked
        # with an appropriate template
        comment = i18n.twtranslate(self.site.lang, self.redir_comment)
        for result in self.query_results(list='allpages',
                                         apnamespace='14',  # Category:
                                         apfrom='!',
                                         apfilterredir='redirects',
                                         aplimit='max'):
            gen = (pywikibot.Page(self.site, page_item['title'])
                   for page_item in result['allpages'])
            # gen yields all hard redirect pages in namespace 14
            for page in pagegenerators.PreloadingGenerator(gen, 120):
                if page.isCategoryRedirect():
                    # this is already a soft-redirect, so skip it (for now)
                    continue
                target = page.getRedirectTarget()
                if target.namespace() == 14:
                    # this is a hard-redirect to a category page
                    newtext = (u"{{%(template)s|%(cat)s}}"
                               % {'cat': target.title(withNamespace=False),
                                  'template': template_list[0]})
                    try:
                        page.put(newtext, comment, minorEdit=True)
                        self.log_text.append(u"* Added {{tl|%s}} to %s"
                                             % (template_list[0],
                                                page.title(asLink=True,
                                                           textlink=True)))
                    except pywikibot.Error, e:
                        self.log_text.append(
                            u"* Failed to add {{tl|%s}} to %s (%s)"
                            % (template_list[0],
                               page.title(asLink=True, textlink=True), e))
                else:
                    problems.append(
                        u"# %s is a hard redirect to %s"
                        % (page.title(asLink=True, textlink=True),
                           target.title(asLink=True, textlink=True)))

        pywikibot.output("Done checking hard-redirect category pages.")

        comment = i18n.twtranslate(self.site.lang, self.move_comment)
        scan_data = {
            u'action': 'query',
            u'list': 'embeddedin',
            u'einamespace': '14',   # Category:
            u'eilimit': 'max',
            u'format': 'json'
        }
        counts, destmap, catmap = {}, {}, {}
        catlist, catpages, nonemptypages = [], [], []
        target = self.cat_redirect_cat[self.site.family.name][self.site.lang]

        # get a list of all members of the category-redirect category
        for result in self.query_results(generator=u'categorymembers',
                                         gcmtitle=target,
                                         gcmnamespace=u'14',  # CATEGORY
                                         gcmlimit=u'max',
                                         prop='info|categoryinfo'):
            for catdata in result['pages'].values():
                thispage = pywikibot.Page(self.site, catdata['title'])
                catpages.append(thispage)
                if 'categoryinfo' in catdata \
                        and catdata['categoryinfo']['size'] != "0":
                    # save those categories that have contents
                    nonemptypages.append(thispage)

        # preload the category pages for redirected categories
        pywikibot.output(u"")
        pywikibot.output(u"Preloading %s category redirect pages"
                         % len(catpages))
        for cat in pagegenerators.PreloadingGenerator(catpages, 120):
            cat_title = cat.title(withNamespace=False)
            if "category redirect" in cat_title:
                self.log_text.append(u"* Ignoring %s"
                                     % cat.title(asLink=True, textlink=True))
                continue
            try:
                text = cat.get(get_redirect=True)
            except pywikibot.Error:
                self.log_text.append(u"* Could not load %s; ignoring"
                                     % cat.title(asLink=True, textlink=True))
                continue
            if not cat.isCategoryRedirect():
                self.log_text.append(u"* False positive: %s"
                                     % cat.title(asLink=True, textlink=True))
                continue
            if cat_title not in record:
                # make sure every redirect has a record entry
                record[cat_title] = {today: None}
            catlist.append(cat)
            target = cat.getCategoryRedirectTarget()
            destination = target.title(withNamespace=False)
            destmap.setdefault(target, []).append(cat)
            catmap[cat] = destination
##            if match.group(1):
##                # category redirect target starts with "Category:" - fix it
##                text = text[ :match.start(1)] + text[match.end(1): ]
##                try:
##                    cat.put(text,
##                            u"Robot: fixing category redirect parameter format")
##                    self.log_text.append(
##                        u"* Removed category prefix from parameter in %s"
##                         % cat.aslink(textlink=True))
##                except pywikibot.Error:
##                    self.log_text.append(
##                        u"* Unable to save changes to %s"
##                         % cat.aslink(textlink=True))

        # delete record entries for non-existent categories
        for cat_name in list(record.keys()):
            if catlib.Category(self.site,
                               self.catprefix+cat_name) not in catmap:
                del record[cat_name]

        pywikibot.output(u"")
        pywikibot.output(u"Checking %s destination categories" % len(destmap))
        for dest in pagegenerators.PreloadingGenerator(destmap.keys(), 120):
            if not dest.exists():
                for d in destmap[dest]:
                    problems.append("# %s redirects to %s"
                                    % (d.title(asLink=True, textlink=True),
                                       dest.title(asLink=True, textlink=True)))
                    catlist.remove(d)
                    # do a null edit on d to make it appear in the
                    # "needs repair" category (if this wiki has one)
                    try:
                        d.put(d.get(get_redirect=True))
                    except:
                        pass
            if dest in catlist:
                for d in destmap[dest]:
                    # is catmap[dest] also a redirect?
                    newcat = catlib.Category(self.site,
                                             self.catprefix+catmap[dest])
                    while newcat in catlist:
                        if newcat == d or newcat == dest:
                            self.log_text.append(u"* Redirect loop from %s"
                                                 % newcat.title(asLink=True,
                                                                textlink=True))
                            break
                        newcat = catlib.Category(self.site,
                                                 self.catprefix+catmap[newcat])
                    else:
                        self.log_text.append(
                            u"* Fixed double-redirect: %s -> %s -> %s"
                            % (d.title(asLink=True, textlink=True),
                               dest.title(asLink=True, textlink=True),
                               newcat.title(asLink=True, textlink=True)))
                        oldtext = d.get(get_redirect=True)
                        # remove the old redirect from the old text,
                        # leaving behind any non-redirect text
                        oldtext = template_regex.sub("", oldtext)
                        newtext = (u"{{%(redirtemp)s|%(ncat)s}}"
                                   % {'redirtemp': template_list[0],
                                      'ncat': newcat.title(
                                          withNamespace=False)})
                        newtext = newtext + oldtext.strip()
                        try:
                            d.put(newtext,
                                  i18n.twtranslate(self.site.lang,
                                                   self.dbl_redir_comment),
                                  minorEdit=True)
                        except pywikibot.Error, e:
                            self.log_text.append("** Failed: %s" % str(e))

        # only scan those pages that have contents (nonemptypages)
        # and that haven't been removed from catlist as broken redirects
        cats_to_empty = set(catlist) & set(nonemptypages)
        pywikibot.output(u"")
        pywikibot.output(u"Moving pages out of %s redirected categories."
                         % len(cats_to_empty))
#        thread_limit = int(math.log(len(cats_to_empty), 8) + 1)
#        threadpool = ThreadList(limit=1)    # disabling multi-threads

        for cat in cats_to_empty:
            cat_title = cat.title(withNamespace=False)
            if not self.readyToEdit(cat):
                counts[cat_title] = None
                self.log_text.append(u"* Skipping %s; in cooldown period."
                                     % cat.title(asLink=True, textlink=True))
                continue
            found, moved = self.move_contents(cat_title, catmap[cat],
                                              editSummary=comment)
            if found is None:
                self.log_text.append(
                    u"* [[:%s%s]]: error in move_contents"
                    % (self.catprefix, cat_title))
            elif found:
                record[cat_title][today] = found
                self.log_text.append(
                    u"* [[:%s%s]]: %d found, %d moved"
                    % (self.catprefix, cat_title, found, moved))
            counts[cat_title] = found

        cPickle.dump(record, open(datafile, "wb"))

        pywikibot.setAction(i18n.twtranslate(self.site.lang,
                                             self.maint_comment))
        self.log_text.sort()
        problems.sort()
        self.log_page.put(u"\n== %i-%02i-%02iT%02i:%02i:%02iZ ==\n"
                          % time.gmtime()[:6]
                          + u"\n".join(self.log_text)
                          + u"\n" + u"\n".join(problems)
                          + u"\n" + self.get_log_text())
        if self.edit_requests:
            edit_request_page.put(self.edit_request_text
                                  % {'itemlist':
                                     u"\n" + u"\n".join(
                                         (self.edit_request_item % item)
                                         for item in self.edit_requests)})


def main(*args):
    global bot
    try:
        a = pywikibot.handleArgs(*args)
        if len(a) == 1:
            raise RuntimeError('Unrecognized argument "%s"' % a[0])
        elif a:
            raise RuntimeError('Unrecognized arguments: ' +
                               " ".join(('"%s"' % arg) for arg in a))
        bot = CategoryRedirectBot()
        bot.run()
    finally:
        pywikibot.stopme()

if __name__ == "__main__":
    main()

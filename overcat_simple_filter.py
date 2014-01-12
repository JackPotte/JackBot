#!/usr/bin/python
# -*- coding: utf-8  -*-
'''
A bot to do some simple over categorization filtering.
Now it uses the strategy to loop over all images in all the subcategories.
That might be a very good strategy when the parent category is very full, but later on it will become very inefficient.

'''
#
# (C) Pywikipedia bot team, 2013
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys, pywikibot, catlib, pagegenerators

def filterCategory(page):
    '''
    Loop over all subcategories of page and filter them
    '''

    # FIXME: category = catlib.Category(page) doesn't work
    site = page.site()
    title = page.title()
    category = catlib.Category(site, title)

    for subcat in category.subcategories():
        filterSubCategory(subcat, category)

def filterSubCategory(subcat, category):
    '''
    Filter category from all articles and files in subcat
    '''
    articleGen = pagegenerators.PreloadingGenerator(pagegenerators.CategorizedPageGenerator(subcat))

    for article in articleGen:
        pywikibot.output(u'Working on %s' % (article.title(),))
        articleCategories = article.categories()
        if category in articleCategories:
            articleCategories.remove(category)
            text = article.get()
            newtext = pywikibot.replaceCategoryLinks(text, articleCategories)
            pywikibot.showDiff(text, newtext)
            comment = u'Removing [[%s]]: Is already in the subcategory [[%s]]' % (category.title(), subcat.title())
            article.put(newtext, comment)
            
    
def main(args):
    generator = None;
    genFactory = pagegenerators.GeneratorFactory()

    for arg in pywikibot.handleArgs():
        genFactory.handleArg(arg)

    generator = genFactory.getCombinedGenerator()
    if not generator:
        return False

    for page in generator:
        if page.exists() and page.namespace()==14:
            filterCategory(page)
    

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        print "All done!"

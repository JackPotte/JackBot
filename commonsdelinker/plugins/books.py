__version__ = '$Id: 1f27d006d69479ccab5b8ef74b7520b21f0eb82b $'

import re

class FrPhotographie(object):
    hook = 'before_replace'
    def __init__(self, CommonsDelinker):
        self.CommonsDelinker = CommonsDelinker
    def __call__(self, page, summary, image, replacement):
        site = page.site()
        if (site.lang, site.family.name) == ('fr', 'wikibooks') and replacement.get() is None:
            if page.title().startswith('Photographie/') or page.title().startswith('Tribologie/'):
                replacement.set('IMG.svg')
                self.CommonsDelinker.output(u'%s Replaced %s by IMG.svg on %s.' % \
                    (self, image.get(), replacement.get()))

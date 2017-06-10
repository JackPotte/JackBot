__version__ = '$Id: 8dd5178c81aaec9efe3da52f9cbcf5314e3c1153 $'

class SkipPages(object):
    hook = 'before_save'
    def __init__(self, CommonsDelinker):
        self.CommonsDelinker = CommonsDelinker
    def __call__(self, page, text, new_text, summary):
        site = page.site()
        if (site.lang, site.family.name) == ('en', 'wikipedia'):
            if page.title == 'Wikipedia:Sound/list':
                return False
        return True

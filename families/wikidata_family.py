# -*- coding: utf-8  -*-

__version__ = '$Id: 6523f3b3b0fd268f6f6e9cb18463f80e179983b0 $'

import family

# The wikidata family


class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikidata'
        self.langs = {
            'wikidata': 'www.wikidata.org',
            'repo': 'wikidata-test-repo.wikimedia.de',
            'client': 'wikidata-test-client.wikimedia.de',
            'test': 'test.wikidata.org',
        }

        # Override defaults
        self.namespaces[0]['repo'] = [u'', u'Item']
        self.namespaces[1]['repo'] = [u'Talk', u'Item talk']
        del(self.namespaces[828]['_default'])
        del(self.namespaces[829]['_default'])
        self.namespaces[828]['test'] = u'Module'
        self.namespaces[829]['test'] = u'Module talk'
        self.namespaces[828]['wikidata'] = u'Module'
        self.namespaces[829]['wikidata'] = u'Module talk'

        # Most namespaces are inherited from family.Family.
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': [u'Wikidata', u'WD', 'Project'],
            'client': u'Test Wikipedia',
            'repo': u'Testwiki',
        }
        self.namespaces[5] = {
            '_default': [u'Wikidata talk', u'WT', 'Project talk'],
            'client': u'Test Wikipedia talk',
            'repo': u'Testwiki talk',
        }
        self.namespaces[102] = {
            'repo': u'Property',
        }
        self.namespaces[103] = {
            'repo': u'Property talk',
        }
        self.namespaces[120] = {
            'test': u'Property',
            'wikidata': u'Property',
        }
        self.namespaces[121] = {
            'test': u'Property talk',
            'wikidata': u'Property talk',
        }
        self.namespaces[122] = {
            'test': u'Query',
            'wikidata': u'Query',
        }
        self.namespaces[123] = {
            'test': u'Query talk',
            'wikidata': u'Query talk',
        }
        self.namespaces[1198] = {
            'repo': u'Translations',
            'test': u'Translations',
            'wikidata': u'Translations',
        }
        self.namespaces[1199] = {
            'repo': u'Translations talk',
            'test': u'Translations talk',
            'wikidata': u'Translations talk',
        }

    def scriptpath(self, code):
        if code == 'client':
            return ''
        return super(Family, self).scriptpath(code)

    def shared_data_repository(self, code, transcluded=False):
        """Always return a repository tupe. This enables testing whether
        the site opject is the repository itself, see Site.is_data_repository()

        """
        if transcluded:
            return (None, None)
        else:
            if code == 'wikidata':
                return ('wikidata', 'wikidata')
            elif code == 'test':
                return ('test', 'wikidata')
            else:
                return ('repo', 'wikidata')

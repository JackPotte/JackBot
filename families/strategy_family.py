# -*- coding: utf-8  -*-

__version__ = '$Id: 597cfb4b7f06a2046c0d4b22e3c4ccb9314fd3f4 $'

import family, config

# The Wikimedia Strategy family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'strategy'
        self.langs = {
            'strategy': 'strategy.wikimedia.org',
        }

        self.namespaces[4] = {
            '_default': [u'Strategic Planning', 'Project'],
        }
        self.namespaces[5] = {
            '_default': [u'Strategic Planning talk', 'Project talk'],
        }
        self.namespaces[106] = {
            '_default': [u'Proposal'],
        }
        self.namespaces[107] = {
            '_default': [u'Proposal talk'],
        }

        self.interwiki_forward = 'wikipedia'

    def dbName(self, code):
        return 'strategywiki_p'

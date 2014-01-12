# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The wikispecies family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'species'
        self.langs = {
            'species': 'species.wikimedia.org',
        }

        self.namespaces[4] = {
            '_default': [u'Wikispecies', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikispecies talk', self.namespaces[5]['_default']],
        }

        self.interwiki_forward = 'wikipedia'

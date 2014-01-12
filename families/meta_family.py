# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The meta wikimedia family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'meta'
        self.langs = {
            'meta': 'meta.wikimedia.org',
        }

        self.namespaces[4] = {
            '_default': [u'Meta', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Meta talk', self.namespaces[5]['_default']],
        }
        self.namespaces[200] = {
            '_default': u'Grants',
        }
        self.namespaces[201] = {
            '_default': u'Grants talk',
        }
        self.namespaces[202] = {
            '_default': u'Research',
            'meta': [u'Research', u'R'],
        }
        self.namespaces[203] = {
            '_default': u'Research talk',
        }
        self.namespaces[204] = {
            '_default': u'Participation',
        }
        self.namespaces[205] = {
            '_default': u'Participation talk',
        }
        self.namespaces[206] = {
            '_default': u'Iberocoop',
        }
        self.namespaces[207] = {
            '_default': u'Iberocoop talk',
        }
        self.namespaces[208] = {
            '_default': u'Programs',
        }
        self.namespaces[209] = {
            '_default': u'Programs talk',
        }
        self.namespaces[470] = {
            '_default': u'Schema',
        }
        self.namespaces[471] = {
            '_default': u'Schema talk',
        }
        self.namespaces[480] = {
            '_default': u'Zero',
        }
        self.namespaces[481] = {
            '_default': u'Zero talk',
        }
        self.namespaces[866] = {
            '_default': u'CNBanner',
        }
        self.namespaces[867] = {
            '_default': u'CNBanner talk',
        }
        self.namespaces[1198] = {
            '_default': u'Translations',
        }
        self.namespaces[1199] = {
            '_default': u'Translations talk',
        }

        self.interwiki_forward = 'wikipedia'
        self.cross_allowed = ['meta',]

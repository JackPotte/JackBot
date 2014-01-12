# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The MediaWiki family
# user-config.py: usernames['mediawiki']['mediawiki'] = 'User name'

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'mediawiki'

        self.langs = {
            'mediawiki': 'www.mediawiki.org',
        }

        self.namespaces[4] = {
            '_default': [u'Project', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Project talk', self.namespaces[5]['_default']],
        }
        self.namespaces[90] = {
            '_default': u'Thread',
        }
        self.namespaces[91] = {
            '_default': u'Thread talk',
        }
        self.namespaces[92] = {
            '_default': u'Summary',
        }
        self.namespaces[93] = {
            '_default': u'Summary talk',
        }
        self.namespaces[100] = {
            '_default': u'Manual',
        }
        self.namespaces[101] = {
            '_default': u'Manual talk',
        }
        self.namespaces[102] = {
            '_default': u'Extension',
        }
        self.namespaces[103] = {
            '_default': u'Extension talk',
        }
        self.namespaces[104] = {
            '_default': u'API',
        }
        self.namespaces[105] = {
            '_default': u'API talk',
        }
        self.namespaces[106] = {
            '_default': u'Skin',
        }
        self.namespaces[828] = {
            '_default': u'Module',
        }
        self.namespaces[829] = {
            '_default': u'Module talk',
        }
        self.namespaces[107] = {
            '_default': u'Skin talk',
        }
        self.namespaces[1198] = {
            '_default': u'Translations',
        }
        self.namespaces[1199] = {
            '_default': u'Translations talk',
        }
        self.namespaces[2500] = {
            '_default': u'VisualEditor',
        }
        self.namespaces[2501] = {
            '_default': u'VisualEditor talk',
        }

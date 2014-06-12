# -*- coding: utf-8 -*-
"""
This script generates a family file from a given URL.
Hackish, etc. Regexps, yes. Sorry, jwz.

"""
__version__ = "$Id$"

#
# (C) Merlijn van Deen, 2010
# (C) Pywikipedia bot team, 2010
#
# Distributed under the terms of the MIT license
#

# system imports
import sys, re
import codecs
from distutils.version import LooseVersion as V

# creating urls
from urlparse import urlparse, urljoin, ParseResult

# retrieving urls
import urllib2
from urllib2 import HTTPError
def urlopen(url):
    req = urllib2.Request(url, headers = {'User-agent': 'Pywikipedia family generator 0.1 - pywikipediabot.sf.net'})
    return urllib2.urlopen(req)

# Monkey-patching wikipediatools to prevent questions about user_config.py
import wikipediatools
wikipediatools.get_base_dir = lambda: '.'

# Set some config settings, but monkey-patch os.path.exists to prevent loading user_config.py
import os
oldexists = os.path.exists
os.path.exists = lambda x: False

import config
config.mylang = 'en'

os.path.exists = oldexists

# Now we can boot the framework
import wikipedia
import family
import externals                            # check for and install needed
externals.check_setup('BeautifulSoup.py')   #  'externals'

# parsing response data
from BeautifulSoup import BeautifulSoup

import json

class FamilyFileGenerator(object):
    def __init__(self, url=None, name=None, dointerwiki=None):
        if url == None:
            url = raw_input("Please insert URL to wiki: ")
        if name == None:
            name = raw_input("Please insert a short name (eg: freeciv): ")
        self.dointerwiki = dointerwiki
        self.base_url = url
        self.name = name

        self.wikis = {} # {'http://wiki/$1': Wiki('http://wiki/$1'), ...}
        self.langs = [] # [Wiki('http://wiki/$1'), ...]

        self.namespaces = NamespaceStorage()

    def run(self):
        print "Generating family file from %s" % self.base_url

        w = Wiki(self.base_url)
        self.wikis[w.iwpath] = w
        print
        print "=================================="
        print "api url: %s" % w.api
        print "MediaWiki version: %s" % w.version
        print "=================================="
        print

        self.getlangs(w)
        self.getapis()
        self.getnamespaces()
        self.writefile()

    def getlangs(self, w):
        print "Determining other languages...",
        try:
            iw = json.load(urlopen(w.api + "?action=query&meta=siteinfo&siprop=interwikimap&sifilteriw=local&format=json"))
            if 'error' in iw:
                raise RuntimeError ('%s - %s' % (iw['error']['code'], iw['error']['info']))
            self.langs = [wiki for wiki in iw['query']['interwikimap'] if u'language' in wiki]
            print u' '.join(sorted([wiki[u'prefix'] for wiki in self.langs]))
        except HTTPError, e:
            self.langs = []
            print e, "; continuing..."

        if len([lang for lang in self.langs if lang['url'] == w.iwpath]) == 0:
            self.langs.append({u'language': w.lang,
                               u'local': u'',
                               u'prefix': w.lang,
                               u'url': w.iwpath})

        if len(self.langs) > 1:
           if self.dointerwiki is None:
               makeiw = raw_input("\nThere are %i languages available.\nDo you want to generate interwiki links? This might take a long time. ([y]es/[N]o/[e]dit)" % len(self.langs)).lower()
           else:
               makeiw = self.dointerwiki
           
           if makeiw == "y":
               pass
           elif makeiw == "e":
               for wiki in self.langs:
                   print wiki['prefix'], wiki['url']
               do_langs = raw_input("Which languages do you want: ")
               self.langs = [wiki for wiki in self.langs if wiki['prefix'] in do_langs or wiki['url'] == w.iwpath]
           else:
               self.langs = [wiki for wiki in self.langs if wiki[u'url'] == w.iwpath]

    def getapis(self):
        print "Loading wikis... "
        for lang in self.langs:
            print "  * %s... " % (lang[u'prefix']),
            if lang[u'url'] not in self.wikis:
                try:
                    self.wikis[lang[u'url']] = Wiki(lang[u'url'])
                    print "downloaded"
                except Exception, e:
                    print e
            else:
                print "in cache"

    def getnamespaces(self):
        print "Retrieving namespaces... ",
        for key in self.wikis.keys():
            w = self.wikis[key]
            print "%s " % w.lang,
            try:
                self.namespaces.addfromwiki(w)
            except Exception, e:
                print e, (" - removing language %s" % key)
                del self.wikis[key]
        print

    def writefile(self):
        fn = "families/%s_family.py" % self.name
        print "Writing %s... " % fn
        try:
            open(fn)
            if raw_input("%s already exists. Overwrite? (y/n)" % fn).lower() == 'n':
                print "Terminating."
                sys.exit(1)
        except IOError: # file not found
            pass
        f = codecs.open(fn, 'w', 'utf-8')

        f.write("""
# -*- coding: utf-8 -*-
\"\"\"
This family file was auto-generated by $Id: da1490ea4b0b41cd8a4cb294fd450dee88814df5 $
Configuration parameters:
  url = %(url)s
  name = %(name)s

Please do not commit this to the SVN repository!
\"\"\"

import family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = '%(name)s'
        self.langs = {
""".lstrip() % {'url': self.base_url, 'name': self.name})

        for w in self.wikis.itervalues():
            f.write("            '%(lang)s': '%(hostname)s',\n" % {'lang': w.lang, 'hostname': urlparse(w.server).netloc})

        f.write("        }\n\n")

        f.write(self.namespaces.output(8))
        f.write("\n\n")

        f.write("    def scriptpath(self, code):\n")
        f.write("        return {\n")

        for w in self.wikis.itervalues():
            f.write("            '%(lang)s': '%(path)s',\n" % {'lang': w.lang, 'path': w.scriptpath})
        f.write("        }[code]\n")
        f.write("\n")

        f.write("    def version(self, code):\n")
        f.write("        return {\n")
        for w in self.wikis.itervalues():
            if w.version == None:
                f.write("            '%(lang)s': None,\n" % {'lang': w.lang})
            else:
                f.write("            '%(lang)s': u'%(ver)s',\n" % {'lang': w.lang, 'ver': w.version})
        f.write("        }[code]\n")

class NamespaceStorage(object):
    def __init__(self):
        self.nsinfo = {}
        self.f = family.Family()

    def addfromwiki(self, w):
        jdata = json.load(urlopen(w.api + "?action=query&format=json&meta=siteinfo&siprop=namespaces|namespacealiases"))
        if 'query' not in jdata:
            jdata = json.load(urlopen(w.api + "?action=query&format=json&meta=siteinfo&siprop=namespaces"))
        if 'query' not in jdata:
            jdata = {'query': {}}  # empty

        data = jdata['query']

        if 'namespaces' in data:
            for ns in data['namespaces'].itervalues():
                self.add(ns['id'], w.lang, ns['*'])
        else:
            print "\n*** Notice: cannot retrieve namespaces for %s" % w.lang

        if 'namespacealiases' in data:
            for ns in data['namespacealiases']:
                self.add(ns['id'], w.lang, ns['*'])
        else:
            print "\n*** Notice: cannot retrieve namespace aliases for %s" % w.lang

    def add(self, ns, lang, translation):
        """ Contains logic for determining whether to define a namespace or not """
        ns = int(ns)
        if ns == 0: # never translate the article namespace
            return
        try:
            if translation != self.f.namespace(lang, ns): # self.f.namespace might return KeyError itself
                raise KeyError
        except KeyError:
            self._store(ns, lang, translation)

    def _store(self, ns, lang, translation):
        """ Contains logic on how to store a translation """
        self.nsinfo.setdefault(ns, {}).setdefault(lang, []).append(translation)

    def output(self, indent):
        data = ""
        for nsid, langs in self.nsinfo.iteritems():
            data += " " * indent
            data += "self.namespaces[%(nsid)i] = self.namespaces.get(%(nsid)i, {})" % locals()
            data += "\n"
            for lang, translations in langs.iteritems():
                data += " " * indent
                data += "self.namespaces[%(nsid)i][%(lang)r] = %(translations)r" % locals()
                data += "\n"
        return data


class Wiki(object):
    REwgEnableApi = re.compile(ur'wgEnableAPI ?= ?true')
    REwgServer = re.compile(ur'wgServer ?= ?"([^"]*)"')
    REwgScriptPath = re.compile(ur'wgScriptPath ?= ?"([^"]*)"')
    REwgArticlePath = re.compile(ur'wgArticlePath ?= ?"([^"]*)"')
    REwgContentLanguage = re.compile(ur'wgContentLanguage ?= ?"([^"]*)"')
    REwgVersion = re.compile(ur'wgVersion ?= ?"([^"]*)"')

    def __init__(self, fromurl):
        self.fromurl = fromurl
        if fromurl.endswith("$1"):
          fromurl = fromurl[:-2]
        try:
            data = urlopen(fromurl).read()
        except HTTPError, e:
            if e.code != 404:
                raise
            data = e.read()
            pass

        bs = BeautifulSoup(data)
        try:
            self.version = bs.find("meta", attrs={'name': "generator"})['content'].replace("MediaWiki ", "")
        except Exception:
            self.version = "0.0"

        if V(self.version) < V("1.17.0"):
            self._parse_pre_117(data)
        else:
            self._parse_post_117(bs, fromurl)

    def _parse_pre_117(self, data):
        if not self.REwgEnableApi.search(data):
            print "*** WARNING: Api does not seem to be enabled on %s" % self.fromurl
        try:
            self.version = self.REwgVersion.search(data).groups()[0]
        except AttributeError:
            self.version = None

        self.server = self.REwgServer.search(data).groups()[0]
        self.scriptpath = self.REwgScriptPath.search(data).groups()[0]
        self.articlepath = self.REwgArticlePath.search(data).groups()[0]
        self.lang = self.REwgContentLanguage.search(data).groups()[0]

        if self.version == None:
            # try to get version using api
            try:
                d = json.load(urlopen(self.api + "?version&format=json"))
                self.version = filter(lambda x: x.startswith("MediaWiki"), [l.strip() for l in d['error']['*'].split("\n")])[0].split()[1]
            except Exception:
                pass

    def _parse_post_117(self, bs, fromurl):
        apipath = bs.find("link", rel='EditURI')['href'].split("?")[0]
        fullurl = urljoin(fromurl, apipath)
        info = json.load(urlopen(fullurl + "?action=query&meta=siteinfo&format=json"))['query']['general']

        self.server = urljoin(fromurl, info['server'])
        for item in ['scriptpath', 'articlepath', 'lang']:
            setattr(self, item, info[item])

    def __cmp__(self, other):
        return (self.server + self.scriptpath == other.server + other.scriptpath)

    def __hash__(self):
        return hash(self.server + self.scriptpath)

    @property
    def api(self):
        return self.server +  self.scriptpath + "/api.php"

    @property
    def iwpath(self):
        return self.server +  self.articlepath


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <url> <short name>" % sys.argv[0]
        print "Example: %s http://www.mywiki.bogus/wiki/Main_Page mywiki" % sys.argv[0]
        print "This will create the file families/mywiki_family.py"

    FamilyFileGenerator(*sys.argv[1:]).run()

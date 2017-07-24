#!/usr/bin/env python
# coding: utf-8
# Ce script formate les articles de Wikilivres

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# Global variables
debugLevel = 0
if len(sys.argv) > 2:
    if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
        debugLevel= 1
fileName = __file__
if debugLevel > 0: print fileName
if fileName.rfind('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
siteLanguage = fileName[:2]
if debugLevel > 1: print siteLanguage
siteFamily = fileName[3:]
siteFamily = siteFamily[:siteFamily.find('.')]
if debugLevel > 1: print siteFamily
site = pywikibot.Site(siteLanguage, siteFamily)
username = config.usernames[siteFamily][siteLanguage]

checkURL = False
fixTags = False
addCategory = False

deprecatedTags = {}
deprecatedTags['big'] = 'strong'
deprecatedTags['center'] = 'div style="text-align: center;"'
deprecatedTags['font color *= *"?'] = 'span style="color:'
deprecatedTags['font face *= *"?'] = 'span style="font-family:'
deprecatedTags['font size *= *"?\+?\-?'] = 'span style="font-size:'
#deprecatedTags['font '] = 'span ' #TODO: ajouter des ";" entre plusieurs param
deprecatedTags['strike'] = 's'
deprecatedTags['tt'] = 'code'
deprecatedTags['BIG'] = 'strong'
deprecatedTags['CENTER'] = 'div style="text-align: center;"'
deprecatedTags['FONT COLOR *= *"?'] = 'span style="color:'
deprecatedTags['FONT SIZE *= *"?\+?'] = 'span style="font-size:'
deprecatedTags['STRIKE'] = 's'
deprecatedTags['TT'] = 'code'
fontSize = {}
fontSize[1] = 0.63
fontSize[2] = 0.82
fontSize[3] = 1.0
fontSize[4] = 1.13
fontSize[5] = 1.5
fontSize[6] = 2.0
fontSize[7] = 3.0
fontColor = []
fontColor.append('black')
fontColor.append('blue')
fontColor.append('green')
fontColor.append('orange')
fontColor.append('red')
fontColor.append('white')
fontColor.append('yellow')
fontColor.append('#808080')


def modification(PageHS):
    if debugLevel > -1: print(PageHS.encode(config.console_encoding, 'replace'))
    summary = u'Formatage'
    page = Page(site, pageName)
    PageBegin = getContentFromPage(page, 'All')
    if PageBegin == 'KO' or PageBegin.find(u'{{en travaux') != -1 or PageBegin.find(u'{{En travaux') != -1: return
    PageTemp = PageBegin
    PageEnd = u''

    #https://fr.wiktionary.org/wiki/Sp%C3%A9cial:LintErrors/bogus-image-options
    badFileParameters = []
    badFileParameters.append(u'')
    for badFileParameter in badFileParameters:
        regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *' + badFileParameter + ur' *(\||\])'
        PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    # Doublons
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *thumb *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *vignette *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *thumb *(\| *vignette *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)
    regex = ur'(\[\[(Image|Fichier|File) *: *[^\]]+)\| *vignette *(\| *thumb *[\|\]])'
    PageTemp = re.sub(regex, ur'\1\3', PageTemp)

    if fixTags:
        if debugLevel > 0: print u'Remplacements des balises'
        PageTemp = PageTemp.replace(u'</br>', u'<br/>')

        #TODO: {{citation}} https://fr.wikiversity.org/w/index.php?title=Matrice%2FD%C3%A9terminant&action=historysubmit&type=revision&diff=669911&oldid=664849
        #TODO: multiparamètre
        PageTemp = PageTemp.replace('<font size="+1" color="red">', ur'<span style="font-size:0.63em; color:red;>')
        regex = ur'<font color="?([^>"]*)"?>'
        pattern = re.compile(regex, re.UNICODE)
        for match in pattern.finditer(PageTemp):
            if debugLevel > 1: print u'Remplacement de ' + match.group(0) + u' par <span style="color:' + match.group(1) + u'">'
            PageTemp = PageTemp.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
            PageTemp = PageTemp.replace('</font>', u'</span>')

        for oldTag, newTag in deprecatedTags.items():
            if debugLevel > 1: print "Clé : %s, valeur : %s." % (oldTag, newTag)
            if oldTag.find(u' ') == -1:
                closingOldTag = oldTag
            else:
                closingOldTag = oldTag[:oldTag.find(u' ')]
            if newTag.find(u' ') == -1:
                closingNewTag = newTag
            else:
                closingNewTag = newTag[:newTag.find(u' ')]
            #regex = ur'<' + oldTag + ur'([^>]*)>([^\n]*)</' + closingOldTag + '>' # bug https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:-flex-nom-fam-/Documentation&diff=prev&oldid=24027702
            regex = ur'< *' + oldTag + ur'([^>]*) *>'
            if re.search(regex, PageTemp):
                summary = summary + u', ajout de ' + newTag
                #PageTemp = re.sub(regex, ur'<' + newTag + ur'\1>', PageTemp)
                pattern = re.compile(regex, re.UNICODE)
                for match in pattern.finditer(PageTemp):
                    if debugLevel > 0: print str(match.group(1))
                    if newTag.find(u'font-size') != -1:
                        size = match.group(1).replace('"', '')
                        try:
                            size = int(size)
                            if size > 7: size = 7
                            openingTag = newTag + str(fontSize[size]) + ur'em"'
                        except ValueError:
                            openingTag = newTag + size + '"'
                    else:
                        openingTag = newTag + match.group(1)
                    PageTemp = PageTemp.replace(match.group(0), ur'<' + openingTag + ur'>')

            regex = ur'</ *' + closingOldTag + ' *>'
            PageTemp = re.sub(regex, ur'</' + closingNewTag + '>', PageTemp)
        PageTemp = PageTemp.replace('<strong">', ur'<strong>')
        PageTemp = PageTemp.replace('<s">', ur'<s>')
        PageTemp = PageTemp.replace('<code">', ur'<code>')
        PageTemp = PageTemp.replace(';"">', ur';">')

        # Fix
        regex = ur'<span style="font\-size:([a-z]+)>'
        pattern = re.compile(regex, re.UNICODE)
        for match in pattern.finditer(PageTemp):
            #summary = summary + u', correction de color'
            PageTemp = PageTemp.replace(match.group(0), u'<span style="color:' + match.group(1) + u'">')
        PageTemp = PageTemp.replace('</font>', u'</span>')
        PageTemp = PageTemp.replace('</font>'.upper(), u'</span>')

        regex = ur'<span style="font\-size:(#[0-9]+)"?>'
        s = re.search(regex, PageTemp)
        if s:
            summary = summary + u', correction de color'
            PageTemp = re.sub(regex, ur'<span style="color:' + s.group(1) + ur'">', PageTemp)

        regex = ur'<span style="text\-size:([0-9]+)"?>'
        s = re.search(regex, PageTemp)
        if s:
            summary = summary + u', correction de font-size'
            PageTemp = re.sub(regex, ur'<span style="font-size:' + str(fontSize[int(s.group(1))]) + ur'em">', PageTemp)

        # Fix :
        regex = ur'(<span style="font\-size:[0-9]+px;">)[0-9]+px</span>([^<]*)</strong></strong>'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1 \2</span>', PageTemp)

        PageTemp = PageTemp.replace(u'<strong><strong><strong><strong><strong><strong>', u'<span style="font-size:75px;">')
        PageTemp = PageTemp.replace(u'<strong><strong><strong><strong><strong>', u'<span style="font-size:50px;">')
        PageTemp = PageTemp.replace(u'<strong><strong><strong><strong>', u'<span style="font-size:40px;">')
        PageTemp = PageTemp.replace(u'<strong><strong><strong>', u'<span style="font-size:25px;">')
        PageTemp = PageTemp.replace(u'<strong><strong>', u'<span style="font-size:20px;">')
        PageTemp = re.sub(ur'</strong></strong></strong></strong></strong></strong>', ur'</span>', PageTemp)
        PageTemp = re.sub(ur'</strong></strong></strong></strong></strong>', ur'</span>', PageTemp)
        PageTemp = re.sub(ur'</strong></strong></strong></strong>', ur'</span>', PageTemp)
        PageTemp = re.sub(ur'</strong></strong></strong>', ur'</span>', PageTemp)
        PageTemp = re.sub(ur'</strong></strong>', ur'</span>', PageTemp)
        regex = ur'<strong>([^<]*)</span>'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'<strong>\1</strong>', PageTemp)
        regex = ur'<strong><span ([^<]*)</span></span>'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'<strong><span \1</span></strong>', PageTemp)
        #PageTemp = re.sub(ur'</span></span>', ur'</span>', PageTemp)

        regex = ur'(\|(ar|fa)(\|flexion)*}} *===\n)<span style *= *"font\-size:[0-9\.]*em">\'\'\'([^\']*)\'\'\'</span>'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"\1'''{{Arab|\4}}'''", PageTemp)
        PageTemp = PageTemp.replace(u'[[Category:', u'[[Catégorie:')

    PageTemp = PageTemp.replace(u'<source lang="html4strict">', u'<source lang="html">')


    # Templates
    oldTemplates = []
    oldTemplates.append(u'lienDePage') # TODO

    regex = ur'({{[a|A]utres projets[^}]*)\|noclear *= *1'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1', PageTemp)
    if debugLevel > 1: raw_input(PageTemp.encode(config.console_encoding, 'replace'))

    if page.namespace() == 0:
        # Traitement des modèles
        regex = ur'\{\{[P|p]ortail([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des portails'
            PageTemp = re.sub(regex, ur'', PageTemp)
        regex = ur'\{\{[P|p]alette([^\}]*)\}\}'
        if re.search(regex, PageTemp):
            summary += ', retrait des palettes'
            PageTemp = re.sub(regex, ur'', PageTemp)
        PageTemp = PageTemp.replace(u'{{PDC}}', u'profondeur de champ')
        PageTemp = PageTemp.replace(u'{{reflist}}', u'{{Références}}')
        PageTemp = PageTemp.replace(u'{{Reflist}}', u'{{Références}}')

        PageTemp = PageTemp.replace(u'[[Catégorie:{{PAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'[[Catégorie:{{BASEPAGENAME}}|{{SUBPAGENAME}}]]', u'{{AutoCat}}')
        PageTemp = PageTemp.replace(u'{{BookCat}}', u'{{AutoCat}}')
        if addCategory:
            if PageTemp.find(u'{{AutoCat}}') == -1 and trim(PageTemp) != '':
                PageTemp = PageTemp + u'\n\n{{AutoCat}}'

        regex = ur'\(*ISBN +([0-9\-]+)\)*'
        if re.search(regex, PageTemp):
            if debugLevel > 0: u'ISBN'
            PageTemp = re.sub(regex, ur'{{ISBN|\1}}', PageTemp)
            summary += ', ajout de {{ISBN}}'

        # Traitement des hyperliens
        if checkURL: PageTemp = hyperlynx(PageTemp)

        # Clés de tri pour les noms propres
        if PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')]
            PageTemp = PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]'):PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie')] + PageTemp[PageTemp.find(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}]]')+len(u'[[Catégorie:Personnalités de la photographie|{{SUBPAGENAME}}'):]
        '''ne convient pas pour les biographies https://fr.wikibooks.org/w/index.php?title=Photographie/Personnalit%C3%A9s/B/Pierre_Berdoy&diff=prev&oldid=526479
        regex = ur'()\n{{DEFAULTSORT[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'()\n{{defaultsort[^}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        '''

    PageEnd = PageEnd + PageTemp
    if PageEnd != PageBegin:
        PageTemp = PageTemp.replace(u'<references/>', u'{{Références}}')
        PageTemp = PageTemp.replace(u'<references />', u'{{Références}}')
        sauvegarde(page, PageEnd, summary)


def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def getWiki(language = 'fr', family = 'wiktionary'):
    if debugLevel > 1: print u'get ' + language + u'.' + family
    return pywikibot.Site(language, family)

def getContentFromPageName(pageName, allowedNamespaces = None):
    page = Page(site, pageName)
    return getContentFromPage(page, allowedNamespaces)

def getContentFromPage(page, allowedNamespaces = None):
    PageBegin = u''
    if page.exists():
        if type(allowedNamespaces) == type([]): #'list'
            if debugLevel > 1: print u' namespace : ' + str(page.namespace())
            condition = page.namespace() in allowedNamespaces
        elif allowedNamespaces == 'All':
            if debugLevel > 1: print u' all namespaces'
            condition = True
        else:
            if debugLevel > 1: print u' content namespaces'
            condition = page.namespace() in [0, 12, 14, 100] or page.title().find(username) != -1
        if condition:
            try:
                PageBegin = page.get()
            except pywikibot.exceptions.BadTitle:
                if debugLevel > 0: print u'IsRedirect l 5658'
                return 'KO'
            except pywikibot.exceptions.IsRedirectPage:
                if debugLevel > 0: print u'IsRedirect l 5662'
                if page.namespace() == 'Template:':
                    PageBegin = page.get(get_redirect=True)
                    if PageBegin[:len(u'#REDIRECT')] == u'#REDIRECT':
                        regex = ur'\[\[([^\]]+)\]\]'
                        s = re.search(regex, PageBegin)
                        if s:
                            PageBegin = getContentFromPageName(s.group(1), allowedNamespaces = allowedNamespaces)
                        else:
                            return 'KO'
                    else:
                        return 'KO'
                else:
                    return 'KO'
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u'NoPage l 5665'
                return 'KO'
            except pywikibot.exceptions.ServerError:
                if debugLevel > 0: print u'NoPage l 5668'
                return 'KO'
        else:
            if debugLevel > 0: print u'Forbidden namespace l 5671'
            return 'KO'
    else:
        if debugLevel > 0: print u'No page l 5674'
        return 'KO'

    return PageBegin

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    if source:
        PagesHS = open(source, 'r')
        while 1:
            PageHS = PagesHS.readline()
            fin = PageHS.find("\t")
            PageHS = PageHS[0:fin]
            if PageHS == '': break
            if PageHS.find(u'[[') != -1:
                PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
            if PageHS.find(u']]') != -1:
                PageHS = PageHS[0:PageHS.find(u']]')]
            modification(PageHS)
        PagesHS.close()

# Lecture du dump
def crawlerXML(source, regex = u''):
    if debugLevel > 1: print u'crawlerXML'
    if source:
        from pywikibot import xmlreader
        dump = xmlreader.XmlDump(source)
        parser = dump.parse()
        outPutFile = open('src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt', 'a')

        for entry in parser:
            PageTemp = entry.text

            if regex != str(''):
                if re.search(regex, PageTemp):
                    outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

            else:
                if debugLevel > 1: print u' balises HTML désuètes'
                for deprecatedTag in deprecatedTags.keys():
                    if PageTemp.find(u'<' + deprecatedTag) != -1:
                        outPutFile.write((entry.title + '\n').encode(config.console_encoding, 'replace'))

        outPutFile.close()
 
# Traitement d'une catégorie
def crawlerCat(category, recursif, apres):
    modifier = u'False'
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    #gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) HS sur Commons
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'
    if recursif == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            if subcategory.title().find(u'.ogg') == -1 and subcategory.title().find(u'spoken') == -1 and subcategory.title().find(u'Wikipedia') == -1 and subcategory.title().find(u'Wikinews') == -1:
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                    modification(Page.title())

def crawlerCat2(category, recursif, apres):
    import pywikibot
    from pywikibot import pagegenerators
    modifier = u'False'
    cat = pywikibot.Category(site, category)    # 'module' object has no attribute 'Category'
    gen =  pagegenerators.CategorizedPageGenerator(cat)
    for Page in gen:
        modification(Page.title())
    if recursif == True:
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
            if subcategory.title().find(u'.ogg') == -1 and subcategory.title().find(u'spoken') == -1 and subcategory.title().find(u'Wikipedia') == -1 and subcategory.title().find(u'Wikinews') == -1:
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                    modification(Page.title())

# Traitement des pages liées
def crawlerLink(pagename, apres):
    modifier = u'False'
    #pagename = unicode(arg[len('-links:'):], 'utf-8')
    page = pywikibot.Page(site, pagename)
    gen = pagegenerators.ReferringPageGenerator(page)
    gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print(Page.title().encode(config.console_encoding, 'replace'))
        if not apres or apres == u'' or modifier == u'True':
            modification(Page.title()) #crawlerLink(Page.title())
        elif Page.title() == apres:
            modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
    modifier = u'False'
    cat = catlib.Category(site, pagename)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        page = pywikibot.Page(site, Page.title())
        gen = pagegenerators.ReferringPageGenerator(page)
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
        for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
            #print(Page.title().encode(config.console_encoding, 'replace'))
            if not apres or apres == u'' or modifier == u'True':
                modification(PageLiee.title()) #crawlerLink(Page.title())
            elif PageLiee.title() == apres:
                modifier = u'True'
                
# Traitement d'une recherche
def crawlerSearch(pagename):
    gen = pagegenerators.SearchPageGenerator(pagename, site=site, namespaces=6)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Traitement des modifications récentes
def crawlerRC():
    gen = pagegenerators.RecentchangesPageGenerator()
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Traitement des modifications d'un compte
def crawlerUser(username):
    gen = pagegenerators.UserContributionsGenerator(username)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        modification(Page.title())

# Toutes les redirections
def crawlerRedirects():
    for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
        modification(Page.title())    
                                        
# Traitement de toutes les pages du site
def crawlerAll(start):
    gen = pagegenerators.AllpagesPageGenerator(start, namespace=0, includeredirects=False)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print (Page.title().encode(config.console_encoding, 'replace'))
        modification(Page.title())

def crawlerSpecialLint():
    page = pywikibot.Page(site, u'Spécial:ApiSandbox')
    raw_input(page._get_parsed_page())  # WARNING: API error pagecannotexist: Namespace doesn't allow actual pages.
    #modification(Page.title())

def crawlerSpecialLint2():
    predata = { # https://fr.wiktionary.org/wiki/Sp%C3%A9cial:ApiSandbox#action=query&format=rawfm&prop=info&list=linterrors&inprop=url&lntcategories=obsolete-tag&lntlimit=5000&lntnamespace=10
       'action': 'query',
       'format': 'json',
       'prop': 'info',
       'list': 'linterrors',
       'inprop': 'url',
       'lntcategories': 'obsolete-tag',
       'lntlimit': '5000',
       'lntnamespace': '10'
    }
    data = site.postForm(site.apipath(), predata) # WARNING: Http response status 405
    if debugLevel > 0: raw_input(data)
    text = simplejson.loads(data)['parse']['text']['*'] # ValueError: No JSON object could be decode
    if debugLevel > 0: raw_input(text)
    #modification(Page.title())

def crawlerSpecialNotCategorized():
    addCategory = True
    for Page in site.uncategorizedpages():
        #print (Page.title().encode(config.console_encoding, 'replace'))
        modification(Page.title())


# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
    page = Page(site,u'User talk:' + username)
    if page.exists():
        PageTemp = u''
        try:
            PageTemp = page.get()
        except pywikibot.exceptions.NoPage: return
        except pywikibot.exceptions.IsRedirectPage: return
        except pywikibot.exceptions.LockedPage: return
        except pywikibot.exceptions.ServerError: return
        except pywikibot.exceptions.BadTitle: return
        except pywikibot.EditConflict: return
        if PageTemp != u"{{/Stop}}":
            pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
            exit(0)

def sauvegarde(PageCourante, Contenu, summary):
    result = "ok"
    if debugLevel > 0:
        if len(Contenu) < 6000:
            print(Contenu.encode(config.console_encoding, 'replace'))
        else:
            taille = 3000
            print(Contenu[:taille].encode(config.console_encoding, 'replace'))
            print u'\n[...]\n'
            print(Contenu[len(Contenu)-taille:].encode(config.console_encoding, 'replace'))
        result = raw_input((u'Sauvegarder [['+PageCourante.title()+u']] ? (o/n) ').encode('utf-8'))
    if result != "n" and result != "no" and result != "non":
        if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
        if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
        try:
            PageCourante.put(Contenu, summary)
        except pywikibot.exceptions.NoPage: 
            print "NoPage en sauvegarde"
            return
        except pywikibot.exceptions.IsRedirectPage: 
            print "IsRedirectPage en sauvegarde"
            return
        except pywikibot.exceptions.LockedPage: 
            print "LockedPage en sauvegarde"
            return
        except pywikibot.EditConflict: 
            print "EditConflict en sauvegarde"
            return
        except pywikibot.exceptions.ServerError: 
            print "ServerError en sauvegarde"
            return
        except pywikibot.exceptions.BadTitle: 
            print "BadTitle en sauvegarde"
            return
        except AttributeError:
            print "AttributeError en sauvegarde"
            return


def main(*args):
    if len(sys.argv) > 1:
        if sys.argv[1] == u'test':
            modification(u'User:' + username + u'/test')
        elif sys.argv[1] == u't':
            modification(u'User:' + username + u'/test court')
        elif sys.argv[1] == u'unit tests' or sys.argv[1] == u'tu':
            addLine(u"== {{langue|fr}} ==\n=== {{S|étymologie}} ===\n{{ébauche-étym|fr}}\n=== {{S|nom|fr}} ===\n{{fr-rég|}}\n\'\'\'{{subst:PAGENAME}}\'\'\' {{pron||fr}} {{genre ?}}\n#\n#* ''''\n==== {{S|variantes orthographiques}} ====\n==== {{S|synonymes}} ====\n==== {{S|antonymes}} ====\n==== {{S|dérivés}} ====\n==== {{S|apparentés}} ====\n==== {{S|vocabulaire}} ====\n==== {{S|hyperonymes}} ====\n==== {{S|hyponymes}} ====\n==== {{S|méronymes}} ====\n==== {{S|holonymes}} ====\n==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n=== {{S|prononciation}} ===\n* {{pron||fr}}\n* {{écouter|<!--  précisez svp la ville ou la région -->||audio=|lang=}}\n==== {{S|homophones}} ====\n==== {{S|paronymes}} ====\n=== {{S|anagrammes}} ===\n=== {{S|voir aussi}} ===\n* {{WP}}\n=== {{S|références}} ===\n", u'fr', u'prononciation', u'* {{pron|boum|fr}}')
        elif sys.argv[1] == u'page':
            modification(u'télétransporter')
        elif sys.argv[1] == u'file' or sys.argv[1] == u'txt':
            crawlerFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            crawlerXML(u'dumps/frwikibooks-20170720-pages-meta-current.xml', regex)
        elif sys.argv[1] == u'link' or sys.argv[1] == u'm':
            crawlerLink(site, u'Modèle:ex',u'')
        elif sys.argv[1] == u'cat':
            crawlerCat(u'Caractères en braille', True, u'')
        elif sys.argv[1] == u's':
            crawlerSearch(u'insource:/\<strong>\<strong>/')
        elif sys.argv[1] == u'u':
            crawlerUser(u'User:JackBot', 10000, u'')
        elif sys.argv[1] == u'redirects':
            crawlerRedirects()
        elif sys.argv[1] == u'all':
           crawlerAll()
        elif sys.argv[1] == u'RC':
            while 1:
                crawlerRCLastDay()
        elif sys.argv[1] == u'nocat':
            crawlerSpecialNotCategorized()
        elif sys.argv[1] == u'lint':
            crawlerSpecialLint()
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            modification(html2Unicode(sys.argv[1]))
    else:
        while 1:
            crawlerRC()

if __name__ == "__main__":
    main(sys.argv)


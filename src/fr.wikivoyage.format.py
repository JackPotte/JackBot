#!/usr/bin/env python
# coding: utf-8
# Ce script formate Wikivoyage

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


def modification(PageHS):
    summary = u'Formatage'
    page = Page(site, PageHS)
    print(PageHS.encode(config.console_encoding, 'replace'))
    if not page.exists(): return
    if page.namespace() != 0 and PageHS.find(u'Utilisateur:JackBot/test') == -1 and PageHS.find(u'Modèle:Cite pmid/') == -1: return
    try:
        PageBegin = page.get()
    except pywikibot.exceptions.NoPage:
        print "NoPage"
        return
    except pywikibot.exceptions.IsRedirectPage:
        print "Redirect page"
        return
    except pywikibot.exceptions.LockedPage:
        print "Locked/protected page"
        return
    if PageBegin.find(u'{{en travaux') != -1 or PageBegin.find(u'{{En travaux') != -1:
        print u'Page en travaux'
        return
    PageTemp = PageBegin
    PageEnd = u''

    if checkURL:
        # Traitements des URL et leurs modèles
        if debugLevel > 0: print u'Test des URL'
        PageTemp = hyperlynx(PageTemp, debugLevel)
        if debugLevel > 0: print (u'--------------------------------------------------------------------------------------------')
        if PageTemp != PageBegin:
            summary = summary + u', vérification des liens externes et traduction de leurs modèles'

    # Protocoles
    PageTemp = PageTemp.replace(u'http://http://', u'http://')


    # Traitements des modèles
    templates = [u'Aller', u'Circuler', u'Voir', u'Faire', u'Acheter', u'Manger', u'Sortir', u'Se loger', u'Destination',
        u'Listing', u'Représentation diplomatique', u'Marqueur', u'Ville'
    ]
    parameters = [
        [u'handicap', u'description', u'Handicap'],
        [u'wifi', u'description', u'Wi-Fi'],
        #[u'numéro gratuit', u'téléphone'],
        #[u'téléphone portable', u'téléphone'],
    ]
    #for template in templates:
    for parameter in parameters:
        #PageTemp = mergeParameters(PageTemp, template, parameter)
        PageTemp = searchDoubles(PageTemp, parameter)

    # Analyse des crochets et accolades (à faire : hors LaTex)
    if PageTemp.count('{') - PageTemp.count('}') != 0:
        if PageHS.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + PageHS + u']] : accolade cassée')
        #if debugLevel > 1: raise Exception(u'Accolade cassée')
    if PageTemp.count('[') - PageTemp.count(']') != 0:
        if PageHS.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + PageHS + u']] : crochet cassé')
        #if debugLevel > 1: raise Exception(u'Crochet cassé')
    if PageBegin.count('[[') - PageBegin.count(']]') != PageTemp.count('[[') - PageTemp.count(']]'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0: print u'Crochets cassés'    #raise Exception(u'Crochets cassés')
        return
    if PageBegin.count('{{') - PageBegin.count('}}') != PageTemp.count('{{') - PageTemp.count('}}'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0: print u'Accolades cassées'    #raise Exception(u'Accolades cassées')
        return

    # Sauvegarde
    PageEnd = PageTemp
    if PageEnd != PageBegin:
        sauvegarde(page,PageEnd,summary)


def mergeParameters(PageTemp, template, parameter):
    if debugLevel > 1: print template + u' : ' + parameter[0] + u' => ' + parameter[1]
    PageEnd = u''

    tRegex = ur'{{[' + template[:1].lower() + u'|' + template[:1].upper() + u']' + template[1:] + ur'([^\|}]*\|)'
    if debugLevel > 1: print str(len(re.findall(tRegex, PageTemp))) + u' ' + template
    while re.search(tRegex, PageTemp):
        # Positionnement au premier paramètre du modèle à modifier
        PageEnd = PageEnd + PageTemp[:re.search(tRegex, PageTemp).end()+len(u'{{' + template)]
        PageTemp = PageTemp[re.search(tRegex, PageTemp).end()+len(u'{{' + template):]

        # Recherche du paramètre dans le modèle courant
        pRegex = ur'\| *' + parameter[0] + ur' *=[^}\|]*'
        nRegex = ur' *' + parameter[0] + ur' *='
        while not re.match(pRegex, PageTemp, re.MULTILINE) and ( \
            (PageTemp.find(u'{{') < PageTemp.find(u'}}') and PageTemp.find(u'{{') != -1) or \
            (PageTemp.find(u'|') < PageTemp.find(u'}}') and PageTemp.find(u'|') != -1) \
        ) :
            #if template == 'Se loger': raw_input(PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace'))
            if PageTemp.find(u'}}') < PageTemp.find(u'|') or (PageTemp.find(u'{{') < PageTemp.find(u'|') and PageTemp.find(u'{{') != -1):
                PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
                PageTemp = PageTemp[PageTemp.find(u'}}')+2:]
            else:
                PageEnd = PageEnd + PageTemp[:PageTemp.find(u'|')+1]
                PageTemp = PageTemp[PageTemp.find(u'|')+1:]

                if re.match(nRegex, PageTemp, re.MULTILINE):
                    PageEnd = PageEnd[:-1]
                    PageTemp = u'|' + PageTemp

        if re.match(pRegex, PageTemp, re.MULTILINE):
            if debugLevel > 0: print u' ' + parameter[0] + u' trouvé dans ' + template + u' en ' + str(re.match(pRegex, PageTemp, re.MULTILINE).start())

            # Capitalisation des modèles
            PageEnd = re.sub(tRegex, ur'{{' + template + ur'\1', PageEnd)
            PageTemp = re.sub(tRegex, ur'{{' + template + ur'\1', PageTemp)

            modele = PageTemp[re.match(pRegex, PageTemp, re.MULTILINE).start():re.match(pRegex, PageTemp, re.MULTILINE).end()]
            if debugLevel > 1: print u' retrait de : ' + modele
            PageTemp = PageTemp[:re.match(pRegex, PageTemp, re.MULTILINE).start()] + PageTemp[re.match(pRegex, PageTemp, re.MULTILINE).end():]
            modele = trim(modele[modele.find(u'=')+1:])

            # Fusion de l'ancien paramètre trouvé
            if modele != u'' and len(parameter) > 1:
                # Dans le modèle courant, après les modèles imbriqués, voire parameter[1] s'il n'existe pas
                #regex = ur'\| *' + parameter[1] + ur' *=({{.*?}}|.)*$' + re.search = modèle précédent
                #regex = ur'\| *' + parameter[1] + ur' *=[^{}]*$' + re.match = modèle suivant
                regex = ur'\| *' + parameter[1] + ur' *=[^{}]*$'    # Si rien, tél dans mdl suivant, sinon mdl précédent, d'où le rfind à la place
                if re.search(regex, PageEnd, re.MULTILINE):
                    if debugLevel > 0: print ' paramètre : ' + parameter[1] + u'= situé avant ' + parameter[0] + u'='
                    if debugLevel > 1: raw_input(PageEnd[re.search(regex, PageEnd, re.MULTILINE).end():].encode(config.console_encoding, 'replace'))
                    if PageEnd.rfind(template) != -1:
                        PageTemp = PageEnd[PageEnd.rfind(template):] + PageTemp
                        PageEnd = PageEnd[:PageEnd.rfind(template)]
                    else:
                        return PageEnd + PageTemp

                regex = ur'^({{.*?}}|.)*\| *' + parameter[1] + ur' *='
                while PageTemp.find(u'{{') != -1 and PageTemp.find(u'}}') != -1 and PageTemp.find(u'{{') < PageTemp.find(u'}}') \
                    and (not re.search(regex, PageTemp, re.MULTILINE) or re.search(regex, PageTemp, re.MULTILINE).end() > PageTemp.find(u'}}')):
                    PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
                    PageTemp = PageTemp[PageTemp.find(u'}}')+2:]

                if not re.search(regex, PageTemp, re.MULTILINE):
                    # BUG
                    if debugLevel > 1: print ' ajout du paramètre : ' + parameter[1]
                    PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')]
                    PageTemp = u'| ' + parameter[1] + u' = ' + PageTemp[PageTemp.find(u'}}'):]
                else:
                    if debugLevel > 1: print ' paramètre ' + parameter[1] + u' existant'
                    PageEnd = PageEnd + PageTemp[:re.search(regex, PageTemp, re.MULTILINE).end()]
                    PageTemp = PageTemp[re.search(regex, PageTemp, re.MULTILINE).end():]

                if len(parameter) > 2:
                    # à proposer ? if modele == 'non défini': parameter[2] = u''
                    newTemplate = u'{{' + parameter[2] + u'|' + modele + u'}} '
                else:
                    if modele.find(u'(') != -1:
                        newTemplate = modele
                    else:
                        newTemplate = modele + u' (' + parameter[0] + u')'

                    # Après le contenu du paramètre
                    regex = ur'[^\|}]*'
                    if re.match(regex, PageTemp, re.MULTILINE):
                        PageEnd = PageEnd + PageTemp[:re.match(regex, PageTemp, re.MULTILINE).end()]
                        PageTemp = PageTemp[re.match(regex, PageTemp, re.MULTILINE).end():]

                    while PageEnd[-1:] == u' ':
                        PageEnd = PageEnd[:-1]
                    if PageEnd[-1:] != u'=':
                        newTemplate = u', ' + newTemplate
                # Ajout de parameter[0] en début de parameter[1]
                if debugLevel > 1: print u' ajout de : ' + newTemplate
                PageEnd = PageEnd + newTemplate

            if debugLevel > 1:
                #print template
                raw_input(PageTemp[:PageTemp.find(u'=')].encode(config.console_encoding, 'replace'))

        elif debugLevel > 1: print parameter[0] + u' non trouvé dans ' + template + u' ' + str(len(PageEnd))

    return PageEnd + PageTemp


def getWiki(language = 'fr', family = 'wiktionary'):
    if debugLevel > 1: print u'get ' + language + u'.' + family
    return pywikibot.Site(language, family)

def searchDoubles(PageTemp, parameter):
    if debugLevel > 0: u' Recherche de doublons dans le modèle : ' + parameter[1]
    PageEnd = u''
    regex = ur'{{' + parameter[1] + ur'[^\n]*{{' + parameter[1]
    while re.search(regex, PageTemp):
        raw_input(PageTemp[re.search(regex, PageTemp).start():re.search(regex, PageTemp).end()].encode(config.console_encoding, 'replace'))

    return PageEnd + PageTemp


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

# Traitement d'une catégorie
def crawlerCat(category, recursif = False, apres = u''):
    modifier = u'False'
    cat = catlib.Category(site, category)
    pages = cat.articlesList(True)
    #gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [ns]) HS sur Commons
    for Page in pagegenerators.PreloadingGenerator(pages, 100):
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
    gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
    for Page in pagegenerators.PreloadingGenerator(gen,100):
        #print (Page.title().encode(config.console_encoding, 'replace'))
        modification(Page.title())

# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
    page = Page(site,u'User talk:' + mynick)
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

def trim(s):
    return s.strip(u' \t\n\r\0\x0Bu')

# Lancement
if len(sys.argv) > 1:
    DebutScan = u''
    if len(sys.argv) > 2:
        if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
            debugLevel = 1
        else:
            DebutScan = sys.argv[2]
    if sys.argv[1] == u'test':
        modification(u'Utilisateur:' + mynick + u'/test')
    elif sys.argv[1] == u'test2':
        modification(u'Utilisateur:' + mynick + u'/test2')
    elif sys.argv[1] == u'txt':
        crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
    elif sys.argv[1] == u'txt2':
        crawlerFile(u'articles_' + language + u'_' + family + u'2.txt')
    elif sys.argv[1] == u'u':
        crawlerUser(u'Utilisateur:JackBot')
    elif sys.argv[1] == u'r':
        if len(sys.argv) > 2:
            crawlerSearch(sys.argv[2])
        else:
            crawlerSearch(u'chinois')
    elif sys.argv[1] == u'm':
        crawlerLink(u'Modèle:Wi-Fi', u'')
        crawlerLink(u'Modèle:Handicap', u'')
    elif sys.argv[1] == u'cat':
        crawlerCat(u'Article avec listing avec paramètre wifi', False, u'')
        crawlerCat(u'Article avec listing avec paramètre handicap', False, u'')
        crawlerCat(u'Article avec listing avec paramètre téléphone portable‎', False, u'')
        crawlerCat(u'Article avec listing avec paramètre numéro gratuit‎', False, u'')
    elif sys.argv[1] == u'page':
        modification(u'10e arrondissement de Paris')
    else:
        modification(sys.argv[1])    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
    crawlerLink(u'Modèle:Listing',u'')

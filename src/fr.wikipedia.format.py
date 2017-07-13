#!/usr/bin/env python
# coding: utf-8
# Ce script :
#     Vérifie tous les hyperliens, les marque comme {{lien brisé}} le cas échéant, et traduit leurs modèles en français
#     Retire les espaces dans {{FORMATNUM:}} qui empêche de les trier dans les tableaux
#     Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
# A terme peut-être :
#     Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...), et remplacement des liens bleu fr.wikipedia.org/wiki par [[ ]], des liens rouges par {{lien|lang=xx}}
#     Mettra à jour les évaluations à partir du bandeau ébauche
#     Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto) ou : python cosmetic_changes.py -lang:"fr" -recentchanges

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import hyperlynx
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# Global variables
debugLevel = 0
fileName = __file__
if debugLevel > 0: print fileName
safeMode = True # Count if the braces & brackets are even before saving
siteLanguage = u'fr'
siteFamily = u'wikipedia'
#site.lang
#site.family.name
username = config.usernames[siteFamily][siteLanguage]
if debugLevel > 1: print siteLanguage
if debugLevel > 1: print siteFamily
site = pywikibot.Site(siteLanguage, siteFamily)

checkURL = True
allNamespaces = False
output = u'dumps/articles_WPout.txt'


# Modification du wiki
def modification(pageName):
    summary = u'Formatage'
    page = Page(site,pageName)
    print(pageName.encode(config.console_encoding, 'replace'))
    if not page.exists(): return
    if not allNamespaces and page.namespace() != 0 and pageName.find(u'Utilisateur:JackBot/test') == -1 and pageName.find(u'Modèle:Cite pmid/') == -1: return
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
        print "Page en travaux"
        return
    PageTemp = PageBegin


    # Traitements des URL et leurs modèles
    if checkURL:
        if debugLevel > 0: print u'Test des URL'
        PageTemp = hyperlynx(PageTemp, debugLevel)
    if debugLevel > 0: print (u'--------------------------------------------------------------------------------------------')
    if PageTemp != PageBegin:
        summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/11#Identifier les liens brisés (le retour ;-))|Vérification des liens externes]]'
        summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer_les_.7B.7BCite_web.7D.7D_par_.7B.7BLien_web.7D.7D|traduction de leurs modèles]]'
    regex = ur'({{[l|L]ien *\|[^}]*)traducteur( *=)'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1trad\2', PageTemp)
    PageTemp = PageTemp.replace(u'http://http://', u'http://')
    PageTemp = PageTemp.replace(u'https://https://', u'https://')

    # Titres manquants (ébauche)
    '''PageEnd = u''
    regex = ur'{{[l|L]ien web *\|'
    if re.search(regex, PageTemp):
        PageEnd = PageTemp[:re.search(regex, PageTemp).start()]
        PageTemp = PageTemp[re.search(regex, PageTemp).start():]
        PageTemp = addParameter(PageTemp, u'titre')
    PageTemp = PageEnd + PageTemp'''

    # Autres modèles (https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Page_utilisant_un_mod%C3%A8le_avec_un_param%C3%A8tre_obsol%C3%A8te)
    PageTemp = PageTemp.replace(u'{{Reflist|2}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{reflist|2}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Reflist|3}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{reflist|3}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Reflist|30em}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{reflist|30em}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Reflist|colwidth = 30em}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Reflist|colwidth=40em}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Références|2}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{références|2}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Références|30em}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{références|colonnes}}', u'{{Références}}')
    PageTemp = PageTemp.replace(u'{{Références|taille}}', u'{{Références}}')
    
    # Rustine temporaire pour https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Page_du_mod%C3%A8le_Article_comportant_une_erreur
    '''
    PageEnd = u''
    while PageTemp.find(u'{{article') != -1:
        PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{article')+len(u'{{article')]
        PageTemp = PageTemp[PageTemp.find(u'{{article')+len(u'{{article'):]
        if PageTemp.find(u'éditeur=') != -1 and PageTemp.find(u'éditeur=') < PageTemp.find(u'}}') and (PageTemp.find(u'périodique=') == -1 or PageTemp.find(u'périodique=') > PageTemp.find(u'}}')) and (PageTemp.find(u'revue=') == -1 or PageTemp.find(u'revue=') > PageTemp.find(u'}}')) and (PageTemp.find(u'journal=') == -1 or PageTemp.find(u'journal=') > PageTemp.find(u'}}')):
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'éditeur=')] + u'périodique='
            PageTemp = PageTemp[PageTemp.find(u'éditeur=')+len(u'éditeur='):]
    PageTemp = PageEnd + PageTemp
    PageEnd = u''
    while PageTemp.find(u'{{Article') != -1:
        PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{Article')+len(u'{{Article')]
        PageTemp = PageTemp[PageTemp.find(u'{{Article')+len(u'{{Article'):]
        if PageTemp.find(u'éditeur=') != -1 and PageTemp.find(u'éditeur=') < PageTemp.find(u'}}') and (PageTemp.find(u'périodique=') == -1 or PageTemp.find(u'périodique=') > PageTemp.find(u'}}')) and (PageTemp.find(u'revue=') == -1 or PageTemp.find(u'revue=') > PageTemp.find(u'}}')) and (PageTemp.find(u'journal=') == -1 or PageTemp.find(u'journal=') > PageTemp.find(u'}}')):
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'éditeur=')] + u'périodique='
            PageTemp = PageTemp[PageTemp.find(u'éditeur=')+len(u'éditeur='):]        
    PageTemp = PageEnd + PageTemp
    '''
    
    # Nombres
    PageTemp = re.sub(ur'{{ *(formatnum|Formatnum|FORMATNUM)\:([0-9]*) *([0-9]*)}}', ur'{{\1:\2\3}}', PageTemp)

    # Textes
    regex = u'([^\./])[Mm]arianne2.fr'
    PageTemp = re.sub(regex, ur'\1Marianne', PageTemp)

    # Analyse des crochets et accolades (à faire : hors LaTex)
    if PageTemp.count('{') - PageTemp.count('}') != 0:
        if pageName.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + pageName + u']] : accolade cassée')
        #if debugLevel > 1: raise Exception(u'Accolade cassée')
    if PageTemp.count('[') - PageTemp.count(']') != 0:
        if pageName.find(u'Utilisateur:JackBot/') == -1: log(u'*[[' + pageName + u']] : crochet cassé')
        #if debugLevel > 1: raise Exception(u'Crochet cassé')
    if PageBegin.count('[[') - PageBegin.count(']]') != PageTemp.count('[[') - PageTemp.count(']]'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0: print u'Crochets cassés'    #raise Exception(u'Crochets cassés')
        if safeMode: return
    if PageBegin.count('{{') - PageBegin.count('}}') != PageTemp.count('{{') - PageTemp.count('}}'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(PageTemp + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0: print u'Accolades cassées'    #raise Exception(u'Accolades cassées')
        if safeMode: return

    # Catégories
    if pageName.find(u'Modèle:Cite pmid/') != -1:
        PageTemp = PageTemp.replace(u'Catégorie:Modèle de source‎', u'Catégorie:Modèle pmid')
        PageTemp = PageTemp.replace(u'[[Catégorie:Modèle pmid]]', u'[[Catégorie:Modèle pmid‎|{{SUBPAGENAME}}]]')

    # Sauvegarde
    PageEnd = PageTemp
    if PageEnd != PageBegin and PageEnd != PageBegin.replace(u'{{chapitre |', u'{{chapitre|') and PageEnd != PageBegin.replace(u'{{Chapitre |', u'{{Chapitre|'):
        #PageEnd = re.sub(ur'<br>', ur'<br/>', PageEnd)
        PageEnd = PageEnd.replace(ur'</ref><ref>', ur'</ref>{{,}}<ref>')
        sauvegarde(page,PageEnd,summary)
        
def addParameter(PageTemp, parameter, content = None):
    PageEnd = u''
    if parameter == u'titre' and content is None:
        # Détermination du titre d'un site web
        URL = getParameter(u'url')
        PageEnd = PageTemp

    else:
        print 'en travaux'
    return PageEnd
        
def replaceParameterValue(PageTemp, template, parameterKey, oldValue, newValue):
    regex = ur'({{ *(' + template[:1].lower() + ur'|' + template[:1].upper() + ur')' + template[1:] + ur' *\n* *\|[^}]*' + parameterKey + ur' *= *)' + oldValue
    if debugLevel > 0: print regex
    PageTemp = re.sub(regex, ur'\1' + newValue, PageTemp)

    return PageTemp

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
    if source:
        PagesHS = open(source, 'r')
        while 1:
            pageName = PagesHS.readline().decode(config.console_encoding, 'replace')
            fin = pageName.find("\t")
            pageName = pageName[0:fin]
            if pageName == '': break
            if pageName.find(u'[[') != -1:
                pageName = pageName[pageName.find(u'[[')+2:len(pageName)]
            if pageName.find(u']]') != -1:
                pageName = pageName[0:pageName.find(u']]')]
            modification(pageName)
        PagesHS.close()

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
    gen = pagegenerators.SearchPageGenerator(pagename, site=site, namespaces=0)
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

def crawlerCatPMID(category):
    cat = catlib.Category(site, category)
    pages = cat.articlesList(False)
    for Page in pagegenerators.PreloadingGenerator(pages,100):
        main = Page.title()
        #main = main[11:len(main)]
        if main.find(u'pmid') != -1:
            modification(main)

# Lancement
if len(sys.argv) > 1:
    arg1 = sys.argv[1].decode('utf-8')
    DebutScan = u''
    if len(sys.argv) > 2:
        if sys.argv[2] == u'debug' or sys.argv[2] == u'd':
            if len(sys.argv) > 3:
                debugLevel = sys.argv[3]
            else:
                debugLevel = 1
        else:
            DebutScan = sys.argv[2]
    if arg1 == 'test':
        modification(u'Utilisateur:' + username + u'/test')
    if arg1 == 'test2':
        modification(u'Utilisateur:' + username + u'/test court')
    elif arg1 == 'txt':
        crawlerFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
    elif arg1 == 'u':
        crawlerUser(u'Utilisateur:JackBot')
    elif arg1 == 'r':
        if len(sys.argv) > 2:
            crawlerSearch(sys.argv[2])
        else:
            crawlerSearch(u'marianne2.fr')
    elif arg1 == 'm':
        crawlerLink(u'Modèle:Cite journal',u'')
    elif arg1 == 'cat':
        crawlerCat(u'Catégorie:Modèle élément chimique',False,u'')
        #crawlerCat(u'Catégorie:Page utilisant un modèle avec un paramètre obsolète',False,u'')
        #crawlerCat(u'Page du modèle Article comportant une erreur',False,u'')
        #crawlerCat(u'Catégorie:Page utilisant un modèle avec une syntaxe erronée',True,u'')    # En test
    elif arg1 == 'page':
        modification(u'Utilisateur:JackBot/test unitaire')
    elif arg1 == 'p':
        modification(u'Utilisateur:Cantons-de-l\'Est/Voie lactée')
    elif arg1 == 'RC':
        while 1:
            crawlerRC()
    else:
        modification(arg1)    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
    # Quotidiennement :
    crawlerCatPMID(u'Catégorie:Modèle de source')
    crawlerLink(u'Modèle:Cite web',u'')
    crawlerLink(u'Modèle:Cite journal',u'')
    crawlerLink(u'Modèle:Cite news',u'')
    crawlerLink(u'Modèle:Cite press release',u'')
    crawlerLink(u'Modèle:Cite episode',u'')
    crawlerLink(u'Modèle:Cite video',u'')
    crawlerLink(u'Modèle:Cite conference',u'')
    crawlerLink(u'Modèle:Cite arXiv',u'')
    crawlerLink(u'Modèle:Lien news',u'')
    crawlerLink(u'Modèle:deadlink',u'')
    crawlerLink(u'Modèle:lien brise',u'')
    crawlerLink(u'Modèle:lien cassé',u'')
    crawlerLink(u'Modèle:lien mort',u'')
    crawlerLink(u'Modèle:lien web brisé',u'')
    crawlerLink(u'Modèle:webarchive',u'')
    crawlerLink(u'Modèle:Docu',u'')
    crawlerLink(u'Modèle:Cita web',u'')
    crawlerLink(u'Modèle:Cita noticia',u'')
    crawlerLink(u'Modèle:Citeweb',u'')
    crawlerLink(u'Modèle:Cite magazine',u'')
    crawlerLink(u'Modèle:Cite',u'')
    crawlerLink(u'Modèle:Cite book',u'')

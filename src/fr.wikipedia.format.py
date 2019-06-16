#!/usr/bin/env python
# coding: utf-8
# Ce script :
#     Vérifie tous les hyperliens, les marque comme {{lien brisé}} le cas échéant, et traduit leurs modèles en français
#     Ajoute des liens vers les projets frères dans les pages d'homonymie, multilatéralement
# A terme peut-être :
#     Mettra à jour les liens vers les projets frères existants (fusions avec Sisterlinks...), et remplacement des liens bleu fr.wikipedia.org/wiki par [[ ]], des liens rouges par {{lien|lang=xx}}
#     Mettra à jour les évaluations à partir du bandeau ébauche
#     Corrigera les fautes d'orthographes courantes, signalées dans http://fr.wikipedia.org/wiki/Wikip%C3%A9dia:AutoWikiBrowser/Typos (semi-auto) ou : python cosmetic_changes.py -lang:"fr" -recentchanges

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, datetime, os, re, socket, sys, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

# Global variables
debugLevel = 0
debugAliases = ['-debug', '-d']
for debugAlias in debugAliases:
    if debugAlias in sys.argv:
        debugLevel= 1
        sys.argv.remove(debugAlias)

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

translateURL = True
fixTags = False
fixFiles = True
allNamespaces = False
fixArticle = False
fixMissingTitles = False
safeMode = True # Count if the braces & brackets are even before saving
output = u'dumps/articles_WPout.txt'
referencesAliases = []


def treatPageByName(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatage'
    page = Page(site, pageName)
    if not page.exists(): return
    if not hasMoreThanTime(page): return
    if not allNamespaces and page.namespace() != 0 and pageName.find(username) == -1 and \
        pageName.find(u'Template:Cite pmid/') == -1:
        return
    PageBegin = getContentFromPage(page, 'All')
    if PageBegin == 'KO':
        print 'Page illisible'
        return
    currentPage = PageBegin


    #*** Traitement des textes ***
    if debugLevel > 0: print u' Traitements généraux'
    currentPage = globalOperations(currentPage)
    if fixFiles: currentPage = replaceFilesErrors(currentPage)
    if fixTags: currentPage = replaceDepretacedTags(currentPage)
    if translateURL:
        if debugLevel > 0: print u'Test des URL'
        currentPage = hyperlynx(currentPage)
    regex = ur'({{[Ll]ien *\|[^}]*)traducteur( *=)'
    if re.search(regex, currentPage):
        currentPage = re.sub(regex, ur'\1trad\2', currentPage)
    currentPage = currentPage.replace(u'hhttp://', u'http://')

    regex = ur'({{[Ll]ien brisé*\|[^}]*url *=[^\|\'}]*)\'\'(\| *titre *=[^\|\'}]*)\'\''
    if re.search(regex, currentPage):
        currentPage = re.sub(regex, ur'\1\2', currentPage)

    #*** Traitement des modèles ***
    #https://fr.wikipedia.org/wiki/Catégorie:Page_utilisant_un_modèle_avec_un_paramètre_obsolète
    regex = ur' *{{[Rr]eflist([^}]*)}}'
    if re.search(regex, currentPage):
        currentPage = re.sub(regex,  ur'{{Références\1}}', currentPage)
    #TODO: garder les paramètres non vides : pasdecol, group(e), références, mais quid de taille et colonnes ?

    # https://fr.wikipedia.org/wiki/Catégorie:Page_du_modèle_Article_comportant_une_erreur
    if fixArticle:
        finalPage = u''
        while currentPage.find(u'{{article') != -1:
            finalPage = finalPage + currentPage[:currentPage.find(u'{{article')+len(u'{{article')]
            currentPage = currentPage[currentPage.find(u'{{article')+len(u'{{article'):]
            if currentPage.find(u'éditeur=') != -1 and currentPage.find(u'éditeur=') < currentPage.find(u'}}') and (currentPage.find(u'périodique=') == -1 or currentPage.find(u'périodique=') > currentPage.find(u'}}')) and (currentPage.find(u'revue=') == -1 or currentPage.find(u'revue=') > currentPage.find(u'}}')) and (currentPage.find(u'journal=') == -1 or currentPage.find(u'journal=') > currentPage.find(u'}}')):
                finalPage = finalPage + currentPage[:currentPage.find(u'éditeur=')] + u'périodique='
                currentPage = currentPage[currentPage.find(u'éditeur=')+len(u'éditeur='):]
        currentPage = finalPage + currentPage
        finalPage = u''
        while currentPage.find(u'{{Article') != -1:
            finalPage = finalPage + currentPage[:currentPage.find(u'{{Article')+len(u'{{Article')]
            currentPage = currentPage[currentPage.find(u'{{Article')+len(u'{{Article'):]
            if currentPage.find(u'éditeur=') != -1 and currentPage.find(u'éditeur=') < currentPage.find(u'}}') and (currentPage.find(u'périodique=') == -1 or currentPage.find(u'périodique=') > currentPage.find(u'}}')) and (currentPage.find(u'revue=') == -1 or currentPage.find(u'revue=') > currentPage.find(u'}}')) and (currentPage.find(u'journal=') == -1 or currentPage.find(u'journal=') > currentPage.find(u'}}')):
                finalPage = finalPage + currentPage[:currentPage.find(u'éditeur=')] + u'périodique='
                currentPage = currentPage[currentPage.find(u'éditeur=')+len(u'éditeur='):]        
        currentPage = finalPage + currentPage

    if fixMissingTitles:
        # Titres manquants (TODO: en test)
        finalPage = u''
        regex = ur'{{[l|L]ien web *\|'
        if re.search(regex, currentPage):
            finalPage = currentPage[:re.search(regex, currentPage).start()]
            currentPage = currentPage[re.search(regex, currentPage).start():]
            currentPage = addParameter(currentPage, u'titre')
        currentPage = finalPage + currentPage


    #*** Traitement des Catégories ***
    if pageName.find(u'Template:Cite pmid/') != -1:
        currentPage = currentPage.replace(u'Catégorie:Modèle de source‎', u'Catégorie:Modèle pmid')
        currentPage = currentPage.replace(u'[[Catégorie:Modèle pmid]]', u'[[Catégorie:Modèle pmid‎|{{SUBPAGENAME}}]]')


    # Analyse des crochets et accolades (à faire : hors LaTex)
    if currentPage.count('{') - currentPage.count('}') != 0:
        if pageName.find(u'User:JackBot/') == -1: log(u'*[[' + pageName + u']] : accolade cassée')
        #if debugLevel > 1: raise Exception(u'Accolade cassée')
    if currentPage.count('[') - currentPage.count(']') != 0:
        if pageName.find(u'User:JackBot/') == -1: log(u'*[[' + pageName + u']] : crochet cassé')
        #if debugLevel > 1: raise Exception(u'Crochet cassé')
    if PageBegin.count('[[') - PageBegin.count(']]') != currentPage.count('[[') - currentPage.count(']]'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(currentPage + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0:
            print u'Crochets cassés'    #raise Exception(u'Crochets cassés')
            raw_input(PageBegin.encode(config.console_encoding, 'replace'))
        if safeMode: return
    if PageBegin.count('{{') - PageBegin.count('}}') != currentPage.count('{{') - currentPage.count('}}'):
        txtfile = codecs.open(output, 'a', 'utf-8')
        txtfile.write(currentPage + u'\n\n------------------------------------------------------------------------------------------------------------\n\n')
        txtfile.close()    
        if debugLevel > 0:
            print u'Accolades cassées'    #raise Exception(u'Accolades cassées')
            raw_input(currentPage.encode(config.console_encoding, 'replace'))
        if safeMode: return

    finalPage = currentPage
    if debugLevel > 0: print (u'--------------------------------------------------------------------------------------------')
    if finalPage != PageBegin and finalPage != PageBegin.replace(u'{{chapitre |', u'{{chapitre|') and finalPage != PageBegin.replace(u'{{Chapitre |', u'{{Chapitre|'):
        summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer_les_.7B.7BCite_web.7D.7D_par_.7B.7BLien_web.7D.7D|traduction des modèles de liens]]'
        finalPage = finalPage.replace(ur'</ref><ref>', ur'</ref>{{,}}<ref>')
        savePage(page, finalPage, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
setGlobalsHL(debugLevel, site, username)
def main(*args):
    global allNamespaces
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'-test2' or sys.argv[1] == u'-tu':
            treatPageByName(u'User:' + username + u'/test unitaire')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            allNamespaces = True
            treatPageByName(u'SIMP J013656.5+093347')
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = u'\| *French *\|'
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.pagesByXML(siteLanguage + siteFamily + '\-.*xml', regex)
        elif sys.argv[1] == u'-u':
            p.pagesByUser(u'User:' + username)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2], namespaces = [0])
            else:
                p.pagesBySearch(u'"hhttp://"')
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Modèle:Dead link')
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat':
            global translateURL
            translateURL = False
            allNamespaces = True
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Catégorie:Pages utilisant des liens magiques ISBN', namespaces = None, afterPage = afterPage)
            #p.pagesByCat(u'Catégorie:Pages avec ISBN invalide', namespaces = None, afterPage = afterPage)
        elif sys.argv[1] == u'-redirects':
            p.pagesByRedirects()
        elif sys.argv[1] == u'-all':
           p.pagesByAll()
        elif sys.argv[1] == u'-RC':
            while 1:
                p.pagesByRCLastDay()
        elif sys.argv[1] == u'-nocat':
            p.pagesBySpecialNotCategorized()
        elif sys.argv[1] == u'-lint':
            p.pagesBySpecialLint(lintCategories = 'missing-end-tag', namespaces = [0])
        elif sys.argv[1] == u'-extlinks':
            p. pagesBySpecialLinkSearch('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        # Daily:
        p.pagesByCat(u'Catégorie:Modèle de source', namespaces = [10], names = ['pmid'])
        p.pagesByLink(u'Template:Cite web')
        p.pagesByLink(u'Template:Cite journal')
        p.pagesByLink(u'Template:Cite news')
        p.pagesByLink(u'Template:Cite press release')
        p.pagesByLink(u'Template:Cite episode')
        p.pagesByLink(u'Template:Cite video')
        p.pagesByLink(u'Template:Cite conference')
        p.pagesByLink(u'Template:Cite arXiv')
        p.pagesByLink(u'Template:Lien news')
        p.pagesByLink(u'Template:deadlink')
        p.pagesByLink(u'Template:lien brise')
        p.pagesByLink(u'Template:lien cassé')
        p.pagesByLink(u'Template:lien mort')
        p.pagesByLink(u'Template:lien web brisé')
        p.pagesByLink(u'Template:webarchive')
        p.pagesByLink(u'Template:Docu')
        p.pagesByLink(u'Template:Cita web')
        p.pagesByLink(u'Template:Cita noticia')
        p.pagesByLink(u'Template:Citeweb')
        p.pagesByLink(u'Template:Cite magazine')
        p.pagesByLink(u'Template:Cite')
        p.pagesByLink(u'Template:Cite book')
        #p.pagesByLink(u'Template:Reflist') Interblocages quotidients

if __name__ == "__main__":
    main(sys.argv)

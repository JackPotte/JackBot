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

checkURL = True
fixTags = False
fixFiles = True
allNamespaces = False
fixArticle = False
fixMissingTitles = False
safeMode = True # Count if the braces & brackets are even before saving
output = u'dumps/articles_WPout.txt'


def treatPageByName(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatage'
    page = Page(site,pageName)
    if not page.exists(): return
    if not hasMoreThanTime(page): return
    if not allNamespaces and page.namespace() != 0 and pageName.find(username) == -1 and pageName.find(u'Modèle:Cite pmid/') == -1: return
    PageBegin = getContentFromPage(page, 'All')
    PageTemp = PageBegin

    #*** Traitement des textes ***
    regex = ur'([^\./])[Mm]arianne2.fr'
    PageTemp = re.sub(regex, ur'\1Marianne', PageTemp)

    if PageTemp.find('http://www.dmoz.org/search?') == -1:
        regex = ur'\[http://www\.dmoz\.org/([^ \]<}{\'"]*)([^\]]*)\]'
        PageTemp = re.sub(regex, ur'[[dmoz:\1|\2]]', PageTemp)
        regex =   ur'http://www\.dmoz\.org/([^ \]<}{\'"]*)'
        PageTemp = re.sub(regex, ur'[[dmoz:\1]]', PageTemp)

    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
    if checkURL:
        if debugLevel > 0: print u'Test des URL'
        PageTemp = hyperlynx(PageTemp, debugLevel)
    regex = ur'({{[l|L]ien *\|[^}]*)traducteur( *=)'
    if re.search(regex, PageTemp):
        PageTemp = re.sub(regex, ur'\1trad\2', PageTemp)
    PageTemp = PageTemp.replace(u'http://http://', u'http://')
    PageTemp = PageTemp.replace(u'https://https://', u'https://')

    #*** Traitement des modèles ***
    PageTemp = re.sub(ur'{{ *(formatnum|Formatnum|FORMATNUM)\:([0-9]*) *([0-9]*)}}', ur'{{\1:\2\3}}', PageTemp)

    #https://fr.wikipedia.org/wiki/Catégorie:Page_utilisant_un_modèle_avec_un_paramètre_obsolète
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
    
    # https://fr.wikipedia.org/wiki/Catégorie:Page_du_modèle_Article_comportant_une_erreur
    if fixArticle:
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

    if fixMissingTitles:
        # Titres manquants (TODO: en test)
        PageEnd = u''
        regex = ur'{{[l|L]ien web *\|'
        if re.search(regex, PageTemp):
            PageEnd = PageTemp[:re.search(regex, PageTemp).start()]
            PageTemp = PageTemp[re.search(regex, PageTemp).start():]
            PageTemp = addParameter(PageTemp, u'titre')
        PageTemp = PageEnd + PageTemp


    #*** Traitement des Catégories ***
    if pageName.find(u'Modèle:Cite pmid/') != -1:
        PageTemp = PageTemp.replace(u'Catégorie:Modèle de source‎', u'Catégorie:Modèle pmid')
        PageTemp = PageTemp.replace(u'[[Catégorie:Modèle pmid]]', u'[[Catégorie:Modèle pmid‎|{{SUBPAGENAME}}]]')


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

    PageEnd = PageTemp
    if debugLevel > 0: print (u'--------------------------------------------------------------------------------------------')
    if PageEnd != PageBegin and PageEnd != PageBegin.replace(u'{{chapitre |', u'{{chapitre|') and PageEnd != PageBegin.replace(u'{{Chapitre |', u'{{Chapitre|'):
        summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/11#Identifier les liens brisés (le retour ;-))|Vérification des liens externes]]'
        summary = summary + u', [[Wikipédia:Bot/Requêtes/2012/12#Remplacer_les_.7B.7BCite_web.7D.7D_par_.7B.7BLien_web.7D.7D|traduction de leurs modèles]]'
        PageEnd = PageEnd.replace(ur'</ref><ref>', ur'</ref>{{,}}<ref>')
        savePage(page, PageEnd, summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
def main(*args):
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        if sys.argv[1] == u'-test':
            treatPageByName(u'Utilisateur:' + username + u'/test')
        elif sys.argv[1] == u'-test2':
            treatPageByName(u'Utilisateur:' + username + u'/test2')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            treatPageByName(u'Catégorie:Python')
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = u''
            if len(sys.argv) > 2: regex = sys.argv[2]
            p.pagesByXML(siteLanguage + siteFamily + '.*xml', regex)
        elif sys.argv[1] == u'-u':
            p.pagesByUser(u'User:' + username)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'chinois')
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Modèle:autres projets')
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat':
            afterPage = u''
            if len(sys.argv) > 2: afterPage = sys.argv[2]
            p.pagesByCat(u'Catégorie:Python', afterPage = afterPage)
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
            p.pagesBySpecialLint()
        elif sys.argv[1] == u'-extlinks':
            p. pagesBySpecialLinkSearch('www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            treatPageByName(html2Unicode(sys.argv[1]))
    else:
        # Daily:
        p.pagesByCat(u'Catégorie:Modèle de source', ns = 10, names = ['pmid'])
        p.pagesByLink(u'Modèle:Cite web',u'')
        p.pagesByLink(u'Modèle:Cite journal',u'')
        p.pagesByLink(u'Modèle:Cite news',u'')
        p.pagesByLink(u'Modèle:Cite press release',u'')
        p.pagesByLink(u'Modèle:Cite episode',u'')
        p.pagesByLink(u'Modèle:Cite video',u'')
        p.pagesByLink(u'Modèle:Cite conference',u'')
        p.pagesByLink(u'Modèle:Cite arXiv',u'')
        p.pagesByLink(u'Modèle:Lien news',u'')
        p.pagesByLink(u'Modèle:deadlink',u'')
        p.pagesByLink(u'Modèle:lien brise',u'')
        p.pagesByLink(u'Modèle:lien cassé',u'')
        p.pagesByLink(u'Modèle:lien mort',u'')
        p.pagesByLink(u'Modèle:lien web brisé',u'')
        p.pagesByLink(u'Modèle:webarchive',u'')
        p.pagesByLink(u'Modèle:Docu',u'')
        p.pagesByLink(u'Modèle:Cita web',u'')
        p.pagesByLink(u'Modèle:Cita noticia',u'')
        p.pagesByLink(u'Modèle:Citeweb',u'')
        p.pagesByLink(u'Modèle:Cite magazine',u'')
        p.pagesByLink(u'Modèle:Cite',u'')
        p.pagesByLink(u'Modèle:Cite book',u'')

if __name__ == "__main__":
    main(sys.argv)

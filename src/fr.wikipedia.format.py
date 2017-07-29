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
debugAliases = ['debug', 'd', '-d']
for debugAlias in debugAliases:
    if debugAlias in sys.argv:
        debugLevel= 1
        sys.argv.remove(debugAlias)

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
fixTags = False
fixFiles = True
allNamespaces = False
output = u'dumps/articles_WPout.txt'


def treatPageByName(pageName):
    summary = u'Formatage'
    page = Page(site,pageName)
    print(pageName.encode(config.console_encoding, 'replace'))
    if not page.exists(): return
    if not hasMoreThanTime(page): return
    if not allNamespaces and page.namespace() != 0 and pageName.find(u'Utilisateur:JackBot/test') == -1 and pageName.find(u'Modèle:Cite pmid/') == -1: return
    PageBegin = getContentFromPage(page, 'All')
    PageTemp = PageBegin

    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
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
        savePage(page,PageEnd,summary)


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
def main(*args):
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
            treatPageByName(u'Utilisateur:' + username + u'/test')
        if arg1 == 'test2':
            treatPageByName(u'Utilisateur:' + username + u'/test court')
        elif arg1 == 'txt':
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt')
        elif arg1 == 'u':
            p.pagesByUser(u'Utilisateur:JackBot')
        elif arg1 == 'r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'marianne2.fr')
        elif arg1 == 'm':
            p.pagesByLink(u'Modèle:Cite journal',u'')
        elif arg1 == 'cat':
            p.pagesByCat(u'Catégorie:Modèle élément chimique',False,u'')
            #p.pagesByCat(u'Catégorie:Page utilisant un modèle avec un paramètre obsolète',False,u'')
            #p.pagesByCat(u'Page du modèle Article comportant une erreur',False,u'')
            #p.pagesByCat(u'Catégorie:Page utilisant un modèle avec une syntaxe erronée',True,u'')    # En test
        elif arg1 == 'page':
            treatPageByName(u'Utilisateur:JackBot/test unitaire')
        elif arg1 == 'p':
            treatPageByName(u'Utilisateur:Cantons-de-l\'Est/Voie lactée')
        elif arg1 == 'RC':
            while 1:
                p.pagesByRC()
        else:
            treatPageByName(arg1)    # Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
    else:
        # Quotidiennement :
        p.pagesByCatPMID(u'Catégorie:Modèle de source')
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

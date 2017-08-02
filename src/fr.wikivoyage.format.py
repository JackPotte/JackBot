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

checkURL = False
fixTags = False
fixFiles = True


def treatPageByName(pageName):
    print(pageName.encode(config.console_encoding, 'replace'))
    summary = u'Formatage'
    page = Page(site, pageName)
    PageBegin = getContentFromPage(page, 'All')
    PageTemp = PageBegin
    PageEnd = u''

    PageTemp = globalOperations(PageTemp)
    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
    if checkURL: PageTemp = hyperlynx(PageTemp)

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
        savePage(page,PageEnd,summary)


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
            p.pagesByCat(u'Catégorie:Pages utilisant des liens magiques ISBN', namespaces = None, afterPage = afterPage)
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
        while 1:
            p.pagesByRC()

if __name__ == "__main__":
    main(sys.argv)

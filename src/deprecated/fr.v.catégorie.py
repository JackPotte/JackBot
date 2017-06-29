﻿#!/usr/bin/env python
# coding: utf-8
# Ce script retire les catégories en double
 
# Importation des modules
import catlib, pagegenerators, os, codecs, urllib
from wikipedia import *
 
# Déclaration
language = "fr"
family = "wikiversity"
mynick = "JackBot"
site = getSite(language,family)
summary = u'Retrait des catégories en double'
 
# Modification du wiki
def modification(PageHS):
        page = Page(site,PageHS)
        if page.exists():
                if page.namespace() !=0 and page.title() != u'Utilisateur:JackBot/test': 
                        return
                else:
                        try:
                                PageTemp = page.get()
                        except wikipedia.NoPage:
                                print "NoPage"
                                return
                        except wikipedia.IsRedirectPage:
                                print "Redirect page"
                                return
                        except wikipedia.LockedPage:
                                print "Locked/protected page"
                                return
        else:
                return
 
        # Détermination de la catégorie introduite par le modèle
        if PageTemp.find(u'{{Chapitre') == -1 and PageTemp.find(u'{{chapitre') == -1:
                return
        elif PageHS.find(u'/') == -1:
                return
        else:
                categorie = u'[[Catégorie:' + PageHS[0:PageHS.find(u'/')] + u']]'
                if PageTemp.find(categorie) != -1: PageTemp = PageTemp[0:PageTemp.find(categorie)] + PageTemp[PageTemp.find(categorie)+len(categorie):len(PageTemp)]
 
        if page.get() != PageTemp:
                # Retouches cosmétiques
                if  PageTemp.find(u'{{Chapitre') != -1:
                        PageTemp2 = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                        while PageTemp2.find(u'\n\n') != -1 and PageTemp2.find(u'\n\n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')] + PageTemp2[0:PageTemp2.find(u'\n\n')] + PageTemp2[PageTemp2.find(u'\n\n')+1:len(PageTemp2)]
                                PageTemp2 = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                        while PageTemp2.find(u'\n \n') != -1 and PageTemp2.find(u'\n \n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')] + PageTemp2[0:PageTemp2.find(u'\n \n')] + PageTemp2[PageTemp2.find(u'\n \n')+2:len(PageTemp2)]
                        while PageTemp2.find(u'\n  \n') != -1 and PageTemp2.find(u'\n  \n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre')] + PageTemp2[0:PageTemp2.find(u'\n  \n')] + PageTemp2[PageTemp2.find(u'\n  \n')+3:len(PageTemp2)]
                                PageTemp2 = PageTemp[PageTemp.find(u'{{Chapitre')+len(u'{{Chapitre'):len(PageTemp)]
                elif PageTemp.find(u'{{chapitre') != -1:
                        PageTemp2 = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
                        while PageTemp2.find(u'\n\n') != -1 and PageTemp2.find(u'\n\n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')] + PageTemp2[0:PageTemp2.find(u'\n\n')] + PageTemp2[PageTemp2.find(u'\n\n')+1:len(PageTemp2)]
                                PageTemp2 = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
                        while PageTemp2.find(u'\n \n') != -1 and PageTemp2.find(u'\n \n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')] + PageTemp2[0:PageTemp2.find(u'\n \n')] + PageTemp2[PageTemp2.find(u'\n \n')+2:len(PageTemp2)]
                        while PageTemp2.find(u'\n  \n') != -1 and PageTemp2.find(u'\n  \n') < PageTemp2.find(u'}}'):
                                PageTemp = PageTemp[0:PageTemp.find(u'{{chapitre')+len(u'{{chapitre')] + PageTemp2[0:PageTemp2.find(u'\n  \n')] + PageTemp2[PageTemp2.find(u'\n  \n')+3:len(PageTemp2)]
                                PageTemp2 = PageTemp[PageTemp.find(u'{{chapitre')+len(u'{{chapitre'):len(PageTemp)]
 
                # Sauvegarde semie-automatique
                #result=u'ok'
                #print (PageTemp.encode(config.console_encoding, 'replace'))
                #result = raw_input('\033[94m' + "Sauvegarder ? (o/n)" + '\033[0m')
                #if result == u'n' or result == u'no' or result == u'non': 
                #       return
                #else:
                try:
                                page.put(PageTemp, summary)
                except pywikibot.EditConflict:
                                print "Conflict"
                                return
                except wikipedia.NoPage:
                                print "NoPage"
                                return
                except wikipedia.IsRedirectPage:
                                print "Redirect page"
                                return
                except wikipedia.LockedPage:
                                print "Locked/protected page"
                                return  
 
 
# Permet à tout le monde de stopper le bot en lui écrivant
def arretdurgence():
        arrettitle = ''.join(u"Discussion utilisateur:JackBot")
        arretpage = pywikibot.Page(pywikibot.getSite(), arrettitle)
        gen = iter([arretpage])
        arret = arretpage.get()
        if arret != u"{{/Stop}}":
                pywikibot.output(u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
                exit(0)
 
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
        if source:
                PagesHS = open(source, 'r')
                while 1:
                        PageHS = PagesHS.readline()
                        fin = PageHS.find("\t")
                        PageHS = PageHS[0:fin]
                        if PageHS == '': break
                        modification(PageHS)
                PagesHS.close()
 
# Traitement d'une catégorie
def crawlerCat(category):
        cat = catlib.Category(site, category)
        pages = cat.articlesList(False)
        for Page in pagegenerators.PreloadingGenerator(pages,100):
                modification(Page.title()) #crawlerLink(Page.title())
        subcat = cat.subcategories(recurse = True)
        for subcategory in subcat:
                pages = subcategory.articlesList(False)
                for Page in pagegenerators.PreloadingGenerator(pages,100):
                        modification(Page.title())
 
# Traitement des pages liées
def crawlerLink(pagename):
        #pagename = unicode(arg[len('-links:'):], 'utf-8')
        page = wikipedia.Page(site, pagename)
        gen = pagegenerators.ReferringPageGenerator(page)
        #gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        for Page in pagegenerators.PreloadingGenerator(gen,100):
                modification(Page.title())
 
# Traitement d'une recherche
def crawlerSearch(pagename):
        gen = pagegenerators.SearchPageGenerator(pagename, namespaces = "0")
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
 
 
# Lancement
TraitementLiens = crawlerLink(u'Modèle:Chapitre')
'''
TraitementWord = modification(u'Utilisateur:JackBot/test')
TraitementCategory = crawlerCat(u'chinois')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot')
TraitementFile = crawlerFile('articles_list.txt')
TraitementRecherche = crawlerSearch(u'chinois')
while 1:
        TraitementRC = crawlerRC()
'''


#!/usr/bin/env python
# coding: utf-8

import pywikibot
from pywikibot import *
import datetime, re
debugLevel = 0

class WikiPage:

    def __init__(self, site, pageName = u''):
        self.site = site
        if pageName != u'': self.page = Page(site, pageName)
        self.summary = u''


    def getContent(self, ns = 0):
        if self.page.exists():
            try:
                revisionDate = self.page.getVersionHistory()[0][1]
            except pywikibot.exceptions.NoPage:
                if debugLevel > 0: print u' no page l 22 ' #+ page.title()
                return u''
            if debugLevel > 1: print revisionDate
            now = datetime.datetime.now()
            if debugLevel > 1: print now
            interval = (now - revisionDate).days
            if debugLevel > 1: print interval
            # Usually a revision is patrolled after 15 days, then the flexion creation can be done
            if interval < 15:
                if debugLevel > 1: print u' recent page ' #+ page.title()

            if (self.page.namespace() == ns or self.page.namespace() == u':') and not self.page.isFlowPage():
                try:
                    if debugLevel > 1: print u' downloading...'
                    pageContent = self.page.get()
                except pywikibot.exceptions.NoPage:
                    if debugLevel > 0: print u' no page ' #+ page.title()
                    return u''
                except pywikibot.exceptions.InvalidPage:
                    if debugLevel > 0: print u' invalid page ' #+ page.title()
                    return u''
                except pywikibot.exceptions.ServerError:
                    if debugLevel > 0: print u' server error ' #+ page.title()
                    return u''
                except pywikibot.exceptions.IsRedirectPage:
                    try:
                        pageContent = self.page.get(get_redirect=True)
                    except:
                        if debugLevel > 0: print u' redirect error ' #+ page.title()
                        return u''
            elif debugLevel > 0: print u' wrong namespace or Flow'
        else:
            if debugLevel > 0: print u' inexistent page ' #+ page.title()
            return u''

        return pageContent


    def addText(self, Page, CodeLangue, Section, Contenu): # pb : propre au WT
        if debugLevel > 1:
            print u'  addText'
            print u'  ' + CodeLangue
            print u'  ' + Section
            print u"\n" + Contenu
        if Page != '' and CodeLangue != '' and Section != '' and Contenu != '':
            if Page.find(Contenu) == -1 and Page.find(u'{{langue|' + CodeLangue + u'}}') != -1:
                if Section == u'catégorie' and Contenu.find(u'[[Catégorie:') == -1: Contenu = u'[[Catégorie:' + Contenu + u']]'
                if Section == u'clé de tri' and Contenu.find(u'{{clé de tri|') == -1: Contenu = u'{{clé de tri|' + Contenu + u'}}'

                # Recherche de l'ordre théorique de la section à ajouter
                NumSection = NumeroSection(Section)
                if NumSection >= len(Sections):
                    if debugLevel > 0:
                        print u'  ajout de ' + Section.encode(config.console_encoding, 'replace')
                        print u'  comme section de nature grammaticale' # entre traductions et prononciation
                        print u'  (car ' + str(len(Sections)) + u' = ' + str(NumSection) + u')'
                    #return Page
                    addSection = False
                    NumSection = NumeroSection(u'prononciation')

                else:
                    addSection = True
                if debugLevel > 1: print u' position S : ' + str(NumSection)

                # Recherche de l'ordre réel de la section à ajouter
                PageTemp2 = Page[Page.find(u'{{langue|' + CodeLangue + u'}}')+len(u'{{langue|' + CodeLangue + u'}}'):]
                #SectionPage = re.findall("{{S\|([^}]+)}}", PageTemp2) # Mais il faut trouver le {{langue}} de la limite de fin
                SectionPage = re.findall(ur"\n=+ *{{S?\|?([^}/|]+)([^}]*)}}", PageTemp2)
                if debugLevel > 1:
                    o = 0
                    while o < len(SectionPage):
                         print u'SectionPage ' + str(SectionPage[o]).encode(config.console_encoding, 'replace')
                         o = o + 1
                    if o == len(SectionPage): o = o - 1
                    raw_input()

                o = 0
                if debugLevel > 0: print u'Taille : ' + str(len(SectionPage[o]))
                if len(SectionPage[o]) > 0:
                    #raw_input(str(SectionPage[0][0].encode(config.console_encoding, 'replace')))
                    # pb encodage : étymologie non fusionnée + catégorie = 1 au lieu de 20 !?
                    #while o < len(SectionPage) and str(SectionPage[o][0].encode(config.console_encoding, 'replace')) != 'langue' and NumeroSection(SectionPage[o][0]) <= NumSection:
                    while o < len(SectionPage) and SectionPage[o][0] != u'langue' and NumeroSection(SectionPage[o][0]) <= NumSection:
                        if debugLevel > 0:
                            print u'SectionPage 0 ' + SectionPage[o][0]
                            print u'NumeroSection : ' + str(NumeroSection(SectionPage[o][0]))
                        o = o + 1
                    o = o - 1
                    if debugLevel > 1: print u' position O : ' + o

                    if debugLevel > 0:
                        print u''
                        print u'Ajout de '
                        print Section.encode(config.console_encoding, 'replace')
                        if o == len(SectionPage) -1:
                            print u' après '
                            print SectionPage[o][0]
                            print u' (car ' + str(NumeroSection(SectionPage[o][0])) + u' < ' + str(NumSection) + u')'
                        else:
                            print u' avant '
                            print SectionPage[o][0]
                            print u' (car ' + str(NumeroSection(SectionPage[o][0])) + u' > ' + str(NumSection) + u')'
                        print u''

                    # Ajout après la section trouvée
                    if PageTemp2.find(u'{{S|' + SectionPage[o][0]) == -1:
                        print 'Erreur d\'encodage'
                        return

                    PageTemp3 = PageTemp2[PageTemp2.find(u'{{S|' + SectionPage[o][0]):]
                    if addSection and SectionPage[o][0] != Section and Section != u'catégorie' and Section != u'clé de tri':
                        if debugLevel > 1: print u' ajout de la section'
                        Contenu = u'\n' + Niveau[NumSection] + u' {{S|' + Section + u'}} ' + Niveau[NumSection] + u'\n' + Contenu

                    # Ajout à la ligne
                    if PageTemp3.find(u'\n==') == -1:
                        regex = ur'\n\[\[\w?\w?\w?:'
                        if re.compile(regex).search(Page):
                            interwikis = re.search(regex, Page).start()
                            categories = Page.find(u'\n[[Catégorie:')
                            defaultSort = Page.find(u'\n{{clé de tri|')

                            if (interwikis < categories or categories == -1) and (interwikis < defaultSort or defaultSort == -1):
                                if debugLevel > 0: print u' ajout avant les interwikis'
                                try:
                                    Page = Page[:interwikis] + u'\n' + Contenu + u'\n' + Page[interwikis:]
                                except:
                                    print u' pb regex interwiki'
                            elif categories != -1 and (categories < defaultSort or defaultSort == -1):
                                if debugLevel > 0: print u' ajout avant les catégories'
                                Page = Page[:Page.find(u'\n[[Catégorie:')] + Contenu + Page[Page.find(u'\n[[Catégorie:'):]
                            elif defaultSort != -1:
                                if debugLevel > 0: print u' ajout avant la clé de tri'
                                Page = Page[:Page.find(u'\n{{clé de tri|')] + Contenu + Page[Page.find(u'\n{{clé de tri|'):]
                            else:
                                if debugLevel > 0: print u' ajout en fin de page'
                                Page = Page + Contenu
                        else:
                            if debugLevel > 0: print u' ajout en fin de page'
                            Page = Page + Contenu
                    else:
                        Page = Page[:-len(PageTemp2)] + PageTemp2[:-len(PageTemp3)] + PageTemp3[:PageTemp3.find(u'\n==')] + Contenu + u'\n\n' + PageTemp3[PageTemp3.find(u'\n=='):]
                    Page = Page.replace(u'\n\n\n', u'\n\n')
        return Page


    def stop(self, userName = u'JackBot'):
        page = pywikibot.Page(site, u'User talk:' + userName)
        if page.exists():
            PageTemp = u''
            try:
                PageTemp = page.get()
            except pywikibot.exceptions.NoPage: return
            except pywikibot.exceptions.IsRedirectPage: return
            except pywikibot.exceptions.ServerError: return
            except pywikibot.exceptions.BadTitle: return
            if PageTemp != u"{{/Stop}}":
                pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
                exit(0)


    def save(self, pageContent, summary, userName = u'JackBot'):
        result = 'ok'
        if debugLevel > 0:
            if len(pageContent) < 6000:
                print(pageContent.encode(config.console_encoding, 'replace'))
            else:
                taille = 6000
                print(pageContent[:taille].encode(config.console_encoding, 'replace'))
                print u'\n[...]\n'
                print(pageContent[len(pageContent)-taille:].encode(config.console_encoding, 'replace'))
            result = raw_input(u'Save? (y/n) ')
        if result != 'n' and result != 'no' and result != 'non':
            #if self.page.title().find(u'Utilisateur:' + userName + u'/') == -1: self.stop(userName)
            if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
            try:
                self.page.put(pageContent, summary)
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


def NumeroSection(Section):
    if debugLevel > 1: print u' NumeroSection()'
    #UnicodeDecodeError: 'ascii' codec can't decode byte 0x82 in position 1: ordinal not in range(128)
    #if isinstance(Section, str): Section = Section
    #if isinstance(Section, str): Section = Section.encode(config.console_encoding, 'replace')
    #if isinstance(Section, str): Section = Section.encode('utf-8')
    #if isinstance(Section, str): Section = Section.decode('ascii')
    #if isinstance(Section, str): Section = Section.decode('ascii').encode(config.console_encoding, 'replace')
    #if isinstance(Section, str): Section = Section.decode('ascii').encode('utf-8')
    #if isinstance(Section, str): Section = unicode(Section)
    #if isinstance(Section, unicode): Section = Section.decode("utf-8")
    
    s = 0
    while s < len(Sections) and Section != Sections[s]:
        s = s + 1
    if s >= len(Sections):
        if debugLevel > 0: print u'  "' + Section + u'" non trouvé'
        #s = 1    # pour éviter de lister les natures grammaticales
    if debugLevel > 1: print u'   ' + Section + u' = ' + str(s)

    return s


Sections = []
Niveau = []
Sections.append(u'étymologie')
Niveau.append(u'===')
Sections.append(u'nom')
Niveau.append(u'===')
Sections.append(u'variantes orthographiques')
Niveau.append(u'====')
Sections.append(u'synonymes')
Niveau.append(u'====')
Sections.append(u'antonymes')
Niveau.append(u'====')
Sections.append(u'dérivés')
Niveau.append(u'====')
Sections.append(u'apparentés')
Niveau.append(u'====')
Sections.append(u'vocabulaire')
Niveau.append(u'====')
Sections.append(u'hyperonymes')
Niveau.append(u'====')
Sections.append(u'hyponymes')
Niveau.append(u'====')
Sections.append(u'méronymes')
Niveau.append(u'====')
Sections.append(u'holonymes')
Niveau.append(u'====')
Sections.append(u'traductions')
Niveau.append(u'====')
Sections.append(u'prononciation')
Niveau.append(u'===')
Sections.append(u'homophones')
Niveau.append(u'====')
Sections.append(u'paronymes')
Niveau.append(u'====')
Sections.append(u'anagrammes')
Niveau.append(u'===')
Sections.append(u'voir aussi')
Niveau.append(u'===')
Sections.append(u'références')
Niveau.append(u'===')
Sections.append(u'catégorie')
Niveau.append(u'')
Sections.append(u'clé de tri')
Niveau.append(u'')

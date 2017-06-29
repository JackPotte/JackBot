#!/usr/bin/env python
# coding: utf-8
'''
Ce script vérifie toutes les URL des articles :
    1) de la forme http://, https:// et [//
    2) incluses dans certains modèles (pas tous étant donnée leur complexité, car certains incluent des {{{1}}} et {{{2}}} dans leurs URL)
    3) il traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}})
    4) il ajoute ou retire {{lien brisé}} le cas échéant
'''

# Déclaration
from __future__ import absolute_import, unicode_literals
import os.path
import pywikibot
from pywikibot import *
import re
import hyperlynx, html2Unicode
import codecs, urllib, urllib2, httplib, json, pprint, urlparse, datetime, re, webbrowser, cookielib, socket, time, ssl
import requests

language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = pywikibot.Site(language,family)

# Préférences
debugLevel = 0
semiauto = False
retablirNonBrise = False    # Reteste les liens brisés
languePage = u'en'

brokenDomains = []
brokenDomains.append('marianne2.fr')    # Site remplacé par marianne.net en mai 2017

blockedDomains = [] # à cause des popovers ou node.js ?
blockedDomains.append(u'bbc.co.uk')
blockedDomains.append(u'biodiversitylibrary.org')
blockedDomains.append(u'charts.fi')
blockedDomains.append(u'cia.gov')
blockedDomains.append(u'finnishcharts.com')
blockedDomains.append(u'history.navy.mil') # IP Free bloquée en lecture
blockedDomains.append(u'itunes.apple.com')
blockedDomains.append(u'nytimes.com')
blockedDomains.append(u'rottentomatoes.com')
blockedDomains.append(u'soundcloud.com')
blockedDomains.append(u'twitter.com')

authorizedFiles = []
authorizedFiles.append(u'.pdf')

# Modèles qui incluent des URL dans leurs pages
ligne = 4
colonne = 2
TabModeles = [[0] * (colonne+1) for _ in range(ligne+1)]
TabModeles[1][1] = u'Import:DAF8'
TabModeles[1][2] = u'http://www.cnrtl.fr/definition/academie8/'
TabModeles[2][1] = u'R:DAF8'
TabModeles[2][2] = u'http://www.cnrtl.fr/definition/academie8/'
TabModeles[3][1] = u'Import:Littré'
TabModeles[3][2] = u'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='
TabModeles[4][1] = u'R:Littré'
TabModeles[4][2] = u'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='

# Modèles qui incluent des URL dans leurs paramètres
ModeleEN = []
ModeleFR = []
ModeleEN.append(u'cite web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'cite news')
ModeleFR.append(u'article')
ModeleEN.append(u'cite journal')
ModeleFR.append(u'article')
ModeleEN.append(u'lien news')
ModeleFR.append(u'article')
ModeleEN.append(u'cite video')
ModeleFR.append(u'lien vidéo')
ModeleEN.append(u'cite episode')
ModeleFR.append(u'citation épisode')
ModeleEN.append(u'cite arXiv')
ModeleFR.append(u'lien arXiv')
ModeleEN.append(u'cite press release')
ModeleFR.append(u'lien web')
ModeleEN.append(u'cite conference')
ModeleFR.append(u'lien conférence')
ModeleEN.append(u'docu')
ModeleFR.append(u'lien vidéo')
ModeleEN.append(u'cite book')
ModeleFR.append(u'ouvrage')
# it
ModeleEN.append(u'cita pubblicazione')
ModeleFR.append(u'article')
limiteL = len(ModeleFR)    # Limite de la liste des modèles traduis de l'anglais (langue=en)

# Modèle avec alias français
ModeleEN.append(u'deadlink')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'webarchive')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'lien brise')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'lien cassé')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'lien mort')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'lien web brisé')
ModeleFR.append(u'lien brisé')
ModeleEN.append(u'lien Web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'cita web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'cita noticia')
ModeleFR.append(u'lien news')
ModeleEN.append(u'web site')
ModeleFR.append(u'lien web')
ModeleEN.append(u'site web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'périodique')
ModeleFR.append(u'article')
ModeleEN.append(u'quote')
ModeleFR.append(u'citation bloc')

# Modèles pour traduire leurs paramètres uniquement
ModeleEN.append(u'lire en ligne')
ModeleFR.append(u'lire en ligne')
ModeleEN.append(u'dts')
ModeleFR.append(u'dts')
ModeleEN.append(u'Chapitre')
ModeleFR.append(u'Chapitre')
limiteM = len(ModeleFR)

# Paramètres à remplacer
ParamEN = []
ParamFR = []
ParamEN.append(u'author')
ParamFR.append(u'auteur')
ParamEN.append(u'authorlink1')
ParamFR.append(u'lien auteur1')
ParamEN.append(u'title')
ParamFR.append(u'titre')
ParamEN.append(u'publisher')
ParamFR.append(u'éditeur')
ParamEN.append(u'work')    # paramètre de {{lien web}} différent pour {{article}}
ParamFR.append(u'périodique')
ParamEN.append(u'newspaper')
ParamFR.append(u'journal')
ParamEN.append(u'day')
ParamFR.append(u'jour')
ParamEN.append(u'month')
ParamFR.append(u'mois')
ParamEN.append(u'year')
ParamFR.append(u'année')
ParamEN.append(u'accessdate')
ParamFR.append(u'consulté le')
ParamEN.append(u'language')
ParamFR.append(u'langue')
ParamEN.append(u'quote')
ParamFR.append(u'extrait')
ParamEN.append(u'titre vo')
ParamFR.append(u'titre original')
ParamEN.append(u'first')
ParamFR.append(u'prénom')
ParamEN.append(u'surname')
ParamFR.append(u'nom')
ParamEN.append(u'last')
ParamFR.append(u'nom')
for p in range(1,31):
    ParamEN.append(u'first'+str(p))
    ParamFR.append(u'prénom'+str(p))
    ParamEN.append(u'given'+str(p))
    ParamFR.append(u'prénom'+str(p))
    ParamEN.append(u'last'+str(p))
    ParamFR.append(u'nom'+str(p))
    ParamEN.append(u'surname'+str(p))
    ParamFR.append(u'nom'+str(p))
    ParamEN.append(u'author'+str(p))
    ParamFR.append(u'auteur'+str(p))
ParamEN.append(u'issue')
ParamFR.append(u'numéro')
ParamEN.append(u'authorlink')
ParamFR.append(u'lien auteur')
ParamEN.append(u'author-link')
ParamFR.append(u'lien auteur')
for p in range(1,10):
    ParamEN.append(u'authorlink'+str(p))
    ParamFR.append(u'lien auteur'+str(p))
    ParamEN.append(u'author'+str(p)+u'link')
    ParamFR.append(u'lien auteur'+str(p))
ParamEN.append(u'coauthorlink')
ParamFR.append(u'lien coauteur')
ParamEN.append(u'coauthor-link')
ParamFR.append(u'lien coauteur')
ParamEN.append(u'surname1')
ParamFR.append(u'nom1')
ParamEN.append(u'coauthors')
ParamFR.append(u'coauteurs')
ParamEN.append(u'co-auteurs')
ParamFR.append(u'coauteurs')
ParamEN.append(u'co-auteur')
ParamFR.append(u'coauteur')
ParamEN.append(u'given')
ParamFR.append(u'prénom')
ParamEN.append(u'trad')
ParamFR.append(u'traducteur')
ParamEN.append(u'at')
ParamFR.append(u'passage')
ParamEN.append(u'origyear')
ParamFR.append(u'année première impression')
ParamEN.append(u'location')
ParamFR.append(u'lieu')
ParamEN.append(u'place')
ParamFR.append(u'lieu')
ParamEN.append(u'publication-date')
ParamFR.append(u'année')
ParamEN.append(u'writers')
ParamFR.append(u'scénario')
ParamEN.append(u'episodelink')
ParamFR.append(u'lien épisode')
ParamEN.append(u'serieslink')
ParamFR.append(u'lien série')
ParamEN.append(u'titlelink')
ParamFR.append(u'lien titre')
ParamEN.append(u'credits')
ParamFR.append(u'crédits')
ParamEN.append(u'network')
ParamFR.append(u'réseau')
ParamEN.append(u'station')
ParamFR.append(u'chaîne')
ParamEN.append(u'city')
ParamFR.append(u'ville')
ParamEN.append(u'began')
ParamFR.append(u'début')
ParamEN.append(u'ended')
ParamFR.append(u'fin')
ParamEN.append(u'diffusion')
ParamFR.append(u'airdate')
ParamEN.append(u'number')
ParamFR.append(u'numéro')
ParamEN.append(u'season')
ParamFR.append(u'saison')
ParamEN.append(u'year2')
ParamFR.append(u'année2')
ParamEN.append(u'month2')
ParamFR.append(u'mois2')
ParamEN.append(u'time')
ParamFR.append(u'temps')
ParamEN.append(u'accessyear')
ParamFR.append(u'année accès')
ParamEN.append(u'accessmonth')
ParamFR.append(u'mois accès')
ParamEN.append(u'conference')
ParamFR.append(u'conférence')
ParamEN.append(u'conferenceurl')
ParamFR.append(u'urlconférence')
ParamEN.append(u'others')
ParamFR.append(u'autres')
ParamEN.append(u'booktitle')
ParamFR.append(u'titre livre')

ParamEN.append(u'en ligne le')
ParamFR.append(u'archivedate')

# espagnol
ParamEN.append(u'autor')
ParamFR.append(u'auteur')
ParamEN.append(u'título')
ParamFR.append(u'titre')
ParamEN.append(u'fechaacceso')
ParamFR.append(u'consulté le')
ParamEN.append(u'fecha')
ParamFR.append(u'date')
ParamEN.append(u'obra')
ParamFR.append(u'série')
ParamEN.append(u'idioma')
ParamFR.append(u'langue')
ParamEN.append(u'publicació')
ParamFR.append(u'éditeur')
ParamEN.append(u'editorial')
ParamFR.append(u'journal')
ParamEN.append(u'series')
ParamFR.append(u'collection')
ParamEN.append(u'agency')
ParamFR.append(u'auteur institutionnel')
ParamEN.append(u'magazine')
ParamFR.append(u'périodique')

# italien
ParamEN.append(u'autore')
ParamFR.append(u'auteur')
ParamEN.append(u'titolo')
ParamFR.append(u'titre')
ParamEN.append(u'accesso')
ParamFR.append(u'consulté le')
ParamEN.append(u'data')
ParamFR.append(u'date')
ParamEN.append(u'nome')
ParamFR.append(u'prénom')
ParamEN.append(u'cognome')
ParamFR.append(u'nom')
ParamEN.append(u'linkautore')
ParamFR.append(u'lien auteur')
ParamEN.append(u'coautori')
ParamFR.append(u'coauteurs')
ParamEN.append(u'rivista')
ParamFR.append(u'journal')
ParamEN.append(u'giorno')
ParamFR.append(u'jour')
ParamEN.append(u'mese')
ParamFR.append(u'mois')
ParamEN.append(u'anno')
ParamFR.append(u'année')
ParamEN.append(u'pagine')
ParamFR.append(u'page')

limiteP = len(ParamEN)
if limiteP != len(ParamFR):
    raw_input(u'Erreur l 227')
    
# URL à remplacer
limiteU = 3
URLDeplace = range(1, limiteU +1)
URLDeplace[1] = u'athena.unige.ch/athena'
URLDeplace[2] = u'un2sg4.unige.ch/athena'

# Caractères délimitant la fin des URL
# http://tools.ietf.org/html/rfc3986
# http://fr.wiktionary.org/wiki/Annexe:Titres_non_pris_en_charge
limiteURL = 14
FinDURL = range(1, limiteURL +1)
FinDURL[1] = u' '
FinDURL[2] = u'\n'
FinDURL[3] = u'['
FinDURL[4] = u']'
FinDURL[5] = u'{'
FinDURL[6] = u'}'
FinDURL[7] = u'<'
FinDURL[8] = u'>'    
FinDURL[9] = u'|'
FinDURL[10] = u'^'
FinDURL[11] = u'\\'
FinDURL[12] = u'`'
FinDURL[13] = u'"'
#FinDURL.append(u'~'    # dans 1ère RFC seulement
# Caractères qui ne peuvent pas être en dernière position d'une URL :
limiteURL2 = 7
FinDURL2 = range(1, limiteURL +1)
FinDURL2[1] = u'.'
FinDURL2[2] = u','
FinDURL2[3] = u';'
FinDURL2[4] = u'!'
FinDURL2[5] = u'?'
FinDURL2[6] = u')' # mais pas ( ou ) simple
FinDURL2[7] = u"'"

ligneB = 6
colonneB = 2
Balise = [[0] * (colonneB+1) for _ in range(ligneB+1)]
Balise[1][1] = u'<pre>'
Balise[1][2] = u'</pre>'
Balise[2][1] = u'<nowiki>'
Balise[2][2] = u'</nowiki>'
Balise[3][1] = u'<ref name='
Balise[3][2] = u'>'
Balise[4][1] = u'<rdf'
Balise[4][2] = u'>'
Balise[5][1] = u'<source'
Balise[5][2] = u'</source' + u'>'
Balise[6][1] = u'\n '
Balise[6][2] = u'\n'
'''
if debugLevel == 0:
    ligneB = ligneB + 1
    Balise[ligneB-1][1] = u'<!--'
    Balise[ligneB-1][2] = u'-->'
'''
limiteE = 20
Erreur = []
Erreur.append("403 Forbidden")
Erreur.append("404 – File not found")
Erreur.append("404 error")
Erreur.append("404 Not Found")
Erreur.append("404. That’s an error.")
Erreur.append("Error 404 - Not found")
Erreur.append("Error 404 (Not Found)")
Erreur.append("Error 503 (Server Error)")
Erreur.append("Page not found")    # bug avec http://www.ifpi.org/content/section_news/plat2000.html et http://www.edinburgh.gov.uk/trams/include/uploads/story_so_far/Tram_Factsheets_2.pdf
Erreur.append("Runtime Error")
Erreur.append("server timedout")
Erreur.append("Sorry, no matching records for query")
Erreur.append("The page you requested cannot be found")
Erreur.append("this page can't be found")
Erreur.append("The service you requested is not available at this time")
Erreur.append("There is currently no text in this page.") # wiki
# En français
Erreur.append("Cette forme est introuvable !")
Erreur.append("Soit vous avez mal &#233;crit le titre")
Erreur.append(u'Soit vous avez mal écrit le titre')
Erreur.append(u'Terme introuvable')
Erreur.append(u"nom de domaine demandé n'est plus actif")
Erreur.append("Il n'y a pour l'instant aucun texte sur cette page.")
    
# Média trop volumineux    
limiteF = 52
Format = range(1, limiteF +1)
# Audio
Format[1] = u'RIFF'
Format[2] = u'WAV'
Format[3] = u'BWF'
Format[4] = u'Ogg'
Format[5] = u'AIFF'
Format[6] = u'CAF'
Format[7] = u'PCM'
Format[8] = u'RAW'
Format[9] = u'CDA'
Format[10] = u'FLAC'
Format[11] = u'ALAC'
Format[12] = u'AC3'
Format[13] = u'MP3'
Format[14] = u'mp3PRO'
Format[15] = u'Ogg Vorbis'
Format[16] = u'VQF'
Format[17] = u'TwinVQ'
Format[18] = u'WMA'
Format[19] = u'AU'
Format[20] = u'ASF'
Format[21] = u'AA'
Format[22] = u'AAC'
Format[23] = u'MPEG-2 AAC'
Format[24] = u'ATRAC'
Format[25] = u'iKlax'
Format[26] = u'U-MYX'
Format[27] = u'MXP4'
# Vidéo
Format[28] = u'avi'
Format[29] = u'mpg'
Format[30] = u'mpeg'
Format[31] = u'mkv'
Format[32] = u'mka'
Format[33] = u'mks'
Format[34] = u'asf'
Format[35] = u'wmv'
Format[36] = u'wma'
Format[37] = u'mov'
Format[38] = u'ogv'
Format[39] = u'oga'
Format[40] = u'ogx'
Format[41] = u'ogm'
Format[42] = u'3gp'
Format[43] = u'3g2'
Format[44] = u'webm'
Format[45] = u'weba'
Format[46] = u'nut'
Format[47] = u'rm'
Format[48] = u'mxf'
Format[49] = u'asx'
Format[50] = u'ts'
Format[51] = u'flv'

# Traduction des mois
ligneM = 12
colonneM = 2
TradM = [[0] * (colonneM+1) for _ in range(ligneM+1)]
TradM[1][1] = u'January'
TradM[1][2] = u'janvier'
TradM[2][1] = u'February'
TradM[2][2] = u'février'
TradM[3][1] = u'March'
TradM[3][2] = u'mars'
TradM[4][1] = u'April'
TradM[4][2] = u'avril'
TradM[5][1] = u'May'
TradM[5][2] = u'mai'
TradM[6][1] = u'June'
TradM[6][2] = u'juin'
TradM[7][1] = u'July'
TradM[7][2] = u'juillet'
TradM[8][1] = u'August'
TradM[8][2] = u'août'
TradM[9][1] = u'September'
TradM[9][2] = u'septembre'
TradM[10][1] = u'October'
TradM[10][2] = u'octobre'
TradM[11][1] = u'November'
TradM[11][2] = u'novembre'
TradM[12][1] = u'December'
TradM[12][2] = u'décembre'

# Traduction des langues
ligneL = 17
colonneL = 2
TradL = [[0] * (colonneL+1) for _ in range(ligneL+1)]
TradL[1][1] = u'French'
TradL[1][2] = u'fr'
TradL[2][1] = u'English'
TradL[2][2] = u'en'
TradL[3][1] = u'German'
TradL[3][2] = u'de'
TradL[4][1] = u'Spanish'
TradL[4][2] = u'es'
TradL[5][1] = u'Italian'
TradL[5][2] = u'it'
TradL[6][1] = u'Portuguese'
TradL[6][2] = u'pt'
TradL[7][1] = u'Dutch'
TradL[7][2] = u'nl'
TradL[8][1] = u'Russian'
TradL[8][2] = u'ru'
TradL[9][1] = u'Chinese'
TradL[9][2] = u'zh'
TradL[10][1] = u'Japanese'
TradL[10][2] = u'ja'
TradL[11][1] = u'Polish'
TradL[11][2] = u'pl'
TradL[12][1] = u'Norwegian'
TradL[12][2] = u'no'
TradL[13][1] = u'Swedish'
TradL[13][2] = u'sv'
TradL[14][1] = u'Finnish'
TradL[14][2] = u'fi'
TradL[15][1] = u'Indonesian'
TradL[15][2] = u'id'
TradL[16][1] = u'Hindi'
TradL[16][2] = u'hi'
TradL[17][1] = u'Arabic'
TradL[17][2] = u'ar'

# Modification du wiki
def hyperlynx(PageTemp, debugLevel = 0):
    if debugLevel > 0:
        print u'------------------------------------'
        #print time.strftime('%d-%m-%Y %H:%m:%S')
    summary = u'Vérification des URL'
    PageEnd = u''
    htmlSource = ''
    url = u''
    PageTemp = PageTemp.replace(u'[//https://', u'[https://')
    PageTemp = PageTemp.replace(u'[//http://', u'[http://')
    PageTemp = PageTemp.replace(u'http://http://', u'http://')
    PageTemp = PageTemp.replace(u'https://https://', u'https://')
    
    # Paramètre langue= si traduction
    for m in range(0, limiteL):
        # Formatage des anciens modèles
        PageTemp = re.sub((u'(Modèle:)?[' + ModeleEN[m][:1] + ur'|' + ModeleEN[m][:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])]).replace(u' ', u'_') + ur' *\|', ModeleEN[m] + ur'|', PageTemp)
        PageTemp = re.sub((u'(Modèle:)?[' + ModeleEN[m][:1] + ur'|' + ModeleEN[m][:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])]).replace(u' ', u'  ') + ur' *\|', ModeleEN[m] + ur'|', PageTemp)
        PageTemp = re.sub((u'(Modèle:)?[' + ModeleEN[m][:1] + ur'|' + ModeleEN[m][:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])]) + ur' *\|', ModeleEN[m] + ur'|', PageTemp)
        # Traitement de chaque modèle à traduire
        while re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]+', PageTemp):
            if debugLevel > 1: raw_input(PageTemp[re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]', PageTemp).end()-1:][:100].encode(config.console_encoding, 'replace'))
            PageEnd = PageEnd + PageTemp[:re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]', PageTemp).end()-1]
            PageTemp = PageTemp[re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]', PageTemp).end()-1:]    
            # Identification du code langue existant dans le modèle
            codelangue = u''
            if PageEnd.rfind(u'{{') != -1:
                PageDebut = PageEnd[:PageEnd.rfind(u'{{')]
                if PageDebut.rfind(u'{{') != -1 and PageDebut.rfind(u'}}') != -1 and (PageDebut[len(PageDebut)-2:] == u'}}' or PageDebut[len(PageDebut)-3:] == u'}} '):
                    codelangue = PageDebut[PageDebut.rfind(u'{{')+2:PageDebut.rfind(u'}}')]
                    if family == 'wikipedia' or family == 'wiktionary':
                        # Recherche de validité mais tous les codes ne sont pas encore sur les sites francophones
                        page2 = Page(site,u'Modèle:' + codelangue)
                        try:
                            PageCode = page2.get()
                        except wikipedia.NoPage:
                            print "NoPage l 425"
                            PageCode = u''
                        except wikipedia.LockedPage: 
                            print "Locked l 428"
                            PageCode = u''
                        except wikipedia.IsRedirectPage: 
                            PageCode = page2.get(get_redirect=True)
                        if debugLevel > 0: print(PageCode.encode(config.console_encoding, 'replace'))
                        if PageCode.find(u'Indication de langue') != -1:
                            if len(codelangue) == 2:    # or len(codelangue) == 3: if codelangue == u'pdf': |format=codelangue, absent de {{lien web}}
                                # Retrait du modèle de langue devenu inutile
                                PageEnd = PageEnd[:PageEnd.rfind(u'{{' + codelangue + u'}}')] + PageEnd[PageEnd.rfind(u'{{' + codelangue + u'}}')+len(u'{{' + codelangue + u'}}'):]
            if codelangue == u'':
                if debugLevel > 0: print u' Code langue à remplacer une fois trouvé sur la page distante...'
                codelangue = 'JackBot'
            # Ajout du code langue dans le modèle
            if debugLevel > 0: print u'Modèle préalable : ' + codelangue.encode(config.console_encoding, 'replace')
            if not re.search(u'[^}]*langu[ag]*e *=[^}]*}}', PageTemp):
                PageTemp = u'|langue=' + codelangue + PageTemp
            elif re.search(u'[^}]*langu[ag]*e *=[^}]*}}', PageTemp).end() > PageTemp.find(u'}}')+2:
                PageTemp = u'|langue=' + codelangue + PageTemp
                
        PageTemp = PageEnd + PageTemp
        PageEnd = u''
            
    for m in range(0, limiteM):
        if debugLevel > 1: print(u' Traduction des noms du modèle ' + ModeleEN[m])
        PageTemp = PageTemp.replace(u'{{' + ModeleEN[m] + u' ', u'{{' + ModeleEN[m] + u'')
        PageTemp = re.sub(ur'({{[\n ]*)[' + ModeleEN[m][0:1] + ur'|' + ModeleEN[m][0:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])] + ur'( *[\||\n\t|}])', ur'\1' +  ModeleFR[m] + ur'\2', PageTemp)
        # Suppression des modèles vides
        regex = u'{{ *[' + ModeleFR[m][0:1] + ur'|' + ModeleFR[m][0:1].upper() + ur']' + ModeleFR[m][1:len(ModeleFR[m])] + ur' *}}'
        while re.search(regex, PageTemp):
            if debugLevel > 1: print(u' while1' + regex)
            PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + PageTemp[re.search(regex, PageTemp).end():]
        # Traduction des paramètres de chaque modèle de la page
        regex = u'{{ *[' + ModeleFR[m][0:1] + ur'|' + ModeleFR[m][0:1].upper() + ur']' + ModeleFR[m][1:len(ModeleFR[m])] + ur' *[\||\n]'
        while re.search(regex, PageTemp):
            if debugLevel > 1: print(u' while2')
            PageEnd = PageEnd + PageTemp[:re.search(regex, PageTemp).start()+2]
            PageTemp = PageTemp[re.search(regex, PageTemp).start()+2:]
            FinPageURL = PageTemp
            FinModele = 0
            # Gestion des modèles inclus dans le modèle de lien
            while FinPageURL.find(u'{{') != -1 and FinPageURL.find(u'{{') < FinPageURL.find(u'}}'):
                if debugLevel > 1: print(u'  while3')
                FinModele = FinModele + FinPageURL.find(u'}}')+2
                FinPageURL = FinPageURL[FinPageURL.find(u'}}')+2:]
            FinModele = FinModele + FinPageURL.find(u'}}')+2
            
            ModeleCourant = PageTemp[:FinModele]
            if debugLevel > 1: raw_input(ModeleCourant.encode(config.console_encoding, 'replace'))
            for p in range(0, limiteP):
                # Faux-amis variables selon les modèles
                if debugLevel > 1: print ParamEN[p].encode(config.console_encoding, 'replace')
                tradFr = ParamFR[p]
                if ParamEN[p] == u'work':
                    if (ModeleCourant.find(u'rticle') != -1 and ModeleCourant.find(u'rticle') < ModeleCourant.find(u'|')) and ModeleCourant.find(u'ériodique') == -1:
                        tradFr = u'périodique'
                    elif ModeleCourant.find(u'ien web') != -1 and ModeleCourant.find(u'ien web') < ModeleCourant.find(u'|'):
                        tradFr = u'série'
                elif ParamEN[p] == u'publisher':
                    if (ModeleCourant.find(u'rticle') != -1 and ModeleCourant.find(u'rticle') < ModeleCourant.find(u'|')) and ModeleCourant.find(u'ériodique') == -1 and ModeleCourant.find(u'|work=') == -1:
                        tradFr = u'périodique'
                    else:
                        tradFr = u'éditeur'
                elif ParamEN[p] == u'language' and (ModeleCourant.find(u'|langue=') != -1 and ModeleCourant.find(u'|langue=') < ModeleCourant.find(u'}}')):
                    tradFr = u''
                elif ParamEN[p] == u'issue' and (ModeleCourant.find(u'|numéro=') != -1 and ModeleCourant.find(u'|numéro=') < ModeleCourant.find(u'}}')):
                    tradFr = u'date'
                elif ParamEN[p] == u'en ligne le':
                    if ModeleCourant.find(u'archiveurl') == -1 and ModeleCourant.find(u'archive url') == -1 and ModeleCourant.find(u'archive-url') == -1:
                        continue
                    elif ModeleCourant.find(u'archivedate') != -1 or ModeleCourant.find(u'archive date') != -1 or ModeleCourant.find(u'archive-date') != -1:
                            continue
                    elif debugLevel > 0: u' archiveurl ' + u' archivedate'

                ModeleCourant = re.sub(ur'(\| *)' + ParamEN[p] + ur'( *=)', ur'\1' + tradFr + ur'\2', ModeleCourant)
                ModeleCourant = ModeleCourant.replace(u'|=',u'|')
                ModeleCourant = ModeleCourant.replace(u'| =',u'|')
                ModeleCourant = ModeleCourant.replace(u'|  =',u'|')
                ModeleCourant = ModeleCourant.replace(u'|}}',u'}}')
                ModeleCourant = ModeleCourant.replace(u'| }}',u'}}')
                if ModeleCourant.find(u'{{') == -1:    # Sans modèle inclus
                    ModeleCourant = ModeleCourant.replace(u'||',u'|')
            if debugLevel > 1: print FinModele
            
            PageTemp = ModeleCourant + PageTemp[FinModele:]
            
        PageTemp = PageEnd + PageTemp
        PageEnd = u''
    
    
    # Traduction des dates
    limiteParamDate = 9
    ParamDate = range(1, limiteParamDate +1)
    ParamDate[1] = u'date'
    ParamDate[2] = u'mois'
    ParamDate[3] = u'consulté le'
    ParamDate[4] = u'en ligne le'
    # Modèle
    ParamDate[5] = u'dts'
    ParamDate[6] = u'Dts'
    ParamDate[7] = u'date triable'
    ParamDate[8] = u'Date triable'
    for m in range(1, ligneM+1):
        if debugLevel > 1:
            print u'Mois ' + str(m)
            print TradM[m][1]
        for p in range(1, limiteParamDate):
            if debugLevel > 1: print u'Recherche de ' + ParamDate[p] + u' *=[ ,0-9]*' + TradM[m][1]
            if p > 4:
                PageTemp = re.sub(ur'({{ *' + ParamDate[p] + ur'[^}]+)' + TradM[m][1] + ur'([^}]+}})', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
                PageTemp = re.sub(ur'({{ *' + ParamDate[p] + ur'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' + TradM[m][2] + ur'(\|[ 0-9][ 0-9])}}', ur'\1\3|' +  TradM[m][2] + ur'\2}}', PageTemp)
            else:
                PageTemp = re.sub(ur'(\| *' + ParamDate[p] + ur' *=[ ,0-9]*)' + TradM[m][1] + ur'([ ,0-9]*\.? *[<|\||\n\t|}])', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
                PageTemp = re.sub(ur'(\| *' + ParamDate[p] + ur' *=[ ,0-9]*)' + TradM[m][1][:1].lower() + TradM[m][1][1:] + ur'([ ,0-9]*\.? *[<|\||\n\t|}])', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
                
                # Ordre des dates : jj mois aaaa'
                if debugLevel > 1: print u'Recherche de ' + ParamDate[p] + u' *= *' + TradM[m][2] + u' *([0-9]+), '
                PageTemp = re.sub(ur'(\| *' + ParamDate[p] + u' *= *)' + TradM[m][2] + ur' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])', ur'\1' + ur'\2' + ur' ' + TradM[m][2] + ur' ' + ur'\3' + ur'\4', PageTemp)    # trim(u'\3') ne fonctionne pas
                
    if debugLevel > 0: print u'Traduction des langues'
    for l in range(1, ligneL+1):
        if debugLevel > 1:
            print u'Langue ' + str(l)
            print TradL[l][1]
        PageTemp = re.sub(ur'(\| *langue *= *)' + TradL[l][1] + ur'( *[<|\||\n\t|}])', ur'\1' +  TradL[l][2] + ur'\2', PageTemp)
    
        # Rustine suite à un imprévu censé être réglé ci-dessus, mais qui touche presque 10 % des pages.
        PageTemp = re.sub(ur'{{' + TradL[l][2] + ur'}}[ \n]*({{[Aa]rticle\|langue=' + TradL[l][2] + ur'\|)', ur'\1', PageTemp)
        PageTemp = re.sub(ur'{{' + TradL[l][2] + ur'}}[ \n]*({{[Ll]ien web\|langue=' + TradL[l][2] + ur'\|)', ur'\1', PageTemp)
        PageTemp = re.sub(ur'{{' + TradL[l][2] + ur'}}[ \n]*({{[Oo]uvrage\|langue=' + TradL[l][2] + ur'\|)', ur'\1', PageTemp)
    
    # Suppression des paramètres vides en doublon
    # à faire...
    
    if debugLevel > 1:
        print u'Fin des traductions :'
        raw_input(PageTemp.encode(config.console_encoding, 'replace'))    

    # Recherche de chaque hyperlien en clair ------------------------------------------------------------------------------------------------------------------------------------
    while PageTemp.find(u'//') != -1:
        if debugLevel > 0: print u'-----------------------------------------------------------------'
        url = u''
        DebutURL = u''
        CharFinURL = u''
        titre = u''
        FinModele = 0
        LienBrise = False
        # Avant l'URL
        PageDebut = PageTemp[:PageTemp.find(u'//')]
        while PageTemp.find(u'//') > PageTemp.find(u'}}') and PageTemp.find(u'}}') != -1:
            if debugLevel > 0: print u'URL après un modèle'
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
            PageTemp = PageTemp[PageTemp.find(u'}}')+2:]

        # Balises interdisant la modification de l'URL
        ignoredLink = False
        for b in range(1,ligneB):
            if PageDebut.rfind(Balise[b][1]) != -1 and PageDebut.rfind(Balise[b][1]) > PageDebut.rfind(Balise[b][2]):
                ignoredLink = True
                if debugLevel > 0: print u'URL dans ' + Balise[b][1]
                break
            if PageEnd.rfind(Balise[b][1]) != -1 and PageEnd.rfind(Balise[b][1]) > PageEnd.rfind(Balise[b][2]):
                ignoredLink = True
                if debugLevel > 0: print u'URL dans ' + Balise[b][1]
                break
        if ignoredLink == False:
            # titre=
            if PageDebut.rfind(u'titre=') != -1 and PageDebut.rfind(u'titre=') > PageDebut.rfind(u'{{') and PageDebut.rfind(u'titre=') > PageDebut.rfind(u'}}'):
                PageTemp3 = PageDebut[PageDebut.rfind(u'titre=')+len(u'titre='):len(PageDebut)]
                if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.rfind(u'}}') == -1):
                    titre = PageTemp3[0:PageTemp3.find(u'|')]
                else:
                    titre = PageTemp3[0:len(PageTemp3)]
                if debugLevel > 0: print u'Titre avant URL'
            elif PageDebut.rfind(u'titre =') != -1 and PageDebut.rfind(u'titre =') > PageDebut.rfind(u'{{') and PageDebut.rfind(u'titre =') > PageDebut.rfind(u'}}'):
                PageTemp3 = PageDebut[PageDebut.rfind(u'titre =')+len(u'titre ='):len(PageDebut)]
                if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.rfind(u'}}') == -1):
                    titre = PageTemp3[0:PageTemp3.find(u'|')]
                else:
                    titre = PageTemp3[0:len(PageTemp3)]
                if debugLevel > 0: print u'Titre avant URL'
        
            # url=
            if PageDebut[len(PageDebut)-1:len(PageDebut)] == u'[':
                if debugLevel > 0: print u'URL entre crochets sans protocole'
                DebutURL = 1
            elif PageDebut[len(PageDebut)-5:len(PageDebut)] == u'http:':
                if debugLevel > 0: print u'URL http'
                DebutURL = 5
            elif PageDebut[len(PageDebut)-6:len(PageDebut)] == u'https:':
                if debugLevel > 0: print u'URL https'
                DebutURL = 6
            elif PageDebut[len(PageDebut)-2:len(PageDebut)] == u'{{':
                if debugLevel > 0: print u"URL d'un modèle"
                break
            else:
                if debugLevel > 0: print u'URL sans http ni crochet'
                DebutURL = 0
            if DebutURL != 0:
                # Après l'URL
                FinPageURL = PageTemp[PageTemp.find(u'//'):]
                # url=    
                CharFinURL = u' '
                for l in range(1,limiteURL):
                    if FinPageURL.find(CharFinURL) == -1 or (FinPageURL.find(FinDURL[l]) != -1 and FinPageURL.find(FinDURL[l]) < FinPageURL.find(CharFinURL)):
                        CharFinURL = FinDURL[l]
                if debugLevel > 0: print u'*Caractère de fin URL : ' + CharFinURL
                
                if DebutURL == 1:
                    url = u'http:' + PageTemp[PageTemp.find(u'//'):PageTemp.find(u'//')+FinPageURL.find(CharFinURL)]
                    if titre == u'':
                        titre = PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):]
                        titre = trim(titre[:titre.find(u']')])
                else:
                    url = PageTemp[PageTemp.find(u'//')-DebutURL:PageTemp.find(u'//')+FinPageURL.find(CharFinURL)]
                if len(url) <= 10:
                    url = u''
                    htmlSource = u''
                    LienBrise = False
                else:
                    for u in range(1,limiteURL2):
                        while url[len(url)-1:] == FinDURL2[u]:
                            url = url[:len(url)-1]
                            if debugLevel > 0: print u'Réduction de l\'URL de ' + FinDURL2[u]
                    
                    Media = False
                    for f in range(1,limiteF):
                        if url[len(url)-len(Format[f])-1:].lower() == u'.' + Format[f].lower():
                            if debugLevel > 0:
                                print url.encode(config.console_encoding, 'replace')
                                print u'Média détecté (memory error potentielle)'
                            Media = True
                    if Media == False:
                        if debugLevel > 0: print(u'Recherche de la page distante')
                        htmlSource = TestURL(url, debugLevel)
                        if debugLevel > 0: print(u'Recherche dans son contenu')
                        LienBrise = TestPage(htmlSource, url)
                
                # Site réputé HS, mais invisible car ses sous-pages ont toutes été déplacées, et renvoient vers l'accueil
                for u in range(1,limiteU):
                    if url.find(URLDeplace[u]) != -1 and len(url) > len(URLDeplace[u]) + 8:    #http://.../
                        LienBrise = True
                
                # Confirmation manuelle
                if semiauto == True:
                    webbrowser.open_new_tab(url)
                    if LienBrise == True:
                        result = raw_input("Lien brisé ? (o/n) ")
                    else:
                        result = raw_input("Lien fonctionnel ? (o/n) ")
                    if result != "n" and result != "no" and result != "non":
                        LienBrise = True
                    else:
                        LienBrise = False
                        
                if debugLevel > 0:
                    # Compte-rendu des URL détectées
                    try:
                        print u'*URL : ' + url.encode(config.console_encoding, 'replace')
                        print u'*Titre : ' + titre.encode(config.console_encoding, 'replace')
                        print u'*HS : ' + str(LienBrise)
                        print type(htmlSource)
                    except UnicodeDecodeError:
                        print u'*HS : ' + str(LienBrise)
                        print "UnicodeDecodeError l 466"
                if debugLevel > 1: raw_input (htmlSource[:7000])
                
                # Modification du wiki en conséquence    
                DebutPage = PageTemp[0:PageTemp.find(u'//')+2]
                DebutURL = max(DebutPage.find(u'http://'),DebutPage.find(u'https://'),DebutPage.find(u'[//'))
                
                # Saut des modèles inclus dans un modèle de lien
                while DebutPage.rfind(u'{{') != -1 and DebutPage.rfind(u'{{') < DebutPage.rfind(u'}}'):
                    # pb des multiples crochets fermants sautés : {{ ({{ }} }})
                    PageTemp2 = DebutPage[DebutPage.rfind(u'{{'):]
                    if PageTemp2.rfind(u'}}') == PageTemp2.rfind(u'{{'):
                        DebutPage = DebutPage[:DebutPage.rfind(u'{{')]
                    else:
                        DebutPage = u''
                        break
                    if debugLevel > 1: raw_input(DebutPage[-100:].encode(config.console_encoding, 'replace'))
                    
                
                # Détection si l'hyperlien est dans un modèle (si aucun modèle n'est fermé avant eux)
                if DebutPage.rfind(u'{{') != -1 and DebutPage.rfind(u'{{') > DebutPage.rfind(u'}}'):
                    DebutModele = DebutPage.rfind(u'{{')
                    DebutPage = DebutPage[DebutPage.rfind(u'{{'):len(DebutPage)]
                    AncienModele = u''
                    # Lien dans un modèle connu (consensus en cours pour les autres, atention aux infobox)
                    '''for m in range(1,limiteM):
                        regex = u'{{ *[' + ModeleFR[m][0:1] + ur'|' + ModeleFR[m][0:1].upper() + ur']' + ModeleFR[m][1:len(ModeleFR[m])] + ur' *[\||\n]'
                    ''' 
                    if re.search(u'{{ *[L|l]ien web *[\||\n]', DebutPage):
                        AncienModele = u'lien web'
                        if debugLevel > 0: print u'Détection de ' + AncienModele
                    elif re.search('{{ *[L|l]ire en ligne *[\||\n]', DebutPage):
                        AncienModele = u'lire en ligne'
                        if debugLevel > 0: print u'Détection de ' + AncienModele
                    elif retablirNonBrise == True and re.search(u'{{ *[L|l]ien brisé *[\||\n]', DebutPage):
                        AncienModele = u'lien brisé'
                        if debugLevel > 0: print u'Détection de ' + AncienModele
                        
                    #if DebutPage[0:2] == u'{{': AncienModele = trim(DebutPage[2:DebutPage.find(u'|')])
                    
                    FinModele = PageTemp.find(u'//')+2
                    FinPageModele = PageTemp[FinModele:len(PageTemp)]
                    # Calcul des modèles inclus dans le modèle de lien
                    while FinPageModele.find(u'}}') != -1 and FinPageModele.find(u'}}') > FinPageModele.find(u'{{') and FinPageModele.find(u'{{') != -1:
                        FinModele = FinModele + FinPageModele.find(u'}}')+2
                        FinPageModele = FinPageModele[FinPageModele.find(u'}}')+2:len(FinPageModele)]
                    FinModele = FinModele + FinPageModele.find(u'}}')+2
                    ModeleCourant = PageTemp[DebutModele:FinModele]
                    #if debugLevel > 0: print "*Modele : " + ModeleCourant[:100].encode(config.console_encoding, 'replace')
                    
                    if AncienModele != u'':
                        if debugLevel > 0: print u'Ancien modèle à traiter : ' + AncienModele
                        if LienBrise == True:
                            try:
                                PageTemp = PageTemp[:DebutModele] + u'{{lien brisé' + PageTemp[re.search(u'{{ *[' + AncienModele[:1] + u'|' + AncienModele[:1].upper() + u']' + AncienModele[1:] + u' *[\||\n]', PageTemp).end()-1:]
                            except AttributeError:
                                raise "Regex introuvable ligne 811"
                                
                        elif AncienModele == u'lien brisé':
                            if debugLevel > 0: print u'Rétablissement d\'un ancien lien brisé'
                            PageTemp = PageTemp[:PageTemp.find(AncienModele)] + u'lien web' + PageTemp[PageTemp.find(AncienModele)+len(AncienModele):]
                        '''
                        # titre=
                        if re.search(u'\| *titre *=', FinPageURL):
                            if debugLevel > 0: print u'Titre après URL'
                            if titre == u'' and re.search(u'\| *titre *=', FinPageURL).end() != -1 and re.search(u'\| *titre *=', FinPageURL).end() < FinPageURL.find(u'\n') and re.search(u'\| *titre *=', FinPageURL).end() < FinPageURL.find(u'}}'):
                                PageTemp3 = FinPageURL[re.search(u'\| *titre *=', FinPageURL).end():]
                                # Modèles inclus dans les titres
                                while PageTemp3.find(u'{{') != -1 and PageTemp3.find(u'{{') < PageTemp3.find(u'}}') and PageTemp3.find(u'{{') < PageTemp3.find(u'|'):
                                    titre = titre + PageTemp3[:PageTemp3.find(u'}}')+2]
                                    PageTemp3 = PageTemp3[PageTemp3.find(u'}}')+2:]
                                if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.find(u'}}') == -1):
                                    titre = titre + PageTemp3[0:PageTemp3.find(u'|')]
                                else:
                                    titre = titre + PageTemp3[0:PageTemp3.find(u'}}')]
                        elif FinPageURL.find(u']') != -1 and (PageTemp.find(u'//') == PageTemp.find(u'[//')+1 or PageTemp.find(u'//') == PageTemp.find(u'[http://')+6 or PageTemp.find(u'//') == PageTemp.find(u'[https://')+7):
                            titre = FinPageURL[FinPageURL.find(CharFinURL)+len(CharFinURL):FinPageURL.find(u']')]
                        if debugLevel > 1: raw_input(FinPageURL.encode(config.console_encoding, 'replace'))    
                        
                        # En cas de modèles inclus le titre a pu ne pas être détecté précédemment
                        if titre == u'' and re.search(u'\| *titre *=', ModeleCourant):
                            PageTemp3 = ModeleCourant[re.search(u'\| *titre *=', ModeleCourant).end():]
                            # Modèles inclus dans les titres
                            while PageTemp3.find(u'{{') != -1 and PageTemp3.find(u'{{') < PageTemp3.find(u'}}') and PageTemp3.find(u'{{') < PageTemp3.find(u'|'):
                                titre = titre + PageTemp3[:PageTemp3.find(u'}}')+2]
                                PageTemp3 = PageTemp3[PageTemp3.find(u'}}')+2:]
                            titre = titre + PageTemp3[:re.search(u'[^\|}\n]*', PageTemp3).end()]
                            if debugLevel > 0:
                                print u'*Titre2 : '
                                print titre.encode(config.console_encoding, 'replace')
                            
                        if LienBrise == True and AncienModele != u'lien brisé' and AncienModele != u'Lien brisé':
                            summary = summary + u', remplacement de ' + AncienModele + u' par {{lien brisé}}'
                            if debugLevel > 0: print u', remplacement de ' + AncienModele + u' par {{lien brisé}}'
                            if titre == u'':
                                PageTemp = PageTemp[0:DebutModele] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[FinModele:len(PageTemp)]
                            else:
                                PageTemp = PageTemp[0:DebutModele] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[FinModele:len(PageTemp)]
                        elif LienBrise == False and (AncienModele == u'lien brisé' or AncienModele == u'Lien brisé'):
                            summary = summary + u', Retrait de {{lien brisé}}'
                            PageTemp = PageTemp[0:DebutModele] + u'{{lien web' + PageTemp[DebutModele+len(u'lien brisé')+2:len(PageTemp)]
                        '''
                            
                        '''elif LienBrise == True:
                        summary = summary + u', ajout de {{lien brisé}}'
                        if DebutURL == 1:
                            if debugLevel > 0: print u'Ajout de lien brisé entre crochets 1'
                            # Lien entre crochets
                            PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
                        else:
                            if debugLevel > 0: print u'Ajout de lien brisé 1'
                            if PageTemp[DebutURL-1:DebutURL] == u'[' and PageTemp[DebutURL-2:DebutURL] != u'[[': DebutURL = DebutURL -1
                            if CharFinURL == u' ' and FinPageURL.find(u']') != -1 and (FinPageURL.find(u'[') == -1 or FinPageURL.find(u']') < FinPageURL.find(u'[')): 
                                # Présence d'un titre
                                PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL)+1:PageTemp.find(u'//')+FinPageURL.find(u']')]  + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
                            elif CharFinURL == u']':
                                PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):len(PageTemp)]
                            else:
                                PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):len(PageTemp)]
                        '''
                    else:
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " dans modèle non géré"
                    
                else:
                    if debugLevel > 0: print u'URL hors modèle'
                    if LienBrise == True:
                        summary = summary + u', ajout de {{lien brisé}}'
                        if DebutURL == 1:
                            if debugLevel > 0: print u'Ajout de lien brisé entre crochets sans protocole'
                            if titre != u'':
                                PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):]
                            else:
                                PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):]
                            #if debugLevel > 0: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
                        else:
                            if debugLevel > 0: print u'Ajout de lien brisé 2'
                            if PageTemp[DebutURL-1:DebutURL] == u'[' and PageTemp[DebutURL-2:DebutURL] != u'[[':
                                if debugLevel > 0: print u'entre crochet'
                                DebutURL = DebutURL -1
                                if titre == u'' :
                                    if debugLevel > 0: "Titre vide"
                                    # Prise en compte des crochets inclus dans un titre
                                    PageTemp2 = PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):]
                                    #if debugLevel > 0: raw_input(PageTemp2.encode(config.console_encoding, 'replace'))
                                    if PageTemp2.find(u']]') != -1 and PageTemp2.find(u']]') < PageTemp2.find(u']'):
                                        while PageTemp2.find(u']]') != -1 and PageTemp2.find(u'[[') != -1 and PageTemp2.find(u'[[') < PageTemp2.find(u']]'):
                                            titre = titre + PageTemp2[:PageTemp2.find(u']]')+1]
                                            PageTemp2 = PageTemp2[PageTemp2.find(u']]')+1:]
                                        titre = trim(titre + PageTemp2[:PageTemp2.find(u']]')])
                                        PageTemp2 = PageTemp2[PageTemp2.find(u']]'):]
                                    while PageTemp2.find(u']') != -1 and PageTemp2.find(u'[') != -1 and PageTemp2.find(u'[') < PageTemp2.find(u']'):
                                        titre = titre + PageTemp2[:PageTemp2.find(u']')+1]
                                        PageTemp2 = PageTemp2[PageTemp2.find(u']')+1:]
                                    titre = trim(titre + PageTemp2[:PageTemp2.find(u']')])
                                    PageTemp2 = PageTemp2[PageTemp2.find(u']'):]
                                if titre != u'':
                                    if debugLevel > 0: "Ajout avec titre"
                                    PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[len(PageTemp)-len(PageTemp2)+1:len(PageTemp)]
                                else:
                                    if debugLevel > 0: "Ajout sans titre"
                                    PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
                            else:    
                                if titre != u'': 
                                    # Présence d'un titre
                                    if debugLevel > 0: print u'URL nue avec titre'
                                    PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL)+1:PageTemp.find(u'//')+FinPageURL.find(u']')]  + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
                                else:
                                    if debugLevel > 0: print u'URL nue sans titre'
                                    PageTemp = PageTemp[:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}} ' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):len(PageTemp)]
                        
                    else:
                        if debugLevel > 0: print u'Aucun changement sur l\'URL http'
            else:
                if debugLevel > 0: print u'Aucun changement sur l\'URL non http'    
        else:
            if debugLevel > 1: print u'URL entre balises sautée'

        # Lien suivant, en sautant les URL incluses dans l'actuelle, et celles avec d'autres protocoles que http(s)
        if FinModele == 0 and LienBrise == False:
            FinPageURL = PageTemp[PageTemp.find(u'//')+2:len(PageTemp)]
            CharFinURL = u' '
            for l in range(1,limiteURL):
                if FinPageURL.find(FinDURL[l]) != -1 and FinPageURL.find(FinDURL[l]) < FinPageURL.find(CharFinURL):
                    CharFinURL = FinDURL[l]
            if debugLevel > 0: print u'Saut après ' + CharFinURL
            PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'//')+2+FinPageURL.find(CharFinURL)]
            PageTemp = PageTemp[PageTemp.find(u'//')+2+FinPageURL.find(CharFinURL):len(PageTemp)]
        else:
            # Saut du reste du modèle courant (contenant parfois d'autres URL à laisser)
            if debugLevel > 0: print u'Saut après }}'
            PageEnd = PageEnd + PageTemp[:FinModele]
            PageTemp = PageTemp[FinModele:]
        if debugLevel > 1: raw_input(PageEnd.encode(config.console_encoding, 'replace'))

    PageTemp = PageEnd + PageTemp
    PageEnd    = u''    
    if debugLevel > 0: print ("Fin des tests URL")
    
    # Recherche de chaque hyperlien de modèles ------------------------------------------------------------------------------------------------------------------------------------
    if PageTemp.find(u'{{langue') != -1: # du Wiktionnaire
        if debugLevel > 0: print ("Modèles Wiktionnaire")
        for m in range(1,ligne):
            PagEnd = u''
            while PageTemp.find(u'{{' + TabModeles[m][1] + u'|') != -1:
                PageEnd =  PageEnd + PageTemp[0:PageTemp.find(u'{{' + TabModeles[m][1] + u'|')+len(u'{{' + TabModeles[m][1] + u'|')]
                PageTemp =  PageTemp[PageTemp.find(u'{{' + TabModeles[m][1] + u'|')+len(u'{{' + TabModeles[m][1] + u'|'):len(PageTemp)]
                if PageTemp[0:PageTemp.find(u'}}')].find(u'|') != -1:
                    Param1Encode = PageTemp[0:PageTemp.find(u'|')].replace(u' ',u'_')
                else:
                    Param1Encode = PageTemp[0:PageTemp.find(u'}}')].replace(u' ',u'_')
                htmlSource = TestURL(TabModeles[m][2] + Param1Encode, debugLevel)
                LienBrise = TestPage(htmlSource,url)
                if LienBrise == True: PageEnd = PageEnd[0:PageEnd.rfind(u'{{' + TabModeles[m][1] + u'|')] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + TabModeles[m][2]
            PageTemp = PageEnd + PageTemp
            PageEnd = u''
        PageTemp = PageEnd + PageTemp
        PageEnd = u''
    if debugLevel > 0: print (u'Fin des tests modèle')
    
    # Paramètre inutile ?
    '''while PageTemp.find(u'|deadurl=no|') != -1:
        PageTemp = PageTemp[0:PageTemp.find(u'|deadurl=no|')+1] + PageTemp[PageTemp.find(u'|deadurl=no|')+len(u'|deadurl=no|'):len(PageTemp)]'''
    # Si dans {{ouvrage}} "lire en ligne" est vide, cela bloque le paramètre "url"
    PageTemp = re.sub(ur'{{(o|O)uvrage(\||\n[^}]*)\| *lire en ligne *= *([\||}|\n]+)', ur'{{\1uvrage\2\3', PageTemp)
    # Idem dans {{article}} : "éditeur" vide bloque "périodique", "journal" ou "revue"
    PageTemp = re.sub(ur'{{(a|A)rticle(\||\n[^}]*)\| *éditeur *= *([\||}|\n]+)', ur'{{\1rticle\2\3', PageTemp)
            
    # Recherche de la langue sur le web
    languePage = u'en'
    try:
        regex = u'<html [^>]*lang *= *"?\'?([a-zA-Z\-]+)'
        result = re.search(regex, htmlSource)
        if result:
            languePage = result.group(1)
            if debugLevel > 0: print u' Langue trouvée sur le site'
            if (len(languePage)) > 6: languePage = u'en'
    except UnicodeDecodeError:
        if debugLevel > 0: print u'UnicodeEncodeError l 1032'

    if debugLevel > 0: print u' Langue retenue : ' + languePage
    try:
        PageTemp = PageTemp.replace(u'|langue=JackBot',u'|langue='+languePage)
    except UnicodeDecodeError:
        if debugLevel > 0: print u'UnicodeEncodeError l 1038'
        PageTemp = PageTemp.replace(u'|langue=JackBot',u'|langue=en')
    
    PageEnd = PageEnd + PageTemp
    PageEnd = PageEnd.replace(u'lien mortarchive', u'lien mort archive')
    if debugLevel > 0: print(u'Fin hyperlynx.py')
    return PageEnd

def TestURL(url, debugLevel = 0):
    # Renvoie la page web d'une URL dès qu'il arrive à la lire.
    if debugLevel > 0: print u'--------'

    for blacklisted in brokenDomains:
        if url.find(blacklisted) != -1:
            if debugLevel > 0: print(u' broken domain')
            return 'ko'
    for whitelisted in blockedDomains:
        if url.find(whitelisted) != -1:
            if debugLevel > 0: print(u' authorized domain')
            return 'ok'
    for whitelisted in authorizedFiles:
        if url[len(url)-len(whitelisted):] == whitelisted:
            if debugLevel > 0: print(u' authorized file')
            return 'ok'

    htmlSource = u''
    connectionMethod = u'Request'
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)  # TODO : ssl.CertificateError: hostname 'www.mediarodzina.com.pl' doesn't match either of 'mediarodzina.pl', 'www.mediarodzina.pl'
        htmlSource = res.read()
        if debugLevel > 0: print str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException' # ex : got more than 100 headers
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        connectionMethod = u'opener'
        try:
            opener = urllib2.build_opener()
            response = opener.open(url)
            htmlSource = response.read()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'
        # pb avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304 qui renvoie 301 car son suffixe est facultatif
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : ssl.CertificateError'
        # HS : https://fr.wikipedia.org/w/index.php?title=Herv%C3%A9_Moulin&type=revision&diff=135989688&oldid=135121040
        url = url.replace(u'https:', u'http:')
        try:
            response = opener.open(url)
            htmlSource = response.read()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'

    connectionMethod = u"urllib2.urlopen(url.encode('utf8'))"
    try:
        htmlSource = urllib2.urlopen(url.encode('utf8')).read()
        if debugLevel > 0: print str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        connectionMethod = u'HTTPCookieProcessor'
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            response = opener.open(url)
            htmlSource = response.read()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'
        
    connectionMethod = u'Request text/html'    
    try:
        req = urllib2.Request(url)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        htmlSource = res.read()
        if debugLevel > 0: print connectionMethod + u' : text/html ' + str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        connectionMethod = u'geturl()'
        try:
            resp = urllib2.urlopen(url)
            req = urllib2.Request(resp.geturl())
            res = urllib2.urlopen(req)
            htmlSource = res.read()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'

    connectionMethod = u'Request Mozilla/5.0'
    agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        headers = { 'User-Agent' : agent }
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        htmlSource = res.read()
        if debugLevel > 0: print connectionMethod + u' : ' + agent + u' : ' + str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        if e.code == "404": return "404 error"
        if socket.gethostname() == u'PavilionDV6':
            connectionMethod = u'follow_all_redirects'    # fonctionne avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304
            try:
                r = requests.get(url)
                req = urllib2.Request(r.url)
                res = urllib2.urlopen(req)
                htmlSource = res.read()
                if debugLevel > 0: print str(len(htmlSource))
                if htmlSource != u'': return htmlSource
            except UnicodeEncodeError:
                if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
            except UnicodeDecodeError:
                if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
            except UnicodeError:
                if debugLevel > 0: print connectionMethod + u' : UnicodeError'
                connectionMethod = u"Méthode url.encode('utf8')"
                try:
                    sock = urllib.urlopen(url.encode('utf8'))
                    htmlSource = sock.read()
                    sock.close()
                    if debugLevel > 0: print str(len(htmlSource))
                    if htmlSource != u'': return htmlSource
                except UnicodeError:
                    if debugLevel > 0: print connectionMethod + u' : UnicodeError'
                except UnicodeEncodeError:
                    if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
                except UnicodeDecodeError:
                    if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
                except httplib.BadStatusLine:
                    if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
                except httplib.HTTPException:
                    if debugLevel > 0: print connectionMethod + u' : HTTPException'
                except httplib.InvalidURL:
                    if debugLevel > 0: print connectionMethod + u' : InvalidURL'
                except urllib2.HTTPError, e:
                    if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
                except IOError as e:
                    if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
                except urllib2.URLError:
                    if debugLevel > 0: print connectionMethod + u' : URLError'
                except MemoryError:
                    if debugLevel > 0: print connectionMethod + u' : MemoryError'
                except requests.exceptions.HTTPError:
                    if debugLevel > 0: print connectionMethod + u' : HTTPError'
                except requests.exceptions.SSLError:
                    if debugLevel > 0: print connectionMethod + u' : SSLError'
                except ssl.CertificateError:
                    if debugLevel > 0: print connectionMethod + u' : CertificateError'
            except httplib.BadStatusLine:
                if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
            except httplib.HTTPException:
                if debugLevel > 0: print connectionMethod + u' : HTTPException'
            except httplib.InvalidURL:
                if debugLevel > 0: print connectionMethod + u' : InvalidURL'
            except urllib2.HTTPError, e:
                if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
            except urllib2.URLError:
                if debugLevel > 0: print connectionMethod + u' : URLError'    
            except requests.exceptions.TooManyRedirects:
                if debugLevel > 0: print connectionMethod + u' : TooManyRedirects'
            except IOError as e:
                if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
            except requests.exceptions.ConnectionError:
                if debugLevel > 0: print connectionMethod + u' ConnectionError'
            except requests.exceptions.InvalidSchema:
                if debugLevel > 0: print connectionMethod + u' InvalidSchema'
            except MemoryError:
                if debugLevel > 0: print connectionMethod + u' : MemoryError'
            except requests.exceptions.HTTPError:
                if debugLevel > 0: print connectionMethod + u' : HTTPError'
            except requests.exceptions.SSLError:
                if debugLevel > 0: print connectionMethod + u' : SSLError'
            except ssl.CertificateError:
                if debugLevel > 0: print connectionMethod + u' : CertificateError'
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'

    connectionMethod = u'Request &_r=4&'
    agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        if url.find(u'_r=') == -1:
            if url.find(u'?') != -1:
                url = url + "&_r=4&"
            else:
                url = url + "?_r=4&"
        else:
            if url.find(u'?') != -1:
                url = url[0:url.find(u'_r=')-1] + "&_r=4&"
            else:
                url = url[0:url.find(u'_r=')-1] + "?_r=4&"
        headers = { 'User-Agent' : agent }
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        htmlSource = res.read()
        if debugLevel > 0: print str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        connectionMethod = u'HTTPRedirectHandler'
        try:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            request = opener.open(url)
            req = urllib2.Request(request.url)
            res = urllib2.urlopen(req)
            htmlSource = res.read()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'        
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'

    connectionMethod = u'urlopen'    # fonctionne avec http://voxofilm.free.fr/vox_0/500_jours_ensemble.htm, et http://www.kurosawa-drawings.com/page/27
    try:
        res = urllib2.urlopen(url)
        htmlSource = res.read()
        if debugLevel > 0: print str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        if e.code == 401: return "ok"    # http://www.nature.com/nature/journal/v442/n7104/full/nature04945.html
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
    except urllib2.URLError:
        if debugLevel > 0: print connectionMethod + u' : URLError'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError' 

    connectionMethod = u'urllib.urlopen'
    try:
        sock = urllib.urlopen(url)
        htmlSource = sock.read()
        sock.close()
        if debugLevel > 0: print str(len(htmlSource))
        if htmlSource != u'': return htmlSource
    except httplib.BadStatusLine:
        if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
    except httplib.HTTPException:
        if debugLevel > 0: print connectionMethod + u' : HTTPException'
    except httplib.InvalidURL:
        if debugLevel > 0: print connectionMethod + u' : InvalidURL'
    except IOError as e:
        if debugLevel > 0: print connectionMethod + u' : I/O error'
    except urllib2.URLError, e:
        if debugLevel > 0: print connectionMethod + u' : URLError %s.' % e.code
    except urllib2.HTTPError, e:
        if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
    except UnicodeEncodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
    except UnicodeDecodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
    except httplib.IncompleteRead:
        if debugLevel > 0: print connectionMethod + u' : IncompleteRead'
    except MemoryError:
        if debugLevel > 0: print connectionMethod + u' : MemoryError'
    except requests.exceptions.HTTPError:
        if debugLevel > 0: print connectionMethod + u' : HTTPError'
    except requests.exceptions.SSLError:
        if debugLevel > 0: print connectionMethod + u' : SSLError'
    except ssl.CertificateError:
        if debugLevel > 0: print connectionMethod + u' : CertificateError'
    except UnicodeError:
        if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        connectionMethod = u"Méthode url.encode('utf8')"
        try:
            sock = urllib.urlopen(url.encode('utf8'))
            htmlSource = sock.read()
            sock.close()
            if debugLevel > 0: print str(len(htmlSource))
            if htmlSource != u'': return htmlSource
        except UnicodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeError'
        except UnicodeEncodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeEncodeError'
        except UnicodeDecodeError:
            if debugLevel > 0: print connectionMethod + u' : UnicodeDecodeError'
        except httplib.BadStatusLine:
            if debugLevel > 0: print connectionMethod + u' : BadStatusLine'
        except httplib.HTTPException:
            if debugLevel > 0: print connectionMethod + u' : HTTPException'
        except httplib.InvalidURL:
            if debugLevel > 0: print connectionMethod + u' : InvalidURL'
        except urllib2.HTTPError, e:
            if debugLevel > 0: print connectionMethod + u' : HTTPError %s.' % e.code
        except IOError as e:
            if debugLevel > 0: print connectionMethod + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
        except urllib2.URLError:
            if debugLevel > 0: print connectionMethod + u' : URLError'
        except MemoryError:
            if debugLevel > 0: print connectionMethod + u' : MemoryError'
        except requests.exceptions.HTTPError:
            if debugLevel > 0: print connectionMethod + u' : HTTPError'
        except requests.exceptions.SSLError:
            if debugLevel > 0: print connectionMethod + u' : SSLError'
        except ssl.CertificateError:
            if debugLevel > 0: print connectionMethod + u' : CertificateError'
    if debugLevel > 0: print connectionMethod + u' Fin du test d\'existance du site'
    return u''

def TestPage(htmlSource, url, debugLevel = 0):
    LienBrise = False
    try:
        #if debugLevel > 1 and htmlSource != u'' and htmlSource is not None: raw_input (htmlSource[0:1000])
        if htmlSource is None:
            if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " none type"
            return True
        elif htmlSource == u'ok' or (htmlSource == u'' and (url.find(u'à') != -1 or url.find(u'é') != -1 or url.find(u'è') != -1 or url.find(u'ê') != -1 or url.find(u'ù') != -1)): # bug http://fr.wikipedia.org/w/index.php?title=Acad%C3%A9mie_fran%C3%A7aise&diff=prev&oldid=92572792
            return False
        elif htmlSource == u'ko' or htmlSource == u'':
            if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " page vide"
            return True
        else:
            if debugLevel > 0: print u' Page non vide'
            # Recherche des erreurs
            for e in range(0,limiteE):
                if debugLevel > 1: print Erreur[e]
                if htmlSource.find(Erreur[e]) != -1 and not re.search("\n[^\n]*if[^\n]*" + Erreur[e], htmlSource):
                    if debugLevel > 1: print u'  Trouvé'
                    # Exceptions
                    if Erreur[e] == "404 Not Found" and url.find("audiofilemagazine.com") == -1:    # Exception avec popup formulaire en erreur
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    # Wikis : page vide à créer
                    if Erreur[e] == "Soit vous avez mal &#233;crit le titre" and url.find("wiki") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    elif Erreur[e] == "Il n'y a pour l'instant aucun texte sur cette page." != -1 and htmlSource.find("wiki") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    elif Erreur[e] == "There is currently no text in this page." != -1 and htmlSource.find("wiki") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    # Sites particuliers
                    elif Erreur[e] == "The page you requested cannot be found" and url.find("restaurantnewsresource.com") == -1:    # bug avec http://www.restaurantnewsresource.com/article35143 (Landry_s_Restaurants_Opens_T_REX_Cafe_at_Downtown_Disney.html)
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    elif Erreur[e] == "Terme introuvable" != -1 and htmlSource.find("Site de l'ATILF") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    elif Erreur[e] == "Cette forme est introuvable !" != -1 and htmlSource.find("Site de l'ATILF") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    elif Erreur[e] == "Sorry, no matching records for query" != -1 and htmlSource.find("ATILF - CNRS") != -1:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break
                    else:
                        LienBrise = True
                        if debugLevel > 0: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
                        break

    except UnicodeError:
        if debugLevel > 0: print u'UnicodeError lors de la lecture'
        LienBrise = False
    except UnicodeEncodeError:
        if debugLevel > 0: print u'UnicodeEncodeError lors de la lecture'
        LienBrise = False
    except UnicodeDecodeError:
        if debugLevel > 0: print u'UnicodeDecodeError lors de la lecture'
        LienBrise = False
    except httplib.BadStatusLine:
        if debugLevel > 0: print u'BadStatusLine lors de la lecture'
    except httplib.HTTPException:
        if debugLevel > 0: print u'HTTPException'
        LienBrise = False
    except httplib.InvalidURL:
        if debugLevel > 0: print u'InvalidURL lors de la lecture'
        LienBrise = False
    except urllib2.HTTPError, e:
        if debugLevel > 0: print u'HTTPError %s.' % e.code +  u' lors de la lecture'
        LienBrise = False
    except IOError as e:
        if debugLevel > 0: print u'I/O error({0}): {1}'.format(e.errno, e.strerror) +  u' lors de la lecture'
        LienBrise = False
    except urllib2.URLError:
        if debugLevel > 0: print u'URLError lors de la lecture'
        LienBrise = False
    else:
        if debugLevel > 1: print u'Fin du test du contenu'
    return LienBrise

def trim(s):
    return s.strip(" \t\n\r\0\x0B")
    
def log(source):        
    txtfile = codecs.open(u'_hyperlinx.log', 'a', 'utf-8')
    txtfile.write(u'\n' + source + u'\n')
    txtfile.close()

# à faire : 
#    i18n
#    sauter les longs PDF comme dans [[w:Apollo 11]]
#    spécifier le remplacement “citation” s'il a les paramètres du modèle anglais
#     remplacer "éditeur" par "périodique" dans "article"

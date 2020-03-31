#!/usr/bin/env python
# coding: utf-8
"""
Ce script traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}}) cf http://www.tradino.org/
Optionellement, il vérifie toutes les URL des articles de la forme http://, https:// et [// ou incluses dans certains modèles
(pas tous étant donnée leur complexité, car certains incluent des {{{1}}} et {{{2}}} dans leurs URL)
"""
from __future__ import absolute_import, unicode_literals
import re
import ssl
import urllib
import webbrowser
import requests
import pywikibot
from pywikibot import *
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
try:
    import http.client as httplib
except ImportError:
    import httplib
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
try:
    import http.cookiejar as cookielib
except ImportError:
    import cookielib
try:
    from src.lib import *
except ImportError:
    from lib import *

debug_level = 0
username = 'JackBot'
site = pywikibot.Site('fr', 'wiktionary')


# *** General functions ***
def setGlobalsHL(mydebug_level, mySite, myUsername):
    global debug_level
    global site
    global username
    debug_level = mydebug_level
    site = mySite
    username = myUsername

# Preferences
semiauto = False
retablirNonBrise = False  # Reteste les liens brisés
checkURL = False

brokenDomains = []
#brokenDomains.append('marianne2.fr')    # Site remplacé par marianne.net en mai 2017

blockedDomains = [] # à cause des popovers ou Node.js ?
blockedDomains.append('bbc.co.uk')
blockedDomains.append('biodiversitylibrary.org')
blockedDomains.append('charts.fi')
blockedDomains.append('cia.gov')
blockedDomains.append('finnishcharts.com')
blockedDomains.append('history.navy.mil') # IP Free bloquée en lecture
blockedDomains.append('itunes.apple.com')
blockedDomains.append('nytimes.com')
blockedDomains.append('psaworldtour.com')
blockedDomains.append('rottentomatoes.com')
blockedDomains.append('soundcloud.com')
blockedDomains.append('twitter.com')
blockedDomains.append('w-siberia.ru')

authorizedFiles = []
authorizedFiles.append('.pdf')

# Modèles qui incluent des URL dans leurs pages
ligne = 4
colonne = 2
TabModeles = [[0] * (colonne+1) for _ in range(ligne+1)]
TabModeles[1][1] = 'Import:DAF8'
TabModeles[1][2] = 'http://www.cnrtl.fr/definition/academie8/'
TabModeles[2][1] = 'R:DAF8'
TabModeles[2][2] = 'http://www.cnrtl.fr/definition/academie8/'
TabModeles[3][1] = 'Import:Littré'
TabModeles[3][2] = 'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='
TabModeles[4][1] = 'R:Littré'
TabModeles[4][2] = 'http://artflx.uchicago.edu/cgi-bin/dicos/pubdico1look.pl?strippedhw='

# Modèles qui incluent des URL dans leurs paramètres
oldTemplate = []
newTemplate = []
oldTemplate.append('cite web')
newTemplate.append('lien web')
oldTemplate.append('citeweb')
newTemplate.append('lien web')
oldTemplate.append('cite news')
newTemplate.append('article')
oldTemplate.append('cite journal')
newTemplate.append('article')
oldTemplate.append('cite magazine')
newTemplate.append('article')
oldTemplate.append('lien news')
newTemplate.append('article')
oldTemplate.append('cite video')
newTemplate.append('lien vidéo')
oldTemplate.append('cite episode')
newTemplate.append('citation épisode')
oldTemplate.append('cite arXiv')
newTemplate.append('lien arXiv')
oldTemplate.append('cite press release')
newTemplate.append('lien web')
oldTemplate.append('cite press_release')
newTemplate.append('lien web')
oldTemplate.append('cite conference')
newTemplate.append('lien conférence')
oldTemplate.append('docu')
newTemplate.append('lien vidéo')
oldTemplate.append('cite book')
newTemplate.append('ouvrage')
#oldTemplate.append('cite')
#newTemplate.append('ouvrage')
# it
oldTemplate.append('cita pubblicazione')
newTemplate.append('article')
oldTemplate.append('cita libro')
newTemplate.append('ouvrage')
# sv
oldTemplate.append('webbref')
newTemplate.append('lien web')
limiteL = len(newTemplate)    # Limite de la liste des modèles traduis de l'anglais (langue=en)

# Modèle avec alias français
oldTemplate.append('deadlink')
newTemplate.append('lien brisé')
#oldTemplate.append('dead link') TODO: if previous template is {{lien brisé}} then remove else replace 
#newTemplate.append('lien brisé')
oldTemplate.append('webarchive')
newTemplate.append('lien brisé')
oldTemplate.append('lien brise')
newTemplate.append('lien brisé')
oldTemplate.append('lien cassé')
newTemplate.append('lien brisé')
oldTemplate.append('lien mort')
newTemplate.append('lien brisé')
oldTemplate.append('lien web brisé')
newTemplate.append('lien brisé')
oldTemplate.append('lien Web')
newTemplate.append('lien web')
oldTemplate.append('cita web')
newTemplate.append('lien web')
oldTemplate.append('cita noticia')
newTemplate.append('lien news')
oldTemplate.append('web site')
newTemplate.append('lien web')
oldTemplate.append('site web')
newTemplate.append('lien web')
oldTemplate.append('périodique')
newTemplate.append('article')
oldTemplate.append('quote')
newTemplate.append('citation bloc')

# Modèles pour traduire leurs paramètres uniquement
oldTemplate.append('lire en ligne')
newTemplate.append('lire en ligne')
oldTemplate.append('dts')
newTemplate.append('dts')
oldTemplate.append('Chapitre')
newTemplate.append('Chapitre')
limiteM = len(newTemplate)

# Paramètres à remplacer
oldParam = []
newParam = []
oldParam.append('author')
newParam.append('auteur')
oldParam.append('authorlink1')
newParam.append('lien auteur1')
oldParam.append('title')
newParam.append('titre')
oldParam.append('publisher')
newParam.append('éditeur')
oldParam.append('work')    # paramètre de {{lien web}} différent pour {{article}}
newParam.append('périodique')
oldParam.append('newspaper')
newParam.append('journal')
oldParam.append('day')
newParam.append('jour')
oldParam.append('month')
newParam.append('mois')
oldParam.append('year')
newParam.append('année')
oldParam.append('accessdate')
newParam.append('consulté le')
oldParam.append('access-date')
newParam.append('consulté le')
oldParam.append('language')
newParam.append('langue')
oldParam.append('lang')
newParam.append('langue')
oldParam.append('quote')
newParam.append('extrait')
oldParam.append('titre vo')
newParam.append('titre original')
oldParam.append('first')
newParam.append('prénom')
oldParam.append('surname')
newParam.append('nom')
oldParam.append('last')
newParam.append('nom')
for p in range(1, 100):
    oldParam.append('first'+str(p))
    newParam.append('prénom'+str(p))
    oldParam.append('given'+str(p))
    newParam.append('prénom'+str(p))
    oldParam.append('last'+str(p))
    newParam.append('nom'+str(p))
    oldParam.append('surname'+str(p))
    newParam.append('nom'+str(p))
    oldParam.append('author'+str(p))
    newParam.append('auteur'+str(p))
oldParam.append('issue')
newParam.append('numéro')
oldParam.append('authorlink')
newParam.append('lien auteur')
oldParam.append('author-link')
newParam.append('lien auteur')
for p in range(1, 100):
    oldParam.append('authorlink'+str(p))
    newParam.append('lien auteur'+str(p))
    oldParam.append('author'+str(p)+'link')
    newParam.append('lien auteur'+str(p))
oldParam.append('coauthorlink')
newParam.append('lien coauteur')
oldParam.append('coauthor-link')
newParam.append('lien coauteur')
oldParam.append('surname1')
newParam.append('nom1')
oldParam.append('coauthors')
newParam.append('coauteurs')
oldParam.append('co-auteurs')
newParam.append('coauteurs')
oldParam.append('co-auteur')
newParam.append('coauteur')
oldParam.append('given')
newParam.append('prénom')
oldParam.append('trad')
newParam.append('traducteur')
oldParam.append('at')
newParam.append('passage')
oldParam.append('origyear')
newParam.append('année première édition') # "année première impression" sur les projets frères
oldParam.append('année première impression')
newParam.append('année première édition')
oldParam.append('location')
newParam.append('lieu')
oldParam.append('place')
newParam.append('lieu')
oldParam.append('publication-date')
newParam.append('année')
oldParam.append('writers')
newParam.append('scénario')
oldParam.append('episodelink')
newParam.append('lien épisode')
oldParam.append('serieslink')
newParam.append('lien série')
oldParam.append('titlelink')
newParam.append('lien titre')
oldParam.append('credits')
newParam.append('crédits')
oldParam.append('network')
newParam.append('réseau')
oldParam.append('station')
newParam.append('chaîne')
oldParam.append('city')
newParam.append('ville')
oldParam.append('began')
newParam.append('début')
oldParam.append('ended')
newParam.append('fin')
oldParam.append('airdate')
newParam.append('diffusion')
oldParam.append('number')
newParam.append('numéro')
oldParam.append('season')
newParam.append('saison')
oldParam.append('year2')
newParam.append('année2')
oldParam.append('month2')
newParam.append('mois2')
oldParam.append('time')
newParam.append('temps')
oldParam.append('accessyear')
newParam.append('année accès')
oldParam.append('accessmonth')
newParam.append('mois accès')
oldParam.append('conference')
newParam.append('conférence')
oldParam.append('conferenceurl')
newParam.append('urlconférence')
oldParam.append('booktitle')
newParam.append('titre livre')
oldParam.append('others')
newParam.append('champ libre')
# Fix
oldParam.append('en ligne le')
newParam.append('archivedate')
oldParam.append('autres')
newParam.append('champ libre')
oldParam.append('Auteur')
newParam.append('auteur')
oldParam.append('auteur-')
newParam.append('auteur')
oldParam.append('editor')
newParam.append('éditeur')
oldParam.append('editor2')
newParam.append('auteur2')

# espagnol
oldParam.append('autor')
newParam.append('auteur')
oldParam.append('título')
newParam.append('titre')
oldParam.append('fechaacceso')
newParam.append('consulté le')
oldParam.append('fecha')
newParam.append('date')
oldParam.append('obra')
newParam.append('série')
oldParam.append('idioma')
newParam.append('langue')
oldParam.append('publicació')
newParam.append('éditeur')
oldParam.append('editorial')
newParam.append('journal')
oldParam.append('series')
newParam.append('collection')
oldParam.append('agency')
newParam.append('auteur institutionnel') # ou "périodique" si absent
oldParam.append('magazine')
newParam.append('périodique')

# italien
oldParam.append('autore')
newParam.append('auteur')
oldParam.append('titolo')
newParam.append('titre')
oldParam.append('accesso')
newParam.append('consulté le')
oldParam.append('data')
newParam.append('date')
oldParam.append('nome')
newParam.append('prénom')
oldParam.append('cognome')
newParam.append('nom')
oldParam.append('linkautore')
newParam.append('lien auteur')
oldParam.append('coautori')
newParam.append('coauteurs')
oldParam.append('rivista')
newParam.append('journal')
oldParam.append('giorno')
newParam.append('jour')
oldParam.append('mese')
newParam.append('mois')
oldParam.append('anno')
newParam.append('année')
oldParam.append('pagine')
newParam.append('page')
oldParam.append('editore')
newParam.append('éditeur')

# suédois
oldParam.append('författar')
newParam.append('auteur')
oldParam.append('titel')
newParam.append('titre')
oldParam.append('hämtdatum')
newParam.append('consulté le')
oldParam.append('datum')
newParam.append('date')
oldParam.append('förnamn')
newParam.append('prénom')
oldParam.append('efternamn')
newParam.append('nom')
oldParam.append('författarlänk')
newParam.append('lien auteur')
oldParam.append('utgivare')
newParam.append('éditeur')
oldParam.append('månad')
newParam.append('mois')
oldParam.append('år')
newParam.append('année')
oldParam.append('sida')
newParam.append('page')
oldParam.append('verk')
newParam.append('périodique')

limiteP = len(oldParam)
if limiteP != len(newParam):
    input('Erreur l 227')
    
# URL à remplacer
URLDeplace = ['athena.unige.ch/athena', 'un2sg4.unige.ch/athena']
limiteU = len(URLDeplace)

# Caractères délimitant la fin des URL
# http://tools.ietf.org/html/rfc3986
# http://fr.wiktionary.org/wiki/Annexe:Titres_non_pris_en_charge
UrlEnd = [' ', '\n', '[', ']', '{', '}', '<', '>', '|', '^', '\\', '`', '"']
#UrlEnd.append('~'    # dans 1ère RFC seulement
UrlLimit = len(UrlEnd)
# Caractères qui ne peuvent pas être en dernière position d'une URL :
UrlEnd2 = ['.', ',', ';', '!', '?', ')', u"'"]
UrlLimit = len(UrlEnd2)

ligneB = 6
colonneB = 2
noTag = [[0] * (colonneB+1) for _ in range(ligneB+1)]
noTag[1][1] = '<pre>'
noTag[1][2] = '</pre>'
noTag[2][1] = '<nowiki>'
noTag[2][2] = '</nowiki>'
noTag[3][1] = '<ref name='
noTag[3][2] = '>'
noTag[4][1] = '<rdf'
noTag[4][2] = '>'
noTag[5][1] = '<source'
noTag[5][2] = '</source' + '>'
noTag[6][1] = '\n '
noTag[6][2] = '\n'
'''
    ligneB = ligneB + 1
    noTag[ligneB-1][1] = '<!--'
    noTag[ligneB-1][2] = '-->'
'''
noTemplates = []
if not retablirNonBrise: noTemplates.append('lien brisé')

Erreur = ["403 Forbidden", "404 – File not found", "404 error", "404 Not Found", "404. That’s an error.",
          "Error 404 - Not found", "Error 404 (Not Found)", "Error 503 (Server Error)", "Page not found",
          "Runtime Error", "server timedout", "Sorry, no matching records for query",
          "The page you requested cannot be found", "this page can't be found",
          "The service you requested is not available at this time", "There is currently no text in this page.",
          "500 Internal Server Error", "Cette forme est introuvable !", "Soit vous avez mal &#233;crit le titre",
          'Soit vous avez mal écrit le titre', 'Terme introuvable', "nom de domaine demandé n'est plus actif",
          "Il n'y a pour l'instant aucun texte sur cette page."]
limiteE = len(Erreur)

# Média trop volumineux    
Format = ['RIFF', 'WAV', 'BWF', 'Ogg', 'AIFF', 'CAF', 'PCM', 'RAW', 'CDA', 'FLAC', 'ALAC', 'AC3', 'MP3', 'mp3PRO',
          'Ogg Vorbis', 'VQF', 'TwinVQ', 'WMA', 'AU', 'ASF', 'AA', 'AAC', 'MPEG-2 AAC', 'ATRAC', 'iKlax', 'U-MYX',
          'MXP4', 'avi', 'mpg', 'mpeg', 'mkv', 'mka', 'mks', 'asf', 'wmv', 'wma', 'mov', 'ogv', 'oga', 'ogx', 'ogm',
          '3gp', '3g2', 'webm', 'weba', 'nut', 'rm', 'mxf', 'asx', 'ts', 'flv']
limiteF = len(Format)

# Traduction des mois
monthLine = 12
monthColumn = 2
TradM = [[0] * (monthColumn + 1) for _ in range(monthLine + 1)]
TradM[1][1] = 'January'
TradM[1][2] = 'janvier'
TradM[2][1] = 'February'
TradM[2][2] = 'février'
TradM[3][1] = 'March'
TradM[3][2] = 'mars'
TradM[4][1] = 'April'
TradM[4][2] = 'avril'
TradM[5][1] = 'May'
TradM[5][2] = 'mai'
TradM[6][1] = 'June'
TradM[6][2] = 'juin'
TradM[7][1] = 'July'
TradM[7][2] = 'juillet'
TradM[8][1] = 'August'
TradM[8][2] = 'août'
TradM[9][1] = 'September'
TradM[9][2] = 'septembre'
TradM[10][1] = 'October'
TradM[10][2] = 'octobre'
TradM[11][1] = 'November'
TradM[11][2] = 'novembre'
TradM[12][1] = 'December'
TradM[12][2] = 'décembre'

# Traduction des langues
ligneL = 17
colonneL = 2
TradL = [[0] * (colonneL+1) for _ in range(ligneL+1)]
TradL[1][1] = 'French'
TradL[1][2] = 'fr'
TradL[2][1] = 'English'
TradL[2][2] = 'en'
TradL[3][1] = 'German'
TradL[3][2] = 'de'
TradL[4][1] = 'Spanish'
TradL[4][2] = 'es'
TradL[5][1] = 'Italian'
TradL[5][2] = 'it'
TradL[6][1] = 'Portuguese'
TradL[6][2] = 'pt'
TradL[7][1] = 'Dutch'
TradL[7][2] = 'nl'
TradL[8][1] = 'Russian'
TradL[8][2] = 'ru'
TradL[9][1] = 'Chinese'
TradL[9][2] = 'zh'
TradL[10][1] = 'Japanese'
TradL[10][2] = 'ja'
TradL[11][1] = 'Polish'
TradL[11][2] = 'pl'
TradL[12][1] = 'Norwegian'
TradL[12][2] = 'no'
TradL[13][1] = 'Swedish'
TradL[13][2] = 'sv'
TradL[14][1] = 'Finnish'
TradL[14][2] = 'fi'
TradL[15][1] = 'Indonesian'
TradL[15][2] = 'id'
TradL[16][1] = 'Hindi'
TradL[16][2] = 'hi'
TradL[17][1] = 'Arabic'
TradL[17][2] = 'ar'


def hyper_lynx(current_page):
    if debug_level > 0:
        print('------------------------------------')
        #print(time.strftime('%d-%m-%Y %H:%m:%S'))
    summary = 'Vérification des URL'
    html_source = ''
    url = ''
    current_page = current_page.replace('[//https://', '[https://')
    current_page = current_page.replace('[//http://', '[http://')
    current_page = current_page.replace('http://http://', 'http://')
    current_page = current_page.replace('https://https://', 'https://')
    current_page = current_page.replace('<ref>{{en}}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}} ', '<ref>{{en}} ')
    current_page = current_page.replace('<ref>{{{en}}} ', '<ref>{{en}} ')
    current_page = re.sub('[C|c]ita(tion)? *\n* *(\|[^}{]*title *=)', r'ouvrage\2', current_page)
    current_page = translateLinkTemplates(current_page)
    current_page = translateDates(current_page)
    current_page = translateLanguages(current_page)

    if debug_level > 1:
        print('Fin des traductions :')
        input(current_page)

    # Recherche de chaque hyperlien en clair ------------------------------------------------------------------------------------------------------------------------------------
    final_page = ''
    while current_page.find('//') != -1:
        if debug_level > 0: print('-----------------------------------------------------------------')
        url = ''
        DebutURL = ''
        CharFinURL = ''
        titre = ''
        templateEndPosition = 0
        is_broken_link = False
        # Avant l'URL
        PageDebut = current_page[:current_page.find('//')]
        while current_page.find('//') > current_page.find('}}') and current_page.find('}}') != -1:
            if debug_level > 0: print('URL après un modèle')
            final_page = final_page + current_page[:current_page.find('}}')+2]
            current_page = current_page[current_page.find('}}')+2:]

        # noTags interdisant la modification de l'URL
        ignored_link = False
        for b in range(1, ligneB):
            if PageDebut.rfind(noTag[b][1]) != -1 and PageDebut.rfind(noTag[b][1]) > PageDebut.rfind(noTag[b][2]):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTag[b][1]
                break
            if final_page.rfind(noTag[b][1]) != -1 and final_page.rfind(noTag[b][1]) > final_page.rfind(noTag[b][2]):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTag[b][1]
                break
        for noTemplate in noTemplates:
            if PageDebut.rfind('{{' + noTemplate + '|') != -1 and PageDebut.rfind('{{' + noTemplate + '|') > PageDebut.rfind('}}'):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTemplate
                break
            if PageDebut.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') != -1 and \
                PageDebut.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') > PageDebut.rfind('}}'):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTemplate
                break
            if final_page.rfind('{{' + noTemplate + '|') != -1 and final_page.rfind('{{' + noTemplate + '|') > final_page.rfind('}}'):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTemplate
                break
            if final_page.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') != -1 and \
                final_page.rfind('{{' + noTemplate[:1].upper() + noTemplate[1:] + '|') > final_page.rfind('}}'):
                ignored_link = True
                if debug_level > 0: print('URL non traitée, car dans ') + noTemplate
                break

        if not ignored_link:
            # titre=
            if PageDebut.rfind('titre=') != -1 and PageDebut.rfind('titre=') > PageDebut.rfind('{{') and PageDebut.rfind('titre=') > PageDebut.rfind('}}'):
                current_page3 = PageDebut[PageDebut.rfind('titre=')+len('titre='):]
                if current_page3.find('|') != -1 and (current_page3.find('|') < current_page3.find('}}') or current_page3.rfind('}}') == -1):
                    titre = current_page3[:current_page3.find('|')]
                else:
                    titre = current_page3
                if debug_level > 0: print('Titre= avant URL : ') + titre
            elif PageDebut.rfind('titre =') != -1 and PageDebut.rfind('titre =') > PageDebut.rfind('{{') and PageDebut.rfind('titre =') > PageDebut.rfind('}}'):
                current_page3 = PageDebut[PageDebut.rfind('titre =')+len('titre ='):]
                if current_page3.find('|') != -1 and (current_page3.find('|') < current_page3.find('}}') or current_page3.rfind('}}') == -1):
                    titre = current_page3[:current_page3.find('|')]
                else:
                    titre = current_page3
                if debug_level > 0: print('Titre = avant URL : ') + titre
        
            # url=
            if PageDebut[-1:] == '[':
                if debug_level > 0: print('URL entre crochets sans protocole')
                DebutURL = 1
            elif PageDebut[-5:] == 'http:':
                if debug_level > 0: print('URL http')
                DebutURL = 5
            elif PageDebut[-6:] == 'https:':
                if debug_level > 0: print('URL https')
                DebutURL = 6
            elif PageDebut[-2:] == '{{':
                if debug_level > 0: print("URL d'un modèle")
                break
            else:
                if debug_level > 0: print('URL sans http ni crochet')
                DebutURL = 0
            if DebutURL != 0:
                # Après l'URL
                FinPageURL = current_page[current_page.find('//'):]
                # url=    
                CharFinURL = ' '
                for l in range(1, UrlLimit):
                    if FinPageURL.find(CharFinURL) == -1 or (FinPageURL.find(UrlEnd[l]) != -1 and FinPageURL.find(UrlEnd[l]) < FinPageURL.find(CharFinURL)):
                        CharFinURL = UrlEnd[l]
                if debug_level > 0: print('*Caractère de fin URL : ') + CharFinURL
                
                if DebutURL == 1:
                    url = 'http:' + current_page[current_page.find('//'):current_page.find('//')+FinPageURL.find(CharFinURL)]
                    if titre == '':
                        titre = current_page[current_page.find('//')+FinPageURL.find(CharFinURL):]
                        titre = trim(titre[:titre.find(']')])
                else:
                    url = current_page[current_page.find('//')-DebutURL:current_page.find('//')+FinPageURL.find(CharFinURL)]
                if len(url) <= 10:
                    url = ''
                    html_source = ''
                    is_broken_link = False
                else:
                    for u in range(1, UrlLimit2):
                        while url[len(url)-1:] == UrlEnd2[u]:
                            url = url[:len(url)-1]
                            if debug_level > 0: print('Réduction de l\'URL de ' + UrlEnd2[u])
                    
                    Media = False
                    for f in range(1,limiteF):
                        if url[len(url)-len(Format[f])-1:].lower() == '.' + Format[f].lower():
                            if debug_level > 0:
                                print(url)
                                print('Média détecté (memory error potentielle)')
                            Media = True
                    if Media == False:
                        if debug_level > 0: print('Recherche de la page distante : ' + url)
                        html_source = testURL(url, debug_level)
                        if debug_level > 0: print('Recherche dans son contenu')
                        is_broken_link = testURLPage(html_source, url)
                
                # Site réputé HS, mais invisible car ses sous-pages ont toutes été déplacées, et renvoient vers l'accueil
                for u in range(1,limiteU):
                    if url.find(URLDeplace[u]) != -1 and len(url) > len(URLDeplace[u]) + 8:    #http://.../
                        is_broken_link = True
                
                # Confirmation manuelle
                if semiauto == True:
                    webbrowser.open_new_tab(url)
                    if is_broken_link:
                        result = input("Lien brisé ? (o/n) ")
                    else:
                        result = input("Lien fonctionnel ? (o/n) ")
                    if result != "n" and result != "no" and result != "non":
                        is_broken_link = True
                    else:
                        is_broken_link = False
                        
                if debug_level > 0:
                    # Compte-rendu des URL détectées
                    try:
                        print('*URL : ') + url
                        print('*Titre : ') + titre
                        print('*HS : ') + str(is_broken_link)
                    except UnicodeDecodeError:
                        print('*HS : ') + str(is_broken_link)
                        print("UnicodeDecodeError l 466")
                if debug_level > 1: input(html_source[:7000])
                
                # Modification du wiki en conséquence    
                DebutPage = current_page[:current_page.find('//')+2]
                DebutURL = max(DebutPage.find('http://'),DebutPage.find('https://'),DebutPage.find('[//'))
                
                # Saut des modèles inclus dans un modèle de lien
                while DebutPage.rfind('{{') != -1 and DebutPage.rfind('{{') < DebutPage.rfind('}}'):
                    # pb des multiples crochets fermants sautés : {{ ({{ }} }})
                    current_page2 = DebutPage[DebutPage.rfind('{{'):]
                    if current_page2.rfind('}}') == current_page2.rfind('{{'):
                        DebutPage = DebutPage[:DebutPage.rfind('{{')]
                    else:
                        DebutPage = ''
                        break
                    if debug_level > 1: input(DebutPage[-100:])
                    
                
                # Détection si l'hyperlien est dans un modèle (si aucun modèle n'est fermé avant eux)
                if (DebutPage.rfind('{{') != -1 and DebutPage.rfind('{{') > DebutPage.rfind('}}')) or \
                    (DebutPage.rfind('url=') != -1 and DebutPage.rfind('url=') > DebutPage.rfind('}}')) or \
                    (DebutPage.rfind('url =') != -1 and DebutPage.rfind('url =') > DebutPage.rfind('}}')):
                    DebutModele = DebutPage.rfind('{{')
                    DebutPage = DebutPage[DebutPage.rfind('{{'):len(DebutPage)]
                    AncienModele = ''
                    # Lien dans un modèle connu (consensus en cours pour les autres, atention aux infobox)
                    '''for m in range(1,limiteM):
                        regex = '{{ *[' + newTemplate[m][0:1] + r'|' + newTemplate[m][0:1].upper() + r']' + newTemplate[m][1:len(newTemplate[m])] + r' *[\||\n]'
                    ''' 
                    if re.search('{{ *[L|l]ien web *[\||\n]', DebutPage):
                        AncienModele = 'lien web'
                        if debug_level > 0: print('Détection de ') + AncienModele
                    elif re.search('{{ *[L|l]ire en ligne *[\||\n]', DebutPage):
                        AncienModele = 'lire en ligne'
                        if debug_level > 0: print('Détection de ') + AncienModele
                    elif retablirNonBrise == True and re.search('{{ *[L|l]ien brisé *[\||\n]', DebutPage):
                        AncienModele = 'lien brisé'
                        if debug_level > 0: print('Détection de ') + AncienModele
                        
                    #if DebutPage[0:2] == '{{': AncienModele = trim(DebutPage[2:DebutPage.find('|')])
                    
                    templateEndPosition = current_page.find('//')+2
                    FinPageModele = current_page[templateEndPosition:len(current_page)]
                    # Calcul des modèles inclus dans le modèle de lien
                    while FinPageModele.find('}}') != -1 and FinPageModele.find('}}') > FinPageModele.find('{{') and FinPageModele.find('{{') != -1:
                        templateEndPosition = templateEndPosition + FinPageModele.find('}}')+2
                        FinPageModele = FinPageModele[FinPageModele.find('}}')+2:len(FinPageModele)]
                    templateEndPosition = templateEndPosition + FinPageModele.find('}}')+2
                    currentTemplate = current_page[DebutModele:templateEndPosition]
                    #if debug_level > 0: print(")*Modele : " + currentTemplate[:100]
                    
                    if AncienModele != '':
                        if debug_level > 0: print('Ancien modèle à traiter : ') + AncienModele
                        if is_broken_link:
                            try:
                                current_page = current_page[:DebutModele] + '{{lien brisé' + current_page[re.search('{{ *[' + AncienModele[:1] + '|' + AncienModele[:1].upper() + ']' + AncienModele[1:] + ' *[\||\n]', current_page).end()-1:]
                            except AttributeError:
                                raise Exception("Regex introuvable ligne 811")
                                
                        elif AncienModele == 'lien brisé':
                            if debug_level > 0: print('Rétablissement d\'un ancien lien brisé')
                            current_page = current_page[:current_page.find(AncienModele)] + 'lien web' + current_page[current_page.find(AncienModele)+len(AncienModele):]
                        '''
                        # titre=
                        if re.search('\| *titre *=', FinPageURL):
                            if debug_level > 0: print('Titre après URL')
                            if titre == '' and re.search('\| *titre *=', FinPageURL).end() != -1 and re.search('\| *titre *=', FinPageURL).end() < FinPageURL.find('\n') and re.search('\| *titre *=', FinPageURL).end() < FinPageURL.find('}}'):
                                current_page3 = FinPageURL[re.search('\| *titre *=', FinPageURL).end():]
                                # Modèles inclus dans les titres
                                while current_page3.find('{{') != -1 and current_page3.find('{{') < current_page3.find('}}') and current_page3.find('{{') < current_page3.find('|'):
                                    titre = titre + current_page3[:current_page3.find('}}')+2]
                                    current_page3 = current_page3[current_page3.find('}}')+2:]
                                if current_page3.find('|') != -1 and (current_page3.find('|') < current_page3.find('}}') or current_page3.find('}}') == -1):
                                    titre = titre + current_page3[0:current_page3.find('|')]
                                else:
                                    titre = titre + current_page3[0:current_page3.find('}}')]
                        elif FinPageURL.find(']') != -1 and (current_page.find('//') == current_page.find('[//')+1 or current_page.find('//') == current_page.find('[http://')+6 or current_page.find('//') == current_page.find('[https://')+7):
                            titre = FinPageURL[FinPageURL.find(CharFinURL)+len(CharFinURL):FinPageURL.find(']')]
                        if debug_level > 1: input(FinPageURL)    
                        
                        # En cas de modèles inclus le titre a pu ne pas être détecté précédemment
                        if titre == '' and re.search('\| *titre *=', currentTemplate):
                            current_page3 = currentTemplate[re.search('\| *titre *=', currentTemplate).end():]
                            # Modèles inclus dans les titres
                            while current_page3.find('{{') != -1 and current_page3.find('{{') < current_page3.find('}}') and current_page3.find('{{') < current_page3.find('|'):
                                titre = titre + current_page3[:current_page3.find('}}')+2]
                                current_page3 = current_page3[current_page3.find('}}')+2:]
                            titre = titre + current_page3[:re.search('[^\|}\n]*', current_page3).end()]
                            if debug_level > 0:
                                print('*Titre2 : ')
                                print(titre)
                            
                        if is_broken_link == True and AncienModele != 'lien brisé' and AncienModele != 'Lien brisé':
                            summary = summary + ', remplacement de ' + AncienModele + ' par {{lien brisé}}'
                            if debug_level > 0: print(', remplacement de ') + AncienModele + ' par {{lien brisé}}'
                            if titre == '':
                                current_page = current_page[0:DebutModele] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' + current_page[templateEndPosition:len(current_page)]
                            else:
                                current_page = current_page[0:DebutModele] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre + '}}' + current_page[templateEndPosition:len(current_page)]
                        elif is_broken_link == False and (AncienModele == 'lien brisé' or AncienModele == 'Lien brisé'):
                            summary = summary + ', Retrait de {{lien brisé}}'
                            current_page = current_page[0:DebutModele] + '{{lien web' + current_page[DebutModele+len('lien brisé')+2:len(current_page)]
                        '''
                            
                        '''elif is_broken_link:
                        summary = summary + ', ajout de {{lien brisé}}'
                        if DebutURL == 1:
                            if debug_level > 0: print('Ajout de lien brisé entre crochets 1')
                            # Lien entre crochets
                            current_page = current_page[0:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre + '}}' + current_page[current_page.find('//')+FinPageURL.find(']')+1:len(current_page)]
                        else:
                            if debug_level > 0: print('Ajout de lien brisé 1')
                            if current_page[DebutURL-1:DebutURL] == '[' and current_page[DebutURL-2:DebutURL] != '[[': DebutURL = DebutURL -1
                            if CharFinURL == ' ' and FinPageURL.find(']') != -1 and (FinPageURL.find('[') == -1 or FinPageURL.find(']') < FinPageURL.find('[')): 
                                # Présence d'un titre
                                current_page = current_page[0:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL)+1:current_page.find('//')+FinPageURL.find(']')]  + '}}' + current_page[current_page.find('//')+FinPageURL.find(']')+1:len(current_page)]
                            elif CharFinURL == ']':
                                current_page = current_page[0:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL):len(current_page)]
                            else:
                                current_page = current_page[0:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL):len(current_page)]
                        '''
                    else:
                        if debug_level > 0: print(url + " dans modèle non géré")
                    
                else:
                    if debug_level > 0: print('URL hors modèle')
                    if is_broken_link:
                        summary = summary + ', ajout de {{lien brisé}}'
                        if DebutURL == 1:
                            if debug_level > 0: print('Ajout de lien brisé entre crochets sans protocole')
                            if titre != '':
                                current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre + '}}' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL):]
                            else:
                                current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL):]
                            #if debug_level > 0: input(current_page)
                        else:
                            if debug_level > 0: print('Ajout de lien brisé 2')
                            if current_page[DebutURL-1:DebutURL] == '[' and current_page[DebutURL-2:DebutURL] != '[[':
                                if debug_level > 0: print('entre crochet')
                                DebutURL = DebutURL -1
                                if titre == '' :
                                    if debug_level > 0: "Titre vide"
                                    # Prise en compte des crochets inclus dans un titre
                                    current_page2 = current_page[current_page.find('//')+FinPageURL.find(CharFinURL):]
                                    #if debug_level > 0: input(current_page2)
                                    if current_page2.find(']]') != -1 and current_page2.find(']]') < current_page2.find(']'):
                                        while current_page2.find(']]') != -1 and current_page2.find('[[') != -1 and current_page2.find('[[') < current_page2.find(']]'):
                                            titre = titre + current_page2[:current_page2.find(']]')+1]
                                            current_page2 = current_page2[current_page2.find(']]')+1:]
                                        titre = trim(titre + current_page2[:current_page2.find(']]')])
                                        current_page2 = current_page2[current_page2.find(']]'):]
                                    while current_page2.find(']') != -1 and current_page2.find('[') != -1 and current_page2.find('[') < current_page2.find(']'):
                                        titre = titre + current_page2[:current_page2.find(']')+1]
                                        current_page2 = current_page2[current_page2.find(']')+1:]
                                    titre = trim(titre + current_page2[:current_page2.find(']')])
                                    current_page2 = current_page2[current_page2.find(']'):]
                                if titre != '':
                                    if debug_level > 0: "Ajout avec titre"
                                    current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + titre + '}}' + current_page[len(current_page)-len(current_page2)+1:len(current_page)]
                                else:
                                    if debug_level > 0: "Ajout sans titre"
                                    current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}}' + current_page[current_page.find('//')+FinPageURL.find(']')+1:len(current_page)]
                            else:    
                                if titre != '': 
                                    # Présence d'un titre
                                    if debug_level > 0: print('URL nue avec titre')
                                    current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '|titre=' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL)+1:current_page.find('//')+FinPageURL.find(']')]  + '}}' + current_page[current_page.find('//')+FinPageURL.find(']')+1:len(current_page)]
                                else:
                                    if debug_level > 0: print('URL nue sans titre')
                                    current_page = current_page[:DebutURL] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + url + '}} ' + current_page[current_page.find('//')+FinPageURL.find(CharFinURL):len(current_page)]
                        
                    else:
                        if debug_level > 0: print('Aucun changement sur l\'URL http')
            else:
                if debug_level > 0: print('Aucun changement sur l\'URL non http')
        else:
            if debug_level > 1: print('URL entre balises sautée')

        # Lien suivant, en sautant les URL incluses dans l'actuelle, et celles avec d'autres protocoles que http(s)
        if templateEndPosition == 0 and is_broken_link == False:
            FinPageURL = current_page[current_page.find('//')+2:len(current_page)]
            CharFinURL = ' '
            for l in range(1,UrlLimit):
                if FinPageURL.find(UrlEnd[l]) != -1 and FinPageURL.find(UrlEnd[l]) < FinPageURL.find(CharFinURL):
                    CharFinURL = UrlEnd[l]
            if debug_level > 0: print('Saut après "') + CharFinURL + '"'
            final_page = final_page + current_page[:current_page.find('//')+2+FinPageURL.find(CharFinURL)]
            current_page = current_page[current_page.find('//')+2+FinPageURL.find(CharFinURL):]
        else:
            # Saut du reste du modèle courant (contenant parfois d'autres URL à laisser)
            if debug_level > 0: print('Saut après "}}"')
            final_page = final_page + current_page[:templateEndPosition]
            current_page = current_page[templateEndPosition:]
        if debug_level > 1: input(final_page)

    if final_page.find('|langue=None') != -1:
        if is_broken_link == False:
            URLlanguage = getURLsite_language(html_source)
            if URLlanguage != 'None':
                try:
                    final_page = final_page.replace('|langue=None', '|langue=' + URLlanguage)
                except UnicodeDecodeError:
                    if debug_level > 0: print('UnicodeEncodeError l 1038')

    current_page = finalPage + current_page
    finalPage = ''    
    if debug_level > 0: print("Fin des tests URL")

    # Recherche de chaque hyperlien de modèles ------------------------------------------------------------------------------------------------------------------------------------
    if current_page.find('{{langue') != -1: # du Wiktionnaire
        if debug_level > 0: print("Modèles Wiktionnaire")
        for m in range(1,ligne):
            finalPage = ''
            while current_page.find('{{' + TabModeles[m][1] + '|') != -1:
                finalPage =  finalPage + current_page[:current_page.find('{{' + TabModeles[m][1] + '|')+len('{{' + TabModeles[m][1] + '|')]
                current_page =  current_page[current_page.find('{{' + TabModeles[m][1] + '|')+len('{{' + TabModeles[m][1] + '|'):len(current_page)]
                if current_page[0:current_page.find('}}')].find('|') != -1:
                    Param1Encode = current_page[:current_page.find('|')].replace(' ',u'_')
                else:
                    Param1Encode = current_page[:current_page.find('}}')].replace(' ',u'_')
                html_source = testURL(TabModeles[m][2] + Param1Encode, debug_level)
                is_broken_link = testURLPage(html_source, url)
                if is_broken_link: finalPage = finalPage[:finalPage.rfind('{{' + TabModeles[m][1] + '|')] + '{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + '|url=' + TabModeles[m][2]
            current_page = finalPage + current_page
            finalPage = ''
        current_page = finalPage + current_page
        finalPage = ''
    if debug_level > 0:
        print('Fin des tests modèle')

    # Paramètres inutiles
    current_page = re.sub(r'{{ *Références *\| *colonnes *= *}}', r'{{Références}}', current_page)
    # Dans {{article}}, "éditeur" vide bloque "périodique", "journal" ou "revue"
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\||\n)[^}]*)\| *éditeur *= *([\||}|\n]+)', r'{{\1rticle\2\3', current_page)
    # https://fr.wikipedia.org/w/index.php?title=Discussion_utilisateur:JackPotte&oldid=prev&diff=165491794#Suggestion_pour_JackBot_:_Signalement_param%C3%A8tre_obligatoire_manquant_+_Lien_web_vs_Article
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *(?:ref|référence|référence simplifiée) *= *harv *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Bot/Requ%C3%AAtes/2020/01#Remplacement_automatique_d%27un_message_d%27erreur_du_mod%C3%A8le_%7B%7BOuvrage%7D%7D
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *display\-authors *= *etal *([\|}\n]+)', r'{{\1uvrage\2|et al.=oui\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *display\-authors *= *[0-9]* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    current_page = re.sub(r'{{ *(o|O)uvrage *((?:\||\n)[^}]*)\| *df *= *(?:mdy\-all|dmy\-all)* *([\|}\n]+)', r'{{\1uvrage\2\3', current_page)
    # Empty 1=
    current_page = re.sub(r'{{ *(a|A)rticle *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1rticle\2\3', current_page)
    current_page = re.sub(r'{{ *(l|L)ien web *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1ien web\2\3', current_page)
    # 1= exists: current_page = re.sub(r'{{ *(o|O)uvrage *((?:\|)[^}]*)\|[ \t]*([\|}]+)', r'{{\1uvrage\2\3', current_page)
    ''' TODO : à vérifier
    while current_page.find('|deadurl=no|') != -1:
        current_page = current_page[:current_page.find('|deadurl=no|')+1] + current_page[current_page.find('|deadurl=no|')+len('|deadurl=no|'):]
    '''

    finalPage = finalPage + current_page

    # TODO: avoid these fixes when: oldTemplate.append('lien mort')
    finalPage = finalPage.replace('<ref></ref>',u'')
    finalPage = finalPage.replace('{{lien mortarchive',u'{{lien mort archive')
    finalPage = finalPage.replace('|langue=None', '')
    finalPage = finalPage.replace('|langue=en|langue=en', '|langue=en')
    if debug_level > 0: print('Fin hyperlynx.py')

    return finalPage


def getURLsite_language(html_source, debug_level = 0):
    if debug_level > 0:
        print('getURLsite_language: code langue à remplacer une fois trouvé sur la page distante...')
    URLlanguage = 'None'
    try:
        regex = '<html [^>]*lang *= *"?\'?([a-zA-Z\-]+)'
        result = re.search(regex, html_source)
        if result:
            URLlanguage = result.group(1)
            if debug_level > 0: print(' Langue trouvée sur le site')
            if (len(URLlanguage)) > 6: URLlanguage = 'None'
    except UnicodeDecodeError:
        if debug_level > 0: print('UnicodeEncodeError l 1032')
    if debug_level > 0: print(' Langue retenue : ') + URLlanguage
    return URLlanguage


def testURL(url, debug_level = 0, opener=None):
    # Renvoie la page web d'une URL dès qu'il arrive à la lire.
    if checkURL == False:
        return 'ok'
    if debug_level > 0:
        print('--------')

    for blacklisted in brokenDomains:
        if url.find(blacklisted) != -1:
            if debug_level > 0:
                print(' broken domain')
            return 'ko'
    for whitelisted in blockedDomains:
        if url.find(whitelisted) != -1:
            if debug_level > 0:
                print(' authorized domain')
            return 'ok'
    for whitelisted in authorizedFiles:
        if url[len(url)-len(whitelisted):] == whitelisted:
            if debug_level > 0:
                print(' authorized file')
            return 'ok'

    html_source = ''
    connection_method = 'Request'
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req) # If blocked here for hours, just whitelist the domain if the page isn't forbidden
        # TODO : ssl.CertificateError: hostname 'www.mediarodzina.com.pl' doesn't match either of 'mediarodzina.pl', 'www.mediarodzina.pl'
        # UnicodeWarning: Unicode unequal comparison failed to convert both arguments to Unicode
        html_source = res.read()
        if debug_level > 0:
            print(str(len(html_source)))
        if html_source != str(''): return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')  # ex : got more than 100 headers
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'opener'
        try:
            opener = urllib2.build_opener()
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''):
                return html_source
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
        # pb avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304 qui renvoie 301 car son suffixe est facultatif
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : ssl.CertificateError')
        # HS : https://fr.wikipedia.org/w/index.php?title=Herv%C3%A9_Moulin&type=revision&diff=135989688&oldid=135121040
        url = url.replace('https:', 'http:')
        try:
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return html_source
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = "urllib2.urlopen(url.encode('utf8'))"
    try:
        html_source = urllib2.urlopen(url.encode('utf8')).read()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''):
            return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'HTTPCookieProcessor'
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            response = opener.open(url)
            html_source = response.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''):
                return html_source
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
        
    connection_method = 'Request text/html'    
    try:
        req = urllib2.Request(url)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0: print(connection_method + ' : text/html ' + str(len(html_source)))
        if html_source != str(''):
            return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'geturl()'
        try:
            resp = urllib2.urlopen(url)
            req = urllib2.Request(resp.geturl())
            res = urllib2.urlopen(req)
            html_source = res.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return html_source
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'Request Mozilla/5.0'
    agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        headers = {'User-Agent': agent}
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0:
            print(connection_method + ' : ' + agent + ' : ' + str(len(html_source)))
        if html_source != str(''):
            return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        if e.code == "404": return "404 error"
        if socket.gethostname() == 'PavilionDV6':
            connection_method = 'follow_all_redirects'    # fonctionne avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304
            try:
                r = requests.get(url)
                req = urllib2.Request(r.url)
                res = urllib2.urlopen(req)
                html_source = res.read()
                if debug_level > 0: print(str(len(html_source)))
                if html_source != str(''): return html_source
            except UnicodeEncodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
            except UnicodeDecodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
            except UnicodeError:
                if debug_level > 0: print(connection_method + ' : UnicodeError')
                connection_method = "Méthode url.encode('utf8')"
                try:
                    sock = urllib.urlopen(url.encode('utf8'))
                    html_source = sock.read()
                    sock.close()
                    if debug_level > 0: print(str(len(html_source)))
                    if html_source != str(''): return html_source
                except UnicodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeError')
                except UnicodeEncodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
                except UnicodeDecodeError:
                    if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
                except httplib.BadStatusLine:
                    if debug_level > 0: print(connection_method + ' : BadStatusLine')
                except httplib.InvalidURL:
                    if debug_level > 0: print(connection_method + ' : InvalidURL')
                except httplib.HTTPException:
                    if debug_level > 0: print(connection_method + ' : HTTPException')
                except urllib2.HTTPError as e:
                    if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
                except IOError as e:
                    if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
                except urllib2.URLError:
                    if debug_level > 0: print(connection_method + ' : URLError')
                except MemoryError:
                    if debug_level > 0: print(connection_method + ' : MemoryError')
                except requests.exceptions.HTTPError:
                    if debug_level > 0: print(connection_method + ' : HTTPError')
                except requests.exceptions.SSLError:
                    if debug_level > 0: print(connection_method + ' : SSLError')
                except ssl.CertificateError:
                    if debug_level > 0: print(connection_method + ' : CertificateError')
            except httplib.BadStatusLine:
                if debug_level > 0: print(connection_method + ' : BadStatusLine')
            except httplib.InvalidURL:
                if debug_level > 0: print(connection_method + ' : InvalidURL')
            except httplib.HTTPException:
                if debug_level > 0: print(connection_method + ' : HTTPException')
            except urllib2.HTTPError as e:
                if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
            except urllib2.URLError:
                if debug_level > 0: print(connection_method + ' : URLError')
            except requests.exceptions.TooManyRedirects:
                if debug_level > 0: print(connection_method + ' : TooManyRedirects')
            except IOError as e:
                if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
            except requests.exceptions.SSLError:
                if debug_level > 0: print(connection_method + ' : SSLError')
            except requests.exceptions.ConnectionError:
                if debug_level > 0: print(connection_method + ' ConnectionError')
            except requests.exceptions.InvalidSchema:
                if debug_level > 0: print(connection_method + ' InvalidSchema')
            except MemoryError:
                if debug_level > 0: print(connection_method + ' : MemoryError')
            except requests.exceptions.HTTPError:
                if debug_level > 0: print(connection_method + ' : HTTPError')
            except ssl.CertificateError:
                if debug_level > 0: print(connection_method + ' : CertificateError')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'Request &_r=4&'
    agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    try:
        if url.find('_r=') == -1:
            if url.find('?') != -1:
                url = url + "&_r=4&"
            else:
                url = url + "?_r=4&"
        else:
            if url.find('?') != -1:
                url = url[0:url.find('_r=')-1] + "&_r=4&"
            else:
                url = url[0:url.find('_r=')-1] + "?_r=4&"
        headers = {'User-Agent': agent}
        req = urllib2.Request(url, "", headers)
        req.add_header('Accept','text/html')
        res = urllib2.urlopen(req)
        html_source = res.read()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        connection_method = 'HTTPRedirectHandler'
        try:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            request = opener.open(url)
            req = urllib2.Request(request.url)
            res = urllib2.urlopen(req)
            html_source = res.read()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return html_source
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')     
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'urlopen'    # fonctionne avec http://voxofilm.free.fr/vox_0/500_jours_ensemble.htm, et http://www.kurosawa-drawings.com/page/27
    try:
        res = urllib2.urlopen(url)
        html_source = res.read()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return html_source
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        if e.code == 401: return "ok"    # http://www.nature.com/nature/journal/v442/n7104/full/nature04945.html
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
    except urllib2.URLError:
        if debug_level > 0: print(connection_method + ' : URLError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')

    connection_method = 'urllib.urlopen'
    try:
        sock = urllib.urlopen(url)
        html_source = sock.read()
        sock.close()
        if debug_level > 0: print(str(len(html_source)))
        if html_source != str(''): return html_source
    except httplib.BadStatusLine:
        if debug_level > 0: print(connection_method + ' : BadStatusLine')
    except httplib.InvalidURL:
        if debug_level > 0: print(connection_method + ' : InvalidURL')
    except httplib.IncompleteRead:
        if debug_level > 0: print(connection_method + ' : IncompleteRead')
    except httplib.HTTPException:
        if debug_level > 0: print(connection_method + ' : HTTPException')
    except IOError as e:
        if debug_level > 0: print(connection_method + ' : I/O error')
    except urllib2.URLError as e:
        if debug_level > 0: print(connection_method + ' : URLError %s.' % e.code)
    except urllib2.HTTPError as e:
        if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
    except UnicodeEncodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
    except UnicodeDecodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
    except MemoryError:
        if debug_level > 0: print(connection_method + ' : MemoryError')
    except requests.exceptions.HTTPError:
        if debug_level > 0: print(connection_method + ' : HTTPError')
    except requests.exceptions.SSLError:
        if debug_level > 0: print(connection_method + ' : SSLError')
    except ssl.CertificateError:
        if debug_level > 0: print(connection_method + ' : CertificateError')
    except UnicodeError:
        if debug_level > 0: print(connection_method + ' : UnicodeError')
        connection_method = "Méthode url.encode('utf8')"
        try:
            sock = urllib.urlopen(url.encode('utf8'))
            html_source = sock.read()
            sock.close()
            if debug_level > 0: print(str(len(html_source)))
            if html_source != str(''): return html_source
        except UnicodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeError')
        except UnicodeEncodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeEncodeError')
        except UnicodeDecodeError:
            if debug_level > 0: print(connection_method + ' : UnicodeDecodeError')
        except httplib.BadStatusLine:
            if debug_level > 0: print(connection_method + ' : BadStatusLine')
        except httplib.InvalidURL:
            if debug_level > 0: print(connection_method + ' : InvalidURL')
        except httplib.HTTPException:
            if debug_level > 0: print(connection_method + ' : HTTPException')
        except urllib2.HTTPError as e:
            if debug_level > 0: print(connection_method + ' : HTTPError %s.' % e.code)
        except IOError as e:
            if debug_level > 0: print(connection_method + ' : I/O error({0}): {1}'.format(e.errno, e.strerror))
        except urllib2.URLError:
            if debug_level > 0: print(connection_method + ' : URLError')
        except MemoryError:
            if debug_level > 0: print(connection_method + ' : MemoryError')
        except requests.exceptions.HTTPError:
            if debug_level > 0: print(connection_method + ' : HTTPError')
        except requests.exceptions.SSLError:
            if debug_level > 0: print(connection_method + ' : SSLError')
        except ssl.CertificateError:
            if debug_level > 0: print(connection_method + ' : CertificateError')
    if debug_level > 0:
        print(connection_method + ' Fin du test d\'existance du site')
    return ''

def testURLPage(html_source, url, debug_level = 0):
    is_broken_link = False
    try:
        #if debug_level > 1 and html_source != str('') and html_source is not None: input(html_source[0:1000])
        if html_source is None:
            if debug_level > 0: print(url + " none type")
            return True
        elif html_source == str('ok') or (html_source == str('') and (url.find('à') != -1 or url.find('é') != -1
            or url.find('è') != -1 or url.find('ê') != -1 or url.find('ù') != -1)):
            # bug http://fr.wikipedia.org/w/index.php?title=Acad%C3%A9mie_fran%C3%A7aise&diff=prev&oldid=92572792
            return False
        elif html_source == str('ko') or html_source == str(''):
            if debug_level > 0: print(url + " page vide")
            return True
        else:
            if debug_level > 0: print(' Page non vide')
            # Recherche des erreurs
            for e in range(0,limiteE):
                if debug_level > 1: print(Erreur[e])
                if html_source.find(Erreur[e]) != -1 and not re.search("\n[^\n]*if[^\n]*" + Erreur[e], html_source):
                    if debug_level > 1: print('  Trouvé')
                    # Exceptions
                    if Erreur[e] == "404 Not Found" and url.find("audiofilemagazine.com") == -1:    # Exception avec popup formulaire en erreur
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    # Wikis : page vide à créer
                    if Erreur[e] == "Soit vous avez mal &#233;crit le titre" and url.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    elif Erreur[e] == "Il n'y a pour l'instant aucun texte sur cette page." != -1 and html_source.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    elif Erreur[e] == "There is currently no text in this page." != -1 and html_source.find("wiki") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    # Sites particuliers
                    elif Erreur[e] == "The page you requested cannot be found" and url.find("restaurantnewsresource.com") == -1:
                        # bug avec http://www.restaurantnewsresource.com/article35143 (Landry_s_Restaurants_Opens_T_REX_Cafe_at_Downtown_Disney.html)
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    elif Erreur[e] == "Terme introuvable" != -1 and html_source.find("Site de l'ATILF") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    elif Erreur[e] == "Cette forme est introuvable !" != -1 and html_source.find("Site de l'ATILF") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    elif Erreur[e] == "Sorry, no matching records for query" != -1 and html_source.find("ATILF - CNRS") != -1:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break
                    else:
                        is_broken_link = True
                        if debug_level > 0: print(url + " : " + Erreur[e])
                        break

    except UnicodeError:
        if debug_level > 0: print('UnicodeError lors de la lecture')
        is_broken_link = False
    except UnicodeEncodeError:
        if debug_level > 0: print('UnicodeEncodeError lors de la lecture')
        is_broken_link = False
    except UnicodeDecodeError:
        if debug_level > 0: print('UnicodeDecodeError lors de la lecture')
        is_broken_link = False
    except httplib.BadStatusLine:
        if debug_level > 0: print('BadStatusLine lors de la lecture')
    except httplib.InvalidURL:
        if debug_level > 0: print('InvalidURL lors de la lecture')
        is_broken_link = False
    except httplib.HTTPException:
        if debug_level > 0: print('HTTPException')
        is_broken_link = False
    except urllib2.HTTPError as e:
        if debug_level > 0: print('HTTPError %s.' % e.code +  ' lors de la lecture')
        is_broken_link = False
    except IOError as e:
        if debug_level > 0: print('I/O error({0}): {1}'.format(e.errno, e.strerror) +  ' lors de la lecture')
        is_broken_link = False
    except urllib2.URLError:
        if debug_level > 0: print('URLError lors de la lecture')
        is_broken_link = False
    else:
        if debug_level > 1: print('Fin du test du contenu')
    return is_broken_link


def getCurrentLinkTemplate(current_page):
    # Extraction du modèle de lien en tenant compte des modèles inclus dedans
    current_page2 = current_page
    templateEndPosition = 0
    while current_page2.find('{{') != -1 and current_page2.find('{{') < current_page2.find('}}'):
        templateEndPosition = templateEndPosition + current_page.find('}}')+2
        current_page2 = current_page2[current_page2.find('}}')+2:]
    templateEndPosition = templateEndPosition + current_page2.find('}}')+2
    currentTemplate = current_page[:templateEndPosition]

    if debug_level > 1:
        print('  getCurrentLinkTemplate()')
        print(templateEndPosition)
        input(currentTemplate)

    return currentTemplate, templateEndPosition


def translateTemplateParameters(currentTemplate):
    if debug_level > 1: print('Remplacement des anciens paramètres, en tenant compte des doublons et des variables selon les modèles')
    for p in range(0, limiteP):
        if debug_level > 1: print(oldParam[p])
        frName = newParam[p]
        if oldParam[p] == 'work':
            if isTemplate(currentTemplate, 'article') and not hasParameter(currentTemplate, 'périodique'):
                frName = 'périodique'
            elif isTemplate(currentTemplate, 'lien web') and not hasParameter(currentTemplate, 'site') and not hasParameter(currentTemplate, 'website'):
                frName = 'site'
            else:
                frName = 'série'
        elif oldParam[p] == 'publisher':
            if isTemplate(currentTemplate, 'article') and not hasParameter(currentTemplate, 'périodique') and not hasParameter(currentTemplate, 'work'):
                frName = 'périodique'
            else:
                frName = 'éditeur'
        elif oldParam[p] == 'agency':
            if isTemplate(currentTemplate, 'article') and not hasParameter(currentTemplate, 'périodique') and not hasParameter(currentTemplate, 'work'):
                frName = 'périodique'
            else:
                frName = 'auteur institutionnel'
        elif oldParam[p] == 'issue' and hasParameter(currentTemplate, 'numéro'):
            frName = 'date' 
        elif oldParam[p] == 'editor':
            if hasParameter(currentTemplate, 'éditeur'):
                frName = 'auteur'
        elif oldParam[p] == 'en ligne le':
            if currentTemplate.find('archiveurl') == -1 and currentTemplate.find('archive url') == -1 and currentTemplate.find('archive-url') == -1:
                continue
            elif currentTemplate.find('archivedate') != -1 or currentTemplate.find('archive date') != -1 or currentTemplate.find('archive-date') != -1:
                continue
            elif debug_level > 0:
                print(' archiveurl ' + ' archivedate')

        regex = r'(\| *)' + newParam[p] + r'( *=)'
        hasDouble = re.search(regex, currentTemplate)
        if not hasDouble:
            regex = r'(\| *)' + oldParam[p] + r'( *=)'
            currentTemplate = re.sub(regex, r'\1' + frName + r'\2', currentTemplate)
    currentTemplate = currentTemplate.replace('|=',u'|')
    currentTemplate = currentTemplate.replace('| =',u'|')
    currentTemplate = currentTemplate.replace('|  =',u'|')
    currentTemplate = currentTemplate.replace('|}}',u'}}')
    currentTemplate = currentTemplate.replace('| }}',u'}}')
    hasIncludedTemplate = currentTemplate.find('{{') != -1
    if not hasIncludedTemplate:
        currentTemplate = currentTemplate.replace('||',u'|')

    return currentTemplate


def translateLinkTemplates(current_page):
    finalPage = ''
    for m in range(0, limiteL):
        # Formatage des anciens modèles
        current_page = re.sub(('(Modèle:)?[' + oldTemplate[m][:1] + r'|' + oldTemplate[m][:1].upper() + r']' + oldTemplate[m][1:]).replace(' ', '_') + r' *\|', oldTemplate[m] + r'|', current_page)
        current_page = re.sub(('(Modèle:)?[' + oldTemplate[m][:1] + r'|' + oldTemplate[m][:1].upper() + r']' + oldTemplate[m][1:]).replace(' ', '  ') + r' *\|', oldTemplate[m] + r'|', current_page)
        current_page = re.sub(('(Modèle:)?[' + oldTemplate[m][:1] + r'|' + oldTemplate[m][:1].upper() + r']' + oldTemplate[m][1:]) + r' *\|', oldTemplate[m] + r'|', current_page)
        # Traitement de chaque modèle à traduire
        while re.search('{{[\n ]*' + oldTemplate[m] + ' *[\||\n]+', current_page):
            if debug_level > 1:
                print('Modèle n°' + str(m))
                print(current_page[re.search('{{[\n ]*' + oldTemplate[m] + ' *[\||\n]', current_page).end()-1:][:100])
            finalPage = finalPage + current_page[:re.search('{{[\n ]*' + oldTemplate[m] + ' *[\||\n]', current_page).end()-1]
            current_page = current_page[re.search('{{[\n ]*' + oldTemplate[m] + ' *[\||\n]', current_page).end()-1:]    
            # Identification du code langue existant dans le modèle
            language_code = ''
            if finalPage.rfind('{{') != -1:
                PageDebut = finalPage[:finalPage.rfind('{{')]
                if PageDebut.rfind('{{') != -1 and PageDebut.rfind('}}') != -1 and (PageDebut[len(PageDebut)-2:] == '}}' or PageDebut[len(PageDebut)-3:] == '}} '):
                    language_code = PageDebut[PageDebut.rfind('{{')+2:PageDebut.rfind('}}')]
                    if site.family in ['wikipedia', 'wiktionary']:
                        # Recherche de validité mais tous les codes ne sont pas encore sur les sites francophones
                        if language_code.find('}}') != -1: language_code = language_code[:language_code.find('}}')]
                        if debug_level > 1: print('Modèle:') + language_code
                        page2 = Page(site, 'Modèle:' + language_code)
                        try:
                            PageCode = page2.get()
                        except pywikibot.exceptions.NoPage:
                            print('NoPage l 425')
                            PageCode = ''
                        except pywikibot.exceptions.LockedPage: 
                            print('Locked l 428')
                            PageCode = ''
                        except pywikibot.exceptions.IsRedirectPage: 
                            PageCode = page2.get(get_redirect=True)
                        if debug_level > 0: print(PageCode)
                        if PageCode.find('Indication de langue') != -1:
                            if len(language_code) == 2:    # or len(language_code) == 3: if language_code == 'pdf': |format=language_code, absent de {{lien web}}
                                # Retrait du modèle de langue devenu inutile
                                finalPage = finalPage[:finalPage.rfind('{{' + language_code + '}}')] + finalPage[finalPage.rfind('{{' + language_code + '}}')+len('{{' + language_code + '}}'):]
            if language_code == '':
                if debug_level > 0: print(' Code langue à remplacer une fois trouvé sur la page distante...')
                language_code = 'None'
            # Ajout du code langue dans le modèle
            if debug_level > 0: print('Modèle préalable : ') + language_code
            regex = r'[^}]*lang(ue|uage)* *=[^}]*}}'
            if not re.search(regex, current_page):
                current_page = '|langue=' + language_code + current_page
            elif re.search(regex, current_page).end() > current_page.find('}}')+2:
                current_page = '|langue=' + language_code + current_page
                
        current_page = finalPage + current_page
        finalPage = ''

    for m in range(0, limiteM):
        if debug_level > 1: print(' Traduction des noms du modèle ' + oldTemplate[m])
        current_page = current_page.replace('{{' + oldTemplate[m] + ' ', '{{' + oldTemplate[m] + '')
        current_page = re.sub(r'({{[\n ]*)[' + oldTemplate[m][:1] + r'|' + oldTemplate[m][:1].upper() + r']' + \
              oldTemplate[m][1:len(oldTemplate[m])] + r'( *[|\n\t}])', r'\1' +  newTemplate[m] + r'\2', current_page)
        # Suppression des modèles vides
        regex = '{{ *[' + newTemplate[m][:1] + r'|' + newTemplate[m][:1].upper() + r']' + newTemplate[m][1:len(newTemplate[m])] + r' *}}'
        while re.search(regex, current_page):
            current_page = current_page[:re.search(regex, current_page).start()] + current_page[re.search(regex, current_page).end():]
        # Traduction des paramètres de chaque modèle de la page
        regex = '{{ *[' + newTemplate[m][:1] + r'|' + newTemplate[m][:1].upper() + r']' + newTemplate[m][1:len(newTemplate[m])] + r' *[\||\n]'
        while re.search(regex, current_page):
            finalPage = finalPage + current_page[:re.search(regex, current_page).start()+2]
            current_page = current_page[re.search(regex, current_page).start()+2:]
            currentTemplate, templateEndPosition = getCurrentLinkTemplate(current_page)
            current_page = translateTemplateParameters(currentTemplate) + current_page[templateEndPosition:]

        current_page = finalPage + current_page
        finalPage = ''

    return current_page


def translateDates(current_page):
    if debug_level > 1: print('  translateDates()')
    date_parameters = ['date', 'mois', 'consulté le', 'en ligne le', 'dts', 'Dts', 'date triable', 'Date triable']
    for m in range(1, monthLine + 1):
        if debug_level > 1:
            print('Mois ') + str(m)
            print(TradM[m][1])
        for p in range(1, len(date_parameters)):
            if debug_level > 1: print('Recherche de ') + date_parameters[p] + ' *=[ ,0-9]*' + TradM[m][1]
            if p > 4:
                current_page = re.sub(r'({{ *' + date_parameters[p] + r'[^}]+)' + TradM[m][1] + r'([^}]+}})', r'\1' +  TradM[m][2] + r'\2', current_page)
                current_page = re.sub(r'({{ *' + date_parameters[p] + r'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' + TradM[m][2] + r'(\|[ 0-9][ 0-9])}}', r'\1\3|' +  TradM[m][2] + r'\2}}', current_page)
            else:
                current_page = re.sub(r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + TradM[m][1] + r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' +  TradM[m][2] + r'\2', current_page)
                current_page = re.sub(r'(\| *' + date_parameters[p] + r' *=[ ,0-9]*)' + TradM[m][1][:1].lower() + TradM[m][1][1:] + r'([ ,0-9]*\.? *[<|\||\n\t|}])', r'\1' +  TradM[m][2] + r'\2', current_page)
                
                # Ordre des dates : jj mois aaaa
                if debug_level > 1: print('Recherche de ') + date_parameters[p] + ' *= *' + TradM[m][2] + ' *([0-9]+), '
                current_page = re.sub(r'(\| *' + date_parameters[p] + ' *= *)' + TradM[m][2] + r' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])', r'\1' + r'\2' + r' ' + TradM[m][2] + r' ' + r'\3' + r'\4', current_page)    # trim('\3') ne fonctionne pas
 
    return current_page


def translateLanguages(current_page):
    if debug_level > 1: print('  translateLanguages()')
    for l in range(1, ligneL+1):
        if debug_level > 1:
            print('Langue ') + str(l)
            print(TradL[l][1])
        current_page = re.sub(r'(\| *langue *= *)' + TradL[l][1] + r'( *[<|\||\n\t|}])', r'\1' +  TradL[l][2] + r'\2', current_page)

        # TODO rustine suite à un imprévu censé être réglé ci-dessus, mais qui touche presque 10 % des pages.
        current_page = re.sub(r'{{' + TradL[l][2] + r'}}[ \n]*({{[Aa]rticle\|langue=' + TradL[l][2] + r'\|)', r'\1', current_page)
        current_page = re.sub(r'{{' + TradL[l][2] + r'}}[ \n]*({{[Ll]ien web\|langue=' + TradL[l][2] + r'\|)', r'\1', current_page)
        current_page = re.sub(r'{{' + TradL[l][2] + r'}}[ \n]*({{[Oo]uvrage\|langue=' + TradL[l][2] + r'\|)', r'\1', current_page)
 
    return current_page

def isTemplate(string, template):
    regex = r'^(' + template[:1].upper() + r'|' + template[:1].lower() + r')' + template[1:]
    return re.search(regex, string)

def hasParameter(string, param):
    regex = r'\| *' + param + r' *='
    return re.search(regex, string)

#!/usr/bin/env python
# coding: utf-8
'''
Ce script vérifie toutes les URL des articles :
	1) de la forme http://, https:// et [//
	2) incluses dans certains modèles (pas tous étant donnée leur complexité, car certains incluent des {{{1}}} et {{{2}}} dans leurs URL)
	3) il traduit les noms et paramètres de ces modèles en français (ex : {{cite web|title=}} par {{lien web|titre=}})
	4) il ajoute ou retire {{lien brisé}} le cas échéant
'''
# {{Date|3|M->mai|2012}}

# Déclaration
import sys, os, catlib, pagegenerators, codecs, urllib, urllib2, httplib, json, pprint, urlparse, datetime, re, webbrowser, cookielib, socket #, ssl
if socket.gethostname() == "1011PX":
	sys.path.append(u'/usr/local/lib/python2.7/dist-packages/requests')
elif socket.gethostname() == u'PavilionDV6':
	import requests
	
from wikipedia import *
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)

# Préférences
debogage = False
debogageLent = False
semiauto = False
retablirNonBrise = False

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
ModeleEN.append(u'lien mort')
ModeleFR.append(u'lien brisé')
# Modèles sans paramètre langue l 545
ModeleEN.append(u'cita web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'cita noticia')
ModeleFR.append(u'lien news')
ModeleEN.append(u'web site')
ModeleFR.append(u'lien web')
ModeleEN.append(u'site web')
ModeleFR.append(u'lien web')
ModeleEN.append(u'lire en ligne')
ModeleFR.append(u'lire en ligne')
ModeleEN.append(u'dts')
ModeleFR.append(u'dts')
ModeleEN.append(u'Quote')
ModeleFR.append(u'Citation bloc')
limiteM = len(ModeleFR)
# Désactivé à la demande d'un contributeur sur WP : https://fr.wikipedia.org/wiki/Discussion_utilisateur:JackPotte/Archives2013#Traduction_de_cite_book_vers_ouvrage
#ModeleEN[18] = u'cite book'
#ModeleFR[18] = u'ouvrage'
#spécifier le remplacement “citation” s'il a les paramètres du modèle anglais.

# Demande de [[Discussion modèle:ouvrage]]
#ModeleEN[] = u'cite book'
#ModeleFR[] = u'ouvrage'

# Paramètres à remplacer
limiteP = 121
ParamEN = range(1, limiteP +1)
ParamFR = range(1, limiteP +1)
ParamEN[1] = u'author'
ParamFR[1] = u'auteur'
ParamEN[2] = u'authorlink1'
ParamFR[2] = u'lien auteur1'
ParamEN[3] = u'title'
ParamFR[3] = u'titre'
ParamEN[4] = u'publisher'
ParamFR[4] = u'éditeur'
ParamEN[5] = u'work'	# paramètre de {{lien web}} différent pour {{article}}
ParamFR[5] = u'périodique'
ParamEN[6] = u'newspaper'
ParamFR[6] = u'journal'
ParamEN[7] = u'day'
ParamFR[7] = u'jour'
ParamEN[8] = u'month'
ParamFR[8] = u'mois'
ParamEN[9] = u'year'
ParamFR[9] = u'année'
ParamEN[10] = u'accessdate'
ParamFR[10] = u'consulté le'
ParamEN[11] = u'language'
ParamFR[11] = u'langue'
ParamEN[12] = u'quote'
ParamFR[12] = u'extrait'
ParamEN[13] = u'titre vo'
ParamFR[13] = u'titre original'
ParamEN[14] = u'first'
ParamFR[14] = u'prénom'
ParamEN[15] = u'surname'
ParamFR[15] = u'nom'
ParamEN[16] = u'last'
ParamFR[16] = u'nom'
ParamEN[17] = u'first1'
ParamFR[17] = u'prénom1'
ParamEN[18] = u'last1'
ParamFR[18] = u'nom1'
ParamEN[19] = u'first2'
ParamFR[19] = u'prénom2'
ParamEN[20] = u'last2'
ParamFR[20] = u'nom2'
ParamEN[21] = u'first3'
ParamFR[21] = u'prénom3'
ParamEN[22] = u'last3'
ParamFR[22] = u'nom3'
ParamEN[23] = u'first4'
ParamFR[23] = u'prénom4'
ParamEN[24] = u'last4'
ParamFR[24] = u'nom4'
ParamEN[25] = u'first5'
ParamFR[25] = u'prénom5'
ParamEN[26] = u'last5'
ParamFR[26] = u'nom5'
ParamEN[27] = u'first6'
ParamFR[27] = u'prénom6'
ParamEN[28] = u'last6'
ParamFR[28] = u'nom6'
ParamEN[29] = u'first7'
ParamFR[29] = u'prénom7'
ParamEN[30] = u'last7'
ParamFR[30] = u'nom7'
ParamEN[31] = u'first8'
ParamFR[31] = u'prénom8'
ParamEN[32] = u'last8'
ParamFR[32] = u'nom8'
ParamEN[33] = u'first9'
ParamFR[33] = u'prénom9'
ParamEN[34] = u'last9'
ParamFR[34] = u'nom9'
ParamEN[35] = u'issue'
ParamFR[35] = u'numéro'
ParamEN[36] = u'authorlink'
ParamFR[36] = u'lien auteur'
ParamEN[37] = u'author-link'
ParamFR[37] = u'lien auteur'
ParamEN[38] = u'authorlink1'
ParamFR[38] = u'lien auteur1'
ParamEN[39] = u'author1-link'
ParamFR[39] = u'lien auteur1'
ParamEN[40] = u'coauthorlink'
ParamFR[40] = u'lien coauteur'
ParamEN[41] = u'coauthor-link'
ParamFR[41] = u'lien coauteur'
ParamEN[42] = u'authorlink2'
ParamFR[42] = u'lien auteur2'
ParamEN[43] = u'author2-link'
ParamFR[43] = u'lien auteur2'
ParamEN[44] = u'authorlink3'
ParamFR[44] = u'lien auteur3'
ParamEN[45] = u'author3-link'
ParamFR[45] = u'lien auteur3'
ParamEN[46] = u'authorlink4'
ParamFR[46] = u'lien auteur4'
ParamEN[47] = u'author4-link'
ParamFR[47] = u'lien auteur4'
ParamEN[48] = u'authorlink5'
ParamFR[48] = u'lien auteur5'
ParamEN[49] = u'author5-link'
ParamFR[49] = u'lien auteur5'
ParamEN[50] = u'authorlink6'
ParamFR[50] = u'lien auteur6'
ParamEN[51] = u'author6-link'
ParamFR[51] = u'lien auteur6'
ParamEN[52] = u'authorlink7'
ParamFR[52] = u'lien auteur7'
ParamEN[53] = u'author7-link'
ParamFR[53] = u'lien auteur7'
ParamEN[54] = u'authorlink8'
ParamFR[54] = u'lien auteur8'
ParamEN[55] = u'author8-link'
ParamFR[55] = u'lien auteur8'
ParamEN[56] = u'authorlink9'
ParamFR[56] = u'lien auteur9'
ParamEN[57] = u'author9-link'
ParamFR[57] = u'lien auteur9'
ParamEN[58] = u'authorlink10'
ParamFR[58] = u'lien auteur10'
ParamEN[59] = u'author10-link'
ParamFR[59] = u'lien auteur10'
ParamEN[60] = u'surname1'
ParamFR[60] = u'nom1'
ParamEN[61] = u'coauthors'
ParamFR[61] = u'coauteurs'
ParamEN[62] = u'co-auteurs'
ParamFR[62] = u'coauteurs'
ParamEN[63] = u'co-auteur'
ParamFR[63] = u'coauteur'
ParamEN[64] = u'surname2'
ParamFR[64] = u'nom2'
ParamEN[65] = u'surname3'
ParamFR[65] = u'nom3'
ParamEN[66] = u'surname4'
ParamFR[66] = u'nom4'
ParamEN[67] = u'surname5'
ParamFR[67] = u'nom5'
ParamEN[68] = u'surname6'
ParamFR[68] = u'nom6'
ParamEN[69] = u'surname7'
ParamFR[69] = u'nom7'
ParamEN[70] = u'surname8'
ParamFR[70] = u'nom8'
ParamEN[71] = u'surname9'
ParamFR[71] = u'nom9'
ParamEN[72] = u'surname10'
ParamFR[72] = u'nom10'
ParamEN[73] = u'given'
ParamFR[73] = u'prénom'
ParamEN[74] = u'given1'
ParamFR[74] = u'prénom1'
ParamEN[75] = u'given2'
ParamFR[75] = u'prénom2'
ParamEN[76] = u'given3'
ParamFR[76] = u'prénom3'
ParamEN[77] = u'given4'
ParamFR[77] = u'prénom4'
ParamEN[78] = u'given5'
ParamFR[78] = u'prénom5'
ParamEN[79] = u'given6'
ParamFR[79] = u'prénom6'
ParamEN[80] = u'given7'
ParamFR[80] = u'prénom7'
ParamEN[81] = u'given8'
ParamFR[81] = u'prénom8'
ParamEN[82] = u'given9'
ParamFR[82] = u'prénom9'
ParamEN[83] = u'given10'
ParamFR[83] = u'prénom10'
ParamEN[84] = u'trad'
ParamFR[84] = u'traducteur'
ParamEN[85] = u'at'
ParamFR[85] = u'passage'
ParamEN[86] = u'origyear'
ParamFR[86] = u'année première impression'
ParamEN[87] = u'location'
ParamFR[87] = u'lieu'
ParamEN[88] = u'place'
ParamFR[88] = u'lieu'
ParamEN[89] = u'publication-date'
ParamFR[89] = u'année'
ParamEN[90] = u'writers'
ParamFR[90] = u'scénario'
ParamEN[91] = u'episodelink'
ParamFR[91] = u'lien épisode'
ParamEN[92] = u'serieslink'
ParamFR[92] = u'lien série'
ParamEN[93] = u'titlelink'
ParamFR[93] = u'lien titre'
ParamEN[94] = u'credits'
ParamFR[94] = u'crédits'
ParamEN[95] = u'network'
ParamFR[95] = u'réseau'
ParamEN[96] = u'station'
ParamFR[96] = u'chaîne'
ParamEN[97] = u'city'
ParamFR[97] = u'ville'
ParamEN[98] = u'began'
ParamFR[98] = u'début'
ParamEN[99] = u'ended'
ParamFR[99] = u'fin'
ParamEN[100] = u'diffusion'
ParamFR[100] = u'airdate'
ParamEN[101] = u'number'
ParamFR[101] = u'numéro'
ParamEN[102] = u'season'
ParamFR[102] = u'saison'
ParamEN[103] = u'year2'
ParamFR[103] = u'année2'
ParamEN[104] = u'month2'
ParamFR[104] = u'mois2'
ParamEN[105] = u'time'
ParamFR[105] = u'temps'
ParamEN[106] = u'accessyear'
ParamFR[106] = u'année accès'
ParamEN[107] = u'accessmonth'
ParamFR[107] = u'mois accès'
ParamEN[108] = u'conference'
ParamFR[108] = u'conférence'
ParamEN[109] = u'conferenceurl'
ParamFR[109] = u'urlconférence'
ParamEN[110] = u'others'
ParamFR[110] = u'autres'
ParamEN[111] = u'booktitle'
ParamFR[111] = u'titre livre'
ParamEN[112] = u'autor'
ParamFR[112] = u'auteur'
ParamEN[113] = u'título'
ParamFR[113] = u'titre' 
ParamEN[114] = u'fechaacceso'
ParamFR[114] = u'consulté le'
ParamEN[115] = u'fecha'
ParamFR[115] = u'date'
ParamEN[116] = u'obra'
ParamFR[116] = u'série' 
ParamEN[117] = u'idioma'
ParamFR[117] = u'langue' 
ParamEN[118] = u'publicació'
ParamFR[118] = u'éditeur' 
ParamEN[119] = u'editorial'
ParamFR[119] = u'journal'
ParamEN[120] = u'archivedate'
ParamFR[120] = u'en ligne le'

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
#FinDURL[] = u'~'	# dans 1ère RFC seulement
# Caractères qui ne peuvent pas être en dernière position d'une URL :
limiteURL2 = 7
FinDURL2 = range(1, limiteURL +1)
FinDURL2[1] = u'.'
FinDURL2[2] = u','
FinDURL2[3] = u';'
FinDURL2[4] = u'!'
FinDURL2[5] = u'?'
FinDURL2[6] = u')' # mais pas ( ou ) simple

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
if debogage == False:
	ligneB = ligneB + 1
	Balise[ligneB-1][1] = u'<!--'
	Balise[ligneB-1][2] = u'-->'

limiteE = 20
Erreur = []
Erreur.append("Error 404 (Not Found)")
Erreur.append("404 error")
Erreur.append("404 Not Found")
Erreur.append("404 – File not found")
Erreur.append("Error 404 - Not found")
Erreur.append("Error 503 (Server Error)")
Erreur.append("Page not found")	# bug avec http://www.ifpi.org/content/section_news/plat2000.html et http://www.edinburgh.gov.uk/trams/include/uploads/story_so_far/Tram_Factsheets_2.pdf
Erreur.append("The page you requested cannot be found")
Erreur.append("this page can't be found")
Erreur.append("The service you requested is not available at this time")
Erreur.append("Sorry, no matching records for query")
Erreur.append("Runtime Error")
Erreur.append("server timedout")
Erreur.append("404. That’s an error.")
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
def hyperlynx(PageTemp):
	if debogage:
		print u'------------------------------------'
		#print time.strftime('%d-%m-%Y %H:%m:%S')
	summary = u'Vérification des URL'
	PageEnd = u''
	url = u''
	PageTemp = PageTemp.replace(u'[//https://', u'[https://')
	PageTemp = PageTemp.replace(u'[//http://', u'[http://')
	
	# Paramètre langue si traduction
	for m in range(0,10):
		# Formatage des anciens modèles
		PageTemp = re.sub((u'[' + ModeleEN[m][:1] + ur'|' + ModeleEN[m][:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])]).replace(u' ', u'_') + ur'\|', ModeleEN[m], PageTemp)
		PageTemp = re.sub((u'[' + ModeleEN[m][:1] + ur'|' + ModeleEN[m][:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])]).replace(u' ', u'  ') + ur'\|', ModeleEN[m], PageTemp)
		# Pour chaque modèle de la page
		while re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]+', PageTemp):
			PageEnd = PageEnd + PageTemp[:re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]', PageTemp).end()-1]
			PageTemp = PageTemp[re.search(u'{{[\n ]*' + ModeleEN[m] + u' *[\||\n]', PageTemp).end()-1:]	
			
			# Identification du code langue existant
			codelangue = u''
			if PageEnd.rfind(u'{{') != -1:
				PageDebut = PageEnd[:PageEnd.rfind(u'{{')]
				if PageDebut.rfind(u'{{') != -1 and PageDebut.rfind(u'}}') != -1 and (PageDebut[len(PageDebut)-2:] == u'}}' or PageDebut[len(PageDebut)-3:] == u'}} '):
					codelangue = PageDebut[PageDebut.rfind(u'{{')+2:PageDebut.rfind(u'}}')]
					'''Abandon de la recherche de validité car tous les code ne sont pas encore sur les sites francophones
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
					raw_input(PageCode.encode(config.console_encoding, 'replace'))
					if PageCode.find(u'Indication de langue') == -1:
						codelangue = u'en'
					else:	'''
					if len(codelangue) == 2:	# or len(codelangue) == 3: if codelangue == u'pdf': |format=codelangue, absent de {{lien web}}
						# Retrait du modèle de langue devenu inutile
						PageEnd = PageEnd[:PageEnd.rfind(u'{{' + codelangue + u'}}')] + PageEnd[PageEnd.rfind(u'{{' + codelangue + u'}}')+len(u'{{' + codelangue + u'}}'):]
					else:
						codelangue = u''
			if codelangue != u'':
				# Ajout du code langue dans le modèle
				if debogage: print(u'Modèle préalable : ' + codelangue.encode(config.console_encoding, 'replace'))
				if not re.search(u'[^}]*langu[ag]*e *=[^}]*}}', PageTemp):
					PageTemp = u'|langue=' + codelangue + PageTemp
				elif re.search(u'[^}]*langu[ag]*e *=[^}]*}}', PageTemp).end() > PageTemp.find(u'}}')+2:
					PageTemp = u'|langue=' + codelangue + PageTemp
				
		PageTemp = PageEnd + PageTemp
		PageEnd = u''
			
	for m in range(0,limiteM):
		if debogageLent: print(u'Traduction des noms du modèle ' + ModeleEN[m])
		PageTemp = PageTemp.replace(u'{{' + ModeleEN[m] + u' ', u'{{' + ModeleEN[m] + u'')
		#if ModeleEN[m] == 'cite web': raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		PageTemp = re.sub(ur'({{[\n ]*)[' + ModeleEN[m][0:1] + ur'|' + ModeleEN[m][0:1].upper() + ur']' + ModeleEN[m][1:len(ModeleEN[m])] + ur'( *[\||\n\t|}])', ur'\1' +  ModeleFR[m] + ur'\2', PageTemp)
		# Suppression des modèles vides
		regex = u'{{ *[' + ModeleFR[m][0:1] + ur'|' + ModeleFR[m][0:1].upper() + ur']' + ModeleFR[m][1:len(ModeleFR[m])] + ur' *}}'
		while re.search(regex, PageTemp):
			PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + PageTemp[re.search(regex, PageTemp).end():]
		# Traduction des paramètres de chaque modèle de la page
		regex = u'{{ *[' + ModeleFR[m][0:1] + ur'|' + ModeleFR[m][0:1].upper() + ur']' + ModeleFR[m][1:len(ModeleFR[m])] + ur' *[\||\n]'
		while re.search(regex, PageTemp):
			PageEnd = PageEnd + PageTemp[:re.search(regex, PageTemp).start()+2]
			PageTemp = PageTemp[re.search(regex, PageTemp).start()+2:]
			FinPageURL = PageTemp
			FinModele = 0
			# Gestion des modèles inclus dans le modèle de lien
			while FinPageURL.find(u'{{') != -1 and FinPageURL.find(u'{{') < FinPageURL.find(u'}}'):
				FinModele = FinModele + FinPageURL.find(u'}}')+2
				FinPageURL = FinPageURL[FinPageURL.find(u'}}')+2:]
			FinModele = FinModele + FinPageURL.find(u'}}')+2
			
			ModeleCourant = PageTemp[:FinModele]
			if debogageLent: raw_input(ModeleCourant.encode(config.console_encoding, 'replace'))
			for p in range(1,limiteP):
				# Faux-amis
				if ParamEN[p] == u'work':
					if ModeleCourant.find(u'rticle') != -1 and ModeleCourant.find(u'rticle') < ModeleCourant.find(u'|'):
						ParamFR[p] = u'périodique'
					elif ModeleCourant.find(u'ien web') != -1 and ModeleCourant.find(u'ien web') < ModeleCourant.find(u'|'):
						ParamFR[p] = u'série'
				elif ParamEN[p] == u'publisher':
					if ModeleCourant.find(u'ewspaper') != -1 or ModeleCourant.find(u'ériodique') != -1 or ModeleCourant.find(u'revue') != -1 or ModeleCourant.find(u'journal') != -1:
						ParamFR[p] = u'éditeur'
					else:
						ParamFR[p] = u'périodique'
				ModeleCourant = re.sub(ur'(\| *)' + ParamEN[p] + ur'( *=)', ur'\1' + ParamFR[p] + ur'\2', ModeleCourant)			
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
		if debogageLent:
			print u'Mois ' + str(m)
			print TradM[m][1]
		for p in range(1, limiteParamDate):
			if debogageLent: print u'Recherche de ' + ParamDate[p] + u' *=[ ,0-9]*' + TradM[m][1]
			if p > 4:
				PageTemp = re.sub(ur'({{ *' + ParamDate[p] + ur'[^}]+)' + TradM[m][1] + ur'([^}]+}})', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
				PageTemp = re.sub(ur'({{ *' + ParamDate[p] + ur'[^}]+)(\|[ 0-9][ 0-9][ 0-9][ 0-9])\|' + TradM[m][2] + ur'(\|[ 0-9][ 0-9])}}', ur'\1\3|' +  TradM[m][2] + ur'\2}}', PageTemp)
			else:
				PageTemp = re.sub(ur'(\| *' + ParamDate[p] + ur' *=[ ,0-9]*)' + TradM[m][1] + ur'([ ,0-9]*\.? *[<|\||\n\t|}])', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
				PageTemp = re.sub(ur'(\| *' + ParamDate[p] + ur' *=[ ,0-9]*)' + TradM[m][1][:1].lower() + TradM[m][1][1:] + ur'([ ,0-9]*\.? *[<|\||\n\t|}])', ur'\1' +  TradM[m][2] + ur'\2', PageTemp)
				
				# Ordre des dates : jj mois aaaa'
				if debogageLent: print u'Recherche de ' + ParamDate[p] + u' *= *' + TradM[m][2] + u' *([0-9]+), '
				PageTemp = re.sub(ur'(\| *' + ParamDate[p] + u' *= *)' + TradM[m][2] + ur' *([0-9]+), *([0-9]+)\.? *([<|\||\n\t|}])', ur'\1' + ur'\2' + ur' ' + TradM[m][2] + ur' ' + ur'\3' + ur'\4', PageTemp)	# trim(u'\3') ne fonctionne pas
				
	if debogage: print u'Traduction des langues'
	for l in range(1, ligneL+1):
		if debogageLent:
			print u'Langue ' + str(l)
			print TradL[l][1]
		PageTemp = re.sub(ur'(\| *langue *= *)' + TradL[l][1] + ur'( *[<|\||\n\t|}])', ur'\1' +  TradL[l][2] + ur'\2', PageTemp)
	
	if debogageLent:
		print u'Fin des traductions :'
		raw_input(PageTemp.encode(config.console_encoding, 'replace'))	

	# Recherche de chaque hyperlien en clair ------------------------------------------------------------------------------------------------------------------------------------
	while PageTemp.find(u'//') != -1:
		if debogage: print u'-----------------------------------------------------------------'
		url = u''
		DebutURL = u''
		CharFinURL = u''
		titre = u''
		FinModele = 0
		LienBrise = False
		# Avant l'URL
		PageDebut = PageTemp[0:PageTemp.find(u'//')]
		# Balises interdisant la modification de l'URL
		saut = False
		for b in range(1,ligneB):
			if PageDebut.rfind(Balise[b][1]) != -1 and PageDebut.rfind(Balise[b][1]) > PageDebut.rfind(Balise[b][2]):
				saut = True
				if debogage: print u'URL dans ' + Balise[b][1]
				break
			if PageEnd.rfind(Balise[b][1]) != -1 and PageEnd.rfind(Balise[b][1]) > PageEnd.rfind(Balise[b][2]):
				saut = True
				if debogage: print u'URL dans ' + Balise[b][1]
				break
		if saut == False:
			# titre=
			if PageDebut.rfind(u'titre=') != -1 and PageDebut.rfind(u'titre=') > PageDebut.rfind(u'{{') and PageDebut.rfind(u'titre=') > PageDebut.rfind(u'}}'):
				PageTemp3 = PageDebut[PageDebut.rfind(u'titre=')+len(u'titre='):len(PageDebut)]
				if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.rfind(u'}}') == -1):
					titre = PageTemp3[0:PageTemp3.find(u'|')]
				else:
					titre = PageTemp3[0:len(PageTemp3)]
				if debogage: print u'Titre avant URL'
			elif PageDebut.rfind(u'titre =') != -1 and PageDebut.rfind(u'titre =') > PageDebut.rfind(u'{{') and PageDebut.rfind(u'titre =') > PageDebut.rfind(u'}}'):
				PageTemp3 = PageDebut[PageDebut.rfind(u'titre =')+len(u'titre ='):len(PageDebut)]
				if PageTemp3.find(u'|') != -1 and (PageTemp3.find(u'|') < PageTemp3.find(u'}}') or PageTemp3.rfind(u'}}') == -1):
					titre = PageTemp3[0:PageTemp3.find(u'|')]
				else:
					titre = PageTemp3[0:len(PageTemp3)]
				if debogage: print u'Titre avant URL'
		
			# url=
			if PageDebut[len(PageDebut)-1:len(PageDebut)] == u'[':
				if debogage: print u'URL entre crochets sans protocole'
				DebutURL = 1
			elif PageDebut[len(PageDebut)-5:len(PageDebut)] == u'http:':
				if debogage: print u'URL http'
				DebutURL = 5
			elif PageDebut[len(PageDebut)-6:len(PageDebut)] == u'https:':
				if debogage: print u'URL https'
				DebutURL = 6
			else:
				if debogage: print u'URL sans http ni crochet'
				DebutURL = 0
			if DebutURL != 0:
				# Après l'URL
				FinPageURL = PageTemp[PageTemp.find(u'//'):len(PageTemp)]
				# url=	
				CharFinURL = u' '
				for l in range(1,limiteURL):
					if FinPageURL.find(CharFinURL) == -1 or (FinPageURL.find(FinDURL[l]) != -1 and FinPageURL.find(FinDURL[l]) < FinPageURL.find(CharFinURL)):
						CharFinURL = FinDURL[l]
				if debogage: print u'*Caractère de fin URL : ' + CharFinURL
				
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
							if debogage: print u'Réduction de l\'URL de ' + FinDURL2[u]
					
					Media = False
					for f in range(1,limiteF):
						if url[len(url)-len(Format[f])-1:].lower() == u'.' + Format[f].lower():
							if debogage:
								print url.encode(config.console_encoding, 'replace')
								print u'Média détecté (memory error potentielle)'
							Media = True
					if Media == False:
						if debogage: print(u'Recherche de la page distante')
						htmlSource = TestURL(url)
						if debogage: print(u'Recherche dans son contenu')
						LienBrise = TestPage(htmlSource,url)
				
				# Site réputé HS, mais invisible car ses sous-pages ont toutes été déplacées, et renvoient vers l'accueil
				for u in range(1,limiteU):
					if url.find(URLDeplace[u]) != -1 and len(url) > len(URLDeplace[u]) + 8:	#http://.../
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
						
				if debogage:
					# Compte-rendu des URL détectées
					try:
						print u'*URL : ' + url.encode(config.console_encoding, 'replace')
						print u'*Titre : ' + titre.encode(config.console_encoding, 'replace')
						print u'*HS : ' + str(LienBrise)
						print type(htmlSource)
					except UnicodeDecodeError:
						print u'*HS : ' + str(LienBrise)
						print "UnicodeDecodeError l 466"
				if debogageLent: raw_input (htmlSource[:7000])
				
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
					#raw_input(DebutPage[-100:].encode(config.console_encoding, 'replace'))
					
				
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
						if debogage: print u'Détection de ' + AncienModele
					elif re.search('{{ *[L|l]ire en ligne *[\||\n]', DebutPage):
						AncienModele = u'lire en ligne'
						if debogage: print u'Détection de ' + AncienModele
					elif retablirNonBrise == True and re.search(u'{{ *[L|l]ien brisé *[\||\n]', DebutPage):
						AncienModele = u'lien brisé'
						if debogage: print u'Détection de ' + AncienModele
						
					#if DebutPage[0:2] == u'{{': AncienModele = trim(DebutPage[2:DebutPage.find(u'|')])
					
					FinModele = PageTemp.find(u'//')+2
					FinPageModele = PageTemp[FinModele:len(PageTemp)]
					# Calcul des modèles inclus dans le modèle de lien
					while FinPageModele.find(u'}}') != -1 and FinPageModele.find(u'}}') > FinPageModele.find(u'{{') and FinPageModele.find(u'{{') != -1:
						FinModele = FinModele + FinPageModele.find(u'}}')+2
						FinPageModele = FinPageModele[FinPageModele.find(u'}}')+2:len(FinPageModele)]
					FinModele = FinModele + FinPageModele.find(u'}}')+2
					ModeleCourant = PageTemp[DebutModele:FinModele]
					if debogage: print "*Modele : " + ModeleCourant[:100].encode(config.console_encoding, 'replace')
					
					if AncienModele != u'':
						if debogage: print u'Ancien modèle à traiter : ' + AncienModele
						if LienBrise == True:
							try:
								PageTemp = PageTemp[0:DebutModele] + u'{{lien brisé' + PageTemp[re.search(u'{{ *[' + AncienModele[0:1] + u'|' + AncienModele[0:1].upper() + u']' + AncienModele[1:] + u' *[\||\n]', PageTemp).end()-1:]
							except AttributeError:
								raise "Regex introuvable ligne 811"
								
						elif AncienModele == u'lien brisé':
							if debogage: print u'Rétablissement d\'un ancien lien brisé'
							PageTemp = PageTemp[:PageTemp.find(AncienModele)] + u'lien web' + PageTemp[PageTemp.find(AncienModele)+len(AncienModele):]
						'''
						# titre=
						if re.search(u'\| *titre *=', FinPageURL):
							if debogage: print u'Titre après URL'
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
						if debogageLent: raw_input(FinPageURL.encode(config.console_encoding, 'replace'))	
						
						# En cas de modèles inclus le titre a pu ne pas être détecté précédemment
						if titre == u'' and re.search(u'\| *titre *=', ModeleCourant):
							PageTemp3 = ModeleCourant[re.search(u'\| *titre *=', ModeleCourant).end():]
							# Modèles inclus dans les titres
							while PageTemp3.find(u'{{') != -1 and PageTemp3.find(u'{{') < PageTemp3.find(u'}}') and PageTemp3.find(u'{{') < PageTemp3.find(u'|'):
								titre = titre + PageTemp3[:PageTemp3.find(u'}}')+2]
								PageTemp3 = PageTemp3[PageTemp3.find(u'}}')+2:]
							titre = titre + PageTemp3[:re.search(u'[^\|}\n]*', PageTemp3).end()]
							if debogage:
								print u'*Titre2 : '
								print titre.encode(config.console_encoding, 'replace')
							
						if LienBrise == True and AncienModele != u'lien brisé' and AncienModele != u'Lien brisé':
							summary = summary + u', remplacement de ' + AncienModele + u' par {{lien brisé}}'
							if debogage: print u', remplacement de ' + AncienModele + u' par {{lien brisé}}'
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
							if debogage: print u'Ajout de lien brisé entre crochets 1'
							# Lien entre crochets
							PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
						else:
							if debogage: print u'Ajout de lien brisé 1'
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
						if debogage: print url.encode(config.console_encoding, 'replace') + " dans modèle non géré"
					
				else:
					if debogage: print u'URL hors modèle'
					if LienBrise == True:
						summary = summary + u', ajout de {{lien brisé}}'
						if DebutURL == 1:
							if debogage: print u'Ajout de lien brisé entre crochets sans protocole'
							if titre != u'':
								PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
							else:
								PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
						else:
							if debogage: print u'Ajout de lien brisé 2'
							if PageTemp[DebutURL-1:DebutURL] == u'[' and PageTemp[DebutURL-2:DebutURL] != u'[[':
								if debogage: print u'entre crochet'
								DebutURL = DebutURL -1
								if titre == u'' :
									if debogage: "Titre vide"
									# Prise en compte des crochets inclus dans un titre
									PageTemp2 = PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):]
									#if debogage: raw_input(PageTemp2.encode(config.console_encoding, 'replace'))
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
									if debogage: "Ajout avec titre"
									PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + titre + u'}}' + PageTemp[len(PageTemp)-len(PageTemp2)+1:len(PageTemp)]
								else:
									if debogage: "Ajout sans titre"
									PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
							else:	
								if titre != u'': 
									# Présence d'un titre
									if debogage: print u'URL nue avec titre'
									PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'|titre=' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL)+1:PageTemp.find(u'//')+FinPageURL.find(u']')]  + u'}}' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(u']')+1:len(PageTemp)]
								else:
									if debogage: print u'URL nue sans titre'
									PageTemp = PageTemp[0:DebutURL] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + url + u'}} ' + PageTemp[PageTemp.find(u'//')+FinPageURL.find(CharFinURL):len(PageTemp)]
						
					else:
						if debogage: print u'Aucun changement sur l\'URL http'
			else:
				if debogage: print u'Aucun changement sur l\'URL non http'	
		else:
			if debogageLent: print u'URL entre balises sautée'
		
		# Lien suivant, en sautant les URL incluses dans l'actuelle, et celles avec d'autres protocoles que http(s)
		if FinModele == 0 and LienBrise == False:
			FinPageURL = PageTemp[PageTemp.find(u'//')+2:len(PageTemp)]
			CharFinURL = u' '
			for l in range(1,limiteURL):
				if FinPageURL.find(FinDURL[l]) != -1 and FinPageURL.find(FinDURL[l]) < FinPageURL.find(CharFinURL):
					CharFinURL = FinDURL[l]
			if debogage: print u'Saut après ' + CharFinURL
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'//')+2+FinPageURL.find(CharFinURL)]
			PageTemp = PageTemp[PageTemp.find(u'//')+2+FinPageURL.find(CharFinURL):len(PageTemp)]
		else:
			# Saut du reste du modèle courant (contenant parfois d'autres URL à laisser)
			if debogage: print u'Saut après }}'
			PageEnd = PageEnd + PageTemp[0:FinModele]
			PageTemp = PageTemp[FinModele:]
		#raw_input(PageEnd.encode(config.console_encoding, 'replace'))
		
	PageTemp = PageEnd + PageTemp
	PageEnd	= u''	
	if debogage: print ("Fin des tests URL")
	
	# Recherche de chaque hyperlien de modèles ------------------------------------------------------------------------------------------------------------------------------------
	if PageTemp.find(u'{{langue') != -1: # du Wiktionnaire
		if debogage: print ("Modèles Wiktionnaire")
		for m in range(1,ligne):
			PagEnd = u''
			while PageTemp.find(u'{{' + TabModeles[m][1] + u'|') != -1:
				PageEnd =  PageEnd + PageTemp[0:PageTemp.find(u'{{' + TabModeles[m][1] + u'|')+len(u'{{' + TabModeles[m][1] + u'|')]
				PageTemp =  PageTemp[PageTemp.find(u'{{' + TabModeles[m][1] + u'|')+len(u'{{' + TabModeles[m][1] + u'|'):len(PageTemp)]
				if PageTemp[0:PageTemp.find(u'}}')].find(u'|') != -1:
					Param1Encode = PageTemp[0:PageTemp.find(u'|')].replace(u' ',u'_')
				else:
					Param1Encode = PageTemp[0:PageTemp.find(u'}}')].replace(u' ',u'_')
				htmlSource = TestURL(TabModeles[m][2] + Param1Encode)
				LienBrise = TestPage(htmlSource,url)
				if LienBrise == True: PageEnd = PageEnd[0:PageEnd.rfind(u'{{' + TabModeles[m][1] + u'|')] + u'{{lien brisé|consulté le=' + time.strftime('%Y-%m-%d') + u'|url=' + TabModeles[m][2]
			PageTemp = PageEnd + PageTemp
			PageEnd = u''
		PageTemp = PageEnd + PageTemp
		PageEnd = u''
	if debogage: print ("Fin des tests modèle")
	
	# Paramètre inutile ?
	'''while PageTemp.find(u'|deadurl=no|') != -1:
		PageTemp = PageTemp[0:PageTemp.find(u'|deadurl=no|')+1] + PageTemp[PageTemp.find(u'|deadurl=no|')+len(u'|deadurl=no|'):len(PageTemp)]'''
	# Si dans {{ouvrage}} "lire en ligne" est vide, cela bloque le paramètre "url"
	PageTemp = re.sub(ur'{{(o|O)uvrage(\||\n[^}]*)\| *lire en ligne *= *([\||}|\n]+)', ur'{{\1uvrage\2\3', PageTemp)
	# Idem dans {{article}} : "éditeur" vide bloque "périodique", "journal" ou "revue"
	PageTemp = re.sub(ur'{{(a|A)rticle(\||\n[^}]*)\| *éditeur *= *([\||}|\n]+)', ur'{{\1rticle\2\3', PageTemp)
	
	PageEnd = PageEnd + PageTemp		
	#if PageEnd != PageBegin: sauvegarde(page,PageEnd, summary)
	return PageEnd

def TestURL(url):
	# Renvoie la page web d'une URL dès qu'il arrive à la lire.
	#debogage = False
	if debogage: print u'--------'
	# Whitelistage
	if url.find(u'history.navy.mil') != -1: return "ok"	# IP Free bloquée en lecture
	htmlSource = ""
	Method = u'Request'
	try:
		req = urllib2.Request(url)
		res = urllib2.urlopen(req)
		htmlSource = res.read()
		if debogage: print str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		Method = u'opener'
		try:
			opener = urllib2.build_opener()
			response = opener.open(url)
			htmlSource = response.read()
			if debogage: print str(len(htmlSource))
			if htmlSource != "": return htmlSource
		except UnicodeEncodeError:
			if debogage: print Method + u' : UnicodeEncodeError'
		except UnicodeDecodeError:
			if debogage: print Method + u' : UnicodeDecodeError'
		except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
		except httplib.BadStatusLine:
			if debogage: print Method + u' : BadStatusLine'
		except httplib.InvalidURL:
			if debogage: print Method + u' : InvalidURL'
		except urllib2.HTTPError, e:
			if debogage: print Method + u' : HTTPError %s.' % e.code
		except IOError as e:
			if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
		except urllib2.URLError:
			if debogage: print Method + u' : URLError'
		# pb avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304 qui renvoie 301 car son suffixe est facultatif
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except MemoryError:
		if debogage: print Method + u' : MemoryError'
		
	Method = u"urllib2.urlopen(url.encode('utf8'))"
	try:
		htmlSource = urllib2.urlopen(url.encode('utf8')).read()
		if debogage: print str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		Method = u'HTTPCookieProcessor'
		try:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			urllib2.install_opener(opener)
			response = opener.open(url)
			htmlSource = response.read()
			if debogage: print str(len(htmlSource))
			if htmlSource != "": return htmlSource
		except UnicodeEncodeError:
			if debogage: print Method + u' : UnicodeEncodeError'
		except UnicodeDecodeError:
			if debogage: print Method + u' : UnicodeDecodeError'
		except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
		except httplib.BadStatusLine:
			if debogage: print Method + u' : BadStatusLine'
		except httplib.InvalidURL:
			if debogage: print Method + u' : InvalidURL'
		except urllib2.HTTPError, e:
			if debogage: print Method + u' : HTTPError %s.' % e.code
		except IOError as e:
			if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
		except urllib2.URLError:
			if debogage: print Method + u' : URLError'
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'	
		
	Method = u'Request text/html'	
	try:
		req = urllib2.Request(url)
		req.add_header('Accept','text/html')
		res = urllib2.urlopen(req)
		htmlSource = res.read()
		if debogage: print Method + u' : text/html ' + str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		Method = u'geturl()'
		try:
			resp = urllib2.urlopen(url)
			req = urllib2.Request(resp.geturl())
			res = urllib2.urlopen(req)
			htmlSource = res.read()
			if debogage: print str(len(htmlSource))
			if htmlSource != "": return htmlSource
		except UnicodeEncodeError:
			if debogage: print Method + u' : UnicodeEncodeError'
		except UnicodeDecodeError:
			if debogage: print Method + u' : UnicodeDecodeError'
		except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
		except httplib.BadStatusLine:
			if debogage: print Method + u' : BadStatusLine'
		except httplib.InvalidURL:
			if debogage: print Method + u' : InvalidURL'
		except urllib2.HTTPError, e:
			if debogage: print Method + u' : HTTPError %s.' % e.code
		except IOError as e:
			if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
		except urllib2.URLError:
			if debogage: print Method + u' : URLError'
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'

	Method = u'Request Mozilla/5.0'
	agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
	try:
		headers = { 'User-Agent' : agent }
		req = urllib2.Request(url, "", headers)
		req.add_header('Accept','text/html')
		res = urllib2.urlopen(req)
		htmlSource = res.read()
		if debogage: print Method + u' : ' + agent + u' : ' + str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		if e.code == "404": return "404 error"
		if socket.gethostname() == u'PavilionDV6':
			Method = u'follow_all_redirects'	# fonctionne avec http://losangeles.broadwayworld.com/article/El_Capitan_Theatre_Presents_Disneys_Mars_Needs_Moms_311421_20110304
			try:
				r = requests.get(url)
				req = urllib2.Request(r.url)
				res = urllib2.urlopen(req)
				htmlSource = res.read()
				if debogage: print str(len(htmlSource))
				if htmlSource != "": return htmlSource
			except UnicodeEncodeError:
				if debogage: print Method + u' : UnicodeEncodeError'
			except UnicodeDecodeError:
				if debogage: print Method + u' : UnicodeDecodeError'
			except UnicodeError:
				if debogage: print Method + u' : UnicodeError'
				Method = u"Méthode url.encode('utf8')"
				try:
					sock = urllib.urlopen(url.encode('utf8'))
					htmlSource = sock.read()
					sock.close()
					if debogage: print str(len(htmlSource))
					if htmlSource != "": return htmlSource
				except UnicodeError:
					if debogage: print Method + u' : UnicodeError'
				except UnicodeEncodeError:
					if debogage: print Method + u' : UnicodeEncodeError'
				except UnicodeDecodeError:
					if debogage: print Method + u' : UnicodeDecodeError'
				except httplib.BadStatusLine:
					if debogage: print Method + u' : BadStatusLine'
				except httplib.InvalidURL:
					if debogage: print Method + u' : InvalidURL'
				except urllib2.HTTPError, e:
					if debogage: print Method + u' : HTTPError %s.' % e.code
				except IOError as e:
					if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
				except urllib2.URLError:
					if debogage: print Method + u' : URLError'
			except httplib.BadStatusLine:
				if debogage: print Method + u' : BadStatusLine'
			except httplib.InvalidURL:
				if debogage: print Method + u' : InvalidURL'
			except urllib2.HTTPError, e:
				if debogage: print Method + u' : HTTPError %s.' % e.code
			except urllib2.URLError:
				if debogage: print Method + u' : URLError'	
			except requests.exceptions.TooManyRedirects:
				if debogage: print Method + u' : TooManyRedirects'
				return u'ok'
			except requests.exceptions.SSLError:
				if debogage: print Method + u' : SSLError'
				return u'ok'
			except IOError as e:
				if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
			except requests.exceptions.ConnectionError:
				if debogage: print Method + u' ConnectionError'
			except requests.exceptions.InvalidSchema:
				if debogage: print Method + u' InvalidSchema'
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'

	Method = u'Request &_r=4&'
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
		if debogage: print str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		Method = u'HTTPRedirectHandler'
		try:
			opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
			request = opener.open(url)
			req = urllib2.Request(request.url)
			res = urllib2.urlopen(req)
			htmlSource = res.read()
			if debogage: print str(len(htmlSource))
			if htmlSource != "": return htmlSource
		except UnicodeEncodeError:
			if debogage: print Method + u' : UnicodeEncodeError'
		except UnicodeDecodeError:
			if debogage: print Method + u' : UnicodeDecodeError'
		except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
		except httplib.BadStatusLine:
			if debogage: print Method + u' : BadStatusLine'
		except httplib.InvalidURL:
			if debogage: print Method + u' : InvalidURL'
		except urllib2.HTTPError, e:
			if debogage: print Method + u' : HTTPError %s.' % e.code
		except IOError as e:
			if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
		except urllib2.URLError:
			if debogage: print Method + u' : URLError'			
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'

	Method = u'urlopen'	# fonctionne avec http://voxofilm.free.fr/vox_0/500_jours_ensemble.htm, et http://www.kurosawa-drawings.com/page/27
	try:
		res = urllib2.urlopen(url)
		htmlSource = res.read()
		if debogage: print str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
		if e.code == 401: return "ok"	# http://www.nature.com/nature/journal/v442/n7104/full/nature04945.html
	except IOError as e:
		if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
	except urllib2.URLError:
		if debogage: print Method + u' : URLError'		

	Method = u'urllib.urlopen'
	try:
		sock = urllib.urlopen(url)
		htmlSource = sock.read()
		sock.close()
		if debogage: print str(len(htmlSource))
		if htmlSource != "": return htmlSource
	except httplib.BadStatusLine:
		if debogage: print Method + u' : BadStatusLine'
	except httplib.InvalidURL:
		if debogage: print Method + u' : InvalidURL'
	except IOError as e:
		if debogage: print Method + u' : I/O error'
	except urllib2.URLError, e:
		if debogage: print Method + u' : URLError %s.' % e.code
	except urllib2.HTTPError, e:
		if debogage: print Method + u' : HTTPError %s.' % e.code
	except UnicodeEncodeError:
		if debogage: print Method + u' : UnicodeEncodeError'
	except UnicodeDecodeError:
		if debogage: print Method + u' : UnicodeDecodeError'
	except UnicodeError:
		if debogage: print Method + u' : UnicodeError'
		Method = u"Méthode url.encode('utf8')"
		try:
			sock = urllib.urlopen(url.encode('utf8'))
			htmlSource = sock.read()
			sock.close()
			if debogage: print str(len(htmlSource))
			if htmlSource != "": return htmlSource
		except UnicodeError:
			if debogage: print Method + u' : UnicodeError'
		except UnicodeEncodeError:
			if debogage: print Method + u' : UnicodeEncodeError'
		except UnicodeDecodeError:
			if debogage: print Method + u' : UnicodeDecodeError'
		except httplib.BadStatusLine:
			if debogage: print Method + u' : BadStatusLine'
		except httplib.InvalidURL:
			if debogage: print Method + u' : InvalidURL'
		except urllib2.HTTPError, e:
			if debogage: print Method + u' : HTTPError %s.' % e.code
		except IOError as e:
			if debogage: print Method + u' : I/O error({0}): {1}'.format(e.errno, e.strerror)
		except urllib2.URLError:
			if debogage: print Method + u' : URLError'
	if debogage: print Method + u' Fin du test d\'existance du site'
	return u''

def TestPage(htmlSource,url):
	LienBrise = False
	try:
		#if debogageLent == True and htmlSource != u'' and htmlSource is not None: raw_input (htmlSource[0:1000])
		if htmlSource is None:
			if debogage: print url.encode(config.console_encoding, 'replace') + " none type"
			LienBrise = True
		elif htmlSource == "" and (url.find(u'à') != -1 or url.find(u'é') != -1 or url.find(u'è') != -1 or url.find(u'ê') != -1 or url.find(u'ù') != -1): # bug http://fr.wikipedia.org/w/index.php?title=Acad%C3%A9mie_fran%C3%A7aise&diff=prev&oldid=92572792
			LienBrise = False
		elif htmlSource == "": #and url[len(url)-4:len(url)] != u'.pdf':
			if debogage: print url.encode(config.console_encoding, 'replace') + " page vide"
			LienBrise = True
		else:
			if debogage: print u' Page non vide'
			#print htmlSource.find(u'texte sur cette page')
			for e in range(0,limiteE):
				if debogageLent: print Erreur[e]
				if htmlSource.find(Erreur[e]) != -1 and not re.search("\n[^\n]*if[^\n]*" + Erreur[e], htmlSource):
					if debogageLent: print u'  Trouvé'
					# Exceptions
					if Erreur[e] == "404 Not Found" and url.find("audiofilemagazine.com") == -1:	# Exception avec popup formulaire en erreur
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					# Wikis : page vide à créer
					if Erreur[e] == "Soit vous avez mal &#233;crit le titre" and url.find("wiki") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					elif Erreur[e] == "Il n'y a pour l'instant aucun texte sur cette page." != -1 and htmlSource.find("wiki") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					elif Erreur[e] == "There is currently no text in this page." != -1 and htmlSource.find("wiki") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					# Sites particuliers
					elif Erreur[e] == "The page you requested cannot be found" and url.find("restaurantnewsresource.com") == -1:	# bug avec http://www.restaurantnewsresource.com/article35143 (Landry_s_Restaurants_Opens_T_REX_Cafe_at_Downtown_Disney.html)
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					elif Erreur[e] == "Terme introuvable" != -1 and htmlSource.find("Site de l'ATILF") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					elif Erreur[e] == "Cette forme est introuvable !" != -1 and htmlSource.find("Site de l'ATILF") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					elif Erreur[e] == "Sorry, no matching records for query" != -1 and htmlSource.find("ATILF - CNRS") != -1:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
					else:
						LienBrise = True
						if debogage: print url.encode(config.console_encoding, 'replace') + " : " + Erreur[e]
						break
	except UnicodeError:
		if debogage: print u'UnicodeError lors de la lecture'
		LienBrise = False
	except UnicodeEncodeError:
		if debogage: print u'UnicodeEncodeError lors de la lecture'
		LienBrise = False
	except UnicodeDecodeError:
		if debogage: print u'UnicodeDecodeError lors de la lecture'
		LienBrise = False
	except httplib.BadStatusLine:
		if debogage: print u'BadStatusLine lors de la lecture'
		LienBrise = False
	except httplib.InvalidURL:
		if debogage: print u'InvalidURL lors de la lecture'
		LienBrise = False
	except urllib2.HTTPError, e:
		if debogage: print u'HTTPError %s.' % e.code +  u' lors de la lecture'
		LienBrise = False
	except IOError as e:
		if debogage: print u'I/O error({0}): {1}'.format(e.errno, e.strerror) +  u' lors de la lecture'
		LienBrise = False
	except urllib2.URLError:
		if debogage: print u'URLError lors de la lecture'
		LienBrise = False

	if url.find(u'www.bbc.co.uk') != -1 or url.find(u'www.cia.gov') != -1 or url.find(u'itunes.apple.com') != -1 or url.find(u'twitter.com') != -1: # or url.find(u'nytimes.com') != -1: pb à 3h32 # http://www.bbc.co.uk/cult/buffy/indetail/earshot/reviews.shtml, https://www.cia.gov/library/publications/the-world-factbook/fields/2060.html
		print u'Site particulier'
		return False #top40.nl
	else:
		if debogageLent: print u'Fin du test du contenu'
		return LienBrise

def trim(s):
    return s.strip(" \t\n\r\0\x0B")
	
def log(source):		
	txtfile = codecs.open(u'_hyperlinx.log', 'a', 'utf-8')
	txtfile.write(u'\n' + source + u'\n')
	txtfile.close()

# à faire : sauter les longs PDF comme dans [[w:Apollo 11]]



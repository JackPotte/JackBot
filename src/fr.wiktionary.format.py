#!/usr/bin/env python
# coding: utf-8
'''
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le serveur Toolforge de Wikimedia :
1) Crée les redirection d'apostrophe dactylographique vers apostrophe typographique.
2) Gère des modèles {{voir}} en début de page.
3) Retire certains doublons de modèles et d'espaces.
4) Remplace les modèles catégorisés comme désuets.
5) Ajoute les prononciations sur la ligne de forme, et certains liens vers les conjugaisons.
6) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
7) Détecte les modèles de contexte à ajouter, et ajoute leurs codes langues  ou "nocat=1"
8) Complète la boite de flexions de verbes en français.
9) Demande les pluriels et genres manquants quand les lemmes les éludent.
10) Ajoute certaines sections traductions manquantes.
11) Ajoute les anagrammes (pour les petits mots faute de vitesse réseau).
etc.
Tests sur http://fr.wiktionary.org/w/index.php?title=Utilisateur%3AJackBot%2Ftest&diff=14533806&oldid=14533695
'''

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, os, re, socket, sys, time, urllib
from lib import *
import pywikibot
from pywikibot import *
from pywikibot import pagegenerators

#TODO map(unicode, sys.argv) # UnicodeDecodeError

# Global variables
debugLevel = 0
debugAliases = [str('-debug'), str('-d')]
for debugAlias in debugAliases:
    if debugAlias in sys.argv:
        debugLevel= 1
        sys.argv.remove(debugAlias)

waitAfterHumans = True
forceAliases = [str('-force'), str('-f')]
for forceAlias in forceAliases:
    if forceAlias in sys.argv:
        waitAfterHumans= False
        sys.argv.remove(forceAlias)       

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
fixOldTemplates = False
addDefaultSortKey = False
allNamespaces = False
treatTemplates = False
treatCategories = False
fixGenders = True
fixFalseFlexions = False
listHomophons = False
listFalseTranslations = False
testImport = False
cancelUser = {}
outputFile = ''
anagramsMaxLength = 4   # sinon trop long : 5 > 5 min, 8 > 1 h par page)

Modele = [] # Liste des modèles du site à traiter
Section = [] # Sections à remplacer
# Paragraphes autorisant les modèles catégorisants par langue ({{voir| et {{voir/ sont gérés individuellement)
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_type_de_mot_du_Wiktionnaire
Modele.append(u'-adj-dem-')
Section.append(u'adjectif démonstratif')
Modele.append(u'-adj-dém-')
Section.append(u'adjectif démonstratif')
Modele.append(u'-adj-excl-')
Section.append(u'adjectif exclamatif')
Modele.append(u'-adj-indef-')
Section.append(u'adjectif indéfini')
Modele.append(u'-adj-indéf-')
Section.append(u'adjectif indéfini')
Modele.append(u'-adj-int-')
Section.append(u'adjectif interrogatif')
Modele.append(u'-adj-num-')
Section.append(u'adjectif numéral')
Modele.append(u'-adj-pos-')
Section.append(u'adjectif possessif')
Modele.append(u'-adjectif-')
Section.append(u'adjectif')
Modele.append(u'-adj-')
Section.append(u'adjectif')
Modele.append(u'-adv-int-')
Section.append(u'adverbe interrogatif')
Modele.append(u'-adv-pron-')
Section.append(u'adverbe pronominal')
Modele.append(u'-adv-rel-')
Section.append(u'adverbe relatif')
Modele.append(u'-adverbe-')
Section.append(u'adverbe')
Modele.append(u'-adv-')
Section.append(u'adverbe')
Modele.append(u'-aff-')
Section.append(u'affixe')
Modele.append(u'-art-def-')
Section.append(u'article défini')
Modele.append(u'-art-déf-')
Section.append(u'article défini')
Modele.append(u'-art-indef-')
Section.append(u'article indéfini')
Modele.append(u'-art-indéf-')
Section.append(u'article indéfini')
Modele.append(u'-art-part-')
Section.append(u'article partitif')
Modele.append(u'-art-')
Section.append(u'article')
Modele.append(u'-aux-')
Section.append(u'verbe')
Modele.append(u'-circonf-')
Section.append(u'circonfixe')
Modele.append(u'-class-')
Section.append(u'classificateur')
Modele.append(u'-conj-coord-')
Section.append(u'conjonction de coordination')
Modele.append(u'-conj-')
Section.append(u'conjonction')
Modele.append(u'-copule-')
Section.append(u'copule')
Modele.append(u'-dét-')
Section.append(u'déterminant')
Modele.append(u'-erreur-')
Section.append(u'erreur')
Modele.append(u'-gismu-')
Section.append(u'gismu')
Modele.append(u'-inf-')
Section.append(u'infixe')
Modele.append(u'-interf-')
Section.append(u'interfixe')
Modele.append(u'-interj-')
Section.append(u'interjection')
Modele.append(u'-lettre-')
Section.append(u'lettre')
Modele.append(u'-nom-fam-')
Section.append(u'nom de famille')
Modele.append(u'-nom-pr-')
Section.append(u'nom propre')
Modele.append(u'-nom-propre-')
Section.append(u'nom propre')
Modele.append(u'-nom-sciences-')
Section.append(u'nom scientifique')
Modele.append(u'-nom-')
Section.append(u'nom')
Modele.append(u'-num-')
Section.append(u'numéral')
Modele.append(u'-numér-')
Section.append(u'numéral')
Modele.append(u'-numéral-')
Section.append(u'numéral')
Modele.append(u'-part-num-')
Section.append(u'particule numérale')
Modele.append(u'-part-')
Section.append(u'particule')
Modele.append(u'-patronyme-')
Section.append(u'patronyme')
Modele.append(u'-post-')
Section.append(u'postposition')
Modele.append(u'-préf-')
Section.append(u'préfixe')
Modele.append(u'-préfixe-')
Section.append(u'préfixe')
Modele.append(u'-prénom-')
Section.append(u'prénom')
Modele.append(u'-pré-nom-')
Section.append(u'pré-nom')
Modele.append(u'-prép-')
Section.append(u'préposition')
Modele.append(u'-pré-verbe-')
Section.append(u'pré-verbe')
Modele.append(u'-pronom-adj-')
Section.append(u'pronom-adjectif')
Modele.append(u'-pronom-dém-')
Section.append(u'pronom démonstratif')
Modele.append(u'-pronom-indéf-')
Section.append(u'pronom indéfini')
Modele.append(u'-pronom-int-')
Section.append(u'pronom interrogatif')
Modele.append(u'-pronom-pers-')
Section.append(u'pronom personnel')
Modele.append(u'-pronom-pos-')
Section.append(u'pronom possessif')
Modele.append(u'-pronom-rel-')
Section.append(u'pronom relatif')
Modele.append(u'-pronom-')
Section.append(u'pronom')
Modele.append(u'-quantif-')
Section.append(u'quantificateur')
Modele.append(u'-radical-')
Section.append(u'radical')
Modele.append(u'-rafsi-')
Section.append(u'rafsi')
Modele.append(u'-sinogramme-')
Section.append(u'sinogramme')
Modele.append(u'-subst-pron-pers-')
Section.append(u'adjectifs')
Modele.append(u'-suf-')
Section.append(u'suffixe')
Modele.append(u'-suffixe-')
Section.append(u'suffixe')
Modele.append(u'-symb-')
Section.append(u'symbole')
Modele.append(u'-symbole-')
Section.append(u'symbole')
Modele.append(u'-verbe-pr-')
Section.append(u'verbe pronominal')
Modele.append(u'-verb-pr-')
Section.append(u'verbe pronominal')
Modele.append(u'-verb-')
Section.append(u'verbe')
Modele.append(u'-verbe-')
Section.append(u'verbe')
Modele.append(u'-faux-prov-')
Section.append(u'faux proverbe')
Modele.append(u'-prov-')
Section.append(u'proverbe')
Modele.append(u'-loc-phr-')
Section.append(u'locution-phrase')
Modele.append(u'-loc-')
Section.append(u'locution')
Modele.append(u'-locution-')
Section.append(u'locution')
Modele.append(u'-var-typo-')
Section.append(u'variante typographique')
Modele.append(u'-onoma-')
Section.append(u'onomatopée')
Modele.append(u'-onomatopée-')
Section.append(u'onomatopée')
Modele.append(u'-interjection-')
Section.append(u'interjection')
limit1 = len(Modele)
# Paragraphes sans code langue catégorisant, de niveau 3
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_contexte
Modele.append(u'-réf-')
Section.append(u'références')
Modele.append(u'-ref-')
Section.append(u'références')
Modele.append(u'-références-')
Section.append(u'références')
Modele.append(u'-sino-dico-')
Section.append(u'dico sinogrammes')
Modele.append(u'-écrit-')
Section.append(u'écriture')
Modele.append(u'-voir-')
Section.append(u'voir aussi')
Modele.append(u'-anagrammes-')
Section.append(u'anagrammes')
Modele.append(u'-anagr-')
Section.append(u'anagrammes')
Modele.append(u'-étym-')
Section.append(u'étymologie')
Modele.append(u'-pron-')
Section.append(u'prononciation')
Modele.append(u'-décl-')
Section.append(u'déclinaison')
limit2 = len(Modele)
# De niveau 4
Modele.append(u'-compos-')
Section.append(u'composés')
Modele.append(u'-dial-')
Section.append(u'variantes dialectales')
Modele.append(u'-faux-amis-')
Section.append(u'faux-amis')
Modele.append(u'-image-')
Section.append(u'images vidéo')
Modele.append(u'-trad-')
Section.append(u'traductions')
Modele.append(u'-dimin-')
Section.append(u'diminutifs')
Modele.append(u'-drv-int-')
Section.append(u'dérivés autres langues')
Modele.append(u'-drv-')
Section.append(u'dérivés')
Modele.append(u'-exp-')
Section.append(u'expressions')
Modele.append(u'-gent-')
Section.append(u'gentilés')
Modele.append(u'-hist-')
Section.append(u'attestations')
Modele.append(u'-holo-')
Section.append(u'holonymes')
Modele.append(u'-hyper-')
Section.append(u'hyperonymes')
Modele.append(u'-hypo-')
Section.append(u'hyponymes')
Modele.append(u'-méro-')
Section.append(u'méronymes')
Modele.append(u'-noms-vern-')
Section.append(u'noms vernaculaires')
Modele.append(u'-ortho-arch-')
Section.append(u'anciennes orthographes')
Modele.append(u'-paro-')
Section.append(u'paronymes')
Modele.append(u'-phrases-')
Section.append(u'phrases')
Modele.append(u'-q-syn-')
Section.append(u'quasi-synonymes')
Modele.append(u'-syn-')
Section.append(u'synonymes')
Modele.append(u'-tran-')
Section.append(u'transcriptions')
Modele.append(u'-trans-')
Section.append(u'transcriptions')
Modele.append(u'-translit-')
Section.append(u'translittérations')
Modele.append(u'-tropo-')
Section.append(u'troponymes')
Modele.append(u'-var-ortho-')
Section.append(u'variantes orthographiques')
Modele.append(u'-var-ortho-')
Section.append(u'variantes ortho')
Modele.append(u'-var-')
Section.append(u'variantes')
Modele.append(u'-vidéo-')
Section.append(u'images vidéo')
Modele.append(u'-voc-')
Section.append(u'vocabulaire')
Modele.append(u'-voc-')
Section.append(u'vocabulaire apparenté')
Modele.append(u'-abréviation-')
Section.append(u'abréviations')
Modele.append(u'-ant-')
Section.append(u'antonymes')
Modele.append(u'-abrév-')
Section.append(u'abréviations')
Modele.append(u'-dial-')
Section.append(u'dial')
Modele.append(u'-apr-')
Section.append(u'apparentés')
Modele.append(u'-conjug-')
Section.append(u'conjugaison')
Modele.append(u'-cit-')
Section.append(u'citations')
Modele.append(u'vidéos')
Section.append(u'vidéos')
Modele.append(u'augmentatifs')
Section.append(u'augmentatifs')
Modele.append(u'diminutifs')
Section.append(u'diminutifs')
Modele.append(u'-notes-')
Section.append(u'notes')
Modele.append(u'-note-')
Section.append(u'notes')
# Avec code langue
Modele.append(u'-homo-')
Section.append(u'homophones')
limit3 = len(Modele)
Modele.append(u'trad-trier')
Section.append(u'traductions à trier')
limit4 = len(Modele)
Modele.append(u'caractère')
Modele.append(u'langue')
Modele.append(u'S')

# https://fr.wiktionary.org/wiki/Catégorie:Modèles_étymologiques
etymologyTemplates = [u'étcompcat', u'étyl', u'étylp', u'louchébem', u'reverlanisation', u'verlan']
etymologyTemplatesWithLanguageAtLang = [u'compos', u'composé de', u'deet', u'date'] #, u'siècle'
etymologyTemplatesInSatelliteWords = [u'abréviation', u'acronyme', u'apocope', u'aphérèse', u'ellipse', u'par ellipse', u'sigle']
etymologyTemplatesWithLanguageAtFirst = etymologyTemplatesInSatelliteWords + [u'agglutination', u'antonomase', \
    u'déglutination', u'mot-valise', u'parataxe', u'syncope', u'univerbation']
etymologyTemplatesWithLanguageAtSecond = [u'dénominal', u'dénominal de', u'déverbal', u'déverbal de', u'déverbal sans suffixe']

# Modèles qui ne sont pas des titres de paragraphes
Modele.append(u'?')
Modele.append(u'doute')
Modele.append(u'm')
Modele.append(u'f')
Modele.append(u'vérifier')
Modele.append(u'formater')
Modele.append(u'suppression')
Modele.append(u'supp')
Modele.append(u'SI')
Modele.append(u'supprimer ?')
Modele.append(u'PàS')
Modele.append(u'(')
Modele.append(u')')
Modele.append(u'trad-début')
Modele.append(u'trad-fin')
Modele.append(u'titre incorrect')
Modele.append(u'trad--')
Modele.append(u'trad-')
Modele.append(u'trad+')
Modele.append(u'trad')
Modele.append(u'préciser')
Modele.append(u'cf')
Modele = Modele + etymologyTemplatesWithLanguageAtLang

limit5 = len(Modele)
Modele.append(u'comparatif')
Modele.append(u'superlatif')
Modele.append(u'beaucoup plus courant')
Modele.append(u'plus courant')
Modele.append(u'beaucoup moins courant')
Modele.append(u'moins courant')
Modele.append(u'b-pl-cour')
Modele.append(u'pl-cour')
Modele.append(u'b-m-cour')
Modele.append(u'm-cour')
Modele.append(u'mf')
Modele.append(u'n')
Modele.append(u'c')
Modele.append(u'pl-rare')
Modele.append(u'plus rare')
Modele.append(u'pluriel')
limit6 = len(Modele)
Modele.append(u'pron')
Modele.append(u'écouter')
Modele.append(u'référence nécessaire')
Modele.append(u'réf?')
Modele.append(u'réf ?')
Modele.append(u'refnec')
Modele.append(u'réfnéc')
Modele.append(u'source?')
Modele.append(u'réfnéc')
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_domaine_d'utilisation
Modele.append(u'1ergroupe')
Modele.append(u'2egroupe')
Modele.append(u'3egroupe')
Modele.append(u'Antiquité')
Modele.append(u'BD')
Modele.append(u'BDD')
Modele.append(u'CB')
Modele.append(u'Internet')
Modele.append(u'Moyen Âge')
Modele.append(u'Scrabble')
Modele.append(u'ablat')
Modele.append(u'ablatif')
Modele.append(u'accord genre ?')
Modele.append(u'accus')
Modele.append(u'accusatif')
Modele.append(u'acoustique')
Modele.append(u'admin')
Modele.append(u'administration')
Modele.append(u'adverbes de lieu')
Modele.append(u'adverbes de temps')
Modele.append(u'adverbes interrogatif')
Modele.append(u'affectueux')
Modele.append(u'agri')
Modele.append(u'agriculture')
Modele.append(u'agronomie')
Modele.append(u'alcools')
Modele.append(u'algues‎')
Modele.append(u'algèbre linéaire')
Modele.append(u'algèbre‎')
Modele.append(u'aliments‎')
Modele.append(u'allatif')
Modele.append(u'alliages')
Modele.append(u'alpi')
Modele.append(u'alpinisme')
Modele.append(u'anal')
Modele.append(u'analogie')
Modele.append(u'analyse')
Modele.append(u'anat')
Modele.append(u'anatomie')
Modele.append(u'anciennes divisions')
Modele.append(u'anciennes localités')
Modele.append(u'angl')
Modele.append(u'anglicisme')
Modele.append(u'anglicismes informatiques')
Modele.append(u'animaux')
Modele.append(u'animé')
Modele.append(u'anthro')
Modele.append(u'anthropologie')
Modele.append(u'antilopes')
Modele.append(u'antiq')
Modele.append(u'antiquité')
Modele.append(u'apiculture')
Modele.append(u'araignées')
Modele.append(u'arboriculture')
Modele.append(u'arbres')
Modele.append(u'arch')
Modele.append(u'archaïque')
Modele.append(u'archaïsme')
Modele.append(u'archi')
Modele.append(u'architecture des ordinateurs')
Modele.append(u'architecture')
Modele.append(u'archéo')
Modele.append(u'archéologie')
Modele.append(u'argot militaire')
Modele.append(u'argot policier')
Modele.append(u'argot polytechnicien')
Modele.append(u'argot scolaire')
Modele.append(u'argot')
Modele.append(u'argots')
Modele.append(u'arithmétique')
Modele.append(u'arme')
Modele.append(u'armement')
Modele.append(u'armes blanches')
Modele.append(u'armes à feu')
Modele.append(u'armes')
Modele.append(u'arthropodes')
Modele.append(u'artillerie')
Modele.append(u'artistes')
Modele.append(u'arts martiaux')
Modele.append(u'arts')
Modele.append(u'assurance')
Modele.append(u'astrol')
Modele.append(u'astrologie')
Modele.append(u'astron')
Modele.append(u'astronautique')
Modele.append(u'astronomie')
Modele.append(u'astrophysique')
Modele.append(u'athlé')
Modele.append(u'athlétisme')
Modele.append(u'atomes')
Modele.append(u'audiovis')
Modele.append(u'audiovisuel')
Modele.append(u'automatique')
Modele.append(u'automo')
Modele.append(u'automobile')
Modele.append(u'auxiliaire')
Modele.append(u'au pluriel uniquement')
Modele.append(u'au singulier uniquement')
Modele.append(u'aviat')
Modele.append(u'aviation')
Modele.append(u'avions')
Modele.append(u'aéro')
Modele.append(u'aéronautique')
Modele.append(u'aïkido')
Modele.append(u'bactéries')
Modele.append(u'bactério')
Modele.append(u'bactériologie')
Modele.append(u'badminton')
Modele.append(u'bandes dessinées')
Modele.append(u'base-ball')
Modele.append(u'baseball')
Modele.append(u'bases de données')
Modele.append(u'basket')
Modele.append(u'bateaux')
Modele.append(u'beaux-arts')
Modele.append(u'bibliothéconomie')
Modele.append(u'bières')
Modele.append(u'bijou')
Modele.append(u'bijouterie')
Modele.append(u'billard')
Modele.append(u'biochimie')
Modele.append(u'biol')
Modele.append(u'biologie cellulaire')
Modele.append(u'biologie')
Modele.append(u'biophysique')
Modele.append(u'bivalves')
Modele.append(u'boissons')
Modele.append(u'botan')
Modele.append(u'botanique')
Modele.append(u'boucherie')
Modele.append(u'bouddhisme')
Modele.append(u'boulangerie')
Modele.append(u'bourrellerie')
Modele.append(u'bovins')
Modele.append(u'bowling')
Modele.append(u'boxe')
Modele.append(u'bridge')
Modele.append(u'broderie')
Modele.append(u'bâtiment')
Modele.append(u'cactus')
Modele.append(u'calendrier')
Modele.append(u'camélidés')
Modele.append(u'canoe')
Modele.append(u'canoë')
Modele.append(u'canoë-kayak')
Modele.append(u'capoeira')
Modele.append(u'capoeira')
Modele.append(u'caprins')
Modele.append(u'cardin')
Modele.append(u'cardinal')
Modele.append(u'carnivore')
Modele.append(u'cartes')
Modele.append(u'cartographie')
Modele.append(u'catch')
Modele.append(u'catholicisme')
Modele.append(u'caténatif')
Modele.append(u'cavalerie')
Modele.append(u'cervidés')
Modele.append(u'chameaux')
Modele.append(u'champignons')
Modele.append(u'charpente')
Modele.append(u'charpenterie')
Modele.append(u'chasse')
Modele.append(u'chats')
Modele.append(u'chaussures')
Modele.append(u'chauves-souris')
Modele.append(u'chaînes de montagnes')
Modele.append(u'chemin de fer')
Modele.append(u'chevaux')
Modele.append(u'chiens')
Modele.append(u'chim')
Modele.append(u'chimie inorganique')
Modele.append(u'chimie organique')
Modele.append(u'chimie physique')
Modele.append(u'chimie')
Modele.append(u'chir')
Modele.append(u'chiromancie')
Modele.append(u'chirurgie')
Modele.append(u'christianisme')
Modele.append(u'chronologie')
Modele.append(u'chênes')
Modele.append(u'cigognes')
Modele.append(u'ciné')
Modele.append(u'cinéma')
Modele.append(u'cirque')
Modele.append(u'cnidaires')
Modele.append(u'cocktails')
Modele.append(u'coiffure')
Modele.append(u'colorimétrie')
Modele.append(u'coléoptères')
Modele.append(u'combat')
Modele.append(u'comm')
Modele.append(u'commerce')
Modele.append(u'commerces')
Modele.append(u'comparatif de')
Modele.append(u'composants électriques')
Modele.append(u'composants électroniques')
Modele.append(u'composants')
Modele.append(u'compta')
Modele.append(u'comptabilité')
Modele.append(u'condiments')
Modele.append(u'confiserie')
Modele.append(u'confiseries')
Modele.append(u'conifères')
Modele.append(u'conjugaison')
Modele.append(u'constr')
Modele.append(u'construction')
Modele.append(u'contemporain')
Modele.append(u'copropriété')
Modele.append(u'coquillages')
Modele.append(u'cordonnerie')
Modele.append(u'cosm')
Modele.append(u'cosmétique')
Modele.append(u'cosmétologie')
Modele.append(u'couche application')
Modele.append(u'couche liaison')
Modele.append(u'couche physique')
Modele.append(u'couche présentation')
Modele.append(u'couche réseau')
Modele.append(u'couche session')
Modele.append(u'couche transport')
Modele.append(u'cour')
Modele.append(u'courant')
Modele.append(u'cours d’eau')
Modele.append(u'course à pied')
Modele.append(u'cout')
Modele.append(u'couture')
Modele.append(u'couverture')
Modele.append(u'couvre-chefs')
Modele.append(u'crabes')
Modele.append(u'crapauds')
Modele.append(u'cricket')
Modele.append(u'crimes')
Modele.append(u'criminels')
Modele.append(u'cristallographie')
Modele.append(u'critiqué')
Modele.append(u'crustacés')
Modele.append(u'cryptomonnaie')
Modele.append(u'cryptomonnaies')
Modele.append(u'créatures')
Modele.append(u'cuis')
Modele.append(u'cuisine')
Modele.append(u'culturisme')
Modele.append(u'cycl')
Modele.append(u'cyclisme')
Modele.append(u'cygnes')
Modele.append(u'cépages')
Modele.append(u'céphalopodes')
Modele.append(u'céramique')
Modele.append(u'céréales')
Modele.append(u'cétacés')
Modele.append(u'danse')
Modele.append(u'danses')
Modele.append(u'datif')
Modele.append(u'dentisterie')
Modele.append(u'dermat')
Modele.append(u'dermatologie')
Modele.append(u'desserts')
Modele.append(u'dessin')
Modele.append(u'dialectes')
Modele.append(u'didact')
Modele.append(u'didactique')
Modele.append(u'dim-lex')
Modele.append(u'diminutif')
Modele.append(u'dinosaures')
Modele.append(u'dinosaures')
Modele.append(u'diplomatie')
Modele.append(u'diplomatie')
Modele.append(u'diptote')
Modele.append(u'distinctions')
Modele.append(u'divinités')
Modele.append(u'documents')
Modele.append(u'drogue')
Modele.append(u'drogues')
Modele.append(u'droit de propriété')
Modele.append(u'droit du travail')
Modele.append(u'droit féodal')
Modele.append(u'droit')
Modele.append(u'dén')
Modele.append(u'dénombrable')
Modele.append(u'dépendant')
Modele.append(u'déris')
Modele.append(u'dérision')
Modele.append(u'dérision')
Modele.append(u'déserts')
Modele.append(u'désuet')
Modele.append(u'détroits')
Modele.append(u'embryologie')
Modele.append(u'enclitique')
Modele.append(u'enfantin')
Modele.append(u'entom')
Modele.append(u'entomol')
Modele.append(u'entomologie')
Modele.append(u'enzymes')
Modele.append(u'escalade')
Modele.append(u'escrime')
Modele.append(u'ethnobiologie')
Modele.append(u'ethnologie')
Modele.append(u'ethnonymes')
Modele.append(u'euphorbes')
Modele.append(u'euphémisme')
Modele.append(u'ex-rare')
Modele.append(u'exag')
Modele.append(u'exagératif')
Modele.append(u'exagération')
Modele.append(u'expression')
Modele.append(u'extrêmement rare')
Modele.append(u'fam')
Modele.append(u'fami')
Modele.append(u'familier')
Modele.append(u'famille')
Modele.append(u'fanta')
Modele.append(u'fantastique')
Modele.append(u'fauconnerie')
Modele.append(u'ferro')
Modele.append(u'ferroviaire')
Modele.append(u'fig.')
Modele.append(u'figure')
Modele.append(u'figures')
Modele.append(u'figuré')
Modele.append(u'finan')
Modele.append(u'finance')
Modele.append(u'finances')
Modele.append(u'fisc')
Modele.append(u'fiscalité')
Modele.append(u'flamants')
Modele.append(u'fleurs')
Modele.append(u'fleuve')
Modele.append(u'fm ?')
Modele.append(u'fonderie')
Modele.append(u'fontainerie')
Modele.append(u'foot')
Modele.append(u'football américain')
Modele.append(u'football canadien')
Modele.append(u'football')
Modele.append(u'footing')
Modele.append(u'formel')
Modele.append(u'fortification')
Modele.append(u'franc-maçonnerie')
Modele.append(u'fromages')
Modele.append(u'fruits')
Modele.append(u'félins')
Modele.append(u'gall')
Modele.append(u'gallicisme')
Modele.append(u'gastro')
Modele.append(u'gastron')
Modele.append(u'gastronomie')
Modele.append(u'gastéropodes')
Modele.append(u'genre ?')
Modele.append(u'genre')
Modele.append(u'genres musicaux')
Modele.append(u'gentilés ?')
Modele.append(u'gentilés')
Modele.append(u'geog')    # à remplacer ?
Modele.append(u'geol')
Modele.append(u'germanisme')
Modele.append(u'giraffidés')
Modele.append(u'glaciol')
Modele.append(u'glaciologie')
Modele.append(u'gladiateurs')
Modele.append(u'golf')
Modele.append(u'golfe')
Modele.append(u'golfes')
Modele.append(u'grades')
Modele.append(u'gram')
Modele.append(u'grammaire')
Modele.append(u'graphe')
Modele.append(u'gravure')
Modele.append(u'grenouilles')
Modele.append(u'grues')
Modele.append(u'guerre')
Modele.append(u'gymnastique')
Modele.append(u'gynécologie')
Modele.append(u'gâteaux')
Modele.append(u'gén-indén')
Modele.append(u'génit')
Modele.append(u'génitif')
Modele.append(u'génitif')
Modele.append(u'généal')
Modele.append(u'généalogie')
Modele.append(u'généralement indénombrable')
Modele.append(u'généralement pluriel')
Modele.append(u'généralement singulier')
Modele.append(u'génétique')
Modele.append(u'géog')
Modele.append(u'géographie')
Modele.append(u'géol')
Modele.append(u'géologie')
Modele.append(u'géom')
Modele.append(u'géomatique')
Modele.append(u'géométrie')
Modele.append(u'géoph')
Modele.append(u'géophysique')
Modele.append(u'hand')
Modele.append(u'handball')
Modele.append(u'handicap')
Modele.append(u'handisport')
Modele.append(u'hapax')
Modele.append(u'herpétologie')
Modele.append(u'hindouisme')
Modele.append(u'hippisme')
Modele.append(u'hippologie')
Modele.append(u'hispanisme')
Modele.append(u'hist')
Modele.append(u'hist')
Modele.append(u'histoire')
Modele.append(u'histol')
Modele.append(u'histologie')
Modele.append(u'histologie')
Modele.append(u'hockey sur glace')
Modele.append(u'hockey')
Modele.append(u'horlogerie')
Modele.append(u'horticulture')
Modele.append(u'humour')
Modele.append(u'hydraulique')
Modele.append(u'hydrobiologie')
Modele.append(u'hygiène')
Modele.append(u'hyperb')
Modele.append(u'hyperbole')
Modele.append(u'hérald')
Modele.append(u'héraldique')
Modele.append(u'hérons')
Modele.append(u'i')
Modele.append(u'ibis')
Modele.append(u'ichtyo')
Modele.append(u'ichtyologie')
Modele.append(u'idiomatique')
Modele.append(u'idiotisme')
Modele.append(u'illégalité')
Modele.append(u'impers')
Modele.append(u'impersonnel')
Modele.append(u'impr')
Modele.append(u'imprimerie')
Modele.append(u'improprement')
Modele.append(u'inanimé')
Modele.append(u'indus')
Modele.append(u'industrie pétrolière')
Modele.append(u'industrie')
Modele.append(u'indéc')
Modele.append(u'indécl')
Modele.append(u'indéclinable')
Modele.append(u'indéfini')
Modele.append(u'indén')
Modele.append(u'indénombrable')
Modele.append(u'info')
Modele.append(u'infographie')
Modele.append(u'inform')
Modele.append(u'informatique')
Modele.append(u'informatique')
Modele.append(u'informel')
Modele.append(u'injur')
Modele.append(u'injurieux')
Modele.append(u'insecte')
Modele.append(u'insectes')
Modele.append(u'instrumental')
Modele.append(u'instruments de mesure')
Modele.append(u'instruments')
Modele.append(u'insultes')
Modele.append(u'intelligence artificielle')
Modele.append(u'interjection')
Modele.append(u'internet')
Modele.append(u'intrans')
Modele.append(u'intransitif')
Modele.append(u'iron')
Modele.append(u'ironie')
Modele.append(u'ironique')
Modele.append(u'irrég')
Modele.append(u'irrégulier')
Modele.append(u'islam')
Modele.append(u'jardi')
Modele.append(u'jardin')
Modele.append(u'jardinage')
Modele.append(u'jazz')
Modele.append(u'jeu de paume')
Modele.append(u'jeu vidéo')
Modele.append(u'jeux de cartes')
Modele.append(u'jeux vidéo')
Modele.append(u'jeux')
Modele.append(u'joaillerie')
Modele.append(u'jogging')
Modele.append(u'jonglage')
Modele.append(u'jonglerie')
Modele.append(u'jouets')
Modele.append(u'journal')
Modele.append(u'journalisme')
Modele.append(u'judaïsme')
Modele.append(u'judo')
Modele.append(u'juri')
Modele.append(u'jurisprudence')
Modele.append(u'just')
Modele.append(u'justice')
Modele.append(u'karaté')
Modele.append(u'kung-fu')
Modele.append(u'langage Java')
Modele.append(u'langage SMS')
Modele.append(u'langages informatiques')
Modele.append(u'langues')
Modele.append(u'latinisme')
Modele.append(u'lexicographie')
Modele.append(u'lianes')
Modele.append(u'ling')
Modele.append(u'linguistique')
Modele.append(u'litote')
Modele.append(u'litt')
Modele.append(u'littér')
Modele.append(u'littéraire')
Modele.append(u'littérature')
Modele.append(u'liturgie')
Modele.append(u'livre')
Modele.append(u'locat')
Modele.append(u'locatif')
Modele.append(u'logi')
Modele.append(u'logique')
Modele.append(u'logistique')
Modele.append(u'loisirs')
Modele.append(u'lutherie')
Modele.append(u'législation')
Modele.append(u'légumes')
Modele.append(u'léporidé')
Modele.append(u'lézards')
Modele.append(u'machines')
Modele.append(u'magnétisme')
Modele.append(u'mah-jong')
Modele.append(u'mahjong')
Modele.append(u'maintenance')
Modele.append(u'majong')
Modele.append(u'maladie')
Modele.append(u'maladies de l’œil')
Modele.append(u'maladies')
Modele.append(u'mammifères')
Modele.append(u'manège')
Modele.append(u'marbrerie')
Modele.append(u'mari')
Modele.append(u'marine')
Modele.append(u'marketing')
Modele.append(u'maroquinerie')
Modele.append(u'marsupial')
Modele.append(u'math')
Modele.append(u'mathématiques')
Modele.append(u'maçon')
Modele.append(u'maçonnerie')
Modele.append(u'menuiserie')
Modele.append(u'mercatique')
Modele.append(u'mers')
Modele.append(u'meuble')
Modele.append(u'meuble héraldique')
Modele.append(u'mf ?')
Modele.append(u'mf ?')
Modele.append(u'microbiologie')
Modele.append(u'mili')
Modele.append(u'milit')
Modele.append(u'militaire')
Modele.append(u'minér')
Modele.append(u'minéral')
Modele.append(u'minéralogie')
Modele.append(u'minéraux')
Modele.append(u'miroiterie')
Modele.append(u'mobilier')
Modele.append(u'mollusques')
Modele.append(u'monarchie')
Modele.append(u'monnaies')
Modele.append(u'montagnes')
Modele.append(u'morphologie végétale')
Modele.append(u'motocyclisme')
Modele.append(u'mouches')
Modele.append(u'muscle')
Modele.append(u'musculation')
Modele.append(u'musi')
Modele.append(u'musiciens')
Modele.append(u'musique')
Modele.append(u'musiques')
Modele.append(u'myco')
Modele.append(u'mycol')
Modele.append(u'mycologie')
Modele.append(u'mythol')
Modele.append(u'mythologie')
Modele.append(u'mythologie égyptienne')
Modele.append(u'mythologie grecque')
Modele.append(u'méca')
Modele.append(u'mécanique')
Modele.append(u'mécoupure')
Modele.append(u'méd')
Modele.append(u'méde')
Modele.append(u'médecine non conv')
Modele.append(u'médecine')
Modele.append(u'média')
Modele.append(u'médicaments')
Modele.append(u'méduses')
Modele.append(u'mélio')
Modele.append(u'mélioratif')
Modele.append(u'métal')
Modele.append(u'métallurgie')
Modele.append(u'métaph')
Modele.append(u'métaphore')
Modele.append(u'métaplasmes')
Modele.append(u'méton')
Modele.append(u'métonymie')
Modele.append(u'métrol')
Modele.append(u'métrologie')
Modele.append(u'météo')
Modele.append(u'météorol')
Modele.append(u'météorologie')
Modele.append(u'narratol')
Modele.append(u'narratologie')
Modele.append(u'nata')
Modele.append(u'natation')
Modele.append(u'navig')
Modele.append(u'navigation')
Modele.append(u'neuro')
Modele.append(u'neurologie')
Modele.append(u'noblesse')
Modele.append(u'nom')
Modele.append(u'nombre')
Modele.append(u'nomin')
Modele.append(u'nominatif')
Modele.append(u'nosologie')
Modele.append(u'note-gentilé')
Modele.append(u'novlangue')
Modele.append(u'nuages')
Modele.append(u'nucl')
Modele.append(u'nucléaire')
Modele.append(u'numis')
Modele.append(u'numismatique')
Modele.append(u'nutrition')
Modele.append(u'néol litt')
Modele.append(u'néol')
Modele.append(u'néologisme')
Modele.append(u'obsolète')
Modele.append(u'obstétrique')
Modele.append(u'oenol')
Modele.append(u'oenologie')
Modele.append(u'oies')
Modele.append(u'oiseaux')
Modele.append(u'ophtalmologie')
Modele.append(u'opti')
Modele.append(u'optique')
Modele.append(u'optométrie')
Modele.append(u'ordin')
Modele.append(u'ordinal')
Modele.append(u'orfèvrerie')
Modele.append(u'ornit')
Modele.append(u'ornithologie')
Modele.append(u'outils')
Modele.append(u'p-us')
Modele.append(u'palindrome')
Modele.append(u'palmiers')
Modele.append(u'paléo')
Modele.append(u'paléographite')
Modele.append(u'paléontol')
Modele.append(u'paléontologie')
Modele.append(u'palmipèdes')
Modele.append(u'papeterie')
Modele.append(u'papillons')
Modele.append(u'papèterie')
Modele.append(u'par analogie')
Modele.append(u'par dérision')
Modele.append(u'par métonymie')
Modele.append(u'parfumerie')
Modele.append(u'passif')
Modele.append(u'pathologie')
Modele.append(u'patin')
Modele.append(u'paume')
Modele.append(u'pays')
Modele.append(u'pêche à la ligne')
Modele.append(u'peinture')
Modele.append(u'perroquets')
Modele.append(u'peu attesté')
Modele.append(u'peu usité')
Modele.append(u'peuplier')
Modele.append(u'peupliers')
Modele.append(u'pharma')
Modele.append(u'pharmacie')
Modele.append(u'pharmacol')
Modele.append(u'pharmacologie')
Modele.append(u'philo')
Modele.append(u'philosophie')
Modele.append(u'phobies')
Modele.append(u'phon')
Modele.append(u'phonologie')
Modele.append(u'phonétique')
Modele.append(u'photo')
Modele.append(u'photographie')
Modele.append(u'phys')
Modele.append(u'physique des réacteurs')
Modele.append(u'physio')
Modele.append(u'physiol')
Modele.append(u'physiologie')
Modele.append(u'physique')
Modele.append(u'phyton')
Modele.append(u'phytonimie')
Modele.append(u'phytopathologie')
Modele.append(u'plais')
Modele.append(u'plaisanterie')
Modele.append(u'planche à neige')
Modele.append(u'planche à roulettes')
Modele.append(u'plans d’eau')
Modele.append(u'plante')
Modele.append(u'plantes aromatiques')
Modele.append(u'plantes')
Modele.append(u'plongée')
Modele.append(u'plurale tantum')
Modele.append(u'pluriel ?')
Modele.append(u'poet')
Modele.append(u'points cardinaux')
Modele.append(u'poires')
Modele.append(u'poisson')
Modele.append(u'poissons')
Modele.append(u'poker')
Modele.append(u'police')
Modele.append(u'polit')
Modele.append(u'politique')
Modele.append(u'pommes')
Modele.append(u'ponctuations')
Modele.append(u'popu')
Modele.append(u'populaire')
Modele.append(u'porcins')
Modele.append(u'positions')
Modele.append(u'poés')
Modele.append(u'poésie')
Modele.append(u'poét')
Modele.append(u'poétique')
Modele.append(u'poules')
Modele.append(u'ppart')
Modele.append(u'presse')
Modele.append(u'prestidigitation')
Modele.append(u'prison')
Modele.append(u'prnl')
Modele.append(u'probabilités')
Modele.append(u'procédure')
Modele.append(u'prog')
Modele.append(u'programmation')
Modele.append(u'pronl')
Modele.append(u'pronominal')
Modele.append(u'propre')
Modele.append(u'propriété')
Modele.append(u'protestantisme')
Modele.append(u'protocoles')
Modele.append(u'protéines')
Modele.append(u'prov')
Modele.append(u'proverbe')
Modele.append(u'proverbes')
Modele.append(u'proverbial')
Modele.append(u'préhistoire')
Modele.append(u'prépositionnel')
Modele.append(u'psych')
Modele.append(u'psychanalyse')
Modele.append(u'psychia')
Modele.append(u'psychiatrie')
Modele.append(u'psycho')
Modele.append(u'psycho')
Modele.append(u'psychol')
Modele.append(u'psychologie')
Modele.append(u'psychotropes')
Modele.append(u'publicité')
Modele.append(u'pâtes')
Modele.append(u'pâtisserie')
Modele.append(u'pédol')
Modele.append(u'pédologie')
Modele.append(u'péjoratif')
Modele.append(u'pélicans')
Modele.append(u'pétanque')
Modele.append(u'pétro')
Modele.append(u'pétrochimie')
Modele.append(u'pêch')
Modele.append(u'pêche')
Modele.append(u'pêches')
Modele.append(u'radio')
Modele.append(u'raies')
Modele.append(u'rapaces')
Modele.append(u'rare')
Modele.append(u'reli')
Modele.append(u'religieux')
Modele.append(u'religion')
Modele.append(u'religions')
Modele.append(u'reliure')
Modele.append(u'renseignement')
Modele.append(u'repro')
Modele.append(u'reproduction')
Modele.append(u'reptiles')
Modele.append(u'rhéto')
Modele.append(u'rhétorique')
Modele.append(u'robotiques')
Modele.append(u'roches')
Modele.append(u'rongeur')
Modele.append(u'rugby')
Modele.append(u'running')
Modele.append(u'récip')
Modele.append(u'réciproque')
Modele.append(u'réfl')
Modele.append(u'réflexif')
Modele.append(u'réfléchi')
Modele.append(u'région')
Modele.append(u'réseau')
Modele.append(u'réseaux informatiques')
Modele.append(u'réseaux')
Modele.append(u'saccusatif')
Modele.append(u'saisons')
Modele.append(u'salades')
Modele.append(u'salles')
Modele.append(u'sandwitchs')
Modele.append(u'sans pron')
Modele.append(u'satellites')
Modele.append(u'saules')
Modele.append(u'saut en hauteur')
Modele.append(u'sci-fi')
Modele.append(u'science-fiction')
Modele.append(u'sciences')
Modele.append(u'scientifiques')
Modele.append(u'scol')
Modele.append(u'scolaire')
Modele.append(u'scul')
Modele.append(u'sculpture')
Modele.append(u'sdatif')
Modele.append(u'seigneuries')
Modele.append(u'sentiments')
Modele.append(u'serpents')
Modele.append(u'serru')
Modele.append(u'serrurerie')
Modele.append(u'sexe')
Modele.append(u'sexualité')
Modele.append(u'singes')
Modele.append(u'singulare tantum')
Modele.append(u'sinstrumental')
Modele.append(u'skate')
Modele.append(u'skateboard')
Modele.append(u'ski alpin')
Modele.append(u'ski de fond')
Modele.append(u'snow')
Modele.append(u'snowboard')
Modele.append(u'socio')
Modele.append(u'sociol')
Modele.append(u'sociologie')
Modele.append(u'soldats')
Modele.append(u'sout')
Modele.append(u'soutenu')
Modele.append(u'spatules')
Modele.append(u'sport de combat')
Modele.append(u'sport de glisse')
Modele.append(u'sport mécanique')
Modele.append(u'sport')
Modele.append(u'sportifs')
Modele.append(u'sports de combat')
Modele.append(u'sports de glisse')
Modele.append(u'sports')
Modele.append(u'squelette')
Modele.append(u'stat')
Modele.append(u'statistiques')
Modele.append(u'stéréochimie')
Modele.append(u'stéréotomie')
Modele.append(u'stéréotype')
Modele.append(u'substances')
Modele.append(u'superlatif de')
Modele.append(u'supprimer-déf ?')
Modele.append(u'surf')
Modele.append(u'sylvi')
Modele.append(u'sylviculture')
Modele.append(u'symboles unités')
Modele.append(u't')
Modele.append(u't/i')
Modele.append(u'taille de pierre')
Modele.append(u'tauromachie')
Modele.append(u'td')
Modele.append(u'tech')
Modele.append(u'technique')
Modele.append(u'techno')
Modele.append(u'technol')
Modele.append(u'technologie')
Modele.append(u'technologie des réacteurs')
Modele.append(u'temps géologiques')
Modele.append(u'temps')
Modele.append(u'tennis de table')
Modele.append(u'tennis')
Modele.append(u'term')
Modele.append(u'terme non standard')
Modele.append(u'territoires')
Modele.append(u'text')
Modele.append(u'textile')
Modele.append(u'textiles')
Modele.append(u'thermodynamique')
Modele.append(u'théol')
Modele.append(u'théologie')
Modele.append(u'théorie des graphes')
Modele.append(u'théât')
Modele.append(u'théâtre')
Modele.append(u'tind')
Modele.append(u'tir à l’arc')
Modele.append(u'tissage')
Modele.append(u'tissus')
Modele.append(u'tonnellerie')
Modele.append(u'topo')
Modele.append(u'topographie')
Modele.append(u'topologie')
Modele.append(u'topon')
Modele.append(u'toponymie')
Modele.append(u'tortues')
Modele.append(u'tour')
Modele.append(u'tourisme')
Modele.append(u'tr-dir')
Modele.append(u'tr-ind')
Modele.append(u'tr-indir')
Modele.append(u'trad-exe')
Modele.append(u'trans')
Modele.append(u'transit')
Modele.append(u'transitif')
Modele.append(u'transp')
Modele.append(u'transport')
Modele.append(u'transports')
Modele.append(u'travail')
Modele.append(u'très familier')
Modele.append(u'très rare')
Modele.append(u'très très rare')
Modele.append(u'très-rare')
Modele.append(u'type')
Modele.append(u'typo')
Modele.append(u'typographie')
Modele.append(u'télé')
Modele.append(u'télécom')
Modele.append(u'télécommunications')
Modele.append(u'téléphonie')
Modele.append(u'télévision')
Modele.append(u'typographie et informatique')
Modele.append(u'ufologie')
Modele.append(u'un os')
Modele.append(u'unités')
Modele.append(u'urban')
Modele.append(u'urbanisme')
Modele.append(u'usage critiqué')
Modele.append(u'usinage')
Modele.append(u'usines')
Modele.append(u'ustensiles')
Modele.append(u'vaudou')
Modele.append(u'vents')
Modele.append(u'verrerie')
Modele.append(u'vers')
Modele.append(u'versification')
Modele.append(u'viandes')
Modele.append(u'vieilli')
Modele.append(u'vieux')
Modele.append(u'vins')
Modele.append(u'virologie')
Modele.append(u'virus')
Modele.append(u'viticulture')
Modele.append(u'vitrerie')
Modele.append(u'vocat')
Modele.append(u'vocatif')
Modele.append(u'voitures')
Modele.append(u'volcanologie')
Modele.append(u'volley')
Modele.append(u'volley-ball')
Modele.append(u'vulg')
Modele.append(u'vulgaire')
Modele.append(u'véhicules')
Modele.append(u'vétérinaire')
Modele.append(u'vête')
Modele.append(u'vêtements')
Modele.append(u'wiki')
Modele.append(u'xénarthres')
Modele.append(u'yoga')
Modele.append(u'zool')
Modele.append(u'zoologie')
Modele.append(u'zootechnie')
Modele.append(u'ébauche-trad-exe')
Modele.append(u'échecs')
Modele.append(u'écol')
Modele.append(u'écologie')
Modele.append(u'écon')
Modele.append(u'économie')
Modele.append(u'écureuils')
Modele.append(u'édifices')
Modele.append(u'édition')
Modele.append(u'éduc')
Modele.append(u'éducation')
Modele.append(u'élatif')
Modele.append(u'élec')
Modele.append(u'électoraux')
Modele.append(u'électricité')
Modele.append(u'électro')
Modele.append(u'électron')
Modele.append(u'électronique')
Modele.append(u'électrot')
Modele.append(u'électrotech')
Modele.append(u'électrotechnique')
Modele.append(u'élevage')
Modele.append(u'éléments')
Modele.append(u'épices')
Modele.append(u'épithète')
Modele.append(u'équi')
Modele.append(u'équitation')
Modele.append(u'établissements')
Modele.append(u'étoiles')
Modele.append(u'œnologie')

limit7 = len(Modele)
# Code langue quoi qu'il arrive
Modele.append(u'...')
Modele.append(u'ébauche-syn')
Modele.append(u'non standard')
Modele.append(u'ébauche-trans')
Modele.append(u'ébauche-étym-nom-scientifique')
Modele.append(u'ébauche-étym')
Modele.append(u'ébauche-déf')
Modele.append(u'ébauche-exe')
Modele.append(u'ébauche-pron')
Modele.append(u'ébauche')
Modele.append(u'Région ?')
Modele.append(u'région ?')

limit8 = len(Modele)
# Code langue si étymologie
Modele = Modele + etymologyTemplatesWithLanguageAtFirst + etymologyTemplatesWithLanguageAtSecond

limit9 = len(Modele)
# Modèles régionaux, avec "nocat" pour les prononciations
Modele.append(u'Acadie')
Modele.append(u'Afrique')
Modele.append(u'Afrique du Sud')
Modele.append(u'Algérie')
Modele.append(u'Allemagne')
Modele.append(u'Alsace')
Modele.append(u'Amérique centrale')
Modele.append(u'Amérique du Nord')
Modele.append(u'Amérique du Sud')
Modele.append(u'Amérique latine')
Modele.append(u'Anjou')
Modele.append(u'Antilles')
Modele.append(u'Aquitaine')
Modele.append(u'Argentine')
Modele.append(u'Australie')
Modele.append(u'Autriche')
Modele.append(u'Auvergne')
Modele.append(u'Baléares')
Modele.append(u'Belgique')
Modele.append(u'Belize')
Modele.append(u'Bénin')
Modele.append(u'Berry')
Modele.append(u'Bolivie')
Modele.append(u'Bordelais')
Modele.append(u'Bourgogne')
Modele.append(u'Brésil')
Modele.append(u'Bretagne')
Modele.append(u'Burkina Faso')
Modele.append(u'Cameroun')
Modele.append(u'Canada')
Modele.append(u'Catalogne')
Modele.append(u'Champagne')
Modele.append(u'Chef-Boutonne')
Modele.append(u'Chili')
Modele.append(u'Chine')
Modele.append(u'Colombie')
Modele.append(u'Commonwealth')
Modele.append(u'Congo')
Modele.append(u'Congo-Brazzaville')
Modele.append(u'Congo-Kinshasa')
Modele.append(u'Corée du Nord')
Modele.append(u'Corée du Sud')
Modele.append(u'Corse')
Modele.append(u'Costa Rica')
Modele.append(u'Côte d’Ivoire')
Modele.append(u'Cuba')
Modele.append(u'Écosse')
Modele.append(u'Espagne')
Modele.append(u'États-Unis')
Modele.append(u'Europe')
Modele.append(u'France')
Modele.append(u'Franche-Comté')
Modele.append(u'Gascogne')
Modele.append(u'Gaspésie')
Modele.append(u'Guadeloupe')
Modele.append(u'Guinée')
Modele.append(u'Guyane')
Modele.append(u'Haïti')
Modele.append(u'Honduras')
Modele.append(u'Hongrie')
Modele.append(u'Île-de-France')
Modele.append(u'Inde')
Modele.append(u'Irlande')
Modele.append(u'‎Israël')
Modele.append(u'Jamaïque')
Modele.append(u'Japon')
Modele.append(u'Languedoc-Roussillon')
Modele.append(u'Le Mans')
Modele.append(u'Lettonie')
Modele.append(u'Liban')
Modele.append(u'Liechtenstein')
Modele.append(u'Limousin')
Modele.append(u'Lituanie')
Modele.append(u'Lorraine')
Modele.append(u'Louisiane')
Modele.append(u'Luxembourg')
Modele.append(u'Lyonnais')
Modele.append(u'Madagascar')
Modele.append(u'Maghreb')
Modele.append(u'Mali')
Modele.append(u'Maroc')
Modele.append(u'Marseille')
Modele.append(u'Maurice')
Modele.append(u'Mauritanie')
Modele.append(u'Mayotte')
Modele.append(u'Mexique')
Modele.append(u'Midi')
Modele.append(u'Midi toulousain')
Modele.append(u'Moldavie')
Modele.append(u'Namibie')
Modele.append(u'Nantes')
Modele.append(u'Navarre')
Modele.append(u'Niger')
Modele.append(u'Nigéria')
Modele.append(u'Normandie')
Modele.append(u'Nouvelle-Calédonie')
Modele.append(u'Nouvelle-Zélande')
Modele.append(u'Occitanie')
Modele.append(u'Océanie')
Modele.append(u'Orient')
Modele.append(u'Paraguay')
Modele.append(u'Paris')
Modele.append(u'Pays-Bas')
Modele.append(u'Pays basque')
Modele.append(u'Pérou')
Modele.append(u'Picardie')
Modele.append(u'Poitou')
Modele.append(u'Pologne')
Modele.append(u'Polynésie française')
Modele.append(u'Porto Rico')
Modele.append(u'Portugal')
Modele.append(u'Provence')
Modele.append(u'Québec')
Modele.append(u'Quercy')
Modele.append(u'République dominicaine')
Modele.append(u'République tchèque')
Modele.append(u'Réunion')
Modele.append(u'Roumanie')
Modele.append(u'Royaume-Uni')
Modele.append(u'Russie')
Modele.append(u'Salvador')
Modele.append(u'Savoie')
Modele.append(u'Sénégal')
Modele.append(u'Slovaquie')
Modele.append(u'Sologne')
Modele.append(u'Suède')
Modele.append(u'Suisse')
Modele.append(u'Taïwan')
Modele.append(u'Tchad')
Modele.append(u'Togo')
Modele.append(u'Transnistrie')
Modele.append(u'Tunisie')
Modele.append(u'Uruguay')
Modele.append(u'Valence')
Modele.append(u'Var')
Modele.append(u'Velay')
Modele.append(u'Venezuela')
Modele.append(u'Viêt Nam')
Modele.append(u'Vosges')

# Abréviations (python pagegenerators.py -redirectonly:Template:!)
Modele.append(u'EU')
Modele.append(u'FR')
Modele.append(u'BE')
Modele.append(u'CH')
Modele.append(u'QC')
Modele.append(u'CA')
Modele.append(u'US')
Modele.append(u'USA')
Modele.append(u'UK')
Modele.append(u'GB')
Modele.append(u'AU')
Modele.append(u'NZ')
Modele.append(u'IE')
# Modèles de pronociation à synchroniser
Modele.append(u'fr-verbe-flexion')

limit10 = len(Modele) # Somme des modèles traités
'''
# TODO : non traités

    # Sans code langue
        Modele.append(u'voir')
        Modele.append(u'spécialement')
        Modele.append(u'région')
        Modele.append(u'régio')
        Modele.append(u'régional')

    # Utilisés sur la ligne de forme (parfois sans parenthèses)
        Modele.append(u'déterminé')
        Modele.append(u'indéterminé')
        Modele.append(u'dét')
        Modele.append(u'indét')
        Modele.append(u'perfectif')
        Modele.append(u'imperfectif')
        Modele.append(u'perf')
        Modele.append(u'imperf')

    # à synchroniser
        Modele.append(u'T')...
'''

Nombre = []
Nombre.append(u'au singulier')
Nombre.append(u'd')
Nombre.append(u'fplur')
Nombre.append(u'fsing')
Nombre.append(u'indén')
Nombre.append(u'indénombrable')
Nombre.append(u'invar')
Nombre.append(u'invariable')
Nombre.append(u'mplur')
Nombre.append(u'msing')
Nombre.append(u'nombre')
Nombre.append(u'nplur')
Nombre.append(u'nsing')
Nombre.append(u'p')
Nombre.append(u'plurale tantum')
Nombre.append(u'pluriel')
Nombre.append(u'pluriel ?')
Nombre.append(u's')
Nombre.append(u'singulier')
Nombre.append(u'singulare tantum')
Nombre.append(u'sp')

Genre = []
Genre.append(u'c')
Genre.append(u'f')
Genre.append(u'fplur')
Genre.append(u'fsing')
Genre.append(u'genre')
Genre.append(u'm')
Genre.append(u'mf')
Genre.append(u'mf ?')
Genre.append(u'fm ?')
Genre.append(u'mplur')
Genre.append(u'msing')
Genre.append(u'n')
Genre.append(u'nplur')
Genre.append(u'nsing')


def treatPageByName(pageName):
    global natures, definitionTemplates, definitionSentences, etymologyTemplates, etymologyTemplatesWithLanguageAtLang, \
        etymologyTemplatesInSatelliteWords, etymologyTemplatesWithLanguageAtFirst, etymologyTemplatesWithLanguageAtSecond
    summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
    if debugLevel > 0: print u'------------------------------------'
    pywikibot.output(u"\n\03{blue}" + pageName + u"\03{default}")
    if pageName[-3:] == u'.js' or pageName[-4:] == u'.css': return
    if pageName.find(u'’') != -1:
        page = Page(site, pageName.replace(u'’', u'\''))
        if not page.exists() and page.namespace() == 0:
            if debugLevel > 0: print u'Création d\'une redirection apostrophe'
            savePage(page, u'#REDIRECT[[' + pageName + ']]', u'Redirection pour apostrophe', minorEdit = True)

    page = Page(site, pageName)
    if debugLevel == 0 and waitAfterHumans and (pageName.find('<') != -1 or not hasMoreThanTime(page)): return

    currentPageContent = getContentFromPage(page, 'All')
    if currentPageContent == 'KO':
        if debugLevel > 0: print u' Page vide'
        return

    if cancelUser != {}:
        pageContent, summary = cancelEdition(page, cancelUser)
        page = Page(site, pageName) # a page reset is needed to edit the last version
        if pageContent != '' and pageContent != currentPageContent:
            savePage(page, pageContent, summary)
        return

    pageContent = currentPageContent
    finalPageContent = u''
    rePageName = re.escape(pageName)

    pageContent = globalOperations(pageContent)
    if fixFiles: pageContent = replaceFilesErrors(pageContent)
    if fixTags: pageContent = replaceDepretacedTags(pageContent)
    if checkURL: pageContent = hyperlynx(pageContent)

    if treatTemplates and page.namespace() == 10:
        # Modèle:
        templates = [u'emploi', u'région', u'registre', u'term']
        for template in templates:
            if not u'{{{clé|' in pageContent and pageContent[:len(u'{{' + template)] == u'{{' + template and u'\n}}<noinclude>' in pageContent:
                summary = u'[[Wiktionnaire:Wikidémie/juillet_2017#Pour_conclure_Wiktionnaire:Prise_de_d.C3.A9cision.2FCl.C3.A9s_de_tri_fran.C3.A7aises_par_d.C3.A9faut|Clé de tri]]'
                pageContent = pageContent[:pageContent.find(u'\n}}<noinclude>')] + u'\n|clé={{{clé|}}}' + pageContent[pageContent.find(u'\n}}<noinclude>'):]

        regex = u'<includeonly> *\n*{{\#if(eq)?: *{{NAMESPACE}}[^<]+\[\[Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section[^<]+</includeonly>'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex,  u'{{anciens modèles de section}}', pageContent, re.MULTILINE)
        if debugLevel > 1: raw_input(pageContent.encode(config.console_encoding, 'replace'))

        finalPageContent = pageContent

    elif page.namespace() == 0 or username in pageName:
        # Articles
        regex = ur'{{(formater|SI|supp|supprimer|PàS)[\|}]'
        if re.search(regex, pageContent):
            if debugLevel > 0: print u'Page en travaux : non traitée l 1409'
            return

        if listHomophons:
            languageSection, hStart, hEnd = getLanguageSection(pageContent, 'fr')
            if languageSection is not None:
                homophons, hStart, hEnd = getSection(languageSection, u'homophones')
                if debugLevel > 1: raw_input(homophons.encode(config.console_encoding, 'replace'))
                outputFile.write((homophons.replace(u'==== {{S|homophones|fr}} ====\n', u'').replace(u'=== {{S|homophones|fr}} ===\n', u'')).encode(config.console_encoding, 'replace'))
            return

        pageContent, summary = addSeeBanner(pageName, pageContent, summary)
        pageContent, summary = formatSections(pageContent, summary)

        if debugLevel > 0: print u' {{S}} conversion and formatting'
        EgalSection = u'==='
        for p in range(1, limit4):
            if debugLevel > 1: print Modele[p] + ur'|S\|'+ Section[p]
            if p == limit2: EgalSection = u'===='
            if p == limit3: EgalSection = u'====='

            regex = ur'[= ]*{{[\-loc]*(' + Modele[p] + ur'|S\|'+ Section[p] + ur')([^}]*)}}[= ]*\n'
            if re.search(regex, pageContent):
                if debugLevel > 1: print u' {{S| : check des niveaux de section 1 : ' + Section[p] + u' ' + EgalSection
                pageContent = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'\2}} ' + EgalSection + u'\n', pageContent)

            regex = ur'[= ]*{{\-flex[\-loc]*(' + Modele[p] + ur'|S\|' + Section[p] + ur')\|([^}]*)}}[= ]*\n'
            if re.search(regex, pageContent):
                if debugLevel > 1: print u' {{S| : check des niveaux de section 2 : ' + Section[p]
                pageContent = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'|\2|flexion}} ' + EgalSection + u'\n', pageContent)

            if p > limit1 and p < limit3-1:
                regex = ur'({{S\|'+ Section[p] + ur')\|[a-z]+}}'
                if debugLevel > 1: print u' {{S| : retrait de code langue'
                pageContent = re.sub(regex, ur'\1}}', pageContent)

        pageContent, summary = formatTranslations(pageContent, summary)
        pageContent, summary = formatTemplates(pageContent, summary)
        pageContent, summary = formatWikicode(pageContent, summary, pageName)
        pageContent, summary = addTemplates(pageContent, summary)
        pageContent, summary = renameTemplates(pageContent, summary)
        pageContent, summary = removeDoubleCategoryWhenTemplate(pageContent, summary)
        pageContent, summary = formatCategories(pageContent, summary)
        pageContent, summary = formatLanguagesTemplates(pageContent, summary, pageName)
        pageContent, summary = sortTranslations(pageContent, summary)
        if addDefaultSortKey:
            pageContent = addDefaultSort(pageName, pageContent) #TODO: compare the Lua with ", empty = True"
        pageContent, summary = addAppendixLinks(pageContent, summary, pageName)

        if debugLevel > 0: print u' Flexions formatting'
        if debugLevel > 1: print u'  fr'
        regex = ur"(=== {{S\|nom\|fr)\|flexion(}} ===\n(?:{{fr[^\n]*\n)*'''" + rePageName + ur"''' [^\n]*{{fsing}})"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1\2', pageContent)
            summary = summary + u', un nom féminin n\'est pas une flexion en français'
        regex = ur"(=== {{S\|nom\|fr)\|flexion(}} ===\n(?:{{fr[^\n]*\n)*'''" + rePageName + ur"''' [^\n]*{{f}}\n# *'*[Ff]éminin (?:de|singulier))"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1\2', pageContent)
            summary = summary + u', un nom féminin n\'est pas une flexion en français'

        if pageName.find(u'*') == -1 and pageName[-1:] == 's':
            language = u'fr'
            naturesWithPlural = ['nom', 'adjectif', 'suffixe']
            singularPageName = getLemmaFromPlural(pageContent, language, naturesWithPlural)
            if singularPageName != u'': treatPageByName(singularPageName) # Formatage des boites de flexion à récupérer
            for nature in naturesWithPlural:
                regex = ur"(== {{langue|" + language + ur"}} ==\n=== {{S\|" + nature + ur"\|" + language + ur")\|num=2"
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\1', pageContent)
                    summary = summary + u', retrait de |num='

                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur")(\}} ===\n[^\n]*\n*'''" + rePageName + ur"'''[^\n]*\n# *'*'*(Masculin)*(Féminin)* *[P|p]luriel de *'*'* *\[\[)"
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\1|flexion\2', pageContent)
                    summary = summary + u', ajout de |flexion'

                if pageName[-2:] != 'ss':
                    if singularPageName != u'':
                        flexionFlexionTemplate = getFlexionTemplate(pageName, language, nature)
                        if flexionFlexionTemplate == u'':
                            if debugLevel > 0: print u' Ajout d\'une boite dans une flexion'
                            lemmaFlexionTemplate = getFlexionTemplateFromLemma(singularPageName, language, nature)
                            for flexionTemplateFrWithMs in flexionTemplatesFrWithMs:
                                if lemmaFlexionTemplate.find(flexionTemplateFrWithMs) != -1:
                                    if debugLevel > 0: print u'flexionTemplateFrWithMs'
                                    regex = ur"\|ms=[^\|}]*"
                                    if not re.search(regex, lemmaFlexionTemplate):
                                        lemmaFlexionTemplate = lemmaFlexionTemplate + ur'|ms=' + singularPageName
                            for flexionTemplateWithS in flexionTemplatesFrWithS:
                                if lemmaFlexionTemplate.find(flexionTemplateWithS) != -1:
                                    regex = ur"\|s=[^\|}]*"
                                    if not re.search(regex, lemmaFlexionTemplate):
                                        lemmaFlexionTemplate = lemmaFlexionTemplate + ur'|s=' + singularPageName

                            ''' Remplacement des {{fr-rég}} par plus précis (lancé pour patcher des pages)
                            if lemmaFlexionTemplate.find(language + ur'-rég') != -1: lemmaFlexionTemplate = u''
                            if lemmaFlexionTemplate != u'':
                                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n){{fr\-rég\|[^}]*}}"
                                if re.search(regex, pageContent):
                                    pageContent = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}', pageContent)
                                    summary = summary + u', remplacement de {{' + language + ur'-rég}} par {{' + lemmaFlexionTemplate + ur'}}'
                            '''

                            if lemmaFlexionTemplate != u'':
                                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''')"
                                if re.search(regex, pageContent):
                                    pageContent = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}\n\2', pageContent)
                                    summary = summary + u', ajout de {{' + lemmaFlexionTemplate + ur'}} depuis le lemme'

                    if pageName[-1:] != 's':
                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)(\|" + language + ur"}}\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, pageContent):
                            #pageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=\7|\3}}\n\2\3\4\7', pageContent)
                            pageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + singularPageName + u'|\3}}\n\2\3\4\5', pageContent)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, pageContent):
                            pageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + singularPageName + u'|}}\n\2\5', pageContent)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

            if debugLevel > 1:  raw_input(pageContent.encode(config.console_encoding, 'replace'))

            if debugLevel > 1:  print u' en'
            if pageName[-2:] != 'ss' and pageName[-3:] != 'hes' and pageName[-3:] != 'ies' and pageName[-3:] != 'ses' and pageName[-3:] != 'ves':
                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)([s|z]\|en}}\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\1{{en-nom-rég|sing=\5|\3}}\n\2\3\4\5', pageContent)
                    summary = summary + u', ajout de {{en-nom-rég}}'

                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\1{{en-nom-rég|sing=\3|}}\n\2\3', pageContent)
                    summary = summary + u', ajout de {{en-nom-rég}}'

        if debugLevel > 0: print u' Missing translations'
        # Si la définition du mot (dit "satellite") ne renvoie pas vers un autre, les centralisant
        #TODO: # Variante,
        regex = ur'(fr\|flexion|' + u'|'.join(definitionSentences) + u'|' + u'|'.join(map(unicode.capitalize, 
            definitionSentences)) + ur')'
        regex2 = ur'{{(formater|SI|supp|supprimer|PàS|S\|erreur|S\|faute|S\|traductions|' + \
            u'|'.join(etymologyTemplatesInSatelliteWords) + ur')[\|}]'
        French, lStart, lEnd = getLanguageSection(pageContent, 'fr')
        if French is not None and re.search(regex, French) is None and re.search(regex2, French) is None and \
            countFirstDefinitionSize(French) > 3:
            summary = summary + u', ajout de {{S|traductions}}'
            pageContent = addLine(pageContent, u'fr', u'traductions', u'{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}')
        # Cosmetic hardfix
        regex = ur'(==== {{S\|traductions}} ====\n)\n* *\n*({{trad\-début)'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1\2', pageContent)
        regex = ur'({{trad\-fin}}\n)([^\n])'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1\n\2', pageContent)

        if debugLevel > 0: print (u' Languages in templates checking')
        addLanguageCode = False # Certaines sections interdisent les modèles de domaine catégorisant
        if debugLevel > 1: print '  addLanguageCode = ' + str(addLanguageCode)
        translationSection = False
        backward = False # Certains modèles nécessitent d'être déplacés puis retraités
        languageCode = None
        if debugLevel > 1: print u'  languageCode = None'
        startPosition = 1
        singularPageName = ''
        infinitive = ''
        # On sauvegarde la partie délimitée par "position" d'une page temporaire dans une page finale jusqu'à disparition de la première
        while startPosition > -1:
            if debugLevel > 1:
                pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
                print(finalPageContent.encode(config.console_encoding, 'replace')[:1000])
                raw_input(pageContent.encode(config.console_encoding, 'replace')[:1000])
                pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
            if debugLevel > 1:
                if languageCode is None:
                    print u'Boucle langue'
                else:
                    print u'Boucle langue : ' + languageCode

# Recherche de chaque modèle de la page
            startPosition = pageContent.find('{{')
            if startPosition < 0: break
            finalPageContent = finalPageContent + pageContent[:startPosition + 2]
            pageContent = pageContent[startPosition + 2:]
            if pageContent.find("|") > pageContent.find('}}'):
                endPosition = pageContent.find('}}')
            elif pageContent.find("|") == -1:
                endPosition = pageContent.find('}}')
            else:
                endPosition = pageContent.find("|")
            currentTemplate = pageContent[:endPosition]

            if not backward:
                if debugLevel > 1:
                    message = u' Remplacement de \x1b[6;31;40m{{' + pageContent[:pageContent.find('}}')+2] + u'\x1b[0m'
                    print(message.encode(config.console_encoding, 'replace'))
            else:
                if debugLevel > 1:
                    print(u' Retour en arrière')
                    pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
            backward = False

            if currentTemplate in Modele:
                p = Modele.index(currentTemplate)
                if debugLevel > 1: pywikibot.output(u'\nTemplate: \03{blue}' + currentTemplate + u'\03{default} (' + str(p) + u')')

                # Missing language section
                if not languageCode and (p < limit1 or p >= limit6) and currentTemplate != u'ébauche':
                    if debugLevel > 0: print u' Page to format manually'
                    finalPageContent = u'{{formater|Section de langue manquante, avant le modèle ' + currentTemplate + u' (au niveau du ' + str(len(finalPageContent)) + u'-ème caractère)}}\n' + finalPageContent + pageContent
                    summary = u'Page à formater manuellement'
                    savePage(page, finalPageContent, summary)
                    return

                elif currentTemplate == u'caractère':
                    languageCode = u'conv'
                    addLanguageCode = False
                    if debugLevel > 0: print ' addLanguageCode = ' + str(addLanguageCode)
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif currentTemplate == u'langue':
                    languageCode = pageContent[endPosition+1:pageContent.find('}}')]
                    if languageCode == u'':
                        if debugLevel > 0: print u'  empty language code'
                        return
                    if debugLevel > 1: print u'  language found: ' + languageCode
                    regex = ur'[a-zA-Z\-]+'
                    if not re.search(regex, languageCode):
                        finalPageContent = u'{{formater|Code langue incorrect : ' + languageCode + u'}}\n' + finalPageContent + pageContent
                        summary = u'Page à formater manuellement'
                        savePage(page, finalPageContent, summary)
                        if debugLevel > 0: print u' Page to format manually'
                        return
                    addLanguageCode = True

                    # Ajout des anagrammes pour cette nouvelle langue détectée
                    if languageCode == u'conv':
                        regex = ur'[= ]*{{S\|anagrammes}}[^}]+\|conv}}\n'
                        if re.compile(regex).search(pageContent):
                            if debugLevel > 0: print u' No anagram for {{conv}}'
                            finalPageContent2 = pageContent[:re.compile(regex).search(pageContent).start()]
                            pageContent2 = pageContent[re.compile(regex).search(pageContent).end():]
                            delta = re.compile(regex).search(pageContent).end()
                            regex = ur'[^}]+\|conv}}\n'
                            while re.compile(regex).search(pageContent2):
                                if debugLevel > 0: print u' No anagram for {{conv}}'
                                delta = delta + re.compile(regex).search(pageContent2).end()
                                pageContent2 = pageContent2[re.compile(regex).search(pageContent2).end():]
                            pageContent = finalPageContent2 + pageContent[delta:]

                    elif debugLevel == 0 and pageContent.find(u'S|erreur|' + languageCode) == -1 and pageContent.find(u'S|faute|' + languageCode) == -1 \
                     and languageCode != u'conv' and pageName[:1] != u'-' and pageName[-1:] != u'-' and not ':' in pageName:
                        if debugLevel > 0: print u' Anagrams for ' + languageCode
                        if pageContent.find(u'{{S|anagr') == -1 and pageName.find(u' ') == -1 and len(pageName) <= anagramsMaxLength:
                            anagrams = anagram(pageName)
                            ListeAnagrammes = u''
                            for anagramme in anagrams:
                                if anagramme != pageName:
                                    if debugLevel > 0: print u' ' + anagramme.encode(config.console_encoding, 'replace')
                                    pageAnagr = Page(site,anagramme)
                                    if pageAnagr.exists():
                                        if pageAnagr.namespace() !=0 and anagramme != u'User:JackBot/test':
                                            break
                                        else:
                                            pageContentAnagr = getContentFromPage(pageAnagr)
                                            if pageContentAnagr == 'KO': break
                                        if pageContentAnagr.find(u'{{langue|' + languageCode + '}}') != -1:
                                            ListeAnagrammes = ListeAnagrammes + u'* {{lien|' + anagramme + u'|' + languageCode + u'}}\n'
                                            if debugLevel > 0: print u' trouvé'
                            if ListeAnagrammes != u'':
                                summary = summary + u', ajout d\'anagrammes ' + languageCode
                                positionAnagr = pageContent.find(u'{{langue|' + languageCode + '}}')+len(u'{{langue|' + languageCode + '}}')
                                pageContent2 = pageContent[positionAnagr:len(pageContent)]
                                if pageContent2.find(u'\n=== {{S|voir') != -1 and ((pageContent2.find(u'{{langue|') != -1 and pageContent2.find(u'{{S|voir') < pageContent2.find(u'{{langue|')) or pageContent2.find(u'{{langue|') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'\n=== {{S|voir')] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'\n=== {{S|voir'):]
                                elif pageContent2.find(u'\n=== {{S|références}}') != -1 and ((pageContent2.find(u'{{langue|') != -1 and pageContent2.find(u'\n=== {{S|références}}') < pageContent2.find(u'{{langue|')) or pageContent2.find(u'{{langue|') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'\n=== {{S|références}}')] +  u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'\n=== {{S|références}}'):]
                                elif pageContent2.find(u'== {{langue|') != -1 and ((pageContent2.find(u'[[Catégorie:') != -1 and pageContent2.find(u'== {{langue|') < pageContent2.find(u'[[Catégorie:')) or pageContent2.find(u'[[Catégorie:') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'== {{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'== {{langue|'):]
                                elif pageContent2.find(u'=={{langue|') != -1 and ((pageContent2.find(u'[[Catégorie:') != -1 and pageContent2.find(u'=={{langue|') < pageContent2.find(u'[[Catégorie:')) or pageContent2.find(u'[[Catégorie:') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'=={{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'=={{langue|'):]        
                                elif pageContent2.find(u'{{clé de tri') != -1:
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'{{clé de tri')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'{{clé de tri'):]
                                elif pageContent2.find(u'[[Catégorie:') != -1:
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'[[Catégorie:')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'[[Catégorie:'):]
                                else:
                                    if debugLevel > 0: print " Ajout avant les interwikis"
                                    regex = ur'\n\[\[\w?\w?\w?:'
                                    if re.compile(regex).search(pageContent):
                                        try:
                                            pageContent = pageContent[:re.search(regex, pageContent).start()] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[re.search(regex, pageContent).start():]
                                        except:
                                            if debugLevel > 0: print u'pb regex interwiki'
                                    else:
                                        pageContent = pageContent + u'\n\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

# Sections
                elif currentTemplate == u'S':
                    section = trim(pageContent[endPosition+1:pageContent.find('}}')])
                    if section.find(u'|') != -1: section = trim(section[:section.find(u'|')])
                    if not section in Section:
                        if debugLevel > 0: print u' Unknown section: ' + section
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                        break
                    if debugLevel > 0: print u' Known section: ' + section

                    if Section.index(section) < limit1:
                        if debugLevel > 1: print u' Definition paragraph'
                        addLanguageCode = True # Paragraphe avec code langue dans les modèles lexicaux
                        translationSection = False

                        if languageCode is None:
                            # TODO: gérer les {{S|étymologie}} en milieu d'article
                            languageCode = pageContent[endPosition+1+len(section)+1:pageContent.find('}}')].replace(u'|flexion', u'') #TODO: num=, genre=...
                            summary = summary + u' ajout du {{langue|' + languageCode + u'}} manquant'
                            pageContent = '== {{langue|' + languageCode + u'}} ==\n' + finalPageContent[finalPageContent.find('==='):] + pageContent
                            finalPageContent = finalPageContent[:finalPageContent.find('===')]
                            backward = True
                            break

                        if pageContent.find(languageCode) == -1 or pageContent.find(languageCode) > pageContent.find('}}'):
                            pageContent = pageContent[:endPosition+1+len(section)] + u'|' + languageCode + pageContent[pageContent.find('}}'):]

                        # Tous ces modèles peuvent facultativement contenir |clé= et |num=, et |genre= pour les prénoms, voire locution=
                        if (pageContent.find(u'|clé=') == -1 or pageContent.find(u'|clé=') > pageContent.find('}}')):
                            if debugLevel > 1: print u'  ' + str(p)                                                                     # eg: 0 for {{S}}
                            if debugLevel > 1: print u'  ' + str(Section.index(section))                                                # eg: 40 for "nom"
                            if debugLevel > 1: print u'  ' + pageContent[:pageContent.find('}}')].encode(config.console_encoding, 'replace') # eg: S|nom|sv|flexion

                            tempPageName = defaultSortByLanguage(pageName, languageCode)
                            if tempPageName != pageName:
                                if debugLevel > 0: print u' "|clé="'
                                tempPageName = defaultSort(tempPageName)
                                pageContent = pageContent[:pageContent.find('}}')] + u'|clé=' + tempPageName + pageContent[pageContent.find('}}'):]
                            
                    else:
                        addLanguageCode = False # Paragraphe sans code langue dans les modèles lexicaux et les titres
                        translationSection = False

                        if section == u'homophones':
                            if debugLevel > 0: print ' Homophons categorization'
                            sectionTitle = pageContent[:pageContent.find('}}')]
                            if sectionTitle.rfind('|') > len(section):
                                pageContent = sectionTitle[:sectionTitle.rfind('|')] + u'|' + languageCode + pageContent[pageContent.find('}}'):]
                            else:
                                pageContent = pageContent[:pageContent.find('}}')] + u'|' + languageCode + pageContent[pageContent.find('}}'):]

                        if section == 'traductions' and languageCode == 'fr':
                            translationSection = True
                            regex = ur'{{S\|traductions}} *=*\n(\n|\:?\*? *({{cf|[Vv]oir))'
                            if not re.search(regex, pageContent):
                                # Ajout de {{trad-début}} si {{T| en français (mais pas {{L| car certains les trient par famille de langue)
                                for t in [u'T', u'ébauche-trad']:
                                    if pageContent.find('{{') == pageContent.find(u'{{' + t + u'|'):
                                        if debugLevel > 0: print u'  {{trad-début}} addition'
                                        if pageContent.find(u'\n') == -1: pageContent = pageContent + u'\n'
                                        pageContent = pageContent[:pageContent.find(u'\n')] + u'\n{{trad-début}}' + pageContent[pageContent.find(u'\n'):]
                                        pageContent2 = pageContent[pageContent.find(u'{{trad-début}}\n')+len(u'{{trad-début}}\n'):]
                                        while pageContent2.find(u'{{' + t + u'|') < pageContent2.find(u'\n') and pageContent2.find(u'{{' + t + u'|') != -1:
                                            pageContent2 = pageContent2[pageContent2.find(u'\n')+1:]
                                        if debugLevel > 0: print u'  {{trad-fin}} addition'
                                        pageContent = pageContent[:len(pageContent)-len(pageContent2)] + u'{{trad-fin}}\n' + pageContent[len(pageContent)-len(pageContent2):]
                            if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace')) 
                        elif section == u'traductions à trier':
                            translationSection = True

                    if debugLevel > 1: print '  addLanguageCode = ' + str(addLanguageCode)
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif currentTemplate in [u'term', u'région']:
                    
                    rawTerm = pageContent[endPosition+1:pageContent.find('}}')]
                    term = trim(rawTerm.replace('[[', '').replace(']]', ''))
                    if term.find('|') != -1: term = trim(term[:term.find('|')])
                    if debugLevel > 0: print u' terminologie ou régionalisme'
                    if term == u'':
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                    else:
                        if debugLevel > 0: print "  1 = " + term
                        templatePage = getContentFromPageName(u'Template:' + term, allowedNamespaces = [u'Template:'])
                        if templatePage.find(u'Catégorie:Modèles de domaine') == -1 and templatePage.find(u'{{région|') == -1 and term[:1] != term[:1].lower():
                            term = term[:1].lower() + term[1:]
                            if debugLevel > 0: print u'  2 = ' + term
                            templatePage = getContentFromPageName(u'Template:' + term, allowedNamespaces = [u'Template:'])
                        if templatePage.find(u'Catégorie:Modèles de domaine') != -1 or templatePage.find(u'{{région|') != -1:
                            if debugLevel > 0: print u'  substitution par le modèle existant'
                            pageContent = '{{' + term + pageContent[endPosition+1+len(rawTerm):]
                            finalPageContent = finalPageContent[:-2]
                            backward = True
                        else:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

# Templates with language code at second
                elif currentTemplate in definitionTemplates + etymologyTemplatesWithLanguageAtSecond + [u'pron', u'phon']: # u'lien'
                    if languageCode != u'conv':
                        if debugLevel > 0: pywikibot.output(u"  Template with language code at second: \03{green}" + currentTemplate+ u"\03{default}")
                        # Tri des lettres de l'API
                        if currentTemplate == u'pron':
                            pageContent2 = pageContent[endPosition+1:pageContent.find('}}')]
                            while pageContent2.find(u'\'') != -1 and pageContent2.find(u'\'') < pageContent2.find('}}') \
                                and (pageContent2.find(u'\'') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1):
                                pageContent = pageContent[:pageContent.find(u'\'')] + u'ˈ' + pageContent[pageContent.find(u'\'')+1:]
                            while pageContent2.find(u'ˈˈˈ') != -1 and pageContent2.find(u'ˈˈˈ') < pageContent2.find('}}') \
                                and (pageContent2.find(u'ˈˈˈ') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1):
                                pageContent = pageContent[:pageContent.find(u'ˈˈˈ')] + u'\'\'\'' + pageContent[pageContent.find(u'ˈˈˈ')+3:]
                            while pageContent2.find(u'ε') != -1 and pageContent2.find(u'ε') < pageContent2.find('}}') \
                                and (pageContent2.find(u'ε') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1):
                                pageContent = pageContent[:pageContent.find(u'ε')] + u'ɛ' + pageContent[pageContent.find(u'ε')+1:]
                            while pageContent2.find(u'ε̃') != -1 and pageContent2.find(u'ε̃') < pageContent2.find('}}') \
                                and (pageContent2.find(u'ε̃') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1):
                                pageContent = pageContent[:pageContent.find(u'ε̃')] + u'ɛ̃' + pageContent[pageContent.find(u'ε̃')+1:]
                            while pageContent2.find(u':') != -1 and pageContent2.find(u':') < pageContent2.find('}}') \
                                and (pageContent2.find(u':') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1):
                                pageContent = pageContent[:pageContent.find(u':')] + u'ː' + pageContent[pageContent.find(u':')+1:]
                            while pageContent2.find(u'g') != -1 and pageContent2.find(u'g') < pageContent2.find('}}') \
                                and (pageContent2.find(u'g') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1) \
                                and pageContent2.find(u'g') != pageContent2.find(u'lang=')+3:
                                pageContent = pageContent[:pageContent.find(u'g')] + u'ɡ' + pageContent[pageContent.find(u'g')+1:]

                            #if languageCode == u'es': β/, /ð/ et /ɣ/ au lieu de de /b/, /d/ et /ɡ/
                        if pageContent[:8] == u'pron||}}':
                            finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')] + languageCode + '}}'
                        elif pageContent[endPosition:endPosition+3] == u'|}}' or pageContent[endPosition:endPosition+4] == u'| }}':
                            finalPageContent = finalPageContent + currentTemplate + "||" + languageCode + '}}'
                        elif (pageContent.find("lang=") != -1 and pageContent.find("lang=") < pageContent.find('}}')):
                            finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2]
                        elif endPosition == pageContent.find(u'|'):
                            pageContent2 = pageContent[endPosition+1:pageContent.find('}}')]
                            if pageContent2.find(u'|') == -1:
                                finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')] + "|" + languageCode + '}}'
                            else:
                                finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2]
                        elif endPosition == pageContent.find('}}'):
                            finalPageContent = finalPageContent + currentTemplate + "||" + languageCode + '}}'
                        else:
                            finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')] + "|" + languageCode + '}}'
                        pageContent = pageContent[pageContent.find('}}')+2:]
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

# Templates with "lang="
                elif currentTemplate in [u'écouter', u'cf'] + etymologyTemplatesWithLanguageAtLang:
                    finalPageContent, pageContent = addLanguageCodeWithNamedParameterToTemplate(
                        finalPageContent,
                        pageContent,
                        currentTemplate,
                        languageCode,
                        endPosition
                    )

                elif currentTemplate in (u'référence nécessaire', u'réf?', u'réf ?', u'refnec', u'réfnéc', u'source?', \
                    u'réfnéc'):
                    pageContent2 = pageContent[endPosition+1:]
                    #TODO regex = ur'lang *= *'
                    if pageContent2.find(u'lang=') == -1 or pageContent2.find(u'lang=') > pageContent2.find('}}'):
                        finalPageContent = finalPageContent + currentTemplate + u'|lang=' + languageCode + \
                            pageContent[endPosition:pageContent.find('}}')+2]
                        pageContent = pageContent[pageContent.find('}}')+2:]
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

# Wrong genders
                elif currentTemplate in (u'm', u'f'):
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko'):
                        finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2]
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        finalPageContent = finalPageContent[:-2]
                        backward = True
                    pageContent = pageContent[pageContent.find('}}')+2:]
                elif currentTemplate in (u'mf', u'mf?'):
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko'):
                        finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2]
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        finalPageContent = finalPageContent[:-2]
                        backward = True
                    pageContent = pageContent[pageContent.find('}}')+2:]
                elif currentTemplate in (u'n', u'c'):
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko' and languageCode != u'fr'):
                        finalPageContent = finalPageContent + currentTemplate + '}}'
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        finalPageContent = finalPageContent[:-2]
                        backward = True
                    pageContent = pageContent[pageContent.find('}}')+2:]

# Templates with language code at first
                elif currentTemplate in (u'perfectif', u'perf', u'imperfectif', u'imperf', u'déterminé', u'dét', \
                    u'indéterminé', u'indét'):
                    if (not addLanguageCode) or finalPageContent.rfind(u'(') > finalPageContent.rfind(u')'): # Si on est dans des parenthèses
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, 'nocat=1')
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, languageCode)

# Templates with two parameters
                elif currentTemplate in (u'conjugaison', u'conj', u'1ergroupe', u'2egroupe', u'3egroupe'):
                    if currentTemplate == u'1ergroupe':
                        pageContent = u'|grp=1' + pageContent[len(u'1ergroupe'):]
                        finalPageContent = finalPageContent + u'conj'
                    elif currentTemplate == u'2egroupe':
                        pageContent = u'|grp=2' + pageContent[len(u'2egroupe'):]
                        finalPageContent = finalPageContent + u'conj'
                    elif currentTemplate == u'3egroupe':
                        pageContent = u'|grp=3' + pageContent[len(u'3egroupe'):]
                        finalPageContent = finalPageContent + u'conj'
                    elif currentTemplate == u'conjugaison':
                        pageContent = pageContent[len(u'conjugaison'):]
                        finalPageContent = finalPageContent + u'conjugaison'
                    elif currentTemplate == u'conj':
                        pageContent = pageContent[len(u'conj'):]
                        finalPageContent = finalPageContent + u'conj'
                    # Vérification des groupes en espagnol, portugais et italien
                    if languageCode == u'es':
                        if pageName[len(pageName)-2:] == u'ar' or pageName[len(pageName)-4:] == u'arsi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=1' + pageContent
                        elif pageName[len(pageName)-2:] == u'er' or pageName[len(pageName)-4:] == u'ersi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=2' + pageContent
                        elif pageName[len(pageName)-2:] == u'ir' or pageName[len(pageName)-4:] == u'irsi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=3' + pageContent

                    elif languageCode == u'pt':
                        if pageName[len(pageName)-2:] == u'ar' or pageName[len(pageName)-4:] == u'ar-se':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=1' + pageContent
                        elif pageName[len(pageName)-2:] == u'er' or pageName[len(pageName)-4:] == u'er-se':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=2' + pageContent
                        elif pageName[len(pageName)-2:] == u'ir' or pageName[len(pageName)-4:] == u'ir-se':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=3' + pageContent

                    elif languageCode == u'it':
                        if pageName[len(pageName)-3:] == u'are' or pageName[len(pageName)-4:] == u'arsi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'1' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'1' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=1' + pageContent
                        elif pageName[len(pageName)-3:] == u'ere' or pageName[len(pageName)-4:] == u'ersi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'2' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'2' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=2' + pageContent
                        elif pageName[len(pageName)-3:] == u'ire' or pageName[len(pageName)-4:] == u'irsi':
                            if (pageContent.find(u'grp=') != -1 and pageContent.find(u'grp=') < pageContent.find('}}')):
                                if pageContent.find(u'|grp=') == pageContent.find(u'|grp=}') or pageContent.find(u'|grp=') == pageContent.find(u'|grp=|'):
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|grp=')+len(u'|grp=')] + u'3' + pageContent[pageContent.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (pageContent.find(u'groupe=') != -1 and pageContent.find(u'groupe=') < pageContent.find('}}')):
                                if pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=}') or pageContent.find(u'|groupe=') == pageContent.find(u'|groupe=|'):
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    pageContent = pageContent[:pageContent.find(u'|groupe=')+len(u'|groupe=')] + u'3' + pageContent[pageContent.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                pageContent = u'|groupe=3' + pageContent

                    if (pageContent.find(languageCode) != -1 and pageContent.find(languageCode) < pageContent.find('}}')) or languageCode == u'fr':
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                    else:
                        if pageContent.find(u'|nocat=1') != -1:
                            pageContent = pageContent[:pageContent.find(u'|nocat=1')] + pageContent[pageContent.find(u'|nocat=1')+len(u'|nocat=1'):]
                        finalPageContent = finalPageContent + u'|' + languageCode + '}}'
                        pageContent = pageContent[pageContent.find('}}')+2:]

                elif currentTemplate == u'trad' or currentTemplate == u'trad+' or currentTemplate == u'trad-' or currentTemplate == u'trad--':
                    if endPosition == pageContent.find('}}') or endPosition == pageContent.find(u'--}}')-2 or endPosition == pageContent.find(u'|en|}}')-4:
                        finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2]
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                    else:
                        # Lettres spéciales à remplacer dans les traductions vers certaines langues
                        pageContent2 = pageContent[endPosition+1:]
                        currentLanguage = pageContent2[:pageContent2.find(u'|')]
                        if currentLanguage == u'ro' or currentLanguage == u'mo':
                            while pageContent.find(u'ş') != -1 and pageContent.find(u'ş') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'ş')] + u'ș' + pageContent[pageContent.find(u'ş')+1:]
                            while pageContent.find(u'Ş') != -1 and pageContent.find(u'Ş') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'Ş')] + u'Ș' + pageContent[pageContent.find(u'Ş')+1:]
                            while pageContent.find(u'ţ') != -1 and pageContent.find(u'ţ') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'ţ')] + u'ț' + pageContent[pageContent.find(u'ţ')+1:]
                            while pageContent.find(u'Ţ') != -1 and pageContent.find(u'Ţ') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'Ţ')] + u'Ț' + pageContent[pageContent.find(u'Ţ')+1:]
                        elif currentLanguage == u'az' or currentLanguage == u'ku' or currentLanguage == u'sq' or currentLanguage == u'tk' or currentLanguage == u'tr' or currentLanguage == u'tt':
                            while pageContent.find(u'ș') != -1 and pageContent.find(u'ș') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'ș')] + u'ş' + pageContent[pageContent.find(u'ș')+1:]
                            while pageContent.find(u'Ș') != -1 and pageContent.find(u'Ș') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'Ș')] + u'Ş' + pageContent[pageContent.find(u'Ș')+1:]
                            while pageContent.find(u'ț') != -1 and pageContent.find(u'ț') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'ț')] + u'ţ' + pageContent[pageContent.find(u'ț')+1:]
                            while pageContent.find(u'Ț') != -1 and pageContent.find(u'Ț') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'Ț')] + u'Ţ' + pageContent[pageContent.find(u'Ț')+1:]
                        elif currentLanguage == u'fon':
                            while pageContent.find(u'ε') != -1 and pageContent.find(u'ε') < pageContent.find(u'\n'):
                                pageContent = pageContent[:pageContent.find(u'ε')] + u'ɛ' + pageContent[pageContent.find(u'ε')+1:]
                        # http://fr.wiktionary.org/wiki/Mod%C3%A8le:code_interwiki
                        elif currentLanguage == u'cmn':
                            pageContent = pageContent[:pageContent.find(u'cmn')] + u'zh' + pageContent[pageContent.find(u'cmn')+len(u'cmn'):]
                        elif currentLanguage == u'nn':
                            pageContent = pageContent[:pageContent.find(u'nn')] + u'no' + pageContent[pageContent.find(u'nn')+len(u'nn'):]
                        elif currentLanguage == u'per':
                            pageContent = pageContent[:pageContent.find(u'per')] + u'fa' + pageContent[pageContent.find(u'per')+len(u'per'):]
                        elif currentLanguage == u'wel':
                            pageContent = pageContent[:pageContent.find(u'wel')] + u'cy' + pageContent[pageContent.find(u'wel')+len(u'wel'):]
                        elif currentLanguage == u'zh-classical':
                            pageContent = pageContent[:pageContent.find(u'zh-classical')] + u'lzh' + pageContent[pageContent.find(u'zh-classical')+len(u'zh-classical'):]
                        elif currentLanguage == u'ko-Hani':
                            pageContent = pageContent[:pageContent.find(u'ko-Hani')] + u'ko' + pageContent[pageContent.find(u'ko-Hani')+len(u'ko-Hani'):]
                        elif currentLanguage == u'ko-hanja':
                            pageContent = pageContent[:pageContent.find(u'ko-hanja')] + u'ko' + pageContent[pageContent.find(u'ko-hanja')+len(u'ko-hanja'):]
                        elif currentLanguage == u'zh-min-nan':
                            pageContent = pageContent[:pageContent.find(u'zh-min-nan')] + u'nan' + pageContent[pageContent.find(u'zh-min-nan')+len(u'zh-min-nan'):]
                        elif currentLanguage == u'roa-rup':
                            pageContent = pageContent[:pageContent.find(u'roa-rup')] + u'rup' + pageContent[pageContent.find(u'roa-rup')+len(u'roa-rup'):]
                        elif currentLanguage == u'zh-yue':
                            pageContent = pageContent[:pageContent.find(u'zh-yue')] + u'yue' + pageContent[pageContent.find(u'zh-yue')+len(u'zh-yue'):]
                        pageContent2 = pageContent[endPosition+1:]
                        currentLanguage = pageContent2[:pageContent2.find(u'|')]

                        if currentLanguage != '': #TODO: reproduire le bug du site fermé, ex : https://fr.wiktionary.org/w/index.php?title=chat&diff=prev&oldid=9366302
                            # Identification des Wiktionnaires hébergeant les traductions
                            siteExterne = u''
                            pageExterne = u''
                            d = 0
                            pageContent3 = pageContent2[pageContent2.find(u'|')+1:]
                            if debugLevel > d: print u' langue distante : ' + currentLanguage
                            if pageContent3.find('}}') == "" or not pageContent3.find('}}'):
                                if debugLevel > d: print u'  aucun mot distant'
                                if finalPageContent.rfind('<!--') == -1 or finalPageContent.rfind('<!--') < finalPageContent.rfind('-->'):
                                    # On retire le modèle pour que la page ne soit plus en catégorie de maintenance
                                    if debugLevel > d: print u' Retrait de commentaire de traduction l 4362'
                                    finalPageContent = finalPageContent[:-2]
                                    backward = True
                            elif currentLanguage == u'conv':
                                siteExterne = getWiki('species', 'species')
                            else:
                                siteExterne = getWiki(currentLanguage, siteFamily)
                            if siteExterne == 'KO':
                                if debugLevel > d: print u'  no site (--)'
                                finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '--')
                                siteExterne = ''
                            elif siteExterne != u'':
                                if pageContent3.find(u'|') != -1 and pageContent3.find(u'|') < pageContent3.find('}}'):
                                    pageExterne = pageContent3[:pageContent3.find(u'|')]
                                else:
                                    pageExterne = pageContent3[:pageContent3.find('}}')]
                            if pageExterne != u'' and pageExterne.find(u'<') != -1:
                                pageExterne = pageExterne[:pageExterne.find(u'<')]
                            if debugLevel > d:
                                print u' page distante : ' + pageExterne

                            # Connexions aux Wiktionnaires pour vérifier la présence de la page (TODO: et de sa section langue)
                            if siteExterne != u'' and pageExterne != u'':
                                pageFound = True
                                try:
                                    PageExt = Page(siteExterne, pageExterne)
                                except pywikibot.exceptions.BadTitle:
                                    if debugLevel > d: print u'  BadTitle (-)'
                                    finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '-')
                                    pageFound = False
                                except pywikibot.exceptions.InvalidTitle:
                                    if debugLevel > d: print u'  InvalidTitle (-)'
                                    finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '-')
                                    pageFound = False
                                except pywikibot.exceptions.NoPage:
                                    if debugLevel > d: print u'  NoPage'
                                    if pageExterne.find(u'\'') != -1:
                                        pageExterne = pageExterne.replace(u'\'', u'’')
                                    elif pageExterne.find(u'’') != -1:
                                        pageExterne = pageExterne.replace(u'’', u'\'')
                                    if pageExterne != PageExt.title():
                                        try:
                                            PageExt = Page(siteExterne, pageExterne)
                                        except pywikibot.exceptions.NoPage:
                                            finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '-')
                                            pageFound = False
                                if pageFound:
                                    pageExtExists = True
                                    try:
                                        pageExtExists = PageExt.exists()
                                    except AttributeError:
                                        if debugLevel > d: print u'  removed site (--)'
                                        finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '--')
                                        pageExtExists = False
                                    except pywikibot.exceptions.InconsistentTitleReceived:
                                        if debugLevel > d: print u'  InconsistentTitleReceived (-)'
                                        finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '-')
                                        pageExtExists = False

                                    if pageExtExists:
                                        if debugLevel > d: print u'  exists (+)'
                                        finalPageContent, pageContent = nextTranslationTemplate(finalPageContent, pageContent, '+')

                elif currentTemplate == u'(':
                    if translationSection:
                        finalPageContent = finalPageContent + u'trad-début'
                    else:
                        finalPageContent = finalPageContent + u'('
                    pageContent = pageContent[len(currentTemplate):]
                elif currentTemplate == u')':
                    if translationSection:
                        finalPageContent = finalPageContent + u'trad-fin'
                    else:
                        finalPageContent = finalPageContent + u')'
                    pageContent = pageContent[len(currentTemplate):]
                elif currentTemplate == u'trad-début':
                    if translationSection:
                        finalPageContent = finalPageContent + u'trad-début'
                    else:
                        finalPageContent = finalPageContent + u'('
                    pageContent = pageContent[len(currentTemplate):]
                elif currentTemplate == u'trad-fin':
                    if translationSection:
                        finalPageContent = finalPageContent + u'trad-fin'
                    else:
                        finalPageContent = finalPageContent + u')'
                    pageContent = pageContent[len(currentTemplate):]

                elif currentTemplate == u'fr-verbe-flexion':
                    if debugLevel > 0: print u'Flexion de verbe'
                    infinitive = getLemmaFromConjugation(currentPageContent)
                    if infinitive != u'':
                        infinitivePage = getContentFromPageName(infinitive)
                        if infinitivePage != 'KO':
                            # http://fr.wiktionary.org/w/index.php?title=Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet
                            pageContent2 = pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):]
                            if pageContent2.find(u'flexion=') != -1 and pageContent2.find(u'flexion=') < pageContent2.find('}}'):
                                pageContent3 = pageContent2[pageContent2.find(u'flexion='):len(pageContent2)]
                                if pageContent3.find(u'|') != -1 and pageContent3.find(u'|') < pageContent3.find(u'}'):
                                    pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')+pageContent2.find(u'flexion=')+pageContent3.find(u'|'):len(pageContent)]
                            pageContent2 = pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                            if pageContent2.find(infinitive) == -1 or pageContent2.find(infinitive) > pageContent2.find('}}'):
                                pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|' + infinitive + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                if pageContent.find(u'|' + infinitive + u'\n') != -1:    # Bug de l'hyperlien vers l'annexe
                                    pageContent = pageContent[:pageContent.find(u'|' + infinitive + u'\n')+len(u'|' + infinitive)] + pageContent[pageContent.find(u'|' + infinitive + u'\n')+len(u'|' + infinitive + u'\n'):len(pageContent)]
                            # Analyse du modèle en cours
                            pageContent2 = pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):]
                            pageContent2 = pageContent2[:pageContent2.find('}}')+2]
                            if pageContent2.find(u'impers=oui') == -1:
                                # http://fr.wiktionary.org/w/index.php?title=Modèle:fr-verbe-flexion&action=edit
                                French, lStart, lEnd = getLanguageSection(infinitivePage, 'fr')
                                if infinitivePage.find(u'{{impers|fr}}') != -1 or (infinitivePage.find(u'{{impersonnel|fr}}') != -1 and French is not None and countDefinitions(French) == 1):
                                    pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|impers=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):]
                                elif (infinitivePage.find(u'|groupe=1') != -1 or infinitivePage.find(u'|grp=1') != -1) and infinitivePage.find(u'|groupe2=') == -1:
                                    # je
                                    if pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pass
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|sub.p.3s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui' + pageContent[pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|imp.p.2s=oui|ind.p.1s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|ind.p.3s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui|sub.p.1s=oui|ind.p.3s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # tu
                                    if pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'sub.p.2s=oui') != -1:
                                        pass
                                    elif pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'sub.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|sub.p.2s=oui' + pageContent[pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.2s=oui') == -1 and pageContent2.find(u'sub.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # nous
                                    if pageContent2.find(u'ind.i.1p=oui') != -1 and pageContent2.find(u'sub.p.1p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.i.1p=oui') != -1 and pageContent2.find(u'sub.p.1p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + pageContent[pageContent.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.i.1p=oui') == -1 and pageContent2.find(u'sub.p.1p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # vous
                                    if pageContent2.find(u'ind.i.2p=oui') != -1 and pageContent2.find(u'sub.p.2p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.i.2p=oui') != -1 and pageContent2.find(u'sub.p.2p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + pageContent[pageContent.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.i.2p=oui') == -1 and pageContent2.find(u'sub.p.2p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # ils
                                    if pageContent2.find(u'ind.p.3p=oui') != -1 and pageContent2.find(u'sub.p.3p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.p.3p=oui') != -1 and pageContent2.find(u'sub.p.3p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + pageContent[pageContent.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.p.3p=oui') == -1 and pageContent2.find(u'sub.p.3p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                # Certains -ir sont du 3ème
                                elif (infinitivePage.find(u'|groupe=2') != -1 or infinitivePage.find(u'|grp=2') != -1) and infinitivePage.find(u'{{impers') == -1 and infinitivePage.find(u'|groupe2=') == -1:
                                    # je
                                    if pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pass
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui')] + u'|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui' + pageContent[pageContent.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui' + pageContent[pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') == -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') != -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') != -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') == -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.2s=oui') == -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]

                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui' + pageContent[pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') != -1 and pageContent2.find(u'ind.p.2s=oui') == -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + pageContent[pageContent.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'ind.p.1s=oui') == -1 and pageContent2.find(u'ind.p.2s=oui') != -1 and pageContent2.find(u'ind.ps.1s=oui') == -1 and pageContent2.find(u'ind.ps.2s=oui') == -1 and pageContent2.find(u'imp.p.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.p.1s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + pageContent[pageContent.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(pageContent)]

                                    #...
                                    if pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'sub.i.1s=oui') != -1:
                                        pass
                                    elif pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'sub.i.1s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui')] + u'|sub.i.1s=oui' + pageContent[pageContent.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'sub.i.1s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui' + pageContent[pageContent.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'sub.i.1s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'sub.p.1s=oui') != -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'sub.i.1s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui|sub.i.1s=oui' + pageContent[pageContent.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(pageContent)]
                                    elif pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') == -1 and pageContent2.find(u'sub.i.1s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.p.3s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    elif pageContent2.find(u'sub.p.1s=oui') == -1 and pageContent2.find(u'sub.p.3s=oui') != -1 and pageContent2.find(u'sub.i.1s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.i.1s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # tu
                                    if pageContent2.find(u'sub.p.2s=oui') != -1 and pageContent2.find(u'sub.i.2s=oui') != -1:
                                        pass
                                    if pageContent2.find(u'sub.p.2s=oui') != -1 and pageContent2.find(u'sub.i.2s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui')] + u'|sub.i.2s=oui' + pageContent[pageContent.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui'):len(pageContent)]
                                    if pageContent2.find(u'sub.p.2s=oui') == -1 and pageContent2.find(u'sub.i.2s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.2s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # il
                                    if pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'ind.ps.3s=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.p.3s=oui') != -1 and pageContent2.find(u'ind.ps.3s=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|ind.ps.3s=oui' + pageContent[pageContent.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.p.3s=oui') == -1 and pageContent2.find(u'ind.ps.3s=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # nous
                                    if pageContent2.find(u'ind.i.1p=oui') != -1 and pageContent2.find(u'sub.p.1p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.i.1p=oui') != -1 and pageContent2.find(u'sub.p.1p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + pageContent[pageContent.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.i.1p=oui') == -1 and pageContent2.find(u'sub.p.1p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # vous
                                    if pageContent2.find(u'ind.i.2p=oui') != -1 and pageContent2.find(u'sub.p.2p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.i.2p=oui') != -1 and pageContent2.find(u'sub.p.2p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + pageContent[pageContent.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.i.2p=oui') == -1 and pageContent2.find(u'sub.p.2p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                    # ils
                                    if pageContent2.find(u'ind.p.3p=oui') != -1 and pageContent2.find(u'sub.p.3p=oui') != -1:
                                        pass
                                    if pageContent2.find(u'ind.p.3p=oui') != -1 and pageContent2.find(u'sub.p.3p=oui') == -1:
                                        pageContent = pageContent[:pageContent.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + pageContent[pageContent.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(pageContent)]
                                    if pageContent2.find(u'ind.p.3p=oui') == -1 and pageContent2.find(u'sub.p.3p=oui') != -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(pageContent)]
                                elif (infinitivePage.find(u'|groupe=3') != -1 or infinitivePage.find(u'|grp=3') != -1) and infinitivePage.find(u'|groupe2=') == -1:
                                    if pageContent2.find(u'grp=3') == -1:
                                        pageContent = pageContent[:pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|grp=3' + pageContent[pageContent.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):]

                    finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n')+1]
                    pageContent = pageContent[pageContent.find(u'\n')+1:]

                elif p < limit5:
                    if debugLevel > 0: print u' limit5 : paragraphe sans code langue contenant un texte'
                    addLanguageCode = False
                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    #trad = False
                    if pageContent.find('}}') > pageContent.find('{{') and pageContent.find('{{') != -1:
                        pageContent2 = pageContent[pageContent.find('}}')+2:]
                        finalPageContent = finalPageContent + pageContent[:pageContent.find('}}')+2+pageContent2.find('}}')+2]
                        pageContent = pageContent[pageContent.find('}}')+2+pageContent2.find('}}')+2:]
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif p < limit6:
                    if debugLevel > 0: print u' limit6 : modèle sans paramètre'
                    finalPageContent = finalPageContent + currentTemplate + '}}'
                    pageContent = pageContent[pageContent.find('}}')+2:]

                elif p < limit7:
                    if debugLevel > 0: print u' limit7 : paragraphe potentiellement avec code langue, voire |spéc='
                    if currentTemplate == pageContent[:pageContent.find('}}')]:
                        if addLanguageCode:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, languageCode)
                        else:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, 'nocat=1')
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif p < limit8:
                    if debugLevel > 0: print u' limit8 : modèle catégorisé quel que soit addLanguageCode (ex : ébauches)'
                    if currentTemplate == u'ébauche' and not languageCode and pageContent.find(u'== {{langue') != -1:
                        if debugLevel > 0: print u'  déplacement du 1e {{ébauche}} pour être traité après détermination de la langue'
                        nextSection = u'{{caractère}}'
                        if pageContent.find(nextSection) == -1:
                            nextSection = u'{{langue|'
                        pageContent2 = pageContent[pageContent.find(nextSection):]
                        pageContent = pageContent[pageContent.find('}}')+2:pageContent.find(nextSection)+pageContent2.find(u'\n')+1] \
                         + u'{{ébauche}}\n' + pageContent[pageContent.find(nextSection)+pageContent2.find(u'\n')+1:]
                        finalPageContent = finalPageContent[:-2]
                        backward = True
                    elif languageCode:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, languageCode)
                    else:
                       finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, 'nocat=1')

                elif p < limit9:
                    if debugLevel > 0: print u' limit9 : modèle catégorisé dans les étymologies'
                    if currentTemplate == pageContent[:pageContent.find('}}')]:
                        if addLanguageCode or section == u'étymologie':
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, languageCode)
                        else:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, 'nocat=1')
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                else:
                    if debugLevel > 0: print u' Modèle régional : non catégorisé dans la prononciation'
                    if finalPageContent.rfind('{{') != -1:
                        finalPageContent2 = finalPageContent[:finalPageContent.rfind('{{')]
                        if addLanguageCode and ((finalPageContent2.rfind('{{') != finalPageContent2.rfind(u'{{pron|') and \
                         finalPageContent2.rfind('{{') != finalPageContent2.rfind(u'{{US|') and finalPageContent2.rfind('{{') != finalPageContent2.rfind(u'{{UK|')) \
                          or finalPageContent.rfind(u'{{pron|') < finalPageContent.rfind(u'\n') or finalPageContent2.rfind(u'{{pron|') == -1) \
                          and ((pageContent.find('{{') != pageContent.find(u'{{pron|') or pageContent.find(u'{{pron|') > pageContent.find(u'\n')) \
                          or pageContent.find(u'{{pron|') == -1):
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, languageCode)
                        else:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent, currentTemplate, 'nocat=1')

                if debugLevel > 1:
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
                    pywikibot.output(u"\n\03{blue}Modèle traité\03{default}")
                    print (finalPageContent.encode(config.console_encoding, 'replace')[:1000])
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
                    raw_input (pageContent.encode(config.console_encoding, 'replace'))
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
            else:
                if fixOldTemplates:
                    if debugLevel > 0: print ' Recherche des modèles de langue désuets'
                    templatePage = getContentFromPageName(u'Template:' + currentTemplate, allowedNamespaces = [u'Template:'])
                    if templatePage.find(u'{{modèle désuet de code langue}}') != -1:
                        if debugLevel > 0: print u' Remplacements de l\'ancien modèle de langue'
                        pageContent = u'subst:nom langue|' + currentTemplate + pageContent[pageContent.find(u'}}'):]
                        pageContent = pageContent.replace(u'{{' + currentTemplate + u'}}', u'{{subst:nom langue|' + currentTemplate + u'}}')
                        finalPageContent = finalPageContent.replace(u'{{' + currentTemplate + u'}}', u'{{subst:nom langue|' + currentTemplate + u'}}')
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                else:
                    if debugLevel > 0: pywikibot.output(u"\n\03{yellow} Unknown template\03{default} " + currentTemplate)
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

            if not backward:
                if debugLevel > 1:
                    message = u' Remplacement par \x1b[6;32;40m' + finalPageContent[finalPageContent.rfind('{{'):] + u'\x1b[0m\n\n'
                    print(message.encode(config.console_encoding, 'replace'))
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
                if debugLevel > 1:
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
                    raw_input(pageContent.encode(config.console_encoding, 'replace'))
                    pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")

            if languageCode is not None and pageContent.find(u'}}') != -1 and (pageContent.find(u'}}') < pageContent.find(u'{{') or pageContent.find(u'{{') == -1):
                if debugLevel > 1: print u'    possible duplicated "lang=" in ' + currentTemplate
                finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                # TODO bug with nested templates: https://fr.wiktionary.org/w/index.php?title=Utilisateur:JackBot/test_unitaire&diff=prev&oldid=25811164
                #regex = ur'({{' + re.escape(currentTemplate) + ur')\|lang=' + languageCode + '(\|[^{}]*({{(.*?)}}|.)*[^{}]*\|lang=' + languageCode + u')'
                regex = ur'({{' + re.escape(currentTemplate) + ur')\|lang=' + languageCode + '(\|[^{}]*\|lang=' + languageCode + u')'
                if re.search(regex, finalPageContent):
                    if debugLevel > 1:
                        print u'    remove duplicated "lang="'
                        print regex # ({{refnec)\|lang=pt(\|[^{}]*({{(.*?)}}|.)*[^{}]*\|lang=pt)
                        raw_input(finalPageContent.encode(config.console_encoding, 'replace'))
                    finalPageContent = re.sub(regex, ur'\1\2', finalPageContent)

        finalPageContent = finalPageContent + pageContent

        if debugLevel > 0: ' Recherche du nombre'
        regex = ur"{{(pluriel|nombre) *\?*\|fr}}( {{[m|f]}})(\n# *'* *([Mm]asculin |[Ff]éminin )*[Pp]luriel d)"
        if re.search(regex, finalPageContent):
            summary = summary + u', précision du pluriel'
            finalPageContent = re.sub(regex, ur'{{p}}\2\3', finalPageContent)

        regex = ur"{{(pluriel|nombre) *\?*\|fr}} *(\n# *'* *([Mm]asculin |[Ff]éminin )*[Pp]luriel d)"
        if re.search(regex, finalPageContent):
            summary = summary + u', précision du pluriel'
            finalPageContent = re.sub(regex, ur'{{p}}\2', finalPageContent)

        if fixGenders:
            if debugLevel > 0: ' Recherche du genre'
            regex = ur"{{genre *\?*\|fr}}(\n# *'* *[Mm]asculin)"
            if re.search(regex, finalPageContent):
                finalPageContent = re.sub(regex, ur'{{m}}\1', finalPageContent)
                summary = summary + u', précision du genre m'
                if debugLevel > 1: print '  m1'

            regex = ur"{{genre *\?*\|fr}}(\n# *'* *[Ff]éminin)"
            if re.search(regex, finalPageContent):
                finalPageContent = re.sub(regex, ur'{{f}}\1', finalPageContent)
                summary = summary + u', précision du genre f'
                if debugLevel > 1: print '  f1'

            if finalPageContent.find(u'{{genre|fr}}') != -1 or finalPageContent.find(u'{{genre ?|fr}}') != -1:
                mSuffixes = ['eur', 'eux', 'ant', 'age', 'ier', 'ien', 'ois', 'ais', 'isme', 'el', 'if', 'ment', 'ments'] # pas "é" : adaptabilité
                for mSuffix in mSuffixes:
                    if pageName[-len(mSuffix):] == mSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{m}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{m}}")
                        summary = summary + u', précision du genre m'
                        if debugLevel > 1: print '  m2'
                        break

                fSuffixes = ['euse', 'ante', 'ance', 'ette', 'ienne', 'rie', 'oise', 'aise', 'logie', 'tion', 'ité', 'elle', 'ive']
                for fSuffix in fSuffixes:
                    if pageName[-len(fSuffix):] == fSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{f}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{f}}")
                        summary = summary + u', précision du genre f'
                        if debugLevel > 1: print '  f2'
                        break

                mfSuffixes = ['iste']
                for mfSuffix in mfSuffixes:
                    if pageName[-len(mfSuffix):] == mfSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{mf}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{mf}}")
                        summary = summary + u', précision du genre mf'
                        if debugLevel > 1: print '  mf1'
                        break

                if singularPageName != u'':
                    lemmaGender = getGenderFromPageName(singularPageName)
                    if lemmaGender != '':
                        finalPageContent = finalPageContent.replace(u'{{genre|fr}}', lemmaGender)
                        finalPageContent = finalPageContent.replace(u'{{genre ?|fr}}', lemmaGender)
                        summary = summary + u', précision du genre ' + lemmaGender
                        if debugLevel > 1: print '  loc'

            if fixFalseFlexions and pageName[-2:] == u'es':
                if debugLevel > 0: ' Hardfix des flexions de noms féminins'
                oldSuffix = []
                newSuffix = []
                oldSuffix.append(ur'eur')
                newSuffix.append(ur'rice')
                oldSuffix.append(ur'eur')
                newSuffix.append(ur'euse')
                oldSuffix.append(ur'eux')
                newSuffix.append(ur'euse')
                oldSuffix.append(ur'er')
                newSuffix.append(ur'ère')
                oldSuffix.append(ur'el')
                newSuffix.append(ur'elle')
                oldSuffix.append(ur'et')
                newSuffix.append(ur'ette')
                oldSuffix.append(ur'n')
                newSuffix.append(ur'nne')
                sectionContent, startPosition, endPosition = getSection(finalPageContent, 'nom')
                if sectionContent is not None:
                    newSectionContent = sectionContent
                    i = 0
                    while i < len(newSuffix):
                        if pageName[-len(newSuffix[i] + u's'):] == newSuffix[i] + u's':
                            regex = ur"({{fr\-rég\|s=[^\|}]+)" + oldSuffix[i] + u"([\|}])"
                            if re.search(regex, newSectionContent):
                                newSectionContent = re.sub(regex, ur'\1' + newSuffix[i] + ur'\2', newSectionContent)

                            regex = ur"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + oldSuffix[i] + u"([\|#][^\]]+)" + oldSuffix[i] + u"(\])"
                            if re.search(regex, newSectionContent):
                                newSectionContent = re.sub(regex, ur'\1' + newSuffix[i] + ur'\2' + newSuffix[i] + ur'\3', newSectionContent)

                            regex = ur"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + oldSuffix[i] + u"([\|#])"
                            if re.search(regex, newSectionContent):
                                newSectionContent = re.sub(regex, ur'\1' + newSuffix[i] + ur'\2', newSectionContent)

                            regex = ur"({{f}}\n# *''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+)" + oldSuffix[i] + u"(\])"
                            if re.search(regex, newSectionContent):
                                newSectionContent = re.sub(regex, ur'\1' + newSuffix[i] + ur'\2', newSectionContent)
                        i = i + 1
                    regex = ur"({{fr\-rég\|s=[^\|}]+[^e\]}])([\|}])"
                    if re.search(regex, newSectionContent):
                        newSectionContent = re.sub(regex, ur'\1e\2', newSectionContent)
                    regex = ur"({{f}}\n# ''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+[^e\]])(\])"
                    if re.search(regex, newSectionContent):
                        newSectionContent = re.sub(regex, ur'\1e\2', newSectionContent)
                    regex = ur"({{f}}\n# ''(?:[fF]éminin )?[pP]luriel de'' \[\[[^\|\]#]+[^e])([\|#][^\]]+[^e\]])(\])"
                    if re.search(regex, newSectionContent):
                        newSectionContent = re.sub(regex, ur'\1e\2e\3', newSectionContent)
                    newSectionContent = newSectionContent.replace('|e}}', '|}}')

                    summary = summary + u', correction de flexion de nom féminin'
                    finalPageContent = finalPageContent.replace(sectionContent, newSectionContent)

        language = 'fr' # TODO: intl
        if finalPageContent.find(u'{{langue|' + language + u'}}') != -1:
            if debugLevel > 0: print u' Recherche des faux homophones car lemme et sa flexion'
            #TODO : modèles des locutions
            #TODO : doublon systématique ? singularPageName = getLemmaFromContent(finalPageContent, language)
            flexionPageName = ''
            if finalPageContent.find('|' + language + '|flexion}}') == -1:
                # Recherche d'éventuelles flexions dans la page du lemme
                flexionTemplate = getFlexionTemplate(pageName, language)
                if flexionTemplate.find(u'inv=') == -1 and \
                 (flexionTemplate[:flexionTemplate.find('|')] in flexionTemplatesFrWithS \
                 or flexionTemplate[:flexionTemplate.find('|')] in flexionTemplatesFrWithMs):
                    flexionPageName = getParameterValue(flexionTemplate, 'p')
                    if flexionPageName == '':
                        flexionPageName = pageName + 's'
                #TODO: flexionTemplate = [conjugaisons]

            for i in range(0, 2):
                if infinitive is not None and infinitive != '':
                    finalPageContent, summary = removeFalseHomophones(finalPageContent, language, pageName, infinitive, summary)
                if singularPageName is not None and singularPageName != '':
                    finalPageContent, summary = removeFalseHomophones(finalPageContent, language, pageName, singularPageName, summary)
                if flexionPageName is not None and flexionPageName != '':
                    finalPageContent, summary = removeFalseHomophones(finalPageContent, language, pageName, flexionPageName, summary)
                MSPageName = getLemmaFromFeminine(finalPageContent, language, ['adjectif'])
                if MSPageName is not None and MSPageName != '':
                     finalPageContent, summary = removeFalseHomophones(finalPageContent, language, pageName, MSPageName, summary)
            if debugLevel > 2: raw_input(finalPageContent.encode(config.console_encoding, 'replace'))             

        regex = ur'([^\n=])(===?=? *{{S\|)'
        if re.search(regex, finalPageContent):
            finalPageContent = re.sub(regex, ur'\1\n\n\2', finalPageContent)

    else:
        # Unknown namespace
        finalPageContent = pageContent

    # Fix
    finalPageContent = finalPageContent.replace(u'|lanɡ=', u'|lang=')
    regex = ur'({{pron)(\|lang=[a-zA-Z]{2,3})(\|[a-zA-Z]{2,3}}})'
    if re.search(regex, finalPageContent):
        finalPageContent = re.sub(regex, ur'\1|\3', finalPageContent)

    if testImport and username in pageName: finalPageContent = addLineTest(finalPageContent)
    if debugLevel > 0: pywikibot.output(u"\n\03{red}---------------------------------------------\03{default}")
    if finalPageContent != currentPageContent:
        if page.namespace() == 0 or username in pageName:
            # Modifications mineures, ne justifiant pas une édition à elles seules
            finalPageContent = finalPageContent.replace(u'  ', u' ')
            regex = ur'\n+(\n\n=* {{S\|)'
            finalPageContent = re.sub(regex, ur'\1', finalPageContent)
            finalPageContent = finalPageContent.replace(u'\n\n\n\n', u'\n\n\n')
            finalPageContent = finalPageContent.replace(u'.\n=', u'.\n\n=')
            regex = ur'(\])(\n== {{langue\|)'
            finalPageContent = re.sub(regex, ur'\1\n\2', finalPageContent)
        savePage(page, finalPageContent, summary)
    elif debugLevel > 0:
        print u'Aucun changement après traitement'


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
setGlobalsWiktionary(debugLevel, site, username)
def main(*args):
    global waitAfterHumans, fixOldTemplates, listHomophons, outputFile, siteLanguage, siteFamily, fixTags, \
    listFalseTranslations, testImport, cancelUser
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        afterPage = u''
        if len(sys.argv) > 2: afterPage = sys.argv[2]

        if sys.argv[1] == str('-test'):
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == str('-test2'):
            treatPageByName(u'User:' + username + u'/test2')
        elif sys.argv[1] == str(u'-tu') or sys.argv[1] == str('-t'):
            treatPageByName(u'User:' + username + u'/test unitaire')
        elif sys.argv[1] == str('-ti'):
            testImport = True
            treatPageByName(u'User:' + username + u'/test unitaire')
        elif sys.argv[1] == str('-page') or sys.argv[1] == str('-p'):
            waitAfterHumans = False
            treatPageByName(u'Nguyễn')
        elif sys.argv[1] == str('-file') or sys.argv[1] == str('-txt'):
            waitAfterHumans = False
            fileName = u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt'
            if debugLevel > 0: print fileName
            p.pagesByFile(fileName)
        elif sys.argv[1] == str('-dump') or sys.argv[1] == str('-xml') or sys.argv[1] == str('-regex'):
            dumpFile = siteLanguage + siteFamily + '\-.*xml'
            if len(sys.argv) > 2:
                regex = sys.argv[2]
            else:
                regex = ur'{term[\n\|].*id *= *[^\n\|{}]+[\n\|]'
            if len(sys.argv) > 3:
                testPage = sys.argv[3]
            else:
                testPage = None
            if testPage is not None:
                pageContent = getContentFromPageName(testPage)
                if re.search(regex, pageContent, re.DOTALL):
                    print 'OK'
                else:
                    print 'KO'
            else:
                p.pagesByXML(dumpFile, regex = regex, namespaces = 10)
        elif sys.argv[1] == str('-u'):
            if len(sys.argv) > 2:
                targetedUser = sys.argv[2]
            else:
                targetedUser = username
            if len(sys.argv) > 3:
                cancelUser['user'] = targetedUser
                cancelUser['action'] = sys.argv[3]
            if len(sys.argv) > 4:
                number = sys.argv[4]
            else:
                number = 1000
            p.pagesByUser(u'User:' + targetedUser, numberOfPagesToTreat = number, namespaces = [0])
        elif sys.argv[1] == str('-search') or sys.argv[1] == str('-s') or sys.argv[1] == str('-r'):
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'insource:/\{\{pron\|lanɡ=/', namespaces = [0])

        elif sys.argv[1] == str('-link') or sys.argv[1] == str('-l') or sys.argv[1] == str('-template') or \
            sys.argv[1] == str('-m'):
            p.pagesByLink(u'Template:gaul', namespaces = [0])
        elif sys.argv[1] == str('-category') or sys.argv[1] == str('-cat') or sys.argv[1] == str('-c'):
            p.pagesByCat(u'Catégorie:Suffixes en occitan', afterPage = u'', recursive = True)
            return
            if len(sys.argv) > 2:
                if sys.argv[2] == str('listFalseTranslations'):
                    listFalseTranslations = True
                    p.pagesByCat(u'Catégorie:Pages "info" si réforme 1895 de l’espéranto')
                elif sys.argv[2] == str('fixOldTemplates'):
                    fixOldTemplates = True
                    p.pagesByCat(u'Appels de modèles incorrects:abréviation', afterPage = afterPage, recursive = False, namespaces = [14])
                else:
                    p.pagesByCat(sys.argv[2].decode(config.console_encoding, 'replace'))
            else:
                p.pagesByCat(u'Langues en anglais', namespaces = None)

        elif sys.argv[1] == str('-redirects'):
            p.pagesByRedirects()
        elif sys.argv[1] == str('-all'):
           p.pagesByAll()
        elif sys.argv[1] == str('-RC'):
            while 1:
                p.pagesByRCLastDay()
        elif sys.argv[1] == str('-nocat'):
            p.pagesBySpecialNotCategorized()
        elif sys.argv[1] == str('-lint'):
            fixTags = True
            p.pagesBySpecialLint()
        elif sys.argv[1] == str('-extlinks'):
            p.pagesBySpecialLinkSearch(u'www.dmoz.org')
        else:
            # Format: http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
            try:
                treatPageByName(html2Unicode(sys.argv[1]))
            except UnicodeDecodeError:
                print u' page à décoder'
                treatPageByName(sys.argv[1].decode(config.console_encoding, 'replace'))
            except UnicodeEncodeError:
                print u' page à encoder'
                treatPageByName(sys.argv[1].encode(config.console_encoding, 'replace'))
    else:
        # Nightly treatment:
        p.pagesByCat(u'Catégorie:Wiktionnaire:Codes langue manquants', recursive = True, \
            exclude = [u'Catégorie:Wiktionnaire:Traductions manquantes sans langue précisée'])
        p.pagesByCat(u'Catégorie:Wiktionnaire:Flexions à vérifier', recursive = True)
        p.pagesByCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée')
        p.pagesByCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet')
        p.pagesByCat(u'Catégorie:Appels de modèles incorrects:deet')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Ébauches à compléter')
        p.pagesByLink(u'Template:trad', namespaces = [0])
        p.pagesByLink(u'Template:clef de tri')
        p.pagesByLink(u'Template:1ergroupe')
        p.pagesByLink(u'Template:2egroupe')
        p.pagesByLink(u'Template:3egroupe')
        p.pagesByLink(u'Template:-')
        p.pagesByLink(u'Template:-ortho-alt-')
        p.pagesByLink(u'Template:mascul')
        p.pagesByLink(u'Template:fémin')
        p.pagesByLink(u'Template:femin')
        p.pagesByLink(u'Template:sing')
        p.pagesByLink(u'Template:plur')
        p.pagesByLink(u'Template:pluri')
        p.pagesByLink(u'Template:=langue=')
        p.pagesByLink(u'Template:-déf-')
        p.pagesByLink(u'Template:pron-rég')
        p.pagesByLink(u'Template:mp')
        p.pagesByLink(u'Template:fp')
        p.pagesByLink(u'Template:vx')
        p.pagesByCat(u'Catégorie:Traduction en français demandée d’exemple(s) écrits en français')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections avec titre inconnu')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections avec paramètres superflus')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections utilisant un alias')
        p.pagesBySearch(u'insource:/\}==== \{\{S\|/', namespaces = [0])
        p.pagesBySearch(u'insource:/\}=== \{\{S\|/', namespaces = [0])
        p.pagesBySearch(u'insource:/[^=]=== \{\{S\|(variantes|synonymes|antonymes|dérivés|apparentés|hyperonymes|hyponymes|méronymes|holonymes|vocabulaire|traductions)/', namespaces = [0])

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/env python
# coding: utf-8
'''
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le labs Wikimedia :
1) Crée les redirection d'apostrophe dactylographique vers apostrophe typographique
2) Gère des modèles {{voir}} en début de page.
3) Retire certains doublons de modèles et d'espaces.
4) Remplace les modèles catégorisés comme obsolètes
5) Ajoute les prononciations sur la ligne de forme, et certains liens vers les conjugaisons.
6) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
7) Détecte les modèles de contexte à ajouter, et ajoute leurs codes langues  ou "nocat=1"
8) Complète la boite de flexions de verbes en français.
9) Ajoute les anagrammes (pour les petits mots)
10) Teste les URL et indique si elles sont brisées avec {{lien brisé}}, et les transforme en modèle s'il existe pour leur site
Tests sur http://fr.wiktionary.org/w/index.php?title=Utilisateur%3AJackBot%2Ftest&diff=14533806&oldid=14533695
'''

from __future__ import absolute_import, unicode_literals
import catlib, codecs, collections, os, re, socket, sys, time, urllib
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
addDefaultSortKey = True
removeDefaultSort = True
allNamespaces = False
treatTemplates = False
treatCategories = False
fixGenders = True
waitAfterHumans = True
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
# Paragraphes sans modèle catégorisant
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
limit2 = len(Modele)
Modele.append(u'-compos-')
Section.append(u'composés')
#Modele.append(u'-décl-')
#Section.append(u'déclinaison')
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
Modele.append(u'-homo-')
Section.append(u'homophones')
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
limit3 = len(Modele)
Modele.append(u'-notes-')
Section.append(u'notes')
Modele.append(u'-note-')
Section.append(u'note')
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
Modele.append(u'anthro')
Modele.append(u'anthropologie')
Modele.append(u'antilopes')
Modele.append(u'antiq')
Modele.append(u'antiquité')
Modele.append(u'apiculture')
Modele.append(u'apiculture')
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
Modele.append(u'arithmétique')
Modele.append(u'arme')
Modele.append(u'armement')
Modele.append(u'armes blanches')
Modele.append(u'armes à feu')
Modele.append(u'armes')
Modele.append(u'arthropodes')
Modele.append(u'artillerie')
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
Modele.append(u'audiovis')
Modele.append(u'audiovisuel')
Modele.append(u'automo')
Modele.append(u'automobile')
Modele.append(u'auxiliaire')
Modele.append(u'auxiliaire')
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
Modele.append(u'hyperb')
Modele.append(u'hyperbole')
Modele.append(u'hérald')
Modele.append(u'héraldique')
Modele.append(u'hérons')
Modele.append(u'i')
Modele.append(u'ibis')
Modele.append(u'ichtyo')
Modele.append(u'ichtyologie')
Modele.append(u'idiotisme')
Modele.append(u'illégalité')
Modele.append(u'impers')
Modele.append(u'impersonnel')
Modele.append(u'impr')
Modele.append(u'imprimerie')
Modele.append(u'improprement')
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
Modele.append(u'papeterie')
Modele.append(u'papillons')
Modele.append(u'papèterie')
Modele.append(u'par analogie')
Modele.append(u'par dérision')
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
Modele.append(u'phys')
Modele.append(u'physio')
Modele.append(u'physiol')
Modele.append(u'physiologie')
Modele.append(u'physique')
Modele.append(u'phyton')
Modele.append(u'phytonimie')
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
Modele.append(u'ébauche-syn')
Modele.append(u'non standard')
Modele.append(u'ébauche-trans')
Modele.append(u'ébauche-étym-nom-scientifique')
Modele.append(u'ébauche-étym')
Modele.append(u'ébauche-déf')
Modele.append(u'ébauche-exe')
Modele.append(u'ébauche-pron')
Modele.append(u'ébauche')
Modele.append(u'...')

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
    print(pageName.encode(config.console_encoding, 'replace'))
    if pageName[-3:] == '.js': return
    if pageName.find(u'’') != -1:
        page = Page(site, pageName.replace(u'’', u'\''))
        if not page.exists():
            if debugLevel > 0: print u'Création d\'une redirection apostrophe'
            savePage(page, u'#REDIRECT[[' + pageName + ']]', u'Redirection pour apostrophe')

    page = Page(site, pageName)
    if debugLevel == 0 and waitAfterHumans and not hasMoreThanTime(page): return

    currentPageContent = getContentFromPage(page, 'All')
    if currentPageContent == 'KO': return
    pageContent = currentPageContent
    finalPageContent = u''
    CleTri = defaultSort(pageName)
    rePageName = re.escape(pageName)

    pageContent = globalOperations(pageContent)
    if fixFiles: pageContent = replaceFilesErrors(pageContent)
    if fixTags: pageContent = replaceDepretacedTags(pageContent)
    if checkURL: pageContent = hyperlynx(pageContent)

    if page.namespace() == 14:
        if u'par caractère' in pageContent:
            pageContent = u'{{tableau han/cat}}'

        finalPageContent = pageContent

    elif treatTemplates and page.namespace() == 10:
        templates = [u'emploi', u'région', u'registre', u'term']
        for template in templates:
            if not u'{{{clé|' in pageContent and pageContent[:len(u'{{' + template)] == u'{{' + template and u'\n}}<noinclude>' in pageContent:
                summary = u'[[Wiktionnaire:Wikidémie/juillet_2017#Pour_conclure_Wiktionnaire:Prise_de_d.C3.A9cision.2FCl.C3.A9s_de_tri_fran.C3.A7aises_par_d.C3.A9faut|Clé de tri]]'
                pageContent = pageContent[:pageContent.find(u'\n}}<noinclude>')] + u'\n|clé={{{clé|}}}' + pageContent[pageContent.find(u'\n}}<noinclude>'):]

        regex = u'<includeonly> *\n*{{\#if(eq)?: *{{NAMESPACE}}[^<]+\[\[Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section[^<]+</includeonly>'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex,  u'{{anciens modèles de section}}', pageContent, re.MULTILINE)
        if debugLevel > 0: raw_input(pageContent.encode(config.console_encoding, 'replace'))

        finalPageContent = pageContent

    elif page.namespace() == 0 or username in pageName:
        regex = ur'{{=([a-z\-]+)=}}'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'{{langue|\1}}', pageContent)

        while pageContent.find(u'{{ ') != -1:
            pageContent = pageContent[:pageContent.find(u'{{ ')+2] + pageContent[pageContent.find(u'{{ ')+3:len(pageContent)]
        regex = ur'{{(formater|SI|supp|supprimer|PàS|S\|erreur|S\|faute)[\|}]'
        if re.search(regex, pageContent):
            if debugLevel > 0: print u'Page en travaux : non traitée l 1409'
            return

        # Alias d'anciens titres de section
        pageContent = pageContent.replace(u'{{-car-}}', u'{{caractère}}')
        pageContent = pageContent.replace(u'{{-note-|s=s}}', u'{{-notes-}}')
        pageContent = pageContent.replace(u'{{-etym-}}', u'{{-étym-}}')
        pageContent = pageContent.replace(u'{{-pronom-personnel-', u'{{-pronom-pers-')

        if debugLevel > 0: print u'Conversion vers {{S}}'
        EgalSection = u'==='
        for p in range(1, limit4):
            if debugLevel > 1: print Modele[p] + ur'|S\|'+ Section[p]
            if p == limit2: EgalSection = u'===='
            if p == limit3: EgalSection = u'====='

            regex = ur'[= ]*{{[\-loc]*(' + Modele[p] + ur'|S\|'+ Section[p] + ur')([^}]*)}}[= ]*'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'\2}} ' + EgalSection, pageContent)

            regex = ur'[= ]*{{\-flex[\-loc]*(' + Modele[p] + ur'|S\|' + Section[p] + ur')\|([^}]*)}}[= ]*'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'|\2|flexion}} ' + EgalSection, pageContent)

        if debugLevel > 1:
            pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
            raw_input(pageContent.encode(config.console_encoding, 'replace'))
            pywikibot.output(u"\n\03{red}---------------------------------------------------\03{default}")
        if pageContent.find(u'|===') != -1 or pageContent.find(u'{===') != -1:
            if debugLevel > 0: print u' *==='
            return

        # Titres en minuscules
        #pageContent = re.sub(ur'{{S\|([^}]+)}}', ur'{{S|' + ur'\1'.lower() + ur'}}', pageContent)
        for f in re.findall("{{S\|([^}]+)}}", pageContent):
            pageContent = pageContent.replace(f, f.lower())
        # Alias peu intuitifs des sections avec langue
        pageContent = pageContent.replace(u'{{S|adj|', u'{{S|adjectif|')
        pageContent = pageContent.replace(u'{{S|adjectifs|', u'{{S|adjectif|')
        pageContent = pageContent.replace(u'{{S|adj-num|', u'{{S|adjectif numéral|')
        pageContent = pageContent.replace(u'{{S|adv|', u'{{S|adverbe|')
        pageContent = pageContent.replace(u'{{S|drv}}', u'{{S|dérivés}}')
        pageContent = pageContent.replace(u'{{S|homo|', u'{{S|homophones|')
        pageContent = pageContent.replace(u'{{S|homo}}', u'{{S|homophones}}')
        pageContent = pageContent.replace(u'{{S|interj|', u'{{S|interjection|')
        pageContent = pageContent.replace(u'{{S|locution adverbiale', u'{{S|adverbe')
        pageContent = pageContent.replace(u'{{S|locution phrase|', u'{{S|locution-phrase|')
        pageContent = pageContent.replace(u'{{S|nom commun|', u'{{S|nom|')
        pageContent = pageContent.replace(u'{{S|nom-fam|', u'{{S|nom de famille|')
        pageContent = pageContent.replace(u'{{S|nom-pr|', u'{{S|nom propre|')
        pageContent = pageContent.replace(u'{{S|pron}}', u'{{S|prononciation}}')
        pageContent = pageContent.replace(u'{{S|symb|', u'{{S|symbole|')
        pageContent = pageContent.replace(u'{{S|verb|', u'{{S|verbe|')
        pageContent = pageContent.replace(u'{{S|apparentés étymologiques', u'{{S|apparentés')
        # Alias peu intuitifs des sections sans langue
        pageContent = re.sub(ur'{{S\| ?abr(é|e)v(iations)?\|?[a-z ]*}}', u'{{S|abréviations}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?anagr(ammes)?\|?[a-z ]*}}', u'{{S|anagrammes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?anciennes orthographes?\|?[a-z ]*}}', u'{{S|anciennes orthographes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?ant(onymes)?\|?[a-z ]*}}', u'{{S|antonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?app(arentés)?\|?[a-zé]*}}', u'{{S|apparentés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?apr\|?[a-zé]*}}', u'{{S|apparentés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?compos(és)?\|?[a-zé]*}}', u'{{S|composés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?dial\|?[a-z ]*}}', u'{{S|variantes dialectales}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?dimin(inutifs)?\|?[a-z ]*}}', u'{{S|diminutifs}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?d(é|e)riv(é|e)s?(\|[a-z ]*}}|}})', u'{{S|dérivés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?drv\|?[a-z ]*}}', u'{{S|dérivés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?dérivés int\|?[a-z ]*}}', u'{{S|dérivés autres langues}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?drv\-int\|?[a-z ]*}}', u'{{S|dérivés autres langues}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?(é|e)tym(ologie)?\|?[a-z ]*}}', u'{{S|étymologie}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?exp(ressions)?\|?[a-z ]*}}', u'{{S|expressions}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?gent(ilés)?\|?[a-zé]*}}', u'{{S|gentilés}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?faux\-amis?\|?[a-zé]*}}', u'{{S|faux-amis}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?holo(nymes)?\|?[a-z ]*}}', u'{{S|holonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?hyper(onymes)?\|?[a-z ]*}}', u'{{S|hyperonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?hypo(nymes)?\|?[a-z ]*}}', u'{{S|hyponymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?m(é|e)ro(nymes)?\|?[a-z ]*}}', u'{{S|méronymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?note\|?[a-z ]*}}', u'{{S|note}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?notes\|?[a-z ]*}}', u'{{S|notes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?paro(nymes)?\|?[a-z ]*}}', u'{{S|paronymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?phrases?\|?[a-z ]*}}', u'{{S|phrases}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?pron(onciation)?\|?[a-z ]*}}', u'{{S|prononciation}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?q\-syn\|?[a-z ]*}}', u'{{S|quasi-synonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?quasi(\-| )syn(onymes)?\|?[a-z ]*}}', u'{{S|quasi-synonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?r(é|e)f[a-zé]*\|?[a-z ]*}}', u'{{S|références}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?syn(onymes)?\|?[a-z ]*}}', u'{{S|synonymes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?trad(uctions)?\|?[a-z]*}}', u'{{S|traductions}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?trad\-trier\|?[a-z ]*}}', u'{{S|traductions à trier}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?traductions à trier\|?[a-z ]*}}', u'{{S|traductions à trier}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?var(iantes)?\|?[a-z]*}}', u'{{S|variantes}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?variantes dial\|?[a-z ]*}}', u'{{S|variantes dialectales}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?variantes dialectales\|?[a-z ]*}}', u'{{S|variantes dialectales}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?var[a-z]*(\-| )ortho(graphiques)?\|?[a-z ]*}}', u'{{S|variantes orthographiques}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?voc(abulaire)?\|?[a-z ]*}}', u'{{S|vocabulaire}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?vocabulaire apparenté\|?[a-z ]*}}', u'{{S|vocabulaire}}', pageContent)
        pageContent = re.sub(ur'{{S\| ?voir( aussi)?\|?[a-z ]*}}', u'{{S|voir aussi}}', pageContent)
        pageContent = pageContent.replace(u'==== {{S|phrases|fr}} ====', u'==== {{S|phrases}} ====')

        regex = ur"= *({{langue\|[^}]+}}) *="
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"= \1 =", pageContent)

        # Formatage général des traductions
        pageContent = pageContent.replace(u'{{trad|', u'{{trad-|')
        pageContent = pageContent.replace(u'{{(}}\n{{ébauche-trad}}\n{{)}}', '')
        pageContent = pageContent.replace(u'{{trad-début|{{trad-trier}}}}', u'{{trad-trier}}\n{{trad-début}}')
        pageContent = pageContent.replace(u'{{trad-début|{{trad-trier|fr}}}}', u'{{trad-trier}}\n{{trad-début}}')

            # 1) Suppression de {{ébauche-trad|fr}} (WT:PPS)
        pageContent = pageContent.replace(ur'{{ébauche-trad|fr}}', u'{{ébauche-trad}}')     # bug ?
        regex = ur'{{ébauche\-trad\|fr}}'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, u'{{ébauche-trad}}', pageContent)

            # 2) Aucun modèle d'ébauche en dehors d'une boite déroulante
        pageContent = pageContent.replace(ur'{{ébauche-trad}}\n{{trad-début}}', u'{{trad-début}}\n{{ébauche-trad}}') # bug ?
        regex = ur'{{ébauche\-trad}}\n{{trad\-début}}'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, u'{{trad-début}}\n{{ébauche-trad}}', pageContent)

        pageContent = pageContent.replace(ur'==== {{S|traductions}} ====\n{{ébauche-trad}}\n', u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n')     # bug ?
        regex = ur'==== {{S\|traductions}} ====\n{{ébauche\-trad}}(\n<![^>]+>)*(\n|$)'
        if re.search(regex, pageContent):
            if debugLevel > 0: print ' ébauche sans boite'
            pageContent = re.sub(regex, u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad|en}}\n{{trad-fin}}\n', pageContent)

            # 3) Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
        pageContent = pageContent.replace(ur'<!--* {{T|en}} : {{trad|en|}}-->', '')     # bug ?
        regex = ur'<!\-\-[^{>]*{{T\|[^>]+>\n?'
        if re.search(regex, pageContent):
            if debugLevel > 0: print ' Commentaire trouvé l 1517'
            pageContent = re.sub(regex, u'', pageContent)
            # Cosmétique
        regex = ur'{{ébauche\-trad}}{{'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, u'{{ébauche-trad}}\n{{', pageContent)

        while pageContent.find(u'{{trad-fin}}\n* {{T|') != -1:
            pageContent2 = pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|'):]
            delta = pageContent2.find(u'\n')+1
            pageContent2 = pageContent2[delta:]
            if pageContent2.find(u'\n') != -1:
                if debugLevel > 0: print pageContent2[:pageContent2.find(u'\n')+1].encode(config.console_encoding, 'replace')
                if pageContent2[:pageContent2.find(u'\n')+1].find(u'trier') != -1: break
                pageContent = pageContent[:pageContent.find(u'{{trad-fin}}\n* {{T|'):] + pageContent2[:pageContent2.find(u'\n')+1] + u'{{trad-fin}}\n' + pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|')+delta+pageContent2.find(u'\n')+1:]
            else:
                if debugLevel > 0: print pageContent2.encode(config.console_encoding, 'replace')
                if pageContent2[:len(pageContent2)].find(u'trier') != -1: break
                pageContent = pageContent[:pageContent.find(u'{{trad-fin}}\n* {{T|'):] + pageContent2[:len(pageContent2)] + u'{{trad-fin}}\n' + pageContent[pageContent.find(u'{{trad-fin}}\n* {{T|')+delta+len(pageContent2):]
            # Cosmétique
        regex = ur'}}{{trad\-fin}}'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, u'}}\n{{trad-fin}}', pageContent)

        if not username in pageName and debugLevel == 0:
            if debugLevel > 0: print u'Ajout des {{voir}}'
            if pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
                pageContent = pageContent[:pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].lower() + pageName[1:] + pageContent[pageContent.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|{{lc:{{PAGENAME}}}}'):len(pageContent)]
                summary = summary + u', subst de {{lc:{{PAGENAME}}}}'
            if pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
                pageContent = pageContent[:pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].upper() + pageName[1:] + pageContent[pageContent.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|{{ucfirst:{{PAGENAME}}}}'):len(pageContent)]
                summary = summary + u', subst de {{ucfirst:{{PAGENAME}}}}'
            if pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
                pageContent = pageContent[:pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].lower() + pageName[1:] + pageContent[pageContent.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|{{LC:{{PAGENAME}}}}'):len(pageContent)]
                summary = summary + u', subst de {{LC:{{PAGENAME}}}}'
            if pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
                pageContent = pageContent[:pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].upper() + pageName[1:] + pageContent[pageContent.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|{{UCFIRST:{{PAGENAME}}}}'):len(pageContent)]
                summary = summary + u', subst de {{UCFIRST:{{PAGENAME}}}}'
            if pageContent.find(u'{{voir|') == -1 and pageContent.find(u'{{voir/') == -1:
                PageVoir = u''
                # Liste de toutes les pages potentiellement "à voir"
                PagesCleTotal = pageName
                if PagesCleTotal.find(pageName.lower()) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName.lower()
                if PagesCleTotal.find(pageName.upper()) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName.upper()
                if PagesCleTotal.find(pageName[:1].lower() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].lower() + pageName[1:]
                if PagesCleTotal.find(pageName[:1].upper() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].upper() + pageName[1:]
                if PagesCleTotal.find(u'-' + pageName[:1].lower() + pageName[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|-' + pageName[:1].lower() + pageName[1:]
                if PagesCleTotal.find(pageName[:1].lower() + pageName[1:] + u'-') == -1: PagesCleTotal = PagesCleTotal + u'|' + pageName[:1].lower() + pageName[1:] + u'-'
                if PagesCleTotal.find(u'-') != -1: PagesCleTotal = PagesCleTotal + u'|' + PagesCleTotal.replace(u'-',u'')
                diacritics = []
                diacritics.append([u'a',u'á',u'à',u'ä',u'â',u'ã'])
                diacritics.append([u'c',u'ç'])
                diacritics.append([u'e',u'é',u'è',u'ë',u'ê'])
                diacritics.append([u'i',u'í',u'ì',u'ï',u'î'])
                diacritics.append([u'n',u'ñ'])
                diacritics.append([u'o',u'ó',u'ò',u'ö',u'ô',u'õ'])
                diacritics.append([u'u',u'ú',u'ù',u'ü',u'û'])
                for l in range(0,len(diacritics)):
                    for d in range(0,len(diacritics[l])):
                        if pageName.find(diacritics[l][d]) != -1:
                            if debugLevel > 1: print u'Titre contenant : ' + diacritics[l][d]
                            Lettre = diacritics[l][d]
                            for d in range(0,len(diacritics[l])):
                                PagesCleTotal = PagesCleTotal + u'|' + pageName.replace(Lettre,diacritics[l][d])
                if PagesCleTotal.find(CleTri) == -1: PagesCleTotal = PagesCleTotal + u'|' + CleTri    # exception ? and pageContent.find(u'{{langue|eo}}') == -1
                # Filtre des pages de la liste "à voir"
                PagesCleRestant = PagesCleTotal + u'|'
                PagesCleTotal = u''
                PagesVoir = u''
                if debugLevel > 0: print u' Recherche des clés...'
                while PagesCleRestant != u'':
                    if debugLevel > 1: print PagesCleRestant.encode(config.console_encoding, 'replace')
                    currentPage = PagesCleRestant[:PagesCleRestant.find(u'|')]
                    PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:len(PagesCleRestant)]
                    pageCle = Page(site, currentPage)
                    pageContentCle = getContentFromPage(pageCle)
                    if pageContentCle != u'KO':
                        if PagesCleTotal.find(currentPage) == -1: PagesCleTotal = PagesCleTotal + u'|' + currentPage
                        if pageContentCle.find(u'{{voir|') != -1:
                            pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|'):len(pageContentCle)]
                            PagesVoir = PagesVoir + u'|' + pageContentCle2[:pageContentCle2.find('}}')]
                        elif pageContentCle.find(u'{{voir/') != -1:
                            pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir/')+len(u'{{voir/'):len(pageContentCle)]
                            pageContent = u'{{voir/' + pageContentCle2[:pageContentCle2.find('}}')+3] + pageContent
                            pageMod = Page(site, u'Template:voir/' + pageContentCle2[:pageContentCle2.find('}}')])
                            pageContentModBegin = getContentFromPage(pageMod)
                            if pageContentModBegin == 'KO': break
                            pageContentMod = pageContentModBegin
                            if pageContentMod.find(u'!') == -1:
                                if pageContentMod.find(pageName) == -1: pageContentMod = pageContentMod[:pageContentMod.find('}}')] + u'|' + pageName + pageContentMod[pageContentMod.find('}}'):len(pageContentMod)]
                                if pageContentMod.find(PageVoir) == -1: pageContentMod = pageContentMod[:pageContentMod.find('}}')] + u'|' + PageVoir + pageContentMod[pageContentMod.find('}}'):len(pageContentMod)]
                            if debugLevel > 0:
                                print u'PagesCleRestant vide'
                            else:
                                if pageContentMod != pageContentModBegin: savePage(pageMod,pageContentMod, summary)
                            PagesCleRestant = u''
                            break

                if debugLevel > 0: print u' Filtre des doublons...'
                if PagesVoir != u'':
                    PagesVoir = PagesVoir + u'|'
                    while PagesVoir.find(u'|') != -1:
                        if PagesCleTotal.find(PagesVoir[:PagesVoir.find(u'|')]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PagesVoir[:PagesVoir.find(u'|')]
                        PagesVoir = PagesVoir[PagesVoir.find(u'|')+1:len(PagesVoir)]
                if debugLevel > 2: raw_input(PagesCleTotal.encode(config.console_encoding, 'replace'))

                if debugLevel > 0: print u' Balayage de toutes les pages "à voir"...'
                if PagesCleTotal != u'':
                    while PagesCleTotal[:1] == u'|': PagesCleTotal = PagesCleTotal[1:len(PagesCleTotal)]
                if PagesCleTotal != pageName:
                    if debugLevel > 0: print u'  Différent de la page courante'
                    PagesCleRestant = PagesCleTotal + u'|'
                    while PagesCleRestant.find(u'|') != -1:
                        currentPage = PagesCleRestant[:PagesCleRestant.find(u'|')]
                        if currentPage == u'':
                            if debugLevel > 0: print u'currentPage vide'
                            break
                        PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:len(PagesCleRestant)]
                        if currentPage != pageName:
                            pageCle = Page(site, currentPage)
                            pageContentCleBegin = getContentFromPage(pageCle)
                        else:
                            pageContentCleBegin = pageContent
                        if pageContentCleBegin != u'KO':
                            pageContentCle = pageContentCleBegin
                            if pageContentCle.find(u'{{voir/') != -1:
                                if debugLevel > 0: print u' {{voir/ trouvé'
                                break
                            elif pageContentCle.find(u'{{voir|') != -1:
                                if debugLevel > 0: print u' {{voir| trouvé'
                                if PagesCleTotal.find(u'|' + currentPage) != -1:
                                    pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|'):]
                                    pageContentCle = pageContentCle[:pageContentCle.find(u'{{voir|')+len(u'{{voir|')] \
                                     + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] \
                                     + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):] \
                                     + pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir|')+pageContentCle2.find('}}'):]
                                else:    # Cas du premier
                                    pageContentCle2 = pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir'):]
                                    pageContentCle = pageContentCle[:pageContentCle.find(u'{{voir|')+len(u'{{voir|')] \
                                     + PagesCleTotal[len(currentPage):] + pageContentCle[pageContentCle.find(u'{{voir|')+len(u'{{voir')+pageContentCle2.find('}}'):]
                                if pageContentCle != pageContentCleBegin:
                                    if currentPage == pageName:
                                        pageContent = pageContentCle
                                    else:
                                        if debugLevel > 0:
                                            print u' Première savePage dédiée à {{voir}}'
                                        else:
                                            savePage(pageCle, pageContentCle, summary)
                            else:
                                if PagesCleTotal.find(u'|' + currentPage) != -1:
                                    pageContentCle = u'{{voir|' + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] \
                                     + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):] + u'}}\n' + pageContentCle
                                else:    # Cas du premier
                                    pageContentCle = u'{{voir' + PagesCleTotal[len(currentPage):len(PagesCleTotal)] + u'}}\n' + pageContentCle
                                if currentPage == pageName:
                                    pageContent = pageContentCle
                                else:    
                                    if debugLevel > 0:
                                        print u' Deuxième savePage dédiée à {{voir}}'
                                    else:
                                        savePage(pageCle, pageContentCle, summary)

            elif pageContent.find(u'{{voir|') != -1:
                if debugLevel > 0: print u'  Identique à la page courante'
                pageContent2 = pageContent[pageContent.find(u'{{voir|'):len(pageContent)]
                if pageContent2.find(u'|' + pageName + u'|') != -1 and pageContent2.find(u'|' + pageName + u'|') < pageContent2.find('}}'):
                    pageContent = pageContent[:pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'|')] + pageContent[pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'|')+len(u'|' + pageName):]
                if pageContent2.find(u'|' + pageName + u'}') != -1 and pageContent2.find(u'|' + pageName + u'}') < pageContent2.find('}}'):
                    pageContent = pageContent[:pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'}')] + pageContent[pageContent.find(u'{{voir|') + pageContent2.find(u'|' + pageName + u'}')+len(u'|' + pageName):]

            if debugLevel > 0: print u' Nettoyage des {{voir}}...'
            if pageContent.find(u'{{voir}}\n') != -1: pageContent = pageContent[:pageContent.find(u'{{voir}}\n')] + pageContent[pageContent.find(u'{{voir}}\n')+len(u'{{voir}}\n'):len(pageContent)]
            if pageContent.find(u'{{voir}}') != -1: pageContent = pageContent[:pageContent.find(u'{{voir}}')] + pageContent[pageContent.find(u'{{voir}}')+len(u'{{voir}}'):len(pageContent)]
            pageContent = html2Unicode(pageContent)
            pageContent = pageContent.replace(u'}}&#32;[[', u'}} [[')
            pageContent = pageContent.replace(u']]&#32;[[', u']] [[')
            regex = ur'\[\[([^\]]*)\|\1\]\]'
            if re.search(regex, pageContent):
                if debugLevel > 0: print u'Lien interne inutile'
                pageContent = re.sub(regex, ur'[[\1]]', pageContent)

        if pageContent.find(u'{{vérifier création automatique}}') != -1:
            if debugLevel > 0: print u' {{vérifier création automatique}} trouvé'
            pageContent2 = pageContent
            LanguesV = u'|'
            while pageContent2.find(u'{{langue|') > 0:
                pageContent2 = pageContent2[pageContent2.find(u'{{langue|')+len(u'{{langue|'):]
                LanguesV += u'|' + pageContent2[:pageContent2.find('}}')]
            if LanguesV != u'|':
                pageContent = pageContent.replace(u'{{vérifier création automatique}}', u'{{vérifier création automatique' + LanguesV + '}}')
            if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))

        pageContent = pageContent.replace(u'{{clef de tri', u'{{clé de tri')
        #TODO: uca-default gère af, am, ar, as, ast, az, be, be-tarask, bg, bn, bn@collation=traditional, bo, br, bs, bs-Cyrl, ca, chr, co, cs, cy, da, de, de-AT@collation=phonebook, dsb, ee, el, en, eo, es, et, eu, fa, fi, fil, fo, fr, fr-CA, fur, fy, ga, gd, gl, gu, ha, haw, he, hi, hr, hsb, hu, hy, id, ig, is, it, ka, kk, kl, km, kn, kok, ku, ky, la, lb, lkt, ln, lo, lt, lv, mk, ml, mn, mo, mr, ms, mt, nb, ne, nl, nn, no, oc, om, or, pa, pl, pt, rm, ro, ru, rup, sco, se, si, sk, sl, smn, sq, sr, sr-Latn, sv, sv@collation=standard, sw, ta, te, th, tk, tl, to, tr, tt, uk, uz, vi, vo, yi, yo, zu
        if addDefaultSortKey:
            if debugLevel > 0: print u'Clés de tri'
            pageContent = addDefaultSort(pageName, pageContent)
        if removeDefaultSort:
            regex = ur'^[ 0-9a-zàçéèêëîôùûA-ZÀÇÉÈÊËÎÔÙÛ]+$'
            if u'{{langue|fr}}' in pageContent and re.search(regex, pageName):
                regex = ur"\n{{clé de tri([^}]*)}}"
                if re.search(regex, pageContent):
                    summary = summary + u', retrait de {{clé de tri}}'
                    pageContent = re.sub(regex, '', pageContent)

        if debugLevel > 0: print u'Catégories de prononciation'
        if pageName[-2:] == u'um' and pageContent.find(u'ɔm|fr}}') != -1:
            pageContent = addCategory(pageContent, u'fr', u'um prononcés /ɔm/ en français')
        if pageName[:2] == u'qu':
            regex = ur'{{pron\|kw[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'qu prononcés /kw/ en français')
        if pageName[:2] == u'qu':
            regex = ur'{{fr\-rég\|kw[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'qu prononcés /kw/ en français')
        if pageName[:2] == u'ch':
            regex = ur'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'ch':
            regex = ur'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'Ch':
            regex = ur'{{pron\|k[^}\|]+\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[:2] == u'Ch':
            regex = ur'{{fr\-rég\|k[^}\|]+}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-2:] == u'ch':
            regex = ur'{{pron\|[^}\|]+k\|fr}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-2:] == u'ch':
            regex = ur'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-3:] == u'chs':
            regex = ur'{{pron\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')
        if pageName[-3:] == u'chs':
            regex = ur'{{fr\-rég\|[^}\|]+k}}'
            if re.search(regex, pageContent):
                pageContent = addCategory(pageContent, u'fr', u'ch prononcés /k/ en français')

        if debugLevel > 1: print u'Formatage de la ligne de forme'
        pageContent = pageContent.replace(u'{{PAGENAME}}', u'{{subst:PAGENAME}}')
        pageContent = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", pageContent)
        pageContent = pageContent.replace(u'[[' + pageName + u']]', u'\'\'\'' + pageName + u'\'\'\'')
        pageContent = pageContent.replace(u'-rég}}\'\'\'', u'-rég}}\n\'\'\'')
        pageContent = pageContent.replace(u']] {{imperf}}', u']] {{imperf|nocat=1}}')
        pageContent = pageContent.replace(u']] {{perf}}', u']] {{perf|nocat=1}}')
        pageContent = pageContent.replace(u'{{perf}} / \'\'\'', u'{{perf|nocat=1}} / \'\'\'')
        pageContent = pageContent.replace(u'{{term|Blason}}', u'{{héraldique}}')
        pageContent = pageContent.replace(u'{{term|Art vétérinaire}}', u'{{vétérinaire}}')

        regex = ur'({{fr\-[^}]*\|[\'’]+=[^}]*)\|[\'’]+=[oui|1]'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|s=[^}]*)\|s=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|ms=[^}]*)\|ms=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        regex = ur'({{fr\-[^}]*\|fs=[^}]*)\|fs=[^}\|]*'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\1', pageContent)
        while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(pageContent):
            i1 = re.search(u'{{T\|.*\n\n\*[ ]*{{T\|', pageContent).end()
            pageContent = pageContent[:i1][:pageContent[:i1].rfind(u'\n')-1] + pageContent[:i1][pageContent[:i1].rfind(u'\n'):len(pageContent[:i1])] + pageContent[i1:]
        regex = u'{{(Latn|Grek|Cyrl|Armn|Geor|Hebr|Arab|Syrc|Thaa|Deva|Hang|Hira|Kana|Hrkt|Hani|Jpan|Hans|Hant|zh-mot|kohan|ko-nom|la-verb|grc-verb|polytonique|FAchar)[\|}]'
        if not re.search(regex, pageContent):
            if debugLevel > 0: print u'Ajout du mot vedette'
            pageContent = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n\{\{[^\n]*\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", pageContent)
        pageContent = pageContent.replace(u'num=1|num=', u'num=1')
        pageContent = pageContent.replace(u'&nbsp;', u' ')
        pageContent = pageContent.replace(u'\n #*', u'\n#*')
        pageContent = pageContent.replace(u'\n #:', u'\n#:')
        pageContent = pageContent.replace(u' }}', '}}')
        pageContent = pageContent.replace(u'|pinv= ', u'|pinv=')
        pageContent = pageContent.replace(u'|pinv=. ', u'|pinv=.')
        #pageContent = re.sub(ur'«[  \t]*', ur'« ', pageContent) # pb &#160;
        #pageContent = re.sub(ur'[  \t]*»', ur' »', pageContent)
        pageContent = pageContent.replace(u'{|\n|}', u'')
        regex = ur"({{S\|verbe\|en}} *=* *\n'*)to "
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"\1", pageContent)

        regex = ur'(=== {{S\|adjectif\|en}} ===\n[^\n]*) *{{pluriel \?\|en}}'
        pageContent = re.sub(regex, ur"\1", pageContent)

        if debugLevel > 0: print u'Formatage des modèles'
        pageContent = pageContent.replace(u'\n {{', u'\n{{')
        pageContent = pageContent.replace(u'{{louchébem|fr}}', u'{{louchébem}}')
        pageContent = pageContent.replace(u'{{reverlanisation|fr}}', u'{{reverlanisation}}')
        pageContent = pageContent.replace(u'{{verlan|fr}}', u'{{verlan}}')
        regex = ur"({{cf|)lang=[^\|}]+\|(:Catégorie:)"
        pageContent = re.sub(regex, ur"\1\2", pageContent)

        pageContent = pageContent.replace(u'|ko-hani}}', u'|ko-Hani}}')
        if debugLevel > 1: print u' Remplacements des anciens codes langue'
        oldTemplate = []
        newTemplate = []
        oldTemplate.append(u'ko-hanja')
        newTemplate.append(u'ko-Hani')
        oldTemplate.append(u'be-x-old')
        newTemplate.append(u'be-tarask')
        oldTemplate.append(u'zh-min-nan')
        newTemplate.append(u'nan')
        oldTemplate.append(u'lsf')
        newTemplate.append(u'fsl')
        oldTemplate.append(u'arg')
        newTemplate.append(u'an')
        oldTemplate.append(u'nav')
        newTemplate.append(u'nv')
        oldTemplate.append(u'prv')
        newTemplate.append(u'oc')
        oldTemplate.append(u'nds-NL')
        newTemplate.append(u'nds-nl')
        oldTemplate.append(u'gsw-FR')
        newTemplate.append(u'gsw-fr')
        oldTemplate.append(u'zh-sc')
        newTemplate.append(u'zh-Hans')
        oldTemplate.append(u'roa-rup')
        newTemplate.append(u'rup')
        for p in range(1, len(oldTemplate)):
            regex = ur'([\|{=])' + oldTemplate[p] + ur'([\|}])'
            if re.search(regex, pageContent):
                pageContent = re.sub(regex, ur'\1' + newTemplate[p] + ur'\2', pageContent)
        pageContent = pageContent.replace(u'{{WP|lang=sgs', u'{{WP|lang=bat-smg')
        pageContent = pageContent.replace(u'{{Source-wikt|nan|', u'{{Source-wikt|zh-min-nan|')

        pageContent = re.sub(ur'{{régio *\| *', ur'{{région|', pageContent)
        pageContent = re.sub(ur'{{terme *\| *', ur'{{term|', pageContent)
        pageContent = re.sub(ur'{{term *\|Registre neutre}} *', ur'', pageContent)
        pageContent = pageContent.replace(u'{{auxiliaire être}}', u'{{note-auxiliaire|fr|être}}')
        pageContent = pageContent.replace(u'{{Citation needed}}', u'{{réf ?}}')
        pageContent = pageContent.replace(u'{{f}} {{fsing}}', u'{{f}}')
        pageContent = pageContent.replace(u'{{m}} {{msing}}', u'{{m}}')
        pageContent = pageContent.replace(u'{{f}} {{p}}', u'{{fplur}}')
        pageContent = pageContent.replace(u'{{m}} {{p}}', u'{{mplur}}')
        pageContent = pageContent.replace(u'fm?', u'fm ?')
        pageContent = pageContent.replace(u'mf?', u'mf ?')
        pageContent = pageContent.replace(u'myt=scandinave', u'myt=nordique')
        pageContent = pageContent.replace(u'{{pron|}}', u'{{pron}}')
        pageContent = pageContent.replace(u'{{prononciation|}}', u'{{prononciation}}')
        pageContent = pageContent.replace(u'{{pron-rég|', u'{{écouter|')
        pageContent = pageContent.replace(u'{{Référence nécessaire}}', u'{{référence nécessaire}}')
        pageContent = pageContent.replace(u'religion|rel=chrétienne', u'christianisme')
        pageContent = pageContent.replace(u'religion|rel=islamique', u'islam')
        pageContent = pageContent.replace(u'religion|rel=musulmane', u'islam')
        pageContent = pageContent.replace(u'religion|rel=boudhiste', u'boudhisme')
        pageContent = pageContent.replace(u'religion|rel=juive', u'judaïsme')
        pageContent = pageContent.replace(u'religion|spéc=chrétienne', u'christianisme')
        pageContent = pageContent.replace(u'religion|spéc=islamique', u'islam')
        pageContent = pageContent.replace(u'religion|spéc=musulmane', u'islam')
        pageContent = pageContent.replace(u'religion|spéc=boudhiste', u'boudhisme')
        pageContent = pageContent.replace(u'religion|spéc=juive', u'judaïsme')
        pageContent = pageContent.replace(u'religion|fr|rel=chrétienne', u'christianisme|fr')
        pageContent = pageContent.replace(u'religion|fr|rel=islamique', u'islam|fr')
        pageContent = pageContent.replace(u'religion|fr|rel=musulmane', u'islam|fr')
        pageContent = pageContent.replace(u'religion|fr|rel=boudhiste', u'boudhisme|fr')
        pageContent = pageContent.replace(u'religion|fr|rel=juive', u'judaïsme|fr')
        pageContent = pageContent.replace(u'religion|nocat=1|rel=chrétienne', u'christianisme|nocat=1')
        pageContent = pageContent.replace(u'religion|nocat=1|rel=islamique', u'islam|nocat=1')
        pageContent = pageContent.replace(u'religion|nocat=1|rel=musulmane', u'islam|nocat=1')
        pageContent = pageContent.replace(u'religion|nocat=1|rel=boudhiste', u'boudhisme|nocat=1')
        pageContent = pageContent.replace(u'religion|nocat=1|rel=juive', u'judaïsme|nocat=1')
        pageContent = pageContent.replace(u'{{sexua|', u'{{sexe|')
        pageContent = pageContent.replace(u'— {{source|', u'{{source|')
        pageContent = pageContent.replace(u'- {{source|', u'{{source|')
        pageContent = pageContent.replace(u'{{term|Antiquité grecque}}', u'{{antiquité|spéc=grecque}}')
        pageContent = pageContent.replace(u'{{term|Antiquité romaine}}', u'{{antiquité|spéc=romaine}}')
        pageContent = pageContent.replace(u'{{antiquité|fr}} {{term|grecque}}', u'{{antiquité|spéc=grecque}}')
        pageContent = pageContent.replace(u'{{antiquité|fr}} {{term|romaine}}', u'{{antiquité|spéc=romaine}}')
        pageContent = pageContent.replace(u'#*: {{trad-exe|fr}}', u'')
        pageContent = pageContent.replace(u'\n{{WP', u'\n* {{WP')
        pageContent = pageContent.replace(u'\n \n', u'\n\n')

        # Factorisation des citations
        #regex = ur"(?:— \(|{{source\|)Cirad/Gret/MAE, ''Mémento de l['’]Agronome'', 1 *692 p(?:\.|ages), p(?:\.|age) ([0-9 ]+), 2002, Paris, France, Cirad/Gret/Ministère des Affaires [EÉ]trangères \(\+ 2 cdroms\)(?:\)|}})"
        #if re.search(regex, pageContent):
        #    pageContent = re.sub(regex, ur"{{Citation/Cirad/Gret/MAE/Mémento de l’Agronome|\1}}", pageContent)

        regex = ur"{{ *dés *([\|}])"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"{{désuet\1", pageContent)
        regex = ur"{{ *fam *([\|}])"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"{{familier\1", pageContent)
        regex = ur"{{ *péj *([\|}])"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"{{péjoratif\1", pageContent)
        regex = ur"{{ *vx *([\|}])"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"{{vieilli\1", pageContent)

        if debugLevel > 1: print u' Modèles alias en doublon'
        regex = ur"(\{\{figuré\|[^}]*\}\}) ?\{\{métaphore\|[^}]*\}\}"
        pattern = re.compile(regex)
        pageContent = pattern.sub(ur"\1", pageContent)
        regex = ur"(\{\{métaphore\|[^}]*\}\}) ?\{\{figuré\|[^}]*\}\}"
        pattern = re.compile(regex)
        pageContent = pattern.sub(ur"\1", pageContent)

        regex = ur"(\{\{départements\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        pageContent = pattern.sub(ur"\1", pageContent)

        regex = ur"(\{\{localités\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        pageContent = pattern.sub(ur"\1", pageContent)

        regex = ur"(\{\{provinces\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        pageContent = pattern.sub(ur"\1", pageContent)

        regex = ur"(\#\* {{ébauche\-exe\|[^}]*}})\n\#\*: {{trad\-exe\|[^}]*}}"
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur"\1", pageContent)

        if debugLevel > 1: print u' Modèles trop courts'
        pageContent = pageContent.replace(u'{{fp}}', u'{{fplur}}')
        pageContent = pageContent.replace(u'{{mp}}', u'{{mplur}}')
        pageContent = pageContent.replace(u'{{fp|fr}}', u'{{fplur}}')
        pageContent = pageContent.replace(u'{{mp|fr}}', u'{{mplur}}')
        pageContent = pageContent.replace(u'{{np}}', u'{{nlur}}')
        pageContent = pageContent.replace(u'{{fs}}', u'{{fsing}}')
        pageContent = pageContent.replace(u'{{mascul}}', u'{{au masculin}}')
        pageContent = pageContent.replace(u'{{fémin}}', u'{{au féminin}}')
        pageContent = pageContent.replace(u'{{femin}}', u'{{au féminin}}')
        pageContent = pageContent.replace(u'{{sing}}', u'{{au singulier}}')
        pageContent = pageContent.replace(u'{{plur}}', u'{{au pluriel}}')
        pageContent = pageContent.replace(u'{{pluri}}', u'{{au pluriel}}')
        pageContent = pageContent.replace(u'{{mascul|', u'{{au masculin|')
        pageContent = pageContent.replace(u'{{fémin|', u'{{au féminin|')
        pageContent = pageContent.replace(u'{{femin|', u'{{au féminin|')
        pageContent = pageContent.replace(u'{{sing|', u'{{au singulier|')
        pageContent = pageContent.replace(u'{{plur|', u'{{au pluriel|')
        pageContent = pageContent.replace(u'{{pluri|', u'{{au pluriel|')
        pageContent = pageContent.replace(u'{{dét|', u'{{déterminé|')
        pageContent = pageContent.replace(u'{{dén|', u'{{dénombrable|')
        pageContent = pageContent.replace(u'{{pl-cour}}', u'{{plus courant}}')
        pageContent = pageContent.replace(u'{{pl-rare}}', u'{{plus rare}}')
        pageContent = pageContent.replace(u'{{mf?}}', u'{{mf ?}}')
        pageContent = pageContent.replace(u'{{fm?}}', u'{{fm ?}}')

        pageContent = pageContent.replace(u'{{arbre|', u'{{arbres|')
        pageContent = pageContent.replace(u'{{arme|', u'{{armement|')
        pageContent = pageContent.replace(u'{{astro|', u'{{astronomie|')
        pageContent = pageContent.replace(u'{{bota|', u'{{botanique|')
        pageContent = pageContent.replace(u'{{électro|', u'{{électronique|')
        pageContent = pageContent.replace(u'{{équi|', u'{{équitation|')
        pageContent = pageContent.replace(u'{{ex|', u'{{e|')
        pageContent = pageContent.replace(u'{{gastro|', u'{{gastronomie|')
        pageContent = pageContent.replace(u'{{légume|', u'{{légumes|')
        pageContent = pageContent.replace(u'{{minéral|', u'{{minéralogie|')
        pageContent = pageContent.replace(u'{{myth|', u'{{mythologie|')
        pageContent = pageContent.replace(u'{{oiseau|', u'{{oiseaux|')
        pageContent = pageContent.replace(u'{{péj|', u'{{péjoratif|')
        pageContent = pageContent.replace(u'{{plante|', u'{{plantes|')
        pageContent = pageContent.replace(u'{{psycho|', u'{{psychologie|')
        pageContent = pageContent.replace(u'{{réseau|', u'{{réseaux|')
        pageContent = pageContent.replace(u'{{typo|', u'{{typographie|')
        pageContent = pageContent.replace(u'{{vêtement|', u'{{vêtements|')
        pageContent = pageContent.replace(u'{{en-nom-rég-double|', u'{{en-nom-rég|')
        pageContent = pageContent.replace(u'{{Valence|ca}}', u'{{valencien}}')
        pageContent = pageContent.replace(u'{{abrév|', u'{{abréviation|')
        pageContent = pageContent.replace(u'{{acron|', u'{{acronyme|')
        regex = ur"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation\|[^}]*)\|m=1}} de([ '])"
        pageContent = re.sub(regex, ur'\1}} De\2', pageContent)
        regex = ur"(\n: *(?:'*\([^)]+\)'*)? *(?:{{[^)]+}})? *(?:{{[^)]+}})? *{{abréviation)\|m=1(\|[^}]*)}} de([ '])"
        pageContent = re.sub(regex, ur'\1\2}} De\3', pageContent)
        regex = ur"(==== {{S\|dérivés autres langues}} ====" + ur"(:?\n\* *{{L\|[^\n]+)?"*10 + ur"\n\* *{{)T\|"
        for i in range(10):
            pageContent = re.sub(regex, ur'\1L|', pageContent)

        if debugLevel > 1: print u' Modèles trop longs'
        pageContent = pageContent.replace(u'{{boîte début', u'{{(')
        pageContent = pageContent.replace(u'{{boîte fin', u'{{)')
        pageContent = pageContent.replace(u'\n{{-}}', u'')

        if debugLevel > 1: print u' Ajout des modèles de référence' # les URL ne contiennent pas les diacritiques des {{PAGENAME}}
        while pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=') != -1:
            pageContent2 = pageContent[pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')+len(u'[http://www.sil.org/iso639-3/documentation.asp?id='):]
            pageContent = pageContent[:pageContent.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')] + u'{{R:SIL|' + pageContent2[:pageContent2.find(u' ')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
            summary = summary + u', ajout de {{R:SIL}}'
        while pageContent.find(u'[http://www.cnrtl.fr/definition/') != -1:
            pageContent2 = pageContent[pageContent.find(u'[http://www.cnrtl.fr/definition/')+len(u'[http://www.cnrtl.fr/definition/'):len(pageContent)]
            pageContent = pageContent[:pageContent.find(u'[http://www.cnrtl.fr/definition/')] + u'{{R:TLFi|' + pageContent2[:pageContent2.find(u' ')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
            summary = summary + u', ajout de {{R:TLFi}}'
        while pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/') != -1:
            pageContent2 = pageContent[pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/')+len(u'[http://www.mediadico.com/dictionnaire/definition/'):len(pageContent)]
            pageContent = pageContent[:pageContent.find(u'[http://www.mediadico.com/dictionnaire/definition/')] + u'{{R:Mediadico|' + pageContent2[:pageContent2.find(u'/1')] + '}}' + pageContent2[pageContent2.find(u']')+1:]
            summary = summary + u', ajout de {{R:Mediadico}}'

        importedSites = ['DAF8', 'Littré']
        for importedSite in importedSites:
            regex = ur'\n\** *{{R:' + importedSite + ur'}} *\n\** *({{Import:' + importedSite + ur'}})'
            if re.search(regex, pageContent):
                summary = summary + u', doublon {{R:' + importedSite + ur'}}'
                pageContent = re.sub(regex, ur'\n* \1', pageContent)
            regex = ur'\n\** *({{Import:' + importedSite + ur'}}) *\n\** *{{R:' + importedSite + ur'}}'
            if re.search(regex, pageContent):
                summary = summary + u', doublon {{R:' + importedSite + ur'}}'
                pageContent = re.sub(regex, ur'\n* \1', pageContent)

        if debugLevel > 1: print u' Retrait des catégories contenues dans les modèles'
        if pageContent.find(u'[[Catégorie:Villes') != -1 and pageContent.find(u'{{localités|') != -1:
            summary = summary + u', {{villes}} -> {{localités}}'
            pageContent = re.sub(ur'\n\[\[Catégorie:Villes[^\]]*\]\]', ur'', pageContent)

        if pageContent.find(u'\n[[Catégorie:Noms scientifiques]]') != -1 and pageContent.find(u'{{S|nom scientifique|conv}}') != -1:
            pageContent = pageContent.replace(u'\n[[Catégorie:Noms scientifiques]]', u'')

        if pageContent.find(u'\n[[Catégorie:Gentilés en français]]') != -1 and pageContent.find(u'{{note-gentilé|fr}}') != -1:
            pageContent = pageContent.replace(u'\n[[Catégorie:Gentilés en français]]', u'')

        if debugLevel > 0: print u' Modèles à déplacer'
        regex = ur'(==== {{S\|traductions}} ====)(\n{{ébauche\-trad[^}]*}})(\n{{trad-début}})'
        pageContent = re.sub(regex, ur'\1\3\2', pageContent)

        regex = ur'({{trad\-début}})\n*{{trad\-début}}'
        pageContent = re.sub(regex, ur'\1', pageContent)

        regex = ur'({{trad\-fin}})\n*{{trad\-fin}}'
        pageContent = re.sub(regex, ur'\1', pageContent)

        pageLanguages = getPageLanguages(pageContent)
        for pageLanguage in pageLanguages:
            etymTemplates = ['abréviation', 'acronyme', 'sigle']
            if pageLanguage == 'fr': etymTemplates = etymTemplates + ['louchébem', 'reverlanisation', 'verlan']
            for etymTemplate in etymTemplates:
                languageSection, lStart, lEnd = getLanguageSection(pageContent, pageLanguage)
                if languageSection is not None and len(getNaturesSections(languageSection)) == 1 and languageSection.find(etymTemplate[1:]) != -1:
                    # Si le modèle à déplacer est sur la ligne de forme ou de définition
                    regexTemplate = ur"\n'''[^\n]+(\n#)? *({{[^}]+}})? *({{[^}]+}})? *{{" + etymTemplate + ur'(\||})'
                    if re.search(regexTemplate, languageSection):
                        newLanguageSection, summary = removeTemplate(languageSection, etymTemplate, summary, inSection = natures)
                        #TODO generic moveFromNatureToEtymology = remove après (u'|'.join(natures)) + addToEtymology, = addToLine(languageCode, section, append, prepend)
                        etymology, sStart, sEnd = getSection(newLanguageSection, u'étymologie')
                        if etymology is None:
                            newLanguageSection = addLine(newLanguageSection, pageLanguage, u'étymologie', u': {{ébauche-étym|' + pageLanguage + u'}}')
                            etymology, sStart, sEnd = getSection(newLanguageSection, u'étymologie')
                        if etymology is not None and etymology.find(u'{{' + etymTemplate) == -1:
                            regexEtymology = ur'(=\n:* *(\'*\([^\)]*\)\'*)?) *'
                            if re.search(regexEtymology, pageContent):
                                etymology2 = re.sub(regexEtymology, ur'\1 {{' + etymTemplate + ur'}} ', etymology)
                                newLanguageSection = newLanguageSection.replace(etymology, etymology2)
                                if debugLevel > 2: raw_input(pageContent.encode(config.console_encoding, 'replace'))
                                summary = summary + u', [[Wiktionnaire:Prise de décision/Déplacer les modèles de contexte' \
                                + u' étymologiques dans la section « Étymologie »|ajout de {{' + etymTemplate + ur"}} dans l'étymologie]]"
                        pageContent = pageContent.replace(languageSection, newLanguageSection)

        if pageContent.find(u'{{ru-conj') != -1:
            finalPageContent = pageContent[:pageContent.find(u'{{ru-conj')]
            pageContent = pageContent[pageContent.find(u'{{ru-conj'):]
            Annexe = pageContent[:pageContent.find(u'\n')+1]
            pageContent = finalPageContent + pageContent[pageContent.find(u'\n')+1:]
            finalPageContent = u''
            pageAnnexe = Page(site, u'Annexe:Conjugaison en russe/' + pageName)
            AnnexeExistante = getContentFromPage(pageAnnexe)
            if pageAnnexe.exists():
                if AnnexeExistante == 'KO': return
            else:
                AnnexeExistante = u''
            savePage(pageAnnexe, AnnexeExistante + u'\n\n'+Annexe, u'Création à partir de l\'article')

        if debugLevel > 1: print u' Modèles de son' # Ex : {{écoutez | {{audio | | {{sound -> {{écouter
        pageContent = pageContent.replace(u'{{pron-rég|', u'{{écouter|')
        regex = ur'\* ?{{sound}} ?: \[\[Media:([^\|\]]*)\|[^\|\]]*\]\]'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'{{écouter|audio=\1}}', pageContent)
            summary = summary + u', conversion de modèle de son'
        regex = ur'\{{audio\|([^\|}]*)\|[^\|}]*}}'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'{{écouter|audio=\1}}', pageContent)
            summary = summary + u', conversion de modèle de son'
        regex = ur'\n *{{écouter\|'
        if re.search(regex, pageContent):
            pageContent = re.sub(regex, ur'\n* {{écouter|', pageContent)

        limitReg = 13
        ModRegion = range(1, limitReg)
        ModRegion[1] = u'AU'
        ModRegion[2] = u'AR'
        ModRegion[3] = u'AT'
        ModRegion[4] = u'BE'
        ModRegion[5] = u'BR'
        ModRegion[6] = u'CA'
        ModRegion[7] = u'MX'
        ModRegion[8] = u'PT'
        ModRegion[9] = u'QC'
        ModRegion[10] = u'UK'
        ModRegion[11] = u'US'
        for m in range(1, limitReg-1):
            while pageContent.find(u'{{écouter|' + ModRegion[m] + u'|') != -1:
                pageContent = pageContent[:pageContent.find(u'{{écouter|' + ModRegion[m] + u'|')+len('{{écouter|')-1] \
                 + '{{' + ModRegion[m] + u'|nocat=1}}' + pageContent[pageContent.find(u'{{écouter|' + ModRegion[m] + u'|')+len(u'{{écouter|' + ModRegion[m]):]

        if debugLevel > 1: print u' Modèles bandeaux' 
        while pageContent.find(u'\n{{colonnes|') != -1:
            if debugLevel > 0: pywikibot.output(u'\nTemplate: \03{blue}colonnes\03{default}')
            pageContent2 = pageContent[:pageContent.find(u'\n{{colonnes|')]
            if pageContent2.rfind('{{') != -1 and pageContent2.rfind('{{') == pageContent2.rfind(u'{{trad-début'):    # modèles impriqués dans trad
                pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(pageContent)]
                if pageContent2.find(u'\n}}\n') != -1:
                    if pageContent2[:len(u'titre=')] == u'titre=':
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):len(pageContent)]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début|' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] \
                         + '}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                    else:
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(pageContent)]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 1'
                    break

            elif pageContent2.rfind('{{') != -1 and pageContent2.rfind('{{') == pageContent2.rfind(u'{{('):    # modèles impriqués ailleurs
                if debugLevel > 0: pywikibot.output(u'\nTemplate: \03{blue}(\03{default}')
                pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(pageContent)]
                if pageContent2.find(u'\n}}\n') != -1:
                    if pageContent2[:len(u'titre=')] == u'titre=':
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(|' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] + '}}' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                    else:
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 2'
                    break

            elif pageContent2.rfind('{{') != -1 and (pageContent2.rfind('{{') == pageContent2.rfind(u'{{trad-fin') or pageContent2.rfind('{{') == pageContent2.rfind(u'{{S|trad')):
                # modèle à utiliser dans {{S|trad
                pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(pageContent)]
                if pageContent2.find(u'\n}}\n') != -1:
                    if pageContent2[:len(u'titre=')] == u'titre=':
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début|' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] + '}}' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                    else:
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{trad-fin}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{trad-début}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 3'
                    break

            else:    # modèle ailleurs que {{S|trad
                pageContent2 = pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                if pageContent2.find(u'\n}}\n') != -1:
                    if pageContent2[:len(u'titre=')] == u'titre=':
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(|' \
                         + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')] \
                         + '}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'|')+1:]
                    else:
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')] \
                         + u'\n{{)}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+pageContent2.find(u'\n}}\n')+len(u'\n}}'):]
                        pageContent = pageContent[:pageContent.find(u'\n{{colonnes|')] + u'\n{{(}}' + pageContent[pageContent.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 4'
                    break
            while pageContent.find(u'}}1=') != -1:
                pageContent = pageContent[:pageContent.find(u'}}1=')] + pageContent[pageContent.find(u'}}1=')+len(u'}}1='):len(pageContent)]

        if debugLevel > 0: print u'#* or #:'
        finalPageContent = u''
        while pageContent.find(u'\n#:') != -1:
            finalPageContent = finalPageContent + pageContent[:pageContent.find(u'\n#:')+2]
            if finalPageContent.rfind(u'{{langue|') == finalPageContent.rfind(u'{{langue|fr}}'):
                pageContent = u'*' + pageContent[pageContent.find(u'\n#:')+len(u'\n#:'):len(pageContent)]
            else:
                pageContent = u':' + pageContent[pageContent.find(u'\n#:')+len(u'\n#:'):len(pageContent)]
        pageContent = finalPageContent + pageContent
        finalPageContent = u''

        
        if pageContent.find(u'{{langue|fr}}') != -1:

            # Ajout des redirections des pronominaux
            if pageContent.find(u'{{S|verbe|fr}}') != -1 and pageName[:3] != u'se' and pageName[:2] != u's’':
                pageContent2 = pageContent[pageContent.find(u'{{S|verbe|fr}}'):]
                regex = ur'(\n|\')s(e |’)\'\'\''
                if re.search(regex, pageContent2) is not None:
                    if re.search(regex, pageContent2) < pageContent2.find(u'{{S|') or pageContent2.find(u'{{S|') == -1:
                        regex = ur'^[aeiouyàéèêôù]'
                        if re.search(regex, pageName):    # ne pas prendre [:1] car = & si encodage ASCII du paramètre DOS / Unix
                            pageName2 = u's’' + pageName
                        else:
                            pageName2 = u'se ' + pageName
                        page2 = Page(site, pageName2)
                        if not page2.exists():
                            if debugLevel > 0: print u'Création de ' + defaultSort(pageName2)
                            summary2 = u'Création d\'une redirection provisoire catégorisante du pronominal'
                            savePage(page2, u'#REDIRECT[[' + pageName + u']]\n<!-- Redirection temporaire avant de créer le verbe pronominal -->\n[[Catégorie:Wiktionnaire:Verbes pronominaux à créer en français]]', summary2)

            # Ajout de modèles pour les gentités et leurs adjectifs
            if debugLevel > 0: print u'Gentilés'
            regex = ur'({{fr\-[^}]+)\\'
            while re.search(regex, pageContent):
                pageContent = re.sub(regex, ur'\1', pageContent)

            ligne = 6
            colonne = 4
            # TODO : fusionner avec le tableau des modèles de flexion
            ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
            ModeleGent[1][1] = ur'fr-accord-mixte'
            ModeleGent[1][2] = ur's'
            ModeleGent[1][3] = ur'e'
            ModeleGent[1][4] = ur'es'
            ModeleGent[2][1] = ur'fr-accord-s'
            ModeleGent[2][2] = ur''
            ModeleGent[2][3] = ur'e'
            ModeleGent[2][4] = ur'es'
            ModeleGent[3][1] = ur'fr-accord-el'
            ModeleGent[3][2] = ur's'
            ModeleGent[3][3] = ur'le'
            ModeleGent[3][4] = ur'les'
            ModeleGent[4][1] = ur'fr-accord-en'
            ModeleGent[4][2] = ur's'
            ModeleGent[4][3] = ur'ne'
            ModeleGent[4][4] = ur'nes'
            ModeleGent[5][1] = ur'fr-accord-et'
            ModeleGent[5][2] = ur's'
            ModeleGent[5][3] = ur'te'
            ModeleGent[5][4] = ur'tes'
            ModeleGent[6][1] = ur'fr-rég'
            ModeleGent[6][2] = ur's'
            ModeleGent[6][3] = ur''
            ModeleGent[6][4] = ur's'

            for l in range(1, ligne + 1):
                # Depuis un masculin
                regex = ur'\({{p}} : [\[\']*' + rePageName + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + rePageName + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageName + ModeleGent[l][4] + ur'[\]\']*\)'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', pageContent)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                # Depuis un féminin
                if ModeleGent[l][1] == ur'fr-accord-s' and rePageName[-1:] == u'e' and rePageName[-2:-1] == u's':
                    regex = ur'\({{p}} : [\[\']*' + rePageName + ur's[\]\']*, {{m}} : [\[\']*' + rePageName[:-1] + ur'[\]\']*\)'
                    if re.search(regex, pageContent):
                        pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|ms=' + rePageName[:-1].replace(u'\\', u'') + '}}', pageContent)
                        summary = summary + u', conversion des liens flexions en modèle boite'
                regex = ur'\({{f}} : [\[\']*' + rePageName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + rePageName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageName + ModeleGent[l][4] + ur'[\]\']*\)'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', pageContent)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                if debugLevel > 1: print u' avec son'
                regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|[pron\=]*)}}'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\n\4\2}}\1\2\3', pageContent)

                regex = ur'( ===\n)(\'\'\'[^\n]+)({{' + ModeleGent[l][1] + ur'\|[^}]*}})'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\1\3\n\2', pageContent)
                    summary = summary + u', déplacement des modèles de flexions'


            if debugLevel > 0: print u'Traductions manquantes'
            # Si la définition du mot (dit "satellite") ne renvoie pas vers un autre, les centralisant
            regex = ur'(fr\|flexion|' + u'|'.join(definitionSentences) + u'|' + u'|'.join(map(unicode.capitalize, definitionSentences)) + ur')'
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

            # TODO: contrôle du nombre de paragraphes de traduction par rapport au nombre de sens

        if pageContent.find(u'{{langue|es}}') != -1:
            ligne = 1
            colonne = 4
            ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
            ModeleGent[1][1] = ur'es-accord-oa'
            ModeleGent[1][2] = ur'os'
            ModeleGent[1][3] = ur'a'
            ModeleGent[1][4] = ur'as'
            rePageRadicalName = re.escape(pageName[:-1])

            for l in range(1, ligne + 1):
                regex = ur'\({{p}} : [\[\']*' + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' \
                 + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', pageContent)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                regex = ur'\({{f}} : [\[\']*' + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' \
                 + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
                if debugLevel > 1: print regex.encode(config.console_encoding, 'replace')
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', pageContent)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                # Son
                if debugLevel > 0: print u' son'
                regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|' + rePageRadicalName + ur')}}'
                if re.search(regex, pageContent):
                    pageContent = re.sub(regex, ur'\n\4|\2}}\1\2\3', pageContent)

        pageContent, summary = sort_translations(pageContent, summary)

        if debugLevel > 0: print (u'Gestion des codes langues dans les modèles')
        addLanguageCode = False # Certaines sections interdisent les modèles de domaine catégorisant
        if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
        translationSection = False
        backward = False # Certains modèles nécessitent d'être déplacés puis retraités
        languageCode = None
        if debugLevel > 0: print u' languageCode = None'
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

# Recherche de chaque modèle
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
                    if debugLevel > 0: print u' Page à formater manuellement'
                    finalPageContent = u'{{formater|Section de langue manquante, avant le modèle ' + currentTemplate + u' (au niveau du ' + str(len(finalPageContent)) + u'-ème caractère)}}\n' + finalPageContent + pageContent
                    summary = u'Page à formater manuellement'
                    savePage(page, finalPageContent, summary)
                    return

                elif currentTemplate == u'caractère':
                    languageCode = u'conv'
                    addLanguageCode = False
                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif currentTemplate == u'langue':
                    languageCode = pageContent[endPosition+1:pageContent.find('}}')]
                    if languageCode == u'':
                        if debugLevel > 0: print u' code langue vide'
                        return
                    if debugLevel > 0: print u' code langue trouvé : ' + languageCode
                    regex = ur'[a-zA-Z\-]+'
                    if not re.search(regex, languageCode):
                        finalPageContent = u'{{formater|Code langue incorrect : ' + languageCode + u'}}\n' + finalPageContent + pageContent
                        summary = u'Page à formater manuellement'
                        savePage(page, finalPageContent, summary)
                        if debugLevel > 1: print u'Page à formater manuellement'
                        return
                    addLanguageCode = True

                    # Ajout des anagrammes pour cette nouvelle langue détectée
                    if languageCode == u'conv':
                        regex = ur'[= ]*{{S\|anagrammes}}[^}]+\|conv}}\n'
                        if re.compile(regex).search(pageContent):
                            if debugLevel > 0: print u'Retrait d\'anagramme en conv'
                            finalPageContent2 = pageContent[:re.compile(regex).search(pageContent).start()]
                            pageContent2 = pageContent[re.compile(regex).search(pageContent).end():]
                            delta = re.compile(regex).search(pageContent).end()
                            regex = ur'[^}]+\|conv}}\n'
                            while re.compile(regex).search(pageContent2):
                                if debugLevel > 0: print u' autre anagramme en conv'
                                delta = delta + re.compile(regex).search(pageContent2).end()
                                pageContent2 = pageContent2[re.compile(regex).search(pageContent2).end():]
                            pageContent = finalPageContent2 + pageContent[delta:]

                    elif debugLevel == 0 and pageContent.find(u'S|erreur|' + languageCode) == -1 and pageContent.find(u'S|faute|' + languageCode) == -1 \
                     and languageCode != u'conv' and pageName[:1] != u'-' and pageName[-1:] != u'-': #and pageName != u'six':
                        if debugLevel > 0: print u' Anagrammes pour ' + languageCode
                        if pageContent.find(u'{{S|anagr') == -1 and pageName.find(u' ') == -1 and len(pageName) <= anagramsMaxLength:
                            anagrammes = anagram(pageName)
                            ListeAnagrammes = u''
                            for anagramme in anagrammes:
                                if anagramme != pageName:
                                    if debugLevel > 0: print anagramme.encode(config.console_encoding, 'replace')
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
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'\n=== {{S|voir')] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'\n=== {{S|voir'):len(pageContent)]
                                elif pageContent2.find(u'\n=== {{S|références}}') != -1 and ((pageContent2.find(u'{{langue|') != -1 and pageContent2.find(u'\n=== {{S|références}}') < pageContent2.find(u'{{langue|')) or pageContent2.find(u'{{langue|') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'\n=== {{S|références}}')] +  u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'\n=== {{S|références}}'):]
                                elif pageContent2.find(u'== {{langue|') != -1 and ((pageContent2.find(u'[[Catégorie:') != -1 and pageContent2.find(u'== {{langue|') < pageContent2.find(u'[[Catégorie:')) or pageContent2.find(u'[[Catégorie:') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'== {{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'== {{langue|'):len(pageContent)]
                                elif pageContent2.find(u'=={{langue|') != -1 and ((pageContent2.find(u'[[Catégorie:') != -1 and pageContent2.find(u'=={{langue|') < pageContent2.find(u'[[Catégorie:')) or pageContent2.find(u'[[Catégorie:') == -1):
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'=={{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'=={{langue|'):len(pageContent)]        
                                elif pageContent2.find(u'{{clé de tri') != -1:
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'{{clé de tri')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'{{clé de tri'):len(pageContent)]
                                elif pageContent2.find(u'[[Catégorie:') != -1:
                                    pageContent = pageContent[:positionAnagr+pageContent2.find(u'[[Catégorie:')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[positionAnagr+pageContent2.find(u'[[Catégorie:'):len(pageContent)]
                                else:
                                    if debugLevel > 0: print " Ajout avant les interwikis"
                                    regex = ur'\n\[\[\w?\w?\w?:'
                                    if re.compile(regex).search(pageContent):
                                        try:
                                            pageContent = pageContent[:re.search(regex,pageContent).start()] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + pageContent[re.search(regex,pageContent).start():]
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
                        if debugLevel > 0: print u' Section introuvable : ' + section
                        return
                    if debugLevel > 0: print str(' ') + section.encode(config.console_encoding, 'replace')

                    if Section.index(section) < limit1:
                        if debugLevel > 1: print u' Paragraphe définition'
                        addLanguageCode = True # Paragraphe avec code langue dans les modèles lexicaux
                        translationSection = False

                        if languageCode is None:
                            languageCode = pageContent[endPosition+1+len(section)+1:pageContent.find('}}')]
                            if debugLevel > 0: print u'  ajout du {{langue|' + languageCode + u'}} manquant'
                            pageContent = '== {{langue|' + languageCode + u'}} ==\n' + finalPageContent[finalPageContent.rfind('==='):] + pageContent
                            finalPageContent = finalPageContent[:finalPageContent.rfind('===')]
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
                                if debugLevel > 0: print u' ajout de "clé="'
                                tempPageName = defaultSort(tempPageName)
                                pageContent = pageContent[:pageContent.find('}}')] + u'|clé=' + tempPageName + pageContent[pageContent.find('}}'):]

                    else:
                        addLanguageCode = False # Paragraphe sans code langue dans les modèles lexicaux et les titres
                        translationSection = False

                        if section == u'homophones':
                            if debugLevel > 0: print ' Catégorisation des homophones'
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
                                        pageContent = pageContent[:pageContent.find(u'\n')] + u'\n{{trad-début}}' + pageContent[pageContent.find(u'\n'):]
                                        pageContent2 = pageContent[pageContent.find(u'{{trad-début}}\n')+len(u'{{trad-début}}\n'):]
                                        if pageContent2.find(u'\n') == -1:
                                            pageContent = pageContent + u'\n'
                                            pageContent2 = pageContent2 + u'\n'
                                        while pageContent2.find(u'{{' + t + u'|') < pageContent2.find(u'\n') and pageContent2.find(u'{{' + t + u'|') != -1:
                                            pageContent2 = pageContent2[pageContent2.find(u'\n')+1:]
                                        pageContent = pageContent[:len(pageContent)-len(pageContent2)] + u'{{trad-fin}}\n' + pageContent[len(pageContent)-len(pageContent2):]
                        elif section == u'traductions à trier':
                            translationSection = True

                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif currentTemplate in [u'term', u'région']:
                    
                    rawTerm = pageContent[endPosition+1:pageContent.find('}}')]
                    term = trim(rawTerm.replace('[[', '').replace(']]', ''))
                    if term.find('|') != -1: term = term[:term.find('|')]
                    if debugLevel > 0: print " terminologie ou régionalisme 1 = " + term
                    templatePage = getContentFromPageName(u'Template:' + term, allowedNamespaces = [u'Template:'])
                    if templatePage.find(u'Catégorie:Modèles de domaine') == -1 and templatePage.find(u'{{région|') == -1 and term[:1] != term[:1].lower():
                        term = term[:1].lower() + term[1:]
                        if debugLevel > 0: print u' terminologie ou régionalisme 2 = ' + term
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
                        # Tri des lettres de l'API
                        if currentTemplate == u'pron':
                            pageContent2 = pageContent[endPosition+1:pageContent.find('}}')]
                            while pageContent2.find(u'\'') != -1 and pageContent2.find(u'\'') < pageContent2.find('}}') and (pageContent2.find(u'\'') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u'\'')] + u'ˈ' + pageContent[pageContent.find(u'\'')+1:]
                            while pageContent2.find(u'ˈˈˈ') != -1 and pageContent2.find(u'ˈˈˈ') < pageContent2.find('}}') and (pageContent2.find(u'ˈˈˈ') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u'ˈˈˈ')] + u'\'\'\'' + pageContent[pageContent.find(u'ˈˈˈ')+3:]
                            while pageContent2.find(u'ε') != -1 and pageContent2.find(u'ε') < pageContent2.find('}}') and (pageContent2.find(u'ε') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u'ε')] + u'ɛ' + pageContent[pageContent.find(u'ε')+1:]
                            while pageContent2.find(u'ε̃') != -1 and pageContent2.find(u'ε̃') < pageContent2.find('}}') and (pageContent2.find(u'ε̃') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u'ε̃')] + u'ɛ̃' + pageContent[pageContent.find(u'ε̃')+1:]
                            while pageContent2.find(u':') != -1 and pageContent2.find(u':') < pageContent2.find('}}') and (pageContent2.find(u':') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u':')] + u'ː' + pageContent[pageContent.find(u':')+1:]
                            while pageContent2.find(u'g') != -1 and pageContent2.find(u'g') < pageContent2.find('}}') and (pageContent2.find(u'g') < pageContent2.find(u'|') or pageContent2.find(u'|') == -1): pageContent = pageContent[:pageContent.find(u'g')] + u'ɡ' + pageContent[pageContent.find(u'g')+1:]
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
                    pageContent2 = pageContent[endPosition+1:]
                    # Saut des modèles régionnaux
                    if (pageContent2.find('lang=') == -1 or pageContent2.find('lang=') > pageContent2.find('}}')) and \
                        (currentTemplate != u'cf' or pageContent2.find('}}') > endPosition+1 and (pageContent2.find(':') == -1 or pageContent2.find(':') > pageContent2.find('}}'))):
                        while pageContent2.find('{{') < pageContent2.find('}}') and pageContent2.find('{{') != -1:
                            pageContent2 = pageContent2[pageContent2.find('}}')+2:]
                        if pageContent2.find('lang=') == -1 or pageContent2.find('lang=') > pageContent2.find('}}'):
                            finalPageContent = finalPageContent + currentTemplate + u'|lang=' + languageCode + pageContent[endPosition:pageContent.find('}}')+2]
                            pageContent = pageContent[pageContent.find('}}')+2:]
                        else:
                            finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                    else:
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)

                elif currentTemplate in (u'référence nécessaire', u'réf?', u'réf ?', u'refnec', u'réfnéc', u'source?', \
                    u'réfnéc'):
                    pageContent2 = pageContent[endPosition+1:len(pageContent)]
                    if pageContent2.find("lang=") == -1 or pageContent2.find("lang=") > pageContent2.find('}}'):
                        finalPageContent = finalPageContent + currentTemplate + u'|lang=' + languageCode + pageContent[endPosition:pageContent.find('}}')+2]
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
                if debugLevel > 0:
                    print ' Recherche des modèles de langue désuets'
                    templatePage = getContentFromPageName(u'Template:' + currentTemplate, allowedNamespaces = [u'Template:'])
                    if templatePage.find(u'{{modèle désuet de code langue}}') != -1:
                        if debugLevel > 0: print u' Remplacements de l\'ancien modèle de langue'
                        pageContent = u'subst:nom langue|' + currentTemplate + pageContent[pageContent.find(u'}}'):]
                        pageContent = pageContent.replace(u'{{' + currentTemplate + u'}}', u'{{subst:nom langue|' + currentTemplate + u'}}')
                        finalPageContent, pageContent = nextTemplate(finalPageContent, pageContent)
                else:
                    if debugLevel > 0: pywikibot.output(u"\n\03{blue}Modèle inconnu\03{default} " + currentTemplate)
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

        finalPageContent = finalPageContent + pageContent


        if debugLevel > 0: print u'Formatage des flexions'
        if debugLevel > 1: print u' fr'
        regex = ur"(=== {{S\|nom\|fr)\|flexion(}} ===\n(?:{{fr[^\n]*\n)*'''" + rePageName + ur"''' [^\n]*{{fsing}})"
        if re.search(regex, finalPageContent):
            finalPageContent = re.sub(regex, ur'\1\2', finalPageContent)
            summary = summary + u', un nom féminin n\'est pas une flexion en français'
        regex = ur"(=== {{S\|nom\|fr)\|flexion(}} ===\n(?:{{fr[^\n]*\n)*'''" + rePageName + ur"''' [^\n]*{{f}}\n# *'*[Ff]éminin (?:de|singulier))"
        if re.search(regex, finalPageContent):
            finalPageContent = re.sub(regex, ur'\1\2', finalPageContent)
            summary = summary + u', un nom féminin n\'est pas une flexion en français'

        if pageName.find(u'*') == -1 and pageName[-1:] == 's':
            language = u'fr'
            naturesWithPlural = ['nom', 'adjectif', 'suffixe']
            singularPageName = getLemmaFromPlural(finalPageContent, language, naturesWithPlural)
            if singularPageName != u'': treatPageByName(singularPageName) # Formatage des boites de flexion à récupérer
            for nature in naturesWithPlural:
                regex = ur"(== {{langue|" + language + ur"}} ==\n=== {{S\|" + nature + ur"\|" + language + ur")\|num=2"
                if re.search(regex, finalPageContent):
                    finalPageContent = re.sub(regex, ur'\1', finalPageContent)
                    summary = summary + u', retrait de |num='

                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur")(\}} ===\n[^\n]*\n*'''" + rePageName + ur"'''[^\n]*\n# *'*'*(Masculin)*(Féminin)* *[P|p]luriel de *'*'* *\[\[)"
                if re.search(regex, finalPageContent):
                    finalPageContent = re.sub(regex, ur'\1|flexion\2', finalPageContent)
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
                                if re.search(regex, finalPageContent):
                                    finalPageContent = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}', finalPageContent)
                                    summary = summary + u', remplacement de {{' + language + ur'-rég}} par {{' + lemmaFlexionTemplate + ur'}}'
                            '''

                            if lemmaFlexionTemplate != u'':
                                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''')"
                                if re.search(regex, finalPageContent):
                                    finalPageContent = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}\n\2', finalPageContent)
                                    summary = summary + u', ajout de {{' + lemmaFlexionTemplate + ur'}} depuis le lemme'

                    if pageName[-1:] != 's':
                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)(\|" + language + ur"}}\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, finalPageContent):
                            #finalPageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=\7|\3}}\n\2\3\4\7', finalPageContent)
                            finalPageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + singularPageName + u'|\3}}\n\2\3\4\5', finalPageContent)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, finalPageContent):
                            finalPageContent = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + singularPageName + u'|}}\n\2\5', finalPageContent)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

            if debugLevel > 1: raw_input(finalPageContent.encode(config.console_encoding, 'replace'))

            if debugLevel > 1: print u' en'
            if pageName[-2:] != 'ss' and pageName[-3:] != 'hes' and pageName[-3:] != 'ies' and pageName[-3:] != 'ses' and pageName[-3:] != 'ves':
                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)([s|z]\|en}}\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, finalPageContent):
                    finalPageContent = re.sub(regex, ur'\1{{en-nom-rég|sing=\5|\3}}\n\2\3\4\5', finalPageContent)
                    summary = summary + u', ajout de {{en-nom-rég}}'

                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, finalPageContent):
                    finalPageContent = re.sub(regex, ur'\1{{en-nom-rég|sing=\3|}}\n\2\3', finalPageContent)
                    summary = summary + u', ajout de {{en-nom-rég}}'


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
                if debugLevel > 1: print ' m1'

            regex = ur"{{genre *\?*\|fr}}(\n# *'* *[Ff]éminin)"
            if re.search(regex, finalPageContent):
                finalPageContent = re.sub(regex, ur'{{f}}\1', finalPageContent)
                summary = summary + u', précision du genre f'
                if debugLevel > 1: print ' f1'

            if finalPageContent.find(u'{{genre|fr}}') != -1 or finalPageContent.find(u'{{genre ?|fr}}') != -1:
                mSuffixes = ['eur', 'eux', 'ant', 'age', 'ier', 'ien', 'ois', 'ais', 'isme', 'el', 'if', 'ment', 'ments'] # pas "é" : adaptabilité
                for mSuffix in mSuffixes:
                    if pageName[-len(mSuffix):] == mSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{m}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{m}}")
                        summary = summary + u', précision du genre m'
                        if debugLevel > 1: print ' m2'
                        break

                fSuffixes = ['euse', 'ante', 'ance', 'ette', 'ienne', 'rie', 'oise', 'aise', 'logie', 'tion', 'ité', 'elle', 'ive']
                for fSuffix in fSuffixes:
                    if pageName[-len(fSuffix):] == fSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{f}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{f}}")
                        summary = summary + u', précision du genre f'
                        if debugLevel > 1: print ' f2'
                        break

                mfSuffixes = ['iste']
                for mfSuffix in mfSuffixes:
                    if pageName[-len(mfSuffix):] == mfSuffix:
                        finalPageContent = finalPageContent.replace(u"{{genre|fr}}", u"{{mf}}")
                        finalPageContent = finalPageContent.replace(u"{{genre ?|fr}}", u"{{mf}}")
                        summary = summary + u', précision du genre mf'
                        if debugLevel > 1: print ' mf1'
                        break

                if singularPageName != u'':
                    lemmaGender = getGenderFromPageName(singularPageName)
                    if lemmaGender != '':
                        finalPageContent = finalPageContent.replace(u'{{genre|fr}}', lemmaGender)
                        finalPageContent = finalPageContent.replace(u'{{genre ?|fr}}', lemmaGender)
                        summary = summary + u', précision du genre ' + lemmaGender
                        if debugLevel > 1: print ' loc'


        # Liens vers les annexes de conjugaisons
        LanguesC = [ (u'es',u'ar',u'arsi',u'er',u'ersi',u'ir',u'irsi'),
                     (u'pt',u'ar',u'ar-se',u'er',u'er-se',u'ir',u'ir-se'),
                     (u'it',u'are',u'arsi',u'ere',u'ersi',u'ire',u'irsi'),
                     (u'fr',u'er',u'er',u'ir',u'ir',u're',u'ar'),
                     (u'ru',u'',u'',u'',u'',u'',u'')
                   ]
        if not ' ' in pageName and not pageName in [u'ça va', u'ché', u'estoufaresse', u'estoufarès', u'reco', u'rpz'] and finalPageContent.find(u'{{voir-conj') == -1 and finalPageContent.find(u'[[Image:') == -1:
        # Sinon bugs (ex : https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687, https://fr.wiktionary.org/w/index.php?title=%C3%A7a_va&diff=next&oldid=21742913)
            if debugLevel > 0: print u'Ajout de {{conj}}'
            for l in LanguesC:
                if not (l[0] == u'fr' and pageName[-3:] == u'ave'):
                    if re.compile(ur'{{S\|verbe\|'+l[0]+'}}').search(finalPageContent) and not re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[= ]+\n+[^\n]*\n*[^\n]*\n*{{(conj[a-z1-3\| ]*|invar)').search(finalPageContent):
                        if debugLevel > 0: print u' {{conj|'+l[0]+u'}} manquant'
                        if re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}').search(finalPageContent):
                            if debugLevel > 0: print u' ajout de {{conj|'+l[0]+u'}} après {{pron|...}}'
                            try:
                                i1 = re.search(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}',finalPageContent).end()
                                finalPageContent = finalPageContent[:i1] + u' {{conjugaison|'+l[0]+'}}' + finalPageContent[i1:]
                            except:
                                if debugLevel > 0: print u' Erreur l 5390'
                        else:
                            if debugLevel > 0: print u' pas de prononciation pour ajouter {{conj}}'
    
        if finalPageContent.find(u'{{conj') != -1:
            if debugLevel > 0: print u' Ajout des groupes dans {{conj}}'
            '''for (langue,premier,ppron,deuxieme,dpron,troisieme,tpron) in LanguesC:
                if premier != u'':

                    if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + '}}').search(finalPageContent) and not re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}.*\n*.*{{conj[a-z1-3\| ]*').search(finalPageContent):
                        if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*\n*[ ^\[]*{{pron\|').search(finalPageContent):
                            if pageName[len(pageName)-len(premier):] == premier or pageName[len(pageName)-len(ppron):] == ppron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',finalPageContent).end()
                                    finalPageContent = finalPageContent[:i1] + u' {{conj|grp=1|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + premier
                            elif pageName[len(pageName)-len(premier):] == deuxieme or pageName[len(pageName)-len(ppron):] == dpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',finalPageContent).end()
                                    finalPageContent = finalPageContent[:i1] + u' {{conj|grp=2|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + deuxieme
                            elif pageName[len(pageName)-len(premier):] == troisieme or pageName[len(pageName)-len(ppron):] == tpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',finalPageContent).end()
                                    finalPageContent = finalPageContent[:i1] + u' {{conj|grp=3|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + troisieme
                        else:
                            if pageName[len(pageName)-len(premier):] == premier or pageName[len(pageName)-len(ppron):] == ppron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*\'\'\'',finalPageContent).end()
                                    if finalPageContent[i1:].find(u'{{conj') != -1 and finalPageContent[i1:].find(u'{{conj') < finalPageContent[i1:].find(u'\n') and (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + '}}' + finalPageContent[i1:]
                                    elif finalPageContent[i1:].find(u'{{pron') != -1 and finalPageContent[i1:].find(u'{{pron') < finalPageContent[i1:].find(u'\n') and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        pageContent2 = finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron'):len(finalPageContent[i1:])]
                                        finalPageContent = finalPageContent[:i1] + finalPageContent[i1:][:finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2] + u' {{conj|grp=1|' + langue + '}}' + finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2:len(finalPageContent[i1:])]
                                    elif (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')) and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=1|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
                            elif pageName[len(pageName)-len(premier):] == deuxieme or pageName[len(pageName)-len(ppron):] == dpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',finalPageContent).end()
                                    if finalPageContent[i1:].find(u'{{conj') != -1 and finalPageContent[i1:].find(u'{{conj') < finalPageContent[i1:].find(u'\n') \
                                     and (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + '}}' + finalPageContent[i1:]
                                    elif finalPageContent[i1:].find(u'{{pron') != -1 and finalPageContent[i1:].find(u'{{pron') < finalPageContent[i1:].find(u'\n') \
                                     and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        pageContent2 = finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron'):len(finalPageContent[i1:])]
                                        finalPageContent = finalPageContent[:i1] + finalPageContent[i1:][:finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2] \
                                         + u' {{conj|grp=2|' + langue + '}}' + finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2:len(finalPageContent[i1:])]
                                    elif (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')) \
                                     and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=2|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
                            elif pageName[len(pageName)-len(premier):] == troisieme or pageName[len(pageName)-len(ppron):] == tpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',finalPageContent).end()
                                    if finalPageContent[i1:].find(u'{{conj') != -1 and finalPageContent[i1:].find(u'{{conj') < finalPageContent[i1:].find(u'\n') \
                                     and (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + '}}' + finalPageContent[i1:]
                                    elif finalPageContent[i1:].find(u'{{pron') != -1 and finalPageContent[i1:].find(u'{{pron') < finalPageContent[i1:].find(u'\n') \
                                     and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        pageContent2 = finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron'):len(finalPageContent[i1:])]
                                        finalPageContent = finalPageContent[:i1] + finalPageContent[i1:][:finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2] \
                                         + u' {{conj|grp=3|' + langue + '}}' + finalPageContent[i1:][finalPageContent[i1:].find(u'{{pron')+pageContent2.find('}}')+2:len(finalPageContent[i1:])]
                                    elif (finalPageContent[i1:].find(u'{{pron') == -1 or finalPageContent[i1:].find(u'{{pron') > finalPageContent[i1:].find(u'\n')) \
                                     and (finalPageContent[i1:].find(u'{{conj') == -1 or finalPageContent[i1:].find(u'{{conj') > finalPageContent[i1:].find(u'\n')):
                                        finalPageContent = finalPageContent[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=3|' + langue + '}}' + finalPageContent[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
            '''

        language = 'fr' # TODO: intl
        if finalPageContent.find(u'{{langue|' + language + u'}}') != -1:

            #if debugLevel > 0: print u'\nSynchro des prononciations'
            #finalPageContent = addPronunciationFromContent(finalPageContent, language)  

            if debugLevel > 0: print u'Faux homophones car lemme et sa flexion' # TODO: locutions
            #TODO Doublon systématique ? singularPageName = getLemmaFromContent(finalPageContent, language)
            flexionPageName = ''
            if finalPageContent.find('|' + language + '|flexion}}') == -1:
                # Recherche d'éventuelles flexions dans la page du lemme
                flexionTemplate = getFlexionTemplate(pageName, language)
                if flexionTemplate.find(u'inv=') == -1 and \
                 (flexionTemplate[:flexionTemplate.find('|')] in flexionTemplatesFrWithS \
                 or flexionTemplate[:flexionTemplate.find('|')] in flexionTemplatesFrWithMs):
                    flexionPageName = getParameter(flexionTemplate, 'p')
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

    else:
        finalPageContent = pageContent

    regex = ur'([^\n=])(===?=? *{{S\|)'
    if re.search(regex, finalPageContent):
        finalPageContent = re.sub(regex, ur'\1\n\n\2', finalPageContent)
    finalPageContent = finalPageContent.replace(u'===== {{S|note}} ===== =====', u'===== {{S|note}} =====')

    if debugLevel > 1 and username in pageName: finalPageContent = addLineTest(finalPageContent)
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
        print "Aucun changement"


p = PageProvider(treatPageByName, site, debugLevel)
setGlobals(debugLevel, site, username)
setGlobalsWiktionary(debugLevel, site, username)
def main(*args):
    global waitAfterHumans
    if len(sys.argv) > 1:
        if debugLevel > 1: print sys.argv
        afterPage = u''
        if len(sys.argv) > 2: afterPage = sys.argv[2]

        if sys.argv[1] == u'-test':
            treatPageByName(u'User:' + username + u'/test')
        elif sys.argv[1] == u'-test2':
            treatPageByName(u'User:' + username + u'/test2')
        elif sys.argv[1] == u'-page' or sys.argv[1] == u'-p':
            waitAfterHumans = False
            #treatPageByName(u'Utilisateur:JackBot/test unitaire')
            treatPageByName(u'à loilpé')
        elif sys.argv[1] == u'-file' or sys.argv[1] == u'-txt':
            waitAfterHumans = False
            p.pagesByFile(u'src/lists/articles_' + siteLanguage + u'_' + siteFamily + u'.txt', )
        elif sys.argv[1] == u'-dump' or sys.argv[1] == u'-xml':
            regex = None
            testPage = None
            if testPage is not None:
                pageContent = getContentFromPageName(testPage)
                if re.search(regex, pageContent, re.MULTILINE| re.DOTALL):
                    print 'bon ok'
                else:
                    print 'ko'
                pageContent = getContentFromPageName(u'Utilisateur:JackBot/test unitaire')
                if re.search(regex, pageContent, re.MULTILINE| re.DOTALL):
                    print 'ok'
                else:
                    print 'bon ko'
                return

            if len(sys.argv) > 2:
                regex = sys.argv[2]
            else:
                #TODO
                #regex = ur'{{trad\-fin}}\n*\*{{T\|'
                #regex = ur'{{S\|traductions}} *=*\n{{ébauche\-trad'
                regex = ur'{{trad-début}}\n*{{trad-début}}'
            #p.pagesByXML(siteLanguage + siteFamily + '.*xml', regex = regex)
            p.pagesByXML(siteLanguage + siteFamily + '.*xml', regex = u'=== {{S\|adjectif\|en}} ===\n[^\n]*{{pluriel \?\|en}}')
            #p.pagesByXML(siteLanguage + siteFamily + '\-.*xml', regex = regex, include = u'verbe|it|flexion', exclude = u'it-verbe-flexion'
        elif sys.argv[1] == u'-u':
            p.pagesByUser(u'User:' + username, numberOfPagesToTreat = 4000)
        elif sys.argv[1] == u'-search' or sys.argv[1] == u'-s' or sys.argv[1] == u'-r':
            if len(sys.argv) > 2:
                p.pagesBySearch(sys.argv[2])
            else:
                p.pagesBySearch(u'insource:"{{S|dérivés autres langues}}"', afterPage = u'радъ')
        elif sys.argv[1] == u'-link' or sys.argv[1] == u'-l' or sys.argv[1] == u'-template' or sys.argv[1] == u'-m':
            p.pagesByLink(u'Template:hi', afterPage = afterPage)
            p.pagesByLink(u'Template:ur', afterPage = afterPage)
        elif sys.argv[1] == u'-category' or sys.argv[1] == u'-cat' or sys.argv[1] == u'-c':
            p.pagesByCat(u'Modèles désuets de code langue', namespaces = [0, 14], linked = True)
            #p.pagesByCat(u'Appels de modèles incorrects:abréviation', afterPage = afterPage, recursive = False, namespaces = [14])
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
        # Daily:
        p.pagesByCat(u'Catégorie:Wiktionnaire:Terminologie sans langue précisée', recursive = True)
        p.pagesByCat(u'Catégorie:Wiktionnaire:Flexions à vérifier', recursive = True)
        p.pagesByCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée')
        p.pagesByCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet')
        p.pagesByCat(u'Catégorie:Appels de modèles incorrects:deet')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Ébauches à compléter')
        p.pagesByLink(u'Template:trad')
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
        #p.pagesByLink(u'Template:clé de tri')

if __name__ == "__main__":
    main(sys.argv)

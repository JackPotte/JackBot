#!/usr/bin/env python
# coding: utf-8
'''
Ce script formate les pages du Wiktionnaire, tous les jours après minuit depuis le labs Wikimedia :
1) Retire certains doublons de modèles et d'espaces.
2) Ajoute les clés de tris, prononciations vides, et certains liens vers les conjugaisons.
3) Met à jour les liens vers les traductions (modèles trad, trad+, trad-, trad-début et trad-fin), et les classe par ordre alphabétique.
4) Ajoute les codes langues appropriés dans les modèles du Wiktionnaire du namespace 0 et paragraphes appropriés (dont "nocat=1" si une catégorie le justifie).
5) Complète les flexions de verbes en français à vérifier.
6) Gère des modèles {{voir}} en début de page.
7) Ajoute les anagrammes (pour les petits mots)
8) Teste les URL et indique si elles sont brisées avec {{lien brisé}}, et les transforme en modèle s'il existe pour leur site
9) Remplace les modèles catégorisés comme obsolètes
10) Créer des liens absents : http://fr.wiktionary.org/w/index.php?title=radiateur&diff=prev&oldid=14443668
11) Détecte les modèles à ajouter : http://fr.wiktionary.org/w/index.php?title=cl%C3%A9&diff=prev&oldid=14443625
12) Crée les redirection d'apostrophe dactylographique vers apostrophe typographique
Testé ici : http://fr.wiktionary.org/w/index.php?title=Utilisateur%3AJackBot%2Ftest&diff=14533806&oldid=14533695
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
addDefaultSort = False
anagramsMaxLength = 4   # sinon trop long : 5 > 5 min, 8 > 1 h par page)


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


Modele = [] # Liste des modèles du site à traiter
Section = [] # Sections à remplacer
# Paragraphes autorisant les modèles catégorisants par langue ({{voir| et {{voir/ sont gérés individuellement)
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_type_de_mot_du_Wiktionnaire
Modele.append(u'-adj-dem-')
Section.append(u'adjectif d��monstratif')
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
Modele.append(u'ablat')
Modele.append(u'ablatif')
Modele.append(u'abrév')
Modele.append(u'abréviation')
Modele.append(u'abréviation de')
Modele.append(u'accord genre ?')
Modele.append(u'accus')
Modele.append(u'accusatif')
Modele.append(u'acoustique')
Modele.append(u'acron')
Modele.append(u'acronyme')
Modele.append(u'admin')
Modele.append(u'administration')
Modele.append(u'adverbes de lieu')
Modele.append(u'adverbes de temps')
Modele.append(u'adverbes interrogatif')
Modele.append(u'aéro')
Modele.append(u'aéronautique')
Modele.append(u'affectueux')
Modele.append(u'agri')
Modele.append(u'agriculture')
Modele.append(u'agronomie')
Modele.append(u'aïkido')
Modele.append(u'alcools')
Modele.append(u'algèbre‎')
Modele.append(u'algèbre linéaire')
Modele.append(u'algues‎')
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
Modele.append(u'Antiquité')
Modele.append(u'antiquité')
Modele.append(u'aphérèse')
Modele.append(u'apiculture')
Modele.append(u'apiculture')
Modele.append(u'apocope')
Modele.append(u'apocope familière')
Modele.append(u'arbres')
Modele.append(u'arch')
Modele.append(u'archaïque')
Modele.append(u'archaïsme')
Modele.append(u'archéo')
Modele.append(u'archéologie')
Modele.append(u'archi')
Modele.append(u'architecture')
Modele.append(u'architecture des ordinateurs')
Modele.append(u'argot')
Modele.append(u'argot militaire')
Modele.append(u'argot policier')
Modele.append(u'argot polytechnicien')
Modele.append(u'argot scolaire')
Modele.append(u'arme')
Modele.append(u'armement')
Modele.append(u'armes')
Modele.append(u'armes à feu')
Modele.append(u'armes blanches')
Modele.append(u'arthropodes')
Modele.append(u'artillerie')
Modele.append(u'arts')
Modele.append(u'arts martiaux')
Modele.append(u'astrol')
Modele.append(u'astrologie')
Modele.append(u'astron')
Modele.append(u'astronautique')
Modele.append(u'astronomie')
Modele.append(u'assurance')
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
Modele.append(u'bactéries')
Modele.append(u'bactério')
Modele.append(u'bactériologie')
Modele.append(u'badminton')
Modele.append(u'bandes dessinées')
Modele.append(u'baseball')
Modele.append(u'bases de données')
Modele.append(u'basket')
Modele.append(u'bateaux')
Modele.append(u'BD')
Modele.append(u'BDD')
Modele.append(u'bibliothéconomie')
Modele.append(u'bijou')
Modele.append(u'bijouterie')
Modele.append(u'billard')
Modele.append(u'biochimie')
Modele.append(u'biol')
Modele.append(u'biologie')
Modele.append(u'biologie cellulaire')
Modele.append(u'biophysique')
Modele.append(u'bivalves')
Modele.append(u'boissons')
Modele.append(u'botan')
Modele.append(u'botanique')
Modele.append(u'boucherie')
Modele.append(u'bouddhisme')
Modele.append(u'bowling')
Modele.append(u'boxe')
Modele.append(u'calendrier')
Modele.append(u'camélidés')
Modele.append(u'canoe')
Modele.append(u'canoë')
Modele.append(u'canoë-kayak')
Modele.append(u'capoeira')
Modele.append(u'capoeira')
Modele.append(u'cardin')
Modele.append(u'cardinal')
Modele.append(u'carnivore')
Modele.append(u'cartes')
Modele.append(u'catch')
Modele.append(u'caténatif')
Modele.append(u'catholicisme')
Modele.append(u'CB')
Modele.append(u'cépages')
Modele.append(u'céphalopodes')
Modele.append(u'céramique')
Modele.append(u'céréales')
Modele.append(u'cétacés')
Modele.append(u'chaînes de montagnes')
Modele.append(u'champignons')
Modele.append(u'charpenterie')
Modele.append(u'chasse')
Modele.append(u'chats')
Modele.append(u'chaussures')
Modele.append(u'chevaux')
Modele.append(u'chiens')
Modele.append(u'chim')
Modele.append(u'chimie')
Modele.append(u'chimie inorganique')
Modele.append(u'chimie organique')
Modele.append(u'chimie physique')
Modele.append(u'chir')
Modele.append(u'chiromancie')
Modele.append(u'chirurgie')
Modele.append(u'christianisme')
Modele.append(u'chronologie')
Modele.append(u'ciné')
Modele.append(u'cinéma')
Modele.append(u'cirque')
Modele.append(u'cocktails')
Modele.append(u'coiffure')
Modele.append(u'coléoptères')
Modele.append(u'colorimétrie')
Modele.append(u'combat')
Modele.append(u'comm')
Modele.append(u'commerce')
Modele.append(u'commerces')
Modele.append(u'comparatif de')
Modele.append(u'composants')
Modele.append(u'composants électriques')
Modele.append(u'composants électroniques')
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
Modele.append(u'course à pied')
Modele.append(u'cout')
Modele.append(u'couture')
Modele.append(u'couvre-chefs')
Modele.append(u'crabes')
Modele.append(u'créatures')
Modele.append(u'cricket')
Modele.append(u'crimes')
Modele.append(u'criminels')
Modele.append(u'crustacés')
Modele.append(u'cuis')
Modele.append(u'cuisine')
Modele.append(u'cycl')
Modele.append(u'cyclisme')
Modele.append(u'danse')
Modele.append(u'danses')
Modele.append(u'datif')
Modele.append(u'dén')
Modele.append(u'dénombrable')
Modele.append(u'dénominal de')
Modele.append(u'dentisterie')
Modele.append(u'dépendant')
Modele.append(u'déris')
Modele.append(u'dérision')
Modele.append(u'dérision')
Modele.append(u'dermat')
Modele.append(u'dermatologie')
Modele.append(u'déserts')
Modele.append(u'desserts')
Modele.append(u'dessin')
Modele.append(u'désuet')
Modele.append(u'détroits')
Modele.append(u'déverbal')
Modele.append(u'déverbal de')
Modele.append(u'déverbal sans suffixe')
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
Modele.append(u'droit')
Modele.append(u'droit de propriété')
Modele.append(u'droit du travail')
Modele.append(u'droit féodal')
Modele.append(u'ébauche-trad-exe')
Modele.append(u'trad-exe')
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
Modele.append(u'éléments')
Modele.append(u'élevage')
Modele.append(u'ellipse')
Modele.append(u'enclitique')
Modele.append(u'enfantin')
Modele.append(u'entom')
Modele.append(u'entomol')
Modele.append(u'entomologie')
Modele.append(u'enzymes')
Modele.append(u'épices')
Modele.append(u'épithète')
Modele.append(u'équi')
Modele.append(u'équitation')
Modele.append(u'escalade')
Modele.append(u'escrime')
Modele.append(u'établissements')
Modele.append(u'ethnobiologie')
Modele.append(u'ethnologie')
Modele.append(u'ethnonymes')
Modele.append(u'étoiles')
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
Modele.append(u'félins')
Modele.append(u'ferro')
Modele.append(u'ferroviaire')
Modele.append(u'fig.')
Modele.append(u'figure')
Modele.append(u'figuré')
Modele.append(u'figures')
Modele.append(u'finan')
Modele.append(u'finance')
Modele.append(u'fiscalité')
Modele.append(u'fleurs')
Modele.append(u'fonderie')
Modele.append(u'fontainerie')
Modele.append(u'foot')
Modele.append(u'football')
Modele.append(u'football américain')
Modele.append(u'football canadien')
Modele.append(u'footing')
Modele.append(u'formel')
Modele.append(u'fortification')
Modele.append(u'fromages')
Modele.append(u'fruits')
Modele.append(u'gall')
Modele.append(u'gallicisme')
Modele.append(u'gastro')
Modele.append(u'gastron')
Modele.append(u'gastronomie')
Modele.append(u'gâteaux')
Modele.append(u'gén-indén')
Modele.append(u'généal')
Modele.append(u'généalogie')
Modele.append(u'généralement indénombrable')
Modele.append(u'généralement pluriel')
Modele.append(u'généralement singulier')
Modele.append(u'génétique')
Modele.append(u'génit')
Modele.append(u'génitif')
Modele.append(u'génitif')
Modele.append(u'genre')
Modele.append(u'genre ?')
Modele.append(u'genres musicaux')
Modele.append(u'gentilés')
Modele.append(u'gentilés ?')
Modele.append(u'géog')
Modele.append(u'geog')    # à remplacer ?
Modele.append(u'géographie')
Modele.append(u'geol')
Modele.append(u'géol')
Modele.append(u'géologie')
Modele.append(u'géom')
Modele.append(u'géomatique')
Modele.append(u'géométrie')
Modele.append(u'géoph')
Modele.append(u'géophysique')
Modele.append(u'germanisme')
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
Modele.append(u'gymnastique')
Modele.append(u'hand')
Modele.append(u'handball')
Modele.append(u'hapax')
Modele.append(u'hérald')
Modele.append(u'héraldique')
Modele.append(u'hindouisme')
Modele.append(u'hippisme')
Modele.append(u'hispanisme')
Modele.append(u'hist')
Modele.append(u'hist')
Modele.append(u'histoire')
Modele.append(u'histol')
Modele.append(u'histologie')
Modele.append(u'histologie')
Modele.append(u'horlogerie')
Modele.append(u'horticulture')
Modele.append(u'humour')
Modele.append(u'hydraulique')
Modele.append(u'hydrobiologie')
Modele.append(u'hyperb')
Modele.append(u'hyperbole')
Modele.append(u'i')
Modele.append(u'ichtyo')
Modele.append(u'ichtyologie')
Modele.append(u'idiotisme')
Modele.append(u'illégalité')
Modele.append(u'impers')
Modele.append(u'impersonnel')
Modele.append(u'impr')
Modele.append(u'imprimerie')
Modele.append(u'improprement')
Modele.append(u'indéc')
Modele.append(u'indécl')
Modele.append(u'indéclinable')
Modele.append(u'indéfini')
Modele.append(u'indén')
Modele.append(u'indénombrable')
Modele.append(u'indus')
Modele.append(u'industrie')
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
Modele.append(u'instruments')
Modele.append(u'instruments de mesure')
Modele.append(u'insultes')
Modele.append(u'intelligence artificielle')
Modele.append(u'interjection')
Modele.append(u'Internet')
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
Modele.append(u'jeu vidéo')
Modele.append(u'jeux')
Modele.append(u'jeux de cartes')
Modele.append(u'jeux vidéo')
Modele.append(u'joaillerie')
Modele.append(u'jogging')
Modele.append(u'jonglage')
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
Modele.append(u'législation')
Modele.append(u'légumes')
Modele.append(u'léporidé')
Modele.append(u'lézards')
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
Modele.append(u'machines')
Modele.append(u'maçon')
Modele.append(u'maçonnerie')
Modele.append(u'magnétisme')
Modele.append(u'mah-jong')
Modele.append(u'mahjong')
Modele.append(u'maintenance')
Modele.append(u'majong')
Modele.append(u'maladies de l’œil')
Modele.append(u'maladie')
Modele.append(u'maladies')
Modele.append(u'mammifères')
Modele.append(u'marbrerie')
Modele.append(u'mari')
Modele.append(u'marine')
Modele.append(u'marketing')
Modele.append(u'maroquinerie')
Modele.append(u'marsupial')
Modele.append(u'math')
Modele.append(u'mathématiques')
Modele.append(u'méca')
Modele.append(u'mécanique')
Modele.append(u'méd')
Modele.append(u'méde')
Modele.append(u'médecine')
Modele.append(u'médecine non conv')
Modele.append(u'média')
Modele.append(u'médicaments')
Modele.append(u'mélio')
Modele.append(u'mélioratif')
Modele.append(u'menuiserie')
Modele.append(u'mers')
Modele.append(u'métal')
Modele.append(u'métallurgie')
Modele.append(u'métaph')
Modele.append(u'métaphore')
Modele.append(u'métaplasmes')
Modele.append(u'météo')
Modele.append(u'météorol')
Modele.append(u'météorologie')
Modele.append(u'méton')
Modele.append(u'métonymie')
Modele.append(u'métrol')
Modele.append(u'métrologie')
Modele.append(u'meuble')
Modele.append(u'mf ?')
Modele.append(u'fm ?')
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
Modele.append(u'mot-valise')
Modele.append(u'motocyclisme')
Modele.append(u'Moyen Âge')
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
Modele.append(u'narratol')
Modele.append(u'narratologie')
Modele.append(u'nata')
Modele.append(u'natation')
Modele.append(u'navig')
Modele.append(u'navigation')
Modele.append(u'néol')
Modele.append(u'néol litt')
Modele.append(u'néologisme')
Modele.append(u'neuro')
Modele.append(u'neurologie')
Modele.append(u'noblesse')
Modele.append(u'nom')
Modele.append(u'nombre')
Modele.append(u'nomin')
Modele.append(u'nominatif')
Modele.append(u'nosologie')
Modele.append(u'novlangue')
Modele.append(u'nucl')
Modele.append(u'nucléaire')
Modele.append(u'numis')
Modele.append(u'numismatique')
Modele.append(u'nutrition')
Modele.append(u'obsolète')
Modele.append(u'oenol')
Modele.append(u'oenologie')
Modele.append(u'œnologie')
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
Modele.append(u'paléo')
Modele.append(u'paléographie')
Modele.append(u'paléontol')
Modele.append(u'paléontologie')
Modele.append(u'palindrome')
Modele.append(u'palmiers')
Modele.append(u'papeterie')
Modele.append(u'papèterie')
Modele.append(u'papillons')
Modele.append(u'par analogie')
Modele.append(u'par dérision')
Modele.append(u'par ellipse')
Modele.append(u'parataxe')
Modele.append(u'passif')
Modele.append(u'pâtes')
Modele.append(u'pathologie')
Modele.append(u'patin')
Modele.append(u'pâtisserie')
Modele.append(u'paume')
Modele.append(u'pays')
Modele.append(u'pêch')
Modele.append(u'pêche')
Modele.append(u'pêches')
Modele.append(u'pédol')
Modele.append(u'pédologie')
Modele.append(u'peinture')
Modele.append(u'péjoratif')
Modele.append(u'perroquets')
Modele.append(u'pétanque')
Modele.append(u'pétro')
Modele.append(u'pétrochimie')
Modele.append(u'pétrochimie')
Modele.append(u'peu attesté')
Modele.append(u'peu usité')
Modele.append(u'peuplier')
Modele.append(u'pharma')
Modele.append(u'pharmacie')
Modele.append(u'pharmacol')
Modele.append(u'pharmacologie')
Modele.append(u'philo')
Modele.append(u'philosophie')
Modele.append(u'phobies')
Modele.append(u'phon')
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
Modele.append(u'plantes')
Modele.append(u'plantes aromatiques')
Modele.append(u'plongée')
Modele.append(u'plurale tantum')
Modele.append(u'pluriel')
Modele.append(u'pluriel ?')
Modele.append(u'poés')
Modele.append(u'poésie')
Modele.append(u'poet')
Modele.append(u'poét')
Modele.append(u'poétique')
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
Modele.append(u'positions')
Modele.append(u'ppart')
Modele.append(u'préhistoire')
Modele.append(u'prépositionnel')
Modele.append(u'presse')
Modele.append(u'prestidigitation')
Modele.append(u'prnl')
Modele.append(u'probabilités')
Modele.append(u'prog')
Modele.append(u'programmation')
Modele.append(u'pronl')
Modele.append(u'pronominal')
Modele.append(u'propre')
Modele.append(u'propriété')
Modele.append(u'protéines')
Modele.append(u'protestantisme')
Modele.append(u'protocoles')
Modele.append(u'prov')
Modele.append(u'proverbe')
Modele.append(u'proverbes')
Modele.append(u'proverbial')
Modele.append(u'psych')
Modele.append(u'psychia')
Modele.append(u'psychiatrie')
Modele.append(u'psycho')
Modele.append(u'psycho')
Modele.append(u'psychol')
Modele.append(u'psychologie')
Modele.append(u'psychotropes')
Modele.append(u'rare')
Modele.append(u'récip')
Modele.append(u'réciproque')
Modele.append(u'réfl')
Modele.append(u'réfléchi')
Modele.append(u'réflexif')
Modele.append(u'reli')
Modele.append(u'religieux')
Modele.append(u'religion')
Modele.append(u'religions')
Modele.append(u'reliure')
Modele.append(u'repro')
Modele.append(u'reproduction')
Modele.append(u'reptiles')
Modele.append(u'réseau')
Modele.append(u'réseaux')
Modele.append(u'réseaux informatiques')
Modele.append(u'rhéto')
Modele.append(u'rhétorique')
Modele.append(u'robotiques')
Modele.append(u'roches')
Modele.append(u'rongeur')
Modele.append(u'rugby')
Modele.append(u'running')
Modele.append(u'saccusatif')
Modele.append(u'saisons')
Modele.append(u'salades')
Modele.append(u'sandwitchs')
Modele.append(u'satellites')
Modele.append(u'saules')
Modele.append(u'saut en hauteur')
Modele.append(u'sci-fi')
Modele.append(u'scientifiques')
Modele.append(u'sciences')
Modele.append(u'scol')
Modele.append(u'scolaire')
Modele.append(u'Scrabble')
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
Modele.append(u'sigle')
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
Modele.append(u'sport')
Modele.append(u'sport de combat')
Modele.append(u'sport de glisse')
Modele.append(u'sport mécanique')
Modele.append(u'sportifs')
Modele.append(u'sports')
Modele.append(u'sports de combat')
Modele.append(u'sports de glisse')
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
Modele.append(u'tauromachie')
Modele.append(u'td')
Modele.append(u'tech')
Modele.append(u'technique')
Modele.append(u'techno')
Modele.append(u'technol')
Modele.append(u'technologie')
Modele.append(u'télé')
Modele.append(u'télécom')
Modele.append(u'télécommunications')
Modele.append(u'télévision')
Modele.append(u'temps')
Modele.append(u'temps géologiques')
Modele.append(u'tennis')
Modele.append(u'tennis de table')
Modele.append(u'term')
Modele.append(u'terme non standard')
Modele.append(u'territoires')
Modele.append(u'text')
Modele.append(u'textile')
Modele.append(u'textiles')
Modele.append(u'théât')
Modele.append(u'théâtre')
Modele.append(u'théol')
Modele.append(u'théologie')
Modele.append(u'théorie des graphes')
Modele.append(u'thermodynamique')
Modele.append(u'tind')
Modele.append(u'tissage')
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
Modele.append(u'trans')
Modele.append(u'transit')
Modele.append(u'transitif')
Modele.append(u'transp')
Modele.append(u'transport')
Modele.append(u'travail')
Modele.append(u'très familier')
Modele.append(u'très rare')
Modele.append(u'très-rare')
Modele.append(u'très très rare')
Modele.append(u'type')
Modele.append(u'typo')
Modele.append(u'typographie')
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
Modele.append(u'véhicules')
Modele.append(u'vents')
Modele.append(u'vers')
Modele.append(u'vête')
Modele.append(u'vêtements')
Modele.append(u'vétérinaire')
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
Modele.append(u'wiki')
Modele.append(u'xénarthres')
Modele.append(u'yoga')
Modele.append(u'zool')
Modele.append(u'zoologie')
limit7 = len(Modele)
# Code langue quoi qu'il arrive
Modele.append(u'ébauche-syn')
Modele.append(u'non standard')
Modele.append(u'note-gentilé')
Modele.append(u'ébauche-trans')
Modele.append(u'ébauche-étym-nom-scientifique')
Modele.append(u'ébauche-étym')
Modele.append(u'ébauche-déf')
Modele.append(u'ébauche-exe')
Modele.append(u'ébauche-pron')
Modele.append(u'ébauche')
Modele.append(u'...')
limit8 = len(Modele)
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
limit9 = len(Modele) # Somme des modèles traités
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

# https://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Mod%C3%A8les_d%E2%80%99accord_en_fran%C3%A7ais
flexionTemplatesWithMs = []
flexionTemplatesWithMs.append(u'fr-accord-ain')
flexionTemplatesWithMs.append(u'fr-accord-al')
flexionTemplatesWithMs.append(u'fr-accord-an')
flexionTemplatesWithMs.append(u'fr-accord-cons')
flexionTemplatesWithMs.append(u'fr-accord-eau')
flexionTemplatesWithMs.append(u'fr-accord-el')
flexionTemplatesWithMs.append(u'fr-accord-en')
flexionTemplatesWithMs.append(u'fr-accord-er')
flexionTemplatesWithMs.append(u'fr-accord-et')
flexionTemplatesWithMs.append(u'fr-accord-in')
flexionTemplatesWithMs.append(u'fr-accord-mixte')
flexionTemplatesWithMs.append(u'fr-accord-on')
flexionTemplatesWithMs.append(u'fr-accord-ot')
flexionTemplatesWithMs.append(u'fr-accord-rég')
flexionTemplatesWithMs.append(u'fr-accord-s')
flexionTemplatesWithMs.append(u'fr-accord-un')

flexionTemplatesWithS = []
flexionTemplatesWithS.append(u'fr-rég')
flexionTemplatesWithS.append(u'fr-rég-x')
#TODO: autres = fr-accord-mf-ail, fr-accord-mf-al, fr-accord-comp, fr-accord-comp-mf, fr-accord-eur, fr-accord-eux, fr-accord-f, fr-inv, fr-accord-ind, fr-accord-mf, fr-accord-oux, fr-accord-personne, fr-accord-t-avant1835


def treatPageByName(pageName):
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
    if not hasMoreThanTime(page): return
    PageBegin = getContentFromPage(page, 'All')
    if PageBegin == 'KO': return
    PageTemp = PageBegin
    PageEnd = u''
    CleTri = defaultSort(pageName)
    rePageName = re.escape(pageName)

    PageTemp = globalOperations(PageTemp)
    if fixFiles: PageTemp = replaceFilesErrors(PageTemp)
    if fixTags: PageTemp = replaceDepretacedTags(PageTemp)
    if checkURL: PageTemp = hyperlynx(PageTemp)

    #if page.namespace() == 14:
        #if pageName.find(u'Catégorie:Lexique en français d') != -1 and PageTemp.find(u'[[Catégorie:Lexiques en français|') == -1:
        #    PageTemp = PageTemp + u'\n[[Catégorie:Lexiques en français|' + defaultSort(trim(pageName[pageName.rfind(' '):])) + u']]\n'

    if page.namespace() == 0 or username in pageName:
        regex = ur'{{=([a-z\-]+)=}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'{{langue|\1}}', PageTemp)

        while PageTemp.find(u'{{ ') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{ ')+2] + PageTemp[PageTemp.find(u'{{ ')+3:len(PageTemp)]
        if PageTemp.find(u'{{formater') != -1 or PageTemp.find(u'{{SI|') != -1 or PageTemp.find(u'{{SI}}') != -1 or PageTemp.find(u'{{supp|') != -1 or PageTemp.find(u'{{supp}}') != -1 or PageTemp.find(u'{{supprimer|') != -1 or PageTemp.find(u'{{supprimer') != -1 or PageTemp.find(u'{{PàS') != -1 or PageTemp.find(u'{{S|faute') != -1 or PageTemp.find(u'{{S|erreur') != -1:
            if debugLevel > 0: print u'Page en travaux : non traitée l 1409'
            return

        # Alias d'anciens titres de section
        PageTemp = PageTemp.replace(u'{{-car-}}', u'{{caractère}}')
        PageTemp = PageTemp.replace(u'{{-note-|s=s}}', u'{{-notes-}}')
        PageTemp = PageTemp.replace(u'{{-etym-}}', u'{{-étym-}}')
        PageTemp = PageTemp.replace(u'{{-pronom-personnel-', u'{{-pronom-pers-')

        if debugLevel > 0: print u'Conversion vers {{S}}'
        EgalSection = u'==='
        for p in range(1, limit4):
            if p == limit2: EgalSection = u'===='
            if p == limit3: EgalSection = u'====='

            regex = ur'[= ]*{{[\-loc]*(' + Modele[p] + ur'|S\|'+ Section[p] + ur')([^}]*)}}[= ]*'
            if re.search(regex, PageTemp):
                PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'\2}} ' + EgalSection, PageTemp)

            regex = ur'[= ]*{{\-flex[\-loc]*(' + Modele[p] + ur'|S\|' + Section[p] + ur')\|([^}]*)}}[= ]*'
            if re.search(regex, PageTemp):
                PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'|\2|flexion}} ' + EgalSection, PageTemp)

        if debugLevel > 1:
            pywikibot.output (u"\n\03{red}---------------------------------------------------\03{default}")
            raw_input(PageTemp.encode(config.console_encoding, 'replace'))
            pywikibot.output (u"\n\03{red}---------------------------------------------------\03{default}")
        if PageTemp.find(u'|===') != -1 or PageTemp.find(u'{===') != -1:
            if debugLevel > 0: print u' *==='
            return

        regex = ur'([^\n=])(===?=? *{{S\|)'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1\n\n\2', PageTemp)

        # Titres en minuscules
        #PageTemp = re.sub(ur'{{S\|([^}]+)}}', ur'{{S|' + ur'\1'.lower() + ur'}}', PageTemp)
        for f in re.findall("{{S\|([^}]+)}}", PageTemp):
            PageTemp = PageTemp.replace(f, f.lower())
        # Alias peu intuitifs des sections avec langue
        PageTemp = PageTemp.replace(u'{{S|adj|', u'{{S|adjectif|')
        PageTemp = PageTemp.replace(u'{{S|adjectifs|', u'{{S|adjectif|')
        PageTemp = PageTemp.replace(u'{{S|adj-num|', u'{{S|adjectif numéral|')
        PageTemp = PageTemp.replace(u'{{S|adv|', u'{{S|adverbe|')
        PageTemp = PageTemp.replace(u'{{S|interj|', u'{{S|interjection|')
        PageTemp = PageTemp.replace(u'{{S|locution adverbiale', u'{{S|adverbe')
        PageTemp = PageTemp.replace(u'{{S|locution phrase|', u'{{S|locution-phrase|')
        PageTemp = PageTemp.replace(u'{{S|nom commun|', u'{{S|nom|')
        PageTemp = PageTemp.replace(u'{{S|nom-fam|', u'{{S|nom de famille|')
        PageTemp = PageTemp.replace(u'{{S|nom-pr|', u'{{S|nom propre|')
        PageTemp = PageTemp.replace(u'{{S|symb|', u'{{S|symbole|')
        PageTemp = PageTemp.replace(u'{{S|verb|', u'{{S|verbe|')
        PageTemp = PageTemp.replace(u'{{S|apparentés étymologiques', u'{{S|apparentés')
        # Alias peu intuitifs des sections sans langue
        PageTemp = re.sub(ur'{{S\| ?abr(é|e)v(iations)?\|?[a-z ]*}}', u'{{S|abréviations}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?anagr(ammes)?\|?[a-z ]*}}', u'{{S|anagrammes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?anciennes orthographes?\|?[a-z ]*}}', u'{{S|anciennes orthographes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?ant(onymes)?\|?[a-z ]*}}', u'{{S|antonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?app(arentés)?\|?[a-zé]*}}', u'{{S|apparentés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?apr\|?[a-zé]*}}', u'{{S|apparentés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?compos(és)?\|?[a-zé]*}}', u'{{S|composés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?dial\|?[a-z ]*}}', u'{{S|variantes dialectales}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?dimin(inutifs)?\|?[a-z ]*}}', u'{{S|diminutifs}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?d(é|e)riv(é|e)s?(\|[a-z ]*}}|}})', u'{{S|dérivés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?drv\|?[a-z ]*}}', u'{{S|dérivés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?dérivés int\|?[a-z ]*}}', u'{{S|dérivés autres langues}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?drv\-int\|?[a-z ]*}}', u'{{S|dérivés autres langues}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?(é|e)tym(ologie)?\|?[a-z ]*}}', u'{{S|étymologie}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?exp(ressions)?\|?[a-z ]*}}', u'{{S|expressions}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?gent(ilés)?\|?[a-zé]*}}', u'{{S|gentilés}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?faux\-amis?\|?[a-zé]*}}', u'{{S|faux-amis}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?holo(nymes)?\|?[a-z ]*}}', u'{{S|holonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?homo(phones)?\|?[a-z ]*}}', u'{{S|homophones}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?hyper(onymes)?\|?[a-z ]*}}', u'{{S|hyperonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?hypo(nymes)?\|?[a-z ]*}}', u'{{S|hyponymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?m(é|e)ro(nymes)?\|?[a-z ]*}}', u'{{S|méronymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?note\|?[a-z ]*}}', u'{{S|note}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?notes\|?[a-z ]*}}', u'{{S|notes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?paro(nymes)?\|?[a-z ]*}}', u'{{S|paronymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?phrases?\|?[a-z ]*}}', u'{{S|phrases}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?pron(onciation)?\|?[a-z ]*}}', u'{{S|prononciation}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?q\-syn\|?[a-z ]*}}', u'{{S|quasi-synonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?quasi(\-| )syn(onymes)?\|?[a-z ]*}}', u'{{S|quasi-synonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?r(é|e)f[a-zé]*\|?[a-z ]*}}', u'{{S|références}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?syn(onymes)?\|?[a-z ]*}}', u'{{S|synonymes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?trad(uctions)?\|?[a-z]*}}', u'{{S|traductions}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?trad\-trier\|?[a-z ]*}}', u'{{S|traductions à trier}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?traductions à trier\|?[a-z ]*}}', u'{{S|traductions à trier}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?var(iantes)?\|?[a-z]*}}', u'{{S|variantes}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?variantes dial\|?[a-z ]*}}', u'{{S|variantes dialectales}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?variantes dialectales\|?[a-z ]*}}', u'{{S|variantes dialectales}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?var[a-z]*(\-| )ortho(graphiques)?\|?[a-z ]*}}', u'{{S|variantes orthographiques}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?voc(abulaire)?\|?[a-z ]*}}', u'{{S|vocabulaire}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?vocabulaire apparenté\|?[a-z ]*}}', u'{{S|vocabulaire}}', PageTemp)
        PageTemp = re.sub(ur'{{S\| ?voir( aussi)?\|?[a-z ]*}}', u'{{S|voir aussi}}', PageTemp)
        PageTemp = PageTemp.replace(u'==== {{S|phrases|fr}} ====', u'==== {{S|phrases}} ====')

        regex = ur"= *({{langue\|[^}]+}}) *="
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"= \1 =", PageTemp)

        # Formatage général des traductions
        PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier}}}}', u'{{trad-trier}}\n{{trad-début}}')
        PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier|fr}}}}', u'{{trad-trier}}\n{{trad-début}}')

            # 1) Suppression de {{ébauche-trad|fr}} (WT:PPS)
        PageTemp = PageTemp.replace(ur'{{ébauche-trad|fr}}', u'{{ébauche-trad}}')     # bug ?
        regex = ur'{{ébauche\-trad\|fr}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, u'{{ébauche-trad}}', PageTemp)

            # 2) Aucun modèle d'ébauche en dehors d'une boite déroulante
        PageTemp = PageTemp.replace(ur'{{ébauche-trad}}\n{{trad-début}}', u'{{trad-début}}\n{{ébauche-trad}}') # bug ?
        regex = ur'{{ébauche\-trad}}\n{{trad\-début}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, u'{{trad-début}}\n{{ébauche-trad}}', PageTemp)

        PageTemp = PageTemp.replace(ur'==== {{S|traductions}} ====\n{{ébauche-trad}}\n', u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n')     # bug ?
        regex = ur'==== {{S\|traductions}} ====\n{{ébauche\-trad}}(\n<![^>]+>)*(\n|$)'
        if re.search(regex, PageTemp):
            if debugLevel > 0: print ' ébauche sans boite'
            PageTemp = re.sub(regex, u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad|en}}\n{{trad-fin}}\n', PageTemp)

            # 3) Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
        PageTemp = PageTemp.replace(ur'<!--* {{T|en}} : {{trad|en|}}-->', '')     # bug ?
        regex = ur'<!\-\-[^{>]*{{T\|[^>]+>\n?'
        if re.search(regex, PageTemp):
            if debugLevel > 0: print ' Commentaire trouvé l 1517'
            PageTemp = re.sub(regex, u'', PageTemp)
            # Cosmétique
        regex = ur'{{ébauche\-trad}}{{'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, u'{{ébauche-trad}}\n{{', PageTemp)

            # 4) Contrôle du nombre de paragraphes de traduction par rapport au nombre de sens
        #if PageTemp.find(u'{{langue|fr}}') != -1:
            '''TODO
            NbSensFr = count(#)
            replace(
                {{trad-début}}
                {{ébauche-trad}}
                {{trad-fin}}
                {{trad-début}}
            '''

        while PageTemp.find(u'{{trad-fin}}\n* {{T|') != -1:
            PageTemp2 = PageTemp[PageTemp.find(u'{{trad-fin}}\n* {{T|'):]
            delta = PageTemp2.find(u'\n')+1
            PageTemp2 = PageTemp2[delta:]
            if PageTemp2.find(u'\n') != -1:
                if debugLevel > 0: print PageTemp2[:PageTemp2.find(u'\n')+1].encode(config.console_encoding, 'replace')
                if PageTemp2[:PageTemp2.find(u'\n')+1].find(u'trier') != -1: break
                PageTemp = PageTemp[:PageTemp.find(u'{{trad-fin}}\n* {{T|'):] + PageTemp2[:PageTemp2.find(u'\n')+1] + u'{{trad-fin}}\n' + PageTemp[PageTemp.find(u'{{trad-fin}}\n* {{T|')+delta+PageTemp2.find(u'\n')+1:]
            else:
                if debugLevel > 0: print PageTemp2.encode(config.console_encoding, 'replace')
                if PageTemp2[:len(PageTemp2)].find(u'trier') != -1: break
                PageTemp = PageTemp[:PageTemp.find(u'{{trad-fin}}\n* {{T|'):] + PageTemp2[:len(PageTemp2)] + u'{{trad-fin}}\n' + PageTemp[PageTemp.find(u'{{trad-fin}}\n* {{T|')+delta+len(PageTemp2):]
            # Cosmétique
        regex = ur'}}{{trad\-fin}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, u'}}\n{{trad-fin}}', PageTemp)

        ''' Ajout des traductions, s'il n'y a pas un seul sens renvoyant vers un autre mot les centralisant
        if PageTemp.find(u'{{langue|fr}}') != -1 and PageTemp.find(u'{{S|traductions}}') == -1 and PageTemp.find(u'Variante d') == -1 and PageTemp.find(u'Synonyme d') == -1:
            PageTemp = addCat(PageTemp, u'fr', u'\n==== {{S|traductions}} ====\n{{trad-début}}\n{{trad-fin}}\n')
            summary = summary + u', ajout de {{S|traductions}}'
        '''

        if page.namespace() == 0:
            if debugLevel > 0: print u'Ajout des {{voir}}'
            if PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].lower() + pageName[1:] + PageTemp[PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|{{lc:{{PAGENAME}}}}'):len(PageTemp)]
                summary = summary + u', subst de {{lc:{{PAGENAME}}}}'
            if PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].upper() + pageName[1:] + PageTemp[PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|{{ucfirst:{{PAGENAME}}}}'):len(PageTemp)]
                summary = summary + u', subst de {{ucfirst:{{PAGENAME}}}}'
            if PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].lower() + pageName[1:] + PageTemp[PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|{{LC:{{PAGENAME}}}}'):len(PageTemp)]
                summary = summary + u', subst de {{LC:{{PAGENAME}}}}'
            if PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|')] + pageName[:1].upper() + pageName[1:] + PageTemp[PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|{{UCFIRST:{{PAGENAME}}}}'):len(PageTemp)]
                summary = summary + u', subst de {{UCFIRST:{{PAGENAME}}}}'
            if PageTemp.find(u'{{voir|') == -1 and PageTemp.find(u'{{voir/') == -1:
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
                LettresDiacritiques = []
                LettresDiacritiques.append([u'a',u'á',u'à',u'ä',u'â',u'ã'])
                LettresDiacritiques.append([u'c',u'ç'])
                LettresDiacritiques.append([u'e',u'é',u'è',u'ë',u'ê'])
                LettresDiacritiques.append([u'i',u'í',u'ì',u'ï',u'î'])
                LettresDiacritiques.append([u'n',u'ñ'])
                LettresDiacritiques.append([u'o',u'ó',u'ò',u'ö',u'ô',u'õ'])
                LettresDiacritiques.append([u'u',u'ú',u'ù',u'ü',u'û'])
                for l in range(0,len(LettresDiacritiques)):
                    for d in range(0,len(LettresDiacritiques[l])):
                        if pageName.find(LettresDiacritiques[l][d]) != -1:
                            if debugLevel > 1: print u'Titre contenant : ' + LettresDiacritiques[l][d]
                            Lettre = LettresDiacritiques[l][d]
                            for d in range(0,len(LettresDiacritiques[l])):
                                PagesCleTotal = PagesCleTotal + u'|' + pageName.replace(Lettre,LettresDiacritiques[l][d])
                if PagesCleTotal.find(CleTri) == -1: PagesCleTotal = PagesCleTotal + u'|' + CleTri    # exception ? and PageTemp.find(u'{{langue|eo}}') == -1
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
                    PageTempCle = getContentFromPage(pageCle)
                    if PageTempCle != u'KO':
                        if PagesCleTotal.find(currentPage) == -1: PagesCleTotal = PagesCleTotal + u'|' + currentPage
                        if PageTempCle.find(u'{{voir|') != -1:
                            PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|'):len(PageTempCle)]
                            PagesVoir = PagesVoir + u'|' + PageTempCle2[:PageTempCle2.find('}}')]
                        elif PageTempCle.find(u'{{voir/') != -1:
                            PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir/')+len(u'{{voir/'):len(PageTempCle)]
                            PageTemp = u'{{voir/' + PageTempCle2[:PageTempCle2.find('}}')+3] + PageTemp
                            pageMod = Page(site, u'Template:voir/' + PageTempCle2[:PageTempCle2.find('}}')])
                            PageTempModBegin = getContentFromPage(pageMod)
                            if PageTempModBegin == 'KO': break
                            PageTempMod = PageTempModBegin
                            if PageTempMod.find(u'!') == -1:
                                if PageTempMod.find(pageName) == -1: PageTempMod = PageTempMod[:PageTempMod.find('}}')] + u'|' + pageName + PageTempMod[PageTempMod.find('}}'):len(PageTempMod)]
                                if PageTempMod.find(PageVoir) == -1: PageTempMod = PageTempMod[:PageTempMod.find('}}')] + u'|' + PageVoir + PageTempMod[PageTempMod.find('}}'):len(PageTempMod)]
                            if debugLevel > 0:
                                print u'PagesCleRestant vide'
                            else:
                                if PageTempMod != PageTempModBegin: savePage(pageMod,PageTempMod, summary)
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
                            PageTempCleBegin = getContentFromPage(pageCle)
                        else:
                            PageTempCleBegin = PageTemp
                        if PageTempCleBegin != u'KO':
                            PageTempCle = PageTempCleBegin
                            if PageTempCle.find(u'{{voir/') != -1:
                                if debugLevel > 0: print u' {{voir/ trouvé'
                                break
                            elif PageTempCle.find(u'{{voir|') != -1:
                                if debugLevel > 0: print u' {{voir| trouvé'
                                if PagesCleTotal.find(u'|' + currentPage) != -1:
                                    PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|'):len(PageTempCle)]
                                    PageTempCle = PageTempCle[:PageTempCle.find(u'{{voir|')+len(u'{{voir|')] + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):len(PagesCleTotal)] + PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|')+PageTempCle2.find('}}'):len(PageTempCle)]
                                else:    # Cas du premier
                                    PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir'):len(PageTempCle)]
                                    PageTempCle = PageTempCle[:PageTempCle.find(u'{{voir|')+len(u'{{voir|')] + PagesCleTotal[len(currentPage):len(PagesCleTotal)] + PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir')+PageTempCle2.find('}}'):len(PageTempCle)]
                                if PageTempCle != PageTempCleBegin:
                                    if currentPage == pageName:
                                        PageTemp = PageTempCle
                                    else:
                                        if debugLevel > 0:
                                            print u' Première savePage dédiée à {{voir}}'
                                        else:
                                            savePage(pageCle, PageTempCle, summary)
                            else:
                                if PagesCleTotal.find(u'|' + currentPage) != -1:
                                    PageTempCle = u'{{voir|' + PagesCleTotal[:PagesCleTotal.find(u'|' + currentPage)] + PagesCleTotal[PagesCleTotal.find(u'|' + currentPage)+len(u'|' + currentPage):len(PagesCleTotal)] + u'}}\n' + PageTempCle
                                else:    # Cas du premier
                                    PageTempCle = u'{{voir' + PagesCleTotal[len(currentPage):len(PagesCleTotal)] + u'}}\n' + PageTempCle
                                if currentPage == pageName:
                                    PageTemp = PageTempCle
                                else:    
                                    if debugLevel > 0:
                                        print u' Deuxième savePage dédiée à {{voir}}'
                                    else:
                                        savePage(pageCle, PageTempCle, summary)

            elif PageTemp.find(u'{{voir|') != -1:
                if debugLevel > 0: print u'  Identique à la page courante'
                PageTemp2 = PageTemp[PageTemp.find(u'{{voir|'):len(PageTemp)]
                if PageTemp2.find(u'|' + pageName + u'|') != -1 and PageTemp2.find(u'|' + pageName + u'|') < PageTemp2.find('}}'):
                    PageTemp = PageTemp[:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + pageName + u'|')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + pageName + u'|')+len(u'|' + pageName):]
                if PageTemp2.find(u'|' + pageName + u'}') != -1 and PageTemp2.find(u'|' + pageName + u'}') < PageTemp2.find('}}'):
                    PageTemp = PageTemp[:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + pageName + u'}')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + pageName + u'}')+len(u'|' + pageName):]

            if debugLevel > 0: print u' Nettoyage des {{voir}}...'
            if PageTemp.find(u'{{voir}}\n') != -1: PageTemp = PageTemp[:PageTemp.find(u'{{voir}}\n')] + PageTemp[PageTemp.find(u'{{voir}}\n')+len(u'{{voir}}\n'):len(PageTemp)]
            if PageTemp.find(u'{{voir}}') != -1: PageTemp = PageTemp[:PageTemp.find(u'{{voir}}')] + PageTemp[PageTemp.find(u'{{voir}}')+len(u'{{voir}}'):len(PageTemp)]
            PageTemp = html2Unicode(PageTemp)
            PageTemp = PageTemp.replace(u'}}&#32;[[', u'}} [[')
            PageTemp = PageTemp.replace(u']]&#32;[[', u']] [[')
            regex = ur'\[\[([^\]]*)\|\1\]\]'
            if re.search(regex, PageTemp):
                if debugLevel > 0: print u'Lien interne inutile'
                PageTemp = re.sub(regex, ur'[[\1]]', PageTemp)

            if PageTemp.find(u'{{vérifier création automatique}}') != -1:
                if debugLevel > 0: print u' {{vérifier création automatique}} trouvé'
                PageTemp2 = PageTemp
                LanguesV = u'|'
                while PageTemp2.find(u'{{langue|') > 0:
                    PageTemp2 = PageTemp2[PageTemp2.find(u'{{langue|')+len(u'{{langue|'):]
                    LanguesV += u'|' + PageTemp2[:PageTemp2.find('}}')]
                if LanguesV != u'|':
                    PageTemp = PageTemp.replace(u'{{vérifier création automatique}}', u'{{vérifier création automatique' + LanguesV + '}}')
                if debugLevel > 2: raw_input(PageTemp.encode(config.console_encoding, 'replace'))

            if addDefaultSort:
                if debugLevel > 0: print u'Clés de tri'
                PageTemp = addDefaultSort(PageTemp)

            if debugLevel > 0: print u'Catégories de prononciation'
            if pageName[-2:] == u'um' and PageTemp.find(u'ɔm|fr}}') != -1:
                PageTemp = addCat(PageTemp, u'fr', u'um prononcés /ɔm/ en français')
            if pageName[:2] == u'qu':
                regex = ur'{{pron\|kw[^}\|]+\|fr}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'qu prononcés /kw/ en français')
            if pageName[:2] == u'qu':
                regex = ur'{{fr\-rég\|kw[^}\|]+}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'qu prononcés /kw/ en français')
            if pageName[:2] == u'ch':
                regex = ur'{{pron\|k[^}\|]+\|fr}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[:2] == u'ch':
                regex = ur'{{fr\-rég\|k[^}\|]+}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[:2] == u'Ch':
                regex = ur'{{pron\|k[^}\|]+\|fr}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[:2] == u'Ch':
                regex = ur'{{fr\-rég\|k[^}\|]+}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[-2:] == u'ch':
                regex = ur'{{pron\|[^}\|]+k\|fr}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[-2:] == u'ch':
                regex = ur'{{fr\-rég\|[^}\|]+k}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[-3:] == u'chs':
                regex = ur'{{pron\|[^}\|]+k}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
            if pageName[-3:] == u'chs':
                regex = ur'{{fr\-rég\|[^}\|]+k}}'
                if re.search(regex, PageTemp):
                    PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')

        if debugLevel > 1: print u'Formatage de la ligne de forme'
        PageTemp = PageTemp.replace(u'{{PAGENAME}}', u'{{subst:PAGENAME}}')
        PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", PageTemp)
        PageTemp = PageTemp.replace(u'[[' + pageName + u']]', u'\'\'\'' + pageName + u'\'\'\'')
        PageTemp = PageTemp.replace(u'-rég}}\'\'\'', u'-rég}}\n\'\'\'')
        PageTemp = PageTemp.replace(u']] {{imperf}}', u']] {{imperf|nocat=1}}')
        PageTemp = PageTemp.replace(u']] {{perf}}', u']] {{perf|nocat=1}}')
        PageTemp = PageTemp.replace(u'{{perf}} / \'\'\'', u'{{perf|nocat=1}} / \'\'\'')
        regex = ur'({{fr\-[^}]*\|[\'’]+=[^}]*)\|[\'’]+=[oui|1]'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'({{fr\-[^}]*\|s=[^}]*)\|s=[^}\|]*'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'({{fr\-[^}]*\|ms=[^}]*)\|ms=[^}\|]*'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        regex = ur'({{fr\-[^}]*\|fs=[^}]*)\|fs=[^}\|]*'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)
        while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(PageTemp):
            i1 = re.search(u'{{T\|.*\n\n\*[ ]*{{T\|', PageTemp).end()
            PageTemp = PageTemp[:i1][:PageTemp[:i1].rfind(u'\n')-1] + PageTemp[:i1][PageTemp[:i1].rfind(u'\n'):len(PageTemp[:i1])] + PageTemp[i1:]
        if PageTemp.find(u'{{Latn') == -1 and PageTemp.find(u'{{Grek') == -1 and PageTemp.find(u'{{Cyrl') == -1 and PageTemp.find(u'{{Armn') == -1 and PageTemp.find(u'{{Geor') == -1 and PageTemp.find(u'{{Hebr') == -1 and PageTemp.find(u'{{Arab') == -1 and PageTemp.find(u'{{Syrc') == -1 and PageTemp.find(u'{{Thaa') == -1 and PageTemp.find(u'{{Deva') == -1 and PageTemp.find(u'{{Hang') == -1 and PageTemp.find(u'{{Hira') == -1 and PageTemp.find(u'{{Kana') == -1 and PageTemp.find(u'{{Hrkt') == -1 and PageTemp.find(u'{{Hani') == -1 and PageTemp.find(u'{{Jpan') == -1 and PageTemp.find(u'{{Hans') == -1 and PageTemp.find(u'{{Hant') == -1 and PageTemp.find(u'{{zh-mot') == -1 and PageTemp.find(u'{{kohan') == -1 and PageTemp.find(u'{{ko-nom') == -1 and PageTemp.find(u'{{la-verb') == -1 and PageTemp.find(u'{{grc-verb') == -1 and PageTemp.find(u'{{polytonique') == -1 and PageTemp.find(u'FAchar') == -1:
            if debugLevel > 0: print u'Ajout du mot vedette'
            PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n\{\{[^\n]*\n)\# *', ur"\1'''" + pageName + ur"''' {{pron}}\n# ", PageTemp)
        PageTemp = PageTemp.replace(u'num=1|num=', u'num=1')
        PageTemp = PageTemp.replace(u'&nbsp;', u' ')
        PageTemp = PageTemp.replace(u'\n #*', u'\n#*')
        PageTemp = PageTemp.replace(u'\n #:', u'\n#:')
        PageTemp = PageTemp.replace(u' }}', '}}')
        PageTemp = PageTemp.replace(u'|pinv= ', u'|pinv=')
        PageTemp = PageTemp.replace(u'|pinv=. ', u'|pinv=.')
        #PageTemp = re.sub(ur'«[  \t]*', ur'« ', PageTemp) # pb &#160;
        #PageTemp = re.sub(ur'[  \t]*»', ur' »', PageTemp)
        PageTemp = PageTemp.replace(u'{|\n|}', u'')
        regex = ur"({{S\|verbe\|en}} *=* *\n'*)to "
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"\1", PageTemp)

        regex = ur' *{{pluriel \?\|[^}]*}}(\n# ?\'*Pluriel d)'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\1', PageTemp)

        if debugLevel > 0: print u'Formatage des modèles'
        PageTemp = PageTemp.replace(u'\n {{', u'\n{{')
        if debugLevel > 1: print u' Remplacements des anciens modèles de langue'
        PageTemp = PageTemp.replace(u'{{grc}}', u'grec ancien')
        PageTemp = PageTemp.replace(u'{{la}}', u'latin')
        PageTemp = PageTemp.replace(u'{{fro}}', u'ancien français')
        PageTemp = PageTemp.replace(u'{{frm}}', u'moyen français')
        PageTemp = PageTemp.replace(u'{{fr}}', u'français')
        PageTemp = PageTemp.replace(u'{{ang}}', u'anglo-saxon')
        PageTemp = PageTemp.replace(u'{{enm}}', u'moyen anglais')
        PageTemp = PageTemp.replace(u'{{en}}', u'anglais')
        PageTemp = PageTemp.replace(u'{{ru}}', u'russe')
        PageTemp = PageTemp.replace(u'{{nl}}', u'néerlandais')
        PageTemp = PageTemp.replace(u'{{pt}}', u'portugais')
        PageTemp = PageTemp.replace(u'{{it}}', u'italien')
        PageTemp = PageTemp.replace(u'{{nds}}', u'bas allemand')
        PageTemp = PageTemp.replace(u'{{nds}}', u'bas allemand')
        PageTemp = PageTemp.replace(u'{{lb}}', u'luxembourgeois')
        PageTemp = PageTemp.replace(u'{{sq}}', u'albanais')
        PageTemp = PageTemp.replace(u'{{kw}}', u'cornique')
        PageTemp = PageTemp.replace(u'{{diq}}', u'dimli (zazaki du Sud)')
        PageTemp = PageTemp.replace(u'{{lv}}', u'letton')
        PageTemp = PageTemp.replace(u'{{oc}}', u'occitan')
        PageTemp = PageTemp.replace(u'{{tr}}', u'turc')
        PageTemp = PageTemp.replace(u'|ko-hani}}', u'|ko-Hani}}')
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
            if re.search(regex, PageTemp):
                PageTemp = re.sub(regex, ur'\1' + newTemplate[p] + ur'\2', PageTemp)
        PageTemp = PageTemp.replace(u'{{WP|lang=sgs', u'{{WP|lang=bat-smg')

        PageTemp = re.sub(ur'{{régio *\| *', ur'{{région|', PageTemp)
        PageTemp = re.sub(ur'{{terme *\| *', ur'{{term|', PageTemp)
        PageTemp = re.sub(ur'{{term *\|Registre neutre}} *', ur'', PageTemp)
        PageTemp = PageTemp.replace(u'{{auxiliaire être}}', u'{{note-auxiliaire|fr|être}}')
        PageTemp = PageTemp.replace(u'{{Citation needed}}', u'{{réf ?}}')
        PageTemp = PageTemp.replace(u'{{escrim|', u'{{escrime|')
        PageTemp = PageTemp.replace(u'{{f}} {{fsing}}', u'{{f}}')
        PageTemp = PageTemp.replace(u'{{m}} {{msing}}', u'{{m}}')
        PageTemp = PageTemp.replace(u'fm?', u'fm ?')
        PageTemp = PageTemp.replace(u'mf?', u'mf ?')
        PageTemp = PageTemp.replace(u'myt=scandinave', u'myt=nordique')
        PageTemp = PageTemp.replace(u'{{pron|}}', u'{{pron}}')
        PageTemp = PageTemp.replace(u'{{prononciation|}}', u'{{prononciation}}')
        PageTemp = PageTemp.replace(u'{{pron-rég|', u'{{écouter|')
        PageTemp = PageTemp.replace(u'{{Référence nécessaire}}', u'{{référence nécessaire}}')
        PageTemp = PageTemp.replace(u'religion|rel=chrétienne', u'christianisme')
        PageTemp = PageTemp.replace(u'religion|rel=islamique', u'islam')
        PageTemp = PageTemp.replace(u'religion|rel=musulmane', u'islam')
        PageTemp = PageTemp.replace(u'religion|rel=boudhiste', u'boudhisme')
        PageTemp = PageTemp.replace(u'religion|rel=juive', u'judaïsme')
        PageTemp = PageTemp.replace(u'religion|spéc=chrétienne', u'christianisme')
        PageTemp = PageTemp.replace(u'religion|spéc=islamique', u'islam')
        PageTemp = PageTemp.replace(u'religion|spéc=musulmane', u'islam')
        PageTemp = PageTemp.replace(u'religion|spéc=boudhiste', u'boudhisme')
        PageTemp = PageTemp.replace(u'religion|spéc=juive', u'judaïsme')
        PageTemp = PageTemp.replace(u'religion|fr|rel=chrétienne', u'christianisme|fr')
        PageTemp = PageTemp.replace(u'religion|fr|rel=islamique', u'islam|fr')
        PageTemp = PageTemp.replace(u'religion|fr|rel=musulmane', u'islam|fr')
        PageTemp = PageTemp.replace(u'religion|fr|rel=boudhiste', u'boudhisme|fr')
        PageTemp = PageTemp.replace(u'religion|fr|rel=juive', u'judaïsme|fr')
        PageTemp = PageTemp.replace(u'religion|nocat=1|rel=chrétienne', u'christianisme|nocat=1')
        PageTemp = PageTemp.replace(u'religion|nocat=1|rel=islamique', u'islam|nocat=1')
        PageTemp = PageTemp.replace(u'religion|nocat=1|rel=musulmane', u'islam|nocat=1')
        PageTemp = PageTemp.replace(u'religion|nocat=1|rel=boudhiste', u'boudhisme|nocat=1')
        PageTemp = PageTemp.replace(u'religion|nocat=1|rel=juive', u'judaïsme|nocat=1')
        PageTemp = PageTemp.replace(u'{{sexua|', u'{{sexe|')
        PageTemp = PageTemp.replace(u'— {{source|', u'{{source|')
        PageTemp = PageTemp.replace(u'- {{source|', u'{{source|')
        PageTemp = PageTemp.replace(u'{{term|Antiquité grecque}}', u'{{antiquité|spéc=grecque}}')
        PageTemp = PageTemp.replace(u'{{term|Antiquité romaine}}', u'{{antiquité|spéc=romaine}}')
        PageTemp = PageTemp.replace(u'{{antiquité|fr}} {{term|grecque}}', u'{{antiquité|spéc=grecque}}')
        PageTemp = PageTemp.replace(u'{{antiquité|fr}} {{term|romaine}}', u'{{antiquité|spéc=romaine}}')
        PageTemp = PageTemp.replace(u'#*: {{trad-exe|fr}}', u'')
        PageTemp = PageTemp.replace(u'\n{{WP', u'\n* {{WP')

        regex = ur"{{ *dés *([\|}])"
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"{{désuet\1", PageTemp)
        regex = ur"{{ *fam *([\|}])"
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"{{familier\1", PageTemp)
        regex = ur"{{ *péj *([\|}])"
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"{{péjoratif\1", PageTemp)
        regex = ur"{{ *vx *([\|}])"
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur"{{vieilli\1", PageTemp)       

        if debugLevel > 1: print u' Modèles alias en doublon'
        regex = ur"(\{\{figuré\|[^}]*\}\}) ?\{\{métaphore\|[^}]*\}\}"
        pattern = re.compile(regex)
        PageTemp = pattern.sub(ur"\1", PageTemp)
        regex = ur"(\{\{métaphore\|[^}]*\}\}) ?\{\{figuré\|[^}]*\}\}"
        pattern = re.compile(regex)
        PageTemp = pattern.sub(ur"\1", PageTemp)

        regex = ur"(\{\{départements\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        PageTemp = pattern.sub(ur"\1", PageTemp)

        regex = ur"(\{\{localités\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        PageTemp = pattern.sub(ur"\1", PageTemp)

        regex = ur"(\{\{provinces\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
        pattern = re.compile(regex)
        PageTemp = pattern.sub(ur"\1", PageTemp)

        if debugLevel > 1: print u' Modèles trop courts'
        PageTemp = PageTemp.replace(u'{{fp}}', u'{{fplur}}')
        PageTemp = PageTemp.replace(u'{{mp}}', u'{{mplur}}')
        PageTemp = PageTemp.replace(u'{{fp|fr}}', u'{{fplur}}')
        PageTemp = PageTemp.replace(u'{{mp|fr}}', u'{{mplur}}')
        PageTemp = PageTemp.replace(u'{{np}}', u'{{nlur}}')
        PageTemp = PageTemp.replace(u'{{fs}}', u'{{fsing}}')
        PageTemp = PageTemp.replace(u'{{mascul}}', u'{{au masculin}}')
        PageTemp = PageTemp.replace(u'{{fémin}}', u'{{au féminin}}')
        PageTemp = PageTemp.replace(u'{{femin}}', u'{{au féminin}}')
        PageTemp = PageTemp.replace(u'{{sing}}', u'{{au singulier}}')
        PageTemp = PageTemp.replace(u'{{plur}}', u'{{au pluriel}}')
        PageTemp = PageTemp.replace(u'{{pluri}}', u'{{au pluriel}}')
        PageTemp = PageTemp.replace(u'{{mascul|', u'{{au masculin|')
        PageTemp = PageTemp.replace(u'{{fémin|', u'{{au féminin|')
        PageTemp = PageTemp.replace(u'{{femin|', u'{{au féminin|')
        PageTemp = PageTemp.replace(u'{{sing|', u'{{au singulier|')
        PageTemp = PageTemp.replace(u'{{plur|', u'{{au pluriel|')
        PageTemp = PageTemp.replace(u'{{pluri|', u'{{au pluriel|')
        PageTemp = PageTemp.replace(u'{{dét|', u'{{déterminé|')
        PageTemp = PageTemp.replace(u'{{dén|', u'{{dénombrable|')
        PageTemp = PageTemp.replace(u'{{pl-cour}}', u'{{plus courant}}')
        PageTemp = PageTemp.replace(u'{{pl-rare}}', u'{{plus rare}}')
        PageTemp = PageTemp.replace(u"# ''féminin de", u"# ''Féminin de")
        PageTemp = PageTemp.replace(u"# ''masculin de", u"# ''Masculin de")
        PageTemp = PageTemp.replace(u'{{mf?}}', u'{{mf ?}}')
        PageTemp = PageTemp.replace(u'{{fm?}}', u'{{fm ?}}')

        PageTemp = PageTemp.replace(u'{{arbre|', u'{{arbres|')
        PageTemp = PageTemp.replace(u'{{arme|', u'{{armement|')
        PageTemp = PageTemp.replace(u'{{astro|', u'{{astronomie|')
        PageTemp = PageTemp.replace(u'{{bota|', u'{{botanique|')
        PageTemp = PageTemp.replace(u'{{électro|', u'{{électronique|')
        PageTemp = PageTemp.replace(u'{{équi|', u'{{équitation|')
        PageTemp = PageTemp.replace(u'{{ex|', u'{{e|')
        PageTemp = PageTemp.replace(u'{{gastro|', u'{{gastronomie|')
        PageTemp = PageTemp.replace(u'{{légume|', u'{{légumes|')
        PageTemp = PageTemp.replace(u'{{minéral|', u'{{minéralogie|')
        PageTemp = PageTemp.replace(u'{{myth|', u'{{mythologie|')
        PageTemp = PageTemp.replace(u'{{oiseau|', u'{{oiseaux|')
        PageTemp = PageTemp.replace(u'{{péj|', u'{{péjoratif|')
        PageTemp = PageTemp.replace(u'{{plante|', u'{{plantes|')
        PageTemp = PageTemp.replace(u'{{psycho|', u'{{psychologie|')
        PageTemp = PageTemp.replace(u'{{réseau|', u'{{réseaux|')
        PageTemp = PageTemp.replace(u'{{typo|', u'{{typographie|')
        PageTemp = PageTemp.replace(u'{{vêtement|', u'{{vêtements|')
        PageTemp = PageTemp.replace(u'{{en-nom-rég-double|', u'{{en-nom-rég|')
        PageTemp = PageTemp.replace(u'{{Valence|ca}}', u'{{valencien}}')
        PageTemp = PageTemp.replace(u'{{boîte début', u'{{(')
        PageTemp = PageTemp.replace(u'{{boîte fin', u'{{)')
        PageTemp = PageTemp.replace(u'\n{{-}}', u'')

        if debugLevel > 1: print u' Ajout des modèles de référence' # les URL ne contiennent pas les diacritiques des {{PAGENAME}}
        while PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=') != -1:
            PageTemp2 = PageTemp[PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')+len(u'[http://www.sil.org/iso639-3/documentation.asp?id='):]
            PageTemp = PageTemp[:PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')] + u'{{R:SIL|' + PageTemp2[:PageTemp2.find(u' ')] + '}}' + PageTemp2[PageTemp2.find(u']')+1:]
            summary = summary + u', ajout de {{R:SIL}}'
        while PageTemp.find(u'[http://www.cnrtl.fr/definition/') != -1:
            PageTemp2 = PageTemp[PageTemp.find(u'[http://www.cnrtl.fr/definition/')+len(u'[http://www.cnrtl.fr/definition/'):len(PageTemp)]
            PageTemp = PageTemp[:PageTemp.find(u'[http://www.cnrtl.fr/definition/')] + u'{{R:TLFi|' + PageTemp2[:PageTemp2.find(u' ')] + '}}' + PageTemp2[PageTemp2.find(u']')+1:len(PageTemp2)]
            summary = summary + u', ajout de {{R:TLFi}}'
        while PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/') != -1:
            PageTemp2 = PageTemp[PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/')+len(u'[http://www.mediadico.com/dictionnaire/definition/'):len(PageTemp)]
            PageTemp = PageTemp[:PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/')] + u'{{R:Mediadico|' + PageTemp2[:PageTemp2.find(u'/1')] + '}}' + PageTemp2[PageTemp2.find(u']')+1:len(PageTemp2)]
            summary = summary + u', ajout de {{R:Mediadico}}'
        while PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}')+len(u'{{R:DAF8}}\n'):len(PageTemp)]
            summary = summary + u', doublon {{R:DAF8}}'
        while PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}')+len(u'{{R:DAF8}}\n\n'):len(PageTemp)]
            summary = summary + u', doublon {{R:DAF8}}'
        while PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}')+len(u'{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}')+len(u'{{Import:DAF8}}\n{{R:DAF8}}'):len(PageTemp)]
            summary = summary + u', doublon {{R:DAF8}}'
        while PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}')] + PageTemp[PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}')+len(u'{{R:Littré}}\n'):len(PageTemp)]
            summary = summary + u', doublon {{R:Littré}}'
        while PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}') != -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}')+len(u'{{Import:Littré}}')] + PageTemp[PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}')+len(u'{{Import:Littré}}\n{{R:Littré}}'):len(PageTemp)]
            summary = summary + u', doublon {{R:Littré}}'
        PageTemp = PageTemp.replace(u'\n{{Import:', u'\n* {{Import:')

        if debugLevel > 1: print u' Retrait des catégories contenues dans les modèles'
        if PageTemp.find(u'[[Catégorie:Villes') != -1 and PageTemp.find(u'{{localités|') != -1:
            summary = summary + u', {{villes}} -> {{localités}}'
            PageTemp = re.sub(ur'\n\[\[Catégorie:Villes[^\]]*\]\]', ur'', PageTemp)

        if PageTemp.find(u'\n[[Catégorie:Noms scientifiques]]') != -1 and PageTemp.find(u'{{S|nom scientifique|conv}}') != -1:
            PageTemp = PageTemp.replace(u'\n[[Catégorie:Noms scientifiques]]', u'')

        if PageTemp.find(u'\n[[Catégorie:Gentilés en français]]') != -1 and PageTemp.find(u'{{note-gentilé|fr}}') != -1:
            PageTemp = PageTemp.replace(u'\n[[Catégorie:Gentilés en français]]', u'')

        if debugLevel > 1: print u' Modèles à déplacer'
        if PageTemp.find(u'{{ru-conj') != -1:
            PageEnd = PageTemp[:PageTemp.find(u'{{ru-conj')]
            PageTemp = PageTemp[PageTemp.find(u'{{ru-conj'):]
            Annexe = PageTemp[:PageTemp.find(u'\n')+1]
            PageTemp = PageEnd + PageTemp[PageTemp.find(u'\n')+1:]
            PageEnd = u''
            pageAnnexe = Page(site, u'Annexe:Conjugaison en russe/' + pageName)
            AnnexeExistante = getContentFromPage(pageAnnexe)
            if pageAnnexe.exists():
                if AnnexeExistante == 'KO': return
            else:
                AnnexeExistante = u''
            savePage(pageAnnexe, AnnexeExistante + u'\n\n'+Annexe, u'Création à partir de l\'article')

        if debugLevel > 1: print u' Modèles de son' # Ex : {{écoutez | {{audio | | {{sound -> {{écouter
        PageTemp = PageTemp.replace(u'{{pron-rég|', u'{{écouter|')
        regex = ur'\* ?{{sound}} ?: \[\[Media:([^\|\]]*)\|[^\|\]]*\]\]'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'{{écouter|audio=\1}}', PageTemp)
            summary = summary + u', conversion de modèle de son'
        regex = ur'\{{audio\|([^\|}]*)\|[^\|}]*}}'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'{{écouter|audio=\1}}', PageTemp)
            summary = summary + u', conversion de modèle de son'
        regex = ur'\n *{{écouter\|'
        if re.search(regex, PageTemp):
            PageTemp = re.sub(regex, ur'\n* {{écouter|', PageTemp)

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
            while PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|')+len('{{écouter|')-1] + '{{' + ModRegion[m] + u'|nocat=1}}' + PageTemp[PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|')+len(u'{{écouter|' + ModRegion[m]):]

        if debugLevel > 1: print u' Modèles bandeaux' 
        while PageTemp.find(u'\n{{colonnes|') != -1:
            if debugLevel > 0: pywikibot.output (u'\nTemplate: \03{blue}colonnes\03{default}')
            PageTemp2 = PageTemp[:PageTemp.find(u'\n{{colonnes|')]
            if PageTemp2.rfind('{{') != -1 and PageTemp2.rfind('{{') == PageTemp2.rfind(u'{{trad-début'):    # modèles impriqués dans trad
                PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                if PageTemp2.find(u'\n}}\n') != -1:
                    if PageTemp2[:len(u'titre=')] == u'titre=':
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + '}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
                    else:
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 1'
                    break

            elif PageTemp2.rfind('{{') != -1 and PageTemp2.rfind('{{') == PageTemp2.rfind(u'{{('):    # modèles impriqués ailleurs
                if debugLevel > 0: pywikibot.output (u'\nTemplate: \03{blue}(\03{default}')
                PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                if PageTemp2.find(u'\n}}\n') != -1:
                    if PageTemp2[:len(u'titre=')] == u'titre=':
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + '}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
                    else:
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 2'
                    break

            elif PageTemp2.rfind('{{') != -1 and (PageTemp2.rfind('{{') == PageTemp2.rfind(u'{{trad-fin') or PageTemp2.rfind('{{') == PageTemp2.rfind(u'{{S|trad')):
                # modèle à utiliser dans {{S|trad
                PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                if PageTemp2.find(u'\n}}\n') != -1:
                    if PageTemp2[:len(u'titre=')] == u'titre=':
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + '}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
                    else:
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 3'
                    break

            else:    # modèle ailleurs que {{S|trad
                PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                if PageTemp2.find(u'\n}}\n') != -1:
                    if PageTemp2[:len(u'titre=')] == u'titre=':
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + '}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:]
                    else:
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):]
                        PageTemp = PageTemp[:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):]
                else:
                    if debugLevel > 0: print u'pb {{colonnes}} 4'
                    break
            while PageTemp.find(u'}}1=') != -1:
                PageTemp = PageTemp[:PageTemp.find(u'}}1=')] + PageTemp[PageTemp.find(u'}}1=')+len(u'}}1='):len(PageTemp)]

        # #* or #:
        PageEnd = u''
        while PageTemp.find(u'\n#:') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n#:')+2]
            if PageEnd.rfind(u'{{langue|') == PageEnd.rfind(u'{{langue|fr}}'):
                PageTemp = u'*' + PageTemp[PageTemp.find(u'\n#:')+len(u'\n#:'):len(PageTemp)]
            else:
                PageTemp = u':' + PageTemp[PageTemp.find(u'\n#:')+len(u'\n#:'):len(PageTemp)]
        PageTemp = PageEnd + PageTemp
        PageEnd = u''

        # Faux homophones : lemme et sa flexion
        if debugLevel > 0: print u'Faux homophones'
        if PageTemp.find(u'|flexion}}') != -1 and pageName[len(pageName)-1:] == u's' and PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']],') == -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']]')+len(u'{{S|homophones}}\n*[[' + pageName[:len(pageName)-1] + u']]')+1:len(PageTemp)]
        elif PageTemp.find(u'|flexion}}') != -1 and pageName[len(pageName)-1:] == u's' and PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']],') == -1:
            PageTemp = PageTemp[:PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']]')+len(u'{{S|homophones}}\n* [[' + pageName[:len(pageName)-1] + u']]')+1:len(PageTemp)]

        # Ajout des redirections des pronominaux
        if PageTemp.find(u'{{S|verbe|fr}}') != -1 and pageName[:3] != u'se' and pageName[:2] != u's’':
            PageTemp2 = PageTemp[PageTemp.find(u'{{S|verbe|fr}}'):]
            regex = ur'(\n|\')s(e |’)\'\'\''
            if re.search(regex, PageTemp2) is not None:
                if re.search(regex, PageTemp2) < PageTemp2.find(u'{{S|') or PageTemp2.find(u'{{S|') == -1:
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
        if PageTemp.find(u'{{langue|fr}}') != -1:
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
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                # Depuis un féminin
                if ModeleGent[l][1] == ur'fr-accord-s' and rePageName[-1:] == u'e' and rePageName[-2:-1] == u's':
                    regex = ur'\({{p}} : [\[\']*' + rePageName + ur's[\]\']*, {{m}} : [\[\']*' + rePageName[:-1] + ur'[\]\']*\)'
                    if re.search(regex, PageTemp):
                        PageTemp = re.sub(regex, '{{' + ModeleGent[l][1] + u'|ms=' + rePageName[:-1] + '}}', PageTemp)
                        summary = summary + u', conversion des liens flexions en modèle boite'
                regex = ur'\({{f}} : [\[\']*' + rePageName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + rePageName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageName + ModeleGent[l][4] + ur'[\]\']*\)'
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, '{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                if debugLevel > 1: print u' avec son'
                regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|[pron\=]*)}}'
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, ur'\n\4\2}}\1\2\3', PageTemp)

                regex = ur'( ===\n)(\'\'\'[^\n]+)({{' + ModeleGent[l][1] + ur'\|[^}]*}})'
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, ur'\1\3\n\2', PageTemp)
                    summary = summary + u', déplacement des modèles de flexions'

        elif PageTemp.find(u'{{langue|es}}') != -1:
            ligne = 1
            colonne = 4
            ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
            ModeleGent[1][1] = ur'es-accord-oa'
            ModeleGent[1][2] = ur'os'
            ModeleGent[1][3] = ur'a'
            ModeleGent[1][4] = ur'as'
            rePageRadicalName = re.escape(pageName[:-1])

            for l in range(1, ligne + 1):
                regex = ur'\({{p}} : [\[\']*' + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', PageTemp)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                regex = ur'\({{f}} : [\[\']*' + rePageRadicalName + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + rePageRadicalName + ModeleGent[l][4] + ur'[\]\']*\)'
                if debugLevel > 0: print regex.encode(config.console_encoding, 'replace')
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, '{{' + ModeleGent[l][1] + u'|' + rePageRadicalName + ur'}}', PageTemp)
                    summary = summary + u', conversion des liens flexions en modèle boite'
                # Son
                if debugLevel > 0: print u' son'
                regex = ur'(\n\'\'\'' + rePageName + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|' + rePageRadicalName + ur')}}'
                if re.search(regex, PageTemp):
                    PageTemp = re.sub(regex, ur'\n\4|\2}}\1\2\3', PageTemp)


        # Détection d'une première traduction aux normes
        regex = u'\* ?{{[a-z][a-z][a-z]?\-?[a-z]?[a-z]?[a-z]?}} :'
        PageEnd = u''
        while PageTemp.find(u'{{trad-début')!=-1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{trad-début')]
            PageTemp = PageTemp[PageTemp.find(u'{{trad-début'):]
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')+1]
            PageTemp = PageTemp[PageTemp.find(u'\n')+1:]
            if re.search(regex, PageTemp):
                if re.search(regex, PageTemp).start() < PageTemp.find('{{'):
                    if debugLevel > 0: print u'Ajout d\'un modèle T'
                    PageTemp = PageTemp[:PageTemp.find('{{')+2] + u'T|' + PageTemp[PageTemp.find('{{')+2:]
        PageTemp = PageEnd + PageTemp
        PageEnd = u''

        # Classement des traductions (et ajout des modèles T après le premier de la liste)
        if debugLevel > 0: print u'Classement des traductions'
        while PageTemp.find(u'{{T|') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{T|')]
            PageTemp = PageTemp[PageTemp.find(u'{{T|'):]
            # Ajout des T
            PageTemp2 = PageTemp[PageTemp.find(u'\n'):]
            if re.search(regex, PageTemp2):
                if re.search(regex, PageTemp2).start() < PageTemp2.find('{{'):
                    if debugLevel > 0: print u'Ajout d\'un modèle T'
                    PageTemp = PageTemp[:PageTemp.find(u'\n')+PageTemp2.find('{{')+2] + u'T|' + PageTemp[PageTemp.find(u'\n')+PageTemp2.find('{{')+2:]

            # Rangement de la ligne de la traduction par ordre alphabétique de la langue dans PageEnd
            langue1 = PageTemp[PageTemp.find(u'{{T|')+4:PageTemp.find(u'}')]
            if langue1.find(u'|') != -1: langue1 = langue1[:langue1.find(u'|')]
            #raw_input(PageEnd.encode(config.console_encoding, 'replace'))
            if langue1 != u'' and (PageEnd.find(u'<!--') == -1 or PageEnd.find(u'-->') != -1): # bug https://fr.wiktionary.org/w/index.php?title=Utilisateur:JackBot/test&diff=15092317&oldid=15090227
                #if PageEnd.find(u'<!--') != -1: raw_input(PageEnd[:PageEnd.rfind(u'\n')].encode(config.console_encoding, 'replace'))
                if debugLevel > 1: print u'Langue 1 : ' + langue1
                if len(langue1) > 3 and langue1.find(u'-') == -1:
                    langue = langue1
                else:
                    try:
                        langue = defaultSort(languages[langue1].decode("utf8"))
                    except KeyError:
                        if debugLevel > 0: print "KeyError l 2556"
                        break
                    except UnboundLocalError:
                        if debugLevel > 0: print "UnboundLocalError l 2559"
                        break
                langue2 = u'zzz'
                if PageEnd.rfind(u'\n') == -1 or PageTemp.find(u'\n') == -1: break
                TradCourante = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[:PageTemp.find(u'\n')]
                TradSuivantes = u''
                PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
                PageTemp = PageTemp[PageTemp.find(u'\n'):len(PageTemp)]
                while PageEnd.rfind('{{') != PageEnd.rfind(u'{{S|traductions') and PageEnd.rfind('{{') != PageEnd.rfind(u'{{trad-début') and PageEnd.rfind('{{') != PageEnd.rfind(u'{{trad-fin') and PageEnd.rfind('{{') != PageEnd.rfind(u'{{S|traductions à trier') and langue2 > langue and PageEnd.rfind(u'{{T') != PageEnd.rfind(u'{{T|conv') and PageEnd.rfind('{{') != PageEnd.rfind(u'{{(') and (PageEnd.rfind('{{') > PageEnd.rfind(u'|nocat') or PageEnd.rfind(u'|nocat') == -1):
                    langue2 = PageEnd[PageEnd.rfind(u'{{T|')+len(u'{{T|'):len(PageEnd)]
                    langue2 = langue2[:langue2.find('}}')]
                    if langue2.find(u'|') != -1: langue2 = langue2[:langue2.find(u'|')]
                    if debugLevel > 1: print u'Langue 2 : ' + langue2
                    if len(langue2) > 3 and langue2.find(u'-') == -1:
                        langue = langue2
                    else:
                        try:
                            langue2 = defaultSort(languages[langue2].decode("utf8"))
                        except KeyError:
                            if debugLevel > 0: print "KeyError l 2160"
                            break
                    if langue2 != u'' and langue2 > langue:
                        if debugLevel > 0: langue2 + u' > ' + langue
                        if PageEnd.rfind(u'\n') > PageEnd.rfind(u'trad-début'):
                            TradSuivantes = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + TradSuivantes
                            PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
                            summary = summary + ', traduction ' + langue2 + u' > ' + langue
                        elif PageEnd.rfind(u'\n') != -1:
                            # Cas de la première de la liste
                            TradCourante = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + TradCourante
                            PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
                        #print PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)].encode(config.console_encoding, 'replace')
                    else:
                        break
                PageEnd = PageEnd + TradCourante + TradSuivantes
            elif PageTemp.find(u'\n') != -1:
                if debugLevel > 0: print u' Retrait de commentaire de traduction l 2357'
                PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')]
                PageTemp = PageTemp[PageTemp.find(u'\n'):]
            else:
                PageEnd = PageEnd + PageTemp
                PageTemp = u''
            if debugLevel > 1: print u'Ligne : ' + PageTemp[:PageTemp.find(u'\n')+1].encode(config.console_encoding, 'replace')
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')+1]
            PageTemp = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
            #print(PageEnd.encode(config.console_encoding, 'replace'))
            #print(PageTemp.encode(config.console_encoding, 'replace'))'''
        PageTemp = PageEnd + PageTemp
        PageEnd = u''

        # TODO: Classement des sections modifiables
        """PageEnd = u''
        while PageTemp.find(u'{{langue|') != -1:
            PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{langue|')+len(u'{{langue|')]
            PageTemp = PageTemp[PageTemp.find(u'{{langue|')+len(u'{{langue|'):len(PageTemp)]
            if PageTemp.find(u'{{langue|') != -1:
                # Rangement des paragraphes par ordre alphabétique de langue dans PageEnd
                langue1 = PageTemp[:PageTemp.find(u'}')]
                if langue1.find(u'|') != -1: langue1 = langue1[:langue1.find(u'|')]
                if langue1 != u'':
                    #print(langue1) # ca pt
                    Langue1 = Page(site,u'Modèle:' + langue1)
                    try: PageTemp2 = Langue1.get()
                    except pywikibot.exceptions.NoPage:
                        print "NoPage l 1521 : " + langue1
                        return
                    except pywikibot.exceptions.IsRedirectPage:
                        PageTemp2 = Langue1.getRedirectTarget().title() + u'<noinclude>'
                    except pywikibot.exceptions.ServerError:
                        print "ServerError l 1527 : " + langue1
                        return
                    except pywikibot.exceptions.BadTitle:
                        print "BadTitle l 1530 : " + langue1
                        return
                    if PageTemp2.find(u'<noinclude>') != -1:
                        langue = defaultSort(PageTemp2[:PageTemp2.find(u'<noinclude>')])
                        langue2 = u'zzz'
                        if PageTemp.find(u'\n== {{langue|') != -1:
                            ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[:PageTemp.find(u'\n== {{langue|')]
                            PageTemp = PageTemp[PageTemp.find(u'\n== {{langue|'):len(PageTemp)]
                        elif PageTemp.find(u'\n=={{langue|') != -1:
                            ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[:PageTemp.find(u'\n=={{langue|')]
                            PageTemp = PageTemp[PageTemp.find(u'\n=={{langue|'):len(PageTemp)]
                        else:
                            ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp
                            PageTemp = u''
                        PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
                        ParagSuivants = u''
                        #raw_input (ParagCourant.encode(config.console_encoding, 'replace'))
                        # Comparaison du paragraphe courant avec le précédent, et rangement dans ParagSuivants de ce qui doit le suivre
                        while PageEnd.rfind(u'{{langue|') != -1  and PageEnd.rfind(u'{{langue|') < PageEnd.rfind('}}')  and PageEnd.rfind(u'{{langue|') != PageEnd.rfind(u'{{langue|fr'):
                            langue2 = PageEnd[PageEnd.rfind(u'{{langue|')+len(u'{{langue|'):len(PageEnd)]
                            langue2 = langue2[:langue2.find('}}')]
                            if langue2.find(u'|') != -1: langue2 = langue2[:langue2.find(u'|')]
                            Langue2 = Page(site,u'Modèle:' + langue2)
                            try: PageTemp3 = Langue2.get()
                            except pywikibot.exceptions.NoPage:
                                print "NoPage l 1607 : " + langue2
                                return
                            except pywikibot.exceptions.ServerError:
                                print "ServerError l 1610 : " + langue2
                                return
                            except pywikibot.exceptions.IsRedirectPage:
                                print u'Redirection l 1613 : ' + langue2
                                return
                            except pywikibot.exceptions.BadTitle:
                                print u'BadTitle l 1616 : ' + langue2
                                return
                            if PageTemp3.find(u'<noinclude>') != -1:
                                langue2 = defaultSort(PageTemp3[:PageTemp3.find(u'<noinclude>')])
                                print langue2 # espagnol catalan
                                if langue2 > langue:
                                    summary = summary + ', section ' + langue2 + u' > ' + langue
                                    print langue2 + u' > ' + langue
                                    ParagSuivants = PageEnd[PageEnd.rfind(u'{{langue|'):len(PageEnd)] + ParagSuivants
                                    PageEnd = PageEnd[:PageEnd.rfind(u'{{langue|')]
                                    ParagSuivants = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + ParagSuivants
                                else:
                                    ParagCourant = PageEnd[PageEnd.rfind(u'{{langue|'):len(PageEnd)] + ParagCourant
                                    PageEnd = PageEnd[:PageEnd.rfind(u'{{langue|')]
                                    ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + ParagCourant
                                    #raw_input (ParagCourant.encode(config.console_encoding, 'replace')) catalan, espagnol, portugais
                                PageEnd = PageEnd[:PageEnd.rfind(u'\n')]
                            else:
                                print u'l 1629'
                                return
                        #raw_input (PageEnd.encode(config.console_encoding, 'replace'))
                        PageEnd = PageEnd + ParagCourant + ParagSuivants
                else:
                    print u'l 1634'
                    return
                PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{langue|')]
                PageTemp = PageTemp[PageTemp.find(u'{{langue|'):len(PageTemp)]
                #raw_input (PageTemp.encode(config.console_encoding, 'replace'))
            else:
                PageEnd = PageEnd + PageTemp
                PageTemp = u''
            #print(PageEnd.encode(config.console_encoding, 'replace'))
            #print(PageTemp.encode(config.console_encoding, 'replace'))
        PageTemp = PageEnd + PageTemp
        PageEnd = u''"""


        if debugLevel > 0: print (u'Gestion des codes langues dans les modèles')
        addLanguageCode = False # Certaines sections interdisent les modèles de domaine catégorisant
        if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
        translationSection = False
        backward = False # Certains modèles nécessitent d'être déplacés puis retraités
        languageCode = None
        if debugLevel > 0: print u' languageCode = None'
        startPosition = 1
        # On sauvegarde la partie délimitée par "position" d'une page temporaire dans une page finale jusqu'à disparition de la première
        while startPosition > -1:
            if debugLevel > 1:
                pywikibot.output (u"\n\03{red}---------------------------------------------------\03{default}")
                print(PageEnd.encode(config.console_encoding, 'replace')[:1000])
                raw_input(PageTemp.encode(config.console_encoding, 'replace')[:1000])
                pywikibot.output (u"\n\03{red}---------------------------------------------------\03{default}")
            if debugLevel > 1:
                if languageCode is None:
                    print u'Boucle langue'
                else:
                    print u'Boucle langue : ' + languageCode

# Recherche de chaque modèle
            startPosition = PageTemp.find('{{')
            if startPosition < 0: break
            PageEnd = PageEnd + PageTemp[:startPosition + 2]
            PageTemp = PageTemp[startPosition + 2:]
            if PageTemp.find("|") > PageTemp.find('}}'):
                endPosition = PageTemp.find('}}')
            elif PageTemp.find("|") == -1:
                endPosition = PageTemp.find('}}')
            else:
                endPosition = PageTemp.find("|")
            currentTemplate = PageTemp[:endPosition]

            if not backward:
                if debugLevel > 0:
                    message = u' Remplacement de \x1b[6;31;40m{{' + PageTemp[:PageTemp.find('}}')+2] + u'\x1b[0m'
                    print(message.encode(config.console_encoding, 'replace'))
            else:
                if debugLevel > 0:
                    print(u' Retour en arrière')
                    pywikibot.output (u"\n\03{red}---------------------------------------------------\03{default}")
            backward = False

            if currentTemplate in Modele:
                p = Modele.index(currentTemplate)
                if debugLevel > 0: pywikibot.output (u'\nTemplate: \03{blue}' + currentTemplate + u'\03{default} (' + str(p) + u')')

                # Missing language section
                if not languageCode and (p < limit1 or p >= limit6) and currentTemplate != u'ébauche':
                    if debugLevel > 0: print u' Page à formater manuellement'
                    PageEnd = u'{{formater|Section de langue manquante, avant le modèle ' + currentTemplate + u' (au niveau du ' + str(len(PageEnd)) + u'-ème caractère)}}\n' + PageEnd + PageTemp
                    summary = u'Page à formater manuellement'
                    savePage(page, PageEnd, summary)
                    return

                elif currentTemplate == u'caractère':
                    languageCode = u'conv'
                    addLanguageCode = False
                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif currentTemplate == u'langue':
                    languageCode = PageTemp[endPosition+1:PageTemp.find('}}')]
                    if languageCode == u'':
                        if debugLevel > 0: print u' code langue vide'
                        return #TODO : chercher dans {{S}}
                    if debugLevel > 0: print u' code langue trouvé : ' + languageCode
                    regex = ur'[a-zA-Z\-]+'
                    if not re.search(regex, languageCode):
                        PageEnd = u'{{formater|Code langue incorrect : ' + languageCode + u'}}\n' + PageEnd + PageTemp
                        summary = u'Page à formater manuellement'
                        savePage(page, PageEnd, summary)
                        if debugLevel > 1: print u'Page à formater manuellement'
                        return
                    addLanguageCode = True

                    # Ajout des anagrammes pour cette nouvelle langue détectée
                    if languageCode == u'conv':
                        regex = ur'[= ]*{{S\|anagrammes}}[^}]+\|conv}}\n'
                        if re.compile(regex).search(PageTemp):
                            if debugLevel > 0: print u'Retrait d\'anagramme en conv'
                            PageEnd2 = PageTemp[:re.compile(regex).search(PageTemp).start()]
                            PageTemp2 = PageTemp[re.compile(regex).search(PageTemp).end():]
                            delta = re.compile(regex).search(PageTemp).end()
                            regex = ur'[^}]+\|conv}}\n'
                            while re.compile(regex).search(PageTemp2):
                                if debugLevel > 0: print u' autre anagramme en conv'
                                delta = delta + re.compile(regex).search(PageTemp2).end()
                                PageTemp2 = PageTemp2[re.compile(regex).search(PageTemp2).end():]
                            PageTemp = PageEnd2 + PageTemp[delta:]

                    elif PageTemp.find(u'S|erreur|' + languageCode) == -1 and PageTemp.find(u'S|faute|' + languageCode) == -1  and languageCode != u'conv' and pageName[:1] != u'-' and pageName[-1:] != u'-': #and pageName != u'six':
                        if debugLevel > 0: print u' Anagrammes pour ' + languageCode
                        if PageTemp.find(u'{{S|anagr') == -1 and pageName.find(u' ') == -1 and len(pageName) <= anagramsMaxLength:
                            anagrammes = anagram(pageName)
                            ListeAnagrammes = u''
                            for anagramme in anagrammes:
                                if anagramme != pageName:
                                    if debugLevel > 0: print anagramme.encode(config.console_encoding, 'replace')
                                    pageAnagr = Page(site,anagramme)
                                    if pageAnagr.exists():
                                        if pageAnagr.namespace() !=0 and anagramme != u'Utilisateur:JackBot/test':
                                            break
                                        else:
                                            PageTempAnagr = getContentFromPage(pageAnagr)
                                            if PageTempAnagr == 'KO': break
                                        if PageTempAnagr.find(u'{{langue|' + languageCode + '}}') != -1:
                                            ListeAnagrammes = ListeAnagrammes + u'* {{lien|' + anagramme + u'|' + languageCode + u'}}\n'
                                            if debugLevel > 0: print u' trouvé'
                            if ListeAnagrammes != u'':
                                summary = summary + u', ajout d\'anagrammes ' + languageCode
                                positionAnagr = PageTemp.find(u'{{langue|' + languageCode + '}}')+len(u'{{langue|' + languageCode + '}}')
                                PageTemp2 = PageTemp[positionAnagr:len(PageTemp)]
                                if PageTemp2.find(u'\n=== {{S|voir') != -1 and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'{{S|voir') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'\n=== {{S|voir')] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'\n=== {{S|voir'):len(PageTemp)]
                                elif PageTemp2.find(u'\n=== {{S|références}}') != -1 and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'\n=== {{S|références}}') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'\n=== {{S|références}}')] +  u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'\n=== {{S|références}}'):len(PageTemp)]
                                elif PageTemp2.find(u'== {{langue|') != -1 and ((PageTemp2.find(u'[[Catégorie:') != -1 and PageTemp2.find(u'== {{langue|') < PageTemp2.find(u'[[Catégorie:')) or PageTemp2.find(u'[[Catégorie:') == -1):
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'== {{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'== {{langue|'):len(PageTemp)]
                                elif PageTemp2.find(u'=={{langue|') != -1 and ((PageTemp2.find(u'[[Catégorie:') != -1 and PageTemp2.find(u'=={{langue|') < PageTemp2.find(u'[[Catégorie:')) or PageTemp2.find(u'[[Catégorie:') == -1):
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'=={{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'=={{langue|'):len(PageTemp)]        
                                elif PageTemp2.find(u'{{clé de tri') != -1:
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'{{clé de tri')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'{{clé de tri'):len(PageTemp)]
                                elif PageTemp2.find(u'[[Catégorie:') != -1:
                                    PageTemp = PageTemp[:positionAnagr+PageTemp2.find(u'[[Catégorie:')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'[[Catégorie:'):len(PageTemp)]
                                else:
                                    if debugLevel > 0: print " Ajout avant les interwikis"
                                    regex = ur'\n\[\[\w?\w?\w?:'
                                    if re.compile(regex).search(PageTemp):
                                        try:
                                            PageTemp = PageTemp[:re.search(regex,PageTemp).start()] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[re.search(regex,PageTemp).start():]
                                        except:
                                            if debugLevel > 0: print u'pb regex interwiki'
                                    else:
                                        PageTemp = PageTemp + u'\n\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes
                    PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

# Sections
                elif currentTemplate == u'S':
                    section = trim(PageTemp[endPosition+1:PageTemp.find('}}')])
                    if section.find(u'|') != -1: section = trim(section[:section.find(u'|')])
                    if not section in Section:
                        if debugLevel > 0: print u' Section introuvable : ' + section
                        return
                    if debugLevel > 0: print str(' ') + section.encode(config.console_encoding, 'replace')

                    if Section.index(section) < limit1:
                        if debugLevel > 1: print u' Paragraphe définition'
                        addLanguageCode = True # Paragraphe avec code langue dans les modèles lexicaux
                        translationSection = False

                        if PageTemp.find(languageCode) == -1 or PageTemp.find(languageCode) > PageTemp.find('}}'):
                            PageTemp = PageTemp[:endPosition+1+len(section)] + u'|' + languageCode + PageTemp[PageTemp.find('}}'):]

                        # Tous ces modèles peuvent facultativement contenir |clé= et |num=, et |genre= pour les prénoms, voire locution=
                        if (PageTemp.find(u'|clé=') == -1 or PageTemp.find(u'|clé=') > PageTemp.find('}}')):
                            if debugLevel > 1: print u'  ' + str(p)                                                                     # eg: 0 for {{S}}
                            if debugLevel > 1: print u'  ' + str(Section.index(section))                                                # eg: 40 for "nom"
                            if debugLevel > 1: print u'  ' + PageTemp[:PageTemp.find('}}')].encode(config.console_encoding, 'replace') # eg: S|nom|sv|flexion

                            tempPageName = defaultSortByLanguage(pageName, languageCode)
                            if tempPageName != pageName:
                                if debugLevel > 0: print u' ajout de "clé="'
                                tempPageName = defaultSort(tempPageName)
                                PageTemp = PageTemp[:PageTemp.find('}}')] + u'|clé=' + tempPageName + PageTemp[PageTemp.find('}}'):]

                    else:
                        addLanguageCode = False # Paragraphe sans code langue dans les modèles lexicaux et les titres
                        translationSection = False

                        if section == u'homophones':
                            if debugLevel > 0: print ' Catégorisation des homophones'
                            PageTemp = PageTemp[:PageTemp.find('}}')] + u'|' + languageCode + PageTemp[PageTemp.find('}}'):]

                        if section == 'traductions':
                            translationSection = True
                            # Ajout de {{trad-début}} si {{T| en français (pas {{L| car certains les trient par famille de langue)
                            if PageTemp.find('{{') == PageTemp.find(u'{{T|') and languageCode == 'fr':
                                PageTemp = PageTemp[:PageTemp.find(u'\n')] + u'\n{{trad-début}}' + PageTemp[PageTemp.find(u'\n'):]
                                PageTemp2 = PageTemp[PageTemp.find(u'{{trad-début}}\n')+len(u'{{trad-début}}\n'):]
                                if PageTemp2.find(u'\n') == -1:
                                    PageTemp = PageTemp + u'\n'
                                    PageTemp2 = PageTemp2 + u'\n'
                                while PageTemp2.find(u'{{T|') < PageTemp2.find(u'\n') and PageTemp2.find(u'{{T|') != -1:
                                    PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:]
                                PageTemp = PageTemp[:len(PageTemp)-len(PageTemp2)] + u'{{trad-fin}}\n' + PageTemp[len(PageTemp)-len(PageTemp2):]
                        elif section == u'traductions à trier':
                            translationSection = True

                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif currentTemplate == u'term':
                    rawTerm = PageTemp[endPosition+1:PageTemp.find('}}')]
                    term = trim(rawTerm.replace('[[', '').replace(']]', ''))
                    if term.find('|') != -1: term = term[:term.find('|')]
                    if debugLevel > 0: print " terminologie = " + term
                    templatePage = getContentFromPageName(u'Template:' + term, allowedNamespaces = [u'Template:'])
                    if templatePage.find(u'Catégorie:Modèles de domaine') == -1 and term[:1] != term[:1].lower():
                        term = term[:1].lower() + term[1:]
                        if debugLevel > 0: print " terminologie = " + trim(str(term))
                        templatePage = getContentFromPageName(u'Template:' + term, allowedNamespaces = [u'Template:'])
                    if templatePage.find(u'Catégorie:Modèles de domaine') != -1:
                        if debugLevel > 0: print u'  substitution par le modèle existant'
                        PageTemp = '{{' + term + PageTemp[endPosition+1+len(rawTerm):]
                        PageEnd = PageEnd[:-2]
                        backward = True
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

# Templates with language code at second
                elif currentTemplate == u'pron' or currentTemplate == u'phon' or currentTemplate == u'dénominal de' or currentTemplate == u'déverbal de' or currentTemplate == u'déverbal' or currentTemplate == u'superlatif de' or currentTemplate == u'comparatif de' or currentTemplate == u'déverbal sans suffixe' or currentTemplate == u'abréviation de':
                    if languageCode != u'conv':
                        # Tri des lettres de l'API
                        if currentTemplate == u'pron':
                            PageTemp2 = PageTemp[endPosition+1:PageTemp.find('}}')]
                            while PageTemp2.find(u'\'') != -1 and PageTemp2.find(u'\'') < PageTemp2.find('}}') and (PageTemp2.find(u'\'') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u'\'')] + u'ˈ' + PageTemp[PageTemp.find(u'\'')+1:len(PageTemp)]
                            while PageTemp2.find(u'ˈˈˈ') != -1 and PageTemp2.find(u'ˈˈˈ') < PageTemp2.find('}}') and (PageTemp2.find(u'ˈˈˈ') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u'ˈˈˈ')] + u'\'\'\'' + PageTemp[PageTemp.find(u'ˈˈˈ')+3:len(PageTemp)]
                            while PageTemp2.find(u'ε') != -1 and PageTemp2.find(u'ε') < PageTemp2.find('}}') and (PageTemp2.find(u'ε') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u'ε')] + u'ɛ' + PageTemp[PageTemp.find(u'ε')+1:len(PageTemp)]
                            while PageTemp2.find(u'ε̃') != -1 and PageTemp2.find(u'ε̃') < PageTemp2.find('}}') and (PageTemp2.find(u'ε̃') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u'ε̃')] + u'ɛ̃' + PageTemp[PageTemp.find(u'ε̃')+1:len(PageTemp)]
                            while PageTemp2.find(u':') != -1 and PageTemp2.find(u':') < PageTemp2.find('}}') and (PageTemp2.find(u':') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u':')] + u'ː' + PageTemp[PageTemp.find(u':')+1:len(PageTemp)]
                            while PageTemp2.find(u'g') != -1 and PageTemp2.find(u'g') < PageTemp2.find('}}') and (PageTemp2.find(u'g') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[:PageTemp.find(u'g')] + u'ɡ' + PageTemp[PageTemp.find(u'g')+1:len(PageTemp)]
                            #if languageCode == u'es': β/, /ð/ et /ɣ/ au lieu de de /b/, /d/ et /ɡ/
                        if PageTemp[:8] == u'pron||}}':
                            PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')] + languageCode + '}}'
                        elif PageTemp[endPosition:endPosition+3] == u'|}}' or PageTemp[endPosition:endPosition+4] == u'| }}':
                            PageEnd = PageEnd + currentTemplate + "||" + languageCode + '}}'
                        elif (PageTemp.find("lang=") != -1 and PageTemp.find("lang=") < PageTemp.find('}}')):
                            PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                        elif endPosition == PageTemp.find(u'|'):
                            PageTemp2 = PageTemp[endPosition+1:PageTemp.find('}}')]
                            if PageTemp2.find(u'|') == -1:
                                PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')] + "|" + languageCode + '}}'
                            else:
                                PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                        elif endPosition == PageTemp.find('}}'):
                            PageEnd = PageEnd + currentTemplate + "||" + languageCode + '}}'
                        else:
                            PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')] + "|" + languageCode + '}}'
                        PageTemp = PageTemp[PageTemp.find('}}')+2:]
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif currentTemplate == u'écouter':
                    PageTemp2 = PageTemp[endPosition+1:len(PageTemp)]
                    # Saut des modèles régionnaux
                    if PageTemp2.find("lang=") == -1 or PageTemp2.find("lang=") > PageTemp2.find('}}'):
                        while PageTemp2.find('{{') < PageTemp2.find('}}') and PageTemp2.find('{{') != -1:
                            PageTemp2 = PageTemp2[PageTemp2.find('}}')+2:]
                        if PageTemp2.find("lang=") == -1 or PageTemp2.find("lang=") > PageTemp2.find('}}'):
                            PageEnd = PageEnd + currentTemplate + u'|lang=' + languageCode + PageTemp[endPosition:PageTemp.find('}}')+2]
                            PageTemp = PageTemp[PageTemp.find('}}')+2:]
                        else:
                            PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif currentTemplate == u'référence nécessaire' or currentTemplate == u'réf?' or currentTemplate == u'réf ?' or currentTemplate == u'refnec' or currentTemplate == u'réfnéc' or currentTemplate == u'source?' or currentTemplate == u'réfnéc':
                    PageTemp2 = PageTemp[endPosition+1:len(PageTemp)]
                    if PageTemp2.find("lang=") == -1 or PageTemp2.find("lang=") > PageTemp2.find('}}'):
                        PageEnd = PageEnd + currentTemplate + u'|lang=' + languageCode + PageTemp[endPosition:PageTemp.find('}}')+2]
                        PageTemp = PageTemp[PageTemp.find('}}')+2:]
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

# Wrong genders
                elif currentTemplate == u'm' or currentTemplate == u'f':
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko'):
                        PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        PageEnd = PageEnd[:-2]
                        backward = True
                    PageTemp = PageTemp[PageTemp.find('}}')+2:]
                elif currentTemplate == u'mf' or currentTemplate == u'mf?':
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko'):
                        PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        PageEnd = PageEnd[:-2]
                        backward = True
                    PageTemp = PageTemp[PageTemp.find('}}')+2:]
                elif currentTemplate == u'n' or currentTemplate == u'c':
                    if translationSection or (languageCode != u'en' and languageCode != u'zh' and languageCode != u'ja' and languageCode != u'ko' and languageCode != u'fr'):
                        PageEnd = PageEnd + currentTemplate + '}}'
                    else:
                        if debugLevel > 0: print u' retrait de genre inexistant en ' + languageCode
                        PageEnd = PageEnd[:-2]
                        backward = True
                    PageTemp = PageTemp[PageTemp.find('}}')+2:]

# Templates with language code at first
                elif currentTemplate == u'perfectif' or currentTemplate == u'perf' or currentTemplate == u'imperfectif' or currentTemplate == u'imperf' or currentTemplate == u'déterminé' or currentTemplate == u'dét' or currentTemplate == u'indéterminé' or currentTemplate == u'indét':
                    if (not addLanguageCode) or PageEnd.rfind(u'(') > PageEnd.rfind(u')'): # Si on est dans des parenthèses
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, 'nocat=1')
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, languageCode)

                elif currentTemplate == u'conjugaison' or currentTemplate == u'conj' or currentTemplate == u'1ergroupe' or currentTemplate == u'2egroupe' or currentTemplate == u'3egroupe':    # Modèle à deux paramètres
                    if currentTemplate == u'1ergroupe':
                        PageTemp = u'|grp=1' + PageTemp[len(u'1ergroupe'):]
                        PageEnd = PageEnd + u'conj'
                    elif currentTemplate == u'2egroupe':
                        PageTemp = u'|grp=2' + PageTemp[len(u'2egroupe'):]
                        PageEnd = PageEnd + u'conj'
                    elif currentTemplate == u'3egroupe':
                        PageTemp = u'|grp=3' + PageTemp[len(u'3egroupe'):]
                        PageEnd = PageEnd + u'conj'
                    elif currentTemplate == u'conjugaison':
                        PageTemp = PageTemp[len(u'conjugaison'):]
                        PageEnd = PageEnd + u'conjugaison'
                    elif currentTemplate == u'conj':
                        PageTemp = PageTemp[len(u'conj'):]
                        PageEnd = PageEnd + u'conj'
                    # Vérification des groupes en espagnol, portugais et italien
                    if languageCode == u'es':
                        if pageName[len(pageName)-2:] == u'ar' or pageName[len(pageName)-4:] == u'arsi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=1' + PageTemp
                        elif pageName[len(pageName)-2:] == u'er' or pageName[len(pageName)-4:] == u'ersi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=2' + PageTemp
                        elif pageName[len(pageName)-2:] == u'ir' or pageName[len(pageName)-4:] == u'irsi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=3' + PageTemp

                    elif languageCode == u'pt':
                        if pageName[len(pageName)-2:] == u'ar' or pageName[len(pageName)-4:] == u'ar-se':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=1' + PageTemp
                        elif pageName[len(pageName)-2:] == u'er' or pageName[len(pageName)-4:] == u'er-se':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=2' + PageTemp
                        elif pageName[len(pageName)-2:] == u'ir' or pageName[len(pageName)-4:] == u'ir-se':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=3' + PageTemp

                    elif languageCode == u'it':
                        if pageName[len(pageName)-3:] == u'are' or pageName[len(pageName)-4:] == u'arsi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=1' + PageTemp
                        elif pageName[len(pageName)-3:] == u'ere' or pageName[len(pageName)-4:] == u'ersi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=2' + PageTemp
                        elif pageName[len(pageName)-3:] == u'ire' or pageName[len(pageName)-4:] == u'irsi':
                            if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:]
                            elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find('}}')):
                                if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):]
                                else:
                                    PageTemp = PageTemp[:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:]
                            else:
                                PageTemp = u'|groupe=3' + PageTemp

                    if (PageTemp.find(languageCode) != -1 and PageTemp.find(languageCode) < PageTemp.find('}}')) or languageCode == u'fr':
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)
                    else:
                        if PageTemp.find(u'|nocat=1') != -1:
                            PageTemp = PageTemp[:PageTemp.find(u'|nocat=1')] + PageTemp[PageTemp.find(u'|nocat=1')+len(u'|nocat=1'):]
                        PageEnd = PageEnd + u'|' + languageCode + '}}'
                        PageTemp = PageTemp[PageTemp.find('}}')+2:]

                elif currentTemplate == u'trad' or currentTemplate == u'trad+' or currentTemplate == u'trad-' or currentTemplate == u'trad--':
                    if endPosition == PageTemp.find('}}') or endPosition == PageTemp.find(u'--}}')-2 or endPosition == PageTemp.find(u'|en|}}')-4:
                        PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2]
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)
                    else:
                        # Lettres spéciales à remplacer dans les traductions vers certaines langues
                        PageTemp2 = PageTemp[endPosition+1:]
                        currentLanguage = PageTemp2[:PageTemp2.find(u'|')]
                        if currentLanguage == u'ro' or currentLanguage == u'mo':
                            while PageTemp.find(u'ş') != -1 and PageTemp.find(u'ş') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'ş')] + u'ș' + PageTemp[PageTemp.find(u'ş')+1:]
                            while PageTemp.find(u'Ş') != -1 and PageTemp.find(u'Ş') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'Ş')] + u'Ș' + PageTemp[PageTemp.find(u'Ş')+1:]
                            while PageTemp.find(u'ţ') != -1 and PageTemp.find(u'ţ') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'ţ')] + u'ț' + PageTemp[PageTemp.find(u'ţ')+1:]
                            while PageTemp.find(u'Ţ') != -1 and PageTemp.find(u'Ţ') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'Ţ')] + u'Ț' + PageTemp[PageTemp.find(u'Ţ')+1:]
                        elif currentLanguage == u'az' or currentLanguage == u'ku' or currentLanguage == u'sq' or currentLanguage == u'tk' or currentLanguage == u'tr' or currentLanguage == u'tt':
                            while PageTemp.find(u'ș') != -1 and PageTemp.find(u'ș') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'ș')] + u'ş' + PageTemp[PageTemp.find(u'ș')+1:]
                            while PageTemp.find(u'Ș') != -1 and PageTemp.find(u'Ș') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'Ș')] + u'Ş' + PageTemp[PageTemp.find(u'Ș')+1:]
                            while PageTemp.find(u'ț') != -1 and PageTemp.find(u'ț') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'ț')] + u'ţ' + PageTemp[PageTemp.find(u'ț')+1:]
                            while PageTemp.find(u'Ț') != -1 and PageTemp.find(u'Ț') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'Ț')] + u'Ţ' + PageTemp[PageTemp.find(u'Ț')+1:]
                        elif currentLanguage == u'fon':
                            while PageTemp.find(u'ε') != -1 and PageTemp.find(u'ε') < PageTemp.find(u'\n'):
                                PageTemp = PageTemp[:PageTemp.find(u'ε')] + u'ɛ' + PageTemp[PageTemp.find(u'ε')+1:]
                        # http://fr.wiktionary.org/wiki/Mod%C3%A8le:code_interwiki
                        elif currentLanguage == u'cmn':
                            PageTemp = PageTemp[:PageTemp.find(u'cmn')] + u'zh' + PageTemp[PageTemp.find(u'cmn')+len(u'cmn'):]
                        elif currentLanguage == u'nn':
                            PageTemp = PageTemp[:PageTemp.find(u'nn')] + u'no' + PageTemp[PageTemp.find(u'nn')+len(u'nn'):]
                        elif currentLanguage == u'per':
                            PageTemp = PageTemp[:PageTemp.find(u'per')] + u'fa' + PageTemp[PageTemp.find(u'per')+len(u'per'):]
                        elif currentLanguage == u'wel':
                            PageTemp = PageTemp[:PageTemp.find(u'wel')] + u'cy' + PageTemp[PageTemp.find(u'wel')+len(u'wel'):]
                        elif currentLanguage == u'zh-classical':
                            PageTemp = PageTemp[:PageTemp.find(u'zh-classical')] + u'lzh' + PageTemp[PageTemp.find(u'zh-classical')+len(u'zh-classical'):]
                        elif currentLanguage == u'ko-Hani':
                            PageTemp = PageTemp[:PageTemp.find(u'ko-Hani')] + u'ko' + PageTemp[PageTemp.find(u'ko-Hani')+len(u'ko-Hani'):]
                        elif currentLanguage == u'ko-hanja':
                            PageTemp = PageTemp[:PageTemp.find(u'ko-hanja')] + u'ko' + PageTemp[PageTemp.find(u'ko-hanja')+len(u'ko-hanja'):]
                        elif currentLanguage == u'zh-min-nan':
                            PageTemp = PageTemp[:PageTemp.find(u'zh-min-nan')] + u'nan' + PageTemp[PageTemp.find(u'zh-min-nan')+len(u'zh-min-nan'):]
                        elif currentLanguage == u'roa-rup':
                            PageTemp = PageTemp[:PageTemp.find(u'roa-rup')] + u'rup' + PageTemp[PageTemp.find(u'roa-rup')+len(u'roa-rup'):]
                        elif currentLanguage == u'zh-yue':
                            PageTemp = PageTemp[:PageTemp.find(u'zh-yue')] + u'yue' + PageTemp[PageTemp.find(u'zh-yue')+len(u'zh-yue'):]
                        PageTemp2 = PageTemp[endPosition+1:]
                        currentLanguage = PageTemp2[:PageTemp2.find(u'|')]

                        if currentLanguage != '': #TODO: reproduire le bug du site fermé, ex : https://fr.wiktionary.org/w/index.php?title=chat&diff=prev&oldid=9366302
                            # Identification des Wiktionnaires hébergeant les traductions
                            siteExterne = u''
                            pageExterne = u''
                            PageTemp3 = PageTemp2[PageTemp2.find(u'|')+1:]
                            if debugLevel > 0: print u' langue distante : ' + currentLanguage
                            if PageTemp3.find('}}') == "" or not PageTemp3.find('}}'):
                                if debugLevel > 1: print u'  aucun mot distant'
                                if PageEnd.rfind('<!--') == -1 or PageEnd.rfind('<!--') < PageEnd.rfind('-->'):
                                    # On retire le modèle pour que la page ne soit plus en catégorie de maintenance
                                    if debugLevel > 0: print u' Retrait de commentaire de traduction l 4362'
                                    PageEnd = PageEnd[:-2]
                                    backward = True
                            elif currentLanguage == u'conv':
                                siteExterne = getWiki('species', 'species')
                            else:
                                siteExterne = getWiki(currentLanguage, siteFamily)
                            if siteExterne == 'KO':
                                if debugLevel > 1: print u'  no site (--)'
                                PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '--')
                            elif siteExterne != u'':
                                if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find('}}'):
                                    pageExterne = PageTemp3[:PageTemp3.find(u'|')]
                                else:
                                    pageExterne = PageTemp3[:PageTemp3.find('}}')]
                            if pageExterne != u'' and pageExterne.find(u'<') != -1:
                                pageExterne = pageExterne[:pageExterne.find(u'<')]
                            if debugLevel > 1:
                                print u' Page distante : '
                                print pageExterne.encode(config.console_encoding, 'replace')

                            # Connexions aux Wiktionnaires pour vérifier la présence de la page (sous-entendu dans sa langue maternelle)
                            if siteExterne != u'' and pageExterne != u'':
                                pageFound = True
                                try:
                                    PageExt = Page(siteExterne, pageExterne)
                                except pywikibot.exceptions.BadTitle:
                                    if debugLevel > 1: print u'  BadTitle (-)'
                                    PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '-')
                                    pageFound = False
                                except pywikibot.exceptions.InvalidTitle:
                                    if debugLevel > 1: print u'  InvalidTitle (-)'
                                    PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '-')
                                    pageFound = False
                                except pywikibot.exceptions.NoPage:
                                    if debugLevel > 1: print u'  NoPage'
                                    if pageExterne.find(u'\'') != -1:
                                        pageExterne = pageExterne.replace(u'\'', u'’')
                                    elif pageExterne.find(u'’') != -1:
                                        pageExterne = pageExterne.replace(u'’', u'\'')
                                    if pageExterne != PageExt.title():
                                        try:
                                            PageExt = Page(siteExterne, pageExterne)
                                        except pywikibot.exceptions.NoPage:
                                            PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '-')
                                            pageFound = False
                                if pageFound:
                                    pageExtExists = True
                                    try:
                                        pageExtExists = PageExt.exists()
                                    except AttributeError:
                                        if debugLevel > 1: print u'  removed site (--)'
                                        PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '--')
                                        pageExtExists = False
                                    except pywikibot.exceptions.InconsistentTitleReceived:
                                        if debugLevel > 1: print u'  InconsistentTitleReceived (-)'
                                        PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '-')
                                        pageExtExists = False

                                    if pageExtExists:
                                        PageEnd, PageTemp = nextTranslationTemplate(PageEnd, PageTemp, '+')
                                        if debugLevel > 1: print u'  exists (+)'

                elif currentTemplate == u'(':
                    if translationSection:
                        PageEnd = PageEnd + u'trad-début'
                    else:
                        PageEnd = PageEnd + u'('
                    PageTemp = PageTemp[len(currentTemplate):]
                elif currentTemplate == u')':
                    if translationSection:
                        PageEnd = PageEnd + u'trad-fin'
                    else:
                        PageEnd = PageEnd + u')'
                    PageTemp = PageTemp[len(currentTemplate):]
                elif currentTemplate == u'trad-début':
                    if translationSection:
                        PageEnd = PageEnd + u'trad-début'
                    else:
                        PageEnd = PageEnd + u'('
                    PageTemp = PageTemp[len(currentTemplate):]
                elif currentTemplate == u'trad-fin':
                    if translationSection:
                        PageEnd = PageEnd + u'trad-fin'
                    else:
                        PageEnd = PageEnd + u')'
                    PageTemp = PageTemp[len(currentTemplate):]

                elif currentTemplate == u'fr-verbe-flexion':
                    if debugLevel > 0: print u'Flexion de verbe'
                    infinitive = getLemmaFromConjugation(PageBegin)
                    if infinitive != u'':
                        infinitivePage = getContentFromPageName(infinitive)
                        if infinitivePage != 'KO':
                            # http://fr.wiktionary.org/w/index.php?title=Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet
                            PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                            if PageTemp2.find(u'flexion=') != -1 and PageTemp2.find(u'flexion=') < PageTemp2.find('}}'):
                                PageTemp3 = PageTemp2[PageTemp2.find(u'flexion='):len(PageTemp2)]
                                if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
                                    PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')+PageTemp2.find(u'flexion=')+PageTemp3.find(u'|'):len(PageTemp)]
                            PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                            if PageTemp2.find(infinitive) == -1 or PageTemp2.find(infinitive) > PageTemp2.find('}}'):
                                PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|' + infinitive + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                if PageTemp.find(u'|' + infinitive + u'\n') != -1:    # Bug de l'hyperlien vers l'annexe
                                    PageTemp = PageTemp[:PageTemp.find(u'|' + infinitive + u'\n')+len(u'|' + infinitive)] + PageTemp[PageTemp.find(u'|' + infinitive + u'\n')+len(u'|' + infinitive + u'\n'):len(PageTemp)]
                            # Analyse du modèle en cours
                            PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                            PageTemp2 = PageTemp2[:PageTemp2.find('}}')+2]
                            if PageTemp2.find(u'impers=oui') == -1:
                                # http://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:fr-verbe-flexion&action=edit
                                if infinitivePage.find(u'{{impers') != -1 and infinitive != u'être':
                                    PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|impers=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                elif (infinitivePage.find(u'|groupe=1') != -1 or infinitivePage.find(u'|grp=1') != -1) and infinitivePage.find(u'|groupe2=') == -1:
                                    # je
                                    if PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        pass
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|sub.p.3s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|imp.p.2s=oui|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui|sub.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # tu
                                    if PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'sub.p.2s=oui') != -1:
                                        pass
                                    elif PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'sub.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|sub.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'sub.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # nous
                                    if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + PageTemp[PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.i.1p=oui') == -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # vous
                                    if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + PageTemp[PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.i.2p=oui') == -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # ils
                                    if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + PageTemp[PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.p.3p=oui') == -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                # Certains -ir sont du 3ème
                                elif (infinitivePage.find(u'|groupe=2') != -1 or infinitivePage.find(u'|grp=2') != -1) and infinitivePage.find(u'{{impers') == -1 and infinitivePage.find(u'|groupe2=') == -1:
                                    # je
                                    if PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        pass
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui')] + u'|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]

                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.p.1s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]

                                    #...
                                    if PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
                                        pass
                                    elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui')] + u'|sub.i.1s=oui' + PageTemp[PageTemp.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui' + PageTemp[PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui|sub.i.1s=oui' + PageTemp[PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(PageTemp)]
                                    elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.i.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # tu
                                    if PageTemp2.find(u'sub.p.2s=oui') != -1 and PageTemp2.find(u'sub.i.2s=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'sub.p.2s=oui') != -1 and PageTemp2.find(u'sub.i.2s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui')] + u'|sub.i.2s=oui' + PageTemp[PageTemp.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'sub.p.2s=oui') == -1 and PageTemp2.find(u'sub.i.2s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # il
                                    if PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'ind.ps.3s=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'ind.ps.3s=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|ind.ps.3s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'ind.ps.3s=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # nous
                                    if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + PageTemp[PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.i.1p=oui') == -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # vous
                                    if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + PageTemp[PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.i.2p=oui') == -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                    # ils
                                    if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
                                        pass
                                    if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + PageTemp[PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(PageTemp)]
                                    if PageTemp2.find(u'ind.p.3p=oui') == -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
                                elif (infinitivePage.find(u'|groupe=3') != -1 or infinitivePage.find(u'|grp=3') != -1) and infinitivePage.find(u'|groupe2=') == -1:
                                    if PageTemp2.find(u'grp=3') == -1:
                                        PageTemp = PageTemp[:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|grp=3' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):]

                    PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')+1]
                    PageTemp = PageTemp[PageTemp.find(u'\n')+1:]

                elif p < limit5:
                    if debugLevel > 0: print u' limit5 : paragraphe sans code langue contenant un texte'
                    addLanguageCode = False
                    if debugLevel > 0: print " addLanguageCode = " + str(addLanguageCode)
                    #trad = False
                    if PageTemp.find('}}') > PageTemp.find('{{') and PageTemp.find('{{') != -1:
                        PageTemp2 = PageTemp[PageTemp.find('}}')+2:]
                        PageEnd = PageEnd + PageTemp[:PageTemp.find('}}')+2+PageTemp2.find('}}')+2]
                        PageTemp = PageTemp[PageTemp.find('}}')+2+PageTemp2.find('}}')+2:]
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif p < limit6:
                    if debugLevel > 0: print u' limit6 : modèle sans paramètre'
                    PageEnd = PageEnd + currentTemplate + '}}'
                    PageTemp = PageTemp[PageTemp.find('}}')+2:]

                elif p < limit7:
                    if debugLevel > 0: print u' limit7 : paragraphe potentiellement avec code langue, voire |spéc='
                    if currentTemplate == PageTemp[:PageTemp.find('}}')]:
                        if addLanguageCode:
                            PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, languageCode)
                        else:
                            PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, 'nocat=1')
                    else:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

                elif p < limit8:
                    if debugLevel > 0: print u' limit8 : modèle catégorisé quel que soit addLanguageCode (ex : ébauches)'
                    if currentTemplate == u'ébauche' and not languageCode and PageTemp.find(u'== {{langue') != -1:
                        if debugLevel > 0: print u'  déplacement du 1e {{ébauche}} pour être traité après détermination de la langue'
                        nextSection = u'{{caractère}}'
                        if PageTemp.find(nextSection) == -1:
                            nextSection = u'{{langue|'
                        PageTemp2 = PageTemp[PageTemp.find(nextSection):]
                        PageTemp = PageTemp[PageTemp.find('}}')+2:PageTemp.find(nextSection)+PageTemp2.find(u'\n')+1] + u'{{ébauche}}\n' + PageTemp[PageTemp.find(nextSection)+PageTemp2.find(u'\n')+1:]
                        PageEnd = PageEnd[:-2]
                        backward = True
                    elif languageCode:
                        PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, languageCode)
                    else:
                       PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, 'nocat=1')

                else:
                    if debugLevel > 0: print u' Modèle régional : non catégorisé dans la prononciation'
                    if PageEnd.rfind('{{') != -1:
                        PageEnd2 = PageEnd[:PageEnd.rfind('{{')]
                        if addLanguageCode and ((PageEnd2.rfind('{{') != PageEnd2.rfind(u'{{pron|') and PageEnd2.rfind('{{') != PageEnd2.rfind(u'{{US|') and PageEnd2.rfind('{{') != PageEnd2.rfind(u'{{UK|')) or PageEnd.rfind(u'{{pron|') < PageEnd.rfind(u'\n') or PageEnd2.rfind(u'{{pron|') == -1) and ((PageTemp.find('{{') != PageTemp.find(u'{{pron|') or PageTemp.find(u'{{pron|') > PageTemp.find(u'\n')) or PageTemp.find(u'{{pron|') == -1):
                            PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, languageCode)
                        else:
                            PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp, currentTemplate, 'nocat=1')

                if debugLevel > 1:
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
                    pywikibot.output (u"\n\03{blue}Modèle traité\03{default}")
                    print (PageEnd.encode(config.console_encoding, 'replace')[:1000])
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
                    raw_input (PageTemp.encode(config.console_encoding, 'replace'))
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
            else:
                if debugLevel > 0: pywikibot.output (u"\n\03{blue}Modèle inconnu\03{default} " + currentTemplate)
                PageEnd, PageTemp = nextTemplate(PageEnd, PageTemp)

            if not backward:
                if debugLevel > 0:
                    message = u' Remplacement par \x1b[6;32;40m' + PageEnd[PageEnd.rfind('{{'):] + u'\x1b[0m\n\n'
                    print(message.encode(config.console_encoding, 'replace'))
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
                if debugLevel > 1:
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
                    raw_input(PageTemp.encode(config.console_encoding, 'replace'))
                    pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")

        PageEnd = PageEnd + PageTemp


        # Maintenance des genres
        PageEnd = PageEnd.replace(u'{{genre|fr}}\n# Masculin ', u'{{m}}\n# Masculin ')
        PageEnd = PageEnd.replace(u'{{genre|fr}}\n# Féminin ', u'{{f}}\n# Féminin ')
        PageEnd = PageEnd.replace(u"{{genre|fr}}\n# ''Masculin ", u"{{m}}\n# ''Masculin ")
        PageEnd = PageEnd.replace(u"{{genre|fr}}\n# ''Féminin ", u"{{f}}\n# ''Féminin ")
        if pageName[-3:] == u'eur':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-3:] == u'eux':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'euse':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'ant':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'ante':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-4:] == u'ance':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'age':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'ette':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'ier':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-3:] == u'ien':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-5:] == u'ienne':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'rie':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'ois':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'oise':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'ais':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'aise':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-5:] == u'logie':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-4:] == u'tion':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-3:] == u'ité':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-4:] == u'isme':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-2:] == u'el':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'elle':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-2:] == u'if':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-3:] == u'ive':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
        if pageName[-4:] == u'ment':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-5:] == u'ments':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
        if pageName[-4:] == u'iste':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{mf}}")
        if pageName[-4:] == u'aire':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{mf}}")
        if pageName[-1:] == u'é':
            PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")

        if debugLevel > 0: print u'Genre manquant de locution'
        if pageName.find(u' ') != -1 and pageName.find(u'{{langue|fr}}') != -1:
            pageLemma = getLemmaFromLocution(pageName)
            if pageLemma != u'':
                genre = u''
                if pageLemma.find(u'|fr}} {{m}}') != -1:
                    genre = u'{{m}}'
                elif pageLemma.find(u'|fr}} {{f}}') != -1:
                    genre = u'{{f}}'
                if genre != u'':
                    PageEnd = PageEnd.replace(u'{{genre|fr}}', genre)

        if debugLevel > 0: print u'Formatage des flexions'
        regex = ur"(=== {{S\|nom\|fr)\|flexion(}} ===\n'''" + rePageName + ur"''' [^\n]*{{fsing}})"
        if re.search(regex, PageEnd):
            PageEnd = re.sub(regex, ur'\1\2', PageEnd)
            summary = summary + u', un nom féminin n\'est pas une flexion en français'

        if pageName.find(u'*') == -1 and pageName[-1:] == 's':
            natures = [u'nom', u'adjectif', u'suffixe']
            language = u'fr'
            pageLemma = getLemmaFromPlural(PageEnd) # TODO language, nature, & n°
            if pageLemma != u'': treatPageByName(pageLemma) # Formatage des boites de flexion à récupérer
            for nature in natures:
                regex = ur"(== {{langue|" + language + ur"}} ==\n=== {{S\|" + nature + ur"\|" + language + ur")\|num=2"
                if re.search(regex, PageEnd):
                    PageEnd = re.sub(regex, ur'\1', PageEnd)
                    summary = summary + u', retrait de |num='

                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur")(\}} ===\n[^\n]*\n*'''" + rePageName + ur"'''[^\n]*\n# *'*'*(Masculin)*(Féminin)* *[P|p]luriel de *'*'* *\[\[)"
                if re.search(regex, PageEnd):
                    PageEnd = re.sub(regex, ur'\1|flexion\2', PageEnd)
                    summary = summary + u', ajout de |flexion'

                if pageName[-2:] != 'ss':
                    if pageLemma != u'':
                        flexionFlexionTemplate = getFlexionTemplate(pageName, language, nature)
                        if flexionFlexionTemplate == u'':
                            if debugLevel > 0: print u' Ajout d\'une boite dans une flexion'
                            lemmaFlexionTemplate = getFlexionTemplateFromLemma(pageLemma, language, nature)
                            for flexionTemplateWithMs in flexionTemplatesWithMs:
                                if lemmaFlexionTemplate.find(flexionTemplateWithMs) != -1:
                                    if debugLevel > 0: print u'flexionTemplateWithMs'
                                    regex = ur"\|ms=[^\|}]*"
                                    if not re.search(regex, lemmaFlexionTemplate):
                                        lemmaFlexionTemplate = lemmaFlexionTemplate + ur'|ms=' + pageLemma
                            for flexionTemplateWithS in flexionTemplatesWithS:
                                if lemmaFlexionTemplate.find(flexionTemplateWithS) != -1:
                                    regex = ur"\|s=[^\|}]*"
                                    if not re.search(regex, lemmaFlexionTemplate):
                                        lemmaFlexionTemplate = lemmaFlexionTemplate + ur'|s=' + pageLemma

                            ''' Remplacement des {{fr-rég}} par plus précis (lancé pour patcher des pages)
                            if lemmaFlexionTemplate.find(language + ur'-rég') != -1: lemmaFlexionTemplate = u''
                            if lemmaFlexionTemplate != u'':
                                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n){{fr\-rég\|[^}]*}}"
                                if re.search(regex, PageEnd):
                                    PageEnd = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}', PageEnd)
                                    summary = summary + u', remplacement de {{' + language + ur'-rég}} par {{' + lemmaFlexionTemplate + ur'}}'
                            '''

                            if lemmaFlexionTemplate != u'':
                                regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''')"
                                if re.search(regex, PageEnd):
                                    PageEnd = re.sub(regex, ur'\1{{' + lemmaFlexionTemplate + ur'}}\n\2', PageEnd)
                                    summary = summary + u', ajout de {{' + lemmaFlexionTemplate + ur'}} depuis le lemme'

                    if pageName[-1:] != 's':
                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)(\|" + language + ur"}}\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, PageEnd):
                            #PageEnd = re.sub(regex, ur'\1{{' + language + ur'-rég|s=\7|\3}}\n\2\3\4\7', PageEnd)
                            PageEnd = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + pageLemma + u'|\3}}\n\2\3\4\5', PageEnd)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

                        regex = ur"(=== {{S\|" + nature + ur"\|" + language + ur"\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'* *[P|p]luriel de *'*'* *\[\[)([^#\|\]]+)"
                        if re.search(regex, PageEnd):
                            PageEnd = re.sub(regex, ur'\1{{' + language + ur'-rég|s=' + pageLemma + u'|}}\n\2\5', PageEnd)
                            summary = summary + u', ajout de {{' + language + ur'-rég}}'

            if debugLevel > 1: raw_input(PageEnd.encode(config.console_encoding, 'replace'))

            # Anglais
            if pageName[-2:] != 'ss' and pageName[-3:] != 'hes' and pageName[-3:] != 'ies' and pageName[-3:] != 'ses' and pageName[-3:] != 'ves':
                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"''' {{pron\|)([^\|}]*)([s|z]\|en}}\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, PageEnd):
                    PageEnd = re.sub(regex, ur'\1{{en-nom-rég|sing=\5|\3}}\n\2\3\4\5', PageEnd)
                    summary = summary + u', ajout de {{en-nom-rég}}'

                regex = ur"(=== {{S\|nom\|en\|flexion}} ===\n)('''" + pageName + ur"'''\n# *'*'*Pluriel de *'*'* *\[\[)([^#\|\]]+)"
                if re.search(regex, PageEnd):
                    PageEnd = re.sub(regex, ur'\1{{en-nom-rég|sing=\3|}}\n\2\3', PageEnd)
                    summary = summary + u', ajout de {{en-nom-rég}}'

        if debugLevel > 0: print u'\nSynchro des prononciations'
        #TODO: prononciations post-paramètres (à déplacer ?) + tous les modèles, fr-accord-rég... https://fr.wiktionary.org/wiki/Utilisateur:JackBot/test_court
        regex = ur"({{fr\-inv\|)([^{}\|]+)([^{}]*}}\n\'\'\'" + rePageName.replace(u'User:',u'') + ur"'\'\')( *{*f?m?n?}* *)\n"
        if re.search(regex, PageEnd): PageEnd = re.sub(regex, ur'\1\2\3 {{pron|\2|fr}}\4\n', PageEnd)
        regex = ur"({{fr\-rég\|)([^{}\|]+)([^{}]*}}\n'\'\'" + rePageName.replace(u'User:',u'') + ur"'\'\')( *{*f?m?n?}* *)\n"
        if re.search(regex, PageEnd): PageEnd = re.sub(regex, ur'\1\2\3 {{pron|\2|fr}}\4\n', PageEnd)
        # pb des {{fr-rég|p=...|pron}} = {{pron|p|fr}}
        regex = ur"{{pron\|([^}]+)\|fr}}" # TODO: intl
        Prononciations = re.findall(regex, PageEnd)
        if debugLevel > 1: print " " + " ".join(Prononciations).encode(config.console_encoding, 'replace')
        for pron in Prononciations:
            pronInitiale = re.escape(pron)    # Pour retrouver la chaine à susbtituer
            while pron.find(u'=') != -1:
                if debugLevel > 0: print u' prononciation existante trouvée'
                pron = pron[:pron.find(u'=')]
                pron = pron[:pron.rfind(u'|')]
                PageEnd = re.sub(ur'{{pron\|'+pronInitiale+ur'\|fr}}', ur'{{pron|'+pron+ur'|fr}}', PageEnd)

        # Liens vers les annexes de conjugaisons
        LanguesC = [ (u'es',u'ar',u'arsi',u'er',u'ersi',u'ir',u'irsi'),
                     (u'pt',u'ar',u'ar-se',u'er',u'er-se',u'ir',u'ir-se'),
                     (u'it',u'are',u'arsi',u'ere',u'ersi',u'ire',u'irsi'),
                     (u'fr',u'er',u'er',u'ir',u'ir',u're',u'ar'),
                     (u'ru',u'',u'',u'',u'',u'',u'')
                   ]
        if not pageName in [u'ça va', u'ché', u'estoufaresse', u'estoufarès', u'reco', u'rpz'] and PageEnd.find(u'{{voir-conj') == -1 and PageEnd.find(u'[[Image:') == -1:    # Sinon bugs (ex : https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687, https://fr.wiktionary.org/w/index.php?title=%C3%A7a_va&diff=next&oldid=21742913)
            if debugLevel > 0: print u'Ajout de {{conj}}'
            for l in LanguesC:
                if not (l[0] == u'fr' and pageName[-3:] == u'ave'):
                    if re.compile(ur'{{S\|verbe\|'+l[0]+'}}').search(PageEnd) and not re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[= ]+\n+[^\n]*\n*[^\n]*\n*{{conj[a-z1-3\| ]*').search(PageEnd):
                        if debugLevel > 0: print u' {{conj|'+l[0]+u'}} manquant'
                        if re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}').search(PageEnd):
                            if debugLevel > 0: print u' ajout de {{conj|'+l[0]+u'}} après {{pron|...}}'
                            try:
                                i1 = re.search(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}',PageEnd).end()
                                PageEnd = PageEnd[:i1] + u' {{conjugaison|'+l[0]+'}}' + PageEnd[i1:]
                            except:
                                if debugLevel > 0: print u' Erreur l 5390'
                        else:
                            if debugLevel > 0: print u' pas de prononciation pour ajouter {{conj}}'
    
        if PageEnd.find(u'{{conj') != -1:
            if debugLevel > 0: print u' Ajout des groupes dans {{conj}}'
            '''for (langue,premier,ppron,deuxieme,dpron,troisieme,tpron) in LanguesC:
                if premier != u'':

                    if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + '}}').search(PageEnd) and not re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}.*\n*.*{{conj[a-z1-3\| ]*').search(PageEnd):
                        if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*\n*[ ^\[]*{{pron\|').search(PageEnd):
                            if pageName[len(pageName)-len(premier):] == premier or pageName[len(pageName)-len(ppron):] == ppron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
                                    PageEnd = PageEnd[:i1] + u' {{conj|grp=1|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + premier
                            elif pageName[len(pageName)-len(premier):] == deuxieme or pageName[len(pageName)-len(ppron):] == dpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
                                    PageEnd = PageEnd[:i1] + u' {{conj|grp=2|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + deuxieme
                            elif pageName[len(pageName)-len(premier):] == troisieme or pageName[len(pageName)-len(ppron):] == tpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
                                    PageEnd = PageEnd[:i1] + u' {{conj|grp=3|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + troisieme
                        else:
                            if pageName[len(pageName)-len(premier):] == premier or pageName[len(pageName)-len(ppron):] == ppron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*\'\'\'',PageEnd).end()
                                    if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + '}}' + PageEnd[i1:]
                                    elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
                                        PageEnd = PageEnd[:i1] + PageEnd[i1:][:PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2] + u' {{conj|grp=1|' + langue + '}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2:len(PageEnd[i1:])]
                                    elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=1|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
                            elif pageName[len(pageName)-len(premier):] == deuxieme or pageName[len(pageName)-len(ppron):] == dpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',PageEnd).end()
                                    if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + '}}' + PageEnd[i1:]
                                    elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
                                        PageEnd = PageEnd[:i1] + PageEnd[i1:][:PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2] + u' {{conj|grp=2|' + langue + '}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2:len(PageEnd[i1:])]
                                    elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=2|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
                            elif pageName[len(pageName)-len(premier):] == troisieme or pageName[len(pageName)-len(ppron):] == tpron:
                                try:
                                    i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',PageEnd).end()
                                    if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + '}}' + PageEnd[i1:]
                                    elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
                                        PageEnd = PageEnd[:i1] + PageEnd[i1:][:PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2] + u' {{conj|grp=3|' + langue + '}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find('}}')+2:len(PageEnd[i1:])]
                                    elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
                                        PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=3|' + langue + '}}' + PageEnd[i1:]
                                except:
                                    print pageName.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
            '''

    else:
        PageEnd = PageTemp

    if debugLevel > 0: pywikibot.output (u"\n\03{red}---------------------------------------------\03{default}")
    if PageEnd != PageBegin:
        if page.namespace() == u'':
            # Modifications mineures, ne justifiant pas une édition à elles seules
            PageEnd = PageEnd.replace(u'  ', u' ')
            PageEnd = PageEnd.replace(u'\n\n\n\n', u'\n\n\n')
            PageEnd = PageEnd.replace(u'.\n=', u'.\n\n=')
        savePage(page, PageEnd, summary)
    elif debugLevel > 0:
        print "Aucun changement"


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
            treatPageByName(u'Annexe:Liste de racines en indo-européen commun')
            treatPageByName(u'Annexe:Réforme orthographique française de 1878')
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
            p.pagesByCat(u'Catégorie:Pages avec ISBN invalide', namespaces = None, afterPage = afterPage)
            #TODO: ISSN
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
        p.pagesByCat(u'Catégorie:Wiktionnaire:Terminologie sans langue précisée', recursive = True)
        p.pagesByCat(u'Catégorie:Wiktionnaire:Flexions à vérifier', recursive = True)
        p.pagesByCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée')
        p.pagesByCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Ébauches à compléter')
        p.pagesByLink(u'Modèle:trad')
        p.pagesByLink(u'Modèle:1ergroupe')
        p.pagesByLink(u'Modèle:2egroupe')
        p.pagesByLink(u'Modèle:3egroupe')
        p.pagesByLink(u'Modèle:-')
        p.pagesByLink(u'Modèle:-ortho-alt-')
        p.pagesByLink(u'Modèle:mascul')
        p.pagesByLink(u'Modèle:fémin')
        p.pagesByLink(u'Modèle:femin')
        p.pagesByLink(u'Modèle:sing')
        p.pagesByLink(u'Modèle:plur')
        p.pagesByLink(u'Modèle:pluri')
        p.pagesByLink(u'Modèle:=langue=')
        p.pagesByLink(u'Modèle:-déf-')
        p.pagesByLink(u'Modèle:pron-rég')
        p.pagesByLink(u'Modèle:mp')
        p.pagesByLink(u'Modèle:fp')
        p.pagesByLink(u'Modèle:vx')
        p.pagesByCat(u'Catégorie:Traduction en français demandée d’exemple(s) écrits en français')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections avec titre inconnu')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections avec paramètres superflus')
        p.pagesByCat(u'Catégorie:Wiktionnaire:Sections utilisant un alias')

if __name__ == "__main__":
    main(sys.argv)

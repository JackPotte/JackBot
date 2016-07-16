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

# Importation des modules
import catlib, pagegenerators, os, codecs, urllib, re, collections, socket, langues
import hyperlynx, CleDeTri, HTMLUnicode		# Faits maison
from wikipedia import *
''' Bug des n° de lignes auto
from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print str(frameinfo.lineno)
'''

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
siteEN = getSite('en',family)
debogageLent = False
TailleAnagramme = 4 # sinon trop long : 5 > 5 min, 8 > 1 h par page)
Modele = [] # Liste des modèles du site à traiter
Section = [] # Sections à remplacer
# Paragraphes autorisant les modèles catégorisants par langue ({{voir| et {{voir/ sont gérés individuellement)
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_type_de_mot_du_Wiktionnaire
Modele.append(u'S')
Section.append(u'S')
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
limit14 = len(Modele)
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
limit15 = len(Modele)
Modele.append(u'-notes-')
Section.append(u'notes')
Modele.append(u'-note-')
Section.append(u'note')
Modele.append(u'trad-trier')
Section.append(u'traductions à trier')
limit2 = len(Modele)
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
Modele.append(u'voir')
Modele.append(u'préciser')
limit25 = len(Modele)
Modele.append(u'mf?')
Modele.append(u'fm?')
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
limit3 = len(Modele)
Modele.append(u'pron')
Modele.append(u'écouter')
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
Modele.append(u'boissons')
Modele.append(u'botan')
Modele.append(u'botanique')
Modele.append(u'boucherie')
Modele.append(u'bouddhisme')
Modele.append(u'bowling')
Modele.append(u'boxe')
Modele.append(u'calendrier')
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
Modele.append(u'chimie organique')
Modele.append(u'chimie physique')
Modele.append(u'chir')
Modele.append(u'chiromancie')
Modele.append(u'chirurgie')
Modele.append(u'christianisme')
Modele.append(u'ciné')
Modele.append(u'cinéma')
Modele.append(u'cirque')
Modele.append(u'cocktails')
Modele.append(u'coiffure')
Modele.append(u'coléoptères')
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
Modele.append(u'créatures')
Modele.append(u'cricket')
Modele.append(u'crimes')
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
Modele.append(u'dés')
Modele.append(u'desserts')
Modele.append(u'desserts')
Modele.append(u'dessin')
Modele.append(u'désuet')
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
Modele.append(u'fig.')
Modele.append(u'figure')
Modele.append(u'figuré')
Modele.append(u'figures')
Modele.append(u'finan')
Modele.append(u'finance')
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
Modele.append(u'geog')	# à remplacer ?
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
Modele.append(u'mollusques')
Modele.append(u'monarchie')
Modele.append(u'monnaies')
Modele.append(u'montagnes')
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
Modele.append(u'non standard')
Modele.append(u'nosologie')
Modele.append(u'note-gentilé')
Modele.append(u'novlangue')
Modele.append(u'nucl')
Modele.append(u'nucléaire')
Modele.append(u'numis')
Modele.append(u'numismatique')
Modele.append(u'nutrition')
Modele.append(u'obsolète')
Modele.append(u'oenol')
Modele.append(u'oenologie')
Modele.append(u'oiseaux')
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
Modele.append(u'papeterie')
Modele.append(u'papèterie')
Modele.append(u'papillons')
Modele.append(u'par analogie')
Modele.append(u'par dérision')
Modele.append(u'par ellipse')
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
Modele.append(u'péj')
Modele.append(u'péjoratif')
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
Modele.append(u'pop')
Modele.append(u'popu')
Modele.append(u'populaire')
Modele.append(u'positions')
Modele.append(u'ppart')
Modele.append(u'préhistoire')
Modele.append(u'prépositionnel')
Modele.append(u'presse')
Modele.append(u'prnl')
Modele.append(u'probabilités')
Modele.append(u'prog')
Modele.append(u'programmation')
Modele.append(u'pronl')
Modele.append(u'pronominal')
Modele.append(u'propre')
Modele.append(u'propriété')
Modele.append(u'protéines')
Modele.append(u'protocoles')
Modele.append(u'prov')
Modele.append(u'proverbes')
Modele.append(u'proverbial')
Modele.append(u'psych')
Modele.append(u'psychia')
Modele.append(u'psychiatrie')
Modele.append(u'psycho')
Modele.append(u'psycho')
Modele.append(u'psychol')
Modele.append(u'psychologie')
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
Modele.append(u'salades')
Modele.append(u'sandwitchs')
Modele.append(u'satellites')
Modele.append(u'saules')
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
Modele.append(u'temps géologiques')
Modele.append(u'tennis')
Modele.append(u'tennis de table')
Modele.append(u'term')
Modele.append(u'terme')
Modele.append(u'terme non standard')
Modele.append(u'text')
Modele.append(u'text')
Modele.append(u'textile')
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
Modele.append(u'vx')
Modele.append(u'wiki')
Modele.append(u'yoga')
Modele.append(u'zool')
Modele.append(u'zoologie')
limit4 = len(Modele)
# Code langue quoi qu'il arrive
Modele.append(u'ébauche-syn')
Modele.append(u'note-gentilé')
Modele.append(u'ébauche-trans')
Modele.append(u'ébauche-étym-nom-scientifique')
Modele.append(u'ébauche-étym')
Modele.append(u'ébauche-déf')
Modele.append(u'ébauche-exe')
Modele.append(u'ébauche-pron')
Modele.append(u'ébauche')
Modele.append(u'...')
limit5 = len(Modele)
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
limit6 = len(Modele) # Somme des modèles traités
'''
# Non traités
arbres : 3 paramètres

Modele[] = u'fr-rég'
Modele[] = u'fr-inv'
Modele[] = u'fr-accord-rég'
Modele[] = u'en-nom-rég'

	# Sans code langue
		Modele[] = u'spécialement'
		Modele[] = u'région'
		Modele[] = u'régio'
		Modele[] = u'régional'
		
	# Utilisés sur la ligne de forme (parfois sans parenthèses)
		Modele[] = u'déterminé'
		Modele[] = u'indéterminé'
		Modele[] = u'dét'
		Modele[] = u'indét'
		Modele[] = u'perfectif'
		Modele[] = u'imperfectif'
		Modele[] = u'perf'
		Modele[] = u'imperf'
		
Modele[] = u'T' : à synchroniser
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
Genre.append(u'mf?')
Genre.append(u'fm ?')
Genre.append(u'fm?')
Genre.append(u'mplur')
Genre.append(u'msing')
Genre.append(u'n')
Genre.append(u'nplur')
Genre.append(u'nsing')

# Modification du wiki
def modification(PageC):
	#PageC = u'Catégorie:'+PageC[:1].upper()+PageC[1:]
	summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
	if debogage: print u'------------------------------------'
	print(PageC.encode(config.console_encoding, 'replace'))
	
	if PageC.find(u'’') != -1:
		page = Page(site,PageC.replace(u'’', u'\''))
		if not page.exists():
			if debogage: print u'Création d\'une redirection apostrophe'
			sauvegarde(page, u'#REDIRECT[[' + PageC + ']]', u'Redirection pour apostrophe')
	page = Page(site,PageC)
	if page.exists():
		if page.namespace() !=0 and page.namespace() != 100 and page.namespace() != 12 and page.namespace() != 14 and PageC.find(u'Utilisateur:JackBot/') == -1:
			print u'Page non traitée l 1374'
			return
		else:
			try:
				PageBegin = page.get()
			except wikipedia.NoPage:
				print u'NoPage l 1383'
				return
			except wikipedia.IsRedirectPage: 
				PageBegin = page.get(get_redirect=True)
				TxtTmp = u'<!--\n  Redirection créée par le robot User:DaftBot.\n  La création automatique de la page ciblée est prévue prochainement.\n-->'
				if PageBegin.find(TxtTmp) != -1:
					summary = u'[[Catégorie:Redirections à remplacer]]'
					PageBegin = PageBegin[0:PageBegin.find(TxtTmp)] + summary + PageBegin[PageBegin.find(TxtTmp)+len(TxtTmp):len(PageBegin)]
					sauvegarde(page, PageBegin, summary)
				else:
					print u'IsRedirect l 1393'
				return
	else:
		print u'NoPage l 1396'
		return
	PageTemp = PageBegin
	CleTri = CleDeTri.CleDeTri(PageC)
	
	if page.namespace() == 14:
		if debogage: print u'Catégorie'
		# Catégorie
		#if PageC.find(u'Catégorie:Lexique en français d') != -1 and PageTemp.find(u'[[Catégorie:Lexiques en français|') == -1:
		#	PageTemp = PageTemp + u'\n[[Catégorie:Lexiques en français|' + CleDeTri.CleDeTri(trim(PageC[PageC.rfind(' '):])) + u']]\n'
		PageEnd = PageBegin
		
	elif page.namespace() == 0 or PageC.find(u'Utilisateur:JackBot/') != -1:
		regex = ur'{{=([a-z\-]+)=}}'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, ur'{{langue|\1}}', PageTemp)
		
		while PageTemp.find(u'{{ ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{ ')+2] + PageTemp[PageTemp.find(u'{{ ')+3:len(PageTemp)]
		if PageTemp.find(u'{{formater') != -1 or PageTemp.find(u'{{SI|') != -1 or PageTemp.find(u'{{SI}}') != -1 or PageTemp.find(u'{{supp|') != -1 or PageTemp.find(u'{{supp}}') != -1 or PageTemp.find(u'{{supprimer|') != -1 or PageTemp.find(u'{{supprimer') != -1 or PageTemp.find(u'{{PàS') != -1 or PageTemp.find(u'{{S|faute') != -1 or PageTemp.find(u'{{S|erreur') != -1:
			if debogage: print u'Page en travaux : non traitée l 1409'
			return
		
		# Alias d'anciens titres de section
		PageTemp = PageTemp.replace(u'{{-car-}}', u'{{caractère}}')
		PageTemp = PageTemp.replace(u'{{-note-|s=s}}', u'{{-notes-}}')
		PageTemp = PageTemp.replace(u'{{-etym-}}', u'{{-étym-}}')
		PageTemp = PageTemp.replace(u'-pronom-personnel-', u'-pronom-pers-')
		
		if debogage: print u'Conversion vers {{S}}'
		EgalSection = u'==='
		for p in range(1,limit2):
			if p == limit14: EgalSection = u'===='
			if p == limit15: EgalSection = u'====='
			
			regex = ur'[= ]*{{[\-loc]*(' + Modele[p] + ur'|S\|'+ Section[p] + ur')([^}]*)}}[= ]*'
			if re.search(regex, PageTemp):
				PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'\2}} ' + EgalSection, PageTemp)

			regex = ur'[= ]*{{\-flex[\-loc]*(' + Modele[p] + ur'|S\|' + Section[p] + ur')\|([^}]*)}}[= ]*'
			if re.search(regex, PageTemp):
				PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'|\2|flexion}} ' + EgalSection, PageTemp)

		if debogageLent: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		if PageTemp.find(u'|===') != -1 or PageTemp.find(u'{===') != -1:
			if debogage: print u' *==='
			return
		
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
		PageTemp = PageTemp.replace(u'{{S|locution phrase|', u'{{S|locution-phrase|')
		PageTemp = PageTemp.replace(u'{{S|nom commun', u'{{S|nom|')
		PageTemp = PageTemp.replace(u'{{S|nom-fam|', u'{{S|nom de famille|')
		PageTemp = PageTemp.replace(u'{{S|nom-pr|', u'{{S|nom propre|')
		PageTemp = PageTemp.replace(u'{{S|phrase|', u'{{S|locution-phrase|')
		PageTemp = PageTemp.replace(u'{{S|symb|', u'{{S|symbole|')
		PageTemp = PageTemp.replace(u'{{S|verb|', u'{{S|verbe|')
		# Alias peu intuitifs des sections sans langue
		PageTemp = re.sub(ur'{{S\|abr(é|e)v\|?[a-z]*}}', u'{{S|abréviations}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|anagr\|?[a-z]*}}', u'{{S|anagrammes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|ant\|?[a-z]*}}', u'{{S|antonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|app\|?[a-zé]*}}', u'{{S|apparentés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|apr\|?[a-zé]*}}', u'{{S|apparentés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|compos\|?[a-zé]*}}', u'{{S|composés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|dial\|?[a-z]*}}', u'{{S|variantes dialectales}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|dimin\|?[a-z]*}}', u'{{S|diminutifs}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|d(é|e)riv(é|e)\|?[a-z]*}}', u'{{S|dérivés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|drv\|?[a-z]*}}', u'{{S|dérivés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|dérivés int\|?[a-z]*}}', u'{{S|dérivés autres langues}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|drv\-int\|?[a-z]*}}', u'{{S|dérivés autres langues}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|(é|e)tym\|?[a-z]*}}', u'{{S|étymologie}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|exp\|?[a-z]*}}', u'{{S|expressions}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|gent\|?[a-zé]*}}', u'{{S|gentilés}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|holo\|?[a-z]*}}', u'{{S|holonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|homo\|?[a-z]*}}', u'{{S|homophones}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|hyper\|?[a-z]*}}', u'{{S|hyperonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|hypo\|?[a-z]*}}', u'{{S|hyponymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|m(é|e)ro\|?[a-z]*}}', u'{{S|méronymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|paro\|?[a-z]*}}', u'{{S|paronymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|pron\|?[a-z]*}}', u'{{S|prononciation}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|q\-syn\|?[a-z]*}}', u'{{S|quasi-synonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|quasi(\-| )syn\|?[a-z]*}}', u'{{S|quasi-synonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|r(é|e)f\|?[a-zé]*}}', u'{{S|références}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|syn\|?[a-z]*}}', u'{{S|synonymes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|trad\|?[a-z]*}}', u'{{S|traductions}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|trad\-trier\|?[a-z]*}}', u'{{S|traductions à trier}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|var\|?[a-z]*}}', u'{{S|variantes}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|var[a-z]*(\-| )ortho\|?[a-z]*}}', u'{{S|variantes orthographiques}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|voc\|?[a-z]*}}', u'{{S|vocabulaire}}', PageTemp)
		PageTemp = re.sub(ur'{{S\|voir\|?[a-z]*}}', u'{{S|voir aussi}}', PageTemp)
		
		'''
		raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		PageTemp = PageTemp.replace(u'{{S|abrév}}', u'{{S|abréviations}}')
		PageTemp = PageTemp.replace(u'{{S|anagramme}}', u'{{S|anagrammes}}')
		PageTemp = PageTemp.replace(u'{{S|anagr}}', u'{{S|anagrammes}}')
		PageTemp = PageTemp.replace(u'{{S|ant}}', u'{{S|antonymes}}')
		PageTemp = PageTemp.replace(u'{{S|anto}}', u'{{S|antonymes}}')
		PageTemp = PageTemp.replace(u'{{S|antonyme}}', u'{{S|antonymes}}')
		PageTemp = PageTemp.replace(u'{{S|app}}', u'{{S|apparentés}}')
		PageTemp = PageTemp.replace(u'{{S|apparenté}}', u'{{S|apparentés}}')
		PageTemp = PageTemp.replace(u'{{S|apr}}', u'{{S|apparentés}}')
		PageTemp = PageTemp.replace(u'{{S|apparentés étymologiques}}', u'{{S|apparentés}}')
		PageTemp = PageTemp.replace(u'{{S|compos}}', u'{{S|composés}}')
		PageTemp = PageTemp.replace(u'{{S|composé}}', u'{{S|composés}}')
		PageTemp = PageTemp.replace(u'{{S|dial}}', u'{{S|variantes dialectales}}')
		PageTemp = PageTemp.replace(u'{{S|dimin}}', u'{{S|diminutifs}}')
		PageTemp = PageTemp.replace(u'{{S|diminutif}}', u'{{S|diminutifs}}')
		PageTemp = PageTemp.replace(u'{{S|dérivé}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|dérivéés}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|derives}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|drv|en}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|drv}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|drv-int}}', u'{{S|dérivés autres langues}}')
		PageTemp = PageTemp.replace(u'{{S|etym}}', u'{{S|étymologie}}')
		PageTemp = PageTemp.replace(u'{{S|étym}}', u'{{S|étymologie}}')
		PageTemp = PageTemp.replace(u'{{S|etymologie}}', u'{{S|étymologie}}')
		PageTemp = PageTemp.replace(u'{{S|étymologies}}', u'{{S|étymologie}}')
		PageTemp = PageTemp.replace(u'{{S|exp}}', u'{{S|expressions}}')
		PageTemp = PageTemp.replace(u'{{S|expr}}', u'{{S|expressions}}')
		PageTemp = PageTemp.replace(u'{{S|expression}}', u'{{S|expressions}}')
		PageTemp = PageTemp.replace(u'{{S|gent}}', u'{{S|gentilés}}')
		PageTemp = PageTemp.replace(u'{{S|gentilé}}', u'{{S|gentilés}}')
		PageTemp = PageTemp.replace(u'{{S|holo}}', u'{{S|holonymes}}')
		PageTemp = PageTemp.replace(u'{{S|holonyme}}', u'{{S|holonymes}}')
		PageTemp = PageTemp.replace(u'{{S|homo}}', u'{{S|homophones}}')
		PageTemp = PageTemp.replace(u'{{S|homophone}}', u'{{S|homophones}}')
		PageTemp = PageTemp.replace(u'{{S|homonymes}}', u'{{S|homophones}}')
		PageTemp = PageTemp.replace(u'{{S|hyper}}', u'{{S|hyperonymes}}')
		PageTemp = PageTemp.replace(u'{{S|hyperonyme}}', u'{{S|hyperonymes}}')
		PageTemp = PageTemp.replace(u'{{S|hypo}}', u'{{S|hyponymes}}')
		PageTemp = PageTemp.replace(u'{{S|hyponyme}}', u'{{S|hyponymes}}')
		PageTemp = PageTemp.replace(u'{{S|méro}}', u'{{S|méronymes}}')
		PageTemp = PageTemp.replace(u'{{S|méronyme}}', u'{{S|méronymes}}')
		PageTemp = PageTemp.replace(u'{{S|paro}}', u'{{S|paronymes}}')
		PageTemp = PageTemp.replace(u'{{S|paronyme}}', u'{{S|paronymes}}')
		PageTemp = PageTemp.replace(u'{{S|pron}}', u'{{S|prononciation}}')
		PageTemp = PageTemp.replace(u'{{S|prononciations}}', u'{{S|prononciation}}')
		PageTemp = PageTemp.replace(u'{{S|q-syn}}', u'{{S|quasi-synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|quasi-synonyme}}', u'{{S|quasi-synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|quasi synonymes}}', u'{{S|quasi-synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|réf}}', u'{{S|références}}')
		PageTemp = PageTemp.replace(u'{{S|référence}}', u'{{S|références}}')
		PageTemp = PageTemp.replace(u'{{S|syn}}', u'{{S|synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|synonyme}}', u'{{S|synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|trad-trier}}', u'{{S|traductions à trier}}')
		PageTemp = PageTemp.replace(u'{{S|trad}}', u'{{S|traductions}}')
		PageTemp = PageTemp.replace(u'{{S|traduction}}', u'{{S|traductions}}')
		PageTemp = PageTemp.replace(u'{{S|var}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|variante}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|variantes ortho}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|var ortho}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|var-ortho}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|voc}}', u'{{S|vocabulaire}}')
		PageTemp = PageTemp.replace(u'{{S|vocabulaire apparenté par le sens}}', u'{{S|vocabulaire}}')
		PageTemp = PageTemp.replace(u'{{S|voir}}', u'{{S|voir aussi}}')
		'''

		# Formatage général des traductions
		PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier}}}}', u'{{trad-trier}}\n{{trad-début}}')
		PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier|fr}}}}', u'{{trad-trier}}\n{{trad-début}}')
		
			# 1) Suppression de {{ébauche-trad|fr}} (WT:PPS)
		PageTemp = PageTemp.replace(ur'{{ébauche-trad|fr}}', u'{{ébauche-trad}}')	 # bug ?
		regex = ur'{{ébauche\-trad\|fr}}'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, u'{{ébauche-trad}}', PageTemp)
		
			# 2) Aucun modèle d'ébauche en dehors d'une boite déroulante
		PageTemp = PageTemp.replace(ur'{{ébauche-trad}}\n{{trad-début}}', u'{{trad-début}}\n{{ébauche-trad}}') # bug ?
		regex = ur'{{ébauche\-trad}}\n{{trad\-début}}'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, u'{{trad-début}}\n{{ébauche-trad}}', PageTemp)
		
		PageTemp = PageTemp.replace(ur'==== {{S|traductions}} ====\n{{ébauche-trad}}\n', u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad}}\n{{trad-fin}}\n')	 # bug ?	
		regex = ur'==== {{S\|traductions}} ====\n{{ébauche\-trad}}(\n<![^>]+>)*(\n|$)'
		if re.search(regex, PageTemp):
			if debogage: print ' ébauche sans boite'
			PageTemp = re.sub(regex, u'==== {{S|traductions}} ====\n{{trad-début}}\n{{ébauche-trad|en}}\n{{trad-fin}}\n', PageTemp)

			# 3) Anciens commentaires d'aide à l'édition (tolérés avant l'éditeur visuel et editor.js)
		PageTemp = PageTemp.replace(ur'<!--* {{T|en}} : {{trad|en|}}-->', '')	 # bug ?
		regex = ur'<!\-\-[^{>]*{{T\|[^>]+>\n?'
		if re.search(regex, PageTemp):
			if debogage: print ' Commentaire trouvé l 1517'
			PageTemp = re.sub(regex, u'', PageTemp)
			# Cosmétique
		regex = ur'{{ébauche\-trad}}{{'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, u'{{ébauche-trad}}\n{{', PageTemp)
		
		#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		
		# 4) Contrôle du nombre de paragraphes de traduction par rapport au nombre de sens
		#if PageTemp.find(u'{{langue|fr}}') != -1:
			''' à faire 
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
				if debogage: print PageTemp2[:PageTemp2.find(u'\n')+1].encode(config.console_encoding, 'replace')
				if PageTemp2[:PageTemp2.find(u'\n')+1].find(u'trier') != -1: break
				PageTemp = PageTemp[:PageTemp.find(u'{{trad-fin}}\n* {{T|'):] + PageTemp2[:PageTemp2.find(u'\n')+1] + u'{{trad-fin}}\n' + PageTemp[PageTemp.find(u'{{trad-fin}}\n* {{T|')+delta+PageTemp2.find(u'\n')+1:]
			else:
				if debogage: print PageTemp2.encode(config.console_encoding, 'replace')
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
		
		if page.namespace() != 12:
			if debogage: print u'Ajout des {{voir}}'
			if PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageC[0:1].lower() + PageC[1:] + PageTemp[PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|{{lc:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{lc:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageC[0:1].upper() + PageC[1:] + PageTemp[PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|{{ucfirst:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{ucfirst:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageC[0:1].lower() + PageC[1:] + PageTemp[PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|{{LC:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{LC:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageC[0:1].upper() + PageC[1:] + PageTemp[PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|{{UCFIRST:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{UCFIRST:{{PAGENAME}}}}'	
			if PageTemp.find(u'{{voir|') == -1 and PageTemp.find(u'{{voir/') == -1:
				PageVoir = u''
				# Liste de toutes les pages potentiellement "à voir"
				PagesCleTotal = PageC
				if PagesCleTotal.find(PageC.lower()) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageC.lower()
				if PagesCleTotal.find(PageC.upper()) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageC.upper()
				if PagesCleTotal.find(PageC[0:1].lower() + PageC[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageC[0:1].lower() + PageC[1:]
				if PagesCleTotal.find(PageC[0:1].upper() + PageC[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageC[0:1].upper() + PageC[1:]
				if PagesCleTotal.find(u'-' + PageC[0:1].lower() + PageC[1:]) == -1: PagesCleTotal = PagesCleTotal + u'|-' + PageC[0:1].lower() + PageC[1:]
				if PagesCleTotal.find(PageC[0:1].lower() + PageC[1:] + u'-') == -1: PagesCleTotal = PagesCleTotal + u'|' + PageC[0:1].lower() + PageC[1:] + u'-'
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
						if PageC.find(LettresDiacritiques[l][d]) != -1:
							if debogageLent: print u'Titre contenant : ' + LettresDiacritiques[l][d]
							Lettre = LettresDiacritiques[l][d]
							for d in range(0,len(LettresDiacritiques[l])):
								PagesCleTotal = PagesCleTotal + u'|' + PageC.replace(Lettre,LettresDiacritiques[l][d])
				if PagesCleTotal.find(CleTri) == -1: PagesCleTotal = PagesCleTotal + u'|' + CleTri	# exception ? and PageTemp.find(u'{{langue|eo}}') == -1
				# Filtre des pages de la liste "à voir"
				PagesCleRestant = PagesCleTotal + u'|'
				PagesCleTotal = u''
				PagesVoir = u''
				if debogage: print u' Recherche des clés...'
				while PagesCleRestant != u'':
					if debogageLent: print PagesCleRestant.encode(config.console_encoding, 'replace')
					HS = u'False'
					PageCourante = PagesCleRestant[0:PagesCleRestant.find(u'|')]
					PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:len(PagesCleRestant)]
					PageCle = Page(site,PageCourante)
					try:
						PageTempCle = PageCle.get()
					except wikipedia.NoPage:
						HS = u'True'
					except wikipedia.IsRedirectPage:
						HS = u'True'
					except wikipedia.BadTitle:
						HS = u'True'
					if HS == u'False':
						if PagesCleTotal.find(PageCourante) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageCourante
						if PageTempCle.find(u'{{voir|') != -1:
							PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|'):len(PageTempCle)]
							PagesVoir = PagesVoir + u'|' + PageTempCle2[0:PageTempCle2.find(u'}}')]
						elif PageTempCle.find(u'{{voir/') != -1:
							PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir/')+len(u'{{voir/'):len(PageTempCle)]
							PageTemp = u'{{voir/' + PageTempCle2[0:PageTempCle2.find(u'}}')+3] + PageTemp
							pageMod = Page(site,u'Modèle:voir/' + PageTempCle2[0:PageTempCle2.find(u'}}')])
							try:
								PageTempModBegin = pageMod.get()
							except wikipedia.NoPage:
								if debogage: print u'no page'
								break
							except wikipedia.IsRedirectPage:
								if debogage: print "Redirect page"
								break
							PageTempMod = PageTempModBegin
							if PageTempMod.find(u'!') == -1:
								if PageTempMod.find(PageC) == -1: PageTempMod = PageTempMod[0:PageTempMod.find(u'}}')] + u'|' + PageC + PageTempMod[PageTempMod.find(u'}}'):len(PageTempMod)]
								if PageTempMod.find(PageVoir) == -1: PageTempMod = PageTempMod[0:PageTempMod.find(u'}}')] + u'|' + PageVoir + PageTempMod[PageTempMod.find(u'}}'):len(PageTempMod)]
							if PageTempMod != PageTempModBegin: sauvegarde(pageMod,PageTempMod, summary)
							PagesCleRestant = u''
							if debogage: print u'PagesCleRestant vide'
							break

				if debogage: print u' Filtre des doublons...'
				if PagesVoir != u'':
					PagesVoir = PagesVoir + u'|'
					while PagesVoir.find(u'|') != -1:
						if PagesCleTotal.find(PagesVoir[0:PagesVoir.find(u'|')]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PagesVoir[0:PagesVoir.find(u'|')]
						PagesVoir = PagesVoir[PagesVoir.find(u'|')+1:len(PagesVoir)]
				#raw_input(PagesCleTotal.encode(config.console_encoding, 'replace'))
				
				if debogage: print u' Balayage de toutes les pages "à voir"...'
				if PagesCleTotal != u'':
					while PagesCleTotal[0:1] == u'|': PagesCleTotal = PagesCleTotal[1:len(PagesCleTotal)]
				if PagesCleTotal != PageC:
					if debogage: print u'  Différent de la page courante'
					PagesCleRestant = PagesCleTotal + u'|'
					while PagesCleRestant.find(u'|') != -1:
						HS = u'False'
						PageCourante = PagesCleRestant[0:PagesCleRestant.find(u'|')]
						if PageCourante == u'':
							if debogage: print u'PageCourante vide'
							break
						PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:len(PagesCleRestant)]
						if PageCourante != PageC:
							PageCle = Page(site,PageCourante)
							try:
								PageTempCleBegin = PageCle.get()
							except wikipedia.NoPage:
								HS = u'True'
							except wikipedia.IsRedirectPage:
								HS = u'True'
						else:
							PageTempCleBegin = PageTemp
						if HS == u'False':
							PageTempCle = PageTempCleBegin
							if PageTempCle.find(u'{{voir/') != -1:
								if debogage: print u' {{voir/ trouvé'
								break
							elif PageTempCle.find(u'{{voir|') != -1:
								if debogage: print u' {{voir| trouvé'
								if PagesCleTotal.find(u'|' + PageCourante) != -1:
									PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|'):len(PageTempCle)]
									PageTempCle = PageTempCle[0:PageTempCle.find(u'{{voir|')+len(u'{{voir|')] + PagesCleTotal[0:PagesCleTotal.find(u'|' + PageCourante)] + PagesCleTotal[PagesCleTotal.find(u'|' + PageCourante)+len(u'|' + PageCourante):len(PagesCleTotal)] + PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir|')+PageTempCle2.find(u'}}'):len(PageTempCle)]
								else:	# Cas du premier
									PageTempCle2 = PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir'):len(PageTempCle)]
									PageTempCle = PageTempCle[0:PageTempCle.find(u'{{voir|')+len(u'{{voir|')] + PagesCleTotal[len(PageCourante):len(PagesCleTotal)] + PageTempCle[PageTempCle.find(u'{{voir|')+len(u'{{voir')+PageTempCle2.find(u'}}'):len(PageTempCle)]
								if PageTempCle != PageTempCleBegin:
									if PageCourante == PageC:
										PageTemp = PageTempCle
									else:
										if debogage: print u'Première sauvegarde dédiée à {{voir}}'
										sauvegarde(PageCle,PageTempCle, summary)
							else:
								if PagesCleTotal.find(u'|' + PageCourante) != -1:
									PageTempCle = u'{{voir|' + PagesCleTotal[0:PagesCleTotal.find(u'|' + PageCourante)] + PagesCleTotal[PagesCleTotal.find(u'|' + PageCourante)+len(u'|' + PageCourante):len(PagesCleTotal)] + u'}}\n' + PageTempCle
								else:	# Cas du premier
									PageTempCle = u'{{voir' + PagesCleTotal[len(PageCourante):len(PagesCleTotal)] + u'}}\n' + PageTempCle
								if PageCourante == PageC:
									PageTemp = PageTempCle
								else:							
									sauvegarde(PageCle,PageTempCle, summary)
					
			elif PageTemp.find(u'{{voir|') != -1:
				if debogage: print u'  Identique à la page courante'
				PageTemp2 = PageTemp[PageTemp.find(u'{{voir|'):len(PageTemp)]
				if PageTemp2.find(u'|' + PageC + u'|') != -1 and PageTemp2.find(u'|' + PageC + u'|') < PageTemp2.find(u'}}'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageC + u'|')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageC + u'|')+len(u'|' + PageC):len(PageTemp)]
				if PageTemp2.find(u'|' + PageC + u'}') != -1 and PageTemp2.find(u'|' + PageC + u'}') < PageTemp2.find(u'}}'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageC + u'}')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageC + u'}')+len(u'|' + PageC):len(PageTemp)]
			
			'''pb dans [[i]]
			if debogage: print u' Retrait des {{voir| si {{voir/'
			while PageTemp.find(u'{{voir|') != -1 and PageTemp.find(u'{{voir/') != -1:
				PageTemp2 = PageTemp[PageTemp.find(u'{{voir|')+len(u'{{voir|'):]
				PageTemp = PageTemp[:PageTemp.find(u'{{voir|')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'}}')+2:]
			'''
			
			if debogage: print u' Nettoyage des {{voir}}...'
			if PageTemp.find(u'{{voir}}\n') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{voir}}\n')] + PageTemp[PageTemp.find(u'{{voir}}\n')+len(u'{{voir}}\n'):len(PageTemp)]
			if PageTemp.find(u'{{voir}}') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{voir}}')] + PageTemp[PageTemp.find(u'{{voir}}')+len(u'{{voir}}'):len(PageTemp)]
			PageTemp = HTMLUnicode.HTMLUnicode(PageTemp)
			PageTemp = PageTemp.replace(u'}}&#32;[[', u'}} [[')
			PageTemp = PageTemp.replace(u']]&#32;[[', u']] [[')
			regex = ur'\[\[([^\]]*)\|\1\]\]'
			if re.search(regex, PageTemp):
				if debogage: print u'Lien interne inutile'
				PageTemp = re.sub(regex, ur'[[\1]]', PageTemp)

			if PageTemp.find(u'{{vérifier création automatique}}') != -1:
				if debogage: print u' {{vérifier création automatique}} trouvé'
				PageTemp2 = PageTemp
				LanguesV = u'|'
				while PageTemp2.find(u'{{langue|') > 0:
					PageTemp2 = PageTemp2[PageTemp2.find(u'{{langue|')+len(u'{{langue|'):]
					LanguesV += u'|' + PageTemp2[:PageTemp2.find(u'}}')]
				if LanguesV != u'|':
					PageTemp = PageTemp.replace(u'{{vérifier création automatique}}', u'{{vérifier création automatique' + LanguesV + u'}}')
				#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
					
			# Clés de tri
			if debogage: print u'Clés de tri'
			PageTemp = PageTemp.replace(u'{{DEFAULTSORT:', u'{{clé de tri|')
			PageTemp = PageTemp.replace(u'{{CLEDETRI:', u'{{clé de tri|')
			PageTemp = PageTemp.replace(u'{{clef de tri|', u'{{clé de tri|')
			while PageTemp.find(u'\n{clé de tri') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'\n{clé de tri')+1] + u'{' + PageTemp[PageTemp.find(u'\n{clé de tri'):len(PageTemp)]
				
			ClePage = CleTri
			if PageTemp.find(u'{{clé de tri') == -1 and ClePage != u'' and ClePage.lower() != PageC.lower():
					summary = summary + u', {{clé de tri}} ajoutée'
					if PageTemp.rfind(u'\n\n[[') != -1:
						PageTemp2 = PageTemp[PageTemp.rfind(u'\n\n[['):len(PageTemp)]
						if PageTemp2[4:5] == u':' or PageTemp2[5:6] == u':':
							PageTemp = PageTemp[0:PageTemp.rfind(u'\n\n[[')] + u'\n\n{{clé de tri|' + ClePage + u'}}' + PageTemp[PageTemp.rfind(u'\n\n[['):len(PageTemp)]
						else:
							PageTemp = PageTemp + u'\n\n{{clé de tri|' + ClePage + u'}}\n'
					else:
						PageTemp = PageTemp + u'\n\n{{clé de tri|' + ClePage + u'}}\n'
								
			elif PageTemp.find(u'{{clé de tri|') != -1 and (PageTemp.find(u'{{langue|fr}}') != -1 or PageTemp.find(u'{{langue|eo}}') != -1 or PageTemp.find(u'{{langue|en}}') != -1 or PageTemp.find(u'{{langue|es}}') != -1 or PageTemp.find(u'{{langue|de}}') != -1 or PageTemp.find(u'{{langue|pt}}') != -1 or PageTemp.find(u'{{langue|it}}') != -1):
				if debogage: print u' vérification de clé existante pour alphabets connus'
				PageTemp2 = PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|'):len(PageTemp)]
				ClePage = PageTemp2[0:PageTemp2.find(u'}}')]
				'''if CleTri.lower() != ClePage.lower():
					summary = summary + u', {{clé de tri}} corrigée'
					PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')] + CleTri + PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')+PageTemp2.find(u'}}'):len(PageTemp)]'''
				'''pb ʻokina
					if CleTri.lower() == PageC.lower():
					summary = summary + u', {{clé de tri}} supprimée'
					PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|')] + PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')+PageTemp2.find(u'}}')+2:len(PageTemp)]'''
			if debogageLent: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
			
			baratin = u'{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
			if PageTemp.find(baratin) != -1:
				PageTemp = PageTemp[0:PageTemp.find(baratin)] + PageTemp[PageTemp.find(baratin)+len(baratin):len(PageTemp)]
				summary = summary + u', {{clé de tri|}} supprimée'
			baratin = u'{{clé de tri|}}<!-- Veuillez mettre juste après « {{clé de tri| » le titre de la page en y enlevant tous les accents et éventuels apostrophes, et en changeant les éventuels traits d’union et autres caractères spéciaux par une espace ; s’il n’y a rien à changer, merci d’effacer ces lignes. -->'
			'''Inhibé depuis migration Lua :
			if PageTemp.find(baratin) != -1:
				PageTemp = PageTemp[0:PageTemp.find(baratin)] + PageTemp[PageTemp.find(baratin)+len(baratin):len(PageTemp)]
				summary = summary + u', {{clé de tri|}} supprimée'
			if PageTemp.find(u'{{clé de tri|}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|}}')] + PageTemp[PageTemp.find(u'{{clé de tri|}}')+len(u'{{clé de tri|}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri|}} supprimée'
			if PageTemp.find(u'{{clé de tri}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri}}')] + PageTemp[PageTemp.find(u'{{clé de tri}}')+len(u'{{clé de tri}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri}} supprimée'
			if PageTemp.find(u'{{clé de tri|' + PageC.lower() + u'}}') != -1 and PageTemp.find(u'{{S|verb pronominal|fr}}') == -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|' + PageC.lower() + u'}}')] + PageTemp[PageTemp.find(u'{{clé de tri|' + PageC.lower() + u'}}')+len(u'{{clé de tri|' + PageC.lower() + u'}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri}} supprimée'''
			while PageTemp.find(u'{{S|verbe pronominal|') != -1:
				# Remplacement de modèle suite à vote
				PageTemp2 = PageTemp[PageTemp.find(u'{{S|verbe pronominal|'):]
				if PageTemp2.find(u'{{conj') != -1 and PageTemp2.find(u'{{pronominal|') == -1 and PageTemp2.find(u'{{pronl|') == -1 and PageTemp2.find(u'{{prnl|') == -1 and PageTemp2.find(u'{{réflexif|') == -1 and PageTemp2.find(u'{{réfléchi|') == -1 and PageTemp2.find(u'{{réfl|') == -1:
					PageTemp3 = PageTemp2[PageTemp2.find(u'{{conj'):]
					if PageTemp3.find(u'|prnl=') == -1 or PageTemp3.find(u'|prnl=') > PageTemp3.find(u'}}'):
						PageTemp = PageTemp[:PageTemp.find(u'{{S|verbe pronominal|')] + PageTemp2[:PageTemp2.find(u'{{conj')] + PageTemp3[:PageTemp3.find(u'}}')] + u'|prnl=1' + PageTemp3[PageTemp3.find(u'}}'):]
				PageTemp = PageTemp[:PageTemp.find(u'{{S|verbe pronominal|')] + u'{{S|verbe|' + PageTemp[PageTemp.find(u'{{S|verbe pronominal|')+len(u'{{S|verbe pronominal|'):]
			while PageTemp.find(u'\'\'(pronominal)\'\'') != -1:
				PageTemp2 = PageTemp[PageTemp.find(u'\'\'(pronominal)\'\''):]
				if PageTemp2.find(u'|prnl=1') != -1 and PageTemp2.find(u'|prnl=1') < PageTemp2.find(u'\n'):
					PageTemp = PageTemp[:PageTemp.find(u'\'\'(pronominal)\'\'')] + PageTemp[PageTemp.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]
				else:
					PageTemp = PageTemp[:PageTemp.find(u'\'\'(pronominal)\'\'')] + u'{{prnl}}' + PageTemp[PageTemp.find(u'\'\'(pronominal)\'\'')+ len(u'\'\'(pronominal)\'\''):]
			if debogage: print u'Remplacements des balises'
			PageTemp = re.sub(ur'\[\[Category:', ur'[[Catégorie:', PageTemp)
			while PageTemp.find(u'</br>') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'</br>')] + u'<br/>' + PageTemp[PageTemp.find(u'</br>')+len(u'</br>'):len(PageTemp)]
			while PageTemp.find(u'<sup/>') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'<sup/>')] + u'</sup>' + PageTemp[PageTemp.find(u'<sup/>')+len(u'<sup/>'):len(PageTemp)]
			
			if debogage: print u'Catégories de prononciation'
			if PageC[-2:] == u'um' and PageTemp.find(u'ɔm|fr}}') != -1:
				PageTemp = addCat(PageTemp, u'fr', u'um prononcés /ɔm/ en français')
			if PageC[:2] == u'qu':
				regex = ur'{{pron\|kw[^}\|]+\|fr}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'qu prononcés /kw/ en français')
			if PageC[:2] == u'qu':
				regex = ur'{{fr\-rég\|kw[^}\|]+}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'qu prononcés /kw/ en français')
			if PageC[:2] == u'ch':
				regex = ur'{{pron\|k[^}\|]+\|fr}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[:2] == u'ch':
				regex = ur'{{fr\-rég\|k[^}\|]+}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[:2] == u'Ch':
				regex = ur'{{pron\|k[^}\|]+\|fr}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[:2] == u'Ch':
				regex = ur'{{fr\-rég\|k[^}\|]+}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[-2:] == u'ch':
				regex = ur'{{pron\|[^}\|]+k\|fr}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[-2:] == u'ch':
				regex = ur'{{fr\-rég\|[^}\|]+k}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[-3:] == u'chs':
				regex = ur'{{pron\|[^}\|]+k}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			if PageC[-3:] == u'chs':
				regex = ur'{{fr\-rég\|[^}\|]+k}}'
				if re.search(regex, PageTemp):
					PageTemp = addCat(PageTemp, u'fr', u'ch prononcés /k/ en français')
			
		if debogage: print u'Remplacements des modèles'
		PageTemp = re.sub(ur'{{(formatnum|Formatnum|FORMATNUM)\:([0-9]*) ', ur'{{\1:\2', PageTemp)
		PageTemp = re.sub(ur'{{terme*\|Registre neutre}} *', ur'', PageTemp)
		# Ligne de forme
		PageTemp = PageTemp.replace(u'[[' + PageC + u']]', u'\'\'\'' + PageC + u'\'\'\'')
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

		PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n)\# *', ur"\1'''" + PageC + ur"''' {{pron}}\n# ", PageTemp)
		if PageTemp.find(u'{{Latn') == -1 and PageTemp.find(u'{{Grek') == -1 and PageTemp.find(u'{{Cyrl') == -1 and PageTemp.find(u'{{Armn') == -1 and PageTemp.find(u'{{Geor') == -1 and PageTemp.find(u'{{Hebr') == -1 and PageTemp.find(u'{{Arab') == -1 and PageTemp.find(u'{{Syrc') == -1 and PageTemp.find(u'{{Thaa') == -1 and PageTemp.find(u'{{Deva') == -1 and PageTemp.find(u'{{Hang') == -1 and PageTemp.find(u'{{Hira') == -1 and PageTemp.find(u'{{Kana') == -1 and PageTemp.find(u'{{Hrkt') == -1 and PageTemp.find(u'{{Hani') == -1 and PageTemp.find(u'{{Jpan') == -1 and PageTemp.find(u'{{Hans') == -1 and PageTemp.find(u'{{Hant') == -1 and PageTemp.find(u'{{zh-mot') == -1 and PageTemp.find(u'{{kohan') == -1 and PageTemp.find(u'{{ko-nom') == -1 and PageTemp.find(u'{{la-verb') == -1 and PageTemp.find(u'{{grc-verb') == -1 and PageTemp.find(u'{{polytonique') == -1 and PageTemp.find(u'FAchar') == -1:
			if debogage: print u'Ajout du mot vedette'
			PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n\{\{[^\n]*\n)\# *', ur"\1'''" + PageC + ur"''' {{pron}}\n# ", PageTemp)
		while PageTemp.find(u'\n {') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n {')+1] + PageTemp[PageTemp.find(u'\n {')+2:len(PageTemp)]		
		while re.compile('{{T\|.*\n\n\*[ ]*{{T\|').search(PageTemp):
			i1 = re.search(u'{{T\|.*\n\n\*[ ]*{{T\|',PageTemp).end()
			PageTemp = PageTemp[:i1][0:PageTemp[:i1].rfind(u'\n')-1] + PageTemp[:i1][PageTemp[:i1].rfind(u'\n'):len(PageTemp[:i1])] + PageTemp[i1:]
		while PageTemp.find(u'{{ucf|') != -1:
			PageTemp2 = PageTemp[PageTemp.find(u'{{ucf|')+len(u'{{ucf|'):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'{{ucf|')] + u'[[' + PageTemp2[0:PageTemp2.find(u'}}')] + u'|' + PageTemp2[0:1].upper() + PageTemp2[1:PageTemp2.find(u'}}')] + u']]' + PageTemp[PageTemp.find(u'{{ucf|')+len(u'{{ucf|')+PageTemp2.find(u'}}')+2:len(PageTemp)]
		while PageTemp.find(u'— {{source|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'— {{source|')] + PageTemp[PageTemp.find(u'— {{source|')+2:len(PageTemp)]
		while PageTemp.find(u'{{PAGENAME}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{PAGENAME}}')] + u'{{subst:PAGENAME}}' + PageTemp[PageTemp.find(u'{{PAGENAME}}')+len(u'{{PAGENAME}}'):len(PageTemp)]
			summary = summary + u', {{subst:PAGENAME}}'
		while PageTemp.find(u'Catégorie:Villes') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'Catégorie:Villes')] + u'Catégorie:Localités' + PageTemp[PageTemp.find(u'Catégorie:Villes')+len(u'Catégorie:Villes'):len(PageTemp)]
		while PageTemp.find(u'\n{{WP') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n{{WP')+1] + u'*' + PageTemp[PageTemp.find(u'\n{{WP')+1:len(PageTemp)]
		while PageTemp.find(u'{{S|verbes|en}}\nto \'\'\'') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|verbes|en}}\nto \'\'\'')+len(u'{{S|verbes|en}}\n')] + PageTemp[PageTemp.find(u'{{S|verbes|en}}\nto \'\'\'')+len(u'{{S|verbes|en}}\n')+3:len(PageTemp)]
		while PageTemp.find(u'{{S|verbes|en}}\n\'\'\'to ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|verbes|en}}\n\'\'\'to ')+len(u'{{S|verbes|en}}\n\'\'\'')] + PageTemp[PageTemp.find(u'{{S|verbes|en}}\n\'\'\'to ')+len(u'{{S|verbes|en}}\n\'\'\'to '):len(PageTemp)]
		while PageTemp.find(u'{{API|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{API|')] + u'{{pron|' + PageTemp[PageTemp.find(u'{{API|')+len(u'{{API|'):len(PageTemp)]
		while PageTemp.find(u'{{API}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{API}}')] + u'{{pron|}}' + PageTemp[PageTemp.find(u'{{API}}')+len(u'{{API}}'):len(PageTemp)]
		while PageTemp.find(u'\n* {{SAMPA}} : //') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n* {{SAMPA}} : //')] + PageTemp[PageTemp.find(u'\n* {{SAMPA}} : //')+len(u'\n* {{SAMPA}} : //'):len(PageTemp)]
		while PageTemp.find(u'\n* {{SAMPA}}: //') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n* {{SAMPA}}: //')] + PageTemp[PageTemp.find(u'\n* {{SAMPA}}: //')+len(u'\n* {{SAMPA}}: //'):len(PageTemp)]
		PageTemp = PageTemp.replace(u'\n* {{SAMPA}} :\n', u'\n')
		PageTemp = PageTemp.replace(u'{{Massorète}}:', u'{{Massorète}} :')
		PageTemp = PageTemp.replace(u'{{pron||hbo}}:', u'API :')
		PageTemp = PageTemp.replace(u'{{SAMPA}}:', u'{{SAMPA}} :')
		PageTemp = PageTemp.replace(u'{{sexua|', u'{{sexe|')
		PageTemp = PageTemp.replace(u'{{conj-hbo}}', u'{{conjugaison|hbo}}')
		PageTemp = PageTemp.replace(u'{{conj-fro}}', u'{{conjugaison|fro}}')
		PageTemp = PageTemp.replace(u'{{conj-frm}}', u'{{conjugaison|frm}}')
		PageTemp = PageTemp.replace(u'{{conj-fr}}', u'{{conjugaison|fr}}')
		PageTemp = PageTemp.replace(u'{{conj-en}}', u'{{conjugaison|en}}')
		PageTemp = PageTemp.replace(u'{{conj-es}}', u'{{conjugaison|es}}')
		PageTemp = PageTemp.replace(u'{{conj-de}}', u'{{conjugaison|de}}')
		PageTemp = PageTemp.replace(u'{{conj-it}}', u'{{conjugaison|it}}')
		PageTemp = PageTemp.replace(u'{{conj-pl}}', u'{{conjugaison|pl}}')
		PageTemp = PageTemp.replace(u'{{conj-ru}}', u'{{conjugaison|ru}}')
		PageTemp = PageTemp.replace(u'{|\n|}', u'')
		PageTemp = PageTemp.replace(u'{{auxiliaire être}}', u'{{note-auxiliaire|fr|être}}')
		PageTemp = PageTemp.replace(u'myt=scandinave', u'myt=nordique')
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
		PageTemp = PageTemp.replace(u'{{term|Antiquité grecque}}', u'{{antiquité|spéc=grecque}}')
		PageTemp = PageTemp.replace(u'{{term|Antiquité romaine}}', u'{{antiquité|spéc=romaine}}')
		PageTemp = PageTemp.replace(u'{{antiquité|fr}} {{terme|grecque}}', u'{{antiquité|spéc=grecque}}')
		PageTemp = PageTemp.replace(u'{{antiquité|fr}} {{terme|romaine}}', u'{{antiquité|spéc=romaine}}')
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
		PageTemp = PageTemp.replace(u'#*: {{trad-exe|fr}}', u'')
		PageTemp = PageTemp.replace(u'{{pron|}}', u'{{pron}}')
		PageTemp = PageTemp.replace(u'{{prononciation|}}', u'{{prononciation}}')
		PageTemp = PageTemp.replace(u'{{f}} {{fsing}}', u'{{f}}')
		PageTemp = PageTemp.replace(u'{{m}} {{msing}}', u'{{m}}')
		PageTemp = PageTemp.replace(u'{{vx|', u'{{vieilli|')
		
		# Modèle en doublon
		regex = ur"(\{\{départements\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur"\1", PageTemp)
		# Espace manquant
		regex = ur'(\{\{départements\|[^}]*\}\})([^ ]+)'
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur'\1 \2', PageTemp)
		
		regex = ur"(\{\{localités\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur"\1", PageTemp)
		# Espace manquant
		regex = ur'(\{\{localités\|[^}]*\}\})([^ ]+)'
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur'\1 \2', PageTemp)
		
		regex = ur"(\{\{provinces\|[^}]*\}\}) ?\{\{géographie\|[^}]*\}\}"
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur"\1", PageTemp)
		# Espace manquant
		regex = ur'(\{\{provinces\|[^}]*\}\})([^ ]+)'
		pattern = re.compile(regex)
		PageTemp = pattern.sub(ur'\1 \2', PageTemp)

		# Modèles trop courts
		if debogage: print u'Modèles courts'
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
		
		while PageTemp.find(u'[[Annexe:Couleurs en français]]') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'[[Annexe:Couleurs en français]]')] + u'{{Thésaurus|fr|couleur}}' + PageTemp[PageTemp.find(u'[[Annexe:Couleurs en français]]')+len(u'[[Annexe:Couleurs en français]]'):len(PageTemp)]
		while PageTemp.find(u'{{Annexe|Couleurs en français}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{Annexe|Couleurs en français}}')] + u'{{Thésaurus|fr|couleur}}' + PageTemp[PageTemp.find(u'{{Annexe|Couleurs en français}}')+len(u'{{Annexe|Couleurs en français}}'):len(PageTemp)]
		if PageTemp.find(u'{{S|nom scientifique|conv}}') != -1 and PageTemp.find(u'[[Catégorie:Noms scientifiques]]') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'[[Catégorie:Noms scientifiques]]')] + PageTemp[PageTemp.find(u'[[Catégorie:Noms scientifiques]]')+len(u'[[Catégorie:Noms scientifiques]]'):len(PageTemp)]
		
		while PageTemp.find(u'}}: //\n') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'}}: //\n')] + PageTemp[PageTemp.find(u'}}: //\n')+len(u'}}: //'):len(PageTemp)]
		
		while PageTemp.find(u'num=1|num=') != -1:
			if debogage: print u'retrait d\'un double num'
			PageTemp = PageTemp[:PageTemp.find(u'num=1|num=')] + PageTemp[PageTemp.find(u'num=1|num=')+len(u'num=1|'):]
		while PageTemp.find(u'{{figuré}} {{métaphore|fr}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{figuré}} {{métaphore|fr}}')] + u'{{figuré|fr}}' + PageTemp[PageTemp.find(u'{{figuré}} {{métaphore|fr}}')+len(u'{{figuré}} {{métaphore|fr}}'):len(PageTemp)]
		while PageTemp.find(u'{{figuré|fr}} {{métaphore|fr}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{figuré|fr}} {{métaphore|fr}}')] + u'{{figuré|fr}}' + PageTemp[PageTemp.find(u'{{figuré|fr}} {{métaphore|fr}}')+len(u'{{figuré|fr}} {{métaphore|fr}}'):len(PageTemp)]
		while PageTemp.find(u'{{Valence|ca}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{Valence|ca}}')] + u'{{valencien}}' + PageTemp[PageTemp.find(u'{{Valence|ca}}')+len(u'{{Valence|ca}}'):len(PageTemp)]
		while PageTemp.find(u'{{trad/zh') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{trad/zh')] + u'{{trad/défaut' + PageTemp[PageTemp.find(u'{{trad/zh')+len(u'{{trad/zh'):len(PageTemp)]
		while PageTemp.find(u'{{{{T|trad') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{{{T|trad')+2] + PageTemp[PageTemp.find(u'{{{{T|trad')+6:len(PageTemp)]
		while PageTemp.find(u'|type=du nom') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|type=du nom')] + PageTemp[PageTemp.find(u'|type=du nom')+len(u'|type=du nom'):len(PageTemp)]
		while PageTemp.find(u'{{boîte début') != -1:
			if PageTemp.find(u'{{boîte début|titre=') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{boîte début|titre=')+2] + u'(' + PageTemp[PageTemp.find(u'{{boîte début|titre=')+len(u'{{boîte début|titre='):len(PageTemp)]
			else:
				PageTemp = PageTemp[0:PageTemp.find(u'{{boîte début')+2] + u'(' + PageTemp[PageTemp.find(u'{{boîte début')+len(u'{{boîte début'):len(PageTemp)]
		while PageTemp.find(u'{{boîte milieu') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{boîte milieu')+2] + u'-' + PageTemp[PageTemp.find(u'{{boîte milieu')+len(u'{{boîte milieu'):len(PageTemp)]
		while PageTemp.find(u'{{boîte fin') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{boîte fin')+2] + u')' + PageTemp[PageTemp.find(u'{{boîte fin')+len(u'{{boîte fin'):len(PageTemp)]
		while PageTemp.find(u'{{boite début') != -1:
			if PageTemp.find(u'{{boite début|titre=') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{boite début|titre=')+2] + u'(' + PageTemp[PageTemp.find(u'{{boite début|titre=')+len(u'{{boite début|titre='):len(PageTemp)]
			else:
				PageTemp = PageTemp[0:PageTemp.find(u'{{boite début')+2] + u'(' + PageTemp[PageTemp.find(u'{{boite début')+len(u'{{boite début'):len(PageTemp)]
		while PageTemp.find(u'{{boite milieu') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{boite milieu')+2] + u'-' + PageTemp[PageTemp.find(u'{{boite milieu')+len(u'{{boite milieu'):len(PageTemp)]
		while PageTemp.find(u'{{boite fin') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{boite fin')+2] + u')' + PageTemp[PageTemp.find(u'{{boite fin')+len(u'{{boite fin'):len(PageTemp)]
		while PageTemp.find(u'\n{{-}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n{{-}}')] + PageTemp[PageTemp.find(u'\n{{-}}')+len(u'\n{{-}}'):len(PageTemp)]
		while PageTemp.find(u'{{-}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{-}}')] + PageTemp[PageTemp.find(u'{{-}}')+len(u'{{-}}'):len(PageTemp)]
		while PageTemp.find(u'\n{{trad-milieu}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n{{trad-milieu}}')] + PageTemp[PageTemp.find(u'\n{{trad-milieu}}')+len(u'\n{{trad-milieu}}'):len(PageTemp)]
		while PageTemp.find(u'|notat=1') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|notat=1')] + u'|nocat=1' + PageTemp[PageTemp.find(u'|notat=1')+len(u'|notat=1'):len(PageTemp)]

		regex = ur'\{\{ISBN\|([^\}\n]*)\}\}'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, ur'ISBN \1', PageTemp)

		# Modèles à déplacer
		if PageTemp.find(u'{{ru-conj') != -1:
			PageEnd = PageTemp[:PageTemp.find(u'{{ru-conj')]
			PageTemp = PageTemp[PageTemp.find(u'{{ru-conj'):]
			Annexe = PageTemp[:PageTemp.find(u'\n')+1]
			PageTemp = PageEnd + PageTemp[PageTemp.find(u'\n')+1:]
			PageEnd = u''
			pageAnnexe = Page(site,u'Annexe:Conjugaison en russe/'+PageC)
			if pageAnnexe.exists():
				try:
					AnnexeExistante = pageAnnexe.get()
				except wikipedia.NoPage:
					print "NoPage l 2230"
					return
				except wikipedia.IsRedirectPage: 
					print "IsRedirect l 2233"
					return
			else:
				AnnexeExistante = u''
			sauvegarde(pageAnnexe,AnnexeExistante+u'\n\n'+Annexe,u'Création à partir de l\'article')
		
		# Modèles de son. Ex : {{écoutez | {{audio | | {{sound -> {{écouter
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

		LimiteReg = 13
		ModRegion = range(1, LimiteReg)
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
		for m in range(1, LimiteReg-1):
			while PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|') != -1:
				PageTemp = PageTemp[:PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|')+len('{{écouter|')-1] + u'{{' + ModRegion[m] + u'|nocat=1}}' + PageTemp[PageTemp.find(u'{{écouter|' + ModRegion[m] + u'|')+len(u'{{écouter|' + ModRegion[m]):]

		while PageTemp.find(u'\n{{colonnes|') != -1:
			PageTemp2 = PageTemp[0:PageTemp.find(u'\n{{colonnes|')]
			if PageTemp2.rfind(u'{{') != -1 and PageTemp2.rfind(u'{{') == PageTemp2.rfind(u'{{trad-début'):	# modèles impriqués dans trad
				PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				if PageTemp2.find(u'\n}}\n') != -1:
					if PageTemp2[0:len(u'titre=')] == u'titre=':
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + u'}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				else:
					if debogage: print u'pb {{colonnes}} 1'
					break
			elif PageTemp2.rfind(u'{{') != -1 and PageTemp2.rfind(u'{{') == PageTemp2.rfind(u'{{('):	# modèles impriqués ailleurs
				PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				if PageTemp2.find(u'\n}}\n') != -1:
					if PageTemp2[0:len(u'titre=')] == u'titre=':
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + u'}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				else:
					if debogage: print u'pb {{colonnes}} 2'
					break
			elif PageTemp2.rfind(u'{{') != -1 and (PageTemp2.rfind(u'{{') == PageTemp2.rfind(u'{{trad-fin') or PageTemp2.rfind(u'{{') == PageTemp2.rfind(u'{{S|trad')):
				# modèle à utiliser dans {{S|trad
				PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				if PageTemp2.find(u'\n}}\n') != -1:
					if PageTemp2[0:len(u'titre=')] == u'titre=':
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + u'}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{trad-fin}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{trad-début}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				else:
					if debogage: print u'pb {{colonnes}} 3'
					break
			else:	# modèle ailleurs que {{S|trad
				PageTemp2 = PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				if PageTemp2.find(u'\n}}\n') != -1:
					if PageTemp2[0:len(u'titre=')] == u'titre=':
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(|' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|titre='):PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')] + u'}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'|')+1:len(PageTemp)]
					else:
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')] + u'\n{{)}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|')+PageTemp2.find(u'\n}}\n')+len(u'\n}}'):len(PageTemp)]
						PageTemp = PageTemp[0:PageTemp.find(u'\n{{colonnes|')] + u'\n{{(}}' + PageTemp[PageTemp.find(u'\n{{colonnes|')+len(u'\n{{colonnes|'):len(PageTemp)]
				else:
					if debogage: print u'pb {{colonnes}} 4'
					break
			while PageTemp.find(u'}}1=') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'}}1=')] + PageTemp[PageTemp.find(u'}}1=')+len(u'}}1='):len(PageTemp)]

		while PageTemp.find(u'\n #*') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n #*')+1] + PageTemp[PageTemp.find(u'\n #*')+2:len(PageTemp)]
		while PageTemp.find(u'\n #:') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n #:')+1] + PageTemp[PageTemp.find(u'\n #:')+2:len(PageTemp)]
		while PageTemp.find(u' }}') < PageTemp.find(u'}}') and PageTemp.find(u' }}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u' }}')] + PageTemp[PageTemp.find(u' }}')+1:len(PageTemp)]
		
		PageEnd = u''
		while PageTemp.find(u'&nbsp;') != -1:
			if debogage: print u'Espace insécable'
			PageEnd = PageEnd + PageTemp[:PageTemp.find(u'&nbsp;')]
			PageTemp = PageTemp[PageTemp.find(u'&nbsp;'):]
			if PageEnd.rfind(u'{{') == -1 or PageEnd.rfind(u'{{') < PageEnd.rfind(u'}}'):
				PageTemp = u' ' + PageTemp[len(u'&nbsp;'):]
			else:
				PageEnd = PageEnd + PageTemp[:len(u'&nbsp;')]
				PageTemp = PageTemp[len(u'&nbsp;'):]
		PageTemp = PageEnd + PageTemp	
		PageEnd = u''
		while PageTemp.find(u'\n#:') != -1:
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'\n#:')+2]
			if PageEnd.rfind(u'{{langue|') == PageEnd.rfind(u'{{langue|fr}}'):
				PageTemp = u'*' + PageTemp[PageTemp.find(u'\n#:')+len(u'\n#:'):len(PageTemp)]
			else:
				PageTemp = u':' + PageTemp[PageTemp.find(u'\n#:')+len(u'\n#:'):len(PageTemp)]
		PageTemp = PageEnd + PageTemp
		PageEnd = u''
		'''while PageTemp.find(u'#*') != -1 and PageTemp.find(u'#*') != PageTemp.find(u'#*\'\'') and PageTemp.find(u'#*') != PageTemp.find(u'#* \'\''):
			PageTemp = PageTemp[0:PageTemp.find(u'#*')+2] + u'\'\'' + PageTemp[PageTemp.find(u'#*')+2:len(PageTemp)]'''
		while PageTemp.find(u'\n# [[' + PageC + u'|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n# [[' + PageC + u'|')+len(u'\n# [[')] + u'#fr' + PageTemp[PageTemp.find(u'\n# [[' + PageC + u'|')+len(u'\n# [[' + PageC):len(PageTemp)]
		
		# Adverbes Daahbot
		if PageC[-4:] == 'ment':
			PageC2 = PageC[:-4]
			PageTemp = PageTemp.replace(u"''[["+PageC2+u"]]'', par son féminin ''[["+PageC2+u"]]'',", u"''[["+PageC2+u"]]'',")
		
		# Retrait des espaces intégrés au modèle
		while PageTemp.find(u'|pinv= ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|pinv= ')+len(u'|pinv=')] + PageTemp[PageTemp.find(u'|pinv= ')+len(u'|pinv= '):len(PageTemp)]
		while PageTemp.find(u'|pinv=. ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|pinv=. ')+len(u'|pinv=.')] + PageTemp[PageTemp.find(u'|pinv=. ')+len(u'|pinv=. '):len(PageTemp)]
		#while PageTemp.find(u'|pinv=&nbsp;') != -1:
		#	PageTemp = PageTemp[0:PageTemp.find(u'|pinv=&nbsp;')+len(u'|pinv=')] + PageTemp[PageTemp.find(u'|pinv=&nbsp;')+len(u'|pinv=&nbsp;'):len(PageTemp)]
		
		# Faux homophones : lemme et sa flexion
		if debogage: print u'Faux homophones'
		if PageTemp.find(u'|flexion}}') != -1 and PageC[len(PageC)-1:] == u's' and PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']],') == -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']]')+len(u'{{S|homophones}}\n*[[' + PageC[0:len(PageC)-1] + u']]')+1:len(PageTemp)]
		elif PageTemp.find(u'|flexion}}') != -1 and PageC[len(PageC)-1:] == u's' and PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']],') == -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']]')+len(u'{{S|homophones}}\n* [[' + PageC[0:len(PageC)-1] + u']]')+1:len(PageTemp)]
		
		# Ajout des redirections des pronominaux
		if PageTemp.find(u'{{S|verbe|fr}}') != -1 and PageC[:3] != u'se' and PageC[:2] != u's’':
			PageTemp2 = PageTemp[PageTemp.find(u'{{S|verbe|fr}}'):]
			regex = ur'(\n|\')s(e |’)\'\'\''
			if re.search(regex, PageTemp2) is not None:
				if re.search(regex, PageTemp2) < PageTemp2.find(u'{{S|') or PageTemp2.find(u'{{S|') == -1:
					regex = ur'^[aeiouyàéèêôù]'
					if re.search(regex, PageC):	# ne pas prendre [:1] car = & si encodage ASCII du paramètre DOS / Unix
						PageC2 = u's’'+PageC
					else:
						PageC2 = u'se '+PageC
					page2 = Page(site,PageC2)
					if not page2.exists():
						if debogage: print u'Création de ' + CleDeTri.CleDeTri(PageC2)
						summary2 = u'Création d\'une redirection provisoire catégorisante du pronominal'
						sauvegarde(page2, u'#REDIRECT[[' + PageC + u']]\n<!-- Redirection temporaire avant de créer le verbe pronominal -->\n[[Catégorie:Wiktionnaire:Verbes pronominaux à créer en français]]', summary2)
					
		# Ajout de modèles pour les gentités et leurs adjectifs
		if debogage: print u'Gentilés'
		if PageTemp.find(u'{{langue|fr}}') != -1:
			ligne = 6
			colonne = 4
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
			
			for l in range(1,ligne+1):
				regex = ur'\({{p}} : [\[\']*' + PageC + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + PageC + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageC + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, u'{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				regex = ur'\({{f}} : [\[\']*' + PageC + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + PageC + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageC + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, u'{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				# Son
				if debogageLent: print u' son'
				regex = ur'(\n\'\'\'' + PageC + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|[pron\=]*)}}'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'\n\4\2}}\1\2\3', PageTemp)
		
		elif PageTemp.find(u'{{langue|es}}') != -1:
			ligne = 1
			colonne = 4
			ModeleGent = [[0] * (colonne+1) for _ in range(ligne+1)]
			ModeleGent[1][1] = ur'es-accord-oa'
			ModeleGent[1][2] = ur'os'
			ModeleGent[1][3] = ur'a'
			ModeleGent[1][4] = ur'as'
			
			for l in range(1,ligne+1):
				regex = ur'\({{p}} : [\[\']*' + PageC[:-1] + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + PageC[:-1] + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageC[:-1] + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, u'{{' + ModeleGent[l][1] + u'|' + PageC[:-1] + ur'}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				regex = ur'\({{f}} : [\[\']*' + PageC[:-1] + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + PageC[:-1] + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageC[:-1] + ModeleGent[l][4] + ur'[\]\']*\)'
				if debogage: print regex.encode(config.console_encoding, 'replace')
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, u'{{' + ModeleGent[l][1] + u'|' + PageC[:-1] + ur'}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				# Son
				if debogage: print u' son'
				regex = ur'(\n\'\'\'' + PageC + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|' + PageC[:-1] + ur')}}'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'\n\4|\2}}\1\2\3', PageTemp)
					
		# URL de références : elles ne contiennent pas les diacritiques des {{PAGENAME}}
		if debogage: print u'Références'
		while PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=') != -1:
			PageTemp2 = PageTemp[PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')+len(u'[http://www.sil.org/iso639-3/documentation.asp?id='):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'[http://www.sil.org/iso639-3/documentation.asp?id=')] + u'{{R:SIL|' + PageTemp2[0:PageTemp2.find(u' ')] + u'}}' + PageTemp2[PageTemp2.find(u']')+1:len(PageTemp2)]
			summary = summary + u', ajout de {{R:SIL}}'
		while PageTemp.find(u'[http://www.cnrtl.fr/definition/') != -1:
			PageTemp2 = PageTemp[PageTemp.find(u'[http://www.cnrtl.fr/definition/')+len(u'[http://www.cnrtl.fr/definition/'):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'[http://www.cnrtl.fr/definition/')] + u'{{R:TLFi|' + PageTemp2[0:PageTemp2.find(u' ')] + u'}}' + PageTemp2[PageTemp2.find(u']')+1:len(PageTemp2)]
			summary = summary + u', ajout de {{R:TLFi}}'
		while PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/') != -1:
			PageTemp2 = PageTemp[PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/')+len(u'[http://www.mediadico.com/dictionnaire/definition/'):len(PageTemp)]
			PageTemp = PageTemp[0:PageTemp.find(u'[http://www.mediadico.com/dictionnaire/definition/')] + u'{{R:Mediadico|' + PageTemp2[0:PageTemp2.find(u'/1')] + u'}}' + PageTemp2[PageTemp2.find(u']')+1:len(PageTemp2)]
			summary = summary + u', ajout de {{R:Mediadico}}'
		while PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{R:DAF8}}\n{{Import:DAF8}}')+len(u'{{R:DAF8}}\n'):len(PageTemp)]
			summary = summary + u', doublon {{R:DAF8}}'
		while PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{R:DAF8}}\n\n{{Import:DAF8}}')+len(u'{{R:DAF8}}\n\n'):len(PageTemp)]
			summary = summary + u', doublon {{R:DAF8}}'
		while PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}')+len(u'{{Import:DAF8}}')] + PageTemp[PageTemp.find(u'{{Import:DAF8}}\n{{R:DAF8}}')+len(u'{{Import:DAF8}}\n{{R:DAF8}}'):len(PageTemp)]
			summary = summary + u', doublon {{R:DAF8}}'
		while PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}')] + PageTemp[PageTemp.find(u'{{R:Littré}}\n{{Import:Littré}}')+len(u'{{R:Littré}}\n'):len(PageTemp)]
			summary = summary + u', doublon {{R:Littré}}'
		while PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}')+len(u'{{Import:Littré}}')] + PageTemp[PageTemp.find(u'{{Import:Littré}}\n{{R:Littré}}')+len(u'{{Import:Littré}}\n{{R:Littré}}'):len(PageTemp)]
			summary = summary + u', doublon {{R:Littré}}'
		while PageTemp.find(u'\n{{R:') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n{{R:')+1] + u'*' + PageTemp[PageTemp.find(u'\n{{R:')+1:len(PageTemp)]
		while PageTemp.find(u'\n{{Import:') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n{{Import:')+1] + u'*' + PageTemp[PageTemp.find(u'\n{{Import:')+1:len(PageTemp)]
		
		# Détection d'une première traduction aux normes
		regex = u'\* ?{{[a-z][a-z][a-z]?\-?[a-z]?[a-z]?[a-z]?}} :'
		PageEnd = u''
		while PageTemp.find(u'{{trad-début')!=-1:
			PageEnd = PageEnd + PageTemp[:PageTemp.find(u'{{trad-début')]
			PageTemp = PageTemp[PageTemp.find(u'{{trad-début'):]
			PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')+1]
			PageTemp = PageTemp[PageTemp.find(u'\n')+1:]
			if re.search(regex, PageTemp):
				if re.search(regex, PageTemp).start() < PageTemp.find(u'{{'):
					if debogage: print u'Ajout d\'un modèle T'
					PageTemp = PageTemp[:PageTemp.find(u'{{')+2] + u'T|' + PageTemp[PageTemp.find(u'{{')+2:]
		PageTemp = PageEnd + PageTemp
		PageEnd = u''

		# Classement des traductions (et ajout des modèles T après le premier de la liste)
		if debogage: print u'Classement des traductions'
		while PageTemp.find(u'{{T|') != -1:
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{T|')]
			PageTemp = PageTemp[PageTemp.find(u'{{T|'):len(PageTemp)]
			
			# Ajout des T
			PageTemp2 = PageTemp[PageTemp.find(u'\n'):]
			if re.search(regex, PageTemp2):
				if re.search(regex, PageTemp2).start() < PageTemp2.find(u'{{'):
					if debogage: print u'Ajout d\'un modèle T'
					PageTemp = PageTemp[:PageTemp.find(u'\n')+PageTemp2.find(u'{{')+2] + u'T|' + PageTemp[PageTemp.find(u'\n')+PageTemp2.find(u'{{')+2:]
			
			
			# Rangement de la ligne de la traduction par ordre alphabétique de la langue dans PageEnd
			langue1 = PageTemp[PageTemp.find(u'{{T|')+4:PageTemp.find(u'}')]
			if langue1.find(u'|') != -1: langue1 = langue1[0:langue1.find(u'|')]
			#raw_input(PageEnd.encode(config.console_encoding, 'replace'))
			if langue1 != u'' and (PageEnd.find(u'<!--') == -1 or PageEnd.find(u'-->') != -1): # bug https://fr.wiktionary.org/w/index.php?title=Utilisateur:JackBot/test&diff=15092317&oldid=15090227
				#if PageEnd.find(u'<!--') != -1: raw_input(PageEnd[0:PageEnd.rfind(u'\n')].encode(config.console_encoding, 'replace'))
				if debogageLent: print u'Langue 1 : ' + langue1
				if len(langue1) > 3 and langue1.find(u'-') == -1:
					langue = langue1
				else:
					try:
						langue = CleDeTri.CleDeTri(langues.langues[langue1].decode("utf8"))
					except KeyError:
						if debogage: print "KeyError l 2111"
						break
					except UnboundLocalError:
						if debogage: print "UnboundLocalError l 2543"
						break
				langue2 = u'zzz'
				if PageEnd.rfind(u'\n') == -1 or PageTemp.find(u'\n') == -1: break
				TradCourante = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[0:PageTemp.find(u'\n')]
				TradSuivantes = u''
				PageEnd = PageEnd[0:PageEnd.rfind(u'\n')]
				PageTemp = PageTemp[PageTemp.find(u'\n'):len(PageTemp)]
				while PageEnd.rfind(u'{{') != PageEnd.rfind(u'{{S|traductions') and PageEnd.rfind(u'{{') != PageEnd.rfind(u'{{trad-début') and PageEnd.rfind(u'{{') != PageEnd.rfind(u'{{trad-fin') and PageEnd.rfind(u'{{') != PageEnd.rfind(u'{{S|traductions à trier') and langue2 > langue and PageEnd.rfind(u'{{T') != PageEnd.rfind(u'{{T|conv') and PageEnd.rfind(u'{{') != PageEnd.rfind(u'{{(') and (PageEnd.rfind(u'{{') > PageEnd.rfind(u'|nocat') or PageEnd.rfind(u'|nocat') == -1):
					langue2 = PageEnd[PageEnd.rfind(u'{{T|')+len(u'{{T|'):len(PageEnd)]
					langue2 = langue2[0:langue2.find(u'}}')]
					if langue2.find(u'|') != -1: langue2 = langue2[0:langue2.find(u'|')]
					if debogageLent: print u'Langue 2 : ' + langue2
					if len(langue2) > 3 and langue2.find(u'-') == -1:
						langue = langue2
					else:
						try:
							langue2 = CleDeTri.CleDeTri(langues.langues[langue2].decode("utf8"))
						except KeyError:
							if debogage: print "KeyError l 2160"
							break
					if langue2 != u'' and langue2 > langue:
						if debogage: langue2 + u' > ' + langue
						if PageEnd.rfind(u'\n') > PageEnd.rfind(u'trad-début'):
							TradSuivantes = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + TradSuivantes
							PageEnd = PageEnd[0:PageEnd.rfind(u'\n')]
							summary = summary + ', traduction ' + langue2 + u' > ' + langue
						elif PageEnd.rfind(u'\n') != -1:
							# Cas de la première de la liste
							TradCourante = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + TradCourante
							PageEnd = PageEnd[0:PageEnd.rfind(u'\n')]
						#print PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)].encode(config.console_encoding, 'replace')
					else:
						break
				PageEnd = PageEnd + TradCourante + TradSuivantes
			elif PageTemp.find(u'\n') != -1:
				if debogage: print u' Retrait de commentaire de traduction l 2357'
				PageEnd = PageEnd + PageTemp[:PageTemp.find(u'\n')]
				PageTemp = PageTemp[PageTemp.find(u'\n'):]
			else:
				PageEnd = PageEnd + PageTemp
				PageTemp = u''
			if debogageLent: print u'Ligne : ' + PageTemp[:PageTemp.find(u'\n')+1].encode(config.console_encoding, 'replace')
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'\n')+1]
			PageTemp = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
			#print(PageEnd.encode(config.console_encoding, 'replace'))
			#print(PageTemp.encode(config.console_encoding, 'replace'))'''
		PageTemp = PageEnd + PageTemp
		PageEnd = u''

		# Classement des sections modifiables
		"""PageEnd = u''
		while PageTemp.find(u'{{langue|') != -1:
			PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{langue|')+len(u'{{langue|')]
			PageTemp = PageTemp[PageTemp.find(u'{{langue|')+len(u'{{langue|'):len(PageTemp)]
			if PageTemp.find(u'{{langue|') != -1:
				# Rangement des paragraphes par ordre alphabétique de langue dans PageEnd
				langue1 = PageTemp[0:PageTemp.find(u'}')]
				if langue1.find(u'|') != -1: langue1 = langue1[0:langue1.find(u'|')]
				if langue1 != u'':
					#print(langue1) # ca pt
					Langue1 = Page(site,u'Modèle:' + langue1)
					try: PageTemp2 = Langue1.get()
					except wikipedia.NoPage:
						print "NoPage l 1521 : " + langue1
						return
					except wikipedia.IsRedirectPage:
						PageTemp2 = Langue1.getRedirectTarget().title() + u'<noinclude>'
					except wikipedia.ServerError:
						print "ServerError l 1527 : " + langue1
						return
					except wikipedia.BadTitle:
						print "BadTitle l 1530 : " + langue1
						return
					if PageTemp2.find(u'<noinclude>') != -1:
						langue = CleDeTri.CleDeTri(PageTemp2[0:PageTemp2.find(u'<noinclude>')])
						langue2 = u'zzz'
						if PageTemp.find(u'\n== {{langue|') != -1:
							ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[0:PageTemp.find(u'\n== {{langue|')]
							PageTemp = PageTemp[PageTemp.find(u'\n== {{langue|'):len(PageTemp)]
						elif PageTemp.find(u'\n=={{langue|') != -1:
							ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp[0:PageTemp.find(u'\n=={{langue|')]
							PageTemp = PageTemp[PageTemp.find(u'\n=={{langue|'):len(PageTemp)]
						else:
							ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + PageTemp
							PageTemp = u''
						PageEnd = PageEnd[0:PageEnd.rfind(u'\n')]
						ParagSuivants = u''
						#raw_input (ParagCourant.encode(config.console_encoding, 'replace'))
						# Comparaison du paragraphe courant avec le précédent, et rangement dans ParagSuivants de ce qui doit le suivre
						while PageEnd.rfind(u'{{langue|') != -1  and PageEnd.rfind(u'{{langue|') < PageEnd.rfind(u'}}')  and PageEnd.rfind(u'{{langue|') != PageEnd.rfind(u'{{langue|fr'):
							langue2 = PageEnd[PageEnd.rfind(u'{{langue|')+len(u'{{langue|'):len(PageEnd)]
							langue2 = langue2[0:langue2.find(u'}}')]
							if langue2.find(u'|') != -1: langue2 = langue2[0:langue2.find(u'|')]
							Langue2 = Page(site,u'Modèle:' + langue2)
							try: PageTemp3 = Langue2.get()
							except wikipedia.NoPage: 
								print "NoPage l 1607 : " + langue2
								return
							except wikipedia.ServerError: 
								print "ServerError l 1610 : " + langue2
								return
							except wikipedia.IsRedirectPage:
								print u'Redirection l 1613 : ' + langue2
								return
							except wikipedia.BadTitle:
								print u'BadTitle l 1616 : ' + langue2
								return
							if PageTemp3.find(u'<noinclude>') != -1:
								langue2 = CleDeTri.CleDeTri(PageTemp3[0:PageTemp3.find(u'<noinclude>')])
								print langue2 # espagnol catalan
								if langue2 > langue:
									summary = summary + ', section ' + langue2 + u' > ' + langue
									print langue2 + u' > ' + langue
									ParagSuivants = PageEnd[PageEnd.rfind(u'{{langue|'):len(PageEnd)] + ParagSuivants
									PageEnd = PageEnd[0:PageEnd.rfind(u'{{langue|')]
									ParagSuivants = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + ParagSuivants
								else:
									ParagCourant = PageEnd[PageEnd.rfind(u'{{langue|'):len(PageEnd)] + ParagCourant
									PageEnd = PageEnd[0:PageEnd.rfind(u'{{langue|')]
									ParagCourant = PageEnd[PageEnd.rfind(u'\n'):len(PageEnd)] + ParagCourant
									#raw_input (ParagCourant.encode(config.console_encoding, 'replace')) catalan, espagnol, portugais
								PageEnd = PageEnd[0:PageEnd.rfind(u'\n')]
							else: 
								print u'l 1629'
								return
						#raw_input (PageEnd.encode(config.console_encoding, 'replace'))
						PageEnd = PageEnd + ParagCourant + ParagSuivants
				else:
					print u'l 1634'
					return
				PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'{{langue|')]
				PageTemp = PageTemp[PageTemp.find(u'{{langue|'):len(PageTemp)]
				#raw_input (PageTemp.encode(config.console_encoding, 'replace'))
			else:
				PageEnd = PageEnd + PageTemp
				PageTemp = u''
			#print(PageEnd.encode(config.console_encoding, 'replace'))
			#print(PageTemp.encode(config.console_encoding, 'replace'))
		PageTemp = PageEnd + PageTemp
		PageEnd = u''"""
		
		if debogage: print u'Remplacements des anciens codes langue'
		while PageTemp.find(u'=prv=') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'=prv=')] + u'langue|oc' + PageTemp[PageTemp.find(u'=prv=')+len(u'=prv='):len(PageTemp)]
		AncienModele = []
		NouveauModele = []
		AncienModele.append(u'ko-hanja')
		NouveauModele.append(u'ko-Hani')
		AncienModele.append(u'be-x-old')
		NouveauModele.append(u'be-tarask')
		AncienModele.append(u'zh-min-nan')
		NouveauModele.append(u'nan')
		AncienModele.append(u'lsf')
		NouveauModele.append(u'fsl')
		AncienModele.append(u'arg')
		NouveauModele.append(u'an')
		AncienModele.append(u'nav')
		NouveauModele.append(u'nv')
		AncienModele.append(u'prv')
		NouveauModele.append(u'oc')
		AncienModele.append(u'nds-NL')
		NouveauModele.append(u'nds-nl')
		AncienModele.append(u'gsw-FR')
		NouveauModele.append(u'gsw-fr')
		AncienModele.append(u'zh-sc')
		NouveauModele.append(u'zh-Hans')
		AncienModele.append(u'roa-rup')
		NouveauModele.append(u'rup')
		for p in range(1,len(AncienModele)):
			while PageTemp.find(u'|' + AncienModele[p] + u'|') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'|' + AncienModele[p] + u'|')+1] + NouveauModele[p] + PageTemp[PageTemp.find(u'|' + AncienModele[p] + u'|')+len(u'|' + AncienModele[p] + u'|')-1:len(PageTemp)]
			while PageTemp.find(u'|' + AncienModele[p] + u'}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'|' + AncienModele[p] + u'}')+1] + NouveauModele[p] + PageTemp[PageTemp.find(u'|' + AncienModele[p] + u'}')+len(u'|' + AncienModele[p] + u'}')-1:len(PageTemp)]
			while PageTemp.find(u'{' + AncienModele[p] + u'|') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{' + AncienModele[p] + u'|')+1] + NouveauModele[p] + PageTemp[PageTemp.find(u'{' + AncienModele[p] + u'|')+len(u'{' + AncienModele[p] + u'|')-1:len(PageTemp)]
			while PageTemp.find(u'{' + AncienModele[p] + u'}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{' + AncienModele[p] + u'}')+1] + NouveauModele[p] + PageTemp[PageTemp.find(u'{' + AncienModele[p] + u'}')+len(u'{' + AncienModele[p] + u'}')-1:len(PageTemp)]
			while PageTemp.find(u'=' + AncienModele[p] + u'}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'=' + AncienModele[p] + u'}')+1] + NouveauModele[p] + PageTemp[PageTemp.find(u'=' + AncienModele[p] + u'}')+len(u'=' + AncienModele[p] + u'}')-1:len(PageTemp)]
		while PageTemp.find(u'{{WP|lang=sgs') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{WP|lang=sgs')] + u'{{WP|lang=bat-smg' + PageTemp[PageTemp.find(u'{{WP|lang=sgs')+len(u'{{WP|lang=sgs'):len(PageTemp)]
							
		# Ajouts des codes langues
		if debogage: print (u'Gestion des codes langues dans les modèles')
		EstCodeLangue = u'false'
		if debogage: print " EstCodeLangue = " + EstCodeLangue
		trad = u'false'
		codelangue = None
		if debogage: print u'codelangue = None'
		NouvelleLangue = False
		position = 1
		p = 1

		while position > -1:	# On sauvegarde la partie traitée d'une page provisoire dans une page finale jusqu'à disparition de la première
			if debogageLent: 
				print(PageEnd.encode(config.console_encoding, 'replace')[0:1000])
				raw_input(PageTemp.encode(config.console_encoding, 'replace')[0:1000])
			if debogageLent:
				if codelangue is None:
					print u'Boucle langue'
				else:
					print u'Boucle langue : ' + codelangue
			
			''' Eliminer les {{e}}...
			while PageTemp.find(u'}}') != -1 and PageTemp.find(u'}}') != PageTemp.find(u'}} ') and PageTemp.find(u'}}') != PageTemp.find(u'}}\n') and PageTemp.find(u'}}') != PageTemp.find(u'}}.'):
				PageTemp = PageTemp[0:PageTemp.find(u'}}')+2] + u' ' + PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
			while PageTemp.find(u'{{') != -1 and PageTemp.find(u'{{')-1 != PageTemp.find(u' {{') and PageTemp.find(u'{{')-1 != PageTemp.find(u'\n{{'):
				PageTemp = PageTemp[0:PageTemp.find(u'{{')] + u' ' + PageTemp[PageTemp.find(u'{{'):len(PageTemp)]
			# Fonctionne au clavier mais pas en .find ni avec &#171; &#187;, ni test = u'« ', ni &laquo;, ni test.encode : 
			#hexa /u... ?
			print (str(PageTemp.find(u'«')) + u' = ' + str(PageTemp.find(u'« ')))
			print (str(PageTemp.find(u'»')) + u' = ' + str(PageTemp.find(u' »')+1))
			#raw_input ("alors")
			if PageC != u'«' and PageTemp.find(u'«') != -1 and PageTemp.find(u'«') != PageTemp.find(u'« '):
				PageTemp = PageTemp[0:PageTemp.find(u'«')+1] + u' ' + PageTemp[PageTemp.find(u'«')+1:len(PageTemp)]
			if PageC != u'»' and PageTemp.find(u'»') != -1 and PageTemp.find(u'»')-1 != PageTemp.find(u' »'):
				PageTemp = PageTemp[0:PageTemp.find(u'»')] + u' ' + PageTemp[PageTemp.find(u'»'):len(PageTemp)]
			if PageTemp[PageTemp.find(u'«'):PageTemp.find(u'«')+1] != u' ':
				PageTemp = PageTemp[0:PageTemp.find(u'«')+1] + u' ' + PageTemp[PageTemp.find(u'«')+1:len(PageTemp)]
			if PageTemp[PageTemp.find(u'»')-1:PageTemp.find(u'»')] != u' ':
				PageTemp = PageTemp[0:PageTemp.find(u'»')] + u' ' + PageTemp[PageTemp.find(u'»'):len(PageTemp)]'''
			
			# Recherche de chaque modèle
			position = PageTemp.find(u'{{')
			if position < 0: break
			if position == PageTemp.find(u'{{caractère}}'):
				codelangue = u'conv'
				EstCodeLangue = u'false'
				if debogage: print " EstCodeLangue = " + EstCodeLangue
			elif position == PageTemp.find(u'{{langue|'):
				#print (PageEnd.encode(config.console_encoding, 'replace')[0:1000])
				#raw_input (PageTemp[0:position].encode(config.console_encoding, 'replace'))
				if debogage: print u'Nouveau code langue'
				PageTemp2 = PageTemp[position+len(u'{{langue|'):]
				if PageTemp2.find("}}") < PageTemp2.find("|") or PageTemp2.find("|") == -1:
					if PageTemp.find(u'{{langue|') < PageTemp.find(u'}}'):
						if debogage: print u' code langue simple'
						codelangue = PageTemp[PageTemp.find(u'{{langue|')+len(u'{{langue|'):PageTemp.find("}}")]
						EstCodeLangue = u'true'
						if debogage: print " EstCodeLangue = " + EstCodeLangue
					else:
						if debogage: print u' code langue après fin de modèle(s) (imbriqués)'
						PageTemp2 = PageTemp[PageTemp.find(u'{{langue|')+len(u'{{langue|'):]
						codelangue = PageTemp2[:PageTemp2.find(u'}}')]
						EstCodeLangue = u'true'
						if debogage: print " EstCodeLangue = " + EstCodeLangue
				else:
					if debogage: print u' code langue multi-paramètres'
					codelangue = PageTemp[PageTemp.find(u'{{langue|')+len(u'{{langue|'):PageTemp.find(u'{{langue|')+len(u'{{langue|')+PageTemp2.find("}}")]
					EstCodeLangue = u'true'
					if debogage: print " EstCodeLangue = " + EstCodeLangue
					position = PageTemp.find("{{")
				if debogage: print u' code langue trouvé : ' + codelangue
				if codelangue.find(u'=') != -1:
					PageEnd = u'{{formater|Code langue inexistant : ' + codelangue + u'}}\n' + PageBegin
					summary = u'Page à formater manuellement'
					sauvegarde(page, PageEnd, summary)
					return
				NouvelleLangue = True
					
			elif position == PageTemp.find(u'{{langue}}'):
				# Recherche d'un codelangue à préciser
				PageTemp2 = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
				PageTemp2 = PageTemp[PageTemp.find(u'{{')+2:len(PageTemp)]
				PageTemp2 = PageTemp[0:PageTemp.find(u'}}')]
				if PageTemp2.find("|") != -1:
					codelangue = PageTemp2[PageTemp2.find("|")+1:len(PageTemp2)]
					EstCodeLangue = u'true'
					if debogage: print " EstCodeLangue = " + EstCodeLangue
					PageTemp = PageTemp[0:PageTemp.find(u'{{langue}}')] + u'{{langue|' + codelangue + u'}}' + PageTemp[PageTemp.find(u'{{langue}}')+len(u'{{langue}}'):len(PageTemp)]
					position = PageTemp.find("{{")
			
			position = position + 2
			PageEnd = PageEnd + PageTemp[0:position]		# Transfert vers la page finale de l'article jusqu'au modèle en traitement exclu
			PageTemp = PageTemp[position:len(PageTemp)]
			
			# Fin du nom du modèle
			if PageTemp.find("|") > PageTemp.find("}}"):
				position = PageTemp.find("}}")
			elif PageTemp.find("|") == -1:
				position = PageTemp.find("}}")
			else:
				position = PageTemp.find("|")

			# Ajout des anagrammes pour cette nouvelle langue détectée
			if codelangue == u'conv':
				regex = ur'[= ]*{{S\|anagrammes}}[^}]+\|conv}}\n'
				if re.compile(regex).search(PageTemp):
					if debogage: print u'Retrait d\'anagramme en conv'
					PageEnd2 = PageTemp[:re.compile(regex).search(PageTemp).start()]
					PageTemp2 = PageTemp[re.compile(regex).search(PageTemp).end():]
					delta = re.compile(regex).search(PageTemp).end()
					regex = ur'[^}]+\|conv}}\n'
					while re.compile(regex).search(PageTemp2):
						if debogage: print u' autre anagramme en conv'
						delta = delta + re.compile(regex).search(PageTemp2).end()
						PageTemp2 = PageTemp2[re.compile(regex).search(PageTemp2).end():]
					PageTemp = PageEnd2 + PageTemp[delta:]
				
			elif NouvelleLangue == True and socket.gethostname() != "willow" and socket.gethostname() != "yarrow" and socket.gethostname() != "nightshade" and PageTemp.find(u'S|erreur|' + codelangue) == -1 and PageTemp.find(u'S|faute|' + codelangue) == -1  and codelangue != u'conv' and PageC[:1] != u'-' and PageC[-1:] != u'-': #and PageC != u'six':
				if debogage: print u' Anagrammes pour ' + codelangue
				if PageTemp.find(u'{{S|anagr') == -1 and PageC.find(u' ') == -1 and len(PageC) <= TailleAnagramme: 
					anagrammes = anagram(PageC)
					ListeAnagrammes = u''
					for anagramme in anagrammes:
						if anagramme != PageC:
							if debogage: print anagramme.encode(config.console_encoding, 'replace')
							pageAnagr = Page(site,anagramme)
							if pageAnagr.exists():
								if pageAnagr.namespace() !=0 and anagramme != u'Utilisateur:JackBot/test':
									break
								else:
									try:
										PageTempAnagr = pageAnagr.get()
									except wikipedia.NoPage: break
									except wikipedia.IsRedirectPage: break
								if PageTempAnagr.find(u'{{langue|' + codelangue + u'}}') != -1:
									ListeAnagrammes = ListeAnagrammes + u'* {{lien|' + anagramme + u'|' + codelangue + u'}}\n'
									if debogage: print u' trouvé'
					if ListeAnagrammes != u'':
						summary = summary + u', ajout d\'anagrammes ' + codelangue
						positionAnagr = PageTemp.find(u'{{langue|' + codelangue + u'}}')+len(u'{{langue|' + codelangue + u'}}')
						PageTemp2 = PageTemp[positionAnagr:len(PageTemp)]
						if PageTemp2.find(u'\n=== {{S|voir') != -1 and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'{{S|voir') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'\n=== {{S|voir')] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'\n=== {{S|voir'):len(PageTemp)]
						elif PageTemp2.find(u'\n=== {{S|références}}') != -1 and ((PageTemp2.find(u'{{langue|') != -1 and PageTemp2.find(u'\n=== {{S|références}}') < PageTemp2.find(u'{{langue|')) or PageTemp2.find(u'{{langue|') == -1):
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'\n=== {{S|références}}')] +  u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'\n=== {{S|références}}'):len(PageTemp)]
						elif PageTemp2.find(u'== {{langue|') != -1 and ((PageTemp2.find(u'[[Catégorie:') != -1 and PageTemp2.find(u'== {{langue|') < PageTemp2.find(u'[[Catégorie:')) or PageTemp2.find(u'[[Catégorie:') == -1):
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'== {{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'== {{langue|'):len(PageTemp)]
						elif PageTemp2.find(u'=={{langue|') != -1 and ((PageTemp2.find(u'[[Catégorie:') != -1 and PageTemp2.find(u'=={{langue|') < PageTemp2.find(u'[[Catégorie:')) or PageTemp2.find(u'[[Catégorie:') == -1):
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'=={{langue|')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'=={{langue|'):len(PageTemp)]								
						elif PageTemp2.find(u'{{clé de tri') != -1:
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'{{clé de tri')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'{{clé de tri'):len(PageTemp)]
						elif PageTemp2.find(u'[[Catégorie:') != -1:
							PageTemp = PageTemp[0:positionAnagr+PageTemp2.find(u'[[Catégorie:')] + u'=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[positionAnagr+PageTemp2.find(u'[[Catégorie:'):len(PageTemp)]
						else:
							if debogage: print " Ajout avant les interwikis"
							regex = ur'\n\[\[\w?\w?\w?:'
							if re.compile(regex).search(PageTemp):
								try:
									PageTemp = PageTemp[:re.search(regex,PageTemp).start()] + u'\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes + u'\n' + PageTemp[re.search(regex,PageTemp).start():]
								except:
									if debogage: print u'pb regex interwiki'
							else:
								PageTemp = PageTemp + u'\n\n=== {{S|anagrammes}} ===\n' + ListeAnagrammes
			
			PageTemp = PageTemp.replace(u'<!-- pas d’{{-anagr-}} -->\n', u'')
			PageTemp = PageTemp.replace(u'<!-- pas d’{{S|anagrammes}} -->\n', u'')
			PageTemp = PageTemp.replace(u'<!-- pas d’anagrammes -->\n', u'')
			PageTemp = PageTemp.replace(u'<!-- pas d’=== {{S|anagrammes}} ===\n-->', u'')
			PageTemp = PageTemp.replace(u'<!--pas d’=== {{S|anagrammes}} ===\n-->', u'')
			PageTemp = PageTemp.replace(u'<!-- pas d’=== {{S|anagrammes}} ===-->', u'')
			NouvelleLangue = False
		
			# Nettoyage des doublons (tester avec ophtalmologie dans adelphe)
			'''PageTemp2 = PageTemp[position+1:len(PageTemp)]
			if codelangue and PageTemp2.find(PageTemp[0:position]) != -1 and PageTemp2.find(u'\n') != -1 and PageTemp2.find(u' {{' + PageTemp[0:position] + u'|' + codelangue + u'}}') < PageTemp2.find(u'\n'):
				PageTemp = PageTemp[0:position+1+PageTemp2.find(u' {{' + PageTemp[0:position] + u'|' + codelangue + u'}}')] + PageTemp[position+1+PageTemp2.find(u' {{' + PageTemp[0:position] + u'|' + codelangue + u'}}')+len(u' {{' + PageTemp[0:position] + u'|' + codelangue + u'}}'):len(PageTemp)]
			elif PageTemp2.find(PageTemp[0:position]) != -1 and PageTemp2.find(u'\n') != -1 and PageTemp2.find(u' {{' + PageTemp[0:position] + u'}}') < PageTemp2.find(u'\n'):
				PageTemp = PageTemp[0:position+1+PageTemp2.find(u' {{' + PageTemp[0:position] + u'}}')] + PageTemp[0:position+1+PageTemp2.find(u' {{' + PageTemp[0:position] + u'}}')+len(u' {{' + PageTemp[0:position] + u'}}'):len(PageTemp)]
			'''
			#print (PageEnd.encode(config.console_encoding, 'replace')[0:1000])
			#print (PageTemp[0:position].encode(config.console_encoding, 'replace'))

			# Comparaison avec chaque modèle connu dans Modele[p], pour identifier le traitement à effectuer
			# à faire : S + -flex-* + -loc-*
			for p in range(0,limit6):
				if Modele[p] == PageTemp[:position]:
					if debogage: print (Modele[p].encode(config.console_encoding, 'replace'))
					# Modèles imbriqués (à sauter)
					'''while PageTemp.find(u'{{') < PageTemp.find(u'}}') and PageTemp.find(u'{{') != -1 and PageTemp.find(u'}}') != -1:
						if debogage:
							print u'Modèle inclu dans '
							print PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
						PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
						# Fin du nom du modèle
						if PageTemp.find("|") > PageTemp.find("}}") or PageTemp.find("|") == -1:
							position = PageTemp.find("}}")
						else:
							position = PageTemp.find("|")
						if position == -1:
							if debogage: print u'Erreur ligne 2271 : modèle brisé'
							return
					PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
					PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
					#break	# pb https://fr.wiktionary.org/w/index.php?title=ordre&curid=343&diff=14727763&oldid=14725107'''
						
					# Si on est dans un modèle spécial, le traiter, sinon par catégorie de génériques
					if not codelangue and (p < limit1 or p >= limit3) and Modele[p] != u'ébauche':
						if debogage: print PageTemp.encode(config.console_encoding, 'replace')
						#if debogage: raw_input(PageEnd.encode(config.console_encoding, 'replace'))
						PageEnd = u'{{formater|Section de langue manquante avant le modèle ' + Modele[p] + u' (au niveau du ' + str(len(PageEnd)) + u'-ème caractère)}}\n' + PageBegin
						summary = u'Page à formater manuellement'
						sauvegarde(page, PageEnd, summary)
						return

					if Modele[p] == u'term' or Modele[p] == u'terme' or Modele[p] == u'term_lien' or Modele[p] == u'régio' or Modele[p] == u'région':
						ModeleT = PageTemp[PageTemp.find("|")+1:PageTemp.find("}}")]
						for p2 in range(1,limit6):
							if Modele[p2] == ModeleT or Modele[p2] == ModeleT[:1].lower() + ModeleT[1:] or u'génie ' + Modele[p2] == ModeleT or u'Génie ' + Modele[p2] == ModeleT:
								if p2 >= limit25 and p2 < limit3:
									PageEnd = PageEnd + Modele[p2] + "}}"
								elif p2 >= limit3:
									if EstCodeLangue == "false":
										PageEnd = PageEnd + Modele[p2] + "|nocat=1}}"
									else:
										PageEnd = PageEnd + Modele[p2] + "|" + codelangue + "}}"
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break							
						break
					elif Modele[p] == u'pron' or Modele[p] == u'phon' or Modele[p] == u'dénominal de' or Modele[p] == u'déverbal de' or Modele[p] == u'déverbal' or Modele[p] == u'superlatif de' or Modele[p] == u'comparatif de' or Modele[p] == u'déverbal sans suffixe' or Modele[p] == u'abréviation de':
						if codelangue != u'conv':
							# Tri des lettres de l'API
							if Modele[p] == u'pron':
								PageTemp2 = PageTemp[position+1:PageTemp.find("}}")]
								while PageTemp2.find(u'\'') != -1 and PageTemp2.find(u'\'') < PageTemp2.find(u'}}') and (PageTemp2.find(u'\'') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u'\'')] + u'ˈ' + PageTemp[PageTemp.find(u'\'')+1:len(PageTemp)]
								while PageTemp2.find(u'ˈˈˈ') != -1 and PageTemp2.find(u'ˈˈˈ') < PageTemp2.find(u'}}') and (PageTemp2.find(u'ˈˈˈ') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u'ˈˈˈ')] + u'\'\'\'' + PageTemp[PageTemp.find(u'ˈˈˈ')+3:len(PageTemp)]	
								while PageTemp2.find(u'ε') != -1 and PageTemp2.find(u'ε') < PageTemp2.find(u'}}') and (PageTemp2.find(u'ε') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u'ε')] + u'ɛ' + PageTemp[PageTemp.find(u'ε')+1:len(PageTemp)]
								while PageTemp2.find(u'ε̃') != -1 and PageTemp2.find(u'ε̃') < PageTemp2.find(u'}}') and (PageTemp2.find(u'ε̃') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u'ε̃')] + u'ɛ̃' + PageTemp[PageTemp.find(u'ε̃')+1:len(PageTemp)]
								while PageTemp2.find(u':') != -1 and PageTemp2.find(u':') < PageTemp2.find(u'}}') and (PageTemp2.find(u':') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u':')] + u'ː' + PageTemp[PageTemp.find(u':')+1:len(PageTemp)]
								while PageTemp2.find(u'g') != -1 and PageTemp2.find(u'g') < PageTemp2.find(u'}}') and (PageTemp2.find(u'g') < PageTemp2.find(u'|') or PageTemp2.find(u'|') == -1): PageTemp = PageTemp[0:PageTemp.find(u'g')] + u'ɡ' + PageTemp[PageTemp.find(u'g')+1:len(PageTemp)]
								#if codelangue == u'es': β/, /ð/ et /ɣ/ au lieu de de /b/, /d/ et /ɡ/
							if PageTemp[0:8] == u'pron||}}':
								PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")] + codelangue + "}}"
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
							elif PageTemp[position:position+3] == u'|}}' or PageTemp[position:position+4] == u'| }}':
								PageEnd = PageEnd + PageTemp[0:position] + "||" + codelangue + "}}"
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
							elif (PageTemp.find("lang=") != -1 and PageTemp.find("lang=") < PageTemp.find("}}")):
								PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")+2]
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
							elif position == PageTemp.find(u'|'):
								PageTemp2 = PageTemp[position+1:PageTemp.find("}}")]
								if PageTemp2.find(u'|') == -1:
									PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")] + "|" + codelangue + "}}"
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								else:
									PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
							elif position == PageTemp.find("}}"):
								PageEnd = PageEnd + PageTemp[0:position] + "||" + codelangue + "}}"
								PageTemp = PageTemp[position+2:len(PageTemp)]
								break
							else:
								PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")] + "|" + codelangue + "}}"
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
						else:
							PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
							PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
							break
					
					elif Modele[p] == u'écouter':
						#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
						PageTemp2 = PageTemp[position+1:len(PageTemp)]
						
						# Saut des modèles régionnaux
						if PageTemp2.find("lang=") == -1 or PageTemp2.find("lang=") > PageTemp2.find("}}"):
							while PageTemp2.find(u'{{') < PageTemp2.find(u'}}') and PageTemp2.find(u'{{') != -1:
								PageTemp2 = PageTemp2[PageTemp2.find(u'}}')+2:]
							if PageTemp2.find("lang=") == -1 or PageTemp2.find("lang=") > PageTemp2.find("}}"):
								PageEnd = PageEnd + PageTemp[:position] + u'|lang=' + codelangue + PageTemp[position:PageTemp.find("}}")+2]
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
						PageEnd = PageEnd + PageTemp[:PageTemp.find("}}")+2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
								
					#elif Modele[p] == u'fr-rég' or Modele[p] == u'fr-inv': synchro de la pronociation avec {{pron|
					
					elif Modele[p] == u'm' or Modele[p] == u'f':
						if trad == u'true' or (codelangue != u'en' and codelangue != u'zh' and codelangue != u'ja' and codelangue != u'ko'):
							PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")+2]
						else:
							PageEnd = PageEnd[0:len(PageEnd)-2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'mf' or Modele[p] == u'mf?':
						if trad == u'true' or (codelangue != u'en' and codelangue != u'zh' and codelangue != u'ja' and codelangue != u'ko'):
							PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")+2]
						else:
							PageEnd = PageEnd[0:len(PageEnd)-2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'n' or Modele[p] == u'c':
						if trad == u'true' or (codelangue != u'en' and codelangue != u'zh' and codelangue != u'ja' and codelangue != u'ko' and codelangue != u'fr'):
							PageEnd = PageEnd + Modele[p] + u'}}'
						else:
							PageEnd = PageEnd[0:len(PageEnd)-2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'aphérèse' or Modele[p] == u'apocope' or Modele[p] == u'apocope familière' or Modele[p] == u'mot-valise' or Modele[p] == u'contraction' or Modele[p] == u'contr' or (
						Modele[p] == u'ellipse') or Modele[p] == u'par ellipse' or Modele[p] == u'abréviation' or Modele[p] == u'abrév' or Modele[p] == u'métonymie' or (
						Modele[p] == u'méton') or Modele[p] == u'antonomase':
						if (EstCodeLangue == u'false') and PageEnd.rfind(u'{{S|') != PageEnd.rfind(u'{{S|étymologie}}'):
							# Les modèles d'étymologie sont les seuls à devoir contenir des codes langues dans ce paragraphe
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
							break
						if position == PageTemp.find("|"): # S'il y a déjà un paramètre
							PageTemp2 = PageTemp[PageTemp.find("|")+1:len(PageTemp)]
							if (PageTemp2.find("m=") > PageTemp2.find("|")) and (PageTemp2.find("m=") < PageTemp2.find("}}")): # Si PageTemp2 = ...|m=1...}}...
								PageEnd = PageEnd + Modele[p] + u'|' + codelangue + u'|m=1}}'
							elif (PageTemp2.find("m=") >= 0) and (PageTemp2.find("m=") < PageTemp2.find("}}")): # Si PageTemp2 = m=1...}}...
								PageEnd = PageEnd + PageTemp[0:position] + u'|m=1|' + codelangue + u'}}'
							elif (PageTemp2.find(u'déf=') > PageTemp2.find("|")) and (PageTemp2.find(u'déf=') < PageTemp2.find("}}")):
								PageEnd = PageEnd + Modele[p] + u'|' + codelangue + u'|déf=oui}}'
							elif (PageTemp2.find(u'déf=') >= 0) and (PageTemp2.find(u'déf=') < PageTemp2.find("}}")):
								PageEnd = PageEnd + PageTemp[0:position] + u'|déf=oui|' + codelangue + u'}}'
							else:
								PageEnd = PageEnd + Modele[p] + u'|' + codelangue + u'}}'
						else:
							PageEnd = PageEnd + PageTemp[0:PageTemp.find("}}")] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'conjugaison' or Modele[p] == u'conj' or Modele[p] == u'1ergroupe' or Modele[p] == u'2egroupe' or Modele[p] == u'3egroupe':	# Modèle à deux paramètres
						if Modele[p] == u'1ergroupe':
							PageTemp = u'|grp=1' + PageTemp[len(u'1ergroupe'):len(PageTemp)]
							PageEnd = PageEnd + u'conj'
						elif Modele[p] == u'2egroupe':
							PageTemp = u'|grp=2' + PageTemp[len(u'2egroupe'):len(PageTemp)]
							PageEnd = PageEnd + u'conj'
						elif Modele[p] == u'3egroupe':
							PageTemp = u'|grp=3' + PageTemp[len(u'3egroupe'):len(PageTemp)]
							PageEnd = PageEnd + u'conj'
						elif Modele[p] == u'conjugaison':
							PageTemp = PageTemp[len(u'conjugaison'):len(PageTemp)]
							PageEnd = PageEnd + u'conjugaison'
						elif Modele[p] == u'conj':
							PageTemp = PageTemp[len(u'conj'):len(PageTemp)]
							PageEnd = PageEnd + u'conj'
						# Vérification des groupes en espagnol, portugais et italien
						if codelangue == u'es':
							if PageC[len(PageC)-2:] == u'ar' or PageC[len(PageC)-4:] == u'arsi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=1' + PageTemp
							elif PageC[len(PageC)-2:] == u'er' or PageC[len(PageC)-4:] == u'ersi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=2' + PageTemp
							elif PageC[len(PageC)-2:] == u'ir' or PageC[len(PageC)-4:] == u'irsi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=3' + PageTemp

						elif codelangue == u'pt':
							if PageC[len(PageC)-2:] == u'ar' or PageC[len(PageC)-4:] == u'ar-se':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=1' + PageTemp
							elif PageC[len(PageC)-2:] == u'er' or PageC[len(PageC)-4:] == u'er-se':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=2' + PageTemp
							elif PageC[len(PageC)-2:] == u'ir' or PageC[len(PageC)-4:] == u'ir-se':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=3' + PageTemp

						elif codelangue == u'it':
							if PageC[len(PageC)-3:] == u'are' or PageC[len(PageC)-4:] == u'arsi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'1' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'1' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=1' + PageTemp
							elif PageC[len(PageC)-3:] == u'ere' or PageC[len(PageC)-4:] == u'ersi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'2' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'2' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=2' + PageTemp
							elif PageC[len(PageC)-3:] == u'ire' or PageC[len(PageC)-4:] == u'irsi':
								if (PageTemp.find(u'grp=') != -1 and PageTemp.find(u'grp=') < PageTemp.find("}}")):
									if PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=}') or PageTemp.find(u'|grp=') == PageTemp.find(u'|grp=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|grp=')+len(u'|grp=')] + u'3' + PageTemp[PageTemp.find(u'|grp=')+len(u'|grp=')+1:len(PageTemp)]
								elif (PageTemp.find(u'groupe=') != -1 and PageTemp.find(u'groupe=') < PageTemp.find("}}")):
									if PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=}') or PageTemp.find(u'|groupe=') == PageTemp.find(u'|groupe=|'):
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe='):len(PageTemp)]
									else:
										PageTemp = PageTemp[0:PageTemp.find(u'|groupe=')+len(u'|groupe=')] + u'3' + PageTemp[PageTemp.find(u'|groupe=')+len(u'|groupe=')+1:len(PageTemp)]
								else:
									PageTemp = u'|groupe=3' + PageTemp

						if (PageTemp.find(codelangue) != -1 and PageTemp.find(codelangue) < PageTemp.find("}}")) or codelangue == u'fr':
							PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							if PageTemp.find(u'|nocat=1') != -1:
								PageTemp = PageTemp[0:PageTemp.find(u'|nocat=1')] + PageTemp[PageTemp.find(u'|nocat=1')+len(u'|nocat=1'):len(PageTemp)]
							PageTemp = u'|' + codelangue + PageTemp
						break
					
					
					elif Modele[p] == u'note-gentilé':
						# Trois paramètres possibles
						PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					
					elif Modele[p] == u'mythologie' or Modele[p] == u'mythol' or Modele[p] == u'myth' or Modele[p] == u'fantastique' or Modele[p] == u'fanta':	# Modèle à deux paramètres
						param = u''
						if (PageTemp.find(u'myt=') != -1 and PageTemp.find(u'myt=') < PageTemp.find("}}")):
							param = u'myt='
						elif (PageTemp.find(u'spéc=') != -1 and PageTemp.find(u'spéc=') < PageTemp.find("}}")):
							param = u'spéc='
						elif (PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find("}}")):
							PageTemp2 = PageTemp[PageTemp.find(u'|')+1:]
							if (PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find("}}")):
								# Présence d'un {{{2}}}, à ne pas retirer
								PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
						if param != u'':
							if PageTemp.find(param) > position+1: # myt= est après le code langue
								if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Animaux imaginaires'
	) != -1 and (PageTemp.find(u':Catégorie:Animaux imaginaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Animaux imaginaires') + 1 != PageTemp.rfind(u'Catégorie:Animaux imaginaires'))

	) or (PageTemp.find(u'Catégorie:Plantes imaginaires'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes imaginaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes imaginaires') + 1 != PageTemp.rfind(u'Catégorie:Plantes imaginaires'))

	) or (PageTemp.find(u'Catégorie:Créatures'
	) != -1 and (PageTemp.find(u':Catégorie:Créatures') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Créatures') + 1 != PageTemp.rfind(u'Catégorie:Créatures'))
	
	) or (PageTemp.find(u'Catégorie:Divinités'
	) != -1 and (PageTemp.find(u':Catégorie:Divinités') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Divinités') + 1 != PageTemp.rfind(u'Catégorie:Divinités'))):
									PageEnd = PageEnd + Modele[p] + u'|nocat=1|' + PageTemp[PageTemp.find(param):PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
								else:
									PageEnd = PageEnd + Modele[p] + u'|' + codelangue + PageTemp[PageTemp.find(param)-1:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
							else: # myt= est avant un éventuel code langue
								PageTemp2 = PageTemp[position+1:len(PageTemp)]
								if (PageTemp2.find(u'|') != -1) and (PageTemp2.find(u'|') < PageTemp2.find(u'}}')): # il y a un code langue
									if EstCodeLangue == "false":
										if debogage: print u' retrait du code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|nocat=1}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')] + u'|nocat=1}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
									else:
										if debogage: print u' avec code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|' + codelangue + u'}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+2] + codelangue + u'}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
								else: # Pas de code langue
									PageEnd = PageEnd + PageTemp[0:position+1+PageTemp2.find(u'}}')] + u'|' + codelangue + u'}}'
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Animaux imaginaires'
	) != -1 and (PageTemp.find(u':Catégorie:Animaux imaginaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Animaux imaginaires') + 1 != PageTemp.rfind(u'Catégorie:Animaux imaginaires'))

	) or (PageTemp.find(u'Catégorie:Plantes imaginaires'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes imaginaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes imaginaires') + 1 != PageTemp.rfind(u'Catégorie:Plantes imaginaires'))

	) or (PageTemp.find(u'Catégorie:Divinités'
	) != -1 and (PageTemp.find(u':Catégorie:Divinités') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Divinités') + 1 != PageTemp.rfind(u'Catégorie:Divinités'))): # Pas de myt= ni de langue
							PageEnd = PageEnd + PageTemp[0:position] + u'|nocat=1}}'
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break

					elif Modele[p] == u'religion' or Modele[p] == u'reli':	# Modèle à deux paramètres
						param = u''
						if (PageTemp.find("rel=") != -1 and PageTemp.find("rel=") < PageTemp.find("}}")):
							param = u'rel='
						elif (PageTemp.find(u'spéc=') != -1 and PageTemp.find(u'spéc=') < PageTemp.find("}}")):
							param = u'spéc='
						elif (PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find("}}")):
							PageTemp2 = PageTemp[PageTemp.find(u'|')+1:]
							if (PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find("}}")):
								# Présence d'un {{{2}}}, à ne pas retirer
								PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
						if param != u'':
							if PageTemp.find(param) > position+1: # rel= est après le code langue
								if (EstCodeLangue == "false"
								
	) or (PageTemp.find(u'Catégorie:Édifices religieux'
	) != -1 and (PageTemp.find(u':Catégorie:Édifices religieux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Édifices religieux') + 1 != PageTemp.rfind(u'Catégorie:Édifices religieux'))
	
	) or (PageTemp.find(u'Catégorie:Divinités'
	) != -1 and (PageTemp.find(u':Catégorie:Divinités') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Divinités') + 1 != PageTemp.rfind(u'Catégorie:Divinités'))):
									PageEnd = PageEnd + Modele[p] + u'|nocat=1|' + PageTemp[PageTemp.find(param):PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
								else:
									PageEnd = PageEnd + Modele[p] + u'|' + codelangue + PageTemp[PageTemp.find(param)-1:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
							else: # rel= est avant un éventuel code langue
								PageTemp2 = PageTemp[position+1:len(PageTemp)]
								if (PageTemp2.find(u'|') != -1) and (PageTemp2.find(u'|') < PageTemp2.find(u'}}')): # il y a un code langue
									if EstCodeLangue == "false":
										if debogage: print u' retrait du code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|nocat=1}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+1] + u'|nocat=1}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
									else:
										if debogage: print u' avec code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|' + codelangue + u'}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+2] + codelangue + u'}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
								else: # Pas de code langue
									PageEnd = PageEnd + PageTemp[:position+1+PageTemp2.find(u'}}')] + u'|' + codelangue + u'}}'
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Divinités'
	) != -1 and (PageTemp.find(u':Catégorie:Divinités') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Divinités') + 1 != PageTemp.rfind(u'Catégorie:Divinités'))): # Pas de rel= ni de langue
							PageEnd = PageEnd + PageTemp[0:position] + u'|nocat=1}}'
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break

					elif Modele[p] == u'sport':
						if (PageTemp.find(u'sport=') != -1 and PageTemp.find(u'sport=') < PageTemp.find("}}")):
							if PageTemp.find(u'sport=') > position+1: # sport= est après le code langue
								if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Sports'
	) != -1 and (PageTemp.find(u':Catégorie:Sports') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Sports') + 1 != PageTemp.rfind(u'Catégorie:Sports'))):
									PageEnd = PageEnd + Modele[p] + u'|nocat=1|' + PageTemp[PageTemp.find(u'sport='):PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
								else:
									PageEnd = PageEnd + Modele[p] + u'|' + codelangue + PageTemp[PageTemp.find(u'sport=')-1:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
							else: # sport= est avant un éventuel code langue
								PageTemp2 = PageTemp[position+1:len(PageTemp)]
								if (PageTemp2.find(u'|') != -1) or (PageTemp2.find(u'|') < PageTemp2.find(u'}}')): # il y a un code langue
									if EstCodeLangue == "false":
										if debogage: print u' retrait du code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|nocat=1}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+1] + u'|nocat=1}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
									else:
										if debogage: print u' avec code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|' + codelangue + u'}}'
										else:
											PageEnd = PageEnd + PageTemp[0:position+PageTemp2.find(u'|')+2] + codelangue + u'}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
								else: # Pas de code langue
									PageEnd = PageEnd + PageTemp[0:position+1+PageTemp2.find(u'}}')] + u'|' + codelangue + u'}}'
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Sports'
	) != -1 and (PageTemp.find(u':Catégorie:Sports') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Sports') + 1 != PageTemp.rfind(u'Catégorie:Sports'))):
							PageEnd = PageEnd + PageTemp[0:position] + u'|nocat=1}}'
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break

					elif Modele[p] == u'antiquité':
						if (PageTemp.find(u'spéc=') != -1 and PageTemp.find(u'spéc=') < PageTemp.find("}}")):
							if PageTemp.find(u'spéc=') > position+1:
								if debogage: print u'spéc= est après le code langue'
								if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Provinces romaines‎'
	) != -1 and (PageTemp.find(u':Catégorie:Provinces romaines‎') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Provinces romaines‎') + 1 != PageTemp.rfind(u'Catégorie:Provinces romaines‎'))):
									PageEnd = PageEnd + Modele[p] + u'|nocat=1|' + PageTemp[PageTemp.find(u'spéc='):PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
								else:
									PageEnd = PageEnd + Modele[p] + u'|' + codelangue + PageTemp[PageTemp.find(u'spéc=')-1:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
							else:
								if debogage: print u'spéc= est avant un éventuel code langue'
								PageTemp2 = PageTemp[position+1:len(PageTemp)]
								if (PageTemp2.find(u'|') != -1) or (PageTemp2.find(u'|') < PageTemp2.find(u'}}')):
									if EstCodeLangue == "false":
										if debogage: print u' retrait du code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|nocat=1}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+1] + u'|nocat=1}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
									else:
										if debogage: print u' avec code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|' + codelangue + u'}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+2] + codelangue + u'}}'
										PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
										break
								else:
									if debogage: print u' pas de code langue'
									PageEnd = PageEnd + PageTemp[0:position+1+PageTemp2.find(u'}}')] + u'|' + codelangue + u'}}'
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Provinces romaines‎'
	) != -1 and (PageTemp.find(u':Catégorie:Provinces romaines‎') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Provinces romaines‎') + 1 != PageTemp.rfind(u'Catégorie:Provinces romaines‎'))):
							PageEnd = PageEnd + PageTemp[0:position] + u'|nocat=1}}'
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
									
					elif Modele[p] == u'plante':
						if (PageTemp.find(u'spéc=') != -1 and PageTemp.find(u'spéc=') < PageTemp.find("}}")):
							if PageTemp.find(u'spéc=') > position+1: # spéc= est après le code langue
								if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Plantes'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes') + 1 != PageTemp.rfind(u'Catégorie:Plantes'))):
									PageEnd = PageEnd + Modele[p] + u'|nocat=1|' + PageTemp[PageTemp.find(u'spéc='):PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
								else:
									PageEnd = PageEnd + Modele[p] + u'|' + codelangue + PageTemp[PageTemp.find(u'spéc=')-1:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
							else: # spéc= est avant un éventuel code langue
								PageTemp2 = PageTemp[position+1:len(PageTemp)]
								if (PageTemp2.find(u'|') != -1) or (PageTemp2.find(u'|') < PageTemp2.find(u'}}')): # il y a un code langue
									if EstCodeLangue == "false":
										if debogage: print u' retrait du code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|nocat=1}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+1] + u'|nocat=1}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
									else:
										if debogage: print u' avec code langue'
										if PageTemp2.find(u'|') > PageTemp2.find(u'}}'):
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'}}')+1] + u'|' + codelangue + u'}}'
										else:
											PageEnd = PageEnd + PageTemp[:position+PageTemp2.find(u'|')+2] + codelangue + u'}}'
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
										break
								else: # Pas de code langue
									PageEnd = PageEnd + PageTemp[0:position+1+PageTemp2.find(u'}}')] + u'|' + codelangue + u'}}'
									PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
									break
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Plantes'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes') + 1 != PageTemp.rfind(u'Catégorie:Plantes'))):
							PageEnd = PageEnd + PageTemp[0:position] + u'|nocat=1}}'
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'athlétisme' or Modele[p] == u'athlé':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Sports'
	) != -1 and (PageTemp.find(u':Catégorie:Sports') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Sports') + 1 != PageTemp.rfind(u'Catégorie:Sports'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'danse':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Danses'
	) != -1 and (PageTemp.find(u':Catégorie:Danses') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Danses') + 1 != PageTemp.rfind(u'Catégorie:Danses'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'jeux':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Jeux'
	) != -1 and (PageTemp.find(u':Catégorie:Jeux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Jeux') + 1 != PageTemp.rfind(u'Catégorie:Jeux'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break

					elif Modele[p] == u'architecture' or Modele[p] == u'archi' or Modele[p] == u'fortification':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Édifices'
	) != -1 and (PageTemp.find(u':Catégorie:Édifices') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Édifices') + 1 != PageTemp.rfind(u'Catégorie:Édifices'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'réseau' or Modele[p] == u'réseaux' or Modele[p] == u'réseaux informatiques':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Protocoles réseau'
	) != -1 and (PageTemp.find(u':Catégorie:Protocoles réseau') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Protocoles réseau') + 1 != PageTemp.rfind(u'Catégorie:Protocoles réseau'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break						
	
					elif Modele[p] == u'géographie' or Modele[p] == u'géog' or Modele[p] == u'geog' or Modele[p] == u'toponymie' or Modele[p] == u'topon':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Gentilés'
	) != -1 and (PageTemp.find(u':Catégorie:Gentilés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Gentilés') + 1 != PageTemp.rfind(u'Catégorie:Gentilés'))

	) or (PageTemp.find(u'{{note-gentilé'
	) != -1 and (PageTemp.find(u'{{note-gentilé') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u'{{note-gentilé') + 1 != PageTemp.rfind(u'{{note-gentilé'))

	) or (PageTemp.find(u'Catégorie:Anciennes divisions géographiques'
	) != -1 and (PageTemp.find(u':Catégorie:Anciennes divisions géographiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Anciennes divisions géographiques') + 1 != PageTemp.rfind(u'Catégorie:Anciennes divisions géographiques'))

	) or (PageTemp.find(u'Catégorie:Collectivités d’outre-mer'
	) != -1 and (PageTemp.find(u':Catégorie:Collectivités d’outre-mer') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Collectivités d’outre-mer‎') + 1 != PageTemp.rfind(u'Catégorie:Collectivités d’outre-mer‎'))

	) or (PageTemp.find(u'Catégorie:Continents'
	) != -1 and (PageTemp.find(u':Catégorie:Continents') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Continents') + 1 != PageTemp.rfind(u'Catégorie:Continents'))

	) or (PageTemp.find(u'Catégorie:Districts'
	) != -1 and (PageTemp.find(u':Catégorie:Districts') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Districts') + 1 != PageTemp.rfind(u'Catégorie:Districts'))

	) or (PageTemp.find(u'Catégorie:Hagiotoponymes‎'
	) != -1 and (PageTemp.find(u':Catégorie:Hagiotoponymes‎') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Hagiotoponymes‎') + 1 != PageTemp.rfind(u'Catégorie:Hagiotoponymes‎'))

	) or (PageTemp.find(u'Catégorie:Hydronymes'
	) != -1 and (PageTemp.find(u':Catégorie:Hydronymes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Hydronymes') + 1 != PageTemp.rfind(u'Catégorie:Hydronymes'))

		) or (PageTemp.find(u'Catégorie:Baies'
		) != -1 and (PageTemp.find(u':Catégorie:Baies') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Baies') + 1 != PageTemp.rfind(u'Catégorie:Baies'))

		) or (PageTemp.find(u'Catégorie:Chutes‎'
		) != -1 and (PageTemp.find(u':Catégorie:Chutes‎') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Chutes‎') + 1 != PageTemp.rfind(u'Catégorie:Chutes‎'))
		
		) or (PageTemp.find(u'Catégorie:Détroits'
		) != -1 and (PageTemp.find(u':Catégorie:Détroits') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Détroits') + 1 != PageTemp.rfind(u'Catégorie:Détroits'))
		
		) or (PageTemp.find(u'Catégorie:Fleuves'
		) != -1 and (PageTemp.find(u':Catégorie:Fleuves') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Fleuves') + 1 != PageTemp.rfind(u'Catégorie:Fleuves'))
	
		) or (PageTemp.find(u'Catégorie:Golfes'
		) != -1 and (PageTemp.find(u':Catégorie:Golfes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Golfes') + 1 != PageTemp.rfind(u'Catégorie:Golfes'))
	
		) or (PageTemp.find(u'Catégorie:Lacs'
		) != -1 and (PageTemp.find(u':Catégorie:Lacs') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Lacs') + 1 != PageTemp.rfind(u'Catégorie:Lacs'))
		
		) or (PageTemp.find(u'Catégorie:Mers'
		) != -1 and (PageTemp.find(u':Catégorie:Mers') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Mers') + 1 != PageTemp.rfind(u'Catégorie:Mers'))
	
		) or (PageTemp.find(u'Catégorie:Océans'
		) != -1 and (PageTemp.find(u':Catégorie:Océans') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Océans') + 1 != PageTemp.rfind(u'Catégorie:Océans'))

		) or (PageTemp.find(u'Catégorie:Rivières'
		) != -1 and (PageTemp.find(u':Catégorie:Rivières') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Rivières') + 1 != PageTemp.rfind(u'Catégorie:Rivières'))

		) or (PageTemp.find(u'Catégorie:Cours d’eau'
		) != -1 and (PageTemp.find(u':Catégorie:Cours d’eau') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
		) and (PageTemp.find(u':Catégorie:Cours d’eau') + 1 != PageTemp.rfind(u'Catégorie:Cours d’eau'))

	) or (PageTemp.find(u'Catégorie:Îles'
	) != -1 and (PageTemp.find(u':Catégorie:Îles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Îles') + 1 != PageTemp.rfind(u'Catégorie:Îles'))

	) or (PageTemp.find(u'Catégorie:Localités'
	) != -1 and (PageTemp.find(u':Catégorie:Localités') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Localités') + 1 != PageTemp.rfind(u'Catégorie:Localités'))	

	) or (PageTemp.find(u'Catégorie:Chaînes de montagnes'
	) != -1 and (PageTemp.find(u':Catégorie:Chaînes de montagnes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chaînes de montagnes') + 1 != PageTemp.rfind(u'Catégorie:Chaînes de montagnes'))

	) or (PageTemp.find(u'Catégorie:Montagnes'
	) != -1 and (PageTemp.find(u':Catégorie:Montagnes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Montagnes') + 1 != PageTemp.rfind(u'Catégorie:Montagnes'))

	) or (PageTemp.find(u'Catégorie:Odonymes'
	) != -1 and (PageTemp.find(u':Catégorie:Odonymes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Odonymes') + 1 != PageTemp.rfind(u'Catégorie:Odonymes'))

	) or (PageTemp.find(u'Catégorie:Pays'
	) != -1 and (PageTemp.find(u':Catégorie:Pays') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pays') + 1 != PageTemp.rfind(u'Catégorie:Pays'))

	) or (PageTemp.find(u'Catégorie:Péninsules'
	) != -1 and (PageTemp.find(u':Catégorie:Péninsules') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Péninsules') + 1 != PageTemp.rfind(u'Catégorie:Péninsules'))
	
	) or (PageTemp.find(u'Catégorie:Quartiers'
	) != -1 and (PageTemp.find(u':Catégorie:Quartiers') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Quartiers') + 1 != PageTemp.rfind(u'Catégorie:Quartiers'))
	
	) or (PageTemp.find(u'Catégorie:Volcans'
	) != -1 and (PageTemp.find(u':Catégorie:Volcans') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Volcans') + 1 != PageTemp.rfind(u'Catégorie:Volcans'))

	) or (PageTemp.find(u'Catégorie:Régions'
	) != -1 and (PageTemp.find(u':Catégorie:Régions') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Régions') + 1 != PageTemp.rfind(u'Catégorie:Régions'))

	) or (PageTemp.find(u'Catégorie:États'
	) != -1 and (PageTemp.find(u':Catégorie:États') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:États') + 1 != PageTemp.rfind(u'Catégorie:États'))

	) or (PageTemp.find(u'Catégorie:Provinces'
	) != -1 and (PageTemp.find(u':Catégorie:Provinces') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Provinces') + 1 != PageTemp.rfind(u'Catégorie:Provinces'))

	) or (PageTemp.find(u'Catégorie:Länder'
	) != -1 and (PageTemp.find(u':Catégorie:Länder') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Länder') + 1 != PageTemp.rfind(u'Catégorie:Länder'))

	) or (PageTemp.find(u'Catégorie:Départements'
	) != -1 and (PageTemp.find(u':Catégorie:Départements') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Départements') + 1 != PageTemp.rfind(u'Catégorie:Départements'))

	) or (PageTemp.find(u'Catégorie:Cantons'
	) != -1 and (PageTemp.find(u':Catégorie:Cantons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cantons') + 1 != PageTemp.rfind(u'Catégorie:Cantons'))

	) or (PageTemp.find(u'Catégorie:Seigneuries‎'
	) != -1 and (PageTemp.find(u':Catégorie:Seigneuries‎') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Seigneuries‎') + 1 != PageTemp.rfind(u'Catégorie:Seigneuries‎'))
	
	) or (PageTemp.find(u'Catégorie:Chefs-lieux'
	) != -1 and (PageTemp.find(u':Catégorie:Chefs-lieux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chefs-lieux') + 1 != PageTemp.rfind(u'Catégorie:Chefs-lieux'))
	
	) or (PageTemp.find(u'Catégorie:Capitales'
	) != -1 and (PageTemp.find(u':Catégorie:Capitales') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Capitales') + 1 != PageTemp.rfind(u'Catégorie:Capitales'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'zoologie' or Modele[p] == u'zool' or Modele[p] == u'animaux' or Modele[p] == u'entomologie' or Modele[p] == u'entomol' or Modele[p] == u'entom' or Modele[p] == u'ornithologie' or Modele[p] == u'poissons' or Modele[p] == u'insectes':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Amphibiens'
	) != -1 and (PageTemp.find(u':Catégorie:Amphibiens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Amphibiens') + 1 != PageTemp.rfind(u'Catégorie:Amphibiens'))

	) or (PageTemp.find(u'Catégorie:Batraciens'
	) != -1 and (PageTemp.find(u':Catégorie:Batraciens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Batraciens') + 1 != PageTemp.rfind(u'Catégorie:Batraciens'))

	) or (PageTemp.find(u'Catégorie:Animaux'
	) != -1 and (PageTemp.find(u':Catégorie:Animaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Animaux') + 1 != PageTemp.rfind(u'Catégorie:Animaux'))

	) or (PageTemp.find(u'Catégorie:Crapauds'
	) != -1 and (PageTemp.find(u':Catégorie:Crapauds') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Crapauds') + 1 != PageTemp.rfind(u'Catégorie:Crapauds'))

	) or (PageTemp.find(u'Catégorie:Créatures'
	) != -1 and (PageTemp.find(u':Catégorie:Créatures') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Créatures') + 1 != PageTemp.rfind(u'Catégorie:Créatures'))

	) or (PageTemp.find(u'Catégorie:Crustacés'
	) != -1 and (PageTemp.find(u':Catégorie:Crustacés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Crustacés') + 1 != PageTemp.rfind(u'Catégorie:Crustacés'))

	) or (PageTemp.find(u'Catégorie:Dinosaures'
	) != -1 and (PageTemp.find(u':Catégorie:Dinosaures') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Dinosaures') + 1 != PageTemp.rfind(u'Catégorie:Dinosaures'))

	) or (PageTemp.find(u'Catégorie:Eumétazoaires'
	) != -1 and (PageTemp.find(u':Catégorie:Eumétazoaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Eumétazoaires') + 1 != PageTemp.rfind(u'Catégorie:Eumétazoaires'))

	) or (PageTemp.find(u'Catégorie:Arthropodes'
	) != -1 and (PageTemp.find(u':Catégorie:Arthropodes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Arthropodes') + 1 != PageTemp.rfind(u'Catégorie:Arthropodes'))

	) or (PageTemp.find(u'Catégorie:Chélicérates'
	) != -1 and (PageTemp.find(u':Catégorie:Chélicérates') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chélicérates') + 1 != PageTemp.rfind(u'Catégorie:Chélicérates'))

	) or (PageTemp.find(u'Catégorie:Arachnides'
	) != -1 and (PageTemp.find(u':Catégorie:Arachnides') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Arachnides') + 1 != PageTemp.rfind(u'Catégorie:Arachnides'))

	) or (PageTemp.find(u'Catégorie:Araignées'
	) != -1 and (PageTemp.find(u':Catégorie:Araignées') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Araignées') + 1 != PageTemp.rfind(u'Catégorie:Araignées'))

	) or (PageTemp.find(u'Catégorie:Insectes'
	) != -1 and (PageTemp.find(u':Catégorie:Insectes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Insectes') + 1 != PageTemp.rfind(u'Catégorie:Insectes'))

	) or (PageTemp.find(u'Catégorie:Mouches'
	) != -1 and (PageTemp.find(u':Catégorie:Mouches') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Mouches') + 1 != PageTemp.rfind(u'Catégorie:Mouches'))

	) or (PageTemp.find(u'Catégorie:Papillons'
	) != -1 and (PageTemp.find(u':Catégorie:Papillons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Papillons') + 1 != PageTemp.rfind(u'Catégorie:Papillons'))

	) or (PageTemp.find(u'Catégorie:Fourmis'
	) != -1 and (PageTemp.find(u':Catégorie:Fourmis') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fourmis') + 1 != PageTemp.rfind(u'Catégorie:Fourmis'))

	) or (PageTemp.find(u'Catégorie:Coléoptères'
	) != -1 and (PageTemp.find(u':Catégorie:Coléoptères') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Coléoptères') + 1 != PageTemp.rfind(u'Catégorie:Coléoptères'))
	
	) or (PageTemp.find(u'Catégorie:Mammifères'
	) != -1 and (PageTemp.find(u':Catégorie:Mammifères') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Mammifères') + 1 != PageTemp.rfind(u'Catégorie:Mammifères'))

	) or (PageTemp.find(u'Catégorie:Carnivores'
	) != -1 and (PageTemp.find(u':Catégorie:Carnivores') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Carnivores') + 1 != PageTemp.rfind(u'Catégorie:Carnivores'))

	) or (PageTemp.find(u'Catégorie:Cétartiodactyles'
	) != -1 and (PageTemp.find(u':Catégorie:Cétartiodactyles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cétartiodactyles') + 1 != PageTemp.rfind(u'Catégorie:Cétartiodactyles'))

	) or (PageTemp.find(u'Catégorie:Chevaux'
	) != -1 and (PageTemp.find(u':Catégorie:Chevaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chevaux') + 1 != PageTemp.rfind(u'Catégorie:Chevaux'))

	) or (PageTemp.find(u'Catégorie:Éléphantidés'
	) != -1 and (PageTemp.find(u':Catégorie:Éléphantidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Éléphantidés') + 1 != PageTemp.rfind(u'Catégorie:Éléphantidés'))

	) or (PageTemp.find(u'Catégorie:Chauves-souris'
	) != -1 and (PageTemp.find(u':Catégorie:Chauves-souris') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chauves-souris') + 1 != PageTemp.rfind(u'Catégorie:Chauves-souris'))

	) or (PageTemp.find(u'Catégorie:Mammifères marins'
	) != -1 and (PageTemp.find(u':Catégorie:Mammifères marins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Mammifères marins') + 1 != PageTemp.rfind(u'Catégorie:Mammifères marins'))

	) or (PageTemp.find(u'Catégorie:Cétacés'
	) != -1 and (PageTemp.find(u':Catégorie:Cétacés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cétacés') + 1 != PageTemp.rfind(u'Catégorie:Cétacés marins'))

	) or (PageTemp.find(u'Catégorie:Ongulés'
	) != -1 and (PageTemp.find(u':Catégorie:Ongulés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ongulés') + 1 != PageTemp.rfind(u'Catégorie:Ongulés'))

	) or (PageTemp.find(u'Catégorie:Équins'
	) != -1 and (PageTemp.find(u':Catégorie:Équins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Équins') + 1 != PageTemp.rfind(u'Catégorie:Équins'))

	) or (PageTemp.find(u'Catégorie:Ruminants'
	) != -1 and (PageTemp.find(u':Catégorie:Ruminants') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ruminants') + 1 != PageTemp.rfind(u'Catégorie:Ruminants'))

	) or (PageTemp.find(u'Catégorie:Bovins'
	) != -1 and (PageTemp.find(u':Catégorie:Bovins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Bovins') + 1 != PageTemp.rfind(u'Catégorie:Bovins'))

	) or (PageTemp.find(u'Catégorie:Ovins'
	) != -1 and (PageTemp.find(u':Catégorie:Ovins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ovins') + 1 != PageTemp.rfind(u'Catégorie:Ovins'))

	) or (PageTemp.find(u'Catégorie:Caprins'
	) != -1 and (PageTemp.find(u':Catégorie:Caprins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Caprins') + 1 != PageTemp.rfind(u'Catégorie:Caprins'))

	) or (PageTemp.find(u'Catégorie:Antilopes'
	) != -1 and (PageTemp.find(u':Catégorie:Antilopes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Antilopes') + 1 != PageTemp.rfind(u'Catégorie:Antilopes'))

	) or (PageTemp.find(u'Catégorie:Cervidés'
	) != -1 and (PageTemp.find(u':Catégorie:Cervidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cervidés') + 1 != PageTemp.rfind(u'Catégorie:Cervidés'))

	) or (PageTemp.find(u'Catégorie:Chameaux'
	) != -1 and (PageTemp.find(u':Catégorie:Chameaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chameaux') + 1 != PageTemp.rfind(u'Catégorie:Chameaux'))

	) or (PageTemp.find(u'Catégorie:Giraffidés'
	) != -1 and (PageTemp.find(u':Catégorie:Giraffidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Giraffidés') + 1 != PageTemp.rfind(u'Catégorie:Giraffidés'))

	) or (PageTemp.find(u'Catégorie:Lamas'
	) != -1 and (PageTemp.find(u':Catégorie:Lamas') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Lamas') + 1 != PageTemp.rfind(u'Catégorie:Lamas'))

	) or (PageTemp.find(u'Catégorie:Lapins'
	) != -1 and (PageTemp.find(u':Catégorie:Lapins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Lapins') + 1 != PageTemp.rfind(u'Catégorie:Lapins'))
	
	) or (PageTemp.find(u'Catégorie:Porcins'
	) != -1 and (PageTemp.find(u':Catégorie:Porcins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Porcins') + 1 != PageTemp.rfind(u'Catégorie:Porcins'))

	) or (PageTemp.find(u'Catégorie:Marsupiaux'
	) != -1 and (PageTemp.find(u':Catégorie:Marsupiaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Marsupiaux') + 1 != PageTemp.rfind(u'Catégorie:Marsupiaux'))

	) or (PageTemp.find(u'Catégorie:Grenouilles'
	) != -1 and (PageTemp.find(u':Catégorie:Grenouilles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Grenouilles') + 1 != PageTemp.rfind(u'Catégorie:Grenouilles'))

	) or (PageTemp.find(u'Catégorie:Marsupiaux'
	) != -1 and (PageTemp.find(u':Catégorie:Marsupiaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Marsupiaux') + 1 != PageTemp.rfind(u'Catégorie:Marsupiaux'))

	) or (PageTemp.find(u'Catégorie:Primates'
	) != -1 and (PageTemp.find(u':Catégorie:Primates') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Primates') + 1 != PageTemp.rfind(u'Catégorie:Primates'))

	) or (PageTemp.find(u'Catégorie:Proboscidiens'
	) != -1 and (PageTemp.find(u':Catégorie:Proboscidiens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Proboscidiens') + 1 != PageTemp.rfind(u'Catégorie:Proboscidiens'))

	) or (PageTemp.find(u'Catégorie:Thériens'
	) != -1 and (PageTemp.find(u':Catégorie:Thériens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Thériens') + 1 != PageTemp.rfind(u'Catégorie:Thériens'))

	) or (PageTemp.find(u'Catégorie:Caniformes'
	) != -1 and (PageTemp.find(u':Catégorie:Caniformes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Caniformes') + 1 != PageTemp.rfind(u'Catégorie:Caniformes'))

	) or (PageTemp.find(u'Catégorie:Canidés'
	) != -1 and (PageTemp.find(u':Catégorie:Canidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Canidés') + 1 != PageTemp.rfind(u'Catégorie:Canidés'))

	) or (PageTemp.find(u'Catégorie:Chiens'
	) != -1 and (PageTemp.find(u':Catégorie:Chiens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chiens') + 1 != PageTemp.rfind(u'Catégorie:Chiens'))

	) or (PageTemp.find(u'Catégorie:Chats'
	) != -1 and (PageTemp.find(u':Catégorie:Chats') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chats') + 1 != PageTemp.rfind(u'Catégorie:Chats'))

	) or (PageTemp.find(u'Catégorie:Félidés'
	) != -1 and (PageTemp.find(u':Catégorie:Félidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Félidés') + 1 != PageTemp.rfind(u'Catégorie:Félidés'))

	) or (PageTemp.find(u'Catégorie:Deutérostomiens'
	) != -1 and (PageTemp.find(u':Catégorie:Deutérostomiens') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Deutérostomiens') + 1 != PageTemp.rfind(u'Catégorie:Deutérostomiens'))

	) or (PageTemp.find(u'Catégorie:Chordés'
	) != -1 and (PageTemp.find(u':Catégorie:Chordés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Chordés') + 1 != PageTemp.rfind(u'Catégorie:Chordés'))

	) or (PageTemp.find(u'Catégorie:Vertébrés'
	) != -1 and (PageTemp.find(u':Catégorie:Vertébrés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Vertébrés') + 1 != PageTemp.rfind(u'Catégorie:Vertébrés'))

	) or (PageTemp.find(u'Catégorie:Mollusques'
	) != -1 and (PageTemp.find(u':Catégorie:Mollusques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Mollusques') + 1 != PageTemp.rfind(u'Catégorie:Mollusques'))

	) or (PageTemp.find(u'Catégorie:Rapaces'
	) != -1 and (PageTemp.find(u':Catégorie:Rapaces') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Rapaces') + 1 != PageTemp.rfind(u'Catégorie:Rapaces'))

	) or (PageTemp.find(u'Catégorie:Oiseaux'
	) != -1 and (PageTemp.find(u':Catégorie:Oiseaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Oiseaux') + 1 != PageTemp.rfind(u'Catégorie:Oiseaux'))

	) or (PageTemp.find(u'Catégorie:Anatidés'
	) != -1 and (PageTemp.find(u':Catégorie:Anatidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Anatidés') + 1 != PageTemp.rfind(u'Catégorie:Anatidés'))

	) or (PageTemp.find(u'Catégorie:Passereaux'
	) != -1 and (PageTemp.find(u':Catégorie:Passereaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Passereaux') + 1 != PageTemp.rfind(u'Catégorie:Passereaux'))

	) or (PageTemp.find(u'Catégorie:Anatidés'
	) != -1 and (PageTemp.find(u':Catégorie:Anatidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Anatidés') + 1 != PageTemp.rfind(u'Catégorie:Anatidés'))

	) or (PageTemp.find(u'Catégorie:Sphéniscidés'
	) != -1 and (PageTemp.find(u':Catégorie:Sphéniscidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Sphéniscidés') + 1 != PageTemp.rfind(u'Catégorie:Sphéniscidés'))

	) or (PageTemp.find(u'Catégorie:Parazoaires'
	) != -1 and (PageTemp.find(u':Catégorie:Parazoaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Parazoaires') + 1 != PageTemp.rfind(u'Catégorie:Parazoaires'))

	) or (PageTemp.find(u'Catégorie:Éponges'
	) != -1 and (PageTemp.find(u':Catégorie:Éponges') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Éponges') + 1 != PageTemp.rfind(u'Catégorie:Éponges'))

	) or (PageTemp.find(u'Catégorie:Poissons'
	) != -1 and (PageTemp.find(u':Catégorie:Poissons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Poissons') + 1 != PageTemp.rfind(u'Catégorie:Poissons'))

	) or (PageTemp.find(u'Catégorie:Requins'
	) != -1 and (PageTemp.find(u':Catégorie:Requins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Requins') + 1 != PageTemp.rfind(u'Catégorie:Requins'))

	) or (PageTemp.find(u'Catégorie:Saumons'
	) != -1 and (PageTemp.find(u':Catégorie:Saumons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Saumons') + 1 != PageTemp.rfind(u'Catégorie:Saumons'))

	) or (PageTemp.find(u'Catégorie:Truites'
	) != -1 and (PageTemp.find(u':Catégorie:Truites') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Truites') + 1 != PageTemp.rfind(u'Catégorie:Truites'))

	) or (PageTemp.find(u'Catégorie:Reptiles'
	) != -1 and (PageTemp.find(u':Catégorie:Reptiles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Reptiles') + 1 != PageTemp.rfind(u'Catégorie:Reptiles'))

	) or (PageTemp.find(u'Catégorie:Serpents'
	) != -1 and (PageTemp.find(u':Catégorie:Serpents') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Serpents') + 1 != PageTemp.rfind(u'Catégorie:Serpents'))

	) or (PageTemp.find(u'Catégorie:Tétrapodes'
	) != -1 and (PageTemp.find(u':Catégorie:Tétrapodes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Tétrapodes') + 1 != PageTemp.rfind(u'Catégorie:Tétrapodes'))

	) or (PageTemp.find(u'Catégorie:Métazoaires supérieurs'
	) != -1 and (PageTemp.find(u':Catégorie:Métazoaires supérieurs') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Métazoaires supérieurs') + 1 != PageTemp.rfind(u'Catégorie:Métazoaires supérieurs'))

	) or (PageTemp.find(u'Catégorie:Féliformes'
	) != -1 and (PageTemp.find(u':Catégorie:Féliformes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Féliformes') + 1 != PageTemp.rfind(u'Catégorie:Féliformes'))

	) or (PageTemp.find(u'Catégorie:Mantinés'
	) != -1 and (PageTemp.find(u':Catégorie:Mantinés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Mantinés') + 1 != PageTemp.rfind(u'Catégorie:Mantinés'))

	) or (PageTemp.find(u'Catégorie:Rangifers'
	) != -1 and (PageTemp.find(u':Catégorie:Rangifers') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Rangifers') + 1 != PageTemp.rfind(u'Catégorie:Rangifers'))

	) or (PageTemp.find(u'Catégorie:Corvidés'
	) != -1 and (PageTemp.find(u':Catégorie:Corvidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Corvidés') + 1 != PageTemp.rfind(u'Catégorie:Corvidés'))

	) or (PageTemp.find(u'Catégorie:Anoures'
	) != -1 and (PageTemp.find(u':Catégorie:Anoures') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Anoures') + 1 != PageTemp.rfind(u'Catégorie:Anoures'))

	) or (PageTemp.find(u'Catégorie:Faucons'
	) != -1 and (PageTemp.find(u':Catégorie:Faucons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Faucons') + 1 != PageTemp.rfind(u'Catégorie:Faucons'))

	) or (PageTemp.find(u'Catégorie:Bivalves'
	) != -1 and (PageTemp.find(u':Catégorie:Bivalves') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Bivalves') + 1 != PageTemp.rfind(u'Catégorie:Bivalves'))

	) or (PageTemp.find(u'Catégorie:Céphalopodes'
	) != -1 and (PageTemp.find(u':Catégorie:Céphalopodes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Céphalopodes') + 1 != PageTemp.rfind(u'Catégorie:Céphalopodes'))

	) or (PageTemp.find(u'Catégorie:Gastéropodes'
	) != -1 and (PageTemp.find(u':Catégorie:Gastéropodes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Gastéropodes') + 1 != PageTemp.rfind(u'Catégorie:Gastéropodes'))

	) or (PageTemp.find(u'Catégorie:Rongeurs'
	) != -1 and (PageTemp.find(u':Catégorie:Rongeurs') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Rongeurs') + 1 != PageTemp.rfind(u'Catégorie:Rongeurs'))

	) or (PageTemp.find(u'Catégorie:Écureuils'
	) != -1 and (PageTemp.find(u':Catégorie:Écureuils') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Écureuils') + 1 != PageTemp.rfind(u'Catégorie:Écureuils'))

	) or (PageTemp.find(u'Catégorie:Ursidés'
	) != -1 and (PageTemp.find(u':Catégorie:Ursidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ursidés') + 1 != PageTemp.rfind(u'Catégorie:Ursidés'))
	
	) or (PageTemp.find(u'Catégorie:Léporidés'
	) != -1 and (PageTemp.find(u':Catégorie:Léporidés') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Léporidés') + 1 != PageTemp.rfind(u'Catégorie:Léporidés'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'botanique' or Modele[p] == u'botan' or Modele[p] == u'phytonymie' or Modele[p] == u'phyton':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Plantes'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes') + 1 != PageTemp.rfind(u'Catégorie:Plantes'))

	) or (PageTemp.find(u'Catégorie:Arbres'
	) != -1 and (PageTemp.find(u':Catégorie:Arbres') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Arbres') + 1 != PageTemp.rfind(u'Catégorie:Arbres'))

	) or (PageTemp.find(u'Catégorie:Peupliers'
	) != -1 and (PageTemp.find(u':Catégorie:Peupliers') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Peupliers') + 1 != PageTemp.rfind(u'Catégorie:Peupliers'))

	) or (PageTemp.find(u'Catégorie:Saules'
	) != -1 and (PageTemp.find(u':Catégorie:Saules') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Saules') + 1 != PageTemp.rfind(u'Catégorie:Saules'))

	) or (PageTemp.find(u'Catégorie:Céréales'
	) != -1 and (PageTemp.find(u':Catégorie:Céréales') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Céréales') + 1 != PageTemp.rfind(u'Catégorie:Céréales'))

	) or (PageTemp.find(u'Catégorie:Fleurs'
	) != -1 and (PageTemp.find(u':Catégorie:Fleurs') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fleurs') + 1 != PageTemp.rfind(u'Catégorie:Fleurs'))

	) or (PageTemp.find(u'Catégorie:Fougères'
	) != -1 and (PageTemp.find(u':Catégorie:Fougères') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fougères') + 1 != PageTemp.rfind(u'Catégorie:Fougères'))

	) or (PageTemp.find(u'Catégorie:Fruits'
	) != -1 and (PageTemp.find(u':Catégorie:Fruits') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fruits') + 1 != PageTemp.rfind(u'Catégorie:Fruits'))

	) or (PageTemp.find(u'Catégorie:Fougères'
	) != -1 and (PageTemp.find(u':Catégorie:Fougères') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fougères') + 1 != PageTemp.rfind(u'Catégorie:Fougères'))

	) or (PageTemp.find(u'Catégorie:Plantes imaginaires'
	) != -1 and (PageTemp.find(u':Catégorie:Plantes imaginaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Plantes imaginaires') + 1 != PageTemp.rfind(u'Catégorie:Plantes imaginaires'))

	) or (PageTemp.find(u'Catégorie:Lianes'
	) != -1 and (PageTemp.find(u':Catégorie:Lianes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Lianes') + 1 != PageTemp.rfind(u'Catégorie:Lianes'))

	) or (PageTemp.find(u'Catégorie:Poires'
	) != -1 and (PageTemp.find(u':Catégorie:Poires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Poires') + 1 != PageTemp.rfind(u'Catégorie:Poires'))

	) or (PageTemp.find(u'Catégorie:Prunes'
	) != -1 and (PageTemp.find(u':Catégorie:Prunes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Prunes') + 1 != PageTemp.rfind(u'Catégorie:Prunes'))

	) or (PageTemp.find(u'Catégorie:Pêches'
	) != -1 and (PageTemp.find(u':Catégorie:Pêches') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pêches') + 1 != PageTemp.rfind(u'Catégorie:Pêches'))

	) or (PageTemp.find(u'Catégorie:Pommes'
	) != -1 and (PageTemp.find(u':Catégorie:Pommes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pommes') + 1 != PageTemp.rfind(u'Catégorie:Pommes'))

	) or (PageTemp.find(u'Catégorie:Pommes de terre'
	) != -1 and (PageTemp.find(u':Catégorie:Pommes de terre') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pommes de terre') + 1 != PageTemp.rfind(u'Catégorie:Pommes de terre'))

	) or (PageTemp.find(u'Catégorie:Algues'
	) != -1 and (PageTemp.find(u':Catégorie:Algues') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Algues') + 1 != PageTemp.rfind(u'Catégorie:Algues'))

	) or (PageTemp.find(u'Catégorie:Dicotylédones'
	) != -1 and (PageTemp.find(u':Catégorie:Dicotylédones') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Dicotylédones') + 1 != PageTemp.rfind(u'Catégorie:Dicotylédones'))

	) or (PageTemp.find(u'Catégorie:Cypéracées'
	) != -1 and (PageTemp.find(u':Catégorie:Cypéracées') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cypéracées') + 1 != PageTemp.rfind(u'Catégorie:Cypéracées'))
	
	) or (PageTemp.find(u'Catégorie:Fabacées'
	) != -1 and (PageTemp.find(u':Catégorie:Fabacées') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fabacées') + 1 != PageTemp.rfind(u'Catégorie:Fabacées'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'médecine' or Modele[p] == u'méde' or Modele[p] == u'vétérinaire' or Modele[p] == u'chirurgie' or Modele[p] == u'chir' or Modele[p] == u'pharmacologie' or Modele[p] == u'pharmacol' or Modele[p] == u'pharmacie' or Modele[p] == u'nosologie' or Modele[p] == u'obstétrique' or Modele[p] == u'pédiatrie' or Modele[p] == u'ophtalmologie' or Modele[p] == u'secourisme' or Modele[p] == u'oncologie' or Modele[p] == u'gynécologie':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Médecine non conventionnelles'
	) != -1 and (PageTemp.find(u'Catégorie:Médecine non conventionnelles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Médecine non conventionnelles') + 1 != PageTemp.rfind(u'Catégorie:Médecine non conventionnelles'))

	) or (PageTemp.find(u'Catégorie:Maladies'
	) != -1 and (PageTemp.find(u'Catégorie:Maladies') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Maladies') + 1 != PageTemp.rfind(u'Catégorie:Maladies'))

	) or (PageTemp.find(u'Catégorie:Maladies de l’œil'
	) != -1 and (PageTemp.find(u'Catégorie:Maladies de l’œil') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Maladies de l’œil') + 1 != PageTemp.rfind(u'Catégorie:Maladies de l’œil'))

	) or (PageTemp.find(u'Catégorie:Maladies orphelines'
	) != -1 and (PageTemp.find(u'Catégorie:Maladies orphelines') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Maladies orphelines') + 1 != PageTemp.rfind(u'Catégorie:Maladies orphelines'))

	) or (PageTemp.find(u'Catégorie:Troubles du langage'
	) != -1 and (PageTemp.find(u'Catégorie:Troubles du langage') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Troubles du langage') + 1 != PageTemp.rfind(u'Catégorie:Troubles du langage'))

	) or (PageTemp.find(u'Catégorie:Phobies'
	) != -1 and (PageTemp.find(u'Catégorie:Phobies') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Phobies') + 1 != PageTemp.rfind(u'Catégorie:Phobies'))

	) or (PageTemp.find(u'Catégorie:Maladies psychiatriques'
	) != -1 and (PageTemp.find(u'Catégorie:Maladies psychiatriques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Maladies psychiatriques') + 1 != PageTemp.rfind(u'Catégorie:Maladies psychiatriques'))

	) or (PageTemp.find(u'Catégorie:Dermatologie'
	) != -1 and (PageTemp.find(u'Catégorie:Dermatologie') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Dermatologie') + 1 != PageTemp.rfind(u'Catégorie:Dermatologie'))

	) or (PageTemp.find(u'Catégorie:Médicaments'
	) != -1 and (PageTemp.find(u':Catégorie:Médicaments') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Médicaments') + 1 != PageTemp.rfind(u'Catégorie:Médicaments'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'métrologie' or Modele[p] == u'métrol':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Unités de mesure'
	) != -1 and (PageTemp.find(u':Catégorie:Unités de mesure') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Unités de mesure') + 1 != PageTemp.rfind(u'Catégorie:Unités de mesure'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'rhétorique' or Modele[p] == u'rhéto':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Figures de style'
	) != -1 and (PageTemp.find(u'Catégorie:Figures de style') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Figures de style') + 1 != PageTemp.rfind(u'Catégorie:Figures de style'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'linguistique' or Modele[p] == u'ling':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Langues'
	) != -1 and (PageTemp.find(u'Catégorie:Langues') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Langues') + 1 != PageTemp.rfind(u'Catégorie:Langues'))

	) or (PageTemp.find(u'{{Catégorie langue'
	) != -1 and (PageTemp.find(u'{{Catégorie langue') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	)

	) or (PageTemp.find(u'{{catégorie langue'
	) != -1 and (PageTemp.find(u'{{catégorie langue') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	)
	
	) or (PageTemp.find(u'Catégorie:Dialectes'
	) != -1 and (PageTemp.find(u'Catégorie:Dialectes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Dialectes') + 1 != PageTemp.rfind(u'Catégorie:Dialectes'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'typographie' or Modele[p] == u'typo':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Ponctuations'
	) != -1 and (PageTemp.find(u'Catégorie:Ponctuations') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ponctuations') + 1 != PageTemp.rfind(u'Catégorie:Ponctuations'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'sciences':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Noms de sciences'
	) != -1 and (PageTemp.find(u'Catégorie:Noms de sciences') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Noms de sciences') + 1 != PageTemp.rfind(u'Catégorie:Noms de sciences'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'astronomie' or Modele[p] == u'astro' or Modele[p] == u'astron':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Étoiles'
	) != -1 and (PageTemp.find(u'Catégorie:Étoiles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Étoiles') + 1 != PageTemp.rfind(u'Catégorie:Étoiles'))

	) or (PageTemp.find(u'Catégorie:Constellations'
	) != -1 and (PageTemp.find(u'Catégorie:Constellations') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Constellations') + 1 != PageTemp.rfind(u'Catégorie:Constellations'))

	) or (PageTemp.find(u'Catégorie:Planètes'
	) != -1 and (PageTemp.find(u'Catégorie:Planètes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Planètes') + 1 != PageTemp.rfind(u'Catégorie:Planètes'))

	) or (PageTemp.find(u'Catégorie:Satellites'
	) != -1 and (PageTemp.find(u'Catégorie:Satellites') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Satellites') + 1 != PageTemp.rfind(u'Catégorie:Satellites'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'astrologie' or Modele[p] == u'astrol':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Zodiaques'
	) != -1 and (PageTemp.find(u'Catégorie:Zodiaques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Zodiaques') + 1 != PageTemp.rfind(u'Catégorie:Zodiaques'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'mycologie' or Modele[p] == u'mycol' or Modele[p] == u'myco':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Champignons'
	) != -1 and (PageTemp.find(u'Catégorie:Champignons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Champignons') + 1 != PageTemp.rfind(u'Catégorie:Champignons'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'sexualité' or Modele[p] == u'sexe':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Positions sexuelles'
	) != -1 and (PageTemp.find(u'Catégorie:Positions sexuelles') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Positions sexuelles') + 1 != PageTemp.rfind(u'Catégorie:Positions sexuelles'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'géologie' or Modele[p] == u'géol':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Temps géologiques'
	) != -1 and (PageTemp.find(u'Catégorie:Temps géologiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Temps géologiques') + 1 != PageTemp.rfind(u'Catégorie:Temps géologiques'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'chimie' or Modele[p] == u'chim' or Modele[p] == u'biochimie' or Modele[p] == u'bioch':
						if (EstCodeLangue == "false"

	) or (PageTemp.find(u'Catégorie:Acides gras'
	) != -1 and (PageTemp.find(u'Catégorie:Acides gras') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Acides gras') + 1 != PageTemp.rfind(u'Catégorie:Acides gras'))

	) or (PageTemp.find(u'Catégorie:Éléments chimiques'
	) != -1 and (PageTemp.find(u'Catégorie:Éléments chimiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Éléments chimiques') + 1 != PageTemp.rfind(u'Catégorie:Éléments chimiques'))

	) or (PageTemp.find(u'Catégorie:Substances chimiques'
	) != -1 and (PageTemp.find(u'Catégorie:Substances chimiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Substances chimiques') + 1 != PageTemp.rfind(u'Catégorie:Substances chimiques'))

	) or (PageTemp.find(u'Catégorie:Symboles des éléments chimiques'
	) != -1 and (PageTemp.find(u'Catégorie:Symboles des éléments chimiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Symboles des éléments chimiques') + 1 != PageTemp.rfind(u'Catégorie:Symboles des éléments chimiques'))

	) or (PageTemp.find(u'Catégorie:Symboles désuets des éléments chimiques'
	) != -1 and (PageTemp.find(u'Catégorie:Symboles désuets des éléments chimiques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Symboles désuets des éléments chimiques') + 1 != PageTemp.rfind(u'Catégorie:Symboles désuets des éléments chimiques'))
		
	) or (PageTemp.find(u'Catégorie:Polymères'
	) != -1 and (PageTemp.find(u'Catégorie:Polymères') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Polymères') + 1 != PageTemp.rfind(u'Catégorie:Polymères'))

	) or (PageTemp.find(u'Catégorie:Métaux'
	) != -1 and (PageTemp.find(u'Catégorie:Métaux') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Métaux') + 1 != PageTemp.rfind(u'Catégorie:Métaux'))
	
	) or (PageTemp.find(u'Catégorie:Alliages'
	) != -1 and (PageTemp.find(u'Catégorie:Alliages') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Alliages') + 1 != PageTemp.rfind(u'Catégorie:Alliages'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'cuisine' or Modele[p] == u'cuis':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Aliments'
	) != -1 and (PageTemp.find(u'Catégorie:Aliments') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Aliments') + 1 != PageTemp.rfind(u'Catégorie:Aliments'))

	) or (PageTemp.find(u'Catégorie:Préparations culinaires'
	) != -1 and (PageTemp.find(u'Catégorie:Préparations culinaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Préparations culinaires') + 1 != PageTemp.rfind(u'Catégorie:Préparations culinaires'))

	) or (PageTemp.find(u'Catégorie:Ustensiles de cuisine'
	) != -1 and (PageTemp.find(u'Catégorie:Ustensiles de cuisine') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Ustensiles de cuisine') + 1 != PageTemp.rfind(u'Catégorie:Ustensiles de cuisine'))

	) or (PageTemp.find(u'Catégorie:Condiments'
	) != -1 and (PageTemp.find(u'Catégorie:Condiments') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Condiments') + 1 != PageTemp.rfind(u'Catégorie:Condiments'))

	) or (PageTemp.find(u'Catégorie:Fromages'
	) != -1 and (PageTemp.find(u'Catégorie:Fromages') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fromages') + 1 != PageTemp.rfind(u'Catégorie:Fromages'))

	) or (PageTemp.find(u'Catégorie:Viandes'
	) != -1 and (PageTemp.find(u'Catégorie:Viandes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Viandes') + 1 != PageTemp.rfind(u'Catégorie:Viandes'))

	) or (PageTemp.find(u'Catégorie:Fruits'
	) != -1 and (PageTemp.find(u'Catégorie:Fruits') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fruits') + 1 != PageTemp.rfind(u'Catégorie:Fruits'))

	) or (PageTemp.find(u'Catégorie:Fruits de mer'
	) != -1 and (PageTemp.find(u'Catégorie:Fruits de mer') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fruits de mer') + 1 != PageTemp.rfind(u'Catégorie:Fruits de mer'))

	) or (PageTemp.find(u'Catégorie:Légumes'
	) != -1 and (PageTemp.find(u'Catégorie:Légumes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Légumes') + 1 != PageTemp.rfind(u'Catégorie:Légumes'))

	) or (PageTemp.find(u'Catégorie:Alcools'
	) != -1 and (PageTemp.find(u'Catégorie:Alcools') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Alcools') + 1 != PageTemp.rfind(u'Catégorie:Alcools'))

	) or (PageTemp.find(u'Catégorie:Vins'
	) != -1 and (PageTemp.find(u'Catégorie:Vins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Vins') + 1 != PageTemp.rfind(u'Catégorie:Vins'))

	) or (PageTemp.find(u'Catégorie:Champignons'
	) != -1 and (PageTemp.find(u'Catégorie:Champignons') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Champignons') + 1 != PageTemp.rfind(u'Catégorie:Champignons'))

	) or (PageTemp.find(u'Catégorie:Pommes'
	) != -1 and (PageTemp.find(u'Catégorie:Pommes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pommes') + 1 != PageTemp.rfind(u'Catégorie:Pommes'))

	) or (PageTemp.find(u'Catégorie:Poires'
	) != -1 and (PageTemp.find(u'Catégorie:Poires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Poires') + 1 != PageTemp.rfind(u'Catégorie:Poires'))

	) or (PageTemp.find(u'Catégorie:Tomates'
	) != -1 and (PageTemp.find(u'Catégorie:Tomates') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Tomates') + 1 != PageTemp.rfind(u'Catégorie:Tomates'))

	) or (PageTemp.find(u'Catégorie:Pâtes'
	) != -1 and (PageTemp.find(u'Catégorie:Pâtes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Pâtes') + 1 != PageTemp.rfind(u'Catégorie:Pâtes'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'œnologie' or Modele[p] == u'œnol':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Vins'
	) != -1 and (PageTemp.find(u'Catégorie:Vins') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Vins') + 1 != PageTemp.rfind(u'Catégorie:Vins'))

	) or (PageTemp.find(u'Catégorie:Cépages'
	) != -1 and (PageTemp.find(u'Catégorie:Cépages') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Cépages') + 1 != PageTemp.rfind(u'Catégorie:Cépages'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'militaire' or Modele[p] == u'mili' or Modele[p] == u'guerre':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Soldats'
	) != -1 and (PageTemp.find(u'Catégorie:Soldats') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Soldats') + 1 != PageTemp.rfind(u'Catégorie:Soldats'))

	) or (PageTemp.find(u'Catégorie:Grades militaires'
	) != -1 and (PageTemp.find(u'Catégorie:Grades militaires') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Grades militaires') + 1 != PageTemp.rfind(u'Catégorie:Grades militaires'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'armement' or Modele[p] == u'arme':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Armes'
	) != -1 and (PageTemp.find(u'Catégorie:Armes') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Armes') + 1 != PageTemp.rfind(u'Catégorie:Armes'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'musique' or Modele[p] == u'musi':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Instruments'
	) != -1 and (PageTemp.find(u'Catégorie:Instruments') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Instruments') + 1 != PageTemp.rfind(u'Catégorie:Instruments'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'construction' or Modele[p] == u'constr' or Modele[p] == u'bâtiment':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Édifices'
	) != -1 and (PageTemp.find(u'Catégorie:Édifices') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Édifices') + 1 != PageTemp.rfind(u'Catégorie:Édifices'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'électricité' or Modele[p] == u'élec':
						if (EstCodeLangue == "false"
	) or (PageTemp.find(u'Catégorie:Composants électriques'
	) != -1 and (PageTemp.find(u'Catégorie:Composants électriques') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Composants électriques') + 1 != PageTemp.rfind(u'Catégorie:Composants électriques'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break			
						
					# Ce modèle par contre remplace la catégorie
					elif Modele[p] == u'injurieux' or Modele[p] == u'injur':
						if (EstCodeLangue == "false"):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							if PageTemp.find(u'[[Catégorie:Insultes en français]]') != -1 and codelangue == u'fr':
								PageTemp = PageTemp[0:PageTemp.find(u'[[Catégorie:Insultes en français]]')] + PageTemp[PageTemp.find(u'[[Catégorie:Insultes en français]]')+len(u'[[Catégorie:Insultes en français]]'):len(PageTemp)]
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'préciser' or Modele[p] == u'?' or Modele[p] == u'doute' or Modele[p] == u'vérifier':
						if codelangue != "" and codelangue is not None:
							if PageTemp[position:position+2] == u'}}' or PageTemp[position:position+4] == u'fr}}':
								PageEnd = PageEnd + PageTemp[0:position] + "||" + codelangue + "}}"
								PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								break
							else:
								while PageTemp.find(u'{{') < PageTemp.find(u'}}') and PageTemp.find(u'{{') != -1:
									# On saute les différents modèles inclus
									PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
									PageTemp = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
								if PageTemp.find("|") > PageTemp.find(u'}}') or PageTemp.find(u'|') == -1:
									position = PageTemp.find("}}")
								else:
									position = PageTemp.find("|")
									PageTemp2 = PageTemp[position+1:len(PageTemp)]
									if PageTemp2.find(u'|') != -1 and PageTemp2.find(u'|') < PageTemp2.find(u'}}'):
										# Code langue déjà renseigné
										break
									elif PageTemp.find(u'|') != -1 and PageTemp.find(u'|') < PageTemp.find(u'}}'):
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')] + u'|' + codelangue + "}}"
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]					
									else:
										PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')] + u'||' + codelangue + "}}"
										PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
								#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
								break
						else:
							break
					elif Modele[p] == u'perfectif' or Modele[p] == u'perf' or Modele[p] == u'imperfectif' or Modele[p] == u'imperf' or Modele[p] == u'déterminé' or Modele[p] == u'dét' or Modele[p] == u'indéterminé' or Modele[p] == u'indét':
						if (EstCodeLangue == "false") or PageEnd.rfind(u'(') > PageEnd.rfind(u')'): # Si on est dans des parenthèses
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
						
					elif Modele[p] == u'trad' or Modele[p] == u'trad+' or Modele[p] == u'trad-' or Modele[p] == u'trad--':
						if position == PageTemp.find(u'}}') or position == PageTemp.find(u'--}}')-2 or position == PageTemp.find(u'|en|}}')-4:
							PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
							PageTemp = PageTemp[PageTemp.find(u'}}')+2:]
							break
						# Lettres spéciales à remplacer dans les traductions vers certaines langues
						PageTemp2 = PageTemp[position+1:len(PageTemp)]
						if PageTemp2[0:PageTemp2.find(u'|')] == u'ro' or PageTemp2[0:PageTemp2.find(u'|')] == u'mo':
							while PageTemp.find(u'ş') != -1 and PageTemp.find(u'ş') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'ş')] + u'ș' + PageTemp[PageTemp.find(u'ş')+1:len(PageTemp)]
							while PageTemp.find(u'Ş') != -1 and PageTemp.find(u'Ş') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'Ş')] + u'Ș' + PageTemp[PageTemp.find(u'Ş')+1:len(PageTemp)]
							while PageTemp.find(u'ţ') != -1 and PageTemp.find(u'ţ') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'ţ')] + u'ț' + PageTemp[PageTemp.find(u'ţ')+1:len(PageTemp)]
							while PageTemp.find(u'Ţ') != -1 and PageTemp.find(u'Ţ') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'Ţ')] + u'Ț' + PageTemp[PageTemp.find(u'Ţ')+1:len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'az' or PageTemp2[0:PageTemp2.find(u'|')] == u'ku' or PageTemp2[0:PageTemp2.find(u'|')] == u'sq' or PageTemp2[0:PageTemp2.find(u'|')] == u'tk' or PageTemp2[0:PageTemp2.find(u'|')] == u'tr' or PageTemp2[0:PageTemp2.find(u'|')] == u'tt':
							while PageTemp.find(u'ș') != -1 and PageTemp.find(u'ș') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'ș')] + u'ş' + PageTemp[PageTemp.find(u'ș')+1:len(PageTemp)]
							while PageTemp.find(u'Ș') != -1 and PageTemp.find(u'Ș') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'Ș')] + u'Ş' + PageTemp[PageTemp.find(u'Ș')+1:len(PageTemp)]
							while PageTemp.find(u'ț') != -1 and PageTemp.find(u'ț') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'ț')] + u'ţ' + PageTemp[PageTemp.find(u'ț')+1:len(PageTemp)]
							while PageTemp.find(u'Ț') != -1 and PageTemp.find(u'Ț') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'Ț')] + u'Ţ' + PageTemp[PageTemp.find(u'Ț')+1:len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'fon':
							while PageTemp.find(u'ε') != -1 and PageTemp.find(u'ε') < PageTemp.find(u'\n'):
								PageTemp = PageTemp[0:PageTemp.find(u'ε')] + u'ɛ' + PageTemp[PageTemp.find(u'ε')+1:len(PageTemp)]
						# http://fr.wiktionary.org/wiki/Mod%C3%A8le:code_interwiki
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'cmn':
							PageTemp = PageTemp[0:PageTemp.find(u'cmn')] + u'zh' + PageTemp[PageTemp.find(u'cmn')+len(u'cmn'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'nn':
							PageTemp = PageTemp[0:PageTemp.find(u'nn')] + u'no' + PageTemp[PageTemp.find(u'nn')+len(u'nn'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'per':
							PageTemp = PageTemp[0:PageTemp.find(u'per')] + u'fa' + PageTemp[PageTemp.find(u'per')+len(u'per'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'wel':
							PageTemp = PageTemp[0:PageTemp.find(u'wel')] + u'cy' + PageTemp[PageTemp.find(u'wel')+len(u'wel'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'zh-classical':
							PageTemp = PageTemp[0:PageTemp.find(u'zh-classical')] + u'lzh' + PageTemp[PageTemp.find(u'zh-classical')+len(u'zh-classical'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'ko-Hani':
							PageTemp = PageTemp[0:PageTemp.find(u'ko-Hani')] + u'ko' + PageTemp[PageTemp.find(u'ko-Hani')+len(u'ko-Hani'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'ko-hanja':
							PageTemp = PageTemp[0:PageTemp.find(u'ko-hanja')] + u'ko' + PageTemp[PageTemp.find(u'ko-hanja')+len(u'ko-hanja'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'zh-min-nan':
							PageTemp = PageTemp[0:PageTemp.find(u'zh-min-nan')] + u'nan' + PageTemp[PageTemp.find(u'zh-min-nan')+len(u'zh-min-nan'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'roa-rup':
							PageTemp = PageTemp[0:PageTemp.find(u'roa-rup')] + u'rup' + PageTemp[PageTemp.find(u'roa-rup')+len(u'roa-rup'):len(PageTemp)]
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'zh-yue':
							PageTemp = PageTemp[0:PageTemp.find(u'zh-yue')] + u'yue' + PageTemp[PageTemp.find(u'zh-yue')+len(u'zh-yue'):len(PageTemp)]
						'''	
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'gsw':
							PageTemp = PageTemp[0:PageTemp.find(u'gsw')] + u'als' + PageTemp[PageTemp.find(u'gsw')+len(u'gsw'):len(PageTemp)]
						'''
						
						# Bug du site fermé, ex : [[chat]]
						if PageTemp2[0:PageTemp2.find(u'|')] == u'mo': break
						
						# Identification des Wiktionnaires hébergeant les traductions
						SiteExt = u''
						PageExterne = u''
						PageTemp2 = PageTemp[position+1:len(PageTemp)]
						PageTemp3 = PageTemp2[PageTemp2.find(u'|')+1:len(PageTemp2)]
						if debogageLent: print u' langue distante : ' + PageTemp2[0:PageTemp2.find(u'|')]
						if PageTemp2[0:PageTemp2.find(u'|')] == "": break
						elif PageTemp3.find(u'}}') == "" or not PageTemp3.find(u'}}'):
							if debogageLent: print u'  aucun mot distant'
							if PageEnd.rfind('<!--') == -1 or PageEnd.rfind('<!--') < PageEnd.rfind('-->'):
								# On retire le modèle pour que la page ne soit plus en catégorie de maintenance
								if debogage: print u' Retrait de commentaire de traduction l 4362'
								PageEnd = PageEnd[:-2]
								PageTemp = PageTemp[PageTemp.find(u'}}')+2:]
							break
						elif PageTemp2[0:PageTemp2.find(u'|')] == u'conv':
							SiteExt = getSite('species', 'species') # Bug species depuis début 2011
						else:
							try:
								SiteExt = getSite(PageTemp2[0:PageTemp2.find(u'|')],family)
							except wikipedia.ServerError:
								PageEnd = PageEnd + PageTemp[0:4] + "--"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  ServerError'
								break
							except wikipedia.NoSuchSite:
								PageEnd = PageEnd + PageTemp[0:4] + "--"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  NoSuchSite'
								break
						if SiteExt != u'':
							if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}}'):
								PageExterne = PageTemp3[0:PageTemp3.find(u'|')]
							else:
								PageExterne = PageTemp3[0:PageTemp3.find(u'}}')]
						# Filtre du nom de la page externe
						if PageExterne != u'':
							if PageExterne.find(u'<') != -1:
								PageExterne = PageExterne[:PageExterne.find(u'<')]
						if debogageLent:
							print u' Page distante : '
							print PageExterne.encode(config.console_encoding, 'replace')
						
						# Connexions aux Wiktionnaires pour vérifier la présence de la page (sous-entendu dans sa langue maternelle)
						if SiteExt != u'' and PageExterne != u'':
							try:
								pageExt = Page(SiteExt,PageExterne)
							except wikipedia.NoPage:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  NoPage'
								break
							except wikipedia.BadTitle:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  BadTitle'
								break
							except wikipedia.InvalidTitle:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  InvalidTitle'
								break
							if pageExt.exists():
								PageEnd = PageEnd + PageTemp[0:4] + "+"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  exists'
								break
							else:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogageLent: print u'  not exists'
								break
						elif debogageLent:
							print u'  no site'
					elif Modele[p] == u'(':
						if trad == u'true':
							PageEnd = PageEnd + u'trad-début'
						else:
							PageEnd = PageEnd + u'('
						PageTemp = PageTemp[position:len(PageTemp)]
						break
					elif Modele[p] == u')':
						if trad == u'true':
							PageEnd = PageEnd + u'trad-fin'
						else:
							PageEnd = PageEnd + u')'
						PageTemp = PageTemp[position:len(PageTemp)]
						break
					elif Modele[p] == u'trad-début':
						if trad == u'true':
							PageEnd = PageEnd + u'trad-début'
						else:
							PageEnd = PageEnd + u'('
						PageTemp = PageTemp[position:len(PageTemp)]
						break
					elif Modele[p] == u'trad-fin':
						if trad == u'true':
							PageEnd = PageEnd + u'trad-fin'
						else:
							PageEnd = PageEnd + u')'
						PageTemp = PageTemp[position:len(PageTemp)]
						break
						
					elif Modele[p] == u'fr-verbe-flexion':
						if debogage: print u'Flexion de verbe'
						Infinitif = PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')]
						if Infinitif == u'verbe':
							PageTemp = PageTemp[0:PageTemp.find(u'[[verbe]]')] + u'verbe' + PageTemp[PageTemp.find(u'[[verbe]]')+len(u'[[verbe]]'):len(PageTemp)]
							Infinitif = PageTemp[PageTemp.find(u'[[')+2:PageTemp.find(u']]')]
						if Infinitif.find(u'|') != -1: Infinitif = Infinitif[Infinitif.find(u'|')+1:len(Infinitif)]
						try:
							page2 = Page(site,Infinitif)
							Page2 = page2.get()
						except wikipedia.NoPage:
							if debogage: print "NoPage flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
							break
						except wikipedia.SectionError:
							if debogage: print "SectionError flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
							break
						except wikipedia.IsRedirectPage:
							if debogage: print "Redirect page flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
							break
						# http://fr.wiktionary.org/w/index.php?title=Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet
						PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
						if PageTemp2.find(u'flexion=') != -1 and PageTemp2.find(u'flexion=') < PageTemp2.find(u'}}'):
							PageTemp3 = PageTemp2[PageTemp2.find(u'flexion='):len(PageTemp2)]
							if PageTemp3.find(u'|') != -1 and PageTemp3.find(u'|') < PageTemp3.find(u'}'):
								PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')+PageTemp2.find(u'flexion=')+PageTemp3.find(u'|'):len(PageTemp)]
						PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
						if PageTemp2.find(Infinitif) == -1 or PageTemp2.find(Infinitif) > PageTemp2.find(u'}}'):
							PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|' + Infinitif + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
							if PageTemp.find(u'|' + Infinitif + u'\n') != -1:	# Bug de l'hyperlien vers l'annexe
								PageTemp = PageTemp[0:PageTemp.find(u'|' + Infinitif + u'\n')+len(u'|' + Infinitif)] + PageTemp[PageTemp.find(u'|' + Infinitif + u'\n')+len(u'|' + Infinitif + u'\n'):len(PageTemp)]
						# Analyse du modèle en cours
						PageTemp2 = PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
						PageTemp2 = PageTemp2[0:PageTemp2.find(u'}}')+2]
						if PageTemp2.find(u'impers=oui') == -1:
							# http://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:fr-verbe-flexion&action=edit
							if Page2.find(u'{{impers') != -1 and Infinitif != u'être':
								PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|impers=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
							elif (Page2.find(u'|groupe=1') != -1 or Page2.find(u'|grp=1') != -1) and Page2.find(u'|groupe2=') == -1:
								# je
								if PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									break
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|sub.p.3s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|imp.p.2s=oui|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|sub.p.3s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|sub.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.3s=oui|sub.p.1s=oui|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# tu
								if PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'sub.p.2s=oui') != -1:
									break
								elif PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'sub.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|sub.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'sub.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# nous
								if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
									break
								if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + PageTemp[PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.i.1p=oui') == -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# vous
								if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
									break
								if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + PageTemp[PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.i.2p=oui') == -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# ils
								if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
									break
								if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + PageTemp[PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.p.3p=oui') == -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
							# Certains -ir sont du 3ème
							elif (Page2.find(u'|groupe=2') != -1 or Page2.find(u'|grp=2') != -1) and Page2.find(u'{{impers') == -1 and Page2.find(u'|groupe2=') == -1:
								# je
								if PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									break
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui')] + u'|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.2s=oui')+len(u'ind.ps.2s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') != -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') != -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui')] + u'|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.ps.1s=oui')+len(u'ind.ps.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.1s=oui|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]

								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') != -1 and PageTemp2.find(u'ind.p.2s=oui') == -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui')] + u'|ind.p.2s=oui|ind.ps.1s=oui|ind.ps.2s=oui' + PageTemp[PageTemp.find(u'ind.p.1s=oui')+len(u'ind.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'ind.p.1s=oui') == -1 and PageTemp2.find(u'ind.p.2s=oui') != -1 and PageTemp2.find(u'ind.ps.1s=oui') == -1 and PageTemp2.find(u'ind.ps.2s=oui') == -1 and PageTemp2.find(u'imp.p.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui')] + u'|ind.p.1s=oui|ind.ps.1s=oui|ind.ps.2s=oui|imp.p.2s=oui' + PageTemp[PageTemp.find(u'ind.p.2s=oui')+len(u'ind.p.2s=oui'):len(PageTemp)]

								#...
								if PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
									break
								elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui')] + u'|sub.i.1s=oui' + PageTemp[PageTemp.find(u'sub.p.3s=oui')+len(u'sub.p.3s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui' + PageTemp[PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'sub.p.1s=oui') != -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui')] + u'|sub.p.3s=oui|sub.i.1s=oui' + PageTemp[PageTemp.find(u'sub.p.1s=oui')+len(u'sub.p.1s=oui'):len(PageTemp)]
								elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') == -1 and PageTemp2.find(u'sub.i.1s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								elif PageTemp2.find(u'sub.p.1s=oui') == -1 and PageTemp2.find(u'sub.p.3s=oui') != -1 and PageTemp2.find(u'sub.i.1s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.1s=oui|sub.i.1s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# tu
								if PageTemp2.find(u'sub.p.2s=oui') != -1 and PageTemp2.find(u'sub.i.2s=oui') != -1:
									break
								if PageTemp2.find(u'sub.p.2s=oui') != -1 and PageTemp2.find(u'sub.i.2s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui')] + u'|sub.i.2s=oui' + PageTemp[PageTemp.find(u'sub.p.2s=oui')+len(u'sub.p.2s=oui'):len(PageTemp)]
								if PageTemp2.find(u'sub.p.2s=oui') == -1 and PageTemp2.find(u'sub.i.2s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|sub.p.2s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# il
								if PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'ind.ps.3s=oui') != -1:
									break
								if PageTemp2.find(u'ind.p.3s=oui') != -1 and PageTemp2.find(u'ind.ps.3s=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui')] + u'|ind.ps.3s=oui' + PageTemp[PageTemp.find(u'ind.p.3s=oui')+len(u'ind.p.3s=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.p.3s=oui') == -1 and PageTemp2.find(u'ind.ps.3s=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# nous
								if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
									break
								if PageTemp2.find(u'ind.i.1p=oui') != -1 and PageTemp2.find(u'sub.p.1p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui')] + u'|sub.p.1p=oui' + PageTemp[PageTemp.find(u'ind.i.1p=oui')+len(u'ind.i.1p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.i.1p=oui') == -1 and PageTemp2.find(u'sub.p.1p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.1p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# vous
								if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
									break
								if PageTemp2.find(u'ind.i.2p=oui') != -1 and PageTemp2.find(u'sub.p.2p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui')] + u'|sub.p.2p=oui' + PageTemp[PageTemp.find(u'ind.i.2p=oui')+len(u'ind.i.2p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.i.2p=oui') == -1 and PageTemp2.find(u'sub.p.2p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.i.2p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
								# ils
								if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
									break
								if PageTemp2.find(u'ind.p.3p=oui') != -1 and PageTemp2.find(u'sub.p.3p=oui') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui')] + u'|sub.p.3p=oui' + PageTemp[PageTemp.find(u'ind.p.3p=oui')+len(u'ind.p.3p=oui'):len(PageTemp)]
								if PageTemp2.find(u'ind.p.3p=oui') == -1 and PageTemp2.find(u'sub.p.3p=oui') != -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.p.3p=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
							elif (Page2.find(u'|groupe=3') != -1 or Page2.find(u'|grp=3') != -1) and Page2.find(u'|groupe2=') == -1:
								if PageTemp2.find(u'grp=3') == -1:
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|grp=3' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
						
						PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'\n')+1]
						PageTemp = PageTemp[PageTemp.find(u'\n')+1:len(PageTemp)]
						break
					
					if p < limit2:
						if Modele[p] != u'S': print 'Erreur de titre section pour ' + Modele[p].encode(config.console_encoding, 'replace')
						TitreSection = PageTemp[position+1:]
						#raw_input(TitreSection.encode(config.console_encoding, 'replace'))
						if TitreSection.find(u'|') < TitreSection.find(u'}') and TitreSection.find(u'|') != -1:
							TitreSection = trim(TitreSection[:TitreSection.find(u'|')])
						else:
							TitreSection = trim(TitreSection[:TitreSection.find(u'}')])

						if debogage: print TitreSection.encode(config.console_encoding, 'replace')
						try:
							Index = Section.index(TitreSection)
						except ValueError:
							if debogage: print u'Section introuvable : ' + TitreSection
							return
						if Index < limit1:
							# Paragraphe définition
							EstCodeLangue = "true"
							trad = u'false'
							# Ajouts en fin de ligne de forme (ex : traitement de Genres_manquants_en_français)
							''' bugs
								https://fr.wiktionary.org/w/index.php?title=nulle&diff=next&oldid=19819870
								https://fr.wiktionary.org/w/index.php?title=protectrice&type=revision&diff=19820554&oldid=19260710
								https://fr.wiktionary.org/w/index.php?title=ma%C3%AForale&type=revision&diff=19820545&oldid=16796920
							if (TitreSection == 'nom' or TitreSection == 'adjectif') and (codelangue == 'fr' or codelangue == 'en' or codelangue == 'es' or codelangue == 'pt' or codelangue == 'it' or codelangue == 'ar' or codelangue == 'ru' or codelangue == 'bg'):	# or codelangue == 'de' : déplacer les {{de-tab-cas qui sont sous la ligne de forme 
								
								if debogage: print u'Recherche du pluriel manquant'
								NombreManquant = True
								if PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'') != -1 and PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'') < 100:
									PageTemp2 = PageTemp[PageTemp.find(u'\n')+1:]
									if PageTemp2.find(u'{{' + codelangue + u'-') > PageTemp2.find(u'\n') or PageTemp2.find(u'{{' + codelangue + u'-') == -1:
										PageTemp2 = PageTemp[PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\''):]
										
										for n in range(0,len(Nombre)):
											if PageTemp2.find(u'{{'+Nombre[n]+u'|') != -1 or PageTemp2.find(u'{{'+Nombre[n]+u'}') != -1 or PageTemp.find(u'|'+Nombre[n]+u'=1') != -1:
												if debogageLent: print u' '+Nombre[n]+u' trouvé'
												NombreManquant = False
											else:
												if debogageLent: print u' '+Nombre[n]+u' non trouvé'
												# [[Wiktionnaire:Flexions]]
												if PageTemp2.find(u'Pluriel d') != -1:
													if debogage: print u' "Pluriel d" trouvé'
													NombreManquant = False
												elif debogageLent:
													print u' "Pluriel d" non trouvé'
												
										if NombreManquant == True:
											PageTemp = PageTemp[:PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\'')+PageTemp2.find(u'\n')] + u' {{pluriel ?|' + codelangue + u'}}' + PageTemp[PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\'')+PageTemp2.find(u'\n'):]
											if summary.find(u'pluriel manquant') == -1: summary = summary + u', pluriel manquant'

								if TitreSection == 'nom' and codelangue != u'en':	# pb pour les adjectifs https://fr.wiktionary.org/w/index.php?title=ma%C3%AFs&curid=9466&diff=19817873&oldid=19282563
									if debogage: print u'Recherche du genre manquant'
									GenreManquant = True
									if PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'') != -1 and PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'') < 100:
										PageTemp2 = PageTemp[PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\''):]
										for n in range(0,len(Genre)): 
											if PageTemp2.find(u'{{' + Genre[n] + u'|') != -1 or PageTemp2.find(u'{{' + Genre[n] + u'}}') != -1 or PageTemp.find(u'|' + Genre[n] + u'=1') != -1:
												if debogage: print u' ' + Genre[n] + u' trouvé'
												GenreManquant = False
										if GenreManquant == True:
											PageTemp = PageTemp[:PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\'')+PageTemp2.find(u'\n')] + u' {{genre|' + codelangue + u'}}' + PageTemp[PageTemp.find(u'\n\'\'\'' + PageC + u'\'\'\'')+len(u'\n\'\'\'' + PageC + u'\'\'\'')+PageTemp2.find(u'\n'):]
											if summary.find(u'genre') == -1: summary = summary + u', genre manquant'
								
								# Remplacement post-recherche
								for n in range(0,2):
									G = [[0] * (2+1) for _ in range(3+1)]
									G[0][0] = u'Masculin'
									G[0][1] = u'm'
									G[1][0] = u'Féminin'
									G[1][1] = u'f'
									G[2][0] = u'Neutre'
									G[2][1] = u'n'
									for g in range(0,2):
										PageTemp = PageTemp.replace(u'{{'+Nombre[n]+u'|'+codelangue+u'}} {{genre|'+codelangue+u'}}\n# \'\''+G[g][0]+u' pluriel', u'{{'+G[g][1]+u'}}\n# \'\'Pluriel')
										PageTemp = PageTemp.replace(u'{{genre|'+codelangue+u'}} {{'+Nombre[n]+u'|'+codelangue+u'}}\n# \'\''+G[g][0]+u' pluriel', u'{{'+G[g][1]+u'}}\n# \'\'Pluriel')
										PageTemp = PageTemp.replace(u'{{'+Nombre[n]+u'|'+codelangue+u'}} {{genre|'+codelangue+u'}}\n# \'\''+G[g][0]+u' singulier', u'{{'+G[g][1]+u'}}\n# \'\'Singulier')
										PageTemp = PageTemp.replace(u'{{genre|'+codelangue+u'}} {{'+Nombre[n]+u'|'+codelangue+u'}}\n# \'\''+G[g][0]+u' singulier', u'{{'+G[g][1]+u'}}\n# \'\'Singulier')
										
										PageTemp = PageTemp.replace(u'{{'+G[g][1]+u"plur}}\n# ''C’est la forme ", u'{{'+G[g][1]+u"}} {{p}}\n# ''Forme ")
										PageTemp = PageTemp.replace(u'{{'+G[g][1]+u"sing}}\n# ''C’est la forme ", u'{{'+G[g][1]+u"}} {{s}}\n# ''Forme ")
										PageTemp = PageTemp.replace(u'le {{p}}', u'le pluriel')
										
										if TitreSection == 'nom':
											try:
												regex = ur'{{'+Nombre[n]+ur'\|'+codelangue+ur'}}\n# \'\''+G[g][0]+ur' pluriel'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Pluriel" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
											try:	
												regex = ur'{{'+Nombre[n]+ur'\|'+codelangue+ur'}}\n# \'\''+G[g][0]+u' singulier'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Singulier" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
											try:
												regex = ur'{{'+G[g][1]+ur'plur}}\n# \'\''+G[g][0]+ur' pluriel'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Pluriel" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
											try:
												regex = ur'{{'+G[g][1]+ur'sing}}\n# \'\''+G[g][0]+ur' singulier'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Singulier" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
											try:
												regex = ur'{{'+G[g][1]+ur'plur}}\n# \'\'Pluriel'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Pluriel" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
											try:
												regex = ur'{{'+G[g][1]+ur'sing}}\n# \'\'Singulier'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u'{{'+G[g][1]+u"}}\n# ''Singulier" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4731'
										elif TitreSection == 'adjectif':
											try:
												regex = ur'{{'+G[g][1]+ur'plur}}\n# \'\'Pluriel'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u"\n# ''Pluriel" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4751'
											try:	
												regex = ur'{{'+G[g][1]+ur'sing}}\n# \'\'Singulier'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + u"\n# ''Singulier" + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4756'
											try:	
												regex = ur'({{invar[^}]*}}) {{genre\|[^}]*}}'
												PageTemp = PageTemp[:re.search(regex, PageTemp).start()] + ur'\1' + PageTemp[re.search(regex, PageTemp).end():]
											except:
												if debogage: print 'erreur l 4761'
										# Retrait des modèles de maintenance
										PageTemp = PageTemp.replace(u'{{'+G[g][1]+u'sing}} {{pluriel ?|' + codelangue + u'}}', u'{{'+G[g][1]+u'plur}}')
										PageTemp = PageTemp.replace(u'{{'+G[g][1]+u'plur}} {{pluriel ?|' + codelangue + u'}}', u'{{'+G[g][1]+u'plur}}')
										regex = ur'({{p}}[^\n]*) ?{{pluriel \?\|' + codelangue + u'}}'
										if re.search(regex, PageTemp):
											PageTemp = re.sub(regex, ur'\1', PageTemp)
										regex = ur'({{invari?a?b?l?e?}}[^\n]*) ?{{pluriel \?\|' + codelangue + u'}}'
										if re.search(regex, PageTemp):
											PageTemp = re.sub(regex, ur'\1', PageTemp)
							'''	
							#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
							regex = ur'{{pluriel \?\|' + codelangue + u'}}(\n# ?\'*Pluriel)'
							if re.search(regex, PageTemp):
								PageTemp = re.sub(regex, ur'\1', PageTemp)
							
						else:
							# Paragraphe sans code langue
							EstCodeLangue = "false"
							if TitreSection == 'traductions':
								trad = u'true'
								# Ajout de {{trad-début}} si {{T| en français (pas {{L| car certains les trient par famille de langue)
								if PageTemp.find(u'{{') == PageTemp.find(u'{{T|') and codelangue == 'fr':
									PageTemp = PageTemp[:PageTemp.find(u'\n')] + u'\n{{trad-début}}' + PageTemp[PageTemp.find(u'\n'):]
									PageTemp2 = PageTemp[PageTemp.find(u'{{trad-début}}\n')+len(u'{{trad-début}}\n'):]
									if PageTemp2.find(u'\n') == -1:
										PageTemp = PageTemp + u'\n'
										PageTemp2 = PageTemp2 + u'\n'
									while PageTemp2.find(u'{{T|') < PageTemp2.find(u'\n') and PageTemp2.find(u'{{T|') != -1:
										PageTemp2 = PageTemp2[PageTemp2.find(u'\n')+1:]
									PageTemp = PageTemp[:len(PageTemp)-len(PageTemp2)] + u'{{trad-fin}}\n' + PageTemp[len(PageTemp)-len(PageTemp2):]
							elif TitreSection == u'traductions à trier':
								trad = u'true'
							else:
								trad = u'false'
						
						if debogage: print " EstCodeLangue = " + EstCodeLangue
						# Tous ces modèles peuvent facultativement contenir |clé= et |num=, et |genre= pour les prénoms
						if ((p < limit1 and p > 0) or (p == 0 and Section.index(TitreSection) < limit1)) and (PageTemp.find(u'|clé=') == -1 or PageTemp.find(u'|clé=') > PageTemp.find(u'}}')):
							if debogageLent: print u'  ' + str(p)
							if debogageLent: print u'  ' + str(Section.index(TitreSection))
							if debogageLent: print PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
							TitreTemp = PageC
							if codelangue == u'es':
								if TitreTemp.find(u'ñ') !=-1: TitreTemp = TitreTemp.replace(u'ñ',u'n€')
								if TitreTemp.find(u'ñ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ñ'.upper(),u'n€')
							
							elif codelangue == u'fi':
								if TitreTemp.find(u'å') !=-1: TitreTemp = TitreTemp.replace(u'å',u'z€')
								if TitreTemp.find(u'å'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'å'.upper(),u'z€')
								if TitreTemp.find(u'ä') !=-1: TitreTemp = TitreTemp.replace(u'ä',u'z€€')
								if TitreTemp.find(u'ä'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ä'.upper(),u'z€€')
								if TitreTemp.find(u'ö') !=-1: TitreTemp = TitreTemp.replace(u'ö',u'z€€€')
								if TitreTemp.find(u'ö'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ö'.upper(),u'z€€€')
								
							elif codelangue == u'os':
								if TitreTemp.find(u'ё') !=-1: TitreTemp = TitreTemp.replace(u'ё',u'е€')
								if TitreTemp.find(u'ё'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ё'.upper(),u'е€')
								if TitreTemp.find(u'ӕ') !=-1: TitreTemp = TitreTemp.replace(u'ӕ',u'а€')
								if TitreTemp.find(u'ӕ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ӕ'.upper(),u'а€')
								# Digrammes
								if TitreTemp.find(u'гъ') !=-1: TitreTemp = TitreTemp.replace(u'гъ',u'г€')
								if TitreTemp.find(u'дж') !=-1: TitreTemp = TitreTemp.replace(u'дж',u'д€')
								if TitreTemp.find(u'дз') !=-1: TitreTemp = TitreTemp.replace(u'дз',u'д€€')
								if TitreTemp.find(u'къ') !=-1: TitreTemp = TitreTemp.replace(u'къ',u'к€')
								if TitreTemp.find(u'пъ') !=-1: TitreTemp = TitreTemp.replace(u'пъ',u'п€')
								if TitreTemp.find(u'тъ') !=-1: TitreTemp = TitreTemp.replace(u'тъ',u'т€')
								if TitreTemp.find(u'хъ') !=-1: TitreTemp = TitreTemp.replace(u'хъ',u'х€')
								if TitreTemp.find(u'цъ') !=-1: TitreTemp = TitreTemp.replace(u'цъ',u'ц€')
								if TitreTemp.find(u'чъ') !=-1: TitreTemp = TitreTemp.replace(u'чъ',u'ч€')
								
							elif codelangue == u'ru':
								#if TitreTemp.find(u'ё') !=-1: TitreTemp = TitreTemp.replace(u'ё',u'е€')
								#if TitreTemp.find(u'ё'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ё'.upper(),u'е€')
								if TitreTemp.find(u'ӕ') !=-1: TitreTemp = TitreTemp.replace(u'ӕ',u'а€')
								if TitreTemp.find(u'ӕ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ӕ'.upper(),u'а€')
								
							if codelangue == u'sl':
								if TitreTemp.find(u'č') !=-1: TitreTemp = TitreTemp.replace(u'č',u'c€')
								if TitreTemp.find(u'č'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'č'.upper(),u'c€')
								if TitreTemp.find(u'š') !=-1: TitreTemp = TitreTemp.replace(u'š',u's€')
								if TitreTemp.find(u'š'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'š'.upper(),u's€')
								if TitreTemp.find(u'ž') !=-1: TitreTemp = TitreTemp.replace(u'ž',u'z€')
								if TitreTemp.find(u'ž'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ž'.upper(),u'z€')
								
							elif codelangue == u'sv':
								if TitreTemp.find(u'å') !=-1: TitreTemp = TitreTemp.replace(u'å',u'z€')	
								if TitreTemp.find(u'å'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'å'.upper(),u'z€')
								if TitreTemp.find(u'ä') !=-1: TitreTemp = TitreTemp.replace(u'ä',u'z€€')	
								if TitreTemp.find(u'ä'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ä'.upper(),u'z€€')	
								if TitreTemp.find(u'ö') !=-1: TitreTemp = TitreTemp.replace(u'ö',u'z€€€')	
								if TitreTemp.find(u'ö'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ö'.upper(),u'z€€€')
								
							elif codelangue == u'vi':
								if TitreTemp.find(u'ả') !=-1: TitreTemp = TitreTemp.replace(u'ả',u'a€')	
								if TitreTemp.find(u'ả'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ả'.upper(),u'a')
								if TitreTemp.find(u'ă') !=-1: TitreTemp = TitreTemp.replace(u'ă',u'a€')	
								if TitreTemp.find(u'ă'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ă'.upper(),u'a€')
								if TitreTemp.find(u'ắ') !=-1: TitreTemp = TitreTemp.replace(u'ắ',u'a€')	
								if TitreTemp.find(u'ắ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ắ'.upper(),u'a€')
								if TitreTemp.find(u'ặ') !=-1: TitreTemp = TitreTemp.replace(u'ặ',u'a€')	
								if TitreTemp.find(u'ặ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ặ'.upper(),u'a€')
								if TitreTemp.find(u'ẳ') !=-1: TitreTemp = TitreTemp.replace(u'ẳ',u'a€')	
								if TitreTemp.find(u'ẳ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ẳ'.upper(),u'a€')
								if TitreTemp.find(u'ằ') !=-1: TitreTemp = TitreTemp.replace(u'ằ',u'a€')	
								if TitreTemp.find(u'ằ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ằ'.upper(),u'a€')
								if TitreTemp.find(u'â') !=-1: TitreTemp = TitreTemp.replace(u'â',u'a€€')	
								if TitreTemp.find(u'â'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'â'.upper(),u'a€€')
								if TitreTemp.find(u'ầ') !=-1: TitreTemp = TitreTemp.replace(u'ầ',u'a€€')	
								if TitreTemp.find(u'ầ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ầ'.upper(),u'a€€')
								if TitreTemp.find(u'ậ') !=-1: TitreTemp = TitreTemp.replace(u'ậ',u'a€€')	
								if TitreTemp.find(u'ậ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ậ'.upper(),u'a€€')
								if TitreTemp.find(u'ấ') !=-1: TitreTemp = TitreTemp.replace(u'ấ',u'a€€')	
								if TitreTemp.find(u'ấ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ấ'.upper(),u'a€€')
								if TitreTemp.find(u'ẩ') !=-1: TitreTemp = TitreTemp.replace(u'ẩ',u'a€€')	
								if TitreTemp.find(u'ẩ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ẩ'.upper(),u'a€€')
								if TitreTemp.find(u'đ') !=-1: TitreTemp = TitreTemp.replace(u'đ',u'd€')	
								if TitreTemp.find(u'đ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'đ'.upper(),u'd€')
								if TitreTemp.find(u'ẹ') !=-1: TitreTemp = TitreTemp.replace(u'ẹ',u'e')	
								if TitreTemp.find(u'ẹ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ẹ'.upper(),u'e')
								if TitreTemp.find(u'ê') !=-1: TitreTemp = TitreTemp.replace(u'ê',u'e€')	
								if TitreTemp.find(u'ê'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ê'.upper(),u'e€')
								if TitreTemp.find(u'ệ') !=-1: TitreTemp = TitreTemp.replace(u'ệ',u'e€')	
								if TitreTemp.find(u'ệ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ệ'.upper(),u'e€')
								if TitreTemp.find(u'ễ') !=-1: TitreTemp = TitreTemp.replace(u'ễ',u'e€')	
								if TitreTemp.find(u'ễ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ễ'.upper(),u'e€')
								if TitreTemp.find(u'ề') !=-1: TitreTemp = TitreTemp.replace(u'ề',u'e€')	
								if TitreTemp.find(u'ề'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ề'.upper(),u'e€')
								if TitreTemp.find(u'ể') !=-1: TitreTemp = TitreTemp.replace(u'ể',u'e€')	
								if TitreTemp.find(u'ể'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ể'.upper(),u'e€')
								if TitreTemp.find(u'ị') !=-1: TitreTemp = TitreTemp.replace(u'ị',u'i')	
								if TitreTemp.find(u'ị'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ị'.upper(),u'i')
								if TitreTemp.find(u'ì') !=-1: TitreTemp = TitreTemp.replace(u'ì',u'i')	
								if TitreTemp.find(u'ì'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ì'.upper(),u'i')
								if TitreTemp.find(u'í') !=-1: TitreTemp = TitreTemp.replace(u'í',u'i')	
								if TitreTemp.find(u'í'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'í'.upper(),u'i')
								if TitreTemp.find(u'ỉ') !=-1: TitreTemp = TitreTemp.replace(u'ỉ',u'i')	
								if TitreTemp.find(u'ỉ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ỉ'.upper(),u'i')
								if TitreTemp.find(u'î') !=-1: TitreTemp = TitreTemp.replace(u'î',u'i')	
								if TitreTemp.find(u'î'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'î'.upper(),u'i')
								if TitreTemp.find(u'ĩ') !=-1: TitreTemp = TitreTemp.replace(u'ĩ',u'i')	
								if TitreTemp.find(u'ĩ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ĩ'.upper(),u'i')
								if TitreTemp.find(u'ọ') !=-1: TitreTemp = TitreTemp.replace(u'ọ',u'o')	
								if TitreTemp.find(u'ọ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ọ'.upper(),u'o')
								if TitreTemp.find(u'ỏ') !=-1: TitreTemp = TitreTemp.replace(u'ỏ',u'o')	
								if TitreTemp.find(u'ỏ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ỏ'.upper(),u'o')
								if TitreTemp.find(u'ô') !=-1: TitreTemp = TitreTemp.replace(u'ô',u'o€')	
								if TitreTemp.find(u'ô'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ô'.upper(),u'o€')
								if TitreTemp.find(u'ơ') !=-1: TitreTemp = TitreTemp.replace(u'ơ',u'o€€')	
								if TitreTemp.find(u'ơ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ơ'.upper(),u'o€€')
								if TitreTemp.find(u'ộ') !=-1: TitreTemp = TitreTemp.replace(u'ộ',u'o€')	
								if TitreTemp.find(u'ộ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ộ'.upper(),u'o€')
								if TitreTemp.find(u'ố') !=-1: TitreTemp = TitreTemp.replace(u'ố',u'o€')	
								if TitreTemp.find(u'ố'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ố'.upper(),u'o€')
								if TitreTemp.find(u'ồ') !=-1: TitreTemp = TitreTemp.replace(u'ồ',u'o€')	
								if TitreTemp.find(u'ồ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ồ'.upper(),u'o€')
								if TitreTemp.find(u'ổ') !=-1: TitreTemp = TitreTemp.replace(u'ổ',u'o€')	
								if TitreTemp.find(u'ổ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ổ'.upper(),u'o€')
								if TitreTemp.find(u'ỗ') !=-1: TitreTemp = TitreTemp.replace(u'ỗ',u'o€')	
								if TitreTemp.find(u'ỗ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ỗ'.upper(),u'o€')
								if TitreTemp.find(u'ỡ') !=-1: TitreTemp = TitreTemp.replace(u'ỡ',u'o€€')	
								if TitreTemp.find(u'ỡ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ỡ'.upper(),u'o€€')
								if TitreTemp.find(u'ở') !=-1: TitreTemp = TitreTemp.replace(u'ở',u'o€€')	
								if TitreTemp.find(u'ở'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ở'.upper(),u'o€€')
								if TitreTemp.find(u'ớ') !=-1: TitreTemp = TitreTemp.replace(u'ớ',u'o€€')	
								if TitreTemp.find(u'ớ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ớ'.upper(),u'o€€')
								if TitreTemp.find(u'ờ') !=-1: TitreTemp = TitreTemp.replace(u'ờ',u'o€€')	
								if TitreTemp.find(u'ờ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ờ'.upper(),u'o€€')
								if TitreTemp.find(u'ụ') !=-1: TitreTemp = TitreTemp.replace(u'ụ',u'u')	
								if TitreTemp.find(u'ụ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ụ'.upper(),u'u')
								if TitreTemp.find(u'ủ') !=-1: TitreTemp = TitreTemp.replace(u'ủ',u'u')	
								if TitreTemp.find(u'ủ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ủ'.upper(),u'u')
								if TitreTemp.find(u'ư') !=-1: TitreTemp = TitreTemp.replace(u'ư',u'u€')	
								if TitreTemp.find(u'ư'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ư'.upper(),u'u€')
								if TitreTemp.find(u'ử') !=-1: TitreTemp = TitreTemp.replace(u'ử',u'u€')	
								if TitreTemp.find(u'ử'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ử'.upper(),u'u€')
								if TitreTemp.find(u'ự') !=-1: TitreTemp = TitreTemp.replace(u'ự',u'u€')	
								if TitreTemp.find(u'ự'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ự'.upper(),u'u€')
								if TitreTemp.find(u'ừ') !=-1: TitreTemp = TitreTemp.replace(u'ừ',u'u€')	
								if TitreTemp.find(u'ừ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ừ'.upper(),u'u€')
								if TitreTemp.find(u'ữ') !=-1: TitreTemp = TitreTemp.replace(u'ữ',u'u€')	
								if TitreTemp.find(u'ữ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ữ'.upper(),u'u€')
								
							if TitreTemp != PageC:
								TitreTemp = CleDeTri.CleDeTri(TitreTemp)
								PageTemp = PageTemp[0:PageTemp.find(u'}}')] + u'|clé=' + TitreTemp + PageTemp[PageTemp.find(u'}}'):len(PageTemp)]
						elif codelangue == u'ru':
							while PageTemp.find(u'е€') < PageTemp.find(u'}}') and PageTemp.find(u'е€') != -1:
								PageTemp = PageTemp[:PageTemp.find(u'е€')+1] + PageTemp[PageTemp.find(u'е€')+2:]
						elif (p > limit1 or (p == 0 and Section.index(TitreSection) > limit1)) and PageTemp.find(u'|clé=') != -1 and PageTemp.find(u'|clé=') < PageTemp.find(u'}}'):
							PageTemp = PageTemp[:PageTemp.find(u'|clé=')] + PageTemp[PageTemp.find(u'}}'):]
						elif debogageLent:
							raw_input(PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace'))
						break
						#PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
						#PageTemp = PageTemp[PageTemp.find(u'}}')+2:]
						#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
					
					elif p < limit25:	# Paragraphe sans code langue contenant un texte
						if debogage: print "limit25"
						EstCodeLangue = "false"
						if debogage: print " EstCodeLangue = " + EstCodeLangue
						#trad = u'false'
						if PageTemp.find(u'}}') > PageTemp.find(u'{{') and PageTemp.find(u'{{') != -1:
							PageTemp2 = PageTemp[PageTemp.find(u'}}')+2:len(PageTemp)]
							PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2+PageTemp2.find(u'}}')+2]
							PageTemp = PageTemp[PageTemp.find(u'}}')+2+PageTemp2.find(u'}}')+2:len(PageTemp)]
							break
						else:
							PageEnd = PageEnd + PageTemp[0:PageTemp.find(u'}}')+2]
					elif p < limit3:
						if debogage: print "limit3"
						if debogage: print u'Modèle sans paramètre'
						PageEnd = PageEnd + PageTemp[0:position] + "}}"
					elif p < limit4:
						if debogage: print "limit4"
						if debogage: print u'Paragraphe potentiellement avec code langue, voire |spéc='
						if PageTemp[:PageTemp.find(u'}}')].find(u'spéc') == -1:
							if EstCodeLangue == "true":
								if debogage: print u' avec'
								PageEnd = PageEnd + PageTemp[:position] + "|" + codelangue + "}}"
							else:
								if debogage: print u' sans'
								PageEnd = PageEnd + PageTemp[:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
							
					elif p < limit5:
						if debogage: print "limit5"
						if debogage: print u' Catégorisée quel que soit EstCodeLangue (ex : ébauches)'
						if codelangue:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						elif Modele[p] == u'ébauche' and PageTemp.find(u'== {{langue') !=-1:
							PageTemp2 = PageTemp[PageTemp.find(u'== {{langue'):]
							PageTemp = PageTemp[PageTemp.find(u'}}')+2:PageTemp.find(u'== {{langue')+PageTemp2.find(u'\n')+1] + u'{{ébauche}}\n' + PageTemp[PageTemp.find(u'== {{langue')+PageTemp2.find(u'\n')+1:]
							PageEnd = PageEnd[:-2]
							break
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
					else:
						if debogage: print u'Paragraphe régional : non catégorisé dans la prononciation'
						if debogageLent: 
							print (PageEnd.encode(config.console_encoding, 'replace')[0:1000])
							raw_input (PageTemp.encode(config.console_encoding, 'replace'))
						if PageEnd.rfind(u'{{') != -1:
							PageEnd2 = PageEnd[0:PageEnd.rfind(u'{{')]
							if EstCodeLangue == "true" and ((PageEnd2.rfind(u'{{') != PageEnd2.rfind(u'{{pron|') and PageEnd2.rfind(u'{{') != PageEnd2.rfind(u'{{US|') and PageEnd2.rfind(u'{{') != PageEnd2.rfind(u'{{UK|')) or PageEnd.rfind(u'{{pron|') < PageEnd.rfind(u'\n') or PageEnd2.rfind(u'{{pron|') == -1) and ((PageTemp.find(u'{{') != PageTemp.find(u'{{pron|') or PageTemp.find(u'{{pron|') > PageTemp.find(u'\n')) or PageTemp.find(u'{{pron|') == -1):
								PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
							else:
								PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
					if position == PageTemp.find("|"):
						position = PageTemp.find("}}")
					PageTemp = PageTemp[position+2:]

				p=p+1
		PageEnd = PageEnd + PageTemp
		
		# Maintenance des genres
		PageEnd = PageEnd.replace(u'{{genre|fr}}\n# Masculin ', u'{{m}}\n# Masculin ')
		PageEnd = PageEnd.replace(u'{{genre|fr}}\n# Féminin ', u'{{f}}\n# Féminin ')
		PageEnd = PageEnd.replace(u"{{genre|fr}}\n# ''Masculin ", u"{{m}}\n# ''Masculin ")
		PageEnd = PageEnd.replace(u"{{genre|fr}}\n# ''Féminin ", u"{{f}}\n# ''Féminin ")
		if PageC[-3:] == u'eur':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-3:] == u'eux':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'euse':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'ant':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'ante':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-4:] == u'ance':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'age':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'ette':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'ier':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-3:] == u'ien':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-5:] == u'ienne':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'rie':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'ois':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'oise':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'ais':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'aise':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-5:] == u'logie':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-4:] == u'tion':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-3:] == u'ité':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-4:] == u'isme':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-2:] == u'el':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'elle':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-2:] == u'if':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-3:] == u'ive':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{f}}")
		if PageC[-4:] == u'ment':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-5:] == u'ments':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		if PageC[-4:] == u'iste':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{mf}}")
		if PageC[-4:] == u'aire':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{mf}}")
		if PageC[-1:] == u'é':
			PageEnd = PageEnd.replace(u"{{genre|fr}}", u"{{m}}")
		
		if debogage: print u'Genre manquant de locution'
		if PageC.find(u' ') != -1 and PageC.find(u'{{langue|fr}}') != -1:
			PageLemme = u''
			page2 = Page(site,PageC[:PageC.find(u' ')])
			if page2.exists():
				if page.namespace() !=0:
					if debogage: print u'Page non traitée l 4785'
					return
				else:
					try:
						PageLemme = page2.get()
					except wikipedia.NoPage:
						if debogage: print "NoPage l 4791"
					except wikipedia.IsRedirectPage: 
						if debogage: print "IsRedirect l 4793"
			else:
				if debogage: print "NoPage l 4795"
			if PageLemme != u'':
				genre = u''
				if PageLemme.find(u'|fr}} {{m}}') != -1:
					genre = u'{{m}}'
				elif PageLemme.find(u'|fr}} {{f}}') != -1:
					genre = u'{{f}}'
				if genre != u'':
					PageEnd = PageEnd.replace(u'{{genre|fr}}', genre)
			
		# Liens vers les annexes de conjugaisons
		LanguesC = [ (u'es',u'ar',u'arsi',u'er',u'ersi',u'ir',u'irsi'),
					 (u'pt',u'ar',u'ar-se',u'er',u'er-se',u'ir',u'ir-se'),
					 (u'it',u'are',u'arsi',u'ere',u'ersi',u'ire',u'irsi'),
					 (u'fr',u'er',u'er',u'ir',u'ir',u're',u'ar'),
					 (u'ru',u'',u'',u'',u'',u'',u'')
				   ]
		if PageEnd.find(u'{{voir-conj') == -1 and PageEnd.find(u'[[Image:') == -1:	# Bug (ex : https://fr.wiktionary.org/w/index.php?title=d%C3%A9finir&diff=10128404&oldid=10127687)	{{lang/span\|[a-z\-]*\|([^}]*)}}
			if debogage: print u'Ajout de {{conj}}'
			for l in LanguesC:
				if re.compile(ur'{{S\|verbe\|'+l[0]+u'}}').search(PageEnd) and not re.compile(ur'{{S\|verbe\|'+l[0]+u'}}.*\n*.*{{conj[a-z1-3\| ]*').search(PageEnd):
					if debogage: print u' {{conj|'+l[0]+u'}} manquant'
					if re.compile(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}').search(PageEnd):
						if debogage: print u' ajout de {{conj|'+l[0]+u'}} après {{pron|...}}'
						try:
							i1 = re.search(ur'{{S\|verbe\|'+l[0]+u'}}[^\n]*\n*[^\n]*\n*[^\{]*{{pron\|[^\}]*}}',PageEnd).end()
							PageEnd = PageEnd[:i1] + u' {{conjugaison|'+l[0]+u'}}' + PageEnd[i1:]
						except:
							if debogage: print u' Erreur l 5390'
					else:
						if debogage: print u' pas de prononciation pour ajouter {{conj}}'
						
		if PageEnd.find(u'{{conj') != -1:
			if debogage: print u' Ajout des groupes dans {{conj}}'
			'''for (langue,premier,ppron,deuxieme,dpron,troisieme,tpron) in LanguesC:
				if premier != u'':

					if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}').search(PageEnd) and not re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}.*\n*.*{{conj[a-z1-3\| ]*').search(PageEnd):
						if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*\n*[ ^\[]*{{pron\|').search(PageEnd):
							if PageC[len(PageC)-len(premier):] == premier or PageC[len(PageC)-len(ppron):] == ppron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
									PageEnd = PageEnd[:i1] + u' {{conj|grp=1|' + langue + u'}}' + PageEnd[i1:]
								except:
									print PageC.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + premier
							elif PageC[len(PageC)-len(premier):] == deuxieme or PageC[len(PageC)-len(ppron):] == dpron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
									PageEnd = PageEnd[:i1] + u' {{conj|grp=2|' + langue + u'}}' + PageEnd[i1:]
								except:
									print PageC.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + deuxieme
							elif PageC[len(PageC)-len(premier):] == troisieme or PageC[len(PageC)-len(ppron):] == tpron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
									PageEnd = PageEnd[:i1] + u' {{conj|grp=3|' + langue + u'}}' + PageEnd[i1:]
								except:
									print PageC.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + troisieme
						else:
							if PageC[len(PageC)-len(premier):] == premier or PageC[len(PageC)-len(ppron):] == ppron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*\'\'\'',PageEnd).end()
									if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}}' + PageEnd[i1:]
									elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
										PageEnd = PageEnd[:i1] + PageEnd[i1:][0:PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2] + u' {{conj|grp=1|' + langue + u'}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2:len(PageEnd[i1:])]
									elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=1|' + langue + u'}}' + PageEnd[i1:]
								except:
									print langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
							elif PageC[len(PageC)-len(premier):] == deuxieme or PageC[len(PageC)-len(ppron):] == dpron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',PageEnd).end()
									if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}}' + PageEnd[i1:]
									elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
										PageEnd = PageEnd[:i1] + PageEnd[i1:][0:PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2] + u' {{conj|grp=2|' + langue + u'}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2:len(PageEnd[i1:])]
									elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=2|' + langue + u'}}' + PageEnd[i1:]
								except:
									print PageC.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
							elif PageC[len(PageC)-len(premier):] == troisieme or PageC[len(PageC)-len(ppron):] == tpron:
								try:
									i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n[^\[]*\'\'\'',PageEnd).end()
									if PageEnd[i1:].find(u'{{conj') != -1 and PageEnd[i1:].find(u'{{conj') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}}' + PageEnd[i1:]
									elif PageEnd[i1:].find(u'{{pron') != -1 and PageEnd[i1:].find(u'{{pron') < PageEnd[i1:].find(u'\n') and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageTemp2 = PageEnd[i1:][PageEnd[i1:].find(u'{{pron'):len(PageEnd[i1:])]
										PageEnd = PageEnd[:i1] + PageEnd[i1:][0:PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2] + u' {{conj|grp=3|' + langue + u'}}' + PageEnd[i1:][PageEnd[i1:].find(u'{{pron')+PageTemp2.find(u'}}')+2:len(PageEnd[i1:])]
									elif (PageEnd[i1:].find(u'{{pron') == -1 or PageEnd[i1:].find(u'{{pron') > PageEnd[i1:].find(u'\n')) and (PageEnd[i1:].find(u'{{conj') == -1 or PageEnd[i1:].find(u'{{conj') > PageEnd[i1:].find(u'\n')):
										PageEnd = PageEnd[:i1] + u' {{pron||' + langue + u'}} {{conj|grp=3|' + langue + u'}}' + PageEnd[i1:]
								except:
									print PageC.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
			'''
		# Interwikis
		if PageEnd.find(u'{{langue|en}}') != -1 and PageEnd.find(u'[[en:') == -1:
			pageEN = Page(siteEN,PageC)
			if pageEN.exists():
				try:
					PageEN = pageEN.get()
				except wikipedia.NoPage:
					print "NoPage l 4698"
					return
				except wikipedia.IsRedirectPage: 
					print "IsRedirect l 4701"
					return
				if PageEN.find(u'==English==') != -1:
					PageEnd = PageEnd + u'\n[[en:' + PageC + u']]'
					summary = summary + u', ajout d\'interwiki'
					
	else:
		PageEnd = PageTemp

	if debogage: print u'Test des URL'
	#PageEnd = hyperlynx.hyperlynx(PageEnd)
	if debogage: print (u'--------------------------------------------------------------------------------------------')
	if PageEnd != PageBegin:
		# Modifications mineures, ne justifiant pas une édition à elles seules
		PageEnd = PageEnd.replace(u'  ', u' ')
		PageEnd = PageEnd.replace(u'\n\n\n\n', u'\n\n\n')
		PageEnd = PageEnd.replace(u'.\n=', u'.\n\n=')
		sauvegarde(page,PageEnd, summary)
	elif debogage:
		print "Aucun changement"
		

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

def addCat(PageTemp, lang, cat):
	if lang != u'':
		if PageTemp.find(cat) == -1 and PageTemp.find(u'{{langue|' + lang + u'}}') != -1:
			if cat.find(u'[[Catégorie:') == -1: cat = u'[[Catégorie:' + cat + u']]'
			PageTemp2 = PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}'):]
			if PageTemp2.find(u'{{langue|') != -1:
				if debogage: print u' catégorie ajoutée avant la section suivante'
				if PageTemp2.find(u'== {{langue|') != -1:
					PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'== {{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'== {{langue|'):]
				elif PageTemp2.find(u'=={{langue|') != -1:
					PageTemp = PageTemp[:PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'=={{langue|')] + cat + u'\n\n' + PageTemp[PageTemp.find(u'{{langue|' + lang + u'}}')+len(u'{{langue|' + lang + u'}}')+PageTemp2.find(u'=={{langue|'):]
				else:
					 print u'Modèle {{langue| mal positionné'
			else:
				if debogage: print u' catégorie ajoutée avant les interwikis'
				regex = ur'\n\[\[\w?\w?\w?:'
				if re.compile(regex).search(PageTemp):
					try:
						PageTemp = PageTemp[:re.search(regex,PageTemp).start()] + u'\n' + cat + u'\n' + PageTemp[re.search(regex,PageTemp).start():]
					except:
						print u'pb regex interwiki'
				else:
					if debogage: print u' catégorie ajoutée en fin de page'
					PageTemp = PageTemp + u'\n' + cat
	return PageTemp

def rec_anagram(counter):
	# Copyright http://www.siteduzero.com/forum-83-541573-p2-exercice-generer-tous-les-anagrammes.html
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1
def anagram(word):
    return rec_anagram(collections.Counter(word))
	
# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def crawlerFile(source):
	if source:
		PagesHS = open(source, 'r')
		while 1:
			PageC = PagesHS.readline()
			fin = PageC.find("\t")
			PageC = PageC[0:fin]
			if PageC == '': break
			if PageC.find(u'[[') != -1:
				PageC = PageC[PageC.find(u'[[')+2:]
			if PageC.find(u']]') != -1:
				PageC = PageC[0:PageC.find(u']]')]
			# Conversion ASCII => Unicode (pour les .txt)
			modification(HTMLUnicode.HTMLUnicode(PageC))
		PagesHS.close()

# Traitement d'une catégorie
def crawlerCat(category,recursif,apres):
	modifier = u'False'
	cat = catlib.Category(site, category)
	pages = cat.articlesList(False)
	gen =  pagegenerators.NamespaceFilterPageGenerator(pages, [0])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'
	if recursif == True:
		subcat = cat.subcategories(recurse = True)
		for subcategory in subcat:
			pages = subcategory.articlesList(False)
			for Page in pagegenerators.PreloadingGenerator(pages,100):
				modification(Page.title())

# Traitement des pages liées
def crawlerLink(pagename,apres):
	modifier = u'False'
	#pagename = unicode(arg[len('-links:'):], 'utf-8')
	page = wikipedia.Page(site, pagename)
	gen = pagegenerators.ReferringPageGenerator(page)
	gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print(Page.title().encode(config.console_encoding, 'replace'))
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title()) #crawlerLink(Page.title())
		elif Page.title() == apres:
			modifier = u'True'

# Traitement des pages liées des entrées d'une catégorie
def crawlerCatLink(pagename,apres):
	modifier = u'False'
	cat = catlib.Category(site, pagename)
	pages = cat.articlesList(False)
	for Page in pagegenerators.PreloadingGenerator(pages,100):
		page = wikipedia.Page(site, Page.title())
		gen = pagegenerators.ReferringPageGenerator(page)
		gen =  pagegenerators.NamespaceFilterPageGenerator(gen, [0])
		for PageLiee in pagegenerators.PreloadingGenerator(gen,100):
			#print(Page.title().encode(config.console_encoding, 'replace'))
			if not apres or apres == u'' or modifier == u'True':
				modification(PageLiee.title()) #crawlerLink(Page.title())
			elif PageLiee.title() == apres:
				modifier = u'True'
				
# Traitement d'une recherche
def crawlerSearch(pagename):
	gen = pagegenerators.SearchPageGenerator(pagename, site = site, namespaces = "0")
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())

# Traitement des modifications récentes
def crawlerRC_last_day(site=site, nobots=True, namespace='0'):
    # Génère les modifications récentes de la dernière journée
	ecart_last_edit = 30 # minutes
	
	date_now = datetime.datetime.utcnow()
	# Date de la plus récente modification à récupérer
	date_start = date_now - datetime.timedelta(minutes=ecart_last_edit)
	# Date d'un jour plus tôt
	date_end = date_start - datetime.timedelta(1)
	
	start_timestamp = date_start.strftime('%Y%m%d%H%M%S')
	end_timestamp = date_end.strftime('%Y%m%d%H%M%S')

	for item in site.recentchanges(number=5000, rcstart=start_timestamp, rcend=end_timestamp, rcshow=None,
					rcdir='older', rctype='edit|new', namespace=namespace,
					includeredirects=True, repeat=False, user=None,
					returndict=False, nobots=nobots):
		yield item[0]
		
def crawlerRC():
	gen = pagegenerators.RecentchangesPageGenerator(site = site)
	ecart_minimal_requis = 30 # min
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print str(ecart_last_edit(Page)) + ' =? ' + str(ecart_minimal_requis)
		if ecart_last_edit(Page) > ecart_minimal_requis:
			modification(Page.title())

def ecart_last_edit(page):
	# Timestamp au format MediaWiki de la dernière version
	time_last_edit = page.getVersionHistory()[0][1]
	match_time = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', time_last_edit)
	# Mise au format "datetime" du timestamp de la dernière version
	datetime_last_edit = datetime.datetime(int(match_time.group(1)), int(match_time.group(2)), int(match_time.group(3)),
		int(match_time.group(4)), int(match_time.group(5)), int(match_time.group(6)))
	datetime_now = datetime.datetime.utcnow()
	diff_last_edit_time = datetime_now - datetime_last_edit
 
	# Ecart en minutes entre l'horodotage actuelle et l'horodotage de la dernière version
	return diff_last_edit_time.seconds/60 + diff_last_edit_time.days*24*60
	
# Traitement des modifications d'un compte
def crawlerUser(username,jusqua,apres):
	modifier = u'False'
	compteur = 0
	gen = pagegenerators.UserContributionsGenerator(username, site = site)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		if not apres or apres == u'' or modifier == u'True':
			modification(Page.title())
			compteur = compteur + 1
			if compteur > jusqua: break
		elif Page.title() == apres:
			modifier = u'True'

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False, site = site)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		#print (Page.title().encode(config.console_encoding, 'replace'))
		modification(Page.title())
	
# Permet à tout le monde de stopper le bot en lui écrivant
def ArretDUrgence():
		page = Page(site,u'User talk:' + mynick)
		if page.exists():
			PageTemp = u''
			try:
				PageTemp = page.get()
			except wikipedia.NoPage: return
			except wikipedia.IsRedirectPage: return
			except wikipedia.ServerError: return
			except wikipedia.BadTitle: return
			if PageTemp != u"{{/Stop}}":
				pywikibot.output (u"\n*** \03{lightyellow}Arrêt d'urgence demandé\03{default} ***")
				exit(0)

def sauvegarde(PageCourante, Contenu, summary):
	result = "ok"
	if debogage:
		if len(Contenu) < 6000:
			print(Contenu.encode(config.console_encoding, 'replace'))
		else:
			taille = 3000
			print(Contenu[:taille].encode(config.console_encoding, 'replace'))
			print u'\n[...]\n'
			print(Contenu[len(Contenu)-taille:].encode(config.console_encoding, 'replace'))
		result = raw_input((u'Sauvegarder [['+PageCourante.title()+u']] ? (o/n) ').encode('utf-8'))
	if result != "n" and result != "no" and result != "non":
		if PageCourante.title().find(u'Utilisateur:JackBot/') == -1: ArretDUrgence()
		if not summary: summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
		try:
			PageCourante.put(Contenu, summary)
		except wikipedia.NoPage: 
			print "NoPage en sauvegarde"
			return
		except wikipedia.IsRedirectPage: 
			print "IsRedirectPage en sauvegarde"
			return
		except wikipedia.LockedPage: 
			print "LockedPage en sauvegarde"
			return
		except pywikibot.EditConflict: 
			print "EditConflict en sauvegarde"
			return
		except wikipedia.ServerError: 
			print "ServerError en sauvegarde"
			return
		except wikipedia.BadTitle: 
			print "BadTitle en sauvegarde"
			return
		except AttributeError:
			print "AttributeError en sauvegarde"
			return

# Lancement
debogage = False
if len(sys.argv) > 1:
	DebutScan = u''
	if len(sys.argv) > 2:
		if sys.argv[2] == u'debug':
			debogage = True
		else:
			DebutScan = sys.argv[2]
	if sys.argv[1] == u'test':
		TraitementPage = modification(u'User:' + mynick + u'/test')
	elif sys.argv[1] == u'txt': 
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'.txt')
	elif sys.argv[1] == u'txt2':
		TraitementFichier = crawlerFile(u'articles_' + language + u'_' + family + u'2.txt')
	elif sys.argv[1] == u'm':
		TraitementLiens = crawlerLink(u'Modèle:ex',u'')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Sections utilisant un alias',False,u'')
		#TraitementCategorie = crawlerCat(u'Catégorie:Termes peu attestés sans langue précisée',False,u'')
		#TraitementCategorie = crawlerCat(u'Catégorie:Genres manquants en français',False,u'')
	elif sys.argv[1] == u'lien':
		TraitementLiens = crawlerLink(u'Modèle:vx',u'')
	elif sys.argv[1] == u'page':
		TraitementPage = modification(u'gastéropode')
	elif sys.argv[1] == u'trad':
		TraitementLiens = crawlerLink(u'Modèle:trad-',u'')
	elif sys.argv[1] == u's':
		TraitementRecherche = crawlerSearch(u'"source à préciser"')
	elif sys.argv[1] == u'u':
		crawlerUser(u'Utilisateur:Nicasser', 1000,u'')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	# Quotidiennement :
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Terminologie sans langue précisée',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Prononciations manquantes sans langue précisée',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Flexions à vérifier',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Ébauches à compléter',False,u'')
	TraitementLiens = crawlerLink(u'Modèle:trad',u'')
	TraitementLiens = crawlerLink(u'Modèle:1ergroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:2egroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:3egroupe',u'')
	TraitementLiens = crawlerLink(u'Modèle:-',u'')
	TraitementLiens = crawlerLink(u'Modèle:-ortho-alt-',u'')
	TraitementLiens = crawlerLink(u'Modèle:mascul',u'')
	TraitementLiens = crawlerLink(u'Modèle:fémin',u'')
	TraitementLiens = crawlerLink(u'Modèle:femin',u'')
	TraitementLiens = crawlerLink(u'Modèle:sing',u'')
	TraitementLiens = crawlerLink(u'Modèle:plur',u'')
	TraitementLiens = crawlerLink(u'Modèle:pluri',u'')
	TraitementLiens = crawlerLink(u'Modèle:=langue=',u'')
	TraitementLiens = crawlerLink(u'Modèle:-déf-',u'')
	TraitementLiens = crawlerLink(u'Modèle:pron-rég',u'')
	TraitementLiens = crawlerLink(u'Modèle:mp',u'')
	TraitementLiens = crawlerLink(u'Modèle:fp',u'')
	TraitementLiens = crawlerLink(u'Modèle:vx',u'')
	TraitementLiens = crawlerLink(u'Modèle:pron-rég',u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Traduction en français demandée d’exemple(s) écrits en français',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Utilisation d’anciens modèles de section',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Sections avec titre inconnu',False,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Sections utilisant un alias',False,u'')
'''	
	while 1:
		TraitementRC = crawlerRC_last_day()

TraitementLiensCategorie = crawlerCatLink(u'Catégorie:Modèles désuets',u'')
TraitementLiens = crawlerLink(u'Modèle:SAMPA',u'') : remplacer les tableaux de prononciations ?
TraitementLiens = crawlerLink(u'Modèle:trad-',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Conjugaisons manquantes en français',True,u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects:pron conv',True,u'')

# Modèles
TraitementPage = modification(u'Modèle:terme')
TraitementLiens = crawlerLink(u'Modèle:terme',u'')
TraitementFichier = crawlerFile(u'articles_WTin.txt')
TraitementLiensCategorie = crawlerCatLink(u'Modèles de code langue',u'')
TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects',True,u'')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot', 800)
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')

python replace.py -lang:commons -family:commons -file:articles_commons.txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
python delete.py -lang:fr -family:wiktionary -file:articles_WTin.txt
python movepages.py -lang:fr -family:wiktionary -pairs:"articles_WTin.txt" -noredirect -pairs
python interwiki.py -lang:fr -family:wiktionary -page:"Wiktionnaire:Accueil communautaire"
python interwiki.py -lang:fr -family:wiktionary -wiktionary -autonomous -force -usercontribs:Otourly
python protect.py -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop

à faire vite : ajouter les groupes des verbes, les paragraphes {{S|traduction}}, et les {{pron}}/{{prononciation}}
'''

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

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
siteEN = getSite('en',family)
debogage = False
debogageLent = False
TailleAnagramme = 5 # sinon trop long : 5 > 5 min, 8 > 1 h par page)

# Modèles du site à traiter
limit2 = 135 # Paragraphes sans modèle catégorisant, {{voir| et {{voir/ sont gérés individuellement
limit6 = 1021 # Somme des modèles traités
Modele = range(1, limit6+1)
Section = range(1, limit2+1)
# http://fr.wiktionary.org/wiki/Catégorie:Modèles_de_type_de_mot_du_Wiktionnaire
Modele[0] = u'S'
Section[0] = u'S'
Modele[1] = u'-adj-dem-'
Section[1] = u'adjectif démonstratif'
Modele[2] = u'-adj-dém-'
Section[2] = u'adjectif démonstratif'
Modele[3] = u'-adj-excl-'
Section[3] = u'adjectif exclamatif'
Modele[4] = u'-adj-indef-'
Section[4] = u'adjectif indéfini'
Modele[5] = u'-adj-indéf-'
Section[5] = u'adjectif indéfini'
Modele[6] = u'-adj-int-'
Section[6] = u'adjectif interrogatif'
Modele[7] = u'-adj-num-'
Section[7] = u'adjectif numéral'
Modele[8] = u'-adj-pos-'
Section[8] = u'adjectif possessif'
Modele[9] = u'-adjectif-'
Section[9] = u'adjectif'
Modele[10] = u'-adj-'
Section[10] = u'adjectif'
Modele[11] = u'-adv-int-'
Section[11] = u'adverbe interrogatif'
Modele[12] = u'-adv-pron-'
Section[12] = u'adverbe pronominal'
Modele[13] = u'-adv-rel-'
Section[13] = u'adverbe relatif'
Modele[14] = u'-adverbe-'
Section[14] = u'adverbe'
Modele[15] = u'-adv-'
Section[15] = u'adverbe'
Modele[16] = u'-aff-'
Section[16] = u'affixe'
Modele[17] = u'-art-def-'
Section[17] = u'article défini'
Modele[18] = u'-art-déf-'
Section[18] = u'article défini'
Modele[19] = u'-art-indef-'
Section[19] = u'article indéfini'
Modele[20] = u'-art-indéf-'
Section[20] = u'article indéfini'
Modele[21] = u'-art-part-'
Section[21] = u'article partitif'
Modele[22] = u'-art-'
Section[22] = u'article'
Modele[23] = u'-aux-'
Section[23] = u'verbe'
Modele[24] = u'-circonf-'
Section[24] = u'circonfixe'
Modele[25] = u'-class-'
Section[25] = u'classificateur'
Modele[26] = u'-conj-coord-'
Section[26] = u'conjonction de coordination'
Modele[27] = u'-conj-'
Section[27] = u'conjonction'
Modele[28] = u'-copule-'
Section[28] = u'copule'
Modele[29] = u'-dét-'
Section[29] = u'déterminant'
Modele[30] = u'-erreur-'
Section[30] = u'erreur'
Modele[31] = u'-gismu-'
Section[31] = u'gismu'
Modele[32] = u'-inf-'
Section[32] = u'infixe'
Modele[33] = u'-interf-'
Section[33] = u'interfixe'
Modele[34] = u'-interj-'
Section[34] = u'interjection'
Modele[35] = u'-lettre-'
Section[35] = u'lettre'
Modele[36] = u'-nom-fam-'
Section[36] = u'nom de famille'
Modele[37] = u'-nom-pr-'
Section[37] = u'nom propre'
Modele[38] = u'-nom-propre-'
Section[38] = u'nom propre'
Modele[39] = u'-nom-sciences-'
Section[39] = u'nom scientifique'
Modele[40] = u'-nom-'
Section[40] = u'nom'
Modele[41] = u'-num-'
Section[41] = u'numéral'
Modele[42] = u'-numér-'
Section[42] = u'numéral'
Modele[43] = u'-numéral-'
Section[43] = u'numéral'
Modele[44] = u'-part-num-'
Section[44] = u'particule numérale'
Modele[45] = u'-part-'
Section[45] = u'particule'
Modele[46] = u'-patronyme-'
Section[46] = u'patronyme'
Modele[47] = u'-post-'
Section[47] = u'postposition'
Modele[48] = u'-préf-'
Section[48] = u'préfixe'
Modele[49] = u'-préfixe-'
Section[49] = u'préfixe'
Modele[50] = u'-prénom-'
Section[50] = u'prénom'
Modele[51] = u'-pré-nom-'
Section[51] = u'pré-nom'
Modele[52] = u'-prép-'
Section[52] = u'préposition'
Modele[53] = u'-pré-verbe-'
Section[53] = u'pré-verbe'
Modele[54] = u'-pronom-adj-'
Section[54] = u'pronom-adjectif'
Modele[55] = u'-pronom-dém-'
Section[55] = u'pronom démonstratif'
Modele[56] = u'-pronom-indéf-'
Section[56] = u'pronom indéfini'
Modele[57] = u'-pronom-int-'
Section[57] = u'pronom interrogatif'
Modele[58] = u'-pronom-pers-'
Section[58] = u'pronom personnel'
Modele[59] = u'-pronom-pos-'
Section[59] = u'pronom possessif'
Modele[60] = u'-pronom-rel-'
Section[60] = u'pronom relatif'
Modele[61] = u'-pronom-'
Section[61] = u'pronom'
Modele[62] = u'-quantif-'
Section[62] = u'quantificateur'
Modele[63] = u'-radical-'
Section[63] = u'radical'
Modele[64] = u'-rafsi-'
Section[64] = u'rafsi'
Modele[65] = u'-sinogramme-'
Section[65] = u'sinogramme'
Modele[66] = u'-subst-pron-pers-'
Section[66] = u'adjectifs'
Modele[67] = u'-suf-'
Section[67] = u'suffixe'
Modele[68] = u'-suffixe-'
Section[68] = u'suffixe'
Modele[69] = u'-symb-'
Section[69] = u'symbole'
Modele[70] = u'-symbole-'
Section[70] = u'symbole'
Modele[71] = u'-verbe-pr-'
Section[71] = u'verbe pronominal'
Modele[72] = u'-verb-pr-'
Section[72] = u'verbe pronominal'
Modele[73] = u'-verb-'
Section[73] = u'verbe'
Modele[74] = u'-verbe-'
Section[74] = u'verbe'
Modele[75] = u'-faux-prov-'
Section[75] = u'faux proverbe'
Modele[76] = u'-prov-'
Section[76] = u'proverbe'
Modele[77] = u'-loc-phr-'
Section[77] = u'locution-phrase'
Modele[78] = u'-loc-'
Section[78] = u'locution'
Modele[79] = u'-locution-'
Section[79] = u'locution'
Modele[80] = u'-var-typo-'
Section[80] = u'variante typographique'
Modele[81] = u'-onoma-'
Section[81] = u'onomatopée'
Modele[82] = u'-onomatopée-'
Section[82] = u'onomatopée'
Modele[83] = u'-interjection-'
Section[83] = u'interjection'

limit1 = 84 # Paragraphes avec modèle catégorisant
# http://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Mod%C3%A8les_de_contexte
Modele[84] = u'-réf-'
Section[84] = u'références'
Modele[85] = u'-références-'
Section[85] = u'références'
Modele[86] = u'-sino-dico-'
Section[86] = u'dico sinogrammes'
Modele[87] = u'-écrit-'
Section[87] = u'écriture'
Modele[88] = u'-voir-'
Section[88] = u'voir aussi'
Modele[89] = u'-anagrammes-'
Section[89] = u'anagrammes'
Modele[90] = u'-anagr-'
Section[90] = u'anagrammes'
Modele[91] = u'-étym-'
Section[91] = u'étymologie'
Modele[92] = u'-pron-'
Section[92] = u'prononciation'

limit14 = 93
Modele[93] = u'-compos-'
Section[93] = u'composés'
Modele[94] = u'-décl-'
Section[94] = u'déclinaison'
Modele[95] = u'-dial-'
Section[95] = u'variantes dialectales'
Modele[96] = u'-faux-amis-'
Section[96] = u'faux-amis'
Modele[97] = u'-image-'
Section[97] = u'images vidéo'
Modele[98] = u'-trad-'
Section[98] = u'traductions'
Modele[99] = u'-dimin-'
Section[99] = u'diminutifs'
Modele[100] = u'-drv-int-'
Section[100] = u'dérivés autres langues'
Modele[101] = u'-drv-'
Section[101] = u'dérivés'
Modele[102] = u'-exp-'
Section[102] = u'expressions'
Modele[103] = u'-gent-'
Section[103] = u'gentilés'
Modele[104] = u'-hist-'
Section[104] = u'attestations'
Modele[105] = u'-homo-'
Section[105] = u'homophones'
Modele[106] = u'-holo-'
Section[106] = u'holonymes'
Modele[107] = u'-hyper-'
Section[107] = u'hyperonymes'
Modele[108] = u'-hypo-'
Section[108] = u'hyponymes'
Modele[109] = u'-méro-'
Section[109] = u'méronymes'
Modele[110] = u'-noms-vern-'
Section[110] = u'noms vernaculaires'
Modele[111] = u'-ortho-arch-'
Section[111] = u'anciennes orthographes'
Modele[112] = u'-paro-'
Section[112] = u'paronymes'
Modele[113] = u'-q-syn-'
Section[113] = u'quasi-synonymes'
Modele[114] = u'-syn-'
Section[114] = u'synonymes'
Modele[115] = u'-tran-'
Section[115] = u'transcriptions'
Modele[116] = u'-trans-'
Section[116] = u'transcriptions'
Modele[117] = u'-translit-'
Section[117] = u'translittérations'
Modele[118] = u'-tropo-'
Section[118] = u'troponymes'
Modele[119] = u'-var-ortho-'
Section[119] = u'variantes orthographiques'
Modele[120] = u'-var-ortho-'
Section[120] = u'variantes ortho'
Modele[121] = u'-var-'
Section[121] = u'variantes'
Modele[122] = u'-vidéo-'
Section[122] = u'images vidéo'
Modele[123] = u'-voc-'
Section[123] = u'vocabulaire'
Modele[124] = u'-voc-'
Section[124] = u'vocabulaire apparenté'
Modele[125] = u'-abréviation-'
Section[125] = u'abréviations'
Modele[126] = u'-ant-'
Section[126] = u'antonymes'
Modele[127] = u'-abrév-'
Section[127] = u'abréviations'
Modele[128] = u'-dial-'
Section[128] = u'dial'
Modele[129] = u'-apr-'
Section[129] = u'apparentés'
Modele[130] = u'-conjug-'
Section[130] = u'conjugaison'
Modele[131] = u'-cit-'
Section[131] = u'citations'

limit15 = 132
Modele[132] = u'-notes-'
Section[132] = u'notes'
Modele[133] = u'-note-'
Section[133] = u'note'
Modele[134] = u'trad-trier'
Section[134] = u'traductions à trier'

# Attention : limit2 est déclarée plus haut
Modele[135] = u'?'
Modele[136] = u'doute'
Modele[137] = u'm'
Modele[138] = u'f'
Modele[139] = u'vérifier'
Modele[140] = u'formater'
Modele[141] = u'suppression'
Modele[142] = u'supp'
Modele[143] = u'SI'
Modele[144] = u'supprimer ?'
Modele[145] = u'PàS'	
Modele[146] = u'('
Modele[147] = u')'
Modele[148] = u'trad-début'
Modele[149] = u'trad-fin'
Modele[150] = u'titre incorrect'
Modele[151] = u'trad--'
Modele[152] = u'trad-'
Modele[153] = u'trad+'
Modele[154] = u'trad'
Modele[155] = u'voir'
Modele[156] = u'préciser'

limit25 = 157
Modele[157] = u'mf?'
Modele[158] = u'fm ?'
Modele[159] = u'comparatif'
Modele[160] = u'superlatif'
Modele[161] = u'beaucoup plus courant'
Modele[162] = u'plus courant'
Modele[163] = u'beaucoup moins courant'
Modele[164] = u'moins courant'
Modele[165] = u'b-pl-cour'
Modele[166] = u'pl-cour'
Modele[167] = u'b-m-cour'
Modele[168] = u'm-cour'
Modele[169] = u'mf'
Modele[170] = u'n'
Modele[171] = u'c'
Modele[172] = u'pl-rare'
Modele[173] = u'plus rare'

limit3 = 174 # Paragraphes sans modèle catégorisant pouvant contenir des modèles
# http://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Mod%C3%A8les_de_domaine_d%E2%80%99utilisation
Modele[174] = u'outils'
Modele[175] = u'saccusatif'
Modele[176] = u'sdatif'
Modele[177] = u'sinstrumental'
Modele[178] = u'pétrochimie'
Modele[179] = u'champignons'
Modele[180] = u'armes'
Modele[181] = u'langues'
Modele[182] = u'roches'
Modele[183] = u'chiromancie'
Modele[184] = u'fruits'
Modele[185] = u'légumes'
Modele[186] = u'gallicisme'
Modele[187] = u'abréviation'
Modele[188] = u'par ellipse'
Modele[189] = u'mélio'
Modele[190] = u'hapax'
Modele[191] = u'préhistoire'
Modele[192] = u'dépendant'
Modele[193] = u'humour'
Modele[194] = u'argot scolaire'
Modele[195] = u'argot policier'
Modele[196] = u'hispanisme'
Modele[197] = u'planche à neige'
Modele[198] = u'planche à roulettes'
Modele[199] = u'volcanologie'
Modele[200] = u'infographie'
Modele[201] = u'football américain'
Modele[202] = u'football canadien'
Modele[203] = u'idiotisme'
Modele[204] = u'scolaire'
Modele[205] = u'logistique'
Modele[206] = u'lutherie'
Modele[207] = u'pétanque'
Modele[208] = u'accord genre ?'
Modele[209] = u'supprimer-déf ?'
Modele[210] = u'hyperbole'
Modele[211] = u'interjection'
Modele[212] = u'ironique'
Modele[213] = u'litote'
Modele[214] = u'littéraire'
Modele[215] = u'péjoratif'
Modele[216] = u'mélioratif'
Modele[217] = u'métaphore'
Modele[218] = u'métonymie'
Modele[219] = u'mot-valise'
Modele[220] = u'néologisme'
Modele[221] = u'néol litt'
Modele[222] = u'anglicisme'
Modele[223] = u'antiquité'
Modele[224] = u'ordinal'
Modele[225] = u'palindrome'
Modele[226] = u'archaïque'
Modele[227] = u'poissons'
Modele[228] = u'virologie'
Modele[229] = u'viticulture'
Modele[230] = u'zoologie'
Modele[231] = u'plaisanterie'
Modele[232] = u'poétique'
Modele[233] = u'populaire'
Modele[234] = u'propre'
Modele[235] = u'proverbial'
Modele[236] = u'rare'
Modele[237] = u'sigle'
Modele[238] = u'soutenu'
Modele[239] = u'désuet'
Modele[240] = u'insecte'
Modele[241] = u'poisson'
Modele[242] = u'très familier'
Modele[243] = u'vieilli'
Modele[244] = u'vulgaire'
Modele[245] = u'wiki'
Modele[246] = u'popu'
Modele[247] = u'vx'
Modele[248] = u'dés'
Modele[249] = u'fam'
Modele[250] = u'péj'
Modele[251] = u'vulg'
Modele[252] = u'télé'
Modele[253] = u'administration'
Modele[254] = u'aéronautique'
Modele[255] = u'agriculture'
Modele[256] = u'alpinisme'
Modele[257] = u'anatomie'
Modele[258] = u'anthropologie'
Modele[259] = u'architecture'
Modele[260] = u'archéologie'
Modele[261] = u'arme'
Modele[262] = u'arts'
Modele[263] = u'astrologie'
Modele[264] = u'astronomie'
Modele[265] = u'audiovisuel'
Modele[266] = u'automobile'
Modele[267] = u'aviation'
Modele[268] = u'bactériologie'
Modele[269] = u'baseball'
Modele[270] = u'basket'
Modele[271] = u'bijouterie'
Modele[272] = u'billard'
Modele[273] = u'biochimie'
Modele[274] = u'biologie'
Modele[275] = u'botanique'
Modele[276] = u'boucherie'
Modele[277] = u'bowling'
Modele[278] = u'cartes'
Modele[279] = u'charpenterie'
Modele[280] = u'chasse'
Modele[281] = u'chimie'
Modele[282] = u'chirurgie'
Modele[283] = u'cinéma'
Modele[284] = u'commerce'
Modele[285] = u'construction'
Modele[286] = u'cosmétologie'
Modele[287] = u'couture'
Modele[288] = u'cricket'
Modele[289] = u'cuisine'
Modele[290] = u'cyclisme'
Modele[291] = u'danse'
Modele[292] = u'dermatologie'
Modele[293] = u'droit'
Modele[294] = u'échecs'
Modele[295] = u'écologie'
Modele[296] = u'finance'
Modele[297] = u'économie'
Modele[298] = u'éducation'
Modele[299] = u'électricité'
Modele[300] = u'électronique'
Modele[301] = u'électrotechnique'
Modele[302] = u'élevage'
Modele[303] = u'entomologie'
Modele[304] = u'équitation'
Modele[305] = u'escrime'
Modele[306] = u'ethnologie'
Modele[307] = u'famille'
Modele[308] = u'fantastique'
Modele[309] = u'fauconnerie'
Modele[310] = u'ferro'
Modele[311] = u'figure'
Modele[312] = u'football'
Modele[313] = u'gastronomie'
Modele[314] = u'généalogie'
Modele[315] = u'génétique'
Modele[316] = u'géographie'
Modele[317] = u'géologie'
Modele[318] = u'géométrie'
Modele[319] = u'géophysique'
Modele[320] = u'glaciologie'
Modele[321] = u'golf'
Modele[322] = u'grammaire'
Modele[323] = u'handball'
Modele[324] = u'héraldique'
Modele[325] = u'histoire'
Modele[326] = u'histologie'
Modele[327] = u'horlogerie'
Modele[328] = u'ichtyologie'
Modele[329] = u'imprimerie'
Modele[330] = u'industrie'
Modele[331] = u'informatique'
Modele[332] = u'internet'
Modele[333] = u'jardinage'
Modele[334] = u'paume'
Modele[335] = u'jeux'
Modele[336] = u'jonglage'
Modele[337] = u'journal'
Modele[338] = u'jurisprudence'
Modele[339] = u'justice'
Modele[340] = u'législation'
Modele[341] = u'linguistique'
Modele[342] = u'littérature'
Modele[343] = u'logique'
Modele[344] = u'maçonnerie'
Modele[345] = u'marine'
Modele[346] = u'mathématiques'
Modele[347] = u'mécanique'
Modele[348] = u'médecine'
Modele[349] = u'médecine non conv'
Modele[350] = u'média'
Modele[351] = u'menuiserie'
Modele[352] = u'métallurgie'
Modele[353] = u'météorologie'
Modele[354] = u'métrologie'
Modele[355] = u'microbiologie'
Modele[356] = u'militaire'
Modele[357] = u'minéralogie'
Modele[358] = u'minéraux'
Modele[359] = u'motocyclisme'
Modele[360] = u'musique'
Modele[361] = u'mycologie'
Modele[362] = u'mythologie'
Modele[363] = u'narratologie'
Modele[364] = u'natation'
Modele[365] = u'navigation'
Modele[366] = u'neurologie'
Modele[367] = u'maladies'
Modele[368] = u'nosologie'
Modele[369] = u'novlangue'
Modele[370] = u'numismatique'
Modele[371] = u'oenologie'
Modele[372] = u'optique'
Modele[373] = u'optométrie'
Modele[374] = u'ornithologie'
Modele[375] = u'paléographie'
Modele[376] = u'paléontologie'
Modele[377] = u'papillons'
Modele[378] = u'pâtisserie'
Modele[379] = u'pays'
Modele[380] = u'pêche'
Modele[381] = u'pédologie'
Modele[382] = u'peinture'
Modele[383] = u'pétrochimie'
Modele[384] = u'pharmacologie'
Modele[385] = u'philosophie'
Modele[386] = u'photographie'
Modele[387] = u'physiologie'
Modele[388] = u'physique'
Modele[389] = u'plante'
Modele[390] = u'poésie'
Modele[391] = u'poker'
Modele[392] = u'police'
Modele[393] = u'politique'
Modele[394] = u'psychiatrie'
Modele[395] = u'psychologie'
Modele[396] = u'religion'
Modele[397] = u'rhétorique'
Modele[398] = u'rugby'
Modele[399] = u'sci-fi'
Modele[400] = u'sciences'
Modele[401] = u'sculpture'
Modele[402] = u'serrurerie'
Modele[403] = u'sexualité'
Modele[404] = u'sociologie'
Modele[405] = u'sport'
Modele[406] = u'statistiques'
Modele[407] = u'sylviculture'
Modele[408] = u'technique'
Modele[409] = u'technologie'
Modele[410] = u'tennis'
Modele[411] = u'textile'
Modele[412] = u'théâtre'
Modele[413] = u'théologie'
Modele[414] = u'thermodynamique'
Modele[415] = u'topographie'
Modele[416] = u'topologie'
Modele[417] = u'toponymie'
Modele[418] = u'tourisme'
Modele[419] = u'transport'
Modele[420] = u'travail'
Modele[421] = u'typographie'
Modele[422] = u'télécommunications'
Modele[423] = u'urbanisme'
Modele[424] = u'vêtements'
Modele[425] = u'marketing'
Modele[426] = u'aphérèse'
Modele[427] = u'apocope'
Modele[428] = u'argot'
Modele[429] = u'cardinal'
Modele[430] = u'informel'
Modele[431] = u'contemporain'
Modele[432] = u'courant'
Modele[433] = u'dérision'
Modele[434] = u'jazz'
Modele[435] = u'tennis de table'
Modele[436] = u'volley-ball'
Modele[437] = u'volley'
Modele[438] = u'badminton'
Modele[438] = u'bases de données'
Modele[439] = u'BDD'
Modele[440] = u'pharma'
Modele[441] = u'apiculture'
Modele[442] = u'coiffure'
Modele[443] = u'astronautique'
Modele[444] = u'animaux'
Modele[445] = u'plantes'
Modele[446] = u'capoeira'
Modele[447] = u'jeu vidéo'
Modele[448] = u'skate'
Modele[449] = u'skateboard'
Modele[450] = u'patin'
Modele[451] = u'escalade'
Modele[452] = u'archéo'
Modele[453] = u'armement'
Modele[454] = u'astrol'
Modele[455] = u'astron'
Modele[456] = u'audiovis'
Modele[457] = u'automo'
Modele[458] = u'aviat'
Modele[459] = u'bactério'
Modele[460] = u'bijou'
Modele[461] = u'biol'
Modele[462] = u'botan'
Modele[463] = u'chir'
Modele[464] = u'ciné'
Modele[465] = u'comm'
Modele[466] = u'constr'
Modele[467] = u'cosm'
Modele[468] = u'text'
Modele[469] = u'cout'
Modele[470] = u'cuis'
Modele[471] = u'cycl'
Modele[472] = u'dermat'
Modele[473] = u'écol'
Modele[474] = u'finan'
Modele[475] = u'écon'
Modele[476] = u'éduc'
Modele[477] = u'élec'
Modele[478] = u'électro'
Modele[479] = u'électrot'
Modele[480] = u'équi'
Modele[481] = u'foot'
Modele[482] = u'gastro'
Modele[483] = u'généal'
Modele[484] = u'géog'
Modele[485] = u'géol'
Modele[486] = u'géom'
Modele[487] = u'géoph'
Modele[488] = u'gram'
Modele[489] = u'hand'
Modele[490] = u'hérald'
Modele[491] = u'hist'
Modele[492] = u'histol'
Modele[493] = u'ichtyo'
Modele[494] = u'impr'
Modele[495] = u'indus'
Modele[496] = u'inform'
Modele[497] = u'jardin'
Modele[498] = u'juri'
Modele[499] = u'just'
Modele[500] = u'ling'
Modele[501] = u'littér'
Modele[502] = u'maçon'
Modele[503] = u'mari'
Modele[504] = u'math'
Modele[505] = u'méca'
Modele[506] = u'méde'
Modele[507] = u'métal'
Modele[508] = u'météo'
Modele[509] = u'métrol'
Modele[510] = u'mili'
Modele[511] = u'minér'
Modele[512] = u'musi'
Modele[513] = u'nata'
Modele[514] = u'navig'
Modele[515] = u'neuro'
Modele[516] = u'numis'
Modele[517] = u'oenol'
Modele[518] = u'ornit'
Modele[519] = u'paléo'
Modele[520] = u'pêch'
Modele[521] = u'pétro'
Modele[522] = u'philo'
Modele[523] = u'photo'
Modele[524] = u'physio'
Modele[525] = u'phys'
Modele[526] = u'poés'
Modele[527] = u'polit'
Modele[528] = u'psych'
Modele[529] = u'psycho'
Modele[530] = u'scul'
Modele[531] = u'serru'
Modele[532] = u'sexe'
Modele[533] = u'socio'
Modele[534] = u'stat'
Modele[535] = u'sylvi'
Modele[536] = u'tech'
Modele[537] = u'théol'
Modele[538] = u'topo'
Modele[539] = u'topon'
Modele[540] = u'tour'
Modele[541] = u'transp'
Modele[542] = u'typo'
Modele[543] = u'télécom'
Modele[544] = u'urban'
Modele[545] = u'vête'
Modele[546] = u'chim'
Modele[547] = u'phys'
Modele[548] = u'milit'
Modele[549] = u'méd'
Modele[550] = u'hist'
Modele[551] = u'gall'
Modele[552] = u'vieux'
Modele[553] = u'vx'
Modele[554] = u'arch'
Modele[555] = u'admin'
Modele[556] = u'aéro'
Modele[557] = u'agri'
Modele[558] = u'text'
Modele[559] = u'logi'
Modele[560] = u'pop'
Modele[561] = u'cardin'
Modele[562] = u'ordin'
Modele[563] = u'électron'
Modele[564] = u'électrotech'
Modele[565] = u'techno'
Modele[566] = u'technol'
Modele[567] = u'théât'
Modele[568] = u'météorol'
Modele[569] = u'info'
Modele[570] = u'méton'
Modele[571] = u'i'
Modele[572] = u't'
Modele[573] = u'trans'
Modele[574] = u'transit'
Modele[575] = u'intrans'
Modele[576] = u'pronl'
Modele[577] = u'prnl'
Modele[578] = u'réfl'
Modele[579] = u'réfléchi'
Modele[580] = u'électoraux'
Modele[581] = u'joaillerie'
Modele[582] = u'rhéto'
Modele[583] = u'exag'
Modele[584] = u'métaph'
Modele[585] = u'cour'
Modele[586] = u'sout'
Modele[587] = u'prov'
Modele[588] = u'phon'
Modele[589] = u'pron'
Modele[590] = u'pron-rég'
Modele[591] = u'term'
Modele[592] = u'terme'
Modele[593] = u'poét'
Modele[594] = u'antiq'
Modele[595] = u'litt'
Modele[596] = u'mythol'
Modele[597] = u'opti'
Modele[598] = u'zool'
Modele[599] = u'hyperb'
Modele[600] = u'gastron'
Modele[601] = u'didactique'
Modele[602] = u'auxiliaire'
Modele[603] = u'td'
Modele[604] = u'tr-dir'
Modele[605] = u'tr-indir'
Modele[606] = u'dim-lex'
Modele[607] = u'diminutif'
Modele[608] = u'diplomatie'
Modele[609] = u'informatique'
Modele[610] = u'diptote'
Modele[611] = u'alpi'
Modele[612] = u'anat'
Modele[613] = u'anthro'
Modele[614] = u'archi'
Modele[615] = u'angl'
Modele[616] = u'vaudou'
Modele[617] = u'maintenance'
Modele[618] = u'phyton'
Modele[619] = u'phytonimie'
Modele[620] = u'généralement indénombrable'
Modele[621] = u'bibliothéconomie'
Modele[622] = u'comparatif de'
Modele[623] = u'acoustique'
Modele[624] = u'dén'
Modele[625] = u'dénombrable'
Modele[626] = u'affectueux'
Modele[627] = u'glaciol'
Modele[628] = u'fanta'
Modele[629] = u'anal'
Modele[630] = u'indénombrable'
Modele[631] = u'indén'
Modele[632] = u'nominatif'
Modele[633] = u'nomin'
Modele[634] = u'accusatif'
Modele[635] = u'accus'
Modele[636] = u'datif'
Modele[637] = u'génitif'
Modele[638] = u'génit'
Modele[639] = u'vocatif'
Modele[640] = u'vocat'
Modele[641] = u'ablatif'
Modele[642] = u'ablat'
Modele[643] = u'allatif'
Modele[644] = u'instrumental'
Modele[645] = u'locat'
Modele[646] = u'locatif'
Modele[647] = u'prépositionnel'
Modele[648] = u'indéclinable'
Modele[649] = u'indécl'
Modele[650] = u'ppart'
Modele[651] = u'génitif'
Modele[652] = u'psychol'
Modele[653] = u'psycho'
Modele[654] = u'chim'
Modele[655] = u'injur'
Modele[656] = u'mycol'
Modele[657] = u'myco'
Modele[658] = u'Internet'
Modele[659] = u'liturgie'
Modele[660] = u'diplomatie'
Modele[661] = u'tauromachie'
Modele[662] = u'germanisme'
Modele[663] = u'squelette'
Modele[664] = u'muscle'
Modele[665] = u'gymnastique'
Modele[666] = u'déverbal sans suffixe'
Modele[667] = u'déverbal'
Modele[668] = u'injurieux'
Modele[669] = u'réflexif'
Modele[670] = u'algèbre‎'
Modele[671] = u'irrég'
Modele[672] = u'irrégulier'
Modele[673] = u'arts martiaux'
Modele[674] = u'hydraulique'
Modele[675] = u'par analogie'
Modele[676] = u'genre'
Modele[677] = u'type'
Modele[678] = u'iron'
Modele[679] = u'ironie'
Modele[680] = u'plais'
Modele[681] = u'très rare'
Modele[682] = u'didact'
Modele[683] = u'algèbre'
Modele[684] = u'acronyme'
Modele[685] = u'allatif'
Modele[686] = u'analogie'
Modele[687] = u'très très rare'
Modele[688] = u'physiol'
Modele[689] = u'reproduction'
Modele[690] = u'repro'
Modele[691] = u'presse'
Modele[692] = u'meuble'
Modele[693] = u'ellipse'
Modele[694] = u'enclitique'
Modele[695] = u'néol'
Modele[696] = u'archaïsme'
Modele[697] = u'nom'
Modele[698] = u'indéc'
Modele[699] = u'vétérinaire'
Modele[700] = u'reli'
Modele[701] = u'entom'
Modele[702] = u'entomol'
Modele[703] = u'pharmacie'
Modele[704] = u'pharmacol'
Modele[705] = u'athlétisme'
Modele[706] = u'athlé'
Modele[707] = u'christianisme'
Modele[708] = u'conjugaison'
Modele[709] = u'1ergroupe'
Modele[710] = u'2egroupe'
Modele[711] = u'3egroupe'
Modele[712] = u'dénominal de'
Modele[713] = u'déverbal de'
Modele[714] = u'superlatif de'
Modele[715] = u'narratol'
Modele[716] = u'passif'
Modele[717] = u'très-rare'
Modele[718] = u'extrêmement rare'
Modele[719] = u'jardi'
Modele[720] = u'sociol'
Modele[721] = u'papeterie'
Modele[722] = u'papèterie'
Modele[723] = u'Sénégal'
Modele[724] = u'geol'
Modele[725] = u'fami'
Modele[726] = u'tind'
Modele[727] = u'pédol'
Modele[728] = u'biophysique'
Modele[729] = u'psychia'
Modele[730] = u'paléontol'
Modele[731] = u'horticulture'
Modele[732] = u'probabilités'
Modele[733] = u'théorie des graphes'
Modele[734] = u'graphe'
Modele[735] = u'dessin'
Modele[736] = u'récip'
Modele[737] = u'réciproque'
Modele[738] = u'minéral'
Modele[739] = u'mah-jong'
Modele[740] = u'mahjong'
Modele[741] = u'majong'
Modele[742] = u'reliure'
Modele[743] = u'gravure'
Modele[744] = u'livre'
Modele[745] = u'canoe'
Modele[746] = u'footing'
Modele[747] = u'jogging'
Modele[748] = u'running'
Modele[749] = u'course à pied'
Modele[750] = u'programmation'
Modele[751] = u'prog'
Modele[752] = u'jeux vidéo'
Modele[753] = u'judo'
Modele[754] = u'gén-indén'
Modele[755] = u'Liban'
Modele[756] = u'caténatif'
Modele[757] = u'ski alpin'
Modele[758] = u'ski de fond'
Modele[759] = u'canoë-kayak'
Modele[760] = u'canoë'
Modele[761] = u'artillerie'
Modele[762] = u'fonderie'
Modele[763] = u'réseau'
Modele[764] = u'impers'
Modele[765] = u'impersonnel'
Modele[766] = u'scol'
Modele[767] = u'obsolète'
Modele[768] = u'surf'
Modele[769] = u'édition'
Modele[770] = u'fortification'
Modele[771] = u'dentisterie'
Modele[772] = u'réseaux'
Modele[773] = u'réseaux informatiques'
Modele[774] = u'karaté'
Modele[775] = u'argot militaire'
Modele[776] = u'combat'
Modele[777] = u'sports de combat'
Modele[778] = u'capoeira'
Modele[779] = u'aïkido'
Modele[780] = u'argot polytechnicien'
Modele[781] = u'élatif'
Modele[782] = u'auxiliaire'
Modele[783] = u'acron'
Modele[784] = u'pronominal'
Modele[785] = u'abrév'
Modele[786] = u'snowboard'
Modele[787] = u'snow'
Modele[788] = u'transitif'
Modele[789] = u'intransitif'
Modele[790] = u'enfantin'
Modele[791] = u'épithète'
Modele[792] = u'euphémisme'
Modele[793] = u'ex-rare'
Modele[794] = u'exagératif'
Modele[795] = u'expression'
Modele[796] = u'familier'
Modele[797] = u'figuré'
Modele[798] = u'formel'
Modele[799] = u'indéfini'
Modele[800] = u'geog'	# à remplacer ?
Modele[801] = u'singulare tantum'
Modele[802] = u'plurale tantum'
Modele[803] = u'islam'
Modele[804] = u'judaïsme'
Modele[805] = u'CB'
Modele[806] = u'yoga'
Modele[807] = u'couche physique'
Modele[808] = u'couche liaison'
Modele[809] = u'couche réseau'
Modele[810] = u'couche transport'
Modele[811] = u'couche session'
Modele[812] = u'couche présentation'
Modele[813] = u'couche application'
Modele[814] = u'bouddhisme'
Modele[815] = u'hindouisme'
Modele[816] = u'pathologie'
Modele[817] = u'boissons'
Modele[818] = u'confiseries'
Modele[819] = u'stéréotomie'
Modele[820] = u'marbrerie'
Modele[821] = u'improprement'
Modele[822] = u'usage critiqué'
Modele[823] = u'éléments'
Modele[824] = u'points cardinaux'
Modele[825] = u'unités'
Modele[826] = u'monnaies'
Modele[827] = u'religions'
Modele[828] = u'voitures'
Modele[829] = u'avions'
Modele[830] = u'figures'
Modele[831] = u'bateaux'
Modele[832] = u'substances'
Modele[833] = u'usines'
Modele[834] = u'miroiterie'
Modele[835] = u'ustensiles'
Modele[836] = u'édifices'
Modele[837] = u'danses'
Modele[838] = u'chiens'
Modele[839] = u'poet'
Modele[840] = u'peu usité'
Modele[841] = u'journalisme'
Modele[842] = u'lézards'
Modele[843] = u'vitrerie'
Modele[844] = u'vents'
Modele[845] = u'usinage'
Modele[846] = u'maroquinerie'
Modele[847] = u'dialectes'
Modele[848] = u'fontainerie'
Modele[849] = u'nucléaire'
Modele[850] = u'phonétique'
Modele[851] = u'par dérision'
Modele[852] = u'dérision'
Modele[853] = u'déris'
Modele[854] = u'nucl'
Modele[855] = u'un os'
Modele[856] = u'boxe'
Modele[857] = u'confiserie'
Modele[858] = u'abréviation de'
Modele[859] = u'instruments'
Modele[860] = u'vins'
Modele[861] = u'fleurs'
Modele[862] = u'apiculture'
Modele[863] = u'illégalité'
Modele[864] = u'biologie cellulaire'
Modele[865] = u'chimie organique'
Modele[866] = u'histologie'
Modele[867] = u'gâteaux'
Modele[868] = u'loisirs'
Modele[869] = u'golfe'
Modele[870] = u'golfes'
Modele[871] = u'véhicules'
Modele[872] = u'musiques'
Modele[873] = u'fig.'
Modele[874] = u'télévision'
Modele[875] = u'desserts'
Modele[876] = u'dinosaures'
#[[Spécial:newpages]]

limit4 = 877	# code langue quoi qu'il arrive
Modele[877] = u'ébauche-syn'
Modele[878] = u'note-gentilé'
Modele[879] = u'ébauche-trans'
Modele[880] = u'ébauche-étym-nom-scientifique'
Modele[881] = u'ébauche-étym'
Modele[882] = u'ébauche-déf'
Modele[883] = u'ébauche-exe'
Modele[884] = u'ébauche-pron'
Modele[885] = u'ébauche'
'''
# non traités
Modele[] = u'spécialement' 
Modele[] = u'T'
Modele[] = u'région'
Modele[] = u'régio'
Modele[] = u'régional'
Modele[] = u'déterminé'
Modele[] = u'indéterminé'
Modele[] = u'dét'
Modele[] = u'indét'
Modele[] = u'perfectif'
Modele[] = u'imperfectif'
Modele[] = u'perf'
Modele[] = u'imperf'
'''
# Modèles régionaux, pb du nocat pour les prononciations
limit5 = 886
Modele[886] = u'Salvador'
Modele[887] = u'Suède'
Modele[888] = u'Suisse'
Modele[889] = u'Sénégal'
Modele[890] = u'Taïwan'
Modele[891] = u'Tchad'
Modele[892] = u'Transnistrie'
Modele[893] = u'Tunisie'
Modele[894] = u'Uruguay'
Modele[895] = u'Valence'
Modele[896] = u'Var'
Modele[897] = u'Velay'
Modele[898] = u'Venezuela'
Modele[899] = u'Viêt Nam'
# Abréviations (python pagegenerators.py -redirectonly:Template:!)
Modele[900] = u'EU'
Modele[901] = u'FR'
Modele[902] = u'BE'
Modele[903] = u'CH'
Modele[904] = u'QC'
Modele[905] = u'CA'
Modele[906] = u'US'
Modele[907] = u'USA'
Modele[908] = u'UK'
Modele[909] = u'GB'
Modele[910] = u'AU'
Modele[911] = u'NZ'
Modele[912] = u'IE'

Modele[913] = u'Europe'
Modele[914] = u'France'
Modele[915] = u'Franche-Comté'
Modele[916] = u'Gascogne'
Modele[917] = u'Gaspésie'
Modele[918] = u'Guinée'
Modele[919] = u'Guyane'
Modele[920] = u'Haïti'
Modele[921] = u'Honduras'
Modele[922] = u'Île-de-France'
Modele[923] = u'Inde'
Modele[924] = u'Irlande'
Modele[925] = u'Jamaïque'
Modele[926] = u'Languedoc-Roussillon'
Modele[927] = u'Le Mans'
Modele[928] = u'Liban'
Modele[929] = u'Liechtenstein'
Modele[930] = u'Limousin'
Modele[931] = u'Louisiane'
Modele[932] = u'Lyonnais'
Modele[933] = u'Madagascar'
Modele[934] = u'Maghreb'
Modele[935] = u'Mali'
Modele[936] = u'Maroc'
Modele[937] = u'Marseille'
Modele[938] = u'Savoie'
Modele[939] = u'Maurice'
Modele[940] = u'Mayotte'
Modele[941] = u'Mexique'
Modele[942] = u'Midi'
Modele[943] = u'Midi toulousain'
Modele[944] = u'Moldavie'
Modele[945] = u'Nantes'

Modele[946] = u'Afrique'
Modele[947] = u'Afrique du Sud'
Modele[948] = u'Algérie'
Modele[949] = u'Allemagne'
Modele[950] = u'Alsace'
Modele[951] = u'Amérique centrale'
Modele[952] = u'Amérique du Nord'
Modele[953] = u'Amérique du Sud'
Modele[954] = u'Amérique latine'
Modele[955] = u'Anjou'
Modele[956] = u'Antilles'
Modele[957] = u'Aquitaine'
Modele[958] = u'Japon'
Modele[959] = u'Argentine'
Modele[960] = u'Australie'
Modele[961] = u'Autriche'
Modele[962] = u'Auvergne'
Modele[963] = u'Baléares'
Modele[964] = u'Orient'
Modele[965] = u'Belgique'
Modele[966] = u'Luxembourg'
Modele[967] = u'Bénin'
Modele[968] = u'Berry'
Modele[969] = u'Bolivie'
Modele[970] = u'Bordelais'
Modele[971] = u'Bourgogne'
Modele[972] = u'Brésil'
Modele[973] = u'Bretagne'
Modele[974] = u'Burkina Faso'
Modele[975] = u'Cameroun'
Modele[976] = u'Canada'
Modele[977] = u'Catalogne'
Modele[978] = u'Champagne'
Modele[979] = u'Chili'
Modele[980] = u'Chine'
Modele[981] = u'Colombie'
Modele[982] = u'Commonwealth'
Modele[983] = u'Congo'
Modele[984] = u'Congo-Brazzaville'
Modele[985] = u'Congo-Kinshasa'
Modele[986] = u'Corse'
Modele[987] = u'Corée du Nord'
Modele[988] = u'Corée du Sud'
Modele[989] = u'Costa Rica'
Modele[990] = u'Côte d’Ivoire'
Modele[991] = u'Cuba'
Modele[992] = u'Écosse'
Modele[993] = u'Espagne'
Modele[994] = u'États-Unis'
Modele[995] = u'Guadeloupe'

Modele[996] = u'Acadie'

Modele[997] = u'Navarre'
Modele[998] = u'Niger'
Modele[999] = u'Nigéria'
Modele[1000] = u'Normandie'
Modele[1001] = u'Nouvelle-Calédonie'
Modele[1002] = u'Nouvelle-Zélande'
Modele[1003] = u'Occitanie'
Modele[1004] = u'Océanie'
Modele[1005] = u'Paraguay'
Modele[1006] = u'Paris'
Modele[1007] = u'Pays-Bas'
Modele[1008] = u'Pays basque'
Modele[1009] = u'Picardie'
Modele[1010] = u'Poitou'
Modele[1011] = u'Polynésie française'
Modele[1012] = u'Portugal'
Modele[1013] = u'Provence'
Modele[1014] = u'Pérou'
Modele[1015] = u'Québec'
Modele[1016] = u'Quercy'
Modele[1017] = u'Réunion'
Modele[1018] = u'Roumanie'
Modele[1019] = u'Royaume-Uni'

# Modèles de pronociation à synchroniser
Modele[1020] = u'fr-verbe-flexion'
#Modele[] = u'fr-rég'
#Modele[] = u'fr-inv'
#Modele[] = u'fr-accord-rég'
#Modele[] = u'en-nom-rég'

# Modification du wiki
def modification(PageHS):
	summary = u'[[Wiktionnaire:Structure des articles|Autoformatage]]'
	if debogage: print u'------------------------------------'
	print(PageHS.encode(config.console_encoding, 'replace'))
	
	if PageHS.find(u'’') != -1:
		page = Page(site,PageHS.replace(u'’', u'\''))
		if not page.exists():
			if debogage: print u'Création d\'une redirection apostrophe'
			sauvegarde(page, u'#REDIRECT[[' + PageHS + ']]', u'Redirection pour apostrophe')
	page = Page(site,PageHS)
	if page.exists():
		if page.namespace() !=0 and page.namespace() != 100 and page.namespace() != 12 and page.namespace() != 14 and PageHS.find(u'Utilisateur:JackBot/') == -1:
			print u'Page non traitée'
			return
		else:
			try:
				PageBegin = page.get()
			except wikipedia.NoPage:
				print "NoPage l 1263"
				return
			except wikipedia.LockedPage: 
				print "Locked l 1266"
				return
			except wikipedia.IsRedirectPage: 
				PageBegin = page.get(get_redirect=True)
				TxtTmp = u'<!--\n  Redirection créée par le robot User:DaftBot.\n  La création automatique de la page ciblée est prévue prochainement.\n-->'
				if PageBegin.find(TxtTmp) != -1:
					summary = u'[[Catégorie:Redirections à remplacer]]'
					PageBegin = PageBegin[0:PageBegin.find(TxtTmp)] + summary + PageBegin[PageBegin.find(TxtTmp)+len(TxtTmp):len(PageBegin)]
					sauvegarde(page, PageBegin, summary)
				else:
					print "IsRedirect l 1276"
				return
	else:
		print "NoPage l 1279"
		return
	PageTemp = PageBegin
	CleTri = CleDeTri.CleDeTri(PageHS)
	
	regex = ur'{{=([a-z\-]+)=}}'
	if re.search(regex, PageTemp):
		PageTemp = re.sub(regex, ur'{{langue|\1}}', PageTemp)
		if summary.find(u'{{langue}}') == -1: summary = summary + u', déploiement de {{langue}}'
	
	if page.namespace() == 0 or PageHS.find(u'Utilisateur:JackBot/') != -1:
		while PageTemp.find(u'{{ ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{ ')+2] + PageTemp[PageTemp.find(u'{{ ')+3:len(PageTemp)]
		if PageTemp.find(u'{{formater') != -1 or PageTemp.find(u'{{SI|') != -1 or PageTemp.find(u'{{SI}}') != -1 or PageTemp.find(u'{{supp|') != -1 or PageTemp.find(u'{{supp}}') != -1 or PageTemp.find(u'{{supprimer|') != -1 or PageTemp.find(u'{{supprimer') != -1 or PageTemp.find(u'{{PàS') != -1 or PageTemp.find(u'{{S|faute') != -1:
			print "Page en travaux : non traitée"
			return
		
		# Titres de section
		PageTemp = PageTemp.replace(u'==== {{\n{{trad-début}{{trad-fin}}\n}S|traductions}} ====', u'==== {{S|traductions}} ====')
		PageTemp = PageTemp.replace(u'==== {{\n\n{{trad-début}{{trad-fin}}\n}S|traductions}} ====', u'==== {{S|traductions}} ====')
		PageTemp = PageTemp.replace(u'==== {{\n\n{{trad-début}{{)}}\n}S|traductions}} ====', u'==== {{S|traductions}} ====')
		PageTemp = PageTemp.replace(u'<!--* {{T|}} : {{trad||}}-->', u'')
		PageTemp = PageTemp.replace(u'{{-car-}}', u'{{caractère}}')
		PageTemp = PageTemp.replace(u'{{-note-|s=s}}', u'{{-notes-}}')
		PageTemp = PageTemp.replace(u'{{-etym-}}', u'{{-étym-}}')
		PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier}}}}', u'{{trad-trier}}\n{{trad-début}}')
		PageTemp = PageTemp.replace(u'{{trad-début|{{trad-trier|fr}}}}', u'{{trad-trier}}\n{{trad-début}}')
		PageTemp = PageTemp.replace(u'-pronom-personnel-', u'-pronom-pers-')
		
		if debogage: print u'Conversion vers {{S}}'
		EgalSection = u'==='
		for p in range(1,limit2):
			if p == limit14: EgalSection = u'===='
			if p == limit15: EgalSection = u'====='
			
			regex = ur'[= ]*{{[\-loc]*(' + Modele[p] + u'|S\|'+ Section[p] + ur')([^}]*)}}[= ]*'
			if re.search(regex, PageTemp):
				PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'\2}} ' + EgalSection, PageTemp)
				if summary.find(u'{{S}}') == -1 and re.search('{{-\w', PageBegin): summary = summary + u', [[WT:Prise de décision/Rendre toutes les sections modifiables|déploiement de {{S}}]]'
			
			regex = ur'[= ]*{{\-flex[\-loc]*(' + Modele[p] + u'|S\|' + Section[p] + ur')\|([^}]*)}}[= ]*'
			if re.search(regex, PageTemp):
				PageTemp = re.sub(regex, EgalSection + ur' {{S|' + Section[p] + ur'|\2|flexion}} ' + EgalSection, PageTemp)
				if summary.find(u'{{S}}') == -1 and re.search('{{-\w', PageBegin): summary = summary + u', [[WT:Prise de décision/Rendre toutes les sections modifiables|déploiement de {{S}}]]'
		
		if debogageLent: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
		if PageTemp.find(u'|===') != -1 or PageTemp.find(u'{===') != -1:
			if debogage: print u' *==='
			return
		
		# Titres en minuscules
		#PageTemp = re.sub(ur'{{S\|([^}]+)}}', ur'{{S|' + ur'\1'.lower() + ur'}}', PageTemp)
		for f in re.findall("{{S\|([^}]+)}}", PageTemp):
			PageTemp = PageTemp.replace(f, f.lower())
		# Alias peu intuitifs
		PageTemp = PageTemp.replace(u'{{S|adj|', u'{{S|adjectif|')
		PageTemp = PageTemp.replace(u'{{S|adjectifs|', u'{{S|adjectif|')
		PageTemp = PageTemp.replace(u'{{S|adv|', u'{{S|adverbe}}')
		PageTemp = PageTemp.replace(u'{{S|locution phrase|', u'{{S|locution-phrase|')
		PageTemp = PageTemp.replace(u'{{S|phrase|', u'{{S|locution-phrase|')
		PageTemp = PageTemp.replace(u'{{S|nom commun', u'{{S|nom|')
		PageTemp = PageTemp.replace(u'{{S|nom-fam|', u'{{S|nom de famille|')
		PageTemp = PageTemp.replace(u'{{S|nom-pr|', u'{{S|nom propre|')
		PageTemp = PageTemp.replace(u'{{S|symb|', u'{{S|symbole|')
		PageTemp = PageTemp.replace(u'{{S|verb|', u'{{S|verbe|')
		
		PageTemp = PageTemp.replace(u'{{S|anagramme}}', u'{{S|anagrammes}}')
		PageTemp = PageTemp.replace(u'{{S|anagr}}', u'{{S|anagrammes}}')
		PageTemp = PageTemp.replace(u'{{S|anto}}', u'{{S|antonymes}}')
		PageTemp = PageTemp.replace(u'{{S|apr}}', u'{{S|apparentés}}')
		PageTemp = PageTemp.replace(u'{{S|compos}}', u'{{S|composés}}')
		PageTemp = PageTemp.replace(u'{{S|dimin}}', u'{{S|diminutifs}}')
		PageTemp = PageTemp.replace(u'{{S|drv|en}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|drv}}', u'{{S|dérivés}}')
		PageTemp = PageTemp.replace(u'{{S|drv-int}}', u'{{S|dérivés autres langues}}')
		PageTemp = PageTemp.replace(u'{{S|etym}}', u'{{S|étymologie}}')
		PageTemp = PageTemp.replace(u'{{S|exp}}', u'{{S|expressions}}')
		PageTemp = PageTemp.replace(u'{{S|gent}}', u'{{S|gentilés}}')
		PageTemp = PageTemp.replace(u'{{S|holo}}', u'{{S|holonymes}}')
		PageTemp = PageTemp.replace(u'{{S|homo}}', u'{{S|homophones}}')
		PageTemp = PageTemp.replace(u'{{S|homonymes}}', u'{{S|homophones}}')
		PageTemp = PageTemp.replace(u'{{S|hyper}}', u'{{S|hyperonymes}}')
		PageTemp = PageTemp.replace(u'{{S|hypo}}', u'{{S|hyponymes}}')
		PageTemp = PageTemp.replace(u'{{S|méro}}', u'{{S|méronymes}}')
		PageTemp = PageTemp.replace(u'{{S|pron}}', u'{{S|prononciation}}')
		PageTemp = PageTemp.replace(u'{{S|prononciations}}', u'{{S|prononciation}}')
		PageTemp = PageTemp.replace(u'{{S|q-syn}}', u'{{S|quasi-synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|réf}}', u'{{S|références}}')
		PageTemp = PageTemp.replace(u'{{S|syn}}', u'{{S|synonymes}}')
		PageTemp = PageTemp.replace(u'{{S|trad-trier}}', u'{{S|traductions à trier}}')
		PageTemp = PageTemp.replace(u'{{S|trad}}', u'{{S|traductions}}')
		PageTemp = PageTemp.replace(u'{{S|traduction}}', u'{{S|traductions}}')
		PageTemp = PageTemp.replace(u'{{S|var}}', u'{{S|variantes orthographiques}}')
		#PageTemp = PageTemp.replace(u'{{S|variantes ortho}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|var-ortho}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|var-ortho|fr}}', u'{{S|variantes orthographiques}}')
		PageTemp = PageTemp.replace(u'{{S|voc}}', u'{{S|vocabulaire}}')
		PageTemp = PageTemp.replace(u'{{S|voir}}', u'{{S|voir aussi}}')
		PageTemp = PageTemp.replace(u'{{S|voir|en}}', u'{{S|voir aussi}}')

		if page.namespace() != 12:
			if debogage: print u'Ajout des {{voir}}'
			if PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageHS[0:1].lower() + PageHS[1:len(PageHS)] + PageTemp[PageTemp.find(u'{{voir|{{lc:{{PAGENAME}}}}}}')+len(u'{{voir|{{lc:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{lc:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageHS[0:1].upper() + PageHS[1:len(PageHS)] + PageTemp[PageTemp.find(u'{{voir|{{ucfirst:{{PAGENAME}}}}}}')+len(u'{{voir|{{ucfirst:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{ucfirst:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageHS[0:1].lower() + PageHS[1:len(PageHS)] + PageTemp[PageTemp.find(u'{{voir|{{LC:{{PAGENAME}}}}}}')+len(u'{{voir|{{LC:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{LC:{{PAGENAME}}}}'
			if PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|')] + PageHS[0:1].upper() + PageHS[1:len(PageHS)] + PageTemp[PageTemp.find(u'{{voir|{{UCFIRST:{{PAGENAME}}}}}}')+len(u'{{voir|{{UCFIRST:{{PAGENAME}}}}'):len(PageTemp)]
				summary = summary + u', subst de {{UCFIRST:{{PAGENAME}}}}'	
			if PageTemp.find(u'{{voir|') == -1 and PageTemp.find(u'{{voir/') == -1:
				PageVoir = u''
				# Liste de toutes les pages potentiellement "à voir"
				PagesCleTotal = PageHS
				if PagesCleTotal.find(PageHS.lower()) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS.lower()
				if PagesCleTotal.find(PageHS.upper()) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS.upper()
				if PagesCleTotal.find(PageHS[0:1].lower() + PageHS[1:len(PageHS)]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:1].lower() + PageHS[1:len(PageHS)]
				if PagesCleTotal.find(PageHS[0:1].upper() + PageHS[1:len(PageHS)]) == -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:1].upper() + PageHS[1:len(PageHS)]
				if PagesCleTotal.find(u'-' + PageHS[0:1].lower() + PageHS[1:len(PageHS)]) == -1: PagesCleTotal = PagesCleTotal + u'|-' + PageHS[0:1].lower() + PageHS[1:len(PageHS)]
				if PagesCleTotal.find(PageHS[0:1].lower() + PageHS[1:len(PageHS)] + u'-') == -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:1].lower() + PageHS[1:len(PageHS)] + u'-'
				if PagesCleTotal.find(u'-') != -1: PagesCleTotal = PagesCleTotal + u'|' + PagesCleTotal.replace(u'-',u'')
				if PageHS.find(u'e') != -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:PageHS.find(u'e')] + u'é' + PageHS[PageHS.find(u'e')+1:len(PageHS)] + u'|' + PageHS[0:PageHS.find(u'e')] + u'è' + PageHS[PageHS.find(u'e')+1:len(PageHS)]
				if PageHS.find(u'é') != -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:PageHS.find(u'é')] + u'e' + PageHS[PageHS.find(u'é')+1:len(PageHS)]
				if PageHS.find(u'è') != -1: PagesCleTotal = PagesCleTotal + u'|' + PageHS[0:PageHS.find(u'è')] + u'e' + PageHS[PageHS.find(u'è')+1:len(PageHS)]
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
								print u'no page'
								break
							except wikipedia.IsRedirectPage:
								print "Redirect page"
								break
							except wikipedia.LockedPage:
								print "Locked/protected page"
								break
							PageTempMod = PageTempModBegin
							if PageTempMod.find(PageHS) == -1: PageTempMod = PageTempMod[0:PageTempMod.find(u'}}')] + u'|' + PageHS + PageTempMod[PageTempMod.find(u'}}'):len(PageTempMod)]
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
				if PagesCleTotal != PageHS:
					if debogage: print u'  Différent de la page courante'
					PagesCleRestant = PagesCleTotal + u'|'
					while PagesCleRestant.find(u'|') != -1:
						HS = u'False'
						PageCourante = PagesCleRestant[0:PagesCleRestant.find(u'|')]
						if PageCourante == u'':
							if debogage: print u'PageCourante vide'
							break
						PagesCleRestant = PagesCleRestant[PagesCleRestant.find(u'|')+1:len(PagesCleRestant)]
						if PageCourante != PageHS:
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
									if PageCourante == PageHS:
										PageTemp = PageTempCle
									else:
										if debogage: print u'Première sauvegarde dédiée à {{voir}}'
										sauvegarde(PageCle,PageTempCle, summary)
							else:
								if PagesCleTotal.find(u'|' + PageCourante) != -1:
									PageTempCle = u'{{voir|' + PagesCleTotal[0:PagesCleTotal.find(u'|' + PageCourante)] + PagesCleTotal[PagesCleTotal.find(u'|' + PageCourante)+len(u'|' + PageCourante):len(PagesCleTotal)] + u'}}\n' + PageTempCle
								else:	# Cas du premier
									PageTempCle = u'{{voir' + PagesCleTotal[len(PageCourante):len(PagesCleTotal)] + u'}}\n' + PageTempCle
								if PageCourante == PageHS:
									PageTemp = PageTempCle
								else:							
									sauvegarde(PageCle,PageTempCle, summary)
					
			elif PageTemp.find(u'{{voir|') != -1:
				if debogage: print u'  Identique à la page courante'
				PageTemp2 = PageTemp[PageTemp.find(u'{{voir|'):len(PageTemp)]
				if PageTemp2.find(u'|' + PageHS + u'|') != -1 and PageTemp2.find(u'|' + PageHS + u'|') < PageTemp2.find(u'}}'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageHS + u'|')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageHS + u'|')+len(u'|' + PageHS):len(PageTemp)]
				if PageTemp2.find(u'|' + PageHS + u'}') != -1 and PageTemp2.find(u'|' + PageHS + u'}') < PageTemp2.find(u'}}'):
					PageTemp = PageTemp[0:PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageHS + u'}')] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'|' + PageHS + u'}')+len(u'|' + PageHS):len(PageTemp)]
			
			while PageTemp.find(u'{{voir|') != -1 and PageTemp.find(u'{{voir/') != -1:
				PageTemp2 = PageTemp[PageTemp.find(u'{{voir|'):len(PageTemp)]
				PageTemp = PageTemp[0:PageTemp.find(u'{{voir|') + PageTemp2.find(u'}}')+2] + PageTemp[PageTemp.find(u'{{voir|') + PageTemp2.find(u'}}')+2:len(PageTemp)]
				
			if debogage: print u' Nettoyage des {{voir}}...'
			if PageTemp.find(u'{{voir}}\n') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{voir}}\n')] + PageTemp[PageTemp.find(u'{{voir}}\n')+len(u'{{voir}}\n'):len(PageTemp)]
			if PageTemp.find(u'{{voir}}') != -1: PageTemp = PageTemp[0:PageTemp.find(u'{{voir}}')] + PageTemp[PageTemp.find(u'{{voir}}')+len(u'{{voir}}'):len(PageTemp)]
			PageTemp = HTMLUnicode.HTMLUnicode(PageTemp)
			PageTemp = PageTemp.replace(u'}}&#32;[[', u'}} [[')
			PageTemp = PageTemp.replace(u']]&#32;[[', u']] [[')
			regex = ur'\[\[([^\]]*)\|\1\]\]'
			if re.search(regex, PageTemp):
				PageTemp = re.sub(regex, ur'[[\1]]', PageTemp)

			if PageTemp.find(u'{{vérifier création automatique}}') != -1:
				if debogage: print u' {{vérifier création automatique}} trouvé'
				PageTemp2 = PageTemp
				Langues = u'|'
				while PageTemp2.find(u'{{langue|') > 0:
					PageTemp2 = PageTemp2[PageTemp2.find(u'{{langue|')+len(u'{{langue|'):]
					Langues += u'|' + PageTemp2[:PageTemp2.find(u'}}')]
				if Langues != u'|':
					PageTemp = PageTemp.replace(u'{{vérifier création automatique}}', u'{{vérifier création automatique' + Langues + u'}}')
				#raw_input(PageTemp.encode(config.console_encoding, 'replace'))
					
			# Clés de tri
			if debogage: print u'Clés de tri'
			PageTemp = PageTemp.replace(u'{{DEFAULTSORT:', u'{{clé de tri|')
			PageTemp = PageTemp.replace(u'{{CLEDETRI:', u'{{clé de tri|')
			PageTemp = PageTemp.replace(u'{{clef de tri|', u'{{clé de tri|')
			while PageTemp.find(u'\n{clé de tri') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'\n{clé de tri')+1] + u'{' + PageTemp[PageTemp.find(u'\n{clé de tri'):len(PageTemp)]
				
			ClePage = CleTri
			if PageTemp.find(u'{{clé de tri') == -1 and ClePage != u'' and ClePage.lower() != PageHS.lower():
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
					if CleTri.lower() == PageHS.lower():
					summary = summary + u', {{clé de tri}} supprimée'
					PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|')] + PageTemp[PageTemp.find(u'{{clé de tri|')+len(u'{{clé de tri|')+PageTemp2.find(u'}}')+2:len(PageTemp)]'''
			if debogageLent: raw_input(PageTemp.encode(config.console_encoding, 'replace'))
			
			baratin = u'{{clé de tri|}}<!-- supprimer si le mot ne contient pas de caractères accentués ni de caractères typographiques (par ex. trait d’union ou apostrophe) ; sinon suivez les instructions à [[Modèle:clé de tri]] -->'
			if PageTemp.find(baratin) != -1:
				PageTemp = PageTemp[0:PageTemp.find(baratin)] + PageTemp[PageTemp.find(baratin)+len(baratin):len(PageTemp)]
				summary = summary + u', {{clé de tri|}} supprimée'
			if PageTemp.find(u'{{clé de tri|}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|}}')] + PageTemp[PageTemp.find(u'{{clé de tri|}}')+len(u'{{clé de tri|}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri|}} supprimée'
			if PageTemp.find(u'{{clé de tri}}') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri}}')] + PageTemp[PageTemp.find(u'{{clé de tri}}')+len(u'{{clé de tri}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri}} supprimée'
			if PageTemp.find(u'{{clé de tri|' + PageHS.lower() + u'}}') != -1 and PageTemp.find(u'{{S|verb pronominal|fr}}') == -1:
				PageTemp = PageTemp[0:PageTemp.find(u'{{clé de tri|' + PageHS.lower() + u'}}')] + PageTemp[PageTemp.find(u'{{clé de tri|' + PageHS.lower() + u'}}')+len(u'{{clé de tri|' + PageHS.lower() + u'}}'):len(PageTemp)]
				summary = summary + u', {{clé de tri}} supprimée'

			if debogage: print u'Remplacements des balises'
			PageTemp = re.sub(ur'\[\[Category:', ur'[[Catégorie:', PageTemp)
			while PageTemp.find(u'</br>') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'</br>')] + u'<br/>' + PageTemp[PageTemp.find(u'</br>')+len(u'</br>'):len(PageTemp)]
			while PageTemp.find(u'<sup/>') != -1:
				PageTemp = PageTemp[0:PageTemp.find(u'<sup/>')] + u'</sup>' + PageTemp[PageTemp.find(u'<sup/>')+len(u'<sup/>'):len(PageTemp)]
		
			# Ajout de catégories
			'''if PageHS[len(PageHS)-len(u'ejar'):] == u'ejar':
				if PageTemp.find(u'{{langue|ca}}') != -1 and PageTemp.find(u'[[Catégorie:Verbes en catalan suffixés en -ejar]]') == -1:
					PageTemp2 = PageTemp[:PageTemp.find(u'{{langue|ca}}')+len(u'{{langue|ca}}'):]
					if PageTemp2.find(u'\n== {{langue|') != -1:
						if debogage: print u'cat au milieu'
						PageTemp = PageTemp[:PageTemp.find(u'{{langue|ca}}')+len(u'{{langue|ca}}')+PageTemp2.find(u'\n== {{langue|')] + u'\n[[Catégorie:Verbes en catalan suffixés en -ejar]]\n\n' + PageTemp[PageTemp.find(u'{{langue|ca}}')+len(u'{{langue|ca}}')+PageTemp2.find(u'\n== {{langue|'):]
					else:
						if debogage: print u'cat à la fin'
						PageTemp = PageTemp + u'\n\n[[Catégorie:Verbes en occitan suffixés en -ejar]]\n'

				if PageTemp.find(u'{{langue|oc}}') != -1 and PageTemp.find(u'[[Catégorie:Verbes en occitan suffixés en -ejar]]') == -1:
					PageTemp2 = PageTemp[PageTemp.find(u'{{langue|oc}}')+len(u'{{langue|oc}}'):]
					if PageTemp2.find(u'\n== {{langue|') != -1:
						if debogage: print u'cat au milieu'
						PageTemp = PageTemp[:PageTemp.find(u'{{langue|oc}}')+len(u'{{langue|oc}}')+PageTemp2.find(u'\n== {{langue|')] + u'\n[[Catégorie:Verbes en occitan suffixés en -ejar]]\n\n' + PageTemp[PageTemp.find(u'{{langue|oc}}')+len(u'{{langue|oc}}')+PageTemp2.find(u'\n== {{langue|'):]
					else:
						if debogage: print u'cat à la fin'
						PageTemp = PageTemp + u'\n\n[[Catégorie:Verbes en occitan suffixés en -ejar]]\n'
			
			elif PageHS[len(PageHS)-len(u'-able'):] == u'-able':
				if PageTemp.find(u'{{langue|fr}}') != -1 and PageTemp.find(u'[[Catégorie:Mots en français suffixés en -able]]') == -1:
				
				if PageTemp.find(u'{{langue|en}}') != -1 and PageTemp.find(u'[[Category:Mots en anglais suffixés en -able]]') == -1:'''

		if debogage: print u'Remplacements des modèles'
		PageTemp = re.sub(ur'{{(formatnum|Formatnum|FORMATNUM)\:([0-9]*) ', ur'{{\1:\2', PageTemp)
		PageTemp = re.sub(ur'{{terme*\|Registre neutre}} *', ur'', PageTemp)
		# Ligne de forme
		while PageTemp.find(u'[[' + PageHS + u']]') != -1:
			PageTemp = PageTemp[:PageTemp.find(u'[[' + PageHS + u']]')] + u'\'\'\'' + PageHS + u'\'\'\'' + PageTemp[PageTemp.find(u'[[' + PageHS + u']]')+len(u'[[' + PageHS + u']]'):]
		while PageTemp.find(u'{{fr-rég}}\'\'\'') != -1:
			PageTemp = PageTemp[:PageTemp.find(u'{{fr-rég}}\'\'\'')+len(u'{{fr-rég}}')] + u'\n' + PageTemp[PageTemp.find(u'{{fr-rég}}\'\'\'')+len(u'{{fr-rég}}'):]
		while PageTemp.find(u'{{es-rég}}\'\'\'') != -1:
			PageTemp = PageTemp[:PageTemp.find(u'{{es-rég}}\'\'\'')+len(u'{{es-rég}}')] + u'\n' + PageTemp[PageTemp.find(u'{{es-rég}}\'\'\'')+len(u'{{es-rég}}'):]
		while PageTemp.find(u'{{pt-rég}}\'\'\'') != -1:
			PageTemp = PageTemp[:PageTemp.find(u'{{pt-rég}}\'\'\'')+len(u'{{pt-rég}}')] + u'\n' + PageTemp[PageTemp.find(u'{{pt-rég}}\'\'\'')+len(u'{{pt-rég}}'):]
		PageTemp = PageTemp.replace(u']] {{imperf}}', u']] {{imperf|nocat=1}}')
		PageTemp = PageTemp.replace(u']] {{perf}}', u']] {{perf|nocat=1}}')
		PageTemp = PageTemp.replace(u'{{perf}} / \'\'\'', u'{{perf|nocat=1}} / \'\'\'')
		
		PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n)\# *', ur"\1'''" + PageHS + ur"''' {{pron}}\n# ", PageTemp)
		if PageTemp.find(u'{{Latn') == -1 and PageTemp.find(u'{{Grek') == -1 and PageTemp.find(u'{{Cyrl') == -1 and PageTemp.find(u'{{Armn') == -1 and PageTemp.find(u'{{Geor') == -1 and PageTemp.find(u'{{Hebr') == -1 and PageTemp.find(u'{{Arab') == -1 and PageTemp.find(u'{{Syrc') == -1 and PageTemp.find(u'{{Thaa') == -1 and PageTemp.find(u'{{Deva') == -1 and PageTemp.find(u'{{Hang') == -1 and PageTemp.find(u'{{Hira') == -1 and PageTemp.find(u'{{Kana') == -1 and PageTemp.find(u'{{Hrkt') == -1 and PageTemp.find(u'{{Hani') == -1 and PageTemp.find(u'{{Jpan') == -1 and PageTemp.find(u'{{Hans') == -1 and PageTemp.find(u'{{Hant') == -1 and PageTemp.find(u'{{zh-mot') == -1 and PageTemp.find(u'{{kohan') == -1 and PageTemp.find(u'{{ko-nom') == -1 and PageTemp.find(u'{{la-verb') == -1 and PageTemp.find(u'{{grc-verb') == -1 and PageTemp.find(u'{{polytonique') == -1 and PageTemp.find(u'FAchar') == -1:
			if debogage: print u'Ajout du mot vedette'
			PageTemp = re.sub(ur'([^d\-]+\-\|[a-z]+\}\}\n\{\{[^\n]*\n)\# *', ur"\1'''" + PageHS + ur"''' {{pron}}\n# ", PageTemp)
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
		regex = ur'\{\{ISBN\|([^\}]*)\}\}'
		if re.search(regex, PageTemp):
			PageTemp = re.sub(regex, ur'ISBN \1', PageTemp)

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
			while PageTemp.find(u'{{pron-rég|' + ModRegion[m] + u'|') != -1:
				PageTemp = PageTemp[:PageTemp.find(u'{{pron-rég|' + ModRegion[m] + u'|')+len('{{pron-rég|')-1] + u'{{' + ModRegion[m] + u'|nocat=1}}' + PageTemp[PageTemp.find(u'{{pron-rég|' + ModRegion[m] + u'|')+len(u'{{pron-rég|' + ModRegion[m]):]

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
		while PageTemp.find(u'\n# [[' + PageHS + u'|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'\n# [[' + PageHS + u'|')+len(u'\n# [[')] + u'#fr' + PageTemp[PageTemp.find(u'\n# [[' + PageHS + u'|')+len(u'\n# [[' + PageHS):len(PageTemp)]
			
		# Retrait des espaces intégrés au modèle
		while PageTemp.find(u'|pinv= ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|pinv= ')+len(u'|pinv=')] + PageTemp[PageTemp.find(u'|pinv= ')+len(u'|pinv= '):len(PageTemp)]
		while PageTemp.find(u'|pinv=. ') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'|pinv=. ')+len(u'|pinv=.')] + PageTemp[PageTemp.find(u'|pinv=. ')+len(u'|pinv=. '):len(PageTemp)]
		#while PageTemp.find(u'|pinv=&nbsp;') != -1:
		#	PageTemp = PageTemp[0:PageTemp.find(u'|pinv=&nbsp;')+len(u'|pinv=')] + PageTemp[PageTemp.find(u'|pinv=&nbsp;')+len(u'|pinv=&nbsp;'):len(PageTemp)]
			
		# Modèles trop courts
		if debogage: print u'Modèles courts'
		while PageTemp.find(u'{{fp}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{fp}}')+4] + u'lur' + PageTemp[PageTemp.find(u'{{fp}}')+4:len(PageTemp)] 
		while PageTemp.find(u'{{mp}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{mp}}')+4] + u'lur' + PageTemp[PageTemp.find(u'{{mp}}')+4:len(PageTemp)] 
		while PageTemp.find(u'{{np}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{np}}')+4] + u'lur' + PageTemp[PageTemp.find(u'{{np}}')+4:len(PageTemp)]
		while PageTemp.find(u'{{mascul}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{mascul}}')] + u'{{au masculin}}' + PageTemp[PageTemp.find(u'{{mascul}}')+len(u'{{mascul}}'):len(PageTemp)] 
		while PageTemp.find(u'{{fémin}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{fémin}}')] + u'{{au féminin}}' + PageTemp[PageTemp.find(u'{{fémin}}')+len(u'{{fémin}}'):len(PageTemp)]
		while PageTemp.find(u'{{femin}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{femin}}')] + u'{{au féminin}}' + PageTemp[PageTemp.find(u'{{femin}}')+len(u'{{femin}}'):len(PageTemp)] 
		while PageTemp.find(u'{{sing}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{sing}}')] + u'{{au singulier}}' + PageTemp[PageTemp.find(u'{{sing}}')+len(u'{{sing}}'):len(PageTemp)]  
		while PageTemp.find(u'{{plur}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{plur}}')] + u'{{au pluriel}}' + PageTemp[PageTemp.find(u'{{plur}}')+len(u'{{plur}}'):len(PageTemp)] 
		while PageTemp.find(u'{{pluri}}') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{pluri}}')] + u'{{au pluriel}}' + PageTemp[PageTemp.find(u'{{pluri}}')+len(u'{{pluri}}'):len(PageTemp)] 
		while PageTemp.find(u'{{mascul|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{mascul|')] + u'{{au masculin|' + PageTemp[PageTemp.find(u'{{mascul|')+len(u'{{mascul|'):len(PageTemp)] 
		while PageTemp.find(u'{{fémin|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{fémin|')] + u'{{au féminin|' + PageTemp[PageTemp.find(u'{{fémin|')+len(u'{{fémin|'):len(PageTemp)]
		while PageTemp.find(u'{{femin|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{femin|')] + u'{{au féminin|' + PageTemp[PageTemp.find(u'{{femin|')+len(u'{{femin|'):len(PageTemp)] 
		while PageTemp.find(u'{{sing|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{sing|')] + u'{{au singulier|' + PageTemp[PageTemp.find(u'{{sing|')+len(u'{{sing|'):len(PageTemp)]  
		while PageTemp.find(u'{{plur|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{plur|')] + u'{{au pluriel|' + PageTemp[PageTemp.find(u'{{plur|')+len(u'{{plur|'):len(PageTemp)] 
		while PageTemp.find(u'{{pluri|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{pluri|')] + u'{{au pluriel|' + PageTemp[PageTemp.find(u'{{pluri|')+len(u'{{pluri|'):len(PageTemp)] 
		while PageTemp.find(u'{{dét|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{dét|')+2] + u'déterminé' + PageTemp[PageTemp.find(u'{{dét|')+len(u'{{dét'):len(PageTemp)]
		while PageTemp.find(u'{{dén|') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{dén|')+2] + u'dénombrable' + PageTemp[PageTemp.find(u'{{dén|')+len(u'{{dén'):len(PageTemp)]

		# Faux homophones : lemme et sa flexion
		if debogage: print u'Faux homophones'
		if PageTemp.find(u'|flexion}}') != -1 and PageHS[len(PageHS)-1:len(PageHS)] == u's' and PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']],') == -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']]')+len(u'{{S|homophones}}\n*[[' + PageHS[0:len(PageHS)-1] + u']]')+1:len(PageTemp)]
		elif PageTemp.find(u'|flexion}}') != -1 and PageHS[len(PageHS)-1:len(PageHS)] == u's' and PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']]\n*') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']]') != -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']] ') == -1 and PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']],') == -1:
			PageTemp = PageTemp[0:PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']]')] + PageTemp[PageTemp.find(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']]')+len(u'{{S|homophones}}\n* [[' + PageHS[0:len(PageHS)-1] + u']]')+1:len(PageTemp)]
		
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
				regex = ur'\({{p}} : [\[\']*' + PageHS + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + PageHS + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageHS + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				regex = ur'\({{f}} : [\[\']*' + PageHS + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + PageHS + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageHS + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'{{' + ModeleGent[l][1] + u'|pron=}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				# Son
				if debogage: print u' son'
				regex = ur'(\n\'\'\'' + PageHS + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|[pron\=]*)}}'
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
				regex = ur'\({{p}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][2] + ur'[\]\']*, {{f}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][3] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][4] + ur'[\]\']*\)'
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'{{' + ModeleGent[l][1] + u'|' + PageHS[:-1] + ur'}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				regex = ur'\({{f}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][3] + ur'[\]\']*, {{mplur}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][2] + ur'[\]\']*, {{fplur}} : [\[\']*' + PageHS[:-1] + ModeleGent[l][4] + ur'[\]\']*\)'
				if debogage: print regex.encode(config.console_encoding, 'replace')
				if re.search(regex, PageTemp):
					PageTemp = re.sub(regex, ur'{{' + ModeleGent[l][1] + u'|' + PageHS[:-1] + ur'}}', PageTemp)
					summary = summary + u', conversion des liens flexions en modèle boite'
				# Son
				if debogage: print u' son'
				regex = ur'(\n\'\'\'' + PageHS + u'\'\'\' *{{pron\|)([^\|]+)(\|fr}}[ {}:mf]*)({{' + ModeleGent[l][1] + ur'\|' + PageHS[:-1] + ur')}}'
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
					langue = CleDeTri.CleDeTri(langues.langues[langue1].decode("utf8"))
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
						langue2 = CleDeTri.CleDeTri(langues.langues[langue2].decode("utf8"))
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
		
		# Remplacement des codes langues
		if debogage: print u'Remplacement des anciens codes langue'
		while PageTemp.find(u'=prv=') != -1:
			PageTemp = PageTemp[0:PageTemp.find(u'=prv=')] + u'langue|oc' + PageTemp[PageTemp.find(u'=prv=')+len(u'=prv='):len(PageTemp)]
		AncienModele = range(1, 13)
		NouveauModele = range(1, 13)
		AncienModele[1] = u'ko-hanja'
		NouveauModele[1] = u'ko-Hani'
		AncienModele[2] = u'be-x-old'
		NouveauModele[2] = u'be-tarask'
		AncienModele[3] = u'zh-min-nan'
		NouveauModele[3] = u'nan'
		AncienModele[4] = u'lsf'
		NouveauModele[4] = u'fsl'
		AncienModele[5] = u'arg'
		NouveauModele[5] = u'an'
		AncienModele[6] = u'nav'
		NouveauModele[6] = u'nv'
		AncienModele[7] = u'prv'
		NouveauModele[7] = u'oc'
		AncienModele[8] = u'nds-NL'
		NouveauModele[8] = u'nds-nl'	
		AncienModele[9] = u'gsw-FR'
		NouveauModele[9] = u'gsw-fr'
		AncienModele[10] = u'zh-sc'
		NouveauModele[10] = u'zh-Hans'
		AncienModele[11] = u'roa-rup'
		NouveauModele[11] = u'rup'
		for p in range(1,12):
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
			if PageHS != u'«' and PageTemp.find(u'«') != -1 and PageTemp.find(u'«') != PageTemp.find(u'« '):
				PageTemp = PageTemp[0:PageTemp.find(u'«')+1] + u' ' + PageTemp[PageTemp.find(u'«')+1:len(PageTemp)]
			if PageHS != u'»' and PageTemp.find(u'»') != -1 and PageTemp.find(u'»')-1 != PageTemp.find(u' »'):
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
			if NouvelleLangue == True and socket.gethostname() != "willow" and socket.gethostname() != "yarrow" and socket.gethostname() != "nightshade" and PageTemp.find(u'-erreur-') == -1 and PageHS != u'six':
				if debogage: print u' Anagrammes pour ' + codelangue
				if PageTemp.find(u'{{S|anagr') == -1 and PageHS.find(u' ') == -1 and len(PageHS) <= TailleAnagramme: 
					anagrammes = anagram(PageHS)
					ListeAnagrammes = u''
					for anagramme in anagrammes:
						if anagramme != PageHS:
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
									except wikipedia.LockedPage: break
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
									print u'pb regex interwiki'
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
							if Modele[p2] == ModeleT or Modele[p2] == ModeleT[0:1].lower() + ModeleT[1:len(ModeleT)]:
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
					
					elif Modele[p] == u'pron-rég':
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
					elif Modele[p] == u'aphérèse' or Modele[p] == u'apocope' or Modele[p] == u'mot-valise' or Modele[p] == u'contraction' or Modele[p] == u'contr' or (
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
							if PageHS[len(PageHS)-2:len(PageHS)] == u'ar' or PageHS[len(PageHS)-4:len(PageHS)] == u'arsi':
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
							elif PageHS[len(PageHS)-2:len(PageHS)] == u'er' or PageHS[len(PageHS)-4:len(PageHS)] == u'ersi':
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
							elif PageHS[len(PageHS)-2:len(PageHS)] == u'ir' or PageHS[len(PageHS)-4:len(PageHS)] == u'irsi':
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
							if PageHS[len(PageHS)-2:len(PageHS)] == u'ar' or PageHS[len(PageHS)-4:len(PageHS)] == u'ar-se':
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
							elif PageHS[len(PageHS)-2:len(PageHS)] == u'er' or PageHS[len(PageHS)-4:len(PageHS)] == u'er-se':
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
							elif PageHS[len(PageHS)-2:len(PageHS)] == u'ir' or PageHS[len(PageHS)-4:len(PageHS)] == u'ir-se':
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
							if PageHS[len(PageHS)-3:len(PageHS)] == u'are' or PageHS[len(PageHS)-4:len(PageHS)] == u'arsi':
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
							elif PageHS[len(PageHS)-3:len(PageHS)] == u'ere' or PageHS[len(PageHS)-4:len(PageHS)] == u'ersi':
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
							elif PageHS[len(PageHS)-3:len(PageHS)] == u'ire' or PageHS[len(PageHS)-4:len(PageHS)] == u'irsi':
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

	) or (PageTemp.find(u'Catégorie:Fabacées'
	) != -1 and (PageTemp.find(u':Catégorie:Fabacées') < PageTemp.find(u'{{langue|') and PageTemp.find(u'{{langue|') != -1 or PageTemp.find(u'{{langue|') == -1
	) and (PageTemp.find(u':Catégorie:Fabacées') + 1 != PageTemp.rfind(u'Catégorie:Fabacées'))):
							PageEnd = PageEnd + PageTemp[0:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
						PageTemp = PageTemp[PageTemp.find("}}")+2:len(PageTemp)]
						break
					elif Modele[p] == u'médecine' or Modele[p] == u'méde' or Modele[p] == u'vétérinaire' or Modele[p] == u'chirurgie' or Modele[p] == u'chir' or Modele[p] == u'pharmacologie' or Modele[p] == u'pharmacol' or Modele[p] == u'pharmacie':
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
					elif Modele[p] == u'chimie' or Modele[p] == u'chim' or Modele[p] == u'biochimie' or Modele[p] == u'bioch':
						if (EstCodeLangue == "false"
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
						if debogage: print u' langue distante : ' + PageTemp2[0:PageTemp2.find(u'|')]
						if PageTemp2[0:PageTemp2.find(u'|')] == "": break
						elif PageTemp3.find(u'}}') == "" or not PageTemp3.find(u'}}'):
							if debogage: print u'  aucun mot distant'
							if PageEnd.rfind('<!--') == -1 or PageEnd.rfind('<!--') < PageEnd.rfind('-->'):
								# On retire le modèle pour que la page ne soit plus en catégorie de maintenance
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
								if debogage: print u'  ServerError'
								break
							except wikipedia.NoSuchSite:
								PageEnd = PageEnd + PageTemp[0:4] + "--"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  NoSuchSite'
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
						if debogage:
							print u' Page distante : '
							print PageExterne.encode(config.console_encoding, 'replace')
						
						# Connexions aux Wiktionnaires pour vérifier la présence de la page (sous-entendu dans sa langue maternelle)
						if SiteExt != u'' and PageExterne != u'':
							try:
								pageExt = Page(SiteExt,PageExterne)
							except wikipedia.NoPage:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  NoPage'
								break
							except wikipedia.BadTitle:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  BadTitle'
								break
							except wikipedia.InvalidTitle:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  InvalidTitle'
								break
							if pageExt.exists():
								PageEnd = PageEnd + PageTemp[0:4] + "+"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  exists'
								break
							else:
								PageEnd = PageEnd + PageTemp[0:4] + "-"
								PageTemp = PageTemp[position:len(PageTemp)]
								if debogage: print u'  not exists'
								break
						elif debogage:
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
							print "NoPage flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
							break
						except wikipedia.SectionError:
							print "SectionError flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
							break
						except wikipedia.IsRedirectPage:
							print "Redirect page flex-verb : " + Infinitif.encode(config.console_encoding, 'replace')
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
							elif Page2.find(u'|groupe=1') != -1 or Page2.find(u'|grp=1') != -1:
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
							elif Page2.find(u'{{impers') == -1 and (Page2.find(u'|groupe=2') != -1 or Page2.find(u'|grp=2') != -1):
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
									PageTemp = PageTemp[0:PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion')] + u'|ind.ps.3s=oui' + PageTemp[PageTemp.find(u'fr-verbe-flexion')+len(u'fr-verbe-flexion'):len(PageTemp)]
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
							elif Page2.find(u'|groupe=3') != -1 or Page2.find(u'|grp=3') != -1:
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
						if Section.index(TitreSection) < limit1:
							# Paragraphe définition
							EstCodeLangue = "true"
							trad = u'false'
							# Ajouts en fin de ligne de forme
							if TitreSection == 'nom' and (codelangue == 'fr' or codelangue == 'es' or codelangue == 'pt' or codelangue == 'it' or codelangue == 'de' or codelangue == 'ar' or codelangue == 'ru'):
								if debogage: print u'Recherche du genre manquant'
								if PageTemp.find(u'\n\'\'\'' + PageHS + u'\'\'\'') != -1 and PageTemp.find(u'\n\'\'\'' + PageHS + u'\'\'\'') < 100:
									PageTemp2 = PageTemp[PageTemp.find(u'\n\'\'\'' + PageHS + u'\'\'\'')+len(u'\n\'\'\'' + PageHS + u'\'\'\''):]
									if (PageTemp2.find(u'{{genre') > PageTemp2.find(u'\n') or PageTemp2.find(u'{{genre') == -1) and (PageTemp2.find(u'{{m') > PageTemp2.find(u'\n') or PageTemp2.find(u'{{m') == -1) and (PageTemp2.find(u'{{f') > PageTemp2.find(u'\n') or PageTemp2.find(u'{{f') == -1) and (PageTemp2.find(u'{{n') > PageTemp2.find(u'\n') or PageTemp2.find(u'{{n') == -1):
										PageTemp = PageTemp[:PageTemp.find(u'\n\'\'\'' + PageHS + u'\'\'\'')+len(u'\n\'\'\'' + PageHS + u'\'\'\'')+PageTemp2.find(u'\n')] + u' {{genre|' + codelangue + u'}}' + PageTemp[PageTemp.find(u'\n\'\'\'' + PageHS + u'\'\'\'')+len(u'\n\'\'\'' + PageHS + u'\'\'\'')+PageTemp2.find(u'\n'):]

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
							if debogage: print u'  ' + str(p)
							if debogage: print u'  ' + str(Section.index(TitreSection))
							if debogage: print PageTemp[:PageTemp.find(u'}}')].encode(config.console_encoding, 'replace')
							TitreTemp = PageHS
							if codelangue == u'es':
								if TitreTemp.find(u'ñ') !=-1: TitreTemp = TitreTemp.replace(u'ñ',u'n€')
								if TitreTemp.find(u'ñ'.upper()) !=-1: TitreTemp = TitreTemp.replace(u'ñ'.upper(),u'n€')
								
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
								
							if TitreTemp != PageHS:
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
								if debogage: print u'avec'
								PageEnd = PageEnd + PageTemp[:position] + "|" + codelangue + "}}"
							else:
								if debogage: print u'sans'
								PageEnd = PageEnd + PageTemp[:position] + "|nocat=1}}"
						else:
							PageEnd = PageEnd + PageTemp[:PageTemp.find(u'}}')+2]
							
					elif p < limit5:
						if debogage: print "limit5"
						if debogage: print u'Catégorisée quel que soit EstCodeLangue (ex : ébauches)'
						if codelangue:
							PageEnd = PageEnd + PageTemp[0:position] + "|" + codelangue + "}}"
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
		if PageHS.find(u' ') != -1:
			PageLemme = u''
			page2 = Page(site,PageHS[:PageHS.find(u' ')])
			if page2.exists():
				if page.namespace() !=0:
					print u'Page non traitée l 4598'
					return
				else:
					try:
						PageLemme = page2.get()
					except wikipedia.NoPage:
						print "NoPage l 4605"
					except wikipedia.LockedPage: 
						print "Locked l 4607"
					except wikipedia.IsRedirectPage: 
						print "IsRedirect l 4609"
			else:
				print "NoPage l 4611"
			if PageLemme != u'':
				genre = u''
				if PageLemme.find(u'|fr}} {{m}}') != -1:
					genre = u'{{m}}'
				elif PageLemme.find(u'|fr}} {{f}}') != -1:
					genre = u'{{f}}'
				if genre != u'':
					PageEnd = PageEnd.replace(u'{{genre|fr}}', genre)
			
		# Liens vers les conjugaisons régulières
		'''if debogage: print u'Ajout de {{conj}}'
		if PageEnd.find(u'[[Image:') == -1:	# Bug (ex : broyer du noir, définir)	{{lang/span\|[a-z\-]*\|([^}]*)}}
			langues = [ (u'es', u'ar', u'arsi', u'er', u'ersi', u'ir', u'irsi'),
					 (u'pt', u'ar', u'ar-se', u'er', u'er-se', u'ir', u'ir-se'),
					 (u'it', u'are', u'arsi', u'ere', u'ersi', u'ire', u'irsi'),
					 (u'fr', u'er', u'er', u'ir', u'ir', u're', u'ar')
				   ]
			for (langue,premier,ppron,deuxieme,dpron,troisieme,tpron) in langues:
				if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}').search(PageEnd) and not re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'}}.*\n*.*{{conj[a-z1-3\| ]*').search(PageEnd):
					if re.compile('{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*\n*[ ^\[]*{{pron\|').search(PageEnd):
						if PageHS[len(PageHS)-len(premier):len(PageHS)] == premier or PageHS[len(PageHS)-len(ppron):len(PageHS)] == ppron:
							try:
								i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
								PageEnd = PageEnd[:i1] + u' {{conj|grp=1|' + langue + u'}}' + PageEnd[i1:]
							except:
								print PageHS.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + premier
						elif PageHS[len(PageHS)-len(premier):len(PageHS)] == deuxieme or PageHS[len(PageHS)-len(ppron):len(PageHS)] == dpron:
							try:
								i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
								PageEnd = PageEnd[:i1] + u' {{conj|grp=2|' + langue + u'}}' + PageEnd[i1:]
							except:
								print PageHS.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + deuxieme
						elif PageHS[len(PageHS)-len(premier):len(PageHS)] == troisieme or PageHS[len(PageHS)-len(ppron):len(PageHS)] == tpron:
							try:
								i1 = re.search(u'{{\-verb[e]*\-[pr\-]*\|[ ]*' + langue + u'.*}}\n.*}}',PageEnd).end()
								PageEnd = PageEnd[:i1] + u' {{conj|grp=3|' + langue + u'}}' + PageEnd[i1:]
							except:
								print PageHS.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' ' + troisieme
					else:
						if PageHS[len(PageHS)-len(premier):len(PageHS)] == premier or PageHS[len(PageHS)-len(ppron):len(PageHS)] == ppron:
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
						elif PageHS[len(PageHS)-len(premier):len(PageHS)] == deuxieme or PageHS[len(PageHS)-len(ppron):len(PageHS)] == dpron:
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
								print PageHS.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
						elif PageHS[len(PageHS)-len(premier):len(PageHS)] == troisieme or PageHS[len(PageHS)-len(ppron):len(PageHS)] == tpron:
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
								print PageHS.encode(config.console_encoding, 'replace') + u' ' + langue.encode(config.console_encoding, 'replace') + u' sans {{pron}}'
		'''
		'''# Recherche de bug
		if PageEnd.find(u'{{trad-début|{{') != -1:		
			txtfile = codecs.open(u'articles_listed.txt', 'a', 'utf-8')
			txtfile.write(u'* [[' + PageHS + u']]\n')
			txtfile.close()'''
	else:
		PageEnd = PageTemp

	# Interwikis
	if PageEnd.find(u'{{langue|en}}') != -1 and PageEnd.find(u'[[en:') == -1:
		pageEN = Page(siteEN,PageHS)
		if pageEN.exists():
			try:
				PageEN = pageEN.get()
			except wikipedia.NoPage:
				print "NoPage l 1296"
				return
			except wikipedia.IsRedirectPage: 
				print "IsRedirect l 1299"
				return
			if PageEN.find(u'==English==') != -1:
				PageEnd = PageEnd + u'\n[[en:' + PageHS + u']]'
				summary = summary + u', ajout d\'interwiki'
				
	# Syntaxe humaine imprévue de {{terme}}
	PageEnd = PageEnd.replace(u'{{nom|nocat=1}}', u"''(Nom)''")
	
	if debogage: print u'Test des URL'
	#PageEnd = hyperlynx.hyperlynx(PageEnd)
	if debogage: print (u'--------------------------------------------------------------------------------------------')
	if PageEnd != PageBegin:
		# Modifications mineures, ne justifiant pas une édition à elles seules
		PageEnd = PageEnd.replace(u'  ', u' ')
		PageEnd = PageEnd.replace(u'\n\n\n\n', u'\n\n\n')
		sauvegarde(page,PageEnd, summary)
	elif debogage:
		print "Aucun changement"
		

def trim(s):
    return s.strip(" \t\n\r\0\x0B")

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
			PageHS = PagesHS.readline()
			fin = PageHS.find("\t")
			PageHS = PageHS[0:fin]
			if PageHS == '': break
			if PageHS.find(u'[[') != -1:
				PageHS = PageHS[PageHS.find(u'[[')+2:len(PageHS)]
			if PageHS.find(u']]') != -1:
				PageHS = PageHS[0:PageHS.find(u']]')]
			# Conversion ASCII => Unicode (pour les .txt)
			modification(HTMLUnicode.HTMLUnicode(PageHS))
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
def crawlerUser(username,jusqua):
	compteur = 0
	gen = pagegenerators.UserContributionsGenerator(username)
	for Page in pagegenerators.PreloadingGenerator(gen,100):
		modification(Page.title())
		compteur = compteur + 1
		if compteur > jusqua: break

# Toutes les redirections
def crawlerRedirects():
	for Page in site.allpages(start=u'', namespace=0, includeredirects='only'):
		modification(Page.title())	
										
# Traitement de toutes les pages du site
def crawlerAll(start):
	gen = pagegenerators.AllpagesPageGenerator(start,namespace=0,includeredirects=False)
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
			except wikipedia.LockedPage: return
			except wikipedia.ServerError: return
			except wikipedia.BadTitle: return
			except pywikibot.EditConflict: return
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
		result = raw_input("Sauvegarder ? (o/n) ")
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
if len(sys.argv) > 1:
	if sys.argv[1] == u'txt':
		TraitementFichier = crawlerFile(u'articles_WTin.txt')
	elif sys.argv[1] == u'cat':
		TraitementCategorie = crawlerCat(u'Catégorie:Pages à vérifier car créées automatiquement',False,u'')
	else:
		TraitementPage = modification(sys.argv[1])	# Format http://tools.wmflabs.org/jackbot/xtools/public_html/unicode-HTML.php
else:
	# Quotidiennement :
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Codes langue manquants',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Flexions à vérifier',True,u'')
	TraitementCategorie = crawlerCat(u'Catégorie:Appels de modèles incorrects:fr-verbe-flexion incomplet',False,u'')
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
	TraitementCategorie = crawlerCat(u'Catégorie:Wiktionnaire:Utilisation d\'anciens modèles de section',True,u'')
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
TraitementRecherche = crawlerSearch(u'"en terme de"')
TraitementUtilisateur = crawlerUser(u'Utilisateur:JackBot', 800)
TraitementRedirections = crawlerRedirects()
TraitementTout = crawlerAll(u'')
	
python delete.py -lang:fr -family:wiktionary -file:articles_WTin.txt
python movepages.py -lang:fr -family:wiktionary -pairs:"articles_WTin.txt" -noredirect -pairs
python interwiki.py -lang:fr -family:wiktionary -wiktionary -new:60
'''

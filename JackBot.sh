#*** Native ***
#python core/pwb.py replace       -lang:commons -family:commons -file:articles_commons.txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
#python core/pwb.py movepages     -lang:fr -family:wiktionary -pairs:"articles_fr_wiktionary.txt" -noredirect -pairs
#python core/pwb.py protect       -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop
#python core/pwb.py delete        -lang:fr -family:wikiversity -file:"scripts/JackBot/articles_fr_wiktionary.txt"
#python core/pwb.py delete        -lang:en -family:wikibooks -cat:"Candidates for speedy deletion"
#python core/pwb.py touch         -lang:fr -family:wiktionary -cat:"Pluriels manquants en français" -namespace:0
#python core/pwb.py touch         -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais" -namespace:0
#python core/pwb.py touch         -lang:en -family:wikibooks -transcludes:"Template:Qr-em" -namespace:0

#python core/pwb.py clean_sandbox -lang:fr -family:wiktionary  -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikibooks   -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikinews    -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikiversity -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikisource  -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikiquote   -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikivoyage  -always
##python core/pwb.py clean_sandbox -lang:fr -family:wikipedia   -always
#python core/pwb.py clean_sandbox -lang:en -family:wikibooks   -always
##python core/pwb.py clean_sandbox -lang:en -family:wikiquote   -always

python core/pwb.py redirect.py double -always -family:wikipedia -lang:fr
python core/pwb.py redirect.py double -always -family:wikipedia -lang:pl
python core/pwb.py redirect.py double -always -family:wikipedia -lang:se
python core/pwb.py redirect.py double -always -family:wikipedia -lang:tr
python core/pwb.py redirect.py double -always -family:wikipedia -lang:ta

python core/pwb.py redirect.py double -always -family:wiktionary -lang:de
python core/pwb.py redirect.py double -always -family:wiktionary -lang:en
python core/pwb.py redirect.py double -always -family:wiktionary -lang:es
python core/pwb.py redirect.py double -always -family:wiktionary -lang:fr
python core/pwb.py redirect.py double -always -family:wiktionary -lang:it
python core/pwb.py redirect.py double -always -family:wiktionary -lang:my
python core/pwb.py redirect.py double -always -family:wiktionary -lang:pt
python core/pwb.py redirect.py double -always -family:wiktionary -lang:ru
python core/pwb.py redirect.py double -always -family:wiktionary -lang:sv
python core/pwb.py redirect.py double -always -family:wiktionary -lang:zh

python core/pwb.py redirect.py double -always -family:wikiversity -lang:en
python core/pwb.py redirect.py double -always -family:wikiversity -lang:fr
python core/pwb.py redirect.py double -always -family:wikibooks -lang:en
python core/pwb.py redirect.py double -always -family:wikibooks -lang:es
python core/pwb.py redirect.py double -always -family:wikibooks -lang:fr
#python core/pwb.py redirect.py double -always -family:wikisource -lang:en
python core/pwb.py redirect.py double -always -family:wikisource -lang:fr
python core/pwb.py redirect.py double -always -family:wikiquote -lang:fr
python core/pwb.py redirect.py double -always -family:wikiquote -lang:en
python core/pwb.py redirect.py double -always -family:wikinews -lang:fr
python core/pwb.py redirect.py double -always -family:wikivoyage -lang:de
python core/pwb.py redirect.py double -always -family:wikivoyage -lang:fr

python core/pwb.py redirect.py broken -lang:fr -family:wiktionary -always
python core/pwb.py redirect.py broken -lang:fr -family:wikiversity -always
#python core/pwb.py redirect.py broken -lang:fr -family:wikibooks -always # pb du livre de photos


#*** Maintained ***
#python core/pwb.py src/fr.wikinews.2wikipedia
#python core/pwb.py src/fr.wikiquote.count-quotes -family:wikiquote -output:"User:JackBot/statistiques" -outputquotes:"Template:NUMBEROFQUOTES"


#*** Homemade ***
#python core/pwb.py src/fr.wikibooks.format -cat
#python core/pwb.py src/fr.wikinews.format -cat
#python core/pwb.py src/fr.wikiquote.format -cat
#python core/pwb.py src/fr.wikiversity.format -cat
#python core/pwb.py src/fr.wikivoyage.format -cat
#python core/pwb.py src/fr.wiktionary.format -cat
#python core/pwb.py src/en.wikiquote.format -cat
#python core/pwb.py src/en.wikiversity.format -cat
#python core/pwb.py src/fr.wikipedia.format -cat
#python core/pwb.py src/en.wiktionary.format -cat
#python core/pwb.py src/en.wikibooks.format -cat
#python core/pwb.py src/fr.wiktionary.format.py -u Escarbot revocation 1000

# Current daily global operations
python core/pwb.py src/en.wikibooks.format -nocat
python core/pwb.py src/fr.wikibooks.format -nocat
python core/pwb.py src/fr.wikiversity.format -nocat
python core/pwb.py src/fr.wikipedia.format
python core/pwb.py src/fr.wiktionary.archive
python core/pwb.py src/fr.wiktionary.create-flexions
python core/pwb.py src/fr.wiktionary.format
python core/pwb.py src/fr.wiktionary.import-from-commons

#TODO: updateDumps.sh (by cron)
